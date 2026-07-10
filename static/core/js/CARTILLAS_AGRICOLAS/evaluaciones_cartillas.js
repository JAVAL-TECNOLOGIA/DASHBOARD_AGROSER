/**
 * Cartillas Agrícolas - Dashboard con filtros dinámicos
 * Init: carga inicial con fecha=hoy, plantillas/lotes/evaluadores desde datos.
 * Filtros: dependientes, combos desde dataset filtrado.
 */
(function() {
    'use strict';

    var API_INIT = '/cartillas-agricolas/api/init/';
    var API_FILTROS = '/cartillas-agricolas/api/filtros/';
    var mapInstance = null;
    var mapMarkers = [];
    var lotesLayerGroup = null;
    var lotesLabelsLayerGroup = null;
    var lotesMapZoomHandler = null;
    var mapModalInstance = null;
    var mapModalMarker = null;
    var modalMapPending = null;
    var modalShownMapHandler = null;
    var TRUNCATE_LENGTH = 50;
    /**
     * World Imagery: en muchas zonas agrícolas las teselas reales fallan ya en z≥18 (mensaje "Map data not yet available").
     * maxNativeZoom bajo: Leaflet solo pide hasta ese {z} y escala hacia arriba → más zoom de usuario sin teselas grises.
     * Subir maxNativeZoom (p. ej. 18) si en tu zona siempre hay imagen nítida y quieres menos “pixelado” al acercar.
     */
    var ESRI_WORLD_IMAGERY_TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
    var ESRI_WORLD_IMAGERY_TILE_OPTIONS = {
        attribution: '&copy; Esri',
        maxZoom: 23,
        maxNativeZoom: 17
    };
    var currentIdArea = null;
    var loading = false;
    var lastFiltrosRequestId = 0;
    var pendingFiltrosXhr = null;
    var lastFechaVal = null;
    var state = { areaId: null, fecha: null, plantillaId: null, loteId: null, evaluadorId: null };

    function getCsrfToken() {
        var name = 'csrftoken';
        var cookies = document.cookie ? document.cookie.split(';') : [];
        for (var i = 0; i < cookies.length; i++) {
            var parts = cookies[i].trim().split('=');
            if (parts[0] === name) return decodeURIComponent(parts[1] || '');
        }
        return ($('[name=csrfmiddlewaretoken]').val && $('[name=csrfmiddlewaretoken]').val()) || '';
    }

    function obtenerIdAreaDesdeRuta() {
        var $content = $('#content');
        if ($content.length && $content.data('id-area')) {
            var id = parseInt($content.data('id-area'), 10);
            return isNaN(id) ? null : id;
        }
        var match = window.location.pathname.match(/\/cartillas-agricolas\/(\d+)/);
        if (match) {
            var n = parseInt(match[1], 10);
            return isNaN(n) ? null : n;
        }
        return null;
    }

    function fechaToYMD(fechaStr) {
        if (!fechaStr) return null;
        var parts = String(fechaStr).split('/');
        if (parts.length === 3) return parts[2] + '-' + parts[1] + '-' + parts[0];
        return fechaStr;
    }

    function fechaToDMY(ymd) {
        if (!ymd) return '';
        var p = String(ymd).split('-');
        if (p.length === 3) return p[2] + '/' + p[1] + '/' + p[0];
        return ymd;
    }

    function getState() {
        var fecha = fechaToYMD($('#filtro-fecha').val());
        return {
            areaId: currentIdArea,
            fecha: fecha,
            plantillaId: $('#filtro-cartilla').val() || null,
            loteId: $('#filtro-lote').val() || null,
            evaluadorId: $('#filtro-evaluador').val() || null
        };
    }

    function fillPlantillas(items) {
        var $sel = $('#filtro-cartilla');
        var current = $sel.val();
        $sel.empty().append('<option value="">Todas las cartillas</option>');
        (items || []).forEach(function(p) {
            var v = p.idPlantilla || p.id;
            var n = p.nombrePlantilla || p.nombre || v;
            $sel.append('<option value="' + v + '">' + n + '</option>');
        });
        if (current && $sel.find('option[value="' + current + '"]').length) $sel.val(current);
    }

    function fillLotes(items) {
        var $sel = $('#filtro-lote');
        var current = $sel.val();
        $sel.empty().append('<option value="">Todos los lotes</option>');
        (items || []).forEach(function(l) {
            var v = l.idLote || l.id;
            var n = l.nombreLote || l.nombre || v;
            $sel.append('<option value="' + v + '">' + n + '</option>');
        });
        if (current && $sel.find('option[value="' + current + '"]').length) $sel.val(current);
    }

    function fillEvaluadores(items) {
        var $sel = $('#filtro-evaluador');
        var current = $sel.val();
        $sel.empty().append('<option value="">Todos los evaluadores</option>');
        (items || []).forEach(function(e) {
            var v = e.idEvaluador || e.id;
            var n = e.nombreEvaluador || e.nombre || v;
            $sel.append('<option value="' + v + '">' + n + '</option>');
        });
        if (current && $sel.find('option[value="' + current + '"]').length) $sel.val(current);
    }

    function formatVal(val) {
        if (val === null || val === undefined || val === '') return '—';
        return String(val);
    }

    function escapeHtml(s) {
        if (s === null || s === undefined) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function buildModalFieldSection(title, iconClass, cols, dataObj) {
        if (!cols || cols.length === 0) return '';
        var html = '<div class="eval-modal-section">';
        html += '<div class="eval-modal-section-title"><i class="fa ' + iconClass + '"></i> ' + escapeHtml(title) + '</div>';
        html += '<div class="row eval-modal-fields">';
        cols.forEach(function(c) {
            var raw = dataObj[c.key];
            var display = formatVal(raw);
            var wide = (c.type || '').toLowerCase() === 'text' || (c.key || '').toLowerCase().indexOf('observacion') >= 0;
            var colClass = wide ? 'col-xs-12' : 'col-sm-6 col-md-4';
            html += '<div class="' + colClass + ' eval-modal-field">';
            html += '<div class="eval-modal-field-label">' + escapeHtml(c.label || c.key) + '</div>';
            html += '<div class="eval-modal-field-value">' + escapeHtml(display) + '</div>';
            html += '</div>';
        });
        html += '</div></div>';
        return html;
    }

    function truncate(val, maxLen) {
        if (val === null || val === undefined || val === '') return '—';
        var s = String(val);
        return s.length <= maxLen ? s : s.substring(0, maxLen) + '...';
    }

    function isLongTextColumn(col) {
        var t = (col.type || 'string').toLowerCase();
        if (t === 'text' || t === 'string') return true;
        var k = (col.key || '').toLowerCase();
        return k.indexOf('observacion') >= 0 || k.indexOf('nota') >= 0 || k.indexOf('comentario') >= 0;
    }

    function renderKPIs(kpis) {
        $('#kpi-acumulado').text(formatVal((kpis || {}).acumulado));
        $('#kpi-promedio').text(formatVal((kpis || {}).promedio));
        $('#kpi-maximo').text(formatVal((kpis || {}).maximo));
        $('#kpi-minimo').text(formatVal((kpis || {}).minimo));
        $('#kpi-muestras').text(formatVal((kpis || {}).muestras));
    }

    function buildTableHeader(baseCols, dynamicCols) {
        var ths = [];
        (baseCols || []).forEach(function(c) { ths.push('<th>' + (c.label || c.key) + '</th>'); });
        (dynamicCols || []).forEach(function(c) { ths.push('<th>' + (c.label || c.key) + '</th>'); });
        return '<tr>' + ths.join('') + '</tr>';
    }

    function buildTableRows(rows, baseCols, dynamicCols) {
        var trs = [];
        (rows || []).forEach(function(r, idx) {
            var tds = [];
            var base = r.base || {}, dynamic = r.dynamic || {};
            (baseCols || []).forEach(function(c) { tds.push('<td>' + formatVal(base[c.key]) + '</td>'); });
            (dynamicCols || []).forEach(function(c) {
                var val = dynamic[c.key];
                var displayVal = formatVal(val);
                if (isLongTextColumn(c) && val && String(val).length > TRUNCATE_LENGTH) {
                    displayVal = truncate(val, TRUNCATE_LENGTH);
                    tds.push('<td class="evaluaciones-cell-truncate" title="' + (String(val).replace(/"/g, '&quot;')) + '">' + displayVal + '</td>');
                } else {
                    tds.push('<td>' + displayVal + '</td>');
                }
            });
            var rowId = r.id != null ? r.id : 'r' + idx;
            trs.push('<tr class="evaluaciones-row-clickable" data-row-id="' + rowId + '" data-row-index="' + idx + '">' + tds.join('') + '</tr>');
        });
        return trs.join('');
    }

    function renderTable(data) {
        var baseCols = data.base_columns || [], dynamicCols = data.dynamic_columns || [];
        var rows = Array.isArray(data.rows) ? data.rows : [];
        var allCols = baseCols.concat(dynamicCols);
        var $tbody = $('#tabla-evaluaciones-body');

        if ($.fn.DataTable.isDataTable('#tabla-evaluaciones')) {
            $('#tabla-evaluaciones').DataTable().destroy();
        }
        $('#tabla-evaluaciones-thead').html(buildTableHeader(baseCols, dynamicCols));
        $tbody.empty();
        if (rows.length === 0) {
            $tbody.html('<tr><td colspan="' + Math.max(allCols.length, 1) + '" class="text-center text-muted">No hay registros para los filtros seleccionados</td></tr>');
        } else {
            $tbody.html(buildTableRows(rows, baseCols, dynamicCols));
        }
        if (rows.length > 0) {
            $('#tabla-evaluaciones').DataTable({ paging: true, pageLength: 10, lengthChange: true, searching: true, ordering: true, info: true, autoWidth: false });
        }
        $tbody.data('evaluaciones-rows', rows);
        $tbody.data('evaluaciones-base-cols', baseCols);
        $tbody.data('evaluaciones-dynamic-cols-modal', data.dynamic_columns_modal || dynamicCols);
    }

    function exportarCSV() {
        var rows = $('#tabla-evaluaciones-body').data('evaluaciones-rows');
        var baseCols = $('#tabla-evaluaciones-body').data('evaluaciones-base-cols');
        var dynamicCols = $('#tabla-evaluaciones-body').data('evaluaciones-dynamic-cols-modal');
        if (!rows || rows.length === 0) {
            (typeof swal !== 'undefined' ? swal('Sin datos', 'No hay registros para exportar', 'info') : alert('No hay registros para exportar'));
            return;
        }
        var allCols = (baseCols || []).concat(dynamicCols || []);
        var lines = [allCols.map(function(c) { return (c.label || c.key || '').replace(/"/g, '""'); }).join(';')];
        rows.forEach(function(r) {
            var base = r.base || {}, dynamic = r.dynamic || {};
            lines.push(allCols.map(function(c) { var v = base[c.key] != null ? base[c.key] : (dynamic[c.key] != null ? dynamic[c.key] : ''); return '"' + String(v).replace(/"/g, '""') + '"'; }).join(';'));
        });
        var blob = new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'evaluaciones_' + ($('#filtro-fecha').val() || '').replace(/\//g, '-') + '.csv';
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
    }

    function toggleDensidadTabla() {
        var $t = $('#tabla-evaluaciones');
        $t.toggleClass('table-sm');
        $(this).attr('title', $t.hasClass('table-sm') ? 'Vista normal' : 'Vista compacta');
    }

    function toggleBusquedaTabla() {
        var $wr = $('#tabla-registros-wrapper').find('.dataTables_wrapper');
        if ($wr.length) $wr.find('.dataTables_filter').toggle();
    }

    function imprimirTabla() { window.print(); }

    function invalidateModalMapSize() {
        if (mapModalInstance && typeof mapModalInstance.invalidateSize === 'function') {
            mapModalInstance.invalidateSize({ animate: false });
        }
    }

    function initModalLeafletMap(lat, lon, rowId) {
        var el = document.getElementById('modal-detalle-mapa-canvas');
        if (!el || typeof L === 'undefined') return;
        if (mapModalInstance) {
            try { mapModalInstance.remove(); } catch (e) {}
            mapModalInstance = null;
            mapModalMarker = null;
        }
        el.innerHTML = '';
        mapModalInstance = L.map(el, {
            scrollWheelZoom: true,
            attributionControl: true,
            maxZoom: ESRI_WORLD_IMAGERY_TILE_OPTIONS.maxZoom
        }).setView([lat, lon], 16);
        L.tileLayer(ESRI_WORLD_IMAGERY_TILE_URL, ESRI_WORLD_IMAGERY_TILE_OPTIONS).addTo(mapModalInstance);
        var customIcon = createCustomMarker();
        var opts = customIcon && customIcon.options ? { icon: customIcon } : {};
        mapModalMarker = L.marker([lat, lon], opts).addTo(mapModalInstance);
        if (rowId != null) mapModalMarker.bindPopup('Registro #' + rowId);

        function fix() {
            if (!mapModalInstance) return;
            invalidateModalMapSize();
            mapModalInstance.setView([lat, lon], mapModalInstance.getZoom());
        }
        fix();
        if (typeof requestAnimationFrame === 'function') {
            requestAnimationFrame(function() { requestAnimationFrame(fix); });
        }
        setTimeout(fix, 120);
        setTimeout(fix, 350);
        setTimeout(fix, 600);
    }

    function openModalDetalle(row, baseCols, dynamicColsModal) {
        var base = row.base || {}, dynamic = row.dynamic || {}, mapData = row.map || {};
        var $modal = $('#modal-detalle-registro');

        var title = 'Detalle del registro';
        if (row.id != null) title += ' <span class="eval-modal-badge">#' + escapeHtml(String(row.id)) + '</span>';
        $('#modal-detalle-titulo').html(title);

        var subParts = [];
        if (base.fecha && base.fecha !== '—') subParts.push('<i class="fa fa-calendar-alt"></i> ' + escapeHtml(String(base.fecha)));
        if (base.cartilla && base.cartilla !== '—') subParts.push('<i class="fa fa-file-alt"></i> ' + escapeHtml(String(base.cartilla)));
        if (base.lote && base.lote !== '—') subParts.push('<i class="fa fa-draw-polygon"></i> Lote ' + escapeHtml(String(base.lote)));
        $('#modal-detalle-subtitle').html(subParts.join(' &nbsp;·&nbsp; '));

        $('#modal-detalle-base').html(buildModalFieldSection('Información general', 'fa-info-circle', baseCols || [], base));
        var htmlDyn = buildModalFieldSection('Campos de evaluación', 'fa-clipboard-list', dynamicColsModal || [], dynamic);
        $('#modal-detalle-dynamic').html(htmlDyn);

        var hasCoords = mapData.lat != null && mapData.lon != null;
        var lat = hasCoords ? parseFloat(mapData.lat) : NaN;
        var lon = hasCoords ? parseFloat(mapData.lon) : NaN;
        hasCoords = hasCoords && !isNaN(lat) && !isNaN(lon);

        $('#modal-detalle-mapa-sin-coords').toggle(!hasCoords);
        $('#modal-detalle-mapa-canvas').toggle(hasCoords);
        var $coordsLbl = $('#modal-detalle-coords-label');
        if (hasCoords) {
            $coordsLbl.text(lat.toFixed(6) + ', ' + lon.toFixed(6)).show();
        } else {
            $coordsLbl.hide().text('');
        }

        modalMapPending = null;
        if (modalShownMapHandler) {
            $modal.off('shown.bs.modal', modalShownMapHandler);
            modalShownMapHandler = null;
        }
        if (mapModalInstance) {
            try { mapModalInstance.remove(); } catch (e) {}
            mapModalInstance = null;
            mapModalMarker = null;
        }
        $('#modal-detalle-mapa-canvas').empty();

        if (hasCoords) {
            modalMapPending = { lat: lat, lon: lon, rowId: row.id };
            modalShownMapHandler = function() {
                $modal.off('shown.bs.modal', modalShownMapHandler);
                modalShownMapHandler = null;
                if (!modalMapPending) return;
                var p = modalMapPending;
                modalMapPending = null;
                initModalLeafletMap(p.lat, p.lon, p.rowId);
            };
            $modal.on('shown.bs.modal', modalShownMapHandler);
            setTimeout(function() {
                if (modalShownMapHandler && modalMapPending) modalShownMapHandler();
            }, 380);
        }

        $modal.modal('show');
    }

    function bindRowClicks() {
        $('#tabla-evaluaciones-body').off('click', 'tr.evaluaciones-row-clickable').on('click', 'tr.evaluaciones-row-clickable', function() {
            var $tr = $(this), rows = $('#tabla-evaluaciones-body').data('evaluaciones-rows');
            var baseCols = $('#tabla-evaluaciones-body').data('evaluaciones-base-cols');
            var dynamicColsModal = $('#tabla-evaluaciones-body').data('evaluaciones-dynamic-cols-modal');
            if (!rows) return;
            var row = rows.find(function(r) { return String(r.id) === String($tr.data('row-id')); }) || rows[$tr.data('row-index')];
            if (row) openModalDetalle(row, baseCols, dynamicColsModal);
        });
    }

    function cleanupModalMap() {
        $('#modal-detalle-registro').on('hidden.bs.modal', function() {
            modalMapPending = null;
            var $m = $(this);
            if (modalShownMapHandler) {
                $m.off('shown.bs.modal', modalShownMapHandler);
                modalShownMapHandler = null;
            }
            if (mapModalInstance) {
                try { mapModalInstance.remove(); } catch (e) {}
                mapModalInstance = null;
                mapModalMarker = null;
            }
        });
    }

    function parseGeometry(geo) {
        if (!geo || typeof geo !== 'string') return null;
        var s = geo.trim();
        if (!s) return null;
        try {
            var parsed = JSON.parse(s);
            if (parsed && (parsed.type === 'Feature' || parsed.type === 'FeatureCollection' || parsed.type === 'Polygon' || parsed.type === 'MultiPolygon')) {
                if (parsed.type === 'Feature') return parsed;
                if (parsed.type === 'FeatureCollection') return parsed;
                return { type: 'Feature', geometry: parsed, properties: {} };
            }
            if (parsed && parsed.geometry) return parsed;
            return { type: 'Feature', geometry: parsed, properties: {} };
        } catch (e) {}
        if (s.toUpperCase().indexOf('POLYGON') === 0 || s.toUpperCase().indexOf('MULTIPOLYGON') === 0) {
            var coordRegex = /(-?\d+\.?\d*)\s+(-?\d+\.?\d*)/g;
            var polygons = [];
            var startParen = s.indexOf('((') >= 0 ? s.indexOf('((') : s.indexOf('(');
            var rest = s.substring(startParen);
            for (var i = 0, depth = 0, segStart = 0; i < rest.length; i++) {
                if (rest[i] === '(') { if (depth === 1) segStart = i + 1; depth++; }
                else if (rest[i] === ')') {
                    depth--;
                    if (depth === 1) {
                        var seg = rest.substring(segStart, i), coords = [], m;
                        coordRegex.lastIndex = 0;
                        while ((m = coordRegex.exec(seg)) !== null) coords.push([parseFloat(m[1]), parseFloat(m[2])]);
                        if (coords.length >= 3) polygons.push([coords]);
                    }
                }
            }
            if (polygons.length === 0) return null;
            var geom = polygons.length === 1 ? { type: 'Polygon', coordinates: polygons[0] } : { type: 'MultiPolygon', coordinates: polygons };
            return { type: 'Feature', geometry: geom, properties: {} };
        }
        return null;
    }

    function ringCoordsToLatLngs(ring) {
        return ring.map(function(c) { return [c[1], c[0]]; });
    }

    function forEachPolygonLatLngRings(geojson, cb) {
        if (!geojson || typeof cb !== 'function') return;
        function handleGeom(geom) {
            if (!geom || !geom.type) return;
            if (geom.type === 'Polygon' && geom.coordinates) {
                cb(geom.coordinates.map(ringCoordsToLatLngs));
            } else if (geom.type === 'MultiPolygon' && geom.coordinates) {
                geom.coordinates.forEach(function(poly) {
                    cb(poly.map(ringCoordsToLatLngs));
                });
            }
        }
        if (geojson.type === 'Feature') {
            handleGeom(geojson.geometry);
        } else if (geojson.type === 'FeatureCollection' && geojson.features) {
            geojson.features.forEach(function(f) { handleGeom(f.geometry); });
        } else if (geojson.type === 'Polygon' || geojson.type === 'MultiPolygon') {
            handleGeom(geojson);
        } else if (geojson.geometry) {
            handleGeom(geojson.geometry);
        }
    }

    function exteriorRingCentroidLatLng(latLngRings) {
        if (!latLngRings || !latLngRings.length) return null;
        var ring = latLngRings[0];
        var n = ring.length;
        if (n > 1 && ring[0][0] === ring[n - 1][0] && ring[0][1] === ring[n - 1][1]) n -= 1;
        if (n < 1) return null;
        var latSum = 0, lngSum = 0;
        for (var i = 0; i < n; i++) {
            latSum += ring[i][0];
            lngSum += ring[i][1];
        }
        return L.latLng(latSum / n, lngSum / n);
    }

    function computeFirstPartCentroid(geojson) {
        var center = null;
        var first = true;
        forEachPolygonLatLngRings(geojson, function(latLngRings) {
            if (first) {
                center = exteriorRingCentroidLatLng(latLngRings);
                first = false;
            }
        });
        return center;
    }

    function buildRegistrosCountByLoteId(rows) {
        var c = {};
        (rows || []).forEach(function(r) {
            var bid = r.base && r.base.loteId != null && r.base.loteId !== '' ? String(r.base.loteId) : null;
            if (bid) c[bid] = (c[bid] || 0) + 1;
        });
        return c;
    }

    function createLoteLabelIcon(labelText) {
        return L.divIcon({
            className: 'evaluaciones-lote-label-marker',
            html: '<div class="evaluaciones-lote-label-inner"><span class="evaluaciones-lote-label-text">' +
                escapeHtml(labelText) + '</span></div>',
            iconSize: [1, 1],
            iconAnchor: [0, 0]
        });
    }

    var MAP_LOTE_ZOOM_FILL_AND_LABELS = 15;
    /** Lotes sin registros (filtro actual): relleno y borde únicos para todos */
    var MAP_LOTE_FILL_IDLE = '#e8f0ea';
    /** Lotes con al menos un registro en la tabla filtrada: relleno azul claro para contrastar con vacíos */
    var MAP_LOTE_FILL_ACTIVE = '#bbdefb';
    var MAP_LOTE_FILL_OPACITY_FAR = 0.32;
    var MAP_LOTE_FILL_OPACITY_NEAR = 0.58;
    /**
     * Contorno tipo “cinta”: halo claro (volumen del borde) + filete oscuro interior.
     * No es un solo trazo; se dibujan dos contornos por polígono, redondeando vértices.
     */
    var MAP_LOTE_RIM_COLOR = '#ffffff';
    var MAP_LOTE_RIM_OPACITY = 0.91;
    var MAP_LOTE_RIM_WEIGHT_IDLE = 5;
    /** Halo más ancho en lotes con datos */
    var MAP_LOTE_RIM_WEIGHT_ACTIVE = 8;
    /** Halo ligeramente azulado para armonizar con el fill sin perder separación del mapa */
    var MAP_LOTE_RIM_COLOR_ACTIVE = '#e3f2fd';
    var MAP_LOTE_RIM_OPACITY_ACTIVE = 0.95;
    var MAP_LOTE_EDGE_COLOR_IDLE = '#141414';
    /** Azul intenso: contraste claro sobre relleno #bbdefb */
    var MAP_LOTE_EDGE_COLOR_ACTIVE = '#0d47a1';
    var MAP_LOTE_EDGE_WEIGHT_IDLE = 1.5;
    var MAP_LOTE_EDGE_WEIGHT_ACTIVE = 3.25;

    function syncLoteLabelsVisibility() {
        if (!mapInstance || !lotesLabelsLayerGroup) return;
        var z = mapInstance.getZoom();
        if (z >= MAP_LOTE_ZOOM_FILL_AND_LABELS) {
            if (!mapInstance.hasLayer(lotesLabelsLayerGroup)) lotesLabelsLayerGroup.addTo(mapInstance);
        } else if (mapInstance.hasLayer(lotesLabelsLayerGroup)) {
            mapInstance.removeLayer(lotesLabelsLayerGroup);
        }
    }

    /**
     * Mismos colores base para todos los lotes vacíos; activos si hay registros (filtro).
     * Zoom alejado: fillOpacity menor; cercano: más intenso.
     */
    function syncLotePolygonStyles() {
        if (!mapInstance || !lotesLayerGroup) return;
        var z = mapInstance.getZoom();
        var close = z >= MAP_LOTE_ZOOM_FILL_AND_LABELS;
        var fillOp = close ? MAP_LOTE_FILL_OPACITY_NEAR : MAP_LOTE_FILL_OPACITY_FAR;
        lotesLayerGroup.eachLayer(function(layer) {
            var active = layer._evalLoteHasRegistros === true;
            if (layer._evalLoteOutlineRim) {
                layer.setStyle({
                    color: active ? MAP_LOTE_RIM_COLOR_ACTIVE : MAP_LOTE_RIM_COLOR,
                    weight: active ? MAP_LOTE_RIM_WEIGHT_ACTIVE : MAP_LOTE_RIM_WEIGHT_IDLE,
                    opacity: active ? MAP_LOTE_RIM_OPACITY_ACTIVE : MAP_LOTE_RIM_OPACITY,
                    fillOpacity: 0,
                    lineJoin: 'round',
                    lineCap: 'round'
                });
                return;
            }
            if (layer._evalLoteOutlineEdge) {
                layer.setStyle({
                    color: active ? MAP_LOTE_EDGE_COLOR_ACTIVE : MAP_LOTE_EDGE_COLOR_IDLE,
                    weight: active ? MAP_LOTE_EDGE_WEIGHT_ACTIVE : MAP_LOTE_EDGE_WEIGHT_IDLE,
                    opacity: 1,
                    fillOpacity: 0,
                    lineJoin: 'round',
                    lineCap: 'round'
                });
                return;
            }
            if (layer._evalLoteShape) {
                layer.setStyle({
                    stroke: false,
                    fillColor: active ? MAP_LOTE_FILL_ACTIVE : MAP_LOTE_FILL_IDLE,
                    fillOpacity: fillOp
                });
            }
        });
    }

    function syncLoteMapOverlays() {
        syncLotePolygonStyles();
        syncLoteLabelsVisibility();
    }

    function addLotePolygonLayers(featureGroup, labelsGroup, geojson, popupHtml, labelCenter, labelText, hasRegistros) {
        var fillLayersForPopup = [];
        var active = !!hasRegistros;
        forEachPolygonLatLngRings(geojson, function(latLngRings) {
            var outlineOpts = { fillOpacity: 0, interactive: false, lineJoin: 'round', lineCap: 'round' };
            var rim = L.polygon(latLngRings, Object.assign({}, outlineOpts, {
                color: active ? MAP_LOTE_RIM_COLOR_ACTIVE : MAP_LOTE_RIM_COLOR,
                weight: active ? MAP_LOTE_RIM_WEIGHT_ACTIVE : MAP_LOTE_RIM_WEIGHT_IDLE,
                opacity: active ? MAP_LOTE_RIM_OPACITY_ACTIVE : MAP_LOTE_RIM_OPACITY
            }));
            rim._evalLoteOutlineRim = true;
            rim._evalLoteHasRegistros = active;
            rim.addTo(featureGroup);

            var edge = L.polygon(latLngRings, Object.assign({}, outlineOpts, {
                color: active ? MAP_LOTE_EDGE_COLOR_ACTIVE : MAP_LOTE_EDGE_COLOR_IDLE,
                weight: active ? MAP_LOTE_EDGE_WEIGHT_ACTIVE : MAP_LOTE_EDGE_WEIGHT_IDLE,
                opacity: 1
            }));
            edge._evalLoteOutlineEdge = true;
            edge._evalLoteHasRegistros = active;
            edge.addTo(featureGroup);

            var poly = L.polygon(latLngRings, {
                stroke: false,
                fillColor: active ? MAP_LOTE_FILL_ACTIVE : MAP_LOTE_FILL_IDLE,
                fillOpacity: MAP_LOTE_FILL_OPACITY_FAR
            });
            poly._evalLoteShape = true;
            poly._evalLoteHasRegistros = active;
            poly.addTo(featureGroup);
            fillLayersForPopup.push(poly);
        });
        fillLayersForPopup.forEach(function(layer) {
            layer.bindPopup(popupHtml);
        });
        if (labelsGroup && labelCenter && labelText) {
            L.marker(labelCenter, { icon: createLoteLabelIcon(labelText), interactive: false }).addTo(labelsGroup);
        }
    }

    function createCustomMarker() {
        return typeof L !== 'undefined' ? L.divIcon({
            className: 'evaluaciones-marker-custom',
            html: '<div class="evaluaciones-marker-pin"></div>',
            iconSize: [24, 24],
            iconAnchor: [12, 24],
        }) : null;
    }

    function fitMapToData(map, lotesGroup, markers) {
        if (!map) return;
        var bounds = [];
        if (lotesGroup && lotesGroup.getBounds && lotesGroup.getBounds().isValid()) bounds.push(lotesGroup.getBounds());
        (markers || []).forEach(function(m) {
            var ll = m.getLatLng ? m.getLatLng() : (m._latlng || null);
            if (ll) bounds.push(L.latLngBounds([ll, ll]));
        });
        if (bounds.length === 0) return;
        if (bounds.length === 1 && markers && markers.length === 1 && !lotesGroup) {
            var ll = markers[0].getLatLng ? markers[0].getLatLng() : markers[0]._latlng;
            if (ll) map.setView([ll.lat, ll.lng], 15);
            return;
        }
        var combined = bounds[0];
        for (var i = 1; i < bounds.length; i++) if (bounds[i]) combined = combined.extend(bounds[i]);
        map.fitBounds(combined, { padding: [24, 24], maxZoom: 16 });
    }

    function renderMap(mapPoints, data) {
        data = data || {};
        var $container = $('#evaluaciones-map'), $placeholder = $('#evaluaciones-map-placeholder'), $canvas = $('#evaluaciones-map-canvas');
        mapPoints = mapPoints || [];
        var validPoints = mapPoints.filter(function(p) { return p.lat != null && p.lon != null; });
        var mapLotes = Array.isArray(data.map_lotes) ? data.map_lotes : [];
        if (!mapLotes.length && data.lote_geo && typeof data.lote_geo === 'string' && data.lote_geo.trim()) {
            mapLotes = [{ idLote: '__legacy__', codigo: data.lote_codigo || '—', geo: data.lote_geo }];
        }
        var registrosByLote = buildRegistrosCountByLoteId(data.rows);
        var hasLotes = mapLotes.length > 0;
        var hasData = validPoints.length > 0 || hasLotes;

        if (mapInstance) {
            if (lotesMapZoomHandler) {
                try { mapInstance.off('zoomend', lotesMapZoomHandler); } catch (e) {}
                lotesMapZoomHandler = null;
            }
            mapMarkers.forEach(function(m) { try { mapInstance.removeLayer(m); } catch (e) {} });
            mapMarkers = [];
            if (lotesLayerGroup) { try { mapInstance.removeLayer(lotesLayerGroup); } catch (e) {} lotesLayerGroup = null; }
            if (lotesLabelsLayerGroup) { try { mapInstance.removeLayer(lotesLabelsLayerGroup); } catch (e) {} }
            lotesLabelsLayerGroup = null;
            mapInstance.remove();
            mapInstance = null;
        }
        if (!hasData) {
            $container.addClass('evaluaciones-map-empty');
            $placeholder.show();
            $canvas.hide().empty();
            return;
        }
        $container.removeClass('evaluaciones-map-empty');
        $placeholder.hide();
        $canvas.show().empty();
        if (typeof L === 'undefined') { $placeholder.show().find('p').first().text('Leaflet no cargado'); return; }

        var centerLat = -13.97, centerLon = -75.73;
        if (validPoints.length > 0) {
            var latSum = 0, lonSum = 0;
            validPoints.forEach(function(p) { latSum += parseFloat(p.lat); lonSum += parseFloat(p.lon); });
            centerLat = latSum / validPoints.length;
            centerLon = lonSum / validPoints.length;
        }
        mapInstance = L.map('evaluaciones-map-canvas', {
            maxZoom: ESRI_WORLD_IMAGERY_TILE_OPTIONS.maxZoom
        }).setView([centerLat, centerLon], 14);
        L.tileLayer(ESRI_WORLD_IMAGERY_TILE_URL, ESRI_WORLD_IMAGERY_TILE_OPTIONS).addTo(mapInstance);
        var customIcon = createCustomMarker();
        if (hasLotes && typeof L !== 'undefined') {
            lotesLayerGroup = L.featureGroup();
            lotesLabelsLayerGroup = L.layerGroup();
            mapLotes.forEach(function(lote) {
                var geojson = parseGeometry(lote.geo);
                if (!geojson) return;
                var lid = String(lote.idLote != null ? lote.idLote : '');
                var codigo = lote.codigo || '—';
                var n = lid && lid !== '__legacy__' ? (registrosByLote[lid] || 0) : 0;
                var labelText = String(codigo) + (n > 0 ? ' (' + n + ')' : '');
                var popup = '<strong>Lote:</strong> ' + escapeHtml(String(codigo));
                var labelCenter = computeFirstPartCentroid(geojson);
                try {
                    addLotePolygonLayers(
                        lotesLayerGroup, lotesLabelsLayerGroup, geojson, popup, labelCenter, labelText,
                        n > 0
                    );
                } catch (err) {}
            });
            if (lotesLayerGroup.getLayers().length) {
                lotesLayerGroup.addTo(mapInstance);
                lotesMapZoomHandler = syncLoteMapOverlays;
                mapInstance.on('zoomend', lotesMapZoomHandler);
                syncLoteMapOverlays();
            } else {
                lotesLayerGroup = null;
                lotesLabelsLayerGroup = null;
            }
        }
        validPoints.forEach(function(p) {
            var opts = customIcon && customIcon.options ? { icon: customIcon } : {};
            var m = L.marker([parseFloat(p.lat), parseFloat(p.lon)], opts).addTo(mapInstance);
            var rid = p.RegistroId != null ? p.RegistroId : null;
            if (rid != null) {
                m.on('click', function() {
                    var rows = $('#tabla-evaluaciones-body').data('evaluaciones-rows');
                    var baseCols = $('#tabla-evaluaciones-body').data('evaluaciones-base-cols');
                    var dynamicColsModal = $('#tabla-evaluaciones-body').data('evaluaciones-dynamic-cols-modal');
                    if (!rows || !rows.length) return;
                    var row = rows.find(function(r) { return String(r.id) === String(rid); });
                    if (row) openModalDetalle(row, baseCols, dynamicColsModal);
                });
            }
            mapMarkers.push(m);
        });
        setTimeout(function() {
            if (mapInstance) {
                mapInstance.invalidateSize();
                fitMapToData(mapInstance, lotesLayerGroup, mapMarkers);
                syncLoteMapOverlays();
            }
        }, 150);
    }

    function applyResponse(data, updateCombos) {
        var rows = Array.isArray(data && data.rows) ? data.rows : [];
        var kpis = data && data.kpis ? data.kpis : { acumulado: 0, promedio: 0, maximo: 0, minimo: 0, muestras: 0 };
        var mapPoints = Array.isArray(data && data.map_points) ? data.map_points : [];

        if (updateCombos !== false) {
            $('#filtro-cartilla').off('change', onChangePlantilla);
            $('#filtro-lote').off('change', onChangeLote);
            $('#filtro-evaluador').off('change', onChangeEvaluador);
            fillPlantillas(data && data.plantillas ? data.plantillas : []);
            fillLotes(data && data.lotes ? data.lotes : []);
            fillEvaluadores(data && data.evaluadores ? data.evaluadores : []);
            $('#filtro-cartilla').on('change', onChangePlantilla);
            $('#filtro-lote').on('change', onChangeLote);
            $('#filtro-evaluador').on('change', onChangeEvaluador);
        }
        renderKPIs(kpis);
        renderTable({
            base_columns: (data && data.base_columns) || [],
            dynamic_columns: (data && data.dynamic_columns) || [],
            rows: rows,
            dynamic_columns_modal: (data && data.dynamic_columns_modal) || (data && data.dynamic_columns) || []
        });
        renderMap(mapPoints, data || {});
        bindRowClicks();
        lastFechaVal = $('#filtro-fecha').val();
    }

    function loadInit() {
        if (loading || !currentIdArea) return;
        loading = true;
        $('#kpis-evaluaciones').addClass('opacity-50');
        var $tbody = $('#tabla-evaluaciones-body');
        $tbody.html('<tr><td colspan="6" class="text-center"><i class="fa fa-spinner fa-spin"></i> Cargando...</td></tr>');

        $.ajax({
            url: API_INIT,
            data: { areaId: currentIdArea },
            type: 'GET',
            dataType: 'json'
        }).done(function(data) {
            if (data.fecha) $('#filtro-fecha').val(fechaToDMY(data.fecha));
            if (!data.plantillas || data.plantillas.length === 0) {
                $tbody.html('<tr><td colspan="6" class="text-center text-muted">Esta área no tiene cartillas configuradas</td></tr>');
                fillPlantillas([]);
                fillLotes([]);
                fillEvaluadores([]);
                renderKPIs({ acumulado: 0, promedio: 0, maximo: 0, minimo: 0, muestras: 0 });
                renderMap([], {});
            } else {
                applyResponse(data);
            }
        }).fail(function(xhr) {
            var msg = (xhr.responseJSON && xhr.responseJSON.error) ? xhr.responseJSON.error : 'Error al cargar';
            $tbody.html('<tr><td colspan="6" class="text-center text-danger">' + msg + '</td></tr>');
            renderKPIs({ acumulado: 0, promedio: 0, maximo: 0, minimo: 0, muestras: 0 });
            renderMap([], {});
        }).always(function() {
            loading = false;
            $('#kpis-evaluaciones').removeClass('opacity-50');
        });
    }

    function loadFiltros(updateCombos) {
        if (!currentIdArea) return;
        var s = getState();
        if (!s.fecha) return;

        if (pendingFiltrosXhr && typeof pendingFiltrosXhr.abort === 'function') {
            pendingFiltrosXhr.abort();
            pendingFiltrosXhr = null;
        }

        var reqId = ++lastFiltrosRequestId;
        loading = true;
        $('#kpis-evaluaciones').addClass('opacity-50');
        var $tbody = $('#tabla-evaluaciones-body');
        var totalCols = 8;
        $tbody.html('<tr><td colspan="' + totalCols + '" class="text-center"><i class="fa fa-spinner fa-spin"></i> Cargando...</td></tr>');

        pendingFiltrosXhr = $.ajax({
            url: API_FILTROS,
            type: 'POST',
            contentType: 'application/json',
            headers: { 'X-CSRFToken': getCsrfToken() },
            data: JSON.stringify({
                areaId: s.areaId,
                fecha: s.fecha,
                plantillaId: s.plantillaId || null,
                loteId: s.loteId || null,
                evaluadorId: s.evaluadorId || null
            }),
            dataType: 'json'
        }).done(function(data) {
            if (reqId !== lastFiltrosRequestId) return;
            applyResponse(data, updateCombos);
        }).fail(function(xhr) {
            if (reqId !== lastFiltrosRequestId) return;
            if (xhr.statusText !== 'abort') {
                var msg = (xhr.responseJSON && xhr.responseJSON.error) ? xhr.responseJSON.error : 'Error al filtrar';
                $tbody.html('<tr><td colspan="' + totalCols + '" class="text-center text-danger">' + msg + '</td></tr>');
                renderKPIs({ acumulado: 0, promedio: 0, maximo: 0, minimo: 0, muestras: 0 });
                renderMap([], {});
            }
        }).always(function() {
            if (reqId === lastFiltrosRequestId) {
                loading = false;
                pendingFiltrosXhr = null;
                $('#kpis-evaluaciones').removeClass('opacity-50');
            }
        });
    }

    function onChangeFecha() {
        var v = $('#filtro-fecha').val();
        if (v === lastFechaVal) return;
        lastFechaVal = v;
        loadFiltros(true);
    }
    function onChangePlantilla() { loadFiltros(true); }
    function onChangeLote() { loadFiltros(true); }
    function onChangeEvaluador() { loadFiltros(true); }

    function init() {
        currentIdArea = obtenerIdAreaDesdeRuta();
        if (currentIdArea == null) {
            $('#filtro-cartilla').html('<option value="">Área no válida</option>');
            $('#kpis-evaluaciones').addClass('opacity-50');
            return;
        }

        $('#filtro-fecha').datepicker({
            format: 'dd/mm/yyyy',
            autoclose: true,
            todayHighlight: true
        });

        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0');
        var yyyy = today.getFullYear();
        var todayStr = dd + '/' + mm + '/' + yyyy;
        $('#filtro-fecha').val(todayStr);
        lastFechaVal = todayStr;

        $('#filtro-cartilla').on('change', onChangePlantilla);
        $('#filtro-fecha').on('change changeDate', onChangeFecha);
        $('#filtro-lote').on('change', onChangeLote);
        $('#filtro-evaluador').on('change', onChangeEvaluador);

        $(window).on('resize.evaluaciones', function() {
            if (mapInstance) mapInstance.invalidateSize();
        });

        $('#btn-export-mock').on('click', exportarCSV);
        $('#btn-vista-tabla-mock').on('click', toggleDensidadTabla);
        $('#btn-filtro-mock').on('click', toggleBusquedaTabla);
        $('#btn-export-csv-menu').on('click', function(e) { e.preventDefault(); exportarCSV(); });
        $('#btn-imprimir-menu').on('click', function(e) { e.preventDefault(); imprimirTabla(); });
        $('#btn-capa-mock, #btn-calor-mock, #btn-areas-mock').on('click', function() { console.log('[Evaluaciones]', this.id); });

        cleanupModalMap();
        loadInit();
    }

    $(document).ready(init);

})();
