import re
from pathlib import Path

from django.conf import settings
from django.db import connections, transaction


def dashboard_template_path(contract_type, extension=None):
    safe_type = re.sub(r"[^A-Za-z0-9_-]+", "_", str(contract_type)).strip("_")
    root = Path(settings.MEDIA_ROOT) / "contratos" / "plantillas" / "dashboard"
    if extension:
        return root / "{}{}".format(safe_type, extension.lower())
    for suffix in (".docx", ".doc"):
        candidate = root / "{}{}".format(safe_type, suffix)
        if candidate.is_file():
            return candidate
    return None


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
                AND (pe.fecha_cese IS NULL OR pe.fecha_cese >= CAST(GETDATE() AS date))
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

    def list_expiring_contracts(self, start_date, end_date):
        sql = """
            WITH latest_contract AS (
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
                RTRIM(p.idplanilla) AS payroll_id,
                RTRIM(pl.descripcion) AS payroll,
                RTRIM(ISNULL(cp.descripcion, 'SIN CARGO')) AS position,
                lc.idcontrato AS contract_id,
                lc.idtipocontrato AS contract_type_id,
                tc.descripcion AS contract_type,
                lc.inicio_contrato,
                lc.final_contrato,
                lc.basico
            FROM latest_contract lc
            INNER JOIN personal_general pg WITH (NOLOCK)
                ON pg.idcodigogeneral = lc.idcodigogeneral
            OUTER APPLY (
                SELECT TOP 1 p0.idempresa, p0.idcodigogeneral, p0.idplanilla, p0.idcargo
                FROM personal p0 WITH (NOLOCK)
                WHERE p0.idempresa = lc.idempresa
                  AND p0.idcodigogeneral = lc.idcodigogeneral
            ) p
            LEFT JOIN planilla pl WITH (NOLOCK)
                ON pl.idempresa = p.idempresa AND pl.idplanilla = p.idplanilla
            LEFT JOIN cargos_personal cp WITH (NOLOCK)
                ON cp.idempresa = p.idempresa AND cp.idcargo = p.idcargo
            LEFT JOIN tipo_contrato tc WITH (NOLOCK)
                ON tc.idtipocontrato = lc.idtipocontrato
            WHERE lc.row_number = 1
              AND lc.final_contrato BETWEEN %s AND %s
              AND EXISTS (
                  SELECT 1
                  FROM personal_empresa pe WITH (NOLOCK)
                  WHERE pe.idempresa = lc.idempresa
                    AND pe.idcodigogeneral = lc.idcodigogeneral
                    AND (pe.fecha_cese IS NULL OR pe.fecha_cese >= CAST(GETDATE() AS date))
              )
            ORDER BY lc.final_contrato, full_name
        """
        return self._rows(sql, [self.company_id, start_date, end_date])

    def get_contract(self, worker_id, contract_id):
        rows = self._rows(
            """
            SELECT TOP 1 idcontrato, idtipocontrato, inicio_contrato,
                final_contrato, basico
            FROM contrato WITH (NOLOCK)
            WHERE idempresa = %s AND idcodigogeneral = %s
              AND idcontrato = %s AND estado = 1
            """,
            [self.company_id, worker_id, contract_id],
        )
        return rows[0] if rows else None

    def contract_document_data(self, worker_id, contract_id):
        rows = self._rows(
            """
            SELECT TOP 1
                pg.idcodigogeneral,
                RTRIM(pg.nrodocumento) AS document,
                LTRIM(RTRIM(CONCAT(pg.a_paterno, ' ', pg.a_materno, ' ', pg.nombres))) AS full_name,
                pg.sexo,
                LTRIM(RTRIM(CONCAT(
                    NULLIF(LTRIM(RTRIM(pg.descripcion_via)), ''),
                    CASE WHEN NULLIF(LTRIM(RTRIM(CONVERT(varchar(30), pg.direccion_numero))), '') IS NULL
                         OR LTRIM(RTRIM(CONVERT(varchar(30), pg.direccion_numero))) = '0' THEN ''
                         ELSE ' ' + LTRIM(RTRIM(CONVERT(varchar(30), pg.direccion_numero))) END,
                    CASE WHEN NULLIF(LTRIM(RTRIM(pg.descripcion_zona)), '') IS NULL THEN ''
                         ELSE ' ' + LTRIM(RTRIM(pg.descripcion_zona)) END
                ))) AS address,
                RTRIM(pg.direccion_referencia) AS address_reference,
                RTRIM(ISNULL(u.ubigeo, '')) AS district,
                RTRIM(ISNULL(u.provincia, '')) AS province,
                RTRIM(ISNULL(u.departamento, '')) AS department,
                RTRIM(ISNULL(cp.descripcion, 'SIN CARGO')) AS position,
                RTRIM(p.idplanilla) AS payroll_id,
                c.idcontrato,
                c.idtipocontrato,
                c.inicio_contrato,
                c.final_contrato,
                c.basico,
                CASE WHEN pe.idcodigogeneral IS NOT NULL
                           AND (pe.fecha_cese IS NULL OR pe.fecha_cese >= CAST(GETDATE() AS date))
                     THEN 1 ELSE 0 END AS is_active
            FROM contrato c WITH (NOLOCK)
            INNER JOIN personal_general pg WITH (NOLOCK)
                ON pg.idcodigogeneral = c.idcodigogeneral
            OUTER APPLY (
                SELECT TOP 1 p0.idempresa, p0.idcodigogeneral, p0.idplanilla, p0.idcargo
                FROM personal p0 WITH (NOLOCK)
                WHERE p0.idempresa = c.idempresa AND p0.idcodigogeneral = c.idcodigogeneral
            ) p
            OUTER APPLY (
                SELECT TOP 1 pe0.idcodigogeneral, pe0.fecha_cese
                FROM personal_empresa pe0 WITH (NOLOCK)
                WHERE pe0.idempresa = c.idempresa
                  AND pe0.idcodigogeneral = c.idcodigogeneral
                ORDER BY pe0.fecha_ingreso DESC, pe0.item DESC
            ) pe
            LEFT JOIN cargos_personal cp WITH (NOLOCK)
                ON cp.idempresa = p.idempresa AND cp.idcargo = p.idcargo
            LEFT JOIN VW_UBIGEO u WITH (NOLOCK)
                ON u.idubigeo = pg.idubigeo
            WHERE c.idempresa = %s AND c.idcodigogeneral = %s
              AND c.idcontrato = %s AND c.estado = 1
            """,
            [self.company_id, worker_id, contract_id],
        )
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

    def employee_catalogs(self):
        def choices(sql, params=()):
            return [(str(row[0]).strip(), str(row[1]).strip()) for row in self._tuples(sql, params)]
        return {
            "marital_status": choices("SELECT IDESTADOCIVIL, DESCRIPCION FROM ESTADO_CIVIL WITH (NOLOCK) WHERE ESTADO=1 ORDER BY DESCRIPCION"),
            "nationality": choices("SELECT IDNACIONALIDAD, DESCRIPCION FROM NACIONALIDAD WITH (NOLOCK) WHERE ESTADO=1 ORDER BY DESCRIPCION"),
            "issuing_country": choices("SELECT CODIGO, DESCRIPCION FROM RTPS_PAISEMISOR WITH (NOLOCK) WHERE ESTADO=1 ORDER BY DESCRIPCION"),
            "birth_place": [("", "Seleccione...")] + choices("SELECT IDUBIGEO, DESCRIPCION FROM UBIGEO WITH (NOLOCK) ORDER BY DESCRIPCION"),
            "payroll": choices("SELECT IDPLANILLA, DESCRIPCION FROM planilla WITH (NOLOCK) WHERE IDEMPRESA=%s AND ISNULL(ESTADO,1)=1 AND IDPLANILLA IN ('ERG','ERA','OBP','OBR') ORDER BY DESCRIPCION", [self.company_id]),
            "position": choices("SELECT IDCARGO, DESCRIPCION FROM cargos_personal WITH (NOLOCK) WHERE IDEMPRESA=%s AND ISNULL(estado,1)=1 ORDER BY DESCRIPCION", [self.company_id]),
        }

    def create_employee_and_contract(self, data):
        worker_id = data["document"]
        with transaction.atomic(using=self.connection_name):
            connection = connections[self.connection_name]
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM personal_general WITH (UPDLOCK,HOLDLOCK) WHERE idcodigogeneral=%s OR nrodocumento=%s", [worker_id, worker_id])
                if cursor.fetchone()[0]:
                    raise ValueError("El DNI ya está registrado en NISIRA.")
                cursor.execute(
                    """INSERT INTO personal_general
                    (idcodigogeneral,estado,a_materno,a_paterno,nombres,sexo,sincroniza,
                     fecha_nacimiento,nrodocumento,telefono,telefono2,celular,email,
                     idnacionalidad,idlugarnac,iddocidentidad,idestadocivil,procedencia,
                     idpaisemisor,fechacreacion)
                    VALUES (%s,1,%s,%s,%s,%s,'N',%s,%s,%s,%s,%s,%s,%s,%s,'01',%s,'',%s,GETDATE())""",
                    [worker_id, data["maternal_surname"], data["paternal_surname"],
                     data["first_names"], data["sex"], data["birth_date"], worker_id,
                     data.get("phone"), data.get("phone2"), data.get("mobile"), data.get("email"),
                     data["nationality"], data.get("birth_place") or None,
                     data["marital_status"], data["issuing_country"]],
                )
                cursor.execute("""SELECT TOP 1 IDTIPOTRABAJADOR,IDTIPOPERSONAL,IDGRUPOTRABAJO,
                    IDSUCURSAL,idhorariotrabajo,dia_descanso FROM personal WITH (NOLOCK)
                    WHERE IDEMPRESA=%s AND IDPLANILLA=%s AND ESTADO=1 ORDER BY FECHACREACION DESC""",
                    [self.company_id, data["payroll"]])
                defaults = cursor.fetchone()
                if not defaults:
                    raise ValueError("La planilla seleccionada no tiene una configuración laboral de referencia.")
                worker_type, personnel_type, work_group, branch, schedule, rest_day = defaults
                cursor.execute("""INSERT INTO personal
                    (idempresa,idcodigogeneral,idplanilla,fecha_inicioplanilla,sincroniza,
                     en_plantilla_asistencia,fechacreacion,idcargo,idtipotrabajador,
                     idtipopersonal,idgrupotrabajo,idsucursal,estado,idhorariotrabajo,dia_descanso)
                    VALUES (%s,%s,%s,%s,'N','S',GETDATE(),%s,%s,%s,%s,%s,1,%s,%s)""",
                    [self.company_id, worker_id, data["payroll"], data["employment_start"],
                     data["position"], worker_type, personnel_type, work_group, branch,
                     schedule, rest_day])
                cursor.execute("""INSERT INTO personal_empresa
                    (idempresa,idcodigogeneral,item,fecha_ingreso,idsituacion,idtipo,
                     fecha_ocurrencia,idgrupo,idtipotrabajador)
                    VALUES (%s,%s,'001',%s,'11','1',%s,'003',%s)""",
                    [self.company_id, worker_id, data["employment_start"],
                     data["employment_start"], worker_type])
            contract_data = dict(data)
            contract_data["worker_id"] = worker_id
            contract_data["contract_type"] = data["contract_type"]
            return worker_id, self.generate(contract_data)

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
                        fechacreacion, idtipocontrato, firma_fisica, idplanilla,
                        firma_contrato
                    ) VALUES (
                        %s, %s, %s, 1, '', '', '', %s, %s, %s, %s, %s,
                        'N', GETDATE(), %s, 0, %s, %s
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
                        data["signature_date"],
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
        local_path = dashboard_template_path(contract_type)
        if local_path:
            return local_path
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

    def _tuples(self, sql, params):
        with connections[self.connection_name].cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
