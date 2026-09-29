from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


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

    def test_sales_report_includes_monthly_and_annual_data(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['ventas'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Evolución mensual de ventas')
        self.assertContains(response, 'Detalle mensual y anual')
        data = response.context['ventas_data']
        self.assertEqual(data['years'], [2023, 2024, 2025, 2026])
        self.assertEqual(len(data['months']), 12)
        self.assertAlmostEqual(sum(value or 0 for value in data['data']['2025']), 8053253.00, places=2)
        self.assertAlmostEqual(sum(value or 0 for value in data['data']['2026']), 5133619.33, places=2)
        self.assertEqual(data['data']['2026'][8:], [None, None, None, None])

    def test_boxes_and_kilos_report_includes_clients_and_both_metrics(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['detalle-cajas-kilos'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Producción por cliente')
        self.assertContains(response, 'Historial mensual por cliente')
        data = response.context['cajas_kilos_data']
        self.assertEqual(len(data['clients']), 13)
        self.assertEqual(data['years'], [2023, 2024, 2025, 2026])
        boxes_2026 = sum(
            value or 0
            for client in data['clients']
            for value in data['metrics']['cajas']['clients'][client]['2026']
        )
        kilos_2026 = sum(
            value or 0
            for client in data['clients']
            for value in data['metrics']['kilos']['clients'][client]['2026']
        )
        self.assertAlmostEqual(boxes_2026, 491982.00, places=2)
        self.assertAlmostEqual(kilos_2026, 3128567.40, places=2)

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
