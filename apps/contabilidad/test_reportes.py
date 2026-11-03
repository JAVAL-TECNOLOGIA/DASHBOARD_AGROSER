from datetime import date, datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from apps.contabilidad.cajas_kilos_service import build_boxes_and_kilos_report
from apps.contabilidad.comparacion_service import build_comparison_report
from apps.contabilidad.costos_service import build_costs_report
from apps.contabilidad.ventas_service import build_sales_report
from apps.contabilidad.ventas_exportacion_service import build_export_sales_report
from apps.contabilidad.liquidacion_caja_service import build_cash_liquidation_report

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

    def test_displays_the_active_report_cards(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reportes']), 6)
        for title in (
            'Comparación',
            'Ventas',
            'Ventas de Exportación',
            'Detalle Cajas y Kilos',
            'Liquidación de Caja',
        ):
            self.assertContains(response, title)
        self.assertNotContains(response, 'Consolidado de Costos y Gastos')
        self.assertNotContains(response, 'Balance General Agosto 2026')

    def test_each_card_opens_its_report_view(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['ventas'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ventas')

    @patch('apps.contabilidad.views.get_export_sales_report')
    def test_export_sales_report_keeps_excel_sections_as_independent_tabs(self, report_mock):
        report_mock.return_value = build_export_sales_report(
            [
                {
                    'date': date(2026, 8, 4), 'document_type': 'FACTURA',
                    'document': 'F002-47', 'customer': 'AYCO FARMS INC',
                    'affected': 0, 'exported': 56000, 'exempt': 0,
                    'sales_tax': 0, 'currency': 'US$', 'exchange_rate': 3.402,
                    'total_usd': 16460.91, 'total_pen': 56000,
                    'reference': '', 'is_export_credit': False,
                },
                {
                    'date': date(2026, 8, 5), 'document_type': 'FACTURA',
                    'document': 'F001-1771', 'customer': 'CLIENTE LOCAL',
                    'affected': 19803.84, 'exported': 0, 'exempt': 0,
                    'sales_tax': 3564.69, 'currency': 'S/', 'exchange_rate': 3.4,
                    'total_usd': 6938.40, 'total_pen': 23368.53,
                    'reference': '', 'is_export_credit': False,
                },
            ],
            [
                {
                    'date': date(2026, 8, 17), 'document_type': 'FAC',
                    'document': 'F001 0035559', 'tax_id': '20344769932',
                    'supplier': 'FRIO AEREO', 'base': 3593.12, 'tax': 646.76,
                    'total': 4239.88, 'currency': 'US$', 'exchange_rate': 3.4,
                    'detail': 'REFRIGERADO F002-47', 'glosa': '',
                },
                {
                    'date': date(2026, 8, 18), 'document_type': 'FAC',
                    'document': 'E001 0001', 'tax_id': '20111111111',
                    'supplier': 'PROVEEDOR LOCAL', 'base': 1000, 'tax': 180,
                    'total': 1180, 'currency': 'S/', 'exchange_rate': 3.4,
                    'detail': 'COMPRA LOCAL', 'glosa': '',
                },
            ],
            current_year=2026,
        )
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['ventas-exportacion'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comparativo mensual')
        self.assertContains(response, 'Detalle de facturas')
        self.assertContains(response, 'Registro de compras')
        data = response.context['ventas_exportacion_data']
        august = next(row for row in data['summary'] if row['year'] == 2026 and row['month'] == 7)
        self.assertEqual(august['sales_with_export'], 75803.84)
        self.assertEqual(august['sales_without_export'], 19803.84)
        self.assertEqual(august['export_cost'], 3593.12)
        self.assertEqual(len(data['invoices']), 1)
        self.assertEqual(len(data['purchases']), 1)

    @patch('apps.contabilidad.views.get_comparison_report')
    def test_comparison_report_uses_nisira_data(self, report_mock):
        report_mock.return_value = build_comparison_report(
            [
                (2026, 5, 'MAQUILA', 61880, 309400),
                (2026, 5, 'EXPORTACION', 12561, 62805),
            ],
            {
                2026: [
                    ('202605', '70401', 0, 516573.83, 0, 0),
                    ('202605', '70201', 0, 705059.10, 0, 0),
                    ('202605', '69401', 398999.46, 0, 0, 0),
                    ('202605', '69201', 695675.52, 0, 0, 0),
                    ('202605', '75', 0, 16410.44, 0, 0),
                    ('202605', '94', 165858.71, 0, 0, 0),
                ],
            },
            current_year=2026,
        )
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['comparacion'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comparación mensual')
        self.assertContains(response, 'Ingresos y costos mensuales')
        self.assertContains(response, 'Fuente: NISIRA ERP')
        self.assertNotContains(response, 'comparacion.xlsx')
        data = response.context['comparacion_data']
        self.assertEqual(data['years'], [2023, 2024, 2025, 2026])
        self.assertEqual(len(data['metrics']), 16)
        metrics = {item['key']: item for item in data['metrics']}
        self.assertEqual(metrics['boxes_maquila']['values']['2026'][4], 61880)
        self.assertEqual(metrics['boxes_export']['values']['2026'][4], 12561)
        self.assertAlmostEqual(metrics['income_maquila']['values']['2026'][4], 516573.83, places=2)
        self.assertAlmostEqual(metrics['income_export']['values']['2026'][4], 705059.10, places=2)

    @patch('apps.contabilidad.views.get_sales_report')
    def test_sales_report_uses_nisira_totals_in_both_currencies(self, report_mock):
        report_mock.return_value = build_sales_report([
            (date(2026, 8, 5), 23368.53, 6938.40, 'AGROEXPOR SOL', 19803.84, 0, 0),
            (date(2026, 8, 5), 26539.97, 7880.04, 'GOURMET FARMS', 22491.50, 0, 0),
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
        self.assertContains(response, 'Venta afectada')
        self.assertContains(response, 'Venta exportación')
        self.assertContains(response, 'Venta exonerada')
        self.assertContains(response, 'Ventas por razón social')
        self.assertNotContains(response, 'Variación interanual')
        self.assertNotContains(response, 'Mejor mes')
        self.assertNotContains(response, 'Promedio mensual')
        data = response.context['ventas_data']
        self.assertEqual(data['years'], [2023, 2024, 2025, 2026])
        self.assertEqual(len(data['months']), 12)
        self.assertNotContains(response, 'ventas.xlsx')
        self.assertAlmostEqual(data['data']['2026'][7], 42295.34, places=2)
        self.assertAlmostEqual(data['data_usd']['2026'][7], 14818.44, places=2)
        self.assertEqual(data['customers'], ['AGROEXPOR SOL', 'GOURMET FARMS'])
        self.assertAlmostEqual(sum(row['affected'] for row in data['sales']), 42295.34, places=2)
        self.assertAlmostEqual(sum(row['total'] for row in data['sales']), 42295.34, places=2)

    @patch('apps.contabilidad.views.get_cash_liquidation_report')
    def test_cash_liquidation_report_uses_balance_general_data(self, report_mock):
        report_mock.return_value = build_cash_liquidation_report([
            ('10110101', 'A', '', 600, 100, 0, 0, 0, 0, 0, 0),
            ('12120101', 'A', '', 1000, 100, 0, 0, 0, 0, 0, 0),
            ('12120102', 'A', '', 2000, 0, 0, 0, 0, 0, 0, 0),
            ('42110001', 'P', '', 100, 5000, 0, 0, 0, 0, 0, 0),
            # Un saldo deudor dentro de una cuenta por pagar no reduce la deuda.
            ('42200018', 'P', '', 700, 200, 0, 0, 0, 0, 0, 0),
        ], report_date=date(2026, 8, 31))
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['liquidacion-caja']),
            {'year': 2026, 'month': 8, 'day': 31},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total por cobrar')
        self.assertContains(response, 'Total por pagar')
        self.assertContains(response, 'Composición de obligaciones')
        data = response.context['liquidacion_caja_data']
        self.assertEqual(data['receivable_total'], 2900.0)
        self.assertEqual(data['payable_total'], 4900.0)
        self.assertEqual(data['cash_total'], 500.0)
        self.assertEqual(data['available_total'], 3400.0)
        self.assertEqual(data['net_position'], -1500.0)

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

    @patch('apps.contabilidad.views.get_costs_report')
    def test_costs_report_uses_nisira_distribution_data(self, report_mock):
        report_mock.return_value = build_costs_report([
            ('_7I50UO80H30616', datetime(2026, 5, 31), '202605', 'DIC', '0001', '0000235', '0001', 'ADMINISTRACION', 'PE', 1, 1, 0, 104, 73927.20),
            ('_7I50V79VN30616', datetime(2026, 5, 31), '202605', 'DIC', '0001', '0000239', '0007', 'PRODUCCION EXPORTACION', 'PE', 1, 1, 1, 19, 670911.61),
        ], current_year=2026, detail_rows=[
            ('202605', '0007', 'AGROSERVICE', 693056.81, 693056.81, 12561, 62805),
            ('202605', '0008', 'AGROEXPOR SOL', 125155.65, 125155.65, 19588, 97940),
        ])
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(reverse('contabilidad_reporte_detalle', args=['costos']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detalle general')
        data = response.context['costos_data']
        self.assertEqual(len(data['records']), 2)
        self.assertEqual(data['records'][0]['detail_count'], 104)
        self.assertFalse(data['records'][0]['costed'])
        self.assertTrue(data['records'][1]['costed'])
        self.assertEqual(data['details'][0]['class_code'], '0007')
        self.assertEqual(data['details'][0]['client'], 'AGROSERVICE')
        self.assertEqual(data['details'][0]['boxes'], 12561.0)
        self.assertEqual(data['details'][0]['kilograms'], 62805.0)

    def test_unknown_report_returns_404(self):
        self.user.admin = True
        self.user.save(update_fields=['admin'])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('contabilidad_reporte_detalle', args=['no-existe'])
        )

        self.assertEqual(response.status_code, 404)
