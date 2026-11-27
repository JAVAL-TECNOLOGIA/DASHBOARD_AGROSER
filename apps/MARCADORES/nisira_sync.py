from collections import defaultdict
from datetime import datetime, timedelta
import re
import unicodedata
from xml.etree import ElementTree

from apps.connection.connect_donluis import connection_string
from apps.connection.local_connection import open_connection


NISIRA_COMPANY = '001'
NISIRA_BRANCH = '028'
SYNC_BATCH_SIZE = 900


def _nisira_xml_text(value):
    """Normaliza texto a ASCII porque el procedimiento recibe SQL TEXT (ANSI)."""
    normalized = unicodedata.normalize('NFKD', str(value or ''))
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Za-z0-9 .,_/\-]', '', ascii_text).strip()


def _xml_for_marks(marks):
    root = ElementTree.Element('VFPData')
    for index, mark in enumerate(marks, start=1):
        row = ElementTree.SubElement(root, 'temporal')
        values = {
            'seleccionado': '1',
            'item': str(index).zfill(3),
            'fecha': mark['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'),
            'marcacion': mark['timestamp'].strftime('%H:%M:%S'),
            'idcodigogeneral': mark['code'],
            'apenom': _nisira_xml_text(mark.get('name', '')),
        }
        for key, value in values.items():
            ElementTree.SubElement(row, key).text = value
    return ElementTree.tostring(root, encoding='unicode')


def _fetch_procedure_rows(cursor):
    """Avanza sobre mensajes/rowcounts hasta encontrar un resultado tabular."""
    while True:
        if cursor.description is not None:
            try:
                return cursor.fetchall()
            except Exception:
                # Algunos procedimientos de NISIRA exponen una descripción
                # transitoria sin filas recuperables; continuar al siguiente set.
                pass
        try:
            if not cursor.nextset():
                return []
        except Exception:
            return []


def _get_configuration(cursor):
    cursor.execute("""
        SELECT TOP 1 RTRIM(IDRESPONSABLE)
        FROM config_sucursal_zktime
        WHERE IDEMPRESA = ? AND IDSUCURSAL = ?
        ORDER BY IDRESPONSABLE
    """, [NISIRA_COMPANY, NISIRA_BRANCH])
    row = cursor.fetchone()
    if not row or not str(row[0] or '').strip():
        raise ValueError('NISIRA no tiene responsable configurado para la sucursal 028.')
    return str(row[0]).strip()


def _ensure_daily_header(cursor, work_date, responsible):
    cursor.execute("""
        SELECT TOP 1 IDCONTROLINGRESO
        FROM CONTROLINGRESOSALIDA_PERSONAL
        WHERE IDEMPRESA = ? AND IDSUCURSAL = ? AND IDRESPONSABLE = ?
          AND CONVERT(date, FECHA) = ? AND ISNULL(GENERADO_ZKTIME, 0) = 0
        ORDER BY FECHACREACION DESC
    """, [NISIRA_COMPANY, NISIRA_BRANCH, responsible, work_date])
    row = cursor.fetchone()
    if row:
        return str(row[0]).strip()

    cursor.execute("""
        SELECT TOP 1 IDDOCUMENTO
        FROM CFG_FORM_DOCUMENTO
        WHERE IDEMPRESA = ? AND CFORM = 'LST_INGRESOSALIDA_PERSONAL'
    """, [NISIRA_COMPANY])
    document = cursor.fetchone()
    if not document or not str(document[0] or '').strip():
        raise ValueError('NISIRA no tiene configurado el documento de control de ingreso/salida.')

    cursor.execute("DECLARE @ID CHAR(15); EXEC OBJSISTEMA_RETURNID @CODI=@ID OUTPUT; SELECT @ID")
    control_id = str(cursor.fetchone()[0]).strip()
    cursor.execute(
        "EXEC OBJTABLAS_RETURNSERIES ?, '001', ?",
        [NISIRA_COMPANY, str(document[0]).strip()],
    )
    series_rows = _fetch_procedure_rows(cursor)
    series_row = series_rows[0] if series_rows else None
    if not series_row:
        raise ValueError('NISIRA no pudo generar la serie y correlativo del documento.')

    cursor.execute("""
        INSERT INTO CONTROLINGRESOSALIDA_PERSONAL (
            IDEMPRESA, IDCONTROLINGRESO, IDSUCURSAL, IDEMISOR, IDDOCUMENTO,
            SERIE, NUMERO, FECHA, PERIODO, IDPLANILLA, IDRESPONSABLE,
            FECHACREACION, IDESTADO, IDREFERENCIA, VENTANA, GENERADO_ZKTIME
        ) VALUES (?, ?, ?, '001', ?, ?, ?, ?, ?, '', ?, GETDATE(), 'PE', '',
                  'EDT_INGRESOSALIDA_PERSONAL', 0)
    """, [
        NISIRA_COMPANY, control_id, NISIRA_BRANCH, str(document[0]).strip(),
        str(series_row[0]).strip(), str(series_row[1]).strip(), work_date,
        work_date.strftime('%Y%m'), responsible,
    ])
    return control_id


def synchronize_marks(marks, username, machine='DASHBOARD'):
    grouped = defaultdict(list)
    for mark in marks:
        grouped[mark['timestamp'].date()].append(mark)

    connection = open_connection(connection_string)
    cursor = connection.cursor()
    sent = 0
    duplicates = 0
    types_corrected = 0
    warnings = []
    documents = []
    try:
        responsible = _get_configuration(cursor)
        for work_date in sorted(grouped):
            day_marks = sorted(grouped[work_date], key=lambda item: item['timestamp'])
            cursor.execute("""
                SELECT RTRIM(IDPERSONAL), FECHA, IDCONTROLINGRESO, ITEM, TIPO
                FROM DCONTROLINGRESOSALIDA_PERSONAL
                WHERE IDEMPRESA = ? AND FECHA >= ? AND FECHA < ?
            """, [NISIRA_COMPANY, work_date, work_date + timedelta(days=1)])
            existing = defaultdict(list)
            for row in cursor.fetchall():
                existing[(str(row[0]).strip(), row[1].replace(microsecond=0))].append({
                    'control_id': str(row[2]).strip(), 'item': str(row[3]).strip(),
                    'kind': str(row[4] or '').strip().upper(),
                })
            pending = []
            for mark in day_marks:
                key = (mark['code'].strip(), mark['timestamp'].replace(microsecond=0))
                if key in existing:
                    duplicates += 1
                    expected_kind = str(mark.get('kind') or '').strip().upper()
                    for stored in existing[key]:
                        if expected_kind in ('I', 'S') and stored['kind'] != expected_kind:
                            cursor.execute("""
                                UPDATE DCONTROLINGRESOSALIDA_PERSONAL
                                SET TIPO = ?
                                WHERE IDEMPRESA = ? AND IDCONTROLINGRESO = ? AND ITEM = ?
                            """, [
                                expected_kind, NISIRA_COMPANY,
                                stored['control_id'], stored['item'],
                            ])
                            types_corrected += cursor.rowcount
                else:
                    pending.append(mark)
            if not pending:
                continue

            control_id = _ensure_daily_header(cursor, work_date, responsible)
            documents.append(control_id)
            for offset in range(0, len(pending), SYNC_BATCH_SIZE):
                batch = pending[offset:offset + SYNC_BATCH_SIZE]
                cursor.execute(
                    "EXEC nsp_grabardetallemarcaciones_txt ?, ?, ?, '', ?, ?, ?, ?, ?",
                    [
                        NISIRA_COMPANY, control_id, work_date, responsible,
                        NISIRA_BRANCH, _xml_for_marks(batch), username[:20], machine[:200],
                    ],
                )
                result_rows = _fetch_procedure_rows(cursor)
                messages = [str(row[1]).strip() for row in result_rows if len(row) > 1]
                non_ok = [message for message in messages if message.upper() != 'OK']
                warnings.extend(non_ok)
                sent += len(batch) - len(non_ok)
                for mark in batch:
                    expected_kind = str(mark.get('kind') or '').strip().upper()
                    if expected_kind not in ('I', 'S'):
                        continue
                    cursor.execute("""
                        UPDATE DCONTROLINGRESOSALIDA_PERSONAL
                        SET TIPO = ?
                        WHERE IDEMPRESA = ? AND IDCONTROLINGRESO = ?
                          AND RTRIM(IDPERSONAL) = ? AND FECHA = ?
                          AND ISNULL(TIPO, '') <> ?
                    """, [
                        expected_kind, NISIRA_COMPANY, control_id,
                        mark['code'].strip(), mark['timestamp'], expected_kind,
                    ])
                    types_corrected += cursor.rowcount
        connection.commit()
        return {
            'sent': max(sent, 0),
            'duplicates': duplicates,
            'types_corrected': types_corrected,
            'warnings': warnings[:50],
            'documents': sorted(set(documents)),
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        try:
            cursor.close()
        finally:
            connection.close()
