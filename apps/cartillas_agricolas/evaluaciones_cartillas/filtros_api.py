"""
API Init y Filtros - Cartillas Agrícolas
Carga inicial y filtros dinámicos por área. Lotes y evaluadores desde datos reales.
"""
import json
from datetime import date
from decimal import Decimal

from django.http import JsonResponse
from django.views import View

from apps.cartillas_agricolas.evaluaciones_cartillas.api_views import (
    BASE_COLUMNS,
    _body_get,
    _collect_dynamic_reference_ids,
    _extract_base_from_row,
    _extract_dynamic_from_body,
    _fetch_campania_lookup,
    _fetch_lote_lookup,
    _fetch_lotes_geometry_por_area,
    _fetch_persona_lookup,
    _fetch_persona_tipo_lookup,
    _fetch_plantilla_lookup,
    _fetch_user_lookup,
    _get_dynamic_columns,
    _intersect_dynamic_columns,
    _parse_datajson,
    _safe_float,
    _to_serializable,
)

try:
    from apps.connection.connect_app_agricola import connection_app_agricola
except ImportError:
    connection_app_agricola = None

try:
    from apps.cartillas_agricolas.services import get_plantillas_por_area
except ImportError:
    def get_plantillas_por_area(id_area):
        return []


def _fetch_registros_para_combos(conn, id_area, fecha, plantilla_id=None):
    """
    Dataset BASE para combos: solo areaId, fecha, plantillaId.
    Usado para poblar lotes y evaluadores. NO incluye loteId ni evaluadorId.
    """
    sql = """
        SELECT pr.RegistroId, pr.PlantillaId, pr.FechaEjecucion, pr.LoteId, pr.UserId, pr.CampaniaId AS ID_CAMPANIA, pr.DataJson
        FROM PlantillaRegistro pr
        INNER JOIN dbo.area_plantilla ap ON ap.id_plantilla = pr.PlantillaId
            AND ap.id_area = ? AND ap.is_active = 1
        WHERE CAST(pr.FechaEjecucion AS DATE) = CAST(? AS DATE)
    """
    params = [id_area, fecha]
    if plantilla_id is not None and plantilla_id != '':
        sql += " AND pr.PlantillaId = ?"
        params.append(plantilla_id)
    sql += " ORDER BY pr.FechaEjecucion"
    cursor = conn.cursor()
    cursor.execute(sql, params)
    raw = cursor.fetchall()
    cols = [c[0] for c in cursor.description]
    cursor.close()
    return raw, cols


def _fetch_registros_resultados(conn, id_area, fecha, plantilla_id=None, lote_id=None, evaluador_id=None):
    """
    Dataset FINAL para resultados: areaId, fecha, plantillaId, loteId?, evaluadorId?.
    Usado para tabla, mapa, KPIs.
    """
    sql = """
        SELECT pr.RegistroId, pr.PlantillaId, pr.FechaEjecucion, pr.LoteId, pr.UserId, pr.CampaniaId AS ID_CAMPANIA, pr.DataJson
        FROM PlantillaRegistro pr
        INNER JOIN dbo.area_plantilla ap ON ap.id_plantilla = pr.PlantillaId
            AND ap.id_area = ? AND ap.is_active = 1
        WHERE CAST(pr.FechaEjecucion AS DATE) = CAST(? AS DATE)
    """
    params = [id_area, fecha]
    if plantilla_id is not None and plantilla_id != '':
        sql += " AND pr.PlantillaId = ?"
        params.append(plantilla_id)
    if lote_id is not None and str(lote_id).strip() != '':
        lote_str = str(lote_id).strip()
        params.append(lote_str)
        try:
            params.append(int(float(lote_str)))
        except (ValueError, TypeError):
            params.append(lote_str)
        sql += " AND (CAST(pr.LoteId AS VARCHAR(50)) = ? OR pr.LoteId = ?)"
    if evaluador_id is not None and str(evaluador_id).strip() != '':
        ev_str = str(evaluador_id).strip()
        params.append(ev_str)
        try:
            params.append(int(float(ev_str)))
        except (ValueError, TypeError):
            params.append(ev_str)
        sql += " AND (CAST(pr.UserId AS VARCHAR(50)) = ? OR pr.UserId = ?)"
    sql += " ORDER BY pr.FechaEjecucion"
    cursor = conn.cursor()
    cursor.execute(sql, params)
    raw = cursor.fetchall()
    cols = [c[0] for c in cursor.description]
    cursor.close()
    return raw, cols


def _extraer_lotes_evaluadores_distintos(rows, columns):
    """Extrae LoteId y UserId únicos de las filas."""
    lote_ids = set()
    user_ids = set()
    for r in rows:
        d = dict(zip(columns, r))
        lid = d.get('LoteId')
        uid = d.get('UserId')
        if lid is not None:
            lote_ids.add(str(lid))
        if uid is not None:
            user_ids.add(str(uid))
    return list(lote_ids), list(user_ids)


def _extraer_campania_ids(rows, columns):
    """IDs de campaña distintos (CampaniaId expuesto como ID_CAMPANIA en el SELECT)."""
    ids = []
    for r in rows:
        d = dict(zip(columns, r))
        cid = d.get('ID_CAMPANIA')
        if cid is not None and str(cid).strip():
            ids.append(str(cid).strip())
    return list(dict.fromkeys(ids))


def _extraer_plantilla_ids_orden(rows, columns):
    """PlantillaId distintos en orden de aparición (para intersección de columnas)."""
    seen = set()
    ordered = []
    for r in rows:
        d = dict(zip(columns, r))
        pid = d.get('PlantillaId')
        if pid is None:
            continue
        k = str(pid).strip()
        if k and k not in seen:
            seen.add(k)
            ordered.append(pid)
    return ordered


def _build_lotes_combo(conn, lote_ids, lote_lookup=None):
    """Convierte lote_ids en lista {idLote, nombreLote} usando LOTE."""
    if not lote_ids:
        return []
    combo = []
    lookup = lote_lookup if lote_lookup is not None else _fetch_lote_lookup(conn, [x for x in lote_ids if x])
    for lid in lote_ids:
        info = lookup.get(str(lid))
        if isinstance(info, dict):
            d = (info.get('descripcion') or '').strip()
            nombre = d or info.get('codigo', str(lid))
        else:
            nombre = str(lid)
        combo.append({'idLote': lid, 'nombreLote': nombre})
    return sorted(combo, key=lambda x: str(x['nombreLote']))


def _map_lotes_list_from_lookup(lotes_area_lookup):
    """Lista map_lotes desde el lookup completo de LOTE (todos los polígonos del área / tabla)."""
    if not lotes_area_lookup:
        return []
    out = []
    for lid in sorted(lotes_area_lookup.keys(), key=lambda x: (len(str(x)), str(x))):
        info = lotes_area_lookup[lid]
        g = info.get('geo')
        if not g:
            continue
        out.append({
            'idLote': lid,
            'codigo': info.get('codigo', lid),
            'geo': g,
        })
    return out


def _build_evaluadores_combo(conn, user_ids):
    """Convierte user_ids en lista {idEvaluador, nombreEvaluador} usando User/Usuario."""
    if not user_ids:
        return []
    combo = []
    lookup = _fetch_user_lookup(conn, [x for x in user_ids if x])
    for uid in user_ids:
        nombre = lookup.get(str(uid), str(uid))
        combo.append({'idEvaluador': uid, 'nombreEvaluador': str(nombre)})
    return sorted(combo, key=lambda x: str(x['nombreEvaluador']))


def _process_rows_to_payload(
    columns, raw_rows, dynamic_columns, lote_lookup, user_lookup, campania_lookup=None, plantilla_lookup=None,
    persona_lookup=None, persona_tipo_lookup=None
):
    """Procesa filas a rows, map_points, kpis."""
    rows = []
    map_points = []
    valores_muestras = []
    for raw in raw_rows:
        row_dict = dict(zip(columns, raw))
        datajson_raw = row_dict.get('DataJson')
        body, header = _parse_datajson(datajson_raw)
        base = _extract_base_from_row(
            row_dict, body, header, lote_lookup, user_lookup, campania_lookup, plantilla_lookup
        )
        dynamic = _extract_dynamic_from_body(body, dynamic_columns, persona_lookup, persona_tipo_lookup)
        lat = (body.get('lat') or body.get('Lat') or body.get('latitude') or
               header.get('lat') or header.get('Lat') or row_dict.get('Lat'))
        lon = (body.get('lon') or body.get('Lon') or body.get('longitude') or
               header.get('lon') or header.get('Lon') or row_dict.get('Lon'))
        map_data = None
        if lat is not None and lon is not None:
            map_data = {'lat': _to_serializable(lat), 'lon': _to_serializable(lon)}
            map_points.append({
                'lat': _to_serializable(lat), 'lon': _to_serializable(lon),
                'RegistroId': row_dict.get('RegistroId'),
                'idLote': _to_serializable(row_dict.get('LoteId')),
            })
        rows.append({'id': row_dict.get('RegistroId'), 'base': base, 'dynamic': dynamic, 'map': map_data})
        cant = _safe_float(_body_get(body, 'cantidadMuestras') or _body_get(body, 'cantidad_muestras') or
                          _body_get(body, 'CantidadMuestras'))
        if cant is not None:
            valores_muestras.append(cant)
    n = len(valores_muestras)
    kpis = {
        'acumulado': round(sum(valores_muestras), 2) if n else 0,
        'promedio': round(sum(valores_muestras) / n, 2) if n else 0,
        'maximo': round(max(valores_muestras), 2) if n else 0,
        'minimo': round(min(valores_muestras), 2) if n else 0,
        'muestras': len(rows),
    }
    return rows, map_points, kpis


def _get_dynamic_columns_for_area(conn, raw_rows, columns, plantilla_id=None):
    """
    Columnas dinámicas: con plantilla_id filtrada, de esa plantilla.
    Con 'Todas las cartillas', intersección de JsonKey entre todas las plantillas presentes en rows.
    """
    if plantilla_id is not None and plantilla_id != '':
        return _get_dynamic_columns(conn, plantilla_id)
    ordered = _extraer_plantilla_ids_orden(raw_rows, columns)
    if not ordered:
        return []
    if len(ordered) == 1:
        return _get_dynamic_columns(conn, ordered[0])
    return _intersect_dynamic_columns(conn, ordered)


class CartillasInitAPIView(View):
    """
    GET /cartillas-agricolas/api/init/?areaId=X
    Carga inicial: fecha=hoy, plantillas del área, lotes y evaluadores desde datos, tabla y mapa.
    """

    def get(self, request):
        area_id_raw = request.GET.get('areaId')
        if not area_id_raw:
            return JsonResponse({'error': 'areaId es requerido'}, status=400)
        try:
            area_id = int(area_id_raw)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'areaId debe ser numérico'}, status=400)
        if not connection_app_agricola:
            return JsonResponse({'error': 'Conexión a BD no disponible'}, status=500)
        hoy = date.today().isoformat()
        payload = self._build_response(area_id, hoy, None, None, None)
        return JsonResponse(payload)

    def _build_response(self, area_id, fecha, plantilla_id, lote_id, evaluador_id):
        plantillas = get_plantillas_por_area(area_id)

        # A. Dataset BASE para combos: solo area, fecha, cartilla (sin lote ni evaluador)
        raw_combos, cols_combos = _fetch_registros_para_combos(
            connection_app_agricola, area_id, fecha, plantilla_id
        )
        lote_ids_combo, user_ids_combo = _extraer_lotes_evaluadores_distintos(raw_combos, cols_combos)
        # B. Dataset FINAL para resultados: incluye lote y evaluador como filtros
        raw_rows, columns = _fetch_registros_resultados(
            connection_app_agricola, area_id, fecha,
            plantilla_id, lote_id, evaluador_id
        )
        dynamic_columns = _get_dynamic_columns_for_area(
            connection_app_agricola, raw_rows, columns, plantilla_id
        )
        dynamic_table = [c for c in dynamic_columns if c.get('visibleInTable', True)]
        lote_ids_res, user_ids_res = _extraer_lotes_evaluadores_distintos(raw_rows, columns)
        lotes_area_lookup = _fetch_lotes_geometry_por_area(connection_app_agricola, area_id)
        lote_ids_union = list(dict.fromkeys(
            [x for x in lote_ids_combo if x is not None] + [x for x in lote_ids_res if x is not None]
        ))
        lote_lookup = dict(lotes_area_lookup)
        missing_for_lookup = [x for x in lote_ids_union if str(x) not in lote_lookup]
        if missing_for_lookup:
            lote_lookup.update(_fetch_lote_lookup(connection_app_agricola, missing_for_lookup))
        lotes_combo = _build_lotes_combo(connection_app_agricola, lote_ids_combo, lote_lookup)
        map_lotes = _map_lotes_list_from_lookup(lotes_area_lookup)
        map_lotes_highlight_ids = list(dict.fromkeys(str(x) for x in lote_ids_res if x is not None))
        evaluadores_combo = _build_evaluadores_combo(connection_app_agricola, user_ids_combo)
        user_lookup = _fetch_user_lookup(connection_app_agricola, user_ids_res)
        campania_lookup = _fetch_campania_lookup(
            connection_app_agricola, _extraer_campania_ids(raw_rows, columns)
        )
        plantilla_lookup = _fetch_plantilla_lookup(
            connection_app_agricola, _extraer_plantilla_ids_orden(raw_rows, columns)
        )
        persona_ids, persona_tipo_ids = _collect_dynamic_reference_ids(raw_rows, columns, dynamic_columns)
        persona_lookup = _fetch_persona_lookup(connection_app_agricola, persona_ids)
        persona_tipo_lookup = _fetch_persona_tipo_lookup(connection_app_agricola, persona_tipo_ids)
        rows, map_points, kpis = _process_rows_to_payload(
            columns, raw_rows, dynamic_columns, lote_lookup, user_lookup, campania_lookup, plantilla_lookup,
            persona_lookup, persona_tipo_lookup
        )
        lote_geo = None
        lote_codigo = None
        for r in rows:
            b = r.get('base') or {}
            if b.get('lote_geo'):
                lote_geo = b['lote_geo']
                lote_codigo = b.get('lote') or '—'
                break
        return {
            'plantillas': plantillas,
            'lotes': lotes_combo,
            'evaluadores': evaluadores_combo,
            'base_columns': BASE_COLUMNS,
            'dynamic_columns': dynamic_table,
            'dynamic_columns_modal': dynamic_columns,
            'rows': rows,
            'kpis': kpis,
            'map_points': map_points,
            'map_lotes': map_lotes,
            'map_lotes_highlight_ids': map_lotes_highlight_ids,
            'lote_geo': lote_geo,
            'lote_codigo': lote_codigo,
            'fecha': fecha,
        }


class CartillasFiltrosAPIView(View):
    """
    POST /cartillas-agricolas/api/filtros/
    Body: { areaId, fecha, plantillaId?, loteId?, evaluadorId? }
    Retorna datos filtrados + combos actualizados (plantillas, lotes, evaluadores).
    """

    def post(self, request):
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = request.POST.dict() if hasattr(request.POST, 'dict') else {}
        area_id = body.get('areaId')
        fecha = body.get('fecha')
        if not area_id:
            return JsonResponse({'error': 'areaId es requerido'}, status=400)
        if not fecha:
            return JsonResponse({'error': 'fecha es requerida'}, status=400)
        try:
            area_id = int(area_id)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'areaId debe ser numérico'}, status=400)
        plantilla_id = body.get('plantillaId') or body.get('plantilla_id')
        lote_id = body.get('loteId') or body.get('lote_id')
        evaluador_id = body.get('evaluadorId') or body.get('evaluador_id')
        if plantilla_id is not None and str(plantilla_id).strip() == '':
            plantilla_id = None
        if lote_id is not None and str(lote_id).strip() == '':
            lote_id = None
        if evaluador_id is not None and str(evaluador_id).strip() == '':
            evaluador_id = None
        if not connection_app_agricola:
            return JsonResponse({'error': 'Conexión a BD no disponible'}, status=500)
        view = CartillasInitAPIView()
        payload = view._build_response(area_id, fecha, plantilla_id, lote_id, evaluador_id)
        return JsonResponse(payload)
