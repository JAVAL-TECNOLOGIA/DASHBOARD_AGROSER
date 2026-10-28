from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
CENT = Decimal("0.01")
MONTHLY_BASIC_THRESHOLD = Decimal("300.00")


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    if value is None or hasattr(value, "year"):
        return value
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def _money(value):
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def project_contract_liquidation(contract):
    """Return a referential projection using the company's payroll rules.

    CTS and gratification are zero because OBP/OBR do not receive them and
    ERG/ERA already include them in the monthly payslip. Vacation accrual is
    estimated at 30 days per 360 service days. Contract basics above the
    configured threshold are normalized from monthly to daily amounts.
    """
    start = _date(contract.get("fecha_ingreso") or contract.get("inicio_contrato"))
    end = _date(contract.get("final_contrato"))
    contract_basic = _money(contract.get("basico"))
    is_monthly = contract_basic > MONTHLY_BASIC_THRESHOLD
    daily_basic = (
        (contract_basic / Decimal("30")).quantize(CENT, rounding=ROUND_HALF_UP)
        if is_monthly else contract_basic
    )
    service_days = max((end - start).days + 1, 0) if start and end else 0
    eligible = service_days >= 30 and daily_basic > 0
    vacation = (
        (daily_basic * Decimal(service_days) / Decimal("12")).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        if eligible
        else ZERO
    )
    return {
        **contract,
        "fecha_ingreso": start,
        "final_contrato": end,
        "contract_basic": contract_basic,
        "daily_basic": daily_basic,
        "basic_periodicity": "MENSUAL" if is_monthly else "DIARIA",
        "service_days": service_days,
        "projected_cts": ZERO,
        "projected_gratification": ZERO,
        "projected_vacation": vacation,
        "projected_total": vacation,
        "eligible": eligible,
    }


def build_projection_summary(contracts, year):
    rows = [project_contract_liquidation(contract) for contract in contracts]
    rows.sort(key=lambda item: (item.get("final_contrato"), item.get("full_name") or ""))
    monthly = defaultdict(lambda: {"workers": 0, "total": ZERO})
    for row in rows:
        end = row.get("final_contrato")
        if end and end.year == int(year):
            monthly[end.month]["workers"] += 1
            monthly[end.month]["total"] += row["projected_total"]
    total = sum((row["projected_total"] for row in rows), ZERO)
    return {
        "projection_rows": rows,
        "projection_total": total.quantize(CENT),
        "projection_workers": len(rows),
        "projection_average": (
            (total / len(rows)).quantize(CENT, rounding=ROUND_HALF_UP)
            if rows else ZERO
        ),
        "projection_months": [
            {
                "month": month,
                "workers": monthly[month]["workers"],
                "total": monthly[month]["total"].quantize(CENT),
            }
            for month in range(1, 13)
        ],
    }


def build_closure_projection(contracts, closing_date):
    """Estimate the cash required if all active personnel leave on closing_date."""
    rows = [project_closure_liquidation(contract, closing_date) for contract in contracts]
    rows.sort(key=lambda item: (item.get("payroll") or "", item.get("full_name") or ""))

    by_payroll = defaultdict(lambda: {"workers": 0, "total": ZERO})
    by_position = defaultdict(lambda: {"workers": 0, "total": ZERO})
    for row in rows:
        payroll = (row.get("payroll") or row.get("payroll_id") or "SIN PLANILLA").strip()
        position = (row.get("position") or "SIN PERFIL").strip()
        by_payroll[payroll]["workers"] += 1
        by_payroll[payroll]["total"] += row["projected_total"]
        by_position[position]["workers"] += 1
        by_position[position]["total"] += row["projected_total"]

    total = sum((row["projected_total"] for row in rows), ZERO).quantize(CENT)
    return {
        "closure_rows": rows,
        "closure_total": total,
        "closure_workers": len(rows),
        "closure_average": (
            (total / len(rows)).quantize(CENT, rounding=ROUND_HALF_UP)
            if rows else ZERO
        ),
        "closure_payrolls": [
            {"name": name, **values, "total": values["total"].quantize(CENT)}
            for name, values in sorted(
                by_payroll.items(), key=lambda item: item[1]["total"], reverse=True
            )
        ],
        "closure_positions": [
            {"name": name, **values, "total": values["total"].quantize(CENT)}
            for name, values in sorted(
                by_position.items(), key=lambda item: item[1]["total"], reverse=True
            )
        ],
    }


def project_closure_liquidation(contract, closing_date):
    """Project the closure scenario with NISIRA's payroll parameters.

    The operational report uses a six-month divisor for performance, then adds
    the current basic salary and family allowance to obtain the computable base.
    Vacation liquidation is base * computable days / 360.
    """
    if not contract.get("has_payroll_parameters"):
        return project_contract_liquidation({**contract, "final_contrato": closing_date})

    start = _date(contract.get("fecha_ingreso") or contract.get("inicio_contrato"))
    contract_basic = _money(contract.get("basico"))
    basic = (
        (contract_basic * Decimal("30")).quantize(CENT)
        if contract_basic <= MONTHLY_BASIC_THRESHOLD else contract_basic
    )
    performance_total = _money(contract.get("performance_total"))
    performance_average = (performance_total / Decimal("6")).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    family_allowance = (
        (_money(contract.get("minimum_wage")) * Decimal("0.10")).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        if contract.get("has_family_allowance") else ZERO
    )
    rest_days = Decimal(str(contract.get("rest_days") or 0)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    performance_days = Decimal(str(contract.get("performance_days") or 0)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    computable_days = rest_days + performance_days
    computable_base = (basic + family_allowance + performance_average).quantize(CENT)
    total = (computable_base * computable_days / Decimal("360")).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    return {
        **contract,
        "fecha_ingreso": start,
        "final_contrato": closing_date,
        "contract_basic": basic,
        "daily_basic": (basic / Decimal("30")).quantize(CENT, rounding=ROUND_HALF_UP),
        "basic_periodicity": "MENSUAL",
        "performance_months": int(contract.get("performance_months") or 0),
        "performance_total": performance_total,
        "performance_average": performance_average,
        "family_allowance": family_allowance,
        "rest_days": rest_days,
        "performance_days": performance_days,
        "service_days": int(computable_days),
        "computable_base": computable_base,
        "projected_cts": ZERO,
        "projected_gratification": ZERO,
        "projected_vacation": total,
        "projected_total": total,
        "eligible": computable_days > 0 and computable_base > 0,
    }
