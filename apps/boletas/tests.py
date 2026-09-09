from datetime import date
from decimal import Decimal

from django.test import SimpleTestCase

from .analytics import build_payroll_summary
from .periods import custom_range, month_range, week_range, week_value_for_date
from .services import PaySlipService
from .worker_forms import WorkerLoginForm, WorkerPasswordChangeForm
from .worker_portal import payslip_fingerprint


class DateRangeTests(SimpleTestCase):
    def test_month_range_uses_first_and_last_day(self):
        result = month_range("2026-02")
        self.assertEqual(result.start, date(2026, 2, 1))
        self.assertEqual(result.end, date(2026, 2, 28))

    def test_first_week_of_2026_starts_on_january_first(self):
        result = week_range("2026-W01")
        self.assertEqual(result.start, date(2026, 1, 1))
        self.assertEqual(result.end, date(2026, 1, 4))

    def test_following_weeks_use_monday_and_sunday(self):
        result = week_range("2026-W02")
        self.assertEqual(result.start, date(2026, 1, 5))
        self.assertEqual(result.end, date(2026, 1, 11))

    def test_regular_week_uses_monday_and_sunday(self):
        result = week_range("2026-W30")
        self.assertEqual(result.start.isoweekday(), 1)
        self.assertEqual(result.end.isoweekday(), 7)
        self.assertEqual((result.end - result.start).days, 6)

    def test_week_value_uses_calendar_year_week(self):
        self.assertEqual(week_value_for_date(date(2026, 1, 1)), "2026-W01")
        self.assertEqual(week_value_for_date(date(2026, 1, 4)), "2026-W01")
        self.assertEqual(week_value_for_date(date(2026, 1, 5)), "2026-W02")

    def test_custom_range_rejects_inverted_dates(self):
        with self.assertRaises(ValueError):
            custom_range("2026-07-31", "2026-07-01")

    def test_custom_range_rejects_more_than_one_year(self):
        with self.assertRaises(ValueError):
            custom_range("2025-01-01", "2026-01-03")


class PayrollTypeTests(SimpleTestCase):
    def test_employee_general(self):
        self.assertEqual(
            PaySlipService.payroll_type(
                {"grupo_planilla": "01", "IDREGIMENLABORAL": "01"}
            ),
            "ERG",
        )

    def test_employee_agrarian(self):
        self.assertEqual(
            PaySlipService.payroll_type(
                {"grupo_planilla": "01", "IDREGIMENLABORAL": "23"}
            ),
            "ERA",
        )

    def test_plant_worker(self):
        self.assertEqual(
            PaySlipService.payroll_type(
                {"grupo_planilla": "02", "IDREGIMENLABORAL": "26"}
            ),
            "OBP",
        )

    def test_general_plant_worker(self):
        self.assertEqual(
            PaySlipService.payroll_type(
                {"grupo_planilla": "02", "IDREGIMENLABORAL": "01"}
            ),
            "OBR",
        )

    def test_income_and_deduction_codes_are_recognized(self):
        self.assertTrue(PaySlipService._is_income({"idtipoconcepto": "IN"}))
        self.assertTrue(PaySlipService._is_deduction({"idtipoconcepto": "DE"}))


class PayrollSummaryTests(SimpleTestCase):
    def test_summary_groups_payrolls_positions_and_totals(self):
        summary = build_payroll_summary(
            [
                {
                    "apenom": "TRABAJADOR UNO",
                    "payroll_type_label": "OBREROS PLANTA",
                    "cargo_personal": "OPERARIO",
                    "basico": Decimal("1000"),
                    "income_total": Decimal("1200"),
                    "deduction_total": Decimal("200"),
                    "net_total": Decimal("1000"),
                },
                {
                    "apenom": "TRABAJADOR DOS",
                    "payroll_type_label": "OBREROS PLANTA",
                    "cargo_personal": "OPERARIO",
                    "basico": Decimal("900"),
                    "income_total": Decimal("1000"),
                    "deduction_total": Decimal("150"),
                    "net_total": Decimal("850"),
                },
            ]
        )
        self.assertEqual(summary["total_workers"], 2)
        self.assertEqual(summary["total_net"], Decimal("1850"))
        self.assertEqual(summary["total_income"], Decimal("2200"))
        self.assertEqual(summary["total_deductions"], Decimal("350"))
        self.assertEqual(summary["payrolls"][0]["workers"], 2)
        self.assertEqual(summary["positions"][0]["name"], "OPERARIO")
        self.assertEqual(summary["workers"][0]["name"], "TRABAJADOR UNO")


class WorkerPortalTests(SimpleTestCase):
    def test_login_requires_eight_digit_document(self):
        form = WorkerLoginForm(data={"document": "ABC", "password": "ABC"})
        self.assertFalse(form.is_valid())
        self.assertIn("document", form.errors)

    def test_new_password_cannot_equal_document(self):
        class Worker:
            username = "12345678"

        form = WorkerPasswordChangeForm(
            data={
                "new_password1": "12345678",
                "new_password2": "12345678",
            },
            user=Worker(),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("new_password1", form.errors)

    def test_payslip_fingerprint_changes_when_net_changes(self):
        period = month_range("2026-07")
        slip = {
            "nrodocumento": "12345678",
            "idcodigogeneral": "12345678",
            "codigoplanilla": "022671",
            "basico": Decimal("1200"),
            "income_total": Decimal("1300"),
            "deduction_total": Decimal("100"),
            "net_total": Decimal("1200"),
            "concepts": [],
        }
        first = payslip_fingerprint(slip, period)
        slip["net_total"] = Decimal("1199")
        second = payslip_fingerprint(slip, period)
        self.assertNotEqual(first, second)
