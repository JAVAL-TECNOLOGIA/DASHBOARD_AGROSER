from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from apps.contabilidad.cajas_kilos_service import build_boxes_and_kilos_report
from apps.contabilidad.ventas_service import build_sales_report

from apps.user.views import UserAdministrationMixin


class ContabilidadReportesViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='contabilidad_test',
            email='contabilidad@example.com',
            first_name='Usuario',
            last_name='Contabilidad',
            password='test-password',
        )
        self.url = reverse('contabilidad_reportes')

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_rejects_user_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_allows_user_with_reports_permission(self):
        permission = Permission.objects.get(
            content_type__app_label='contabilidad',
            codename='ver_reportes_contabilidad',
        )
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reportes de Contabilidad')

    def test_reports_permission_appears_in_user_administration(self):
        permission = Permission.objects.get(
            content_type__app_label='contabilidad',
            codename='ver_reportes_contabilidad',
        )

        permission_groups = dict(UserAdministrationMixin.permission_groups())

        self.assertIn('contabilidad', permission_groups)
        self.assertIn(permission, permission_groups['contabilidad'])

    def test_allows_administrator(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_displays_the_five_report_cards(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reportes']), 5)
        for title in (
            'Comparación',
            'Ventas',
            'Detalle Cajas y Kilos',
            'Consolidado de Costos y Gastos Junio/Julio 2025 - 2026',
            'Balance General Agosto 2026',
        ):
            self.assertContains(response, title)

    def test_each_card_opens_its_report_view(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['ventas'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ventas')

    def test_comparison_report_includes_dashboard_data(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['comparacion'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Evolución mensual')
        self.assertContains(response, 'Variación interanual')
        self.assertEqual(set(response.context['comparacion_data']['data']), {'2023', '2024', '2025', '2026'})
        self.assertEqual(response.context['comparacion_data']['data']['2026']['cajas'][8], None)
        self.assertEqual(len(response.context['comparacion_data']['descriptions']), 21)
        self.assertContains(response, 'Detalle mensual y anual por descripción')
        self.assertContains(response, 'Costo De Ventas Exportacion')

    def test_costs_report_includes_all_four_periods_and_indicators(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'contabilidad_reporte_detalle',
                args=['consolidado-costos-gastos-junio-julio-2025-2026'],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comparación mensual')
        self.assertContains(response, 'Detalle por cuenta y descripción')
        self.assertContains(response, 'Julio 2025')
        data = response.context['costos_gastos_data']
        self.assertEqual(len(data['periods']), 4)
        self.assertEqual(len(data['accounts']), 143)
        self.assertContains(response, '91621101 · Sueldos Empleados')
        self.assertContains(response, '94621101 · Sueldos Empleados')
        june_2025 = next(period for period in data['periods'] if period['key'] == '2025-06')
        july_2026 = next(period for period in data['periods'] if period['key'] == '2026-07')
        self.assertAlmostEqual(june_2025['total'], 543565.29, places=2)
        self.assertFalse(any(row['account'] == '94636401' for row in june_2025['rows']))
        self.assertAlmostEqual(july_2026['total'], 940683.00, places=2)

    @patch('apps.contabilidad.views.get_sales_report')
    def test_sales_report_uses_nisira_totals_in_both_currencies(self, report_mock):
        report_mock.return_value = build_sales_report([
            (date(2026, 8, 5), 23368.53, 6938.40),
            (date(2026, 8, 5), 26539.97, 7880.04),
        ], current_year=2026)
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['ventas'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Evolución mensual de ventas')
        self.assertContains(response, 'Detalle mensual y anual')
        self.assertContains(response, 'Total en dólares')
        data = response.context['ventas_data']
        self.assertEqual(data['years'], [2023, 2024, 2025, 2026])
        self.assertEqual(len(data['months']), 12)
        self.assertNotContains(response, 'ventas.xlsx')
        self.assertAlmostEqual(data['data']['2026'][7], 49908.50, places=2)
        self.assertAlmostEqual(data['data_usd']['2026'][7], 14818.44, places=2)

    @patch('apps.contabilidad.views.get_boxes_and_kilos_report')
    def test_boxes_and_kilos_report_uses_nisira_data(self, report_mock):
        report_mock.return_value = build_boxes_and_kilos_report([
            (2026, 10, 'AGROEXPOR SOL', 'AGROEXPOR SOL', 19588, 97940),
            (2026, 10, 'AGROSERVICE', 'AGROEXPOR SOL', 12561, 62805),
            (2026, 10, 'GOURMET FARMS', 'GOURMET FARMS', 4623, 23465),
        ], current_year=2026)
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['detalle-cajas-kilos'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Producción por productor')
        self.assertContains(response, 'Historial mensual por cliente y productor')
        self.assertNotContains(response, 'cajas y kilos.xlsx')
        data = response.context['cajas_kilos_data']
        self.assertEqual(data['clients'], ['AGROEXPOR SOL', 'AGROSERVICE', 'GOURMET FARMS'])
        self.assertEqual(data['producers'], ['AGROEXPOR SOL', 'GOURMET FARMS'])
        self.assertEqual(data['years'], [2023, 2024, 2025, 2026])
        self.assertEqual(
            data['series'][0]['cajas']['2026'][9],
            19588.0,
        )
        self.assertEqual(
            data['series'][2]['kilos']['2026'][9],
            23465.0,
        )
        self.assertEqual(data['source'], 'NISIRA ERP · Producción de Cajas')

    def test_august_balance_report_reconciles_net_position(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['balance-general-agosto-2026'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Activos líquidos frente a obligaciones')
        self.assertContains(response, 'Lectura gerencial')
        data = response.context['balance_data']
        assets = sum(item['amount'] for item in data['items'] if item['group'] == 'activo')
        obligations = sum(item['amount'] for item in data['items'] if item['group'] == 'obligacion')
        self.assertAlmostEqual(assets, 1685503.89, places=2)
        self.assertAlmostEqual(obligations, 1790463.03, places=2)
        self.assertAlmostEqual(assets - obligations, data['net_position'], places=2)

    def test_unknown_report_returns_404(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['no-existe'])
        )

        self.assertEqual(response.status_code, 404)
