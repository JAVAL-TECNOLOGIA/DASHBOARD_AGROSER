from datetime import date, datetime
from decimal import Decimal
from unittest import TestCase

from .liquidation_projection import (
    build_closure_projection, build_projection_summary, project_closure_liquidation,
    project_contract_liquidation,
)


class LiquidationProjectionTests(TestCase):
    def test_projects_only_vacation_without_cts_or_gratification(self):
        row = project_contract_liquidation({
            "fecha_ingreso": date(2026, 1, 1),
            "final_contrato": date(2026, 4, 30),
            "basico": Decimal("40.00"),
            "payroll_id": "OBP",
        })

        self.assertEqual(row["service_days"], 120)
        self.assertEqual(row["projected_vacation"], Decimal("400.00"))
        self.assertEqual(row["projected_cts"], Decimal("0.00"))
        self.assertEqual(row["projected_gratification"], Decimal("0.00"))
        self.assertEqual(row["projected_total"], Decimal("400.00"))

    def test_requires_at_least_one_month_of_service(self):
        row = project_contract_liquidation({
            "fecha_ingreso": date(2026, 1, 1),
            "final_contrato": date(2026, 1, 20),
            "basico": "40.00",
        })
        self.assertFalse(row["eligible"])
        self.assertEqual(row["projected_total"], Decimal("0.00"))

    def test_converts_monthly_contract_basic_to_daily_rate(self):
        row = project_contract_liquidation({
            "fecha_ingreso": date(2026, 3, 24),
            "final_contrato": date(2026, 6, 24),
            "basico": "1900.00",
        })
        self.assertEqual(row["basic_periodicity"], "MENSUAL")
        self.assertEqual(row["daily_basic"], Decimal("63.33"))
        self.assertLess(row["projected_total"], Decimal("1000.00"))

    def test_groups_projected_total_by_contract_end_month(self):
        summary = build_projection_summary([
            {"fecha_ingreso": date(2026, 1, 1), "final_contrato": date(2026, 4, 30), "basico": 40},
            {"fecha_ingreso": date(2026, 2, 1), "final_contrato": date(2026, 4, 30), "basico": 30},
        ], 2026)
        self.assertEqual(summary["projection_workers"], 2)
        self.assertEqual(summary["projection_months"][3]["workers"], 2)
        self.assertGreater(summary["projection_months"][3]["total"], 0)

    def test_closure_projection_includes_every_active_contract(self):
        summary = build_closure_projection([
            {"full_name": "ANA", "fecha_ingreso": date(2026, 1, 1), "basico": 40,
             "payroll": "OBREROS", "position": "OPERARIO"},
            {"full_name": "LUIS", "fecha_ingreso": date(2026, 2, 1), "basico": 1500,
             "payroll": "EMPLEADOS", "position": "ASISTENTE"},
        ], date(2026, 10, 31))

        self.assertEqual(summary["closure_workers"], 2)
        self.assertEqual(len(summary["closure_payrolls"]), 2)
        self.assertGreater(summary["closure_total"], Decimal("0.00"))
        self.assertEqual(summary["closure_rows"][0]["final_contrato"], date(2026, 10, 31))

    def test_accepts_sql_server_datetime_for_admission_date(self):
        summary = build_closure_projection([{
            "full_name": "ANA",
            "fecha_ingreso": datetime(2026, 1, 1, 0, 0),
            "basico": 40,
        }], date(2026, 10, 31))

        self.assertEqual(summary["closure_workers"], 1)
        self.assertGreater(summary["closure_total"], Decimal("0.00"))

    def test_closure_uses_nisira_performance_parameters(self):
        row = project_closure_liquidation({
            "fecha_ingreso": date(2026, 3, 24),
            "basico": "41.00",
            "performance_months": 8,
            "performance_total": "17173.89",
            "rest_days": "31.82",
            "performance_days": "198.00",
            "has_family_allowance": True,
            "minimum_wage": "1230.00",
            "has_payroll_parameters": True,
        }, date(2026, 10, 31))

        self.assertEqual(row["performance_average"], Decimal("2862.32"))
        self.assertEqual(row["rest_days"], Decimal("32"))
        self.assertEqual(row["service_days"], 230)
        self.assertEqual(row["family_allowance"], Decimal("123.00"))
        self.assertEqual(row["computable_base"], Decimal("4215.32"))
        self.assertEqual(row["projected_total"], Decimal("2693.12"))
