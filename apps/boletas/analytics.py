from collections import defaultdict
from decimal import Decimal


def _decimal(value):
    return Decimal(str(value or 0))


def build_payroll_summary(slips):
    payrolls = defaultdict(
        lambda: {"workers": 0, "net": Decimal("0"), "income": Decimal("0")}
    )
    positions = defaultdict(
        lambda: {"workers": 0, "net": Decimal("0"), "income": Decimal("0")}
    )
    workers = []

    total_net = Decimal("0")
    total_income = Decimal("0")
    total_deductions = Decimal("0")
    total_basic = Decimal("0")

    for slip in slips:
        net = _decimal(slip.get("net_total"))
        income = _decimal(slip.get("income_total"))
        deductions = _decimal(slip.get("deduction_total"))
        basic = _decimal(slip.get("basico"))
        payroll = slip.get("payroll_type_label") or "OTRA PLANILLA"
        position = slip.get("cargo_personal") or "SIN CARGO"

        total_net += net
        total_income += income
        total_deductions += deductions
        total_basic += basic

        payrolls[payroll]["workers"] += 1
        payrolls[payroll]["net"] += net
        payrolls[payroll]["income"] += income

        positions[position]["workers"] += 1
        positions[position]["net"] += net
        positions[position]["income"] += income

        workers.append(
            {
                "name": slip.get("apenom") or "SIN NOMBRE",
                "document": slip.get("nrodocumento") or "",
                "position": position,
                "payroll": payroll,
                "basic": basic,
                "income": income,
                "deductions": deductions,
                "net": net,
            }
        )

    payroll_rows = [
        {"name": name, **values}
        for name, values in sorted(
            payrolls.items(), key=lambda item: item[1]["net"], reverse=True
        )
    ]
    position_rows = [
        {"name": name, **values}
        for name, values in sorted(
            positions.items(), key=lambda item: item[1]["net"], reverse=True
        )
    ]
    workers.sort(key=lambda item: item["net"], reverse=True)

    return {
        "total_workers": len(slips),
        "total_net": total_net,
        "total_income": total_income,
        "total_deductions": total_deductions,
        "total_basic": total_basic,
        "payrolls": payroll_rows,
        "positions": position_rows,
        "workers": workers,
    }
