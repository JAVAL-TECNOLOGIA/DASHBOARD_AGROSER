"""
API Evaluaciones - Cartillas Agrícolas
Vista dinámica: PlantillaRegistro + PlantillaCampo.
Tabla y modal construidos dinámicamente según metadata de PlantillaCampo.
"""
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views import View

try:
    from apps.connection.connect_app_agricola import connection_app_agricola
except ImportError:
    connection_app_agricola = None

# Columnas base fijas del sistema (no dependen de PlantillaCampo)
BASE_COLUMNS = [
    {'key': 'fecha', 'label': 'Fecha'},
    {'key': 'hora', 'label': 'Hora'},
    {'key': 'gps', 'label': 'GPS'},
    {'key': 'lote', 'label': 'Descripción'},
    {'key': 'campania', 'label': 'Campaña'},
    {'key': 'cartilla', 'label': 'Cartilla'},
    {'key': 'evaluador', 'label': 'Evaluador'},
]

PERSONA_FIELD_HINTS = ('operario', 'supervisor', 'podador', 'persona')
PERSONA_TIPO_FIELD_HINTS = ('persona_tipo', 'tipo_persona')


def _parse_datajson(datajson_raw):
    """Parsea DataJson y extrae body, header. Retorna (body, header) o ({}, {})."""
    if not datajson_raw:
        return {}, {}
    try:
        if isinstance(datajson_raw, str):
            data = json.loads(datajson_raw)
        else:
            data = datajson_raw
        return data.get('body', {}), data.get('header', {})
    except (json.JSONDecodeError, TypeError):
        return {}, {}


def _safe_float(val):
    if val is None:
        return None
    try:
        if isinstance(val, (int, float, Decimal)):
            return float(val)
        return float(str(val).replace(',', '.'))
    except (ValueError, TypeError):
        return None


def _to_serializable(val):
    if isinstance(val, Decimal):
        return float(val)
    if hasattr(val, 'isoformat'):
        return val.isoformat()
    return val


def _normalize_key(key):
    """Intenta obtener valor de body con distintas variantes de key (case, camelCase, snake_case)."""
    if not key:
        return key
    k = str(key)
    variants = [k, k.lower(), k.replace('_', '').lower()]
    return variants


def _body_get(body, json_key):
    """
    Obtiene valor de body por JsonKey.
    Busca key exacta y variantes (camelCase, snake_case) para compatibilidad.
    Retorna None si no existe.
    """
    if not body or not json_key:
        return None
    key = str(json_key)
    # Intenta key exacta
    if key in body:
        return body[key]
    # Intenta variantes comunes
    for k in body.keys():
        if k and (k.lower() == key.lower() or k.replace('_', '').lower() == key.replace('_', '').lower()):
            return body[k]
    return None


def _get_dynamic_columns(conn, plantilla_id):
    """
    Obtiene columnas dinámicas desde PlantillaCampo.
    Retorna lista de {key, label, type, visibleInTable}.
    Solo campos con EsActivo=1. visibleInTable según EsVisibleTabla.
    Si PlantillaCampo no existe o falla, retorna [].
    """
    dynamic = []
    try:
        # Intentar columnas típicas de PlantillaCampo (SQL Server case-insensitive)
        sql = """
            SELECT JsonKey, Label, DataType, ISNULL(Orden, 999) AS Orden,
                   ISNULL(EsVisibleTabla, 1) AS EsVisibleTabla,
                   ISNULL(EsActivo, 1) AS EsActivo
            FROM PlantillaCampo
            WHERE PlantillaId = ? AND (EsActivo = 1 OR EsActivo = '1' OR EsActivo = 'true')
            ORDER BY Orden
        """
        cursor = conn.cursor()
        cursor.execute(sql, [plantilla_id])
        for row in cursor.fetchall():
            key = row[0]
            label = row[1] or key
            dtype = row[2] or 'string'
            visible = row[4] in (1, '1', 'true', True, 'True')
            if key:
                dynamic.append({
                    'key': str(key),
                    'label': str(label),
                    'type': str(dtype).lower(),
                    'visibleInTable': bool(visible),
                })
        cursor.close()
    except Exception:
        dynamic = []
    return dynamic


def _intersect_dynamic_columns(conn, plantilla_ids_ordered):
    """
    Columnas dinámicas presentes en todas las plantillas (mismo JsonKey).
    Orden y metadatos (label, type, visibleInTable) según la primera plantilla de la lista.
    """
    if not plantilla_ids_ordered:
        return []
    col_lists = [_get_dynamic_columns(conn, pid) for pid in plantilla_ids_ordered]
    if not col_lists or any(len(lst) == 0 for lst in col_lists):
        return []
    if len(col_lists) == 1:
        return col_lists[0]
    key_sets = [set(c['key'] for c in lst) for lst in col_lists]
    common = set.intersection(*key_sets)
    if not common:
        return []
    first = col_lists[0]
    return [c for c in first if c['key'] in common]


def _fetch_plantilla_lookup(conn, plantilla_ids):
    """
    { str(PlantillaId): Nombre } desde dbo.Plantilla (Nombre nvarchar(150)).
    """
    lookup = {}
    ids = []
    for x in plantilla_ids or []:
        if x is None:
            continue
        try:
            ids.append(int(x))
        except (ValueError, TypeError):
            continue
    uniq = list(dict.fromkeys(ids))
    if not uniq:
        return lookup
    placeholders = ','.join(['?' for _ in uniq])
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT PlantillaId, Nombre FROM dbo.Plantilla WHERE PlantillaId IN ({})".format(placeholders),
            uniq,
        )
        for row in cursor.fetchall():
            kid, nom = row[0], row[1]
            if kid is None:
                continue
            k = str(kid).strip()
            nombre = str(nom).strip() if nom is not None else ''
            lookup[k] = nombre if nombre else k
        cursor.close()
    except Exception:
        pass
    for i in uniq:
        sk = str(i)
        if sk not in lookup:
            lookup[sk] = sk
    return lookup


def _fetch_plantilla_nombre_lookup(conn, plantilla_id):
    """{ str(PlantillaId): Nombre } para una sola plantilla."""
    if plantilla_id is None or plantilla_id == '':
        return {}
    return _fetch_plantilla_lookup(conn, [plantilla_id])


def _extract_base_from_row(row_dict, body, header, lote_lookup=None, user_lookup=None, campania_lookup=None, plantilla_lookup=None):
    """
    Extrae datos base: fecha, hora, gps, lote, campaña, evaluador.
    Lote y evaluador priorizan lookup por ID, luego body, luego ID crudo.
    """
    lote_lookup = lote_lookup or {}
    user_lookup = user_lookup or {}
    fechareg = row_dict.get('FechaEjecucion') or row_dict.get('FechaRegistro')
    fecha_str = ''
    hora_str = ''
    if fechareg:
        d = _to_serializable(fechareg)
        if isinstance(d, str) and 'T' in d:
            fecha_str = d.split('T')[0]
            hora_str = d.split('T')[1][:5] if len(d.split('T')) > 1 else ''
        else:
            fecha_str = str(d)[:10]
            hora_str = ''

    lat = (body.get('lat') or body.get('Lat') or body.get('latitude') or
           header.get('lat') or header.get('Lat') or header.get('latitude') or row_dict.get('Lat'))
    lon = (body.get('lon') or body.get('Lon') or body.get('longitude') or
           header.get('lon') or header.get('Lon') or header.get('longitude') or row_dict.get('Lon'))
    gps = 'OK' if (lat is not None and lon is not None) else '—'

    # Lote: prioriza lookup por LoteId, luego body, luego ID crudo
    lote_id = row_dict.get('LoteId')
    lote_info = lote_lookup.get(str(lote_id)) if lote_id is not None else None
    lote = None
    lote_geo = None
    if lote_info:
        if isinstance(lote_info, dict):
            _desc = (lote_info.get('descripcion') or '').strip()
            lote = _desc or lote_info.get('codigo') or lote_info.get('codigo_lote')
            lote_geo = lote_info.get('geo')
        else:
            lote = lote_info
    if not lote:
        lote = (row_dict.get('LoteCodigo') or row_dict.get('codigo_lote') or
                body.get('loteManual') or body.get('lote_manual') or body.get('LoteManual') or
                body.get('lote') or body.get('Lote'))
    if not lote and lote_id is not None:
        lote = str(lote_id)
    if not lote:
        lote = '—'

    campania_lookup = campania_lookup or {}
    cid = row_dict.get('ID_CAMPANIA') if row_dict.get('ID_CAMPANIA') is not None else row_dict.get('CampaniaId')
    cid_str = str(cid).strip() if cid is not None and str(cid).strip() != '' else None
    campania_desc = campania_lookup.get(cid_str) if cid_str else None
    campania = (body.get('campania') or body.get('Campania') or body.get('campania_id') or
                header.get('campania') or header.get('Campania') or campania_desc or cid_str or '—')

    # Evaluador: prioriza lookup por UserId, luego body, luego ID crudo
    user_id = row_dict.get('UserId')
    evaluador = (user_lookup.get(str(user_id)) if user_id is not None else None or
                 row_dict.get('EvaluadorNombre') or row_dict.get('Nombre') or
                 body.get('evaluador') or body.get('Evaluador') or body.get('userName') or
                 header.get('evaluador') or header.get('userName'))
    if not evaluador and user_id is not None:
        evaluador = str(user_id)
    if not evaluador:
        evaluador = '—'

    plantilla_lookup = plantilla_lookup or {}
    pid = row_dict.get('PlantillaId')
    if pid is not None:
        sk = str(pid).strip()
        cartilla = plantilla_lookup.get(sk) or sk or '—'
    else:
        cartilla = '—'

    out = {
        'fecha': fecha_str or '—',
        'hora': hora_str or '—',
        'gps': gps,
        'lote': _to_serializable(lote),
        'loteId': _to_serializable(lote_id) if lote_id is not None else None,
        'campania': _to_serializable(campania),
        'cartilla': _to_serializable(cartilla),
        'evaluador': _to_serializable(evaluador),
    }
    if lote_geo:
        out['lote_geo'] = lote_geo
    return out


def _column_looks_like_persona_fk(col):
    key = str(col.get('key') or '').lower()
    label = str(col.get('label') or '').lower()
    return key.endswith('id') and any(hint in key or hint in label for hint in PERSONA_FIELD_HINTS)


def _column_looks_like_persona_tipo_fk(col):
    key = str(col.get('key') or '').lower()
    label = str(col.get('label') or '').lower()
    return any(hint in key or hint in label for hint in PERSONA_TIPO_FIELD_HINTS)


def _collect_dynamic_reference_ids(raw_rows, columns, dynamic_columns):
    persona_ids = set()
    persona_tipo_ids = set()
    persona_keys = [col.get('key') for col in dynamic_columns if _column_looks_like_persona_fk(col)]
    persona_tipo_keys = [col.get('key') for col in dynamic_columns if _column_looks_like_persona_tipo_fk(col)]

    if not persona_keys and not persona_tipo_keys:
        return [], []

    for raw in raw_rows:
        row_dict = dict(zip(columns, raw))
        body, _header = _parse_datajson(row_dict.get('DataJson'))
        for key in persona_keys:
            val = _body_get(body, key)
            if val is not None and str(val).strip():
                persona_ids.add(str(val).strip())
        for key in persona_tipo_keys:
            val = _body_get(body, key)
            if val is not None and str(val).strip():
                persona_tipo_ids.add(str(val).strip())

    return list(persona_ids), list(persona_tipo_ids)


def _resolve_dynamic_reference_value(col, raw_value, persona_lookup=None, persona_tipo_lookup=None):
    if raw_value is None or raw_value == '':
        return raw_value

    lookup_key = str(raw_value).strip()
    persona_lookup = persona_lookup or {}
    persona_tipo_lookup = persona_tipo_lookup or {}

    if _column_looks_like_persona_fk(col):
        persona = persona_lookup.get(lookup_key)
        if isinstance(persona, dict):
            nombre = str(persona.get('nombre') or '').strip()
            tipo = str(persona.get('tipo') or '').strip()
            if nombre and tipo:
                return f'{nombre} ({tipo})'
            if nombre:
                return nombre

    if _column_looks_like_persona_tipo_fk(col):
        persona_tipo = persona_tipo_lookup.get(lookup_key)
        if persona_tipo:
            return persona_tipo

    return raw_value


def _extract_dynamic_from_body(body, dynamic_columns, persona_lookup=None, persona_tipo_lookup=None):
    """Extrae valores dinámicos cruzando PlantillaCampo.JsonKey con body."""
    out = {}
    for col in dynamic_columns:
        key = col.get('key')
        val = _body_get(body, key)
        val = _resolve_dynamic_reference_value(col, val, persona_lookup, persona_tipo_lookup)
        out[key] = _to_serializable(val) if val is not None else None
    return out


def _fetch_lote_lookup(conn, lote_ids):
    """
    Obtiene diccionario {lote_id: {'codigo', 'descripcion', 'geo'}}.
    Tabla LOTE: ID_LOTE, codigo_lote, DESCRIPCION, Geom (geometry).
    """
    lookup = {}
    ids = [x for x in lote_ids if x is not None]
    if not ids:
        return lookup
    placeholders = ','.join(['?' for _ in ids])
    variants = [
        ("SELECT ID_LOTE, codigo_lote, DESCRIPCION, Geom.STAsText() FROM dbo.LOTE WHERE ID_LOTE IN ({})".format(placeholders), ids, 3),
        ("SELECT ID_LOTE, codigo_lote, DESCRIPCION FROM dbo.LOTE WHERE ID_LOTE IN ({})".format(placeholders), ids, -1),
    ]
    for sql, params, geo_idx in variants:
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            for row in cursor.fetchall():
                kid = row[0]
                codigo_lote = row[1]
                descripcion = row[2]
                geo = row[geo_idx] if geo_idx >= 0 and len(row) > geo_idx and row[geo_idx] else None
                if kid is not None:
                    cod = str(codigo_lote or '').strip() or str(kid)
                    desc = str(descripcion or '').strip()
                    lookup[str(kid)] = {
                        'codigo': cod,
                        'descripcion': desc,
                        'geo': str(geo).strip() if geo else None,
                    }
            cursor.close()
            if lookup:
                return lookup
        except Exception:
            continue
    return lookup


def _lote_geom_rows_to_lookup(cursor):
    """Convierte filas (ID_LOTE, codigo_lote, DESCRIPCION, WKT) en dict {str(id): {'codigo', 'descripcion', 'geo'}}."""
    lookup = {}
    for row in cursor.fetchall():
        kid = row[0]
        codigo_lote = row[1] if len(row) > 1 else None
        descripcion = row[2] if len(row) > 2 else None
        geo = row[3] if len(row) > 3 else None
        if kid is None:
            continue
        k = str(kid)
        g = str(geo).strip() if geo else None
        if not g:
            continue
        cod = str(codigo_lote or '').strip() or k
        desc = str(descripcion or '').strip()
        lookup[k] = {
            'codigo': cod,
            'descripcion': desc,
            'geo': g,
        }
    return lookup


def _fetch_lotes_geometry_por_area(conn, id_area):
    """
    Todos los registros de dbo.LOTE con geometría, filtrados por área del dashboard cuando
    el esquema lo permite (FUNDO/area_fundo/area_lote/LOTE.id_area, etc.).
    Si ninguna variante devuelve filas, último recurso: todos los lotes con Geom en LOTE.
    """
    if conn is None:
        return {}
    scoped_variants = []
    if id_area is not None:
        scoped_variants = [
            (
                """
                SELECT l.ID_LOTE, l.codigo_lote, l.DESCRIPCION, l.Geom.STAsText()
                FROM dbo.LOTE l
                INNER JOIN dbo.FUNDO f ON l.ID_FUNDO = f.ID_FUNDO
                WHERE f.id_area = ? AND l.Geom IS NOT NULL
                """,
                [id_area],
            ),
            (
                """
                SELECT l.ID_LOTE, l.codigo_lote, l.DESCRIPCION, l.Geom.STAsText()
                FROM dbo.LOTE l
                INNER JOIN dbo.FUNDO f ON l.ID_FUNDO = f.ID_FUNDO
                WHERE f.ID_AREA = ? AND l.Geom IS NOT NULL
                """,
                [id_area],
            ),
            (
                """
                SELECT l.ID_LOTE, l.codigo_lote, l.DESCRIPCION, l.Geom.STAsText()
                FROM dbo.LOTE l
                INNER JOIN dbo.FUNDO f ON l.ID_FUNDO = f.ID_FUNDO
                INNER JOIN dbo.area_fundo af ON af.ID_FUNDO = f.ID_FUNDO AND af.id_area = ?
                WHERE l.Geom IS NOT NULL
                """,
                [id_area],
            ),
            (
                """
                SELECT l.ID_LOTE, l.codigo_lote, l.DESCRIPCION, l.Geom.STAsText()
                FROM dbo.LOTE l
                INNER JOIN dbo.area_lote al ON al.ID_LOTE = l.ID_LOTE AND al.id_area = ?
                WHERE l.Geom IS NOT NULL
                """,
                [id_area],
            ),
            (
                """
                SELECT ID_LOTE, codigo_lote, DESCRIPCION, Geom.STAsText()
                FROM dbo.LOTE
                WHERE id_area = ? AND Geom IS NOT NULL
                """,
                [id_area],
            ),
        ]
    for sql, params in scoped_variants:
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            lookup = _lote_geom_rows_to_lookup(cursor)
            cursor.close()
            if lookup:
                return lookup
        except Exception:
            continue
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ID_LOTE, codigo_lote, DESCRIPCION, Geom.STAsText()
            FROM dbo.LOTE
            WHERE Geom IS NOT NULL
            """
        )
        lookup = _lote_geom_rows_to_lookup(cursor)
        cursor.close()
        return lookup
    except Exception:
        return {}


def _fetch_user_lookup(conn, user_ids):
    """
    Obtiene diccionario {user_id: nombre}.
    user_user: id, first_name, last_name.
    """
    lookup = {}
    ids = [x for x in user_ids if x is not None]
    if not ids:
        return lookup
    placeholders = ','.join(['?' for _ in ids])
    variants = [
        ("SELECT id, RTRIM(ISNULL(first_name,'') + ' ' + ISNULL(last_name,'')) AS Nombre FROM dbo.user_user WHERE id IN ({})".format(placeholders), ids),
        ("SELECT Id, Nombre FROM [User] WHERE Id IN ({})".format(placeholders), ids),
        ("SELECT Id, RTRIM(ISNULL(FirstName,'') + ' ' + ISNULL(LastName,'')) AS Nombre FROM [User] WHERE Id IN ({})".format(placeholders), ids),
        ("SELECT Id, Nombre FROM Usuario WHERE Id IN ({})".format(placeholders), ids),
        ("SELECT Id, Nombre FROM AspNetUsers WHERE Id IN ({})".format(placeholders), ids),
    ]
    for sql, params in variants:
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            cols = [c[0] for c in cursor.description]
            for row in cursor.fetchall():
                row_d = dict(zip(cols, row))
                kid = row_d.get('Id') or row_d.get('id')
                val = (row_d.get('Nombre') or row_d.get('nombre') or
                       ('{} {}'.format(row_d.get('FirstName', ''), row_d.get('LastName', '')).strip() or None))
                if kid is not None and val:
                    lookup[str(kid)] = str(val).strip()
            cursor.close()
            if lookup:
                return lookup
        except Exception:
            continue
    return lookup


def _fetch_persona_lookup(conn, persona_ids):
    """
    Obtiene diccionario {persona_id: {'nombre', 'tipo'}} desde PERSONA y PERSONA_TIPO.
    """
    lookup = {}
    ids = [str(x).strip() for x in persona_ids if x is not None and str(x).strip()]
    if not ids:
        return lookup
    uniq = list(dict.fromkeys(ids))
    placeholders = ','.join(['?' for _ in uniq])
    sql = """
        SELECT p.ID_PERSONA, p.NOMBRE_COMPLETO, pt.DESCRIPCION
        FROM dbo.PERSONA p
        LEFT JOIN dbo.PERSONA_TIPO pt ON pt.ID_PERSONA_TIPO = p.ID_PERSONA_TIPO
        WHERE p.ID_PERSONA IN ({})
    """.format(placeholders)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, uniq)
        for row in cursor.fetchall():
            persona_id, nombre, persona_tipo = row[0], row[1], row[2]
            if persona_id is None:
                continue
            lookup[str(persona_id).strip()] = {
                'nombre': str(nombre or '').strip(),
                'tipo': str(persona_tipo or '').strip(),
            }
        cursor.close()
    except Exception:
        pass
    return lookup


def _fetch_persona_tipo_lookup(conn, persona_tipo_ids):
    """
    Obtiene diccionario {persona_tipo_id: descripcion} desde PERSONA_TIPO.
    """
    lookup = {}
    ids = [str(x).strip() for x in persona_tipo_ids if x is not None and str(x).strip()]
    if not ids:
        return lookup
    uniq = list(dict.fromkeys(ids))
    placeholders = ','.join(['?' for _ in uniq])
    sql = "SELECT ID_PERSONA_TIPO, DESCRIPCION FROM dbo.PERSONA_TIPO WHERE ID_PERSONA_TIPO IN ({})".format(placeholders)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, uniq)
        for row in cursor.fetchall():
            persona_tipo_id, descripcion = row[0], row[1]
            if persona_tipo_id is not None:
                lookup[str(persona_tipo_id).strip()] = str(descripcion or '').strip()
        cursor.close()
    except Exception:
        pass
    return lookup


def _fetch_campania_lookup(conn, campania_ids):
    """
    Obtiene diccionario {ID_CAMPANIA: DESCRIPCION}.
    Tabla dbo.CAMPANIA: ID_CAMPANIA varchar(8), DESCRIPCION varchar(50).
    """
    lookup = {}
    ids = [str(x).strip() for x in campania_ids if x is not None and str(x).strip()]
    if not ids:
        return lookup
    uniq = list(dict.fromkeys(ids))
    placeholders = ','.join(['?' for _ in uniq])
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID_CAMPANIA, DESCRIPCION FROM dbo.CAMPANIA WHERE ID_CAMPANIA IN ({})".format(placeholders),
            uniq
        )
        for row in cursor.fetchall():
            kid, desc = row[0], row[1]
            if kid is not None:
                k = str(kid).strip()
                lookup[k] = str(desc or '').strip() or k
        cursor.close()
    except Exception:
        pass
    return lookup


class EvaluacionesAPIView(View):
    """
    GET /cartillas-agricolas/api/evaluaciones/
    Params: plantilla_id, fecha, lote_id (opcional), user_id (opcional)
    Respuesta: base_columns, dynamic_columns, rows (base, dynamic, map), kpis, map_points
    """

    def get(self, request):
        plantilla_id = request.GET.get('plantilla_id', '2')
        fecha = request.GET.get('fecha')
        lote_id = request.GET.get('lote_id')
        user_id = request.GET.get('user_id')

        if not fecha:
            return JsonResponse({'error': 'El parámetro fecha es requerido (formato: YYYY-MM-DD)'}, status=400)

        if not connection_app_agricola:
            return JsonResponse({'error': 'Conexión a BD no disponible'}, status=500)

        try:
            payload = self._build_response(
                plantilla_id=plantilla_id,
                fecha=fecha,
                lote_id=lote_id,
                user_id=user_id,
            )
            return JsonResponse(payload)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def _build_response(self, plantilla_id, fecha, lote_id=None, user_id=None):
        dynamic_columns = _get_dynamic_columns(connection_app_agricola, plantilla_id)
        # Para tabla: solo las dinámicas con visibleInTable
        dynamic_columns_table = [c for c in dynamic_columns if c.get('visibleInTable', True)]
        # Para modal: todas las dinámicas activas
        dynamic_columns_modal = dynamic_columns

        kpis, rows, map_points = self._fetch_and_process(
            plantilla_id=plantilla_id,
            fecha=fecha,
            lote_id=lote_id,
            user_id=user_id,
            dynamic_columns=dynamic_columns,
        )

        # GEO del lote (primera fila con lote_geo) para dibujar en mapa
        lote_geo = None
        lote_codigo = None
        for r in rows:
            b = r.get('base') or {}
            if b.get('lote_geo'):
                lote_geo = b['lote_geo']
                lote_codigo = b.get('lote') or '—'
                break

        return {
            'base_columns': BASE_COLUMNS,
            'dynamic_columns': dynamic_columns_table,
            'dynamic_columns_modal': dynamic_columns_modal,
            'rows': rows,
            'kpis': kpis,
            'map_points': map_points,
            'lote_geo': lote_geo,
            'lote_codigo': lote_codigo,
        }

    def _fetch_and_process(self, plantilla_id, fecha, lote_id, user_id, dynamic_columns):
        if not connection_app_agricola:
            return self._empty_response()

        sql = """
            SELECT RegistroId, PlantillaId, FechaEjecucion, LoteId, UserId, CampaniaId AS ID_CAMPANIA, DataJson
            FROM PlantillaRegistro
            WHERE PlantillaId = ? AND CAST(FechaEjecucion AS DATE) = CAST(? AS DATE)
        """
        params = [plantilla_id, fecha]
        if lote_id:
            sql += " AND (LoteId = ? OR CAST(LoteId AS VARCHAR(50)) = ?)"
            params.extend([lote_id, str(lote_id)])
        if user_id:
            sql += " AND (UserId = ? OR CAST(UserId AS VARCHAR(50)) = ?)"
            params.extend([user_id, str(user_id)])
        sql += " ORDER BY FechaEjecucion"

        cursor = connection_app_agricola.cursor()
        cursor.execute(sql, params)
        raw_rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        cursor.close()

        # Lookups por LoteId y UserId para mostrar codigo_lote y nombre
        lote_ids = list({dict(zip(columns, r)).get('LoteId') for r in raw_rows})
        user_ids = list({dict(zip(columns, r)).get('UserId') for r in raw_rows})
        lote_ids = [x for x in lote_ids if x is not None]
        user_ids = [x for x in user_ids if x is not None]
        lote_lookup = _fetch_lote_lookup(connection_app_agricola, lote_ids)
        user_lookup = _fetch_user_lookup(connection_app_agricola, user_ids)
        campania_ids = [dict(zip(columns, r)).get('ID_CAMPANIA') for r in raw_rows]
        campania_ids = [x for x in campania_ids if x is not None and str(x).strip()]
        campania_lookup = _fetch_campania_lookup(connection_app_agricola, campania_ids)
        plantilla_lookup = _fetch_plantilla_nombre_lookup(connection_app_agricola, plantilla_id)
        persona_ids, persona_tipo_ids = _collect_dynamic_reference_ids(raw_rows, columns, dynamic_columns)
        persona_lookup = _fetch_persona_lookup(connection_app_agricola, persona_ids)
        persona_tipo_lookup = _fetch_persona_tipo_lookup(connection_app_agricola, persona_tipo_ids)

        return self._process_rows(
            columns, raw_rows, dynamic_columns, lote_lookup, user_lookup, campania_lookup, plantilla_lookup,
            persona_lookup, persona_tipo_lookup
        )

    def _process_rows(self, columns, raw_rows, dynamic_columns, lote_lookup=None, user_lookup=None, campania_lookup=None, plantilla_lookup=None, persona_lookup=None, persona_tipo_lookup=None):
        rows = []
        map_points = []
        valores_muestras = []
        lote_lookup = lote_lookup or {}
        user_lookup = user_lookup or {}
        campania_lookup = campania_lookup or {}
        plantilla_lookup = plantilla_lookup or {}
        persona_lookup = persona_lookup or {}
        persona_tipo_lookup = persona_tipo_lookup or {}

        for raw in raw_rows:
            row_dict = dict(zip(columns, raw))
            datajson_raw = row_dict.get('DataJson')
            body, header = _parse_datajson(datajson_raw)

            base = _extract_base_from_row(
                row_dict, body, header, lote_lookup, user_lookup, campania_lookup, plantilla_lookup
            )
            dynamic = _extract_dynamic_from_body(body, dynamic_columns, persona_lookup, persona_tipo_lookup)

            lat = (body.get('lat') or body.get('Lat') or body.get('latitude') or
                   header.get('lat') or header.get('Lat') or header.get('latitude') or row_dict.get('Lat'))
            lon = (body.get('lon') or body.get('Lon') or body.get('longitude') or
                   header.get('lon') or header.get('Lon') or header.get('longitude') or row_dict.get('Lon'))

            map_data = None
            if lat is not None and lon is not None:
                map_data = {'lat': _to_serializable(lat), 'lon': _to_serializable(lon)}
                map_points.append({
                    'lat': _to_serializable(lat),
                    'lon': _to_serializable(lon),
                    'RegistroId': row_dict.get('RegistroId'),
                    'idLote': _to_serializable(row_dict.get('LoteId')),
                })

            rows.append({
                'id': row_dict.get('RegistroId'),
                'base': base,
                'dynamic': dynamic,
                'map': map_data,
            })

            # KPI: cantidadMuestras (o variantes) para métricas
            cant = _safe_float(_body_get(body, 'cantidadMuestras') or
                              _body_get(body, 'cantidad_muestras') or
                              _body_get(body, 'CantidadMuestras'))
            if cant is not None:
                valores_muestras.append(cant)

        n = len(valores_muestras)
        if n == 0:
            kpis = {
                'acumulado': 0,
                'promedio': 0,
                'maximo': 0,
                'minimo': 0,
                'muestras': len(rows),
            }
        else:
            kpis = {
                'acumulado': round(sum(valores_muestras), 2),
                'promedio': round(sum(valores_muestras) / n, 2),
                'maximo': round(max(valores_muestras), 2),
                'minimo': round(min(valores_muestras), 2),
                'muestras': len(rows),
            }

        return kpis, rows, map_points

    def _empty_response(self):
        return (
            {'acumulado': 0, 'promedio': 0, 'maximo': 0, 'minimo': 0, 'muestras': 0},
            [],
            [],
        )
