from pathlib import Path

from django.conf import settings
from django.db import connections, transaction


class ContractService:
    connection_name = "payroll"

    def __init__(self, company_id=None):
        self.company_id = company_id or settings.PAYSLIP_COMPANY_ID

    def list_personnel(self, start_date, end_date):
        sql = """
            WITH personnel_company AS (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY idempresa, idcodigogeneral
                    ORDER BY fecha_ingreso DESC, item DESC
                ) AS row_number
                FROM personal_empresa WITH (NOLOCK)
                WHERE idempresa = %s
            ),
            latest_contract AS (
                SELECT c.*, ROW_NUMBER() OVER (
                    PARTITION BY c.idempresa, c.idcodigogeneral
                    ORDER BY TRY_CONVERT(int, c.idcontrato) DESC, c.fechacreacion DESC
                ) AS row_number
                FROM contrato c WITH (NOLOCK)
                WHERE c.idempresa = %s AND c.estado = 1
            )
            SELECT
                pg.idcodigogeneral,
                RTRIM(pg.nrodocumento) AS document,
                LTRIM(RTRIM(CONCAT(pg.a_paterno, ' ', pg.a_materno, ' ', pg.nombres))) AS full_name,
                pe.fecha_ingreso,
                pe.fecha_cese,
                RTRIM(p.idplanilla) AS payroll_id,
                RTRIM(pl.descripcion) AS payroll,
                RTRIM(ISNULL(cp.descripcion, 'SIN CARGO')) AS position,
                lc.idcontrato AS contract_id,
                lc.idtipocontrato AS contract_type_id,
                tc.descripcion AS contract_type,
                lc.inicio_contrato,
                lc.final_contrato,
                lc.basico,
                lc.firma_contrato,
                ISNULL(lc.firma_fisica, 0) AS physical_signature
            FROM personnel_company pe
            INNER JOIN personal_general pg WITH (NOLOCK)
                ON pg.idcodigogeneral = pe.idcodigogeneral
            LEFT JOIN personal p WITH (NOLOCK)
                ON p.idempresa = pe.idempresa
                AND p.idcodigogeneral = pe.idcodigogeneral
            LEFT JOIN planilla pl WITH (NOLOCK)
                ON pl.idempresa = p.idempresa AND pl.idplanilla = p.idplanilla
            LEFT JOIN cargos_personal cp WITH (NOLOCK)
                ON cp.idempresa = p.idempresa AND cp.idcargo = p.idcargo
            LEFT JOIN latest_contract lc
                ON lc.idempresa = pe.idempresa
                AND lc.idcodigogeneral = pe.idcodigogeneral
                AND lc.row_number = 1
            LEFT JOIN tipo_contrato tc WITH (NOLOCK)
                ON tc.idtipocontrato = lc.idtipocontrato
            WHERE pe.row_number = 1
                AND pe.fecha_ingreso BETWEEN %s AND %s
            ORDER BY pe.fecha_ingreso DESC, full_name
        """
        return self._rows(sql, [self.company_id, self.company_id, start_date, end_date])

    def get_person(self, worker_id):
        sql = """
            SELECT TOP 1
                pg.idcodigogeneral,
                RTRIM(pg.nrodocumento) AS document,
                LTRIM(RTRIM(CONCAT(pg.a_paterno, ' ', pg.a_materno, ' ', pg.nombres))) AS full_name,
                pe.fecha_ingreso,
                RTRIM(p.idplanilla) AS payroll_id,
                RTRIM(pl.descripcion) AS payroll,
                RTRIM(ISNULL(cp.descripcion, 'SIN CARGO')) AS position
            FROM personal_general pg WITH (NOLOCK)
            INNER JOIN personal_empresa pe WITH (NOLOCK)
                ON pe.idcodigogeneral = pg.idcodigogeneral AND pe.idempresa = %s
            LEFT JOIN personal p WITH (NOLOCK)
                ON p.idempresa = pe.idempresa AND p.idcodigogeneral = pe.idcodigogeneral
            LEFT JOIN planilla pl WITH (NOLOCK)
                ON pl.idempresa = p.idempresa AND pl.idplanilla = p.idplanilla
            LEFT JOIN cargos_personal cp WITH (NOLOCK)
                ON cp.idempresa = p.idempresa AND cp.idcargo = p.idcargo
            WHERE pg.idcodigogeneral = %s
            ORDER BY pe.fecha_ingreso DESC
        """
        rows = self._rows(sql, [self.company_id, worker_id])
        return rows[0] if rows else None

    def contract_types(self):
        return self._rows(
            """
            SELECT idtipocontrato, descripcion, ruta
            FROM tipo_contrato WITH (NOLOCK)
            WHERE estado = 1 AND tipo = 'N'
            ORDER BY descripcion
            """,
            [],
        )

    def generate(self, data):
        worker = self.get_person(data["worker_id"])
        if not worker:
            raise ValueError("El trabajador no existe.")

        with transaction.atomic(using=self.connection_name):
            connection = connections[self.connection_name]
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM contrato WITH (UPDLOCK, HOLDLOCK)
                    WHERE idempresa = %s AND idcodigogeneral = %s AND estado = 1
                      AND (
                        %s BETWEEN inicio_contrato AND final_contrato
                        OR inicio_contrato BETWEEN %s AND %s
                      )
                    """,
                    [
                        self.company_id,
                        data["worker_id"],
                        data["start_date"],
                        data["start_date"],
                        data["end_date"],
                    ],
                )
                if cursor.fetchone()[0]:
                    raise ValueError("El trabajador ya tiene un contrato para esta vigencia.")

                cursor.execute(
                    """
                    SELECT RIGHT('000' + CAST(ISNULL(MAX(TRY_CONVERT(int, idcontrato)), 0) + 1 AS varchar(3)), 3)
                    FROM contrato WITH (UPDLOCK, HOLDLOCK)
                    WHERE idempresa = %s AND idcodigogeneral = %s
                    """,
                    [self.company_id, data["worker_id"]],
                )
                contract_id = cursor.fetchone()[0]
                duration = (data["end_date"] - data["start_date"]).days + 1
                cursor.execute(
                    """
                    INSERT INTO contrato (
                        idempresa, idcodigogeneral, idcontrato, estado, apoderado,
                        apoderado_direcc, apoderado_docident, basico, duracion,
                        final_contrato, inicio_contrato, periodo_prueba, sincroniza,
                        fechacreacion, idtipocontrato, firma_fisica, idplanilla
                    ) VALUES (
                        %s, %s, %s, 1, '', '', '', %s, %s, %s, %s, %s,
                        'N', GETDATE(), %s, 0, %s
                    )
                    """,
                    [
                        self.company_id,
                        data["worker_id"],
                        contract_id,
                        data["basic"],
                        duration,
                        data["end_date"],
                        data["start_date"],
                        data["trial_days"],
                        data["contract_type"],
                        worker["payroll_id"],
                    ],
                )
        return contract_id

    def mark_signed(self, worker_id, contract_id):
        with connections[self.connection_name].cursor() as cursor:
            cursor.execute(
                """
                UPDATE contrato
                SET firma_fisica = 1, firma_contrato = COALESCE(firma_contrato, GETDATE())
                WHERE idempresa = %s AND idcodigogeneral = %s
                  AND idcontrato = %s AND estado = 1
                """,
                [self.company_id, worker_id, contract_id],
            )
            if cursor.rowcount != 1:
                raise ValueError("No se encontró el contrato.")

    def template_path(self, contract_type):
        rows = self._rows(
            """
            SELECT TOP 1 ruta FROM tipo_contrato WITH (NOLOCK)
            WHERE idtipocontrato = %s AND estado = 1
            """,
            [contract_type],
        )
        if not rows or not rows[0]["ruta"]:
            raise FileNotFoundError("El tipo de contrato no tiene plantilla.")
        path = Path(rows[0]["ruta"])
        if path.suffix.lower() not in (".doc", ".docx", ".pdf") or not path.is_file():
            raise FileNotFoundError("La plantilla configurada no está disponible.")
        return path

    def _rows(self, sql, params):
        with connections[self.connection_name].cursor() as cursor:
            cursor.execute(sql, params)
            columns = [column[0] for column in cursor.description]
            return [
                {
                    key: value.strip() if isinstance(value, str) else value
                    for key, value in zip(columns, row)
                }
                for row in cursor.fetchall()
            ]
