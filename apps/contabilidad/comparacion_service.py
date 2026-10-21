from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import connections


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
FIRST_REPORT_YEAR = 2023
CACHE_KEY = 'contabilidad:comparacion:nisira:v1'
CACHE_SECONDS = 10 * 60
DEFAULT_USD_RATE = Decimal('3.30')

METRICS = [
    {'key': 'boxes_maquila', 'label': 'CAJAS PROCESADAS MAQUILA', 'format': 'number'},
    {'key': 'boxes_export', 'label': 'CAJAS PROCESADAS EXPORTACIÓN', 'format': 'number'},
    {'key': 'kilos_maquila', 'label': 'KILOS PROCESADOS MAQUILA', 'format': 'kilos'},
    {'key': 'kilos_export', 'label': 'KILOS PROCESADOS EXPORTACIÓN', 'format': 'kilos'},
    {'key': 'income_maquila', 'label': 'INGRESOS - MAQUILA', 'format': 'pen'},
    {'key': 'income_export', 'label': 'INGRESOS - EXPORTACIÓN', 'format': 'pen'},
    {'key': 'income_goods', 'label': 'INGRESOS MERCADERÍAS', 'format': 'pen'},
    {'key': 'cost_maquila', 'label': 'COSTO MAQUILA', 'format': 'pen'},
    {'key': 'cost_export', 'label': 'COSTO EXPORTACIÓN', 'format': 'pen'},
    {'key': 'cost_goods', 'label': 'COSTO MERCADERÍA', 'format': 'pen'},
    {'key': 'other_income', 'label': 'OTROS INGRESOS', 'format': 'pen'},
    {'key': 'other_expenses', 'label': 'OTROS GASTOS', 'format': 'pen'},
    {'key': 'profit_sharing', 'label': 'PARTICIPACIÓN DE UTILIDADES', 'format': 'pen'},
    {'key': 'income_tax', 'label': 'IMPUESTO A LA RENTA', 'format': 'pen'},
    {'key': 'result_pen', 'label': 'RESULTADO SOLES', 'format': 'pen'},
    {'key': 'result_usd', 'label': 'RESULTADO DÓLARES', 'format': 'usd'},
]


PRODUCTION_SQL = """
SELECT
    YEAR(R.FECHA) AS production_year,
    MONTH(R.FECHA) AS production_month,
    CASE
        WHEN UPPER(LTRIM(RTRIM(COALESCE(CL.NOMCORTO, '')))) = 'AGROSERVICE'
            THEN 'EXPORTACION'
        ELSE 'MAQUILA'
    END AS production_type,
    SUM(CAST(DR.CANTIDAD AS decimal(19, 3))) AS boxes,
    SUM(CAST(COALESCE(PRD.KG_CAJAS, 0) * DR.CANTIDAD AS decimal(19, 3))) AS kilograms
FROM REGISTROPALETA R WITH (NOLOCK)
INNER JOIN DREGISTROPALETA DR WITH (NOLOCK)
    ON DR.IDREGISTROPALETA = R.IDREGISTROPALETA
   AND DR.IDEMPRESA = R.IDEMPRESA
INNER JOIN MOTIVOPALETA MP WITH (NOLOCK)
    ON MP.IDMOTIVOPALETA = R.IDMOTIVOPALETA
   AND MP.IDEMPRESA = R.IDEMPRESA
   AND MP.TIPO_TARJA IN (1, 2)
INNER JOIN PRODUCTOS PRD WITH (NOLOCK)
    ON PRD.IDPRODUCTO = DR.IDPRODUCTO
   AND PRD.IDEMPRESA = DR.IDEMPRESA
LEFT JOIN PROVEEDORLOTE CL WITH (NOLOCK)
    ON CL.IDCLIEPROV = R.IDCLIEPROV
   AND CL.IDEMPRESA = R.IDEMPRESA
WHERE R.IDEMPRESA = %s
  AND R.IDESTADO <> 'AN'
  AND R.FECHA >= %s
  AND R.FECHA < %s
GROUP BY
    YEAR(R.FECHA), MONTH(R.FECHA),
    CASE
        WHEN UPPER(LTRIM(RTRIM(COALESCE(CL.NOMCORTO, '')))) = 'AGROSERVICE'
            THEN 'EXPORTACION'
        ELSE 'MAQUILA'
    END
ORDER BY production_year, production_month, production_type
"""


def _empty_values(years):
    return {str(year): [0.0] * 12 for year in years}


def empty_comparison_report(current_year=None):
    current_year = current_year or date.today().year
    years = list(range(FIRST_REPORT_YEAR, max(FIRST_REPORT_YEAR, current_year) + 1))
    return {
        'months': MONTHS,
        'years': years,
        'metrics': [dict(metric, values=_empty_values(years)) for metric in METRICS],
        'usd_rate': float(DEFAULT_USD_RATE),
        'source': 'NISIRA ERP · Producción y Estado de Ganancias y Pérdidas por Función',
    }


def _metric_map(report):
    return {metric['key']: metric['values'] for metric in report['metrics']}


def _account_group(account):
    return str(account or '').strip()


def build_comparison_report(production_rows, financial_rows_by_year, current_year=None, usd_rate=None):
    report = empty_comparison_report(current_year=current_year)
    values = _metric_map(report)
    years = {str(year) for year in report['years']}
    rate = Decimal(str(usd_rate or DEFAULT_USD_RATE))

    for row_year, row_month, production_type, boxes, kilograms in production_rows:
        year = str(int(row_year))
        if year not in years:
            continue
        index = int(row_month) - 1
        suffix = 'export' if str(production_type).strip().upper() == 'EXPORTACION' else 'maquila'
        values['boxes_' + suffix][year][index] += float(boxes or 0)
        values['kilos_' + suffix][year][index] += float(kilograms or 0)

    for query_year, rows in financial_rows_by_year.items():
        year = str(int(query_year))
        if year not in years:
            continue
        for period, account, debit_pen, credit_pen, _debit_usd, _credit_usd in rows:
            period = str(period).strip()
            if len(period) < 6 or period[:4] != year:
                continue
            index = int(period[4:6]) - 1
            account = _account_group(account)
            amount = Decimal(str(credit_pen or 0)) - Decimal(str(debit_pen or 0))

            if account.startswith('704'):
                values['income_maquila'][year][index] += float(amount)
            elif account.startswith(('702', '703')):
                values['income_export'][year][index] += float(amount)
            elif account.startswith('701'):
                values['income_goods'][year][index] += float(amount)
            elif account.startswith('694'):
                values['cost_maquila'][year][index] += float(amount)
            elif account.startswith(('692', '693')):
                values['cost_export'][year][index] += float(amount)
            elif account.startswith('691'):
                values['cost_goods'][year][index] += float(amount)
            elif account.startswith(('73', '75', '77')):
                values['other_income'][year][index] += float(amount)
            elif account.startswith(('94', '95', '97')):
                values['other_expenses'][year][index] += float(amount)
            elif account.startswith('87'):
                values['profit_sharing'][year][index] += float(amount)
            elif account.startswith('88'):
                values['income_tax'][year][index] += float(amount)

            values['result_pen'][year][index] += float(amount)

        values['result_usd'][year] = [
            float(Decimal(str(amount)) / rate) for amount in values['result_pen'][year]
        ]

    report['usd_rate'] = float(rate)
    return report


def _fetch_financial_rows(cursor, year):
    cursor.execute(
        "EXEC CONT_RPT_EEGGPP_FN %s, %s, %s, %s, %s, %s, %s",
        ['001', '{}01'.format(year), '{}12'.format(year), 'F', 'EF001', 1, '01'],
    )
    while cursor.description is None and cursor.nextset():
        pass
    return cursor.fetchall() if cursor.description is not None else []


def get_comparison_report():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    today = date.today()
    years = list(range(FIRST_REPORT_YEAR, today.year + 1))
    with connections['payroll'].cursor() as cursor:
        cursor.execute(
            PRODUCTION_SQL,
            ['001', date(FIRST_REPORT_YEAR, 1, 1), date(today.year + 1, 1, 1)],
        )
        production_rows = cursor.fetchall()
        financial_rows = {year: _fetch_financial_rows(cursor, year) for year in years}

    report = build_comparison_report(
        production_rows,
        financial_rows,
        current_year=today.year,
        usd_rate=getattr(settings, 'COMPARISON_USD_RATE', DEFAULT_USD_RATE),
    )
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
