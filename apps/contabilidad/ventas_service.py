from datetime import date

from django.core.cache import cache
from django.db import connections


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
FIRST_REPORT_YEAR = 2023
CACHE_KEY = 'contabilidad:ventas:nisira:v1'
CACHE_SECONDS = 10 * 60


def empty_sales_report(current_year=None):
    current_year = current_year or date.today().year
    years = list(range(FIRST_REPORT_YEAR, max(FIRST_REPORT_YEAR, current_year) + 1))
    return {
        'metric': 'Ventas',
        'currency': 'PEN',
        'months': MONTHS,
        'years': years,
        'data': {str(year): [None] * 12 for year in years},
        'data_usd': {str(year): [None] * 12 for year in years},
        'source': 'NISIRA ERP · Registro de Ventas',
    }


def build_sales_report(rows, current_year=None):
    report = empty_sales_report(current_year=current_year)
    for sale_date, total_pen, total_usd in rows:
        year = str(sale_date.year)
        if year not in report['data']:
            continue
        month_index = sale_date.month - 1
        if report['data'][year][month_index] is None:
            report['data'][year][month_index] = 0.0
            report['data_usd'][year][month_index] = 0.0
        report['data'][year][month_index] += float(total_pen or 0)
        report['data_usd'][year][month_index] += float(total_usd or 0)

    for dataset in (report['data'], report['data_usd']):
        for values in dataset.values():
            for index, value in enumerate(values):
                if value is not None:
                    values[index] = round(value, 2)
    return report


def get_sales_report():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    today = date.today()
    with connections['payroll'].cursor() as cursor:
        cursor.execute(
            'EXEC OBJREPORTES_REGISTROVENTAS %s, %s, %s, %s, %s, %s',
            [
                '001',
                f'{FIRST_REPORT_YEAR}01',
                f'{today.year}12',
                'N',
                '',
                0,
            ],
        )
        while cursor.description is None and cursor.nextset():
            pass
        columns = [column[0].upper() for column in cursor.description]
        date_index = columns.index('FECHA')
        total_index = columns.index('TOTAL')
        dollar_index = columns.index('TOTALUS')
        rows = [
            (row[date_index], row[total_index], row[dollar_index])
            for row in cursor.fetchall()
        ]

    report = build_sales_report(rows, current_year=today.year)
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
