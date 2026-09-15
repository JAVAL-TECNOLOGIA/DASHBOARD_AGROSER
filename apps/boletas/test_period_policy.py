from datetime import date
from unittest.mock import patch
from django.test import SimpleTestCase
from .periods import month_range, custom_range, visible_period, portal_month_range
from .services import PaySlipService
from .views import _official_payroll_period
from .worker_portal import worker_slips, resolve_worker_period


class PeriodPolicyTests(SimpleTestCase):
    def test_plant_payroll_uses_an_official_week_from_the_selected_month(self):
        service = PaySlipService()
        service.payroll_weeks = lambda month, payroll: [
            {'number':'41', 'start':date(2026,8,24), 'end':date(2026,8,30), 'equivalent':'41'},
            {'number':'42', 'start':date(2026,8,31), 'end':date(2026,8,31), 'equivalent':'42'},
        ]
        period, weeks, selected = _official_payroll_period(service, 'OBR', '2026-08', '41')
        self.assertEqual(selected, '41')
        self.assertEqual((period.start, period.end), (date(2026,8,24), date(2026,8,30)))
        self.assertEqual(len(weeks), 2)

    def test_partial_weeks_across_months_are_joined_into_seven_days(self):
        service = PaySlipService()
        calendars = {
            '2026-07': [],
            '2026-08': [{'number':'42','start':date(2026,8,31),'end':date(2026,8,31),'equivalent':'42'}],
            '2026-09': [{'number':'43','start':date(2026,9,1),'end':date(2026,9,6),'equivalent':'43'}],
        }
        service.payroll_weeks = lambda month, payroll: calendars[month]
        period, weeks, selected = _official_payroll_period(service, 'OBP', '2026-08', '42+43')
        self.assertEqual(selected, '42+43')
        self.assertEqual(weeks[0]['number'], '42+43')
        self.assertEqual((period.start, period.end), (date(2026,8,31), date(2026,9,6)))

    def test_admin_template_has_official_week_selector(self):
        from django.template.loader import render_to_string
        html = render_to_string('boletas/index.html', {
            'payroll_type':'OBP', 'payroll_week':'42',
            'payroll_weeks':[{'number':'42','start':date(2026,8,31),'end':date(2026,8,31)}],
        })
        self.assertIn('name="payroll_week"', html)
        self.assertIn('Semana 42', html)

    def test_worker_monthly_template_has_no_week_or_range_options(self):
        from django.template.loader import render_to_string
        html = render_to_string('boletas/worker/dashboard.html', {'monthly_only': True, 'mode': 'month'})
        self.assertNotIn('<option value="week"', html)
        self.assertNotIn('<option value="custom"', html)
        self.assertIn('min="2026-08"', html)

    def test_before_august_is_not_queried(self):
        with patch.object(PaySlipService, '_execute') as execute:
            self.assertEqual(PaySlipService().list(month_range('2026-07')), [])
            execute.assert_not_called()
        self.assertEqual(worker_slips('01234567', month_range('2026-07')), [])
        with self.assertRaises(ValueError): portal_month_range('2026-07')

    def test_crossing_range_starts_at_august(self):
        result = visible_period(custom_range('2026-07-25','2026-08-10'))
        self.assertEqual(result.start,date(2026,8,1))

    @patch('apps.boletas.worker_portal.worker_slips', return_value=[{'payroll_type':'ERG'}])
    def test_erg_worker_forces_complete_month(self, slips):
        mode, period, only = resolve_worker_period('01234567','custom',start_value='2026-08-05',end_value='2026-08-10')
        self.assertEqual(mode,'month')
        self.assertTrue(only)
        self.assertEqual(period, month_range('2026-08'))

    @patch('apps.boletas.worker_portal.worker_slips', return_value=[{'payroll_type':'ERA'}])
    def test_era_worker_forces_complete_month(self, slips):
        mode, period, only = resolve_worker_period('01234567','custom',start_value='2026-08-05',end_value='2026-08-10')
        self.assertEqual(mode,'month')
        self.assertTrue(only)
        self.assertEqual(period, month_range('2026-08'))

    @patch('apps.boletas.worker_portal.worker_slips', return_value=[{'payroll_type':'OBP'}])
    def test_obp_worker_forces_complete_month(self, slips):
        mode, period, only = resolve_worker_period('01234567','week',week_value='2026-W33')
        self.assertEqual(mode,'month')
        self.assertTrue(only)
        self.assertEqual(period, month_range('2026-08'))

    @patch('apps.boletas.worker_portal.worker_slips', return_value=[{'payroll_type':'OBR'}])
    def test_other_payroll_keeps_week(self, slips):
        mode, period, only = resolve_worker_period('01234567','week',week_value='2026-W33')
        self.assertEqual(mode,'week')
        self.assertFalse(only)
