import calendar
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.cache import caches
from django.db import connections


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
FIRST_REPORT_YEAR = 2023
CURRENT_DATE_CACHE_SECONDS = 10 * 60
HISTORICAL_CACHE_SECONDS = 30 * 24 * 60 * 60
report_cache = (
    caches['reports']
    if 'reports' in settings.CACHES
    else caches['default']
)

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

TARGET_ACCOUNT_PREFIXES = ('10', '12', '13', '14', '16', '17', '19', '40', '41', '42', '43', '44', '45', '46')
TARGET_ACCOUNT_FILTER = ' OR '.join(
    "(d.idcuenta >= '{0}' AND d.idcuenta < '{1}')".format(prefix, str(int(prefix) + 1).zfill(2))
    for prefix in TARGET_ACCOUNT_PREFIXES
)
FAST_BALANCE_SQL = """
SELECT d.idcuenta,
       p.naturaleza,
       CAST('' AS varchar(1)) AS cl_tipo,
       SUM(ISNULL(d.cargo_mof, 0)) AS cargo_mof,
       SUM(ISNULL(d.abono_mof, 0)) AS abono_mof,
       SUM(ISNULL(d.cargo_mex, 0)) AS cargo_mex,
       SUM(ISNULL(d.abono_mex, 0)) AS abono_mex,
       0 AS cargo_mof1,
       0 AS abono_mof1,
       0 AS cargo_mex1,
       0 AS abono_mex1
FROM cabconta c WITH (NOLOCK)
JOIN detconta d WITH (NOLOCK)
  ON c.idcabconta = d.idcabconta AND c.idempresa = d.idempresa
JOIN planctas p WITH (NOLOCK)
  ON d.idcuenta = p.idcuenta AND d.idempresa = p.idempresa
WHERE c.fecha <= %s
  AND c.idempresa = %s
  AND c.idestado <> 'AN'
  AND p.TIPO_CUENTA = 'B'
  AND (c.es_cierre = 0 OR (c.es_cierre = 1 AND c.periodo <> %s))
  AND ({account_filter})
GROUP BY d.idcuenta, p.naturaleza
ORDER BY d.idcuenta
""".format(account_filter=TARGET_ACCOUNT_FILTER)


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
        'cash_total': 0.0,
        'payables': [
            {'account': account, 'label': label, 'amount': 0.0}
            for account, label in PAYABLE_GROUPS
        ],
        'receivable_total': 0.0,
        'available_total': 0.0,
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
    cash_total = Decimal('0')

    for row in rows:
        account = str(row[0] or '').strip()
        prefix = account[:2]
        debit = Decimal(str(row[3] or 0))
        credit = Decimal(str(row[4] or 0))
        if prefix == '10':
            cash_total += max(debit - credit, Decimal('0'))
        elif prefix in receivable_accounts:
            receivable_totals[prefix] += max(debit - credit, Decimal('0'))
        elif prefix in payable_accounts:
            payable_totals[prefix] += max(credit - debit, Decimal('0'))

    for item in report['receivables']:
        item['amount'] = float(receivable_totals[item['account']])
    for item in report['payables']:
        item['amount'] = float(payable_totals[item['account']])
    report['cash_total'] = round(float(cash_total), 2)
    report['receivable_total'] = round(sum(item['amount'] for item in report['receivables']), 2)
    report['available_total'] = round(report['cash_total'] + report['receivable_total'], 2)
    report['payable_total'] = round(sum(item['amount'] for item in report['payables']), 2)
    report['net_position'] = round(report['available_total'] - report['payable_total'], 2)
    report['coverage'] = round(
        report['available_total'] / report['payable_total'] * 100, 2
    ) if report['payable_total'] else 0.0
    return report


def get_cash_liquidation_report(report_date=None):
    report_date = report_date or date.today()
    cache_key = 'contabilidad:liquidacion-caja:{}:v3'.format(report_date.isoformat())
    cached = report_cache.get(cache_key)
    if cached is not None:
        return cached

    report_cutoff = report_date.strftime('%Y-%m-%d 23:59:59.997')
    try:
        with connections['payroll'].cursor() as cursor:
            cursor.execute(
                FAST_BALANCE_SQL,
                [report_cutoff, '001', report_date.strftime('%Y%m')],
            )
            rows = cursor.fetchall()
    except Exception:
        # Compatibilidad ante cambios futuros del esquema de NISIRA.
        with connections['payroll'].cursor() as cursor:
            cursor.execute(
                'EXEC CONT_RPT_BALANCEGENERAL %s, %s, %s, %s',
                ['001', report_date.strftime('%Y%m%d'), 'S', ''],
            )
            while cursor.description is None and cursor.nextset():
                pass
            rows = cursor.fetchall() if cursor.description is not None else []

    report = build_cash_liquidation_report(rows, report_date=report_date)
    timeout = (
        CURRENT_DATE_CACHE_SECONDS
        if report_date >= date.today()
        else HISTORICAL_CACHE_SECONDS
    )
    report_cache.set(cache_key, report, timeout)
    return report
