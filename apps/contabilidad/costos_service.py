from datetime import date

from django.core.cache import cache
from django.db import connections


MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
FIRST_REPORT_YEAR = 2023
CACHE_KEY = 'contabilidad:costos:nisira:v1'
CACHE_SECONDS = 10 * 60

COSTS_SQL = """
SELECT C.IDCNFDISTRIBUCION, C.FECHA, C.PERIODO, C.IDDOCUMENTO, C.SERIE, C.NUMERO,
       C.IDCLASECCOSTO, COALESCE(NULLIF(LTRIM(RTRIM(CC.DESCRIPCION)), ''), 'SIN CLASE'),
       C.IDESTADO, C.CONFIGURADO, C.DISTRIBUIDO, C.COSTEADO,
       COUNT(D.IDCUENTA), SUM(ISNULL(D.IMPORTE, 0))
FROM CNFDISTRIBUCION C WITH (NOLOCK)
LEFT JOIN CLASESCCOSTO CC WITH (NOLOCK)
  ON CC.IDEMPRESA=C.IDEMPRESA AND CC.IDCLASECCOSTO=C.IDCLASECCOSTO
LEFT JOIN DCNFDISTRIBUCION D WITH (NOLOCK)
  ON D.IDEMPRESA=C.IDEMPRESA AND D.IDCNFDISTRIBUCION=C.IDCNFDISTRIBUCION
WHERE C.IDEMPRESA=%s AND C.FECHA >= %s AND C.FECHA < %s AND C.IDESTADO <> 'AN'
GROUP BY C.IDCNFDISTRIBUCION, C.FECHA, C.PERIODO, C.IDDOCUMENTO, C.SERIE, C.NUMERO,
         C.IDCLASECCOSTO, CC.DESCRIPCION, C.IDESTADO, C.CONFIGURADO, C.DISTRIBUIDO, C.COSTEADO
ORDER BY C.FECHA, C.NUMERO
"""


def empty_costs_report(current_year=None):
    current_year = current_year or date.today().year
    return {'months': MONTHS, 'years': list(range(FIRST_REPORT_YEAR, current_year + 1)), 'classes': [], 'records': [], 'source': 'NISIRA ERP · Distribución y Asiento de Costos'}


def build_costs_report(rows, current_year=None):
    report = empty_costs_report(current_year)
    records = []
    for row in rows:
        record_date = row[1]
        class_code = str(row[6] or '').strip()
        class_name = str(row[7] or '').strip()
        state_code = str(row[8] or '').strip()
        records.append({
            'id': str(row[0]).strip(), 'date': record_date.strftime('%Y-%m-%d'),
            'year': record_date.year, 'month': record_date.month - 1, 'period': str(row[2]).strip(),
            'document': str(row[3]).strip(), 'series': str(row[4]).strip(), 'number': str(row[5]).strip(),
            'class_code': class_code, 'class_name': class_name,
            'state': 'Pendiente' if state_code == 'PE' else state_code,
            'configured': bool(row[9]), 'distributed': bool(row[10]), 'costed': bool(row[11]),
            'detail_count': int(row[12] or 0), 'amount': float(row[13] or 0),
        })
    report['records'] = records
    report['classes'] = sorted({item['class_code'] + ' ' + item['class_name'] for item in records})
    return report


def get_costs_report():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached
    today = date.today()
    with connections['payroll'].cursor() as cursor:
        cursor.execute(COSTS_SQL, ['001', date(FIRST_REPORT_YEAR, 1, 1), date(today.year + 1, 1, 1)])
        rows = cursor.fetchall()
    report = build_costs_report(rows, today.year)
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
