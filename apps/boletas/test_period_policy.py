from datetime import date
from unittest.mock import patch
from django.test import SimpleTestCase
from .periods import month_range, custom_range, visible_period, portal_month_range
from .services import PaySlipService
from .worker_portal import worker_slips, resolve_worker_period


class PeriodPolicyTests(SimpleTestCase):
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

    @patch('apps.boletas.worker_portal.worker_slips', return_value=[{'payroll_type':'OBP'}])
    def test_other_payroll_keeps_week(self, slips):
        mode, period, only = resolve_worker_period('01234567','week',week_value='2026-W33')
        self.assertEqual(mode,'week')
        self.assertFalse(only)
