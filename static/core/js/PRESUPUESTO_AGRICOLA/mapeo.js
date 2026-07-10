// ======= Helpers =======
const COLORS = ["bg-green", "bg-blue", "bg-purple", "bg-orange", "bg-black", "bg-warning"];
const $cards = $("#mapeo-cards");
const $search = $("#mapeo-search");
const $reload = $("#mapeo-reload");
const $modal = $("#mapeoLotesModal");
const $modalTitle = $("#mapeoLotesModalLabel");
const $modalReload = $("#mapeo-modal-reload");
const $table = $("#mapeoLotesTable");
const userId = window.USER_ID;

const skeleton = (n = 6) =>
    Array.from({length: n})
        .map(
            () => `
        <div class="col-md-4 col-sm-6 mb-3">
            <div class="widget widget-stats ${COLORS[Math.floor(Math.random() * COLORS.length)]}">
            <div class="stats-icon"><i class="fa fa-map"></i></div>
            <div class="stats-info">
                <div class="stats-title">
                <span class="placeholder-glow"><span class="placeholder col-7"></span></span>
                </div>
                <div class="stats-number">
                <span class="placeholder-glow"><span class="placeholder col-5"></span></span>
                </div>
            </div>
            <div class="stats-link">
                <span class="placeholder-glow"><span class="placeholder col-3"></span></span>
            </div>
            </div>
        </div>`
        )
        .join("");

const getArray = (res) => {
    if (Array.isArray(res)) return res;
    if (Array.isArray(res?.items)) return res.items;
    if (Array.isArray(res?.results)) return res.results;
    if (Array.isArray(res?.data)) return res.data;
    return [];
};
const EMPRESAS = {
    1: "SOCIEDAD AGRICOLA DON LUIS S.A",
    2: "INVERSIONES AJS S.A.C",
    3: "AGROINDUSTRIA CAMPOVERDE S.A.C"
};
const VARIEDADES = {
    1: "SWEET GLOBE",
    2: "AUTUMN CRISP",
    3: "MOSCATEL",
    4: "SUGRA 56"
};
const escapeHTML = (s) =>
    String(s ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
document.addEventListener("DOMContentLoaded", function () {
    const selectCampania = document.getElementById("select-campania");

    selectCampania.addEventListener("change", function () {
        loadFundos();
    });
});
// ======= Estado =======
let currentFundo = {id: null, nombre: ""};
let lotesDT = null;
let debounceTimer = null;
let tablaMapeo = null;

const formatNumber = (n, d = 0) =>
    Number(n || 0).toLocaleString("es-PE", {
        minimumFractionDigits: d,
        maximumFractionDigits: d,
    });

$(document).ready(function () {
    $('#recargarTablaMapeo').on('click', function () {
        console.log('Recargando tabla mapeo');
        if (tablaMapeo) {
            tablaMapeo.ajax.reload();
        } else {
            cargarTablaMapeo();
        }
    });
    // Carga inicial de fundos
    loadFundos();
});


// ======= Fundos (cards) =======
function loadFundos(q = "", done) {
    $cards.html(skeleton());
    $cards.html(skeleton());
    const campaniaSelect = document.getElementById("select-campania").value;
    $.ajax({
        url: "/presupuesto-agricola/mapeo/api/fundos_por_usuario/?campania=" + campaniaSelect,
        type: "GET",
        success: function (resp) {
            const fundos = getArray(resp);
            if (!fundos.length) {
                $cards.html(`
                        <div class="col-12">
                        <div class="alert alert-warning mb-0">
                            No se encontraron fundos asignados ${q ? `para "<strong>${escapeHTML(q)}</strong>"` : ""}.
                        </div>
                        </div>`);
                return;
            }
            const fundosFiltrados = fundos.filter(f => (f.TOTAL_LOTES || 0) > 0);

            const html = fundosFiltrados.length
                ? fundosFiltrados.map((f, idx) => {
                    const color = COLORS[idx % COLORS.length];
                    return `
                        <div class="col-md-4 col-sm-6 mb-3">
                            <div class="widget widget-stats ${color} mapeo-card" data-id="${escapeHTML(f.ID_FUNDO)}" data-nombre="${escapeHTML(f.DESCRIPCION)}">
                            <div class="stats-icon"><i class="fa fa-map"></i></div>
                            <div class="stats-info">
                                <div class="stats-title">${escapeHTML(f.ID_FUNDO)}</div>
                                <div class="stats-number">${escapeHTML(f.DESCRIPCION || "—")}</div>
                                <div class="stats-desc">EMPRESA: ${escapeHTML(EMPRESAS[f.ID_EMPRESA] || f.ID_EMPRESA || "-")}</div>
                                <div class="stats-desc">TOTAL LOTES: ${escapeHTML(f.TOTAL_LOTES ?? 0)}</div>
                            </div>
                            <div class="stats-link">
  ${f.TOTAL_LOTES > 0
                        ? `<a href="#" class="text-white abrir-lotes" data-id="${escapeHTML(f.ID_FUNDO)}" data-nombre="${escapeHTML(f.DESCRIPCION)}">
         Ver lotes <i class="fa fa-arrow-alt-circle-right"></i>
       </a>`
                        : `<a href="#" class="disabled-link">
         Sin lotes
       </a>`}
</div>
                       
                            </div>
                        </div>`;
                })
                    .join("")
                : `<div class="col-12 text-center text-muted mt-4">
                            <i class="fa fa-info-circle"></i> No hay lotes asignados en ningún fundo
                       </div>`;
            $cards.html(html);
            $cards.off("click.mapeo").on("click.mapeo", ".mapeo-card, .abrir-lotes", function (e) {
                e.preventDefault();
                let id = $(this).data("id");
                let nombre = $(this).data("nombre");
                let campania = $(this).data("campania");
                if (!id) id = $(this).closest(".mapeo-card").data("id");
                if (!nombre) nombre = $(this).closest(".mapeo-card").data("nombre");
                if (!campania) campania = $(this).closest(".mapeo-card").data("campania");
                openLotesModal(id, nombre, campania);
            });
        },
        error: function (xhr) {
            console.error("Error al cargar fundos:", xhr);
            $cards.html(`
                <div class="col-12">
                    <div class="alert alert-danger mb-0">
                    Ocurrió un error al cargar los fundos. Intente nuevamente.
                    </div>
                </div>`);
        },
        complete: function () {
            if (typeof done === "function") done();
        },
    });

    $("#btnGuardarMapeo").off("click.mapeo").on("click.mapeo", function () {
        const plantas = {};

        $("#tablaTipoPlantaMapeo input[type='number']").each(function () {
            const key = $(this).attr("name"); // ejemplo: "productiva"
            const val = parseInt($(this).val()) || 0;
            plantas[key] = val;
        });

        // Obtener valores de los campos simples
        const hileraValor = parseFloat($('#inputHilera').val()) || 0;
        const plantaValor = parseFloat($('#inputPlanta').val()) || 0;
        const densidadCalculada = parseFloat($('#inputDensidad').val()) || 0;

        const data = {
            lote: {
                id_lote: $("#MAPEO_ID_LOTE").val(),
                area_lote: $("#AREA_LOTE").val(),
            },
            mapeo: {
                id_asignacion: $("#ID_ASIGNACION").val(),
                fecha: $("#fechaMapeo").val(),
                hilera: hileraValor,
                planta: plantaValor,
                densidad: densidadCalculada,
                plantas: plantas
            },
            prod_uva: {
                rendimiento: $("#rendimiento").val(),
                rac_planta: $("#racimosPlanta").val(),
                rac_packing: $("#racimoPacking").val(),
                rac_nacional: $("#racimoNacional").val(),
                peso_rac: $("#pesoRacimo").val(),
                caj_lote: $("#cajasLote").val()
            }
        };
        console.log("[GUARDAR MAPEO]:", data);
        // Enviar al backend (POST para crear/actualizar, DELETE para eliminar)
        $.ajax({
            url: "/produccionuva1/api/mapeo_nuevo/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (resp) {
                Swal.fire({icon: 'success', title: 'Guardado', text: 'Mapeo guardado correctamente.'});
                limpiarModalMapeo();
                $("#modalMapeoCRUD").modal("hide");
            },
            error: function (xhr) {
                Swal.fire({icon: 'error', title: 'Error', text: 'No se pudo guardar el mapeo.'});
            }
        });
    });
}

function openLotesModal(fundoId, nombre, campania) {
    console.log("[MAPEO] openLotesModal fundoId:", fundoId, "nombre:", nombre);
    currentFundo = {id: fundoId, nombre};
    $modalTitle.text(`Lotes del fundo: ${nombre}`);
    $modal.modal("show");
    loadLotesCampania(fundoId, campania);
}

function loadLotesCampania(fundoId, done) {
    if (lotesDT) {
        lotesDT.destroy();
        lotesDT = null;
    }
    let campania = document.getElementById("select-campania").value;
    console.log("[MAPEO] Campaña:", campania);
    $table.find("tbody").html(`
            <tr><td colspan="4" class="text-center">
                <span class="spinner-border spinner-border-sm"></span> Cargando lotes...</td></tr>`);

    console.log("[MAPEO] loadLotes llamado", {fundoId, currentFundo, table: $table});

    const userId = window.USER_ID;
    console.log("[MAPEO] USER_ID:", userId);
    if (!userId) {
        $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-danger">No se pudo determinar el usuario actual.</td></tr>`);
        if (typeof done === "function") done();
        return;
    }

    $.ajax({
        url: "/presupuesto-agricola/asignacion/api/asignacion_lote/",
        type: "GET",
        success: function (resp) {
            console.log("[MAPEO] asignacion_lote resp:", resp);
            const asignaciones = getArray(resp).filter(a => String(a.ID_CAMPANIA) === String(campania));
            console.log("[MAPEO] asignaciones filtradas:", asignaciones);
            const lotesAsignados = asignaciones.map(a => a.ID_LOTE);
            console.log("[MAPEO] lotesAsignados:", lotesAsignados);
            if (!lotesAsignados.length) {
                $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-muted">No tienes lotes asignados en este fundo.</td></tr>`);
                if (typeof done === "function") done();
                return;
            }
            $.ajax({
                url: "/presupuesto-agricola/lotes/api/lotes/",
                type: "GET",
                success: function (resp2) {
                    console.log("[MAPEO] lotes resp:", resp2);
                    let lotes = getArray(resp2);
                    lotes = lotes.filter(l => (String(l.ID_FUNDO) === String(fundoId)) && lotesAsignados.includes(l.ID_LOTE || l.id_lote || l.id));
                    console.log("[MAPEO] lotes filtrados:", lotes);
                    if (!lotes.length) {
                        $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-muted">No tienes lotes asignados en este fundo.</td></tr>`);
                        if (typeof done === "function") done();
                        return;
                    }

                    /*const rows = lotes
                        .map(
                            (l, idx) => `
                                <tr class="lote-row" data-id="${escapeHTML(l.ID_LOTE)}" data-nombre="${escapeHTML(l.DESCRIPCION)}" data-area="${escapeHTML(l.AREA_TOTAL)}">
                                    <td>${escapeHTML(l.DESCRIPCION)}</td>
                                    <td class="text-right">${formatNumber(l.AREA_TOTAL, 2)}</td>
                                    <td>${escapeHTML(VARIEDADES[String(l.ID_VARIEDAD)] || "—")}</td>
                                    <td>${escapeHTML(l.CECO || "—")}</td>
                                </tr>`
                        )
                        .join("");*/
                    const rows = lotes.map(l => {
                        // Buscar la asignación correspondiente a este lote
                        const asignacion = asignaciones.find(a => String(a.ID_LOTE) === String(l.ID_LOTE));

                        return `
                                <tr class="lote-row"
                                    data-id="${escapeHTML(l.ID_LOTE)}"
                                    data-nombre="${escapeHTML(l.DESCRIPCION)}"
                                    data-area="${escapeHTML(l.AREA_TOTAL)}"
                                    data-asignacion="${escapeHTML(asignacion ? asignacion.ID_ASIGNACION : '')}">
                                    <td>${escapeHTML(l.DESCRIPCION)}</td>
                                    <td class="text-right">${formatNumber(l.AREA_TOTAL, 2)}</td>
                                    <td>${escapeHTML(VARIEDADES[String(l.ID_VARIEDAD)] || "—")}</td>
                                    <td>${escapeHTML(l.CECO || "—")}</td>
                                </tr>`;
                    }).join("");
                    $table.find("tbody").html(rows);
                    lotesDT = $table.DataTable({
                        dom: "Bfrtip",
                        buttons: [
                            {
                                text: '<i class="fas fa-sync-alt"></i>',
                                className: "btn-sm btn-secondary",
                                action: function (e, dt, node) {
                                    $(node).find("i").addClass("fa-spin");
                                    loadLotes(currentFundo.id, () =>
                                        setTimeout(() => $(node).find("i").removeClass("fa-spin"), 600)
                                    );
                                },
                            },
                            {
                                extend: "excelHtml5",
                                title: `RPT_LOTES_${currentFundo.nombre}`.replace(/\s+/g, "_"),
                                text: '<i class="far fa-file-excel"></i> Excel',
                                className: "btn-sm btn-success",
                                excelStyles: [{template: "green_medium"}],
                            },
                            {
                                extend: "pdfHtml5",
                                title: `RPT_LOTES_${currentFundo.nombre}`,
                                text: '<i class="far fa-file-pdf"></i> PDF',
                                className: "btn-sm btn-danger",
                                orientation: "landscape",
                                pageSize: "A4",
                                customize: function (doc) {
                                    doc.defaultStyle.fontSize = 9;
                                    doc.styles.tableHeader.fontSize = 10;
                                    doc.styles.title.fontSize = 12;
                                    doc.pageMargins = [14, 14, 14, 14];
                                },
                            },
                        ],
                        language: {url: window.dataTableEsUrl || ""},
                        pageLength: 10,
                        searching: true,
                        ordering: true,
                        destroy: true,
                        scrollX: true,
                    });


                    function bindLoteRowClick() {
                        $table.find("tbody").off("click.mapeo").on("click.mapeo", ".lote-row", function () {
                            const loteId = $(this).data("id");
                            const loteNombre = $(this).data("nombre");
                            const areaTotal = $(this).data("area");
                            const idAsignacion = $(this).data("asignacion");
                            openMapeoModal(loteId, loteNombre, areaTotal, idAsignacion);
                        });
                    }

                    bindLoteRowClick();
                    $table.on('draw.dt', function () {
                        bindLoteRowClick();
                    });

                    if (typeof done === "function") done();
                },
                error: function (xhr) {
                    console.error("Error al cargar lotes:", xhr);
                    $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-danger">No se pudieron cargar los lotes.</td></tr>`);
                    if (typeof done === "function") done();
                }
            });
        },
        error: function (xhr) {
            console.error("Error al cargar asignaciones:", xhr);
            $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-danger">No se pudieron cargar tus asignaciones de lotes.</td></tr>`);
            if (typeof done === "function") done();
        }
    });
}

// ====================== //
// 🔹 1. Cargar datos base
// ====================== //
async function fetchMapeoData(idAsignacion) {
    const [tipos, mapeo] = await Promise.all([
        $.getJSON("/presupuesto-agricola/mapeo/api/tipo_planta/"),
        $.getJSON(`/presupuesto-agricola/mapeo/api/mapeo/?ID_ASIGNACION=${idAsignacion}`)
    ]);
    return {tipos: getArray(tipos), mapeo: mapeo};
}

// ====================== //
// 🔹 2. Renderizar detalle
// ====================== //
function renderMapeoDetalles($tbody, tipos, detalles) {
    $tbody.empty();
    let rows = "";

    // Mostrar filas existentes (si las hay)
    if (detalles?.length) {
        let totalPlantas = detalles.reduce((sum, d) => sum + Number(d.CANTIDAD || 0), 0);

        detalles.forEach(det => {
            const porcentaje = totalPlantas ? ((det.CANTIDAD / totalPlantas) * 100).toFixed(2) : 0;
            rows += `
                <tr data-idtpplanta="${det.ID_TPPLANTA}">
                    <td><select class="form-control tipo-planta-select">${renderTipoOptions(tipos, det.ID_TPPLANTA)}</select></td>
                    <td><input type="number" min="0" class="form-control cantidad-mapeo" value="${det.CANTIDAD || 0}"></td>
                    <td class="porcentaje-mapeo">${porcentaje}</td>
                    <td><button type="button" class="btn btn-danger btn-sm btn-borrar-mapeo"><i class="fa fa-trash"></i></button></td>
                </tr>`;
        });
    }

    // Fila vacía para agregar nuevo tipo
    rows += `
        <tr class="fila-agregar">
            <td><select class="form-control tipo-planta-select">${renderTipoOptions(tipos)}</select></td>
            <td><input type="number" min="0" class="form-control cantidad-mapeo"></td>
            <td class="porcentaje-mapeo"></td>
            <td><button type="button" class="btn btn-primary btn-sm btn-agregar-mapeo"><i class="fa fa-plus"></i></button></td>
        </tr>
    `;

    $tbody.html(rows);
}


// ============================ //
// 🔹 1. Eventos de la tabla
// ============================ //
function bindMapeoTableEvents($modal, tipos) {
    const $tbody = $modal.find("#tablaTipoPlantaMapeo tbody");

    // 🔸 Recalcular totales y porcentajes
    function actualizarTotales() {
        let total = 0;
        $tbody.find("tr:not(.fila-agregar) .cantidad-mapeo").each(function () {
            total += Number($(this).val()) || 0;
        });

        $tbody.find("tr:not(.fila-agregar)").each(function () {
            const $row = $(this);
            const cantidad = Number($row.find(".cantidad-mapeo").val()) || 0;
            const porcentaje = total ? ((cantidad / total) * 100).toFixed(2) : "";
            $row.find(".porcentaje-mapeo").text(porcentaje);

        });

        $modal.find("#infoTotalPlantas").text(`Total plantas: ${total}`).show();
    }

    // 🔸 Evitar duplicados
    function tipoYaUsado(idTipo) {
        let existe = false;
        $tbody.find("tr:not(.fila-agregar) .tipo-planta-select").each(function () {
            if (String($(this).val()) === String(idTipo)) {
                existe = true;
                return false;
            }
        });
        return existe;
    }

    // 🔸 Actualizar opciones en la fila de agregar
    function actualizarFilaAgregar() {
        const usados = [];
        $tbody.find("tr:not(.fila-agregar) .tipo-planta-select").each(function () {
            const val = $(this).val();
            if (val) usados.push(String(val));
        });

        const $filaAgregar = $tbody.find(".fila-agregar .tipo-planta-select");
        const opciones = tipos.map(tp => {
            const id = String(tp.ID_TPPLANTA);
            const disabled = usados.includes(id) ? "disabled" : "";
            return `<option value="${id}" ${disabled}>${escapeHTML(tp.DESCRIPCION)}</option>`;
        }).join("");

        $filaAgregar.html(`<option value="">Seleccione...</option>${opciones}`);
    }

    // ========================== //
    // 🟩 EVENTOS DINÁMICOS
    // ========================== //

    // 🔸 1. Cambios en cantidad → recalcular totales
    $tbody.off("input.mapeo change.mapeo").on("input.mapeo change.mapeo", ".cantidad-mapeo", actualizarTotales);

    // 🔸 2. Eliminar fila
    $tbody.off("click.borrar").on("click.borrar", ".btn-borrar-mapeo", function () {
        $(this).closest("tr").remove();
        actualizarFilaAgregar();
        actualizarTotales();
    });

    // 🔸 3. Agregar fila nueva
    $tbody.off("click.agregar").on("click.agregar", ".btn-agregar-mapeo", function () {
        const $row = $(this).closest("tr");
        const idTipo = $row.find(".tipo-planta-select").val();
        const descTipo = $row.find(".tipo-planta-select option:selected").text();
        const cantidad = Number($row.find(".cantidad-mapeo").val()) || 0;

        if (!idTipo || cantidad <= 0) {
            Swal.fire({
                icon: "warning",
                title: "Campos incompletos",
                text: "Selecciona tipo de planta y cantidad válida."
            });
            return;
        }

        // Evitar duplicados
        if (tipoYaUsado(idTipo)) {
            Swal.fire({
                icon: "warning",
                title: "Tipo repetido",
                text: `El tipo "${descTipo}" ya fue agregado.`
            });
            return;
        }

        // Crear nueva fila
        const nuevaFila = `
            <tr data-idtpplanta="${idTipo}">
                <td><select class="form-control tipo-planta-select">
                    <option value="${idTipo}" selected>${escapeHTML(descTipo)}</option>
                </select></td>
                <td><input type="number" min="0" class="form-control cantidad-mapeo" value="${cantidad}"></td>
                <td class="porcentaje-mapeo"></td>
                <td><button type="button" class="btn btn-danger btn-sm btn-borrar-mapeo"><i class="fa fa-trash"></i></button></td>
            </tr>
        `;
        $row.before(nuevaFila);

        // Limpiar la fila de agregar
        $row.find(".tipo-planta-select").val("");
        $row.find(".cantidad-mapeo").val("");

        actualizarFilaAgregar();
        actualizarTotales();
    });

    // Inicializa al abrir
    actualizarFilaAgregar();
    actualizarTotales();
}

// ====================== //
// 🔹 3. Renderizar opciones
// ====================== //
function renderTipoOptions(tipos, selectedId = null) {
    return tipos.map(tp => `
        <option value="${tp.ID_TPPLANTA}" ${String(tp.ID_TPPLANTA) === String(selectedId) ? 'selected' : ''}>
            ${escapeHTML(tp.DESCRIPCION)}
        </option>
    `).join("");
}

// ====================== //
// 🔹 4. Obtener payload
// ====================== //
function getMapeoPayload($modal) {
    const $tbody = $modal.find("#tablaTipoPlantaMapeo tbody");

    const detalles = [];
    $tbody.find("tr:not(.fila-agregar)").each(function () {
        const $row = $(this);
        const id_planta = $row.find(".tipo-planta-select").val();
        const cantidad = parseFloat($row.find(".cantidad-mapeo").val()).toFixed(2) || 0;
        const porcentaje = parseFloat($row.find(".porcentaje-mapeo").text()).toFixed(2) || 0;

        if (id_planta && cantidad > 0) {
            detalles.push({
                ID_TPPLANTA: id_planta,
                CANTIDAD: cantidad,
                PORCENTAJE: porcentaje
            });

        }
    });

    const planta2 = detalles.find(d => d.ID_TPPLANTA === "2");
    const cantidadPlanta2 = planta2 ? planta2.CANTIDAD : 0;
    const densidad = parseFloat($("#inputDensidad").val()).toFixed(2) || 0;
    const hilera = parseFloat($("#inputHilera").val() || 0).toFixed(2);
    const planta = parseFloat($("#inputPlanta").val() || 0).toFixed(2);

    const total_plantas = detalles.reduce((sum, d) => sum + parseFloat(d.CANTIDAD), 0);
    const area_productiva = (total_plantas / (densidad || 1)).toFixed(2);

    console.log('hilera: ' + hilera);
    console.log('planta: ' + planta);
    console.log('densidad: 10000 / (hilera * planta) = ' + densidad);
    console.log('total_plantas: ' + total_plantas);
    console.log('area_productiva: ' + area_productiva);


    const mapeo = {
        ID_ASIGNACION: $("#ID_ASIGNACION").val(),
        FECHA: $("#fechaMapeo").val(),
        HILERA: hilera,
        PLANTA: planta,
        DENSIDAD: densidad,
        AREA_PRODUCTIVA: area_productiva,
        TOTAL_PLANTAS: total_plantas,
        OBSERVACION: $("#inputObservacion").val() || null
    };

    return {mapeo, detalles};
}

// ====================== //
// 🔹 5. Guardar mapeo
// ====================== //
async function saveMapeo($modal) {
    const payload = getMapeoPayload($modal);
    console.log("📤 Enviando mapeo:", payload);

    try {
        const resp = await $.ajax({
            url: "/presupuesto-agricola/mapeo/api/mapeo/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(payload)
        });

        Swal.fire({icon: "success", title: "Guardado", text: "Mapeo guardado correctamente."});
        $("#modalMapeoCRUD").modal("hide");
        console.log("✅ Respuesta backend:", resp);
    } catch (err) {
        console.error("Error al guardar:", err);
        Swal.fire({icon: "error", title: "Error", text: "No se pudo guardar el mapeo."});
    }
}

// ====================== //
// 🔹 6. Inicializar modal
// ====================== //
async function openMapeoModal(loteId, loteNombre, areaTotal, idAsignacion) {
    console.log('idAsignacion:' + idAsignacion);
    const $modal = $("#modalMapeoCRUD");
    const $tbody = $modal.find("#tablaTipoPlantaMapeo tbody");

    $modal.modal("show");
    $modal.find("#MAPEO_ID_LOTE").val(loteId);
    $modal.find("#ID_ASIGNACION").val(idAsignacion);
    $modal.find("#modalMapeoCRUDLabel").text(`Mapeo de Plantas - Lote: ${loteNombre}`);
    $tbody.html(`<tr><td colspan="4" class="text-center"><span class="spinner-border spinner-border-sm"></span> Cargando...</td></tr>`);

    try {
        const {tipos, mapeo} = await fetchMapeoData(idAsignacion);
        console.log("🌱 Datos cargados:", {tipos, mapeo});

        renderMapeoDetalles($tbody, tipos, mapeo.detalles || []);
        bindMapeoTableEvents($modal, tipos);

        // Cargar datos generales si existen
        if (mapeo?.mapeo) {
            const m = mapeo.mapeo;
            $("#inputHilera").val(m.HILERA || "");
            $("#inputPlanta").val(m.PLANTA || "");
            $("#inputDensidad").val(m.DENSIDAD || "");
            $("#inputObservacion").val(m.OBSERVACION || "");
        }

        // Botón guardar
        $("#btnGuardarMapeo").off("click").on("click", () => saveMapeo($modal));

    } catch (err) {
        console.error("Error cargando datos del mapeo:", err);
        Swal.fire({icon: "error", title: "Error", text: "No se pudo cargar el mapeo."});
    }
}

function limpiarModalMapeo() {
    // Limpia todos los inputs numéricos y de texto
    $("#formMapeoCRUD input[type='number'], #formMapeoCRUD input[type='text']").val("");

    // Limpia selects (por ejemplo cajas por lote)
    $("#formMapeoCRUD select").prop("selectedIndex", 0);

    // Limpia campos calculados
    $("#inputDensidad").val("");
    $("#racimoNacional").val("");

    // Limpia campos simples de hilera y planta
    $("#inputHilera").val("");
    $("#inputPlanta").val("");

    // Limpia tabla (si es editable)
    $("#tablaTipoPlantaMapeo tbody input[type='number']").val("");

    // Limpia alertas o mensajes
    $("#infoTotalPlantas").hide().text("");

}

function cargarTablaMapeo() {
    const $modal = $("#modalResumenMapeo");
    const $table = $("#tablaResumenMapeo");
    const campaniaSelect = document.getElementById("select-campania").value;
    console.log('CAMPAÑA:' + campaniaSelect);

    $modal.modal("show");
    $table.find("tbody").html(`<tr><td colspan="10" class="text-center text-muted">Cargando datos...</td></tr>`);

    // 🔹 Llamar directamente al endpoint
    $.getJSON(`/presupuesto-agricola/mapeo/api/mapeo_resumen_campania/?id_campania=${campaniaSelect}`, function (resp) {
        if (!resp.data || !resp.data.length) {
            $table.find("tbody").html(`<tr><td colspan="10" class="text-center text-muted">No hay mapeo registrado para esta campaña.</td></tr>`);
            return;
        }

        const data = resp.data;
        const columnas = Object.keys(data[0]); // columnas dinámicas

        // 🔹 Crear encabezado dinámico
        const headerHtml = columnas.map(col => `<th>${col}</th>`).join("");
        $("#headerPrincipal").html(headerHtml);

        // 🔹 Destruir DataTable anterior
        if ($.fn.DataTable.isDataTable($table)) {
            $table.DataTable().clear().destroy();
        }

        // 🔹 Configurar columnas dinámicas
        const colDefs = columnas.map(col => ({
            data: col,
            className: "text-center align-middle",
            render: (d) => {
                if (col.toUpperCase() === "PORC_TOTAL") {
                    return d ? `${parseFloat(d).toFixed(2)} %` : "0.00 %";
                }
                if (!isNaN(parseFloat(d)) && d !== null && d !== "") {
                    const num = parseFloat(d);
                    return Number.isInteger(num) ? num : num.toFixed(2);
                }
                return d ?? "";
            }
        }));

        // 🔹 Inicializar DataTable
        $table.DataTable({
            data: data,
            columns: colDefs,
            paging: false,
            searching: true,
            ordering: true,
            responsive: true,
            scrollX: true,
            autoWidth: false,
            dom: '<"d-flex justify-content-between"fB>t',  // <-- BUSCADOR IZQUIERDA + BOTONES DERECHA

            buttons: [
                {
                    extend: 'excelHtml5',
                    text: 'Exportar Excel',
                    titleAttr: 'Descargar Excel',
                    className: 'btn btn-success btn-sm'
                }
            ],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                search: "Buscar:"
            }
        });
    }).fail(function (xhr) {
        $table.find("tbody").html(`<tr><td colspan="10" class="text-center text-danger">Error al cargar datos (${xhr.statusText})</td></tr>`);
    });
}

function loadLotes(fundoId, done) {
    if (lotesDT) {
        lotesDT.destroy();
        lotesDT = null;
    }
    $table.find("tbody").html(`
            <tr><td colspan="4" class="text-center">
                <span class="spinner-border spinner-border-sm"></span> Cargando lotes...</td></tr>`);

    console.log("[MAPEO] loadLotes llamado", {fundoId, currentFundo, table: $table});

    const userId = window.USER_ID;
    console.log("[MAPEO] USER_ID:", userId);
    if (!userId) {
        $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-danger">No se pudo determinar el usuario actual.</td></tr>`);
        if (typeof done === "function") done();
        return;
    }

    $.ajax({
        url: "/presupuesto-agricola/asignacion/api/asignacion_lote/",
        type: "GET",
        success: function (resp) {
            console.log("[MAPEOo] asignacion_lote resp:", resp);
            const asignaciones = getArray(resp);
            console.log("[MAPEOo] asignaciones filtradas:", asignaciones);
            const lotesAsignados = asignaciones.map(a => a.ID_LOTE);
            console.log("[MAPEOo] lotesAsignados:", lotesAsignados);
            if (!lotesAsignados.length) {
                $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-muted">No tienes lotes asignados en este fundo.</td></tr>`);
                if (typeof done === "function") done();
                return;
            }
            $.ajax({
                url: "/gerencia_produccion/api/lotes/",
                type: "GET",
                success: function (resp2) {
                    console.log("[MAPEOo] lotes resp:", resp2);
                    let lotes = getArray(resp2);
                    lotes = lotes.filter(l => (String(l.ID_FUNDO) === String(fundoId)) && lotesAsignados.includes(l.ID_LOTE || l.id_lote || l.id));
                    console.log("[MAPEO] lotes filtrados:", lotes);
                    if (!lotes.length) {
                        $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-muted">No tienes lotes asignados en este fundo.</td></tr>`);
                        if (typeof done === "function") done();
                        return;
                    }
                    const rows = lotes
                        .map(
                            (l, idx) => `
                                <tr class="lote-row" data-id="${escapeHTML(l.ID_LOTE)}"
                                data-nombre="${escapeHTML(l.DESCRIPCION)}"
                                data-area="${escapeHTML(l.AREA_TOTAL)}"
                                data-asignacion="${escapeHTML(l.ID_ASIGNACION)}
                                ">
                                    <td>${escapeHTML(l.DESCRIPCION)}</td>
                                    <td class="text-right">${formatNumber(l.AREA_TOTAL, 2)}</td>
                                    <td>${escapeHTML(VARIEDADES[String(l.ID_VARIEDAD)] || "—")}</td>
                                    <td>${escapeHTML(l.CECO || "—")}</td>
                                </tr>`
                        )
                        .join("");
                    $table.find("tbody").html(rows);
                    lotesDT = $table.DataTable({
                        dom: "Bfrtip",
                        buttons: [
                            {
                                text: '<i class="fas fa-sync-alt"></i>',
                                className: "btn-sm btn-secondary",
                                action: function (e, dt, node) {
                                    $(node).find("i").addClass("fa-spin");
                                    loadLotes(currentFundo.id, () =>
                                        setTimeout(() => $(node).find("i").removeClass("fa-spin"), 600)
                                    );
                                },
                            },
                            {
                                extend: "excelHtml5",
                                title: `RPT_LOTES_${currentFundo.nombre}`.replace(/\s+/g, "_"),
                                text: '<i class="far fa-file-excel"></i> Excel',
                                className: "btn-sm btn-success",
                                excelStyles: [{template: "green_medium"}],
                            },
                            {
                                extend: "pdfHtml5",
                                title: `RPT_LOTES_${currentFundo.nombre}`,
                                text: '<i class="far fa-file-pdf"></i> PDF',
                                className: "btn-sm btn-danger",
                                orientation: "landscape",
                                pageSize: "A4",
                                customize: function (doc) {
                                    doc.defaultStyle.fontSize = 9;
                                    doc.styles.tableHeader.fontSize = 10;
                                    doc.styles.title.fontSize = 12;
                                    doc.pageMargins = [14, 14, 14, 14];
                                },
                            },
                        ],
                        language: {url: window.dataTableEsUrl || ""},
                        pageLength: 10,
                        searching: true,
                        ordering: true,
                        destroy: true,
                        scrollX: true,
                    });

                    function bindLoteRowClick() {
                        $table
                            .find("tbody")
                            .off("click.mapeo")
                            .on("click.mapeo", ".lote-row", function () {
                                const loteId = $(this).data("id");
                                const loteNombre = $(this).data("nombre");
                                const areaTotal = $(this).data("area");
                                const idAsignacion = $(this).data("data-asignacion");
                                openMapeoModal(loteId, loteNombre, areaTotal, idAsignacion);
                            });
                    }

                    bindLoteRowClick();
                    $table.on("draw.dt", function () {
                        bindLoteRowClick();
                    });

                    if (typeof done === "function") done();
                },
                error: function (xhr) {
                    console.error("Error al cargar lotes:", xhr);
                    $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-danger">No se pudieron cargar los lotes.</td></tr>`);
                    if (typeof done === "function") done();
                }
            });
        },
        error: function (xhr) {
            console.error("Error al cargar asignaciones:", xhr);
            $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-danger">No se pudieron cargar tus asignaciones de lotes.</td></tr>`);
            if (typeof done === "function") done();
        }
    });
}

// ===== FUNCIONES PARA CAMPOS SIMPLES DE HILERA, PLANTA Y DENSIDAD =====

// Función para calcular densidad automáticamente
function calcularDensidadSimple() {
    const hilera = parseFloat($('#inputHilera').val()).toFixed(2) || 0;
    const planta = parseFloat($('#inputPlanta').val()).toFixed(2) || 0;

    if (hilera > 0 && planta > 0) {
        const densidad = 10000 / (hilera * planta);
        $('#inputDensidad').val(densidad.toFixed(2));
    } else {
        $('#inputDensidad').val('');
    }
}

// Event listeners para cálculo automático
$(document).ready(function () {
    // Calcular densidad cuando cambien los valores de hilera o planta
    $(document).on('input', '#inputHilera, #inputPlanta', function () {
        calcularDensidadSimple();
    });

    // Limpiar campos cuando se abra el modal
    $('#modalMapeoCRUD').on('show.bs.modal', function () {
        $('#inputHilera').val('');
        $('#inputPlanta').val('');
        $('#inputDensidad').val('');
    });
});
