from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def _date(value):
    if value is None or hasattr(value, "year"):
        return value
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def _money(value):
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def project_contract_liquidation(contract):
    """Return a referential projection using the company's payroll rules.

    CTS and gratification are zero because OBP/OBR do not receive them and
    ERG/ERA already include them in the monthly payslip. Vacation accrual is
    estimated at 30 days per 360 service days using the contract daily basic.
    """
    start = _date(contract.get("fecha_ingreso") or contract.get("inicio_contrato"))
    end = _date(contract.get("final_contrato"))
    daily_basic = _money(contract.get("basico"))
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
        "daily_basic": daily_basic,
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
