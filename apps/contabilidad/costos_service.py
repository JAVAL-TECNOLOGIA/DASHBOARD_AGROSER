from datetime import date

from django.core.cache import cache
from django.db import connections


MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
FIRST_REPORT_YEAR = 2023
CACHE_KEY = 'contabilidad:costos:nisira:v5'
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

COST_DETAILS_SQL = """
;WITH COSTS AS (
    SELECT CP.PERIODO, CP.IDCLASECCOSTO, CP.IDCCOSTO, P.IDCLIEPROV,
           COALESCE(NULLIF(LTRIM(RTRIM(P.NOMCORTO)), ''), LTRIM(RTRIM(CC.DESCRIPCION))) AS CLIENT_NAME,
           SUM(ISNULL(CP.CST_MES, 0)) AS MONTH_COST,
           SUM(ISNULL(CP.CST_FINA, 0)) AS FINAL_COST
    FROM COSTOPRODUCCION CP WITH (NOLOCK)
    INNER JOIN C_COSTOS CC WITH (NOLOCK)
      ON CC.IDEMPRESA=CP.IDEMPRESA AND CC.IDCCOSTO=CP.IDCCOSTO
    LEFT JOIN PROVEEDORLOTE P WITH (NOLOCK)
      ON P.IDEMPRESA=CC.IDEMPRESA
     AND UPPER(REPLACE(REPLACE(LTRIM(RTRIM(P.RAZON_SOCIAL)), '.', ''), ' ', ''))=
         UPPER(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(CC.DESCRIPCION)), ' - VARIOS', ''), '.', ''), ' ', ''))
    WHERE CP.IDEMPRESA=%s AND CP.IDCLASECCOSTO IN ('0007', '0008') AND CP.PERIODO BETWEEN %s AND %s
    GROUP BY CP.PERIODO, CP.IDCLASECCOSTO, CP.IDCCOSTO, P.IDCLIEPROV,
             COALESCE(NULLIF(LTRIM(RTRIM(P.NOMCORTO)), ''), LTRIM(RTRIM(CC.DESCRIPCION)))
), PRODUCTION AS (
    SELECT D.PERIODO, D.IDCLASECCOSTO, D.IDCCOSTO,
           SUM(CAST(ISNULL(D.CANTIDAD, 0) AS DECIMAL(19,3))) AS BOXES,
           SUM(CAST(ISNULL(D.CANTIDADEQ, 0) AS DECIMAL(19,3))) AS KILOGRAMS
    FROM DCOSTOPRODUCCION D WITH (NOLOCK)
    WHERE D.IDEMPRESA=%s
      AND D.IDCLASECCOSTO IN ('0007', '0008')
      AND D.PERIODO BETWEEN %s AND %s
    GROUP BY D.PERIODO, D.IDCLASECCOSTO, D.IDCCOSTO
), OPERATIONAL_PRODUCTION AS (
    SELECT CONVERT(CHAR(6), R.FECHA, 112) AS PERIODO, R.IDCLIEPROV,
           SUM(CAST(PRD.KG_CAJAS * DR.CANTIDAD AS DECIMAL(19,3))) AS SUGGESTED_KILOGRAMS
    FROM REGISTROPALETA R WITH (NOLOCK)
    INNER JOIN DREGISTROPALETA DR WITH (NOLOCK)
      ON DR.IDEMPRESA=R.IDEMPRESA AND DR.IDREGISTROPALETA=R.IDREGISTROPALETA
    INNER JOIN MOTIVOPALETA MP WITH (NOLOCK)
      ON MP.IDEMPRESA=R.IDEMPRESA AND MP.IDMOTIVOPALETA=R.IDMOTIVOPALETA AND MP.TIPO_TARJA IN (1,2)
    INNER JOIN PRODUCTOS PRD WITH (NOLOCK)
      ON PRD.IDEMPRESA=DR.IDEMPRESA AND PRD.IDPRODUCTO=DR.IDPRODUCTO
    WHERE R.IDEMPRESA=%s
      AND R.IDESTADO<>'AN'
      AND CONVERT(CHAR(6), R.FECHA, 112) BETWEEN %s AND %s
    GROUP BY CONVERT(CHAR(6), R.FECHA, 112), R.IDCLIEPROV
)
SELECT C.PERIODO, C.IDCLASECCOSTO, C.CLIENT_NAME, C.MONTH_COST, C.FINAL_COST,
       ISNULL(P.BOXES, 0), ISNULL(P.KILOGRAMS, 0), ISNULL(OP.SUGGESTED_KILOGRAMS, 0)
FROM COSTS C
LEFT JOIN PRODUCTION P
  ON P.PERIODO=C.PERIODO
 AND P.IDCLASECCOSTO=C.IDCLASECCOSTO
 AND P.IDCCOSTO=C.IDCCOSTO
LEFT JOIN OPERATIONAL_PRODUCTION OP
  ON OP.PERIODO=C.PERIODO
 AND OP.IDCLIEPROV=C.IDCLIEPROV
ORDER BY C.PERIODO, C.CLIENT_NAME
"""


def empty_costs_report(current_year=None):
    current_year = current_year or date.today().year
    return {'months': MONTHS, 'years': list(range(FIRST_REPORT_YEAR, current_year + 1)), 'classes': [], 'records': [], 'details': [], 'source': 'NISIRA ERP · Distribución y Asiento de Costos'}


def build_costs_report(rows, current_year=None, detail_rows=None):
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
    report['details'] = [{
        'period': str(row[0]).strip(), 'year': int(str(row[0])[:4]), 'month': int(str(row[0])[4:6]) - 1,
        'class_code': str(row[1]).strip(), 'client': str(row[2]).strip(),
        'month_cost': float(row[3] or 0), 'final_cost': float(row[4] or 0),
        'boxes': float(row[5] or 0), 'kilograms': float(row[6] or 0),
        'suggested_kilograms': float((row[7] if len(row) > 7 else row[6]) or 0),
    } for row in (detail_rows or [])]
    return report


def get_costs_report():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached
    today = date.today()
    with connections['payroll'].cursor() as cursor:
        cursor.execute(COSTS_SQL, ['001', date(FIRST_REPORT_YEAR, 1, 1), date(today.year + 1, 1, 1)])
        rows = cursor.fetchall()
        first_period = str(FIRST_REPORT_YEAR) + '01'
        last_period = str(today.year) + '12'
        cursor.execute(COST_DETAILS_SQL, [
            '001', first_period, last_period,
            '001', first_period, last_period,
            '001', first_period, last_period,
        ])
        detail_rows = cursor.fetchall()
    report = build_costs_report(rows, today.year, detail_rows)
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
