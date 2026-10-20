from datetime import date

from django.core.cache import cache
from django.db import connections


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
FIRST_REPORT_YEAR = 2023
CACHE_KEY = 'contabilidad:cajas-kilos:nisira:v3'
CACHE_SECONDS = 10 * 60


PRODUCTION_SUMMARY_SQL = """
SELECT
    YEAR(R.FECHA) AS production_year,
    MONTH(R.FECHA) AS production_month,
    COALESCE(NULLIF(LTRIM(RTRIM(CL.NOMCORTO)), ''), 'SIN CLIENTE') AS client,
    COALESCE(NULLIF(LTRIM(RTRIM(PR.NOMCORTO)), ''), 'SIN PRODUCTOR') AS producer,
    SUM(CAST(DR.CANTIDAD AS decimal(19, 3))) AS boxes,
    SUM(CAST(PRD.KG_CAJAS * DR.CANTIDAD AS decimal(19, 3))) AS kilograms
FROM REGISTROPALETA R WITH (NOLOCK)
INNER JOIN DREGISTROPALETA DR WITH (NOLOCK)
    ON DR.IDREGISTROPALETA = R.IDREGISTROPALETA
   AND DR.IDEMPRESA = R.IDEMPRESA
INNER JOIN MOTIVOPALETA MP WITH (NOLOCK)
    ON R.IDMOTIVOPALETA = MP.IDMOTIVOPALETA
   AND R.IDEMPRESA = MP.IDEMPRESA
   AND MP.TIPO_TARJA IN (1, 2)
INNER JOIN PRODUCTOS PRD WITH (NOLOCK)
    ON DR.IDPRODUCTO = PRD.IDPRODUCTO
   AND DR.IDEMPRESA = PRD.IDEMPRESA
LEFT JOIN PROVEEDORLOTE CL WITH (NOLOCK)
    ON R.IDCLIEPROV = CL.IDCLIEPROV
   AND R.IDEMPRESA = CL.IDEMPRESA
LEFT JOIN PROVEEDORLOTE PR WITH (NOLOCK)
    ON DR.IDCLIEPROV = PR.IDCLIEPROV
   AND DR.IDEMPRESA = PR.IDEMPRESA
WHERE R.IDEMPRESA = %s
  AND R.IDESTADO <> 'AN'
  AND R.FECHA >= %s
  AND R.FECHA < %s
GROUP BY
    YEAR(R.FECHA),
    MONTH(R.FECHA),
    COALESCE(NULLIF(LTRIM(RTRIM(CL.NOMCORTO)), ''), 'SIN CLIENTE'),
    COALESCE(NULLIF(LTRIM(RTRIM(PR.NOMCORTO)), ''), 'SIN PRODUCTOR')
ORDER BY client, producer, production_year, production_month
"""


def _empty_report(years):
    return {
        'months': MONTHS,
        'years': years,
        'clients': [],
        'producers': [],
        'series': [],
        'metrics': {
            'cajas': {
                'label': 'Producción de cajas',
                'unit': 'cajas',
            },
            'kilos': {
                'label': 'Kilogramos procesados',
                'unit': 'kg',
            },
        },
        'source': 'NISIRA ERP · Producción de Cajas',
    }


def build_boxes_and_kilos_report(rows, current_year=None):
    current_year = current_year or date.today().year
    row_years = [int(row[0]) for row in rows]
    last_year = max([current_year, FIRST_REPORT_YEAR] + row_years)
    years = list(range(FIRST_REPORT_YEAR, last_year + 1))
    report = _empty_report(years)

    clients = sorted({str(row[2]).strip() for row in rows if str(row[2]).strip()})
    producers = sorted({str(row[3]).strip() for row in rows if str(row[3]).strip()})
    report['clients'] = clients
    report['producers'] = producers
    combinations = {}

    for production_year, production_month, client_name, producer_name, boxes, kilograms in rows:
        client = str(client_name).strip()
        producer = str(producer_name).strip()
        key = (client, producer)
        if key not in combinations:
            combinations[key] = {
                'client': client,
                'producer': producer,
                'cajas': {str(item): [None] * 12 for item in years},
                'kilos': {str(item): [None] * 12 for item in years},
            }
        year = str(int(production_year))
        month_index = int(production_month) - 1
        if year not in combinations[key]['cajas']:
            continue
        combinations[key]['cajas'][year][month_index] = float(boxes or 0)
        combinations[key]['kilos'][year][month_index] = float(kilograms or 0)

    report['series'] = list(combinations.values())

    return report


def get_boxes_and_kilos_report():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    today = date.today()
    start_date = date(FIRST_REPORT_YEAR, 1, 1)
    end_date = date(today.year + 1, 1, 1)
    with connections['payroll'].cursor() as cursor:
        cursor.execute(
            PRODUCTION_SUMMARY_SQL,
            ['001', start_date, end_date],
        )
        rows = cursor.fetchall()

    report = build_boxes_and_kilos_report(rows, current_year=today.year)
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
