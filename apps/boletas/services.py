import logging
from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import connections


logger = logging.getLogger(__name__)

PAYROLL_TYPES = (
    ("ERG", "EMPLEADOS REGIMEN GENERAL"),
    ("ERA", "EMPLEADOS REGIMEN AGRARIO"),
    ("OBP", "OBREROS PLANTA"),
    ("OBR", "OBREROS PLANTA GENERAL"),
)
PAYROLL_PLAN_IDS = {
    "ERG": "ERG",
    "ERA": "ERA",
    "OBP": "OBP",
    "OBR": "OBR",
}


class PaySlipService:
    HEADER_PROCEDURE = "GETTABLE_RE_BOLETAS_CABECERA_WEB_ASL"
    DETAIL_PROCEDURE = "GETTABLE_RE_BOLETAS_DETALLE_WEB_ASL"

    def __init__(self, company_id=None, currency=None):
        self.company_id = company_id or settings.PAYSLIP_COMPANY_ID
        self.currency = currency or settings.PAYSLIP_CURRENCY

    def list(self, date_range):
        from .periods import visible_period
        date_range = visible_period(date_range)
        if date_range is None:
            return []
        params = [
            self.company_id,
            date_range.start_sql,
            date_range.end_sql,
            self.currency,
        ]
        headers = self._execute(self.HEADER_PROCEDURE, params)
        details = self._execute(self.DETAIL_PROCEDURE, params)
        if headers and not details:
            details = self._list_raw_details(date_range)
        details_by_worker = defaultdict(list)

        for item in details:
            details_by_worker[self._detail_key(item)].append(item)

        slips = []
        for header in headers:
            concepts = details_by_worker.get(self._header_key(header), [])
            concept_sets = [concepts]
            if str(header.get("grupo_planilla") or "").strip() == "01" and any(
                item.get("movement_id") for item in concepts
            ):
                by_movement = defaultdict(list)
                for item in concepts:
                    by_movement[item.get("movement_id")].append(item)
                concept_sets = sorted(
                    by_movement.values(),
                    key=lambda rows: (str(rows[0].get("movement_type") or "") != "N", str(rows[0].get("movement_id") or "")),
                )

            for movement_concepts in concept_sets:
                slip = dict(header)
                income = sum(
                    (self._amount(item) for item in movement_concepts if self._is_income(item)),
                    Decimal("0"),
                )
                deductions = sum(
                    (self._amount(item) for item in movement_concepts if self._is_deduction(item)),
                    Decimal("0"),
                )

                def official_total(code, fallback):
                    match = next(
                        (
                            item for item in movement_concepts
                            if str(item.get("codigo_equiv") or "").strip().upper() == code
                        ),
                        None,
                    )
                    return self._amount(match) if match else fallback

                movement_payroll = next(
                    (
                        str(item.get("payroll_type") or "").strip().upper()
                        for item in movement_concepts
                        if str(item.get("payroll_type") or "").strip().upper() in PAYROLL_PLAN_IDS
                    ),
                    "",
                )
                slip["payroll_type"] = movement_payroll or self.payroll_type(slip)
                slip["payroll_type_label"] = dict(PAYROLL_TYPES).get(
                    slip["payroll_type"], "OTRA PLANILLA"
                )
                slip["movement_id"] = movement_concepts[0].get("movement_id") if movement_concepts else ""
                slip["movement_type"] = movement_concepts[0].get("movement_type") if movement_concepts else ""
                slip["concepts"] = movement_concepts
                slip["income_total"] = official_total("TOT_IN", income)
                slip["deduction_total"] = official_total("TOT_DE", deductions)
                slip["net_total"] = official_total("TO0002", slip["income_total"] - slip["deduction_total"])
                slips.append(slip)

        return slips

    def payroll_weeks(self, period, payroll_type="OBP"):
        """Return the official weekly calendar stored by payroll."""
        sql = """
            SELECT
                RTRIM(SEMANA) AS week_number,
                FECHA_INI AS start_date,
                FECHA_FIN AS end_date,
                RTRIM(ISNULL(SEMANA_EQV, '')) AS equivalent_week
            FROM PERIODO_PLANILLA WITH (NOLOCK)
            WHERE RTRIM(IDEMPRESA) = %s
              AND RTRIM(IDPLANILLA) = %s
              AND RTRIM(PERIODO) = %s
              AND LTRIM(RTRIM(ISNULL(SEMANA, ''))) <> ''
            ORDER BY FECHA_INI, SEMANA
        """
        with connections["payroll"].cursor() as cursor:
            cursor.execute(sql, [self.company_id, payroll_type, period.replace("-", "")])
            return [
                {
                    "number": str(row[0]).strip(),
                    "start": row[1].date() if hasattr(row[1], "date") else row[1],
                    "end": row[2].date() if hasattr(row[2], "date") else row[2],
                    "equivalent": str(row[3] or "").strip(),
                }
                for row in cursor.fetchall()
            ]

    def payroll_periods(self):
        """Return processed periods from payroll movements (from January 2026)."""
        cache_key = "boletas:periods:{}".format(self.company_id)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        sql = """
            SELECT DISTINCT LEFT(RTRIM(m.periodo_planilla), 6)
            FROM movimiento_planilla m WITH (NOLOCK)
            WHERE RTRIM(m.idempresa) = %s
              AND LEFT(RTRIM(m.periodo_planilla), 6) >= '202608'
              AND LEN(LEFT(RTRIM(m.periodo_planilla), 6)) = 6
              AND RTRIM(m.idplanilla) IN ('ERG', 'ERA', 'OBP', 'OBR')
              AND EXISTS (
                  SELECT 1
                  FROM deta_movimiento_planilla d WITH (NOLOCK)
                  WHERE d.idempresa = m.idempresa
                    AND d.idmovimiento = m.idmovimiento
              )
            ORDER BY LEFT(RTRIM(m.periodo_planilla), 6) DESC
        """
        with connections["payroll"].cursor() as cursor:
            cursor.execute(sql, [self.company_id])
            values = [str(row[0]).strip() for row in cursor.fetchall()]
            cache.set(cache_key, values, 600)
            return values

    def worker_payroll_periods(self, document, minimum_period="202608"):
        """Return only periods where the worker has actual payroll detail."""
        sql = """
            SELECT DISTINCT LEFT(RTRIM(m.periodo_planilla), 6) AS payroll_period
            FROM movimiento_planilla m WITH (NOLOCK)
            INNER JOIN personal_general pg WITH (NOLOCK)
                ON pg.idcodigogeneral = m.idcodigogeneral
            WHERE RTRIM(m.idempresa) = %s
              AND RTRIM(pg.nrodocumento) = %s
              AND LEFT(RTRIM(m.periodo_planilla), 6) >= %s
              AND RTRIM(m.idplanilla) IN ('ERG', 'ERA', 'OBP', 'OBR')
              AND EXISTS (
                  SELECT 1
                  FROM deta_movimiento_planilla d WITH (NOLOCK)
                  WHERE d.idempresa = m.idempresa
                    AND d.idmovimiento = m.idmovimiento
              )
            ORDER BY LEFT(RTRIM(m.periodo_planilla), 6) DESC
        """
        with connections["payroll"].cursor() as cursor:
            cursor.execute(sql, [self.company_id, document, minimum_period])
            return [str(row[0]).strip() for row in cursor.fetchall()]

    def monthly_net(self, year, payroll_type="", position=""):
        """Return monthly net payroll totals for a calendar year."""
        sql = """
            SELECT
                LEFT(m.periodo_planilla, 6) AS payroll_month,
                SUM(
                    CASE
                        WHEN c.idtipoconcepto = 'IN' THEN ISNULL(d.calculo, 0)
                        WHEN c.idtipoconcepto = 'DE' THEN -ISNULL(d.calculo, 0)
                        ELSE 0
                    END
                ) AS net_total
            FROM movimiento_planilla m WITH (NOLOCK)
            INNER JOIN deta_movimiento_planilla d WITH (NOLOCK)
                ON d.idempresa = m.idempresa
                AND d.idmovimiento = m.idmovimiento
            INNER JOIN conceptos c WITH (NOLOCK)
                ON c.idempresa = d.idempresa
                AND c.idconcepto = d.idconcepto
            LEFT JOIN personal p WITH (NOLOCK)
                ON p.idempresa = m.idempresa
                AND p.idcodigogeneral = m.idcodigogeneral
                AND p.idplanilla = m.idplanilla
            LEFT JOIN cargos_personal cp WITH (NOLOCK)
                ON cp.idempresa = p.idempresa
                AND cp.idcargo = p.idcargo
            WHERE m.idempresa = %s
                AND LEFT(m.periodo_planilla, 4) = %s
                AND LEFT(m.periodo_planilla, 6) >= '202608'
                AND RTRIM(m.idplanilla) IN ('ERG', 'ERA', 'OBP', 'OBR')
                AND (%s = '' OR RTRIM(m.idplanilla) = %s)
                AND (%s = '' OR RTRIM(ISNULL(cp.descripcion, 'SIN CARGO')) = %s)
            GROUP BY LEFT(m.periodo_planilla, 6)
            ORDER BY LEFT(m.periodo_planilla, 6)
        """
        plan_id = PAYROLL_PLAN_IDS.get(payroll_type, "")
        params = [
            self.company_id,
            str(year),
            plan_id,
            plan_id,
            position,
            position,
        ]
        with connections["payroll"].cursor() as cursor:
            cursor.execute(sql, params)
            values = {
                str(row[0]).strip(): Decimal(str(row[1] or 0))
                for row in cursor.fetchall()
            }
        return [
            {
                "month": "{}{:02d}".format(year, month),
                "net": values.get("{}{:02d}".format(year, month), Decimal("0")),
            }
            for month in range(1, 13)
        ]

    def _execute(self, procedure, params):
        sql = "EXEC {} %s, %s, %s, %s".format(procedure)
        with connections["payroll"].cursor() as cursor:
            cursor.execute(sql, params)
            while cursor.description is None:
                if not cursor.nextset():
                    return []
            columns = [column[0] for column in cursor.description]
            return [
                {
                    key: value.strip() if isinstance(value, str) else value
                    for key, value in zip(columns, row)
                }
                for row in cursor.fetchall()
            ]

    def _list_raw_details(self, date_range):
        sql = """
            DECLARE @periods TABLE (
                idempresa char(3), idplanilla char(6), anio char(4),
                periodo char(6), semana char(2), fecha_ini datetime,
                fecha_fin datetime
            );
            INSERT INTO @periods
            EXEC nsp_periodo_planilla_listar_xfechas_ext %s, %s, %s;

            SELECT
                m.idcodigogeneral,
                RTRIM(m.idplanilla) AS payroll_type,
                m.idmovimiento AS movement_id,
                RTRIM(ISNULL(m.tipo, '')) AS movement_type,
                CASE
                    WHEN RTRIM(m.idplanilla) IN ('ERG', 'ERA') THEN '01'
                    WHEN RTRIM(m.idplanilla) IN ('OBP', 'OBR') THEN '02'
                    ELSE ''
                END AS grupo_planilla,
                d.idconcepto AS codigo_equiv,
                c.descripcion,
                c.idtipoconcepto,
                CASE c.idtipoconcepto
                    WHEN 'IN' THEN 1
                    WHEN 'AE' THEN 2
                    WHEN 'DE' THEN 3
                    ELSE 0
                END AS tipoconcepto,
                SUM(d.calculo) AS importe
            FROM @periods p
            INNER JOIN movimiento_planilla m WITH (NOLOCK)
                ON p.idempresa = m.idempresa
                AND p.idplanilla = m.idplanilla
                AND p.periodo = m.periodo_planilla
                AND p.semana = m.semana
            INNER JOIN deta_movimiento_planilla d WITH (NOLOCK)
                ON d.idempresa = m.idempresa
                AND d.idmovimiento = m.idmovimiento
            INNER JOIN conceptos c WITH (NOLOCK)
                ON c.idempresa = d.idempresa
                AND c.idconcepto = d.idconcepto
            WHERE m.idempresa = %s
                AND ISNULL(d.calculo, 0) <> 0
            GROUP BY
                m.idcodigogeneral, RTRIM(m.idplanilla), m.idmovimiento, RTRIM(ISNULL(m.tipo, '')),
                CASE
                    WHEN RTRIM(m.idplanilla) IN ('ERG', 'ERA') THEN '01'
                    WHEN RTRIM(m.idplanilla) IN ('OBP', 'OBR') THEN '02'
                    ELSE ''
                END,
                d.idconcepto,
                c.descripcion, c.idtipoconcepto
            ORDER BY m.idcodigogeneral, c.idtipoconcepto, d.idconcepto
        """
        params = [
            self.company_id,
            date_range.start_sql,
            date_range.end_sql,
            self.company_id,
        ]
        with connections["payroll"].cursor() as cursor:
            cursor.execute(sql, params)
            while cursor.description is None:
                if not cursor.nextset():
                    return []
            columns = [column[0] for column in cursor.description]
            return [
                {
                    key: value.strip() if isinstance(value, str) else value
                    for key, value in zip(columns, row)
                }
                for row in cursor.fetchall()
            ]

    @staticmethod
    def _header_key(item):
        return (
            str(item.get("idcodigogeneral") or "").strip(),
            str(item.get("grupo_planilla") or "").strip(),
        )

    @staticmethod
    def _detail_key(item):
        return (
            str(item.get("idcodigogeneral") or "").strip(),
            str(item.get("grupo_planilla") or "").strip(),
        )

    @staticmethod
    def payroll_type(item):
        group = str(item.get("grupo_planilla") or "").strip()
        regime = str(item.get("IDREGIMENLABORAL") or "").strip()
        if group == "01":
            return "ERG" if regime == "01" else "ERA"
        if group == "02":
            return "OBR" if regime == "01" else "OBP"
        return ""

    @staticmethod
    def _amount(item):
        return Decimal(str(item.get("importe") or 0))

    @staticmethod
    def _is_income(item):
        if str(item.get("idtipoconcepto") or "").strip().upper() == "IN":
            return True
        value = "{} {}".format(
            item.get("idtipoconcepto") or "",
            item.get("tipoconcepto") or "",
        ).upper()
        return any(word in value for word in ("INGRES", "REMUN", "HABER"))

    @staticmethod
    def _is_deduction(item):
        if str(item.get("idtipoconcepto") or "").strip().upper() == "DE":
            return True
        value = "{} {}".format(
            item.get("idtipoconcepto") or "",
            item.get("tipoconcepto") or "",
        ).upper()
        return any(word in value for word in ("DESCU", "DEDUC", "RETENC"))
