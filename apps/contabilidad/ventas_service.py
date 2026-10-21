from datetime import date

from django.core.cache import cache
from django.db import connections


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
FIRST_REPORT_YEAR = 2023
CACHE_KEY = 'contabilidad:ventas:nisira:v2'
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
        'customers': [],
        'sales': [],
        'source': 'NISIRA ERP · Registro de Ventas',
    }


def build_sales_report(rows, current_year=None):
    report = empty_sales_report(current_year=current_year)
    sales = {}
    for row in rows:
        sale_date, total_pen, total_usd = row[:3]
        customer = str(row[3] or 'SIN RAZÓN SOCIAL').strip().upper() if len(row) > 3 else 'SIN RAZÓN SOCIAL'
        affected = float(row[4] or 0) if len(row) > 4 else 0.0
        exported = float(row[5] or 0) if len(row) > 5 else 0.0
        exempt = float(row[6] or 0) if len(row) > 6 else 0.0
        year = str(sale_date.year)
        if year not in report['data']:
            continue
        month_index = sale_date.month - 1
        if report['data'][year][month_index] is None:
            report['data'][year][month_index] = 0.0
            report['data_usd'][year][month_index] = 0.0
        report['data'][year][month_index] += float(total_pen or 0)
        report['data_usd'][year][month_index] += float(total_usd or 0)
        key = (int(year), month_index, customer)
        if key not in sales:
            sales[key] = {'year': int(year), 'month': month_index, 'customer': customer, 'total': 0.0, 'total_usd': 0.0, 'affected': 0.0, 'exported': 0.0, 'exempt': 0.0}
        sales[key]['total'] += float(total_pen or 0)
        sales[key]['total_usd'] += float(total_usd or 0)
        sales[key]['affected'] += affected
        sales[key]['exported'] += exported
        sales[key]['exempt'] += exempt

    for dataset in (report['data'], report['data_usd']):
        for values in dataset.values():
            for index, value in enumerate(values):
                if value is not None:
                    values[index] = round(value, 2)
    report['sales'] = [{key: round(value, 2) if isinstance(value, float) else value for key, value in item.items()} for item in sales.values()]
    report['customers'] = sorted({item['customer'] for item in report['sales']})
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
        customer_index = columns.index('RAZON_SOCIAL')
        affected_index = columns.index('BASEIMP_AFEC')
        export_index = columns.index('BASEIMP_EXPO')
        exempt_index = columns.index('BASEIMP_EXON')
        rows = [
            (row[date_index], row[total_index], row[dollar_index], row[customer_index], row[affected_index], row[export_index], row[exempt_index])
            for row in cursor.fetchall()
        ]

    report = build_sales_report(rows, current_year=today.year)
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
