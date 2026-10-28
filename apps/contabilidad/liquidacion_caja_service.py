import calendar
from datetime import date
from decimal import Decimal

from django.core.cache import cache
from django.db import connections


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
FIRST_REPORT_YEAR = 2023
CACHE_SECONDS = 10 * 60

RECEIVABLE_GROUPS = (
    ('12', 'Cuentas por Cobrar Comerciales - Terceros'),
    ('13', 'Cuentas por Cobrar Comerciales - Relacionadas'),
    ('14', 'Cuentas por Cobrar al Personal, Accionistas, Directores y Gerentes'),
    ('16', 'Cuentas por Cobrar Diversas - Terceros'),
    ('17', 'Cuentas por Cobrar Diversas - Relacionadas'),
    ('19', 'Estimación de Cobranza Dudosa'),
)
PAYABLE_GROUPS = (
    ('40', 'Tributos, Contraprestaciones y Aportes por Pagar'),
    ('41', 'Remuneraciones y Participaciones por Pagar'),
    ('42', 'Cuentas por Pagar Comerciales - Terceros'),
    ('43', 'Cuentas por Pagar Comerciales - Relacionadas'),
    ('44', 'Cuentas por Pagar a Accionistas, Directores y Gerentes'),
    ('45', 'Obligaciones Financieras'),
    ('46', 'Cuentas por Pagar Diversas - Terceros'),
)


def normalize_report_date(year=None, month=None, day=None):
    today = date.today()
    selected_year = int(year or today.year)
    selected_month = min(12, max(1, int(month or today.month)))
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    selected_day = min(last_day, max(1, int(day or min(today.day, last_day))))
    return date(selected_year, selected_month, selected_day)


def empty_cash_liquidation_report(report_date=None):
    report_date = report_date or date.today()
    years = list(range(FIRST_REPORT_YEAR, max(FIRST_REPORT_YEAR, date.today().year) + 1))
    return {
        'months': MONTHS,
        'years': years,
        'selected': {
            'year': report_date.year,
            'month': report_date.month,
            'day': report_date.day,
            'last_day': calendar.monthrange(report_date.year, report_date.month)[1],
            'label': '{} {}'.format(MONTHS[report_date.month - 1], report_date.year),
        },
        'receivables': [
            {'account': account, 'label': label, 'amount': 0.0}
            for account, label in RECEIVABLE_GROUPS
        ],
        'payables': [
            {'account': account, 'label': label, 'amount': 0.0}
            for account, label in PAYABLE_GROUPS
        ],
        'receivable_total': 0.0,
        'payable_total': 0.0,
        'net_position': 0.0,
        'coverage': 0.0,
        'source': 'NISIRA ERP · Balance General',
    }


def build_cash_liquidation_report(rows, report_date=None):
    report_date = report_date or date.today()
    report = empty_cash_liquidation_report(report_date)
    receivable_accounts = {account for account, unused_label in RECEIVABLE_GROUPS}
    payable_accounts = {account for account, unused_label in PAYABLE_GROUPS}
    receivable_totals = {account: Decimal('0') for account in receivable_accounts}
    payable_totals = {account: Decimal('0') for account in payable_accounts}

    for row in rows:
        account = str(row[0] or '').strip()
        prefix = account[:2]
        debit = Decimal(str(row[3] or 0))
        credit = Decimal(str(row[4] or 0))
        if prefix in receivable_accounts:
            receivable_totals[prefix] += max(debit - credit, Decimal('0'))
        elif prefix in payable_accounts:
            payable_totals[prefix] += max(credit - debit, Decimal('0'))

    for item in report['receivables']:
        item['amount'] = float(receivable_totals[item['account']])
    for item in report['payables']:
        item['amount'] = float(payable_totals[item['account']])
    report['receivable_total'] = round(sum(item['amount'] for item in report['receivables']), 2)
    report['payable_total'] = round(sum(item['amount'] for item in report['payables']), 2)
    report['net_position'] = round(report['receivable_total'] - report['payable_total'], 2)
    report['coverage'] = round(
        report['receivable_total'] / report['payable_total'] * 100, 2
    ) if report['payable_total'] else 0.0
    return report


def get_cash_liquidation_report(report_date=None):
    report_date = report_date or date.today()
    cache_key = 'contabilidad:liquidacion-caja:{}:v1'.format(report_date.isoformat())
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    with connections['payroll'].cursor() as cursor:
        cursor.execute(
            'EXEC CONT_RPT_BALANCEGENERAL %s, %s, %s, %s',
            ['001', report_date.strftime('%Y%m%d'), 'S', ''],
        )
        while cursor.description is None and cursor.nextset():
            pass
        rows = cursor.fetchall() if cursor.description is not None else []

    report = build_cash_liquidation_report(rows, report_date=report_date)
    cache.set(cache_key, report, CACHE_SECONDS)
    return report
