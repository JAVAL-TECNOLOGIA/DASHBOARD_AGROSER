from datetime import datetime

from apps.connection.local_connection import open_connection
import apps.connection.connect_portalaei as portalaei_db


def apply_night_shift_backfill(start_date):
    """Fusiona pares inequívocos de turno nocturno y deja respaldo recuperable."""
    connection = open_connection(portalaei_db.build_pyodbc_connection_string(
        portalaei_db.host, portalaei_db.name, portalaei_db.user,
        portalaei_db.password, mars=False,
    ))
    cursor = connection.cursor()
    try:
        cursor.execute("""
            IF OBJECT_ID('dbo.ASISTENCIA_NOCTURNO_MIGRACION', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.ASISTENCIA_NOCTURNO_MIGRACION (
                    ID_MIGRACION BIGINT IDENTITY(1,1) PRIMARY KEY,
                    ID_ASISTENCIA_ORIGEN INT NOT NULL,
                    ID_ASISTENCIA_DUPLICADA INT NOT NULL,
                    ID_PERSONAL INT NOT NULL,
                    ID_SEDE INT NOT NULL,
                    FECHA_ORIGEN DATE NOT NULL,
                    INGRESO_ORIGEN TIME(0) NOT NULL,
                    SALIDA_ANTERIOR TIME(0) NULL,
                    FECHA_DUPLICADA DATE NOT NULL,
                    INGRESO_DUPLICADO TIME(0) NOT NULL,
                    SALIDA_DUPLICADA TIME(0) NULL,
                    FECHA_MIGRACION DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
                    USUARIO VARCHAR(50) NOT NULL,
                    CONSTRAINT UQ_ASISTENCIA_NOCTURNO_MIG UNIQUE (ID_ASISTENCIA_DUPLICADA)
                );
            END
        """)
        cursor.execute("""
            IF OBJECT_ID('dbo.ASISTENCIA_MODIFICACION_LOG', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.ASISTENCIA_MODIFICACION_LOG (
                    ID_LOG BIGINT IDENTITY(1,1) PRIMARY KEY,
                    ID_ASISTENCIA INT NOT NULL,
                    HORA_INGRESO_ANTERIOR TIME(0) NULL,
                    HORA_SALIDA_ANTERIOR TIME(0) NULL,
                    HORA_INGRESO_NUEVA TIME(0) NULL,
                    HORA_SALIDA_NUEVA TIME(0) NULL,
                    MOTIVO NVARCHAR(500) NOT NULL,
                    USUARIO NVARCHAR(150) NOT NULL,
                    IP_ORIGEN NVARCHAR(64) NULL,
                    FECHA_MODIFICACION DATETIME2(0) NOT NULL DEFAULT SYSDATETIME()
                );
            END
        """)
        cursor.execute("""
            SELECT prev.ID_ASISTENCIA, nxt.ID_ASISTENCIA, prev.ID_PERSONAL,
                   prev.ID_SEDE, CAST(prev.LOG_FECHA AS date), prev.HORA_INGRESO,
                   prev.HORA_SALIDA, CAST(nxt.LOG_FECHA AS date),
                   nxt.HORA_INGRESO, nxt.HORA_SALIDA
            FROM ASISTENCIA prev
            INNER JOIN ASISTENCIA nxt
                ON nxt.ID_PERSONAL = prev.ID_PERSONAL
               AND nxt.ID_SEDE = prev.ID_SEDE
               AND CAST(nxt.LOG_FECHA AS date) = DATEADD(day, 1, CAST(prev.LOG_FECHA AS date))
            WHERE CAST(prev.LOG_FECHA AS date) >= ?
              AND prev.HORA_SALIDA IS NULL
              AND nxt.HORA_INGRESO IS NOT NULL
              AND nxt.HORA_SALIDA IS NULL
              AND nxt.HORA_INGRESO <= CAST('06:00:00' AS time)
              AND DATEDIFF(MINUTE,
                    DATEADD(DAY,DATEDIFF(DAY,0,prev.LOG_FECHA),CAST(prev.HORA_INGRESO AS datetime)),
                    DATEADD(DAY,DATEDIFF(DAY,0,nxt.LOG_FECHA),CAST(nxt.HORA_INGRESO AS datetime))
                  ) BETWEEN 6 AND 960
              AND NOT EXISTS (
                    SELECT 1 FROM dbo.ASISTENCIA_NOCTURNO_MIGRACION b
                    WHERE b.ID_ASISTENCIA_DUPLICADA = nxt.ID_ASISTENCIA
              )
            ORDER BY prev.LOG_FECHA, prev.ID_ASISTENCIA
        """, [start_date])
        candidates = cursor.fetchall()
        applied = []
        for row in candidates:
            (origin_id, duplicate_id, personal_id, site_id, origin_date,
             entry_time, previous_exit, duplicate_date, duplicate_entry,
             duplicate_exit) = row
            entry_dt = datetime.combine(origin_date, entry_time)
            exit_dt = datetime.combine(duplicate_date, duplicate_entry)
            hours = (exit_dt - entry_dt).total_seconds() / 3600
            status = 2 if hours >= 6 else 1
            cursor.execute("""
                INSERT INTO dbo.ASISTENCIA_NOCTURNO_MIGRACION (
                    ID_ASISTENCIA_ORIGEN, ID_ASISTENCIA_DUPLICADA, ID_PERSONAL,
                    ID_SEDE, FECHA_ORIGEN, INGRESO_ORIGEN, SALIDA_ANTERIOR,
                    FECHA_DUPLICADA, INGRESO_DUPLICADO, SALIDA_DUPLICADA, USUARIO
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SYSTEM_NIGHT_SHIFT')
            """, list(row))
            cursor.execute("""
                INSERT INTO dbo.ASISTENCIA_MODIFICACION_LOG (
                    ID_ASISTENCIA, HORA_INGRESO_ANTERIOR, HORA_SALIDA_ANTERIOR,
                    HORA_INGRESO_NUEVA, HORA_SALIDA_NUEVA, MOTIVO, USUARIO, IP_ORIGEN
                ) VALUES (?, ?, ?, ?, ?, ?, 'SYSTEM_NIGHT_SHIFT', 'LOCAL')
            """, [
                origin_id, entry_time, previous_exit, entry_time, duplicate_entry,
                f'Turno nocturno histórico; se fusionó la marcación {duplicate_id} del día siguiente.',
            ])
            cursor.execute("""
                UPDATE ASISTENCIA SET HORA_SALIDA = ?, ESTADO = ?
                WHERE ID_ASISTENCIA = ? AND HORA_SALIDA IS NULL
            """, [duplicate_entry, status, origin_id])
            if cursor.rowcount != 1:
                raise RuntimeError(f'No se pudo actualizar la asistencia {origin_id}.')
            cursor.execute("DELETE FROM ASISTENCIA WHERE ID_ASISTENCIA = ?", [duplicate_id])
            if cursor.rowcount != 1:
                raise RuntimeError(f'No se pudo retirar la marcación duplicada {duplicate_id}.')
            applied.append({
                'origin_id': origin_id, 'duplicate_id': duplicate_id,
                'entry': f'{origin_date} {entry_time}',
                'exit': f'{duplicate_date} {duplicate_entry}',
                'hours': round(hours, 2),
            })
        connection.commit()
        return applied
    except Exception:
        connection.rollback()
        raise
    finally:
        try:
            cursor.close()
        finally:
            connection.close()
