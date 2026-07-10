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

$("#racimosPlanta, #racimoPacking").on("input", recalcularRacimoNacional);

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
        url: "/presupuesto-agricola/produccion_uva/api/fundos_por_usuario/?campania=" + campaniaSelect,
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

        const data = {
            lote: {
                id_lote: $("#MAPEO_ID_LOTE").val(),
                area_lote: $("#AREA_LOTE").val(),
            },
            mapeo: {
                id_asignacion: $("#ID_ASIGNACION").val(),
                hilera: $("#hilera").val(),
                planta: $("#planta").val(),
                densidad: $("#densidad").val(),
                areaProductiva: $("#areaProductiva").val(),
                totalPlantas: $("#totalPlantas").val(),
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
            url: "/presupuesto-agricola/produccion_uva/api/produccion_nuevo/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (resp) {
                Swal.fire({icon: 'success', title: 'Guardado', text: 'Guardado correctamente.'});
                limpiarModalMapeo();
                $("#modalMapeoCRUD").modal("hide");
            },
            error: function (xhr) {
                Swal.fire({icon: 'error', title: 'Error', text: 'No se pudo guardar.'});
            }
        });
    });
    /* $("#btnGuardarMapeo").off("click.mapeo").on("click.mapeo", function () {
         const data = [];
         $tbody.find("tr").each(function () {
             const $row = $(this);
             const id_planta = $row.data("tipo");
             const cantidad = Number($row.find(".cantidad-mapeo").val()) || 0;
             const porcentaje = $row.find(".porcentaje-mapeo").text().replace('%','').trim();
             if (cantidad > 0) {
                 data.push({
                     ID_LOTE: loteId,
                     ID_PLANTA: id_planta,
                     CANTIDAD: cantidad,
                     PORCENTAJE: porcentaje || null,
                     ID_ASIGNACION: idAsignacion
                 });
             }
         });
         $.ajax({
             url: "/produccionuva1/api/mapeo/",
             type: "POST",
             contentType: "application/json",
             data: JSON.stringify({ lote: loteId, mapeos: data }),
             success: function (resp) {
                 Swal.fire({ icon: 'success', title: 'Guardado', text: 'Mapeo guardado correctamente.' });
                 $("#modalMapeoCRUD").modal("hide");
             },
             error: function (xhr) {
                 Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo guardar el mapeo.' });
             }
         });
     });*/
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
                    const rows = lotes
                        .map(
                            (l, idx) => {
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
                                </tr>`
                            })
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
                        $table.find("tbody").off("click.mapeo").on("click.mapeo", ".lote-row", function () {
                            const loteId = $(this).data("id");
                            const loteNombre = $(this).data("nombre");
                            const areaTotal = $(this).data("area");
                            const asignacion = $(this).data("asignacion");
                            openMapeoModal(loteId, loteNombre, areaTotal, asignacion);
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

// ======= Modal CRUD MAPEO DE PLANTAS POR LOTE =======
function openMapeoModal(loteId, loteNombre, areaTotal, asignacion) {
    const $modal = $("#modalMapeoCRUD");
    $modal.find("#MAPEO_ID_LOTE").val(loteId);
    $modal.find("#AREA_LOTE").val(areaTotal);
    $modal.find("#modalMapeoCRUDLabel").text(`Mapeo de Plantas - Lote: ${loteNombre}`);
    $modal.find("#infoTotalPlantas").hide();
    // const $tbody = $modal.find("#tablaTipoPlantaMapeo tbody");
    // $tbody.html('<tr><td colspan="4" class="text-center"><span class="spinner-border spinner-border-sm"></span> Cargando tipos de planta...</td></tr>');



    let idAsignacion = null;
    const userId = window.USER_ID;
    $.getJSON("/presupuesto-agricola/asignacion/api/asignacion_lote/", function (asignacionesResp) {
        const asignaciones = getArray(asignacionesResp);
        const asign = asignaciones.find(a => String(a.ID_LOTE) === String(loteId));
        if (asign) idAsignacion = asignacion;
        $modal.find("#ID_ASIGNACION").val(asignacion);
        $.getJSON(`/presupuesto-agricola/produccion_uva/api/produccion_nuevo/?id_asignacion=${asignacion}`, function (resp) {
            console.log("Respuesta:", resp);

            // 🟥 Caso 1: No existe mapeo
            if (!resp.ok || !resp.found || !resp.data?.mapeo) {
                Swal.fire({
                    icon: "warning",
                    title: "Mapeo no registrado",
                    text: resp.message || "Debes completar primero los datos de Mapeo (Hilera, Planta, Densidad) antes de ingresar Producción.",
                });
                limpiarModalMapeo(); // Limpia campos si corresponde
                return;
            }

            // 🟩 Caso 2: Existe Mapeo → Cargar datos
            const mapeo = resp.data.mapeo;
            const produccion = resp.data.produccion;

            // Cargar datos de mapeo
            $("#hilera").val(mapeo.HILERA);
            $("#planta").val(mapeo.PLANTA);
            $("#densidad").val(mapeo.DENSIDAD);
            $("#areaProductiva").val(mapeo.AREA_PRODUCTIVA);
            $("#totalPlantas").val(mapeo.PLANTAS_PRODUCTIVAS);

            // Bloquear sección de mapeo (solo lectura)
            $("#seccion-mapeo").prop("disabled", true);

            // Habilitar sección de producción
            $("#seccion-produccion").prop("disabled", false);

            // Mostrar modal
            $("#modalMapeo").modal("show");

            // 🟦 Caso 3: existe mapeo pero no producción → mensaje informativo
            if (!produccion) {
                Swal.fire({
                    icon: "info",
                    title: "Listo para registrar Producción",
                    text: "El Mapeo ya está registrado. Puedes continuar ingresando los datos de Producción.",
                    timer: 2500,
                    showConfirmButton: false
                });
            } else {
                 $("#racimosPlanta").val(produccion.RAC_PLANTA);
                $("#racimoPacking").val(produccion.RAC_PACKING);
                $("#racimoNacional").val(produccion.RAC_NACIONAL);
                $("#rendimiento").val(produccion.RENDIMIENTO);
                $("#pesoRacimo").val(produccion.PESO_RAC);
                $("#cajasLote").val(produccion.CAJAS);
            }

             $modal.modal("show");
        }).fail(function (xhr) {
            // 🟥 Caso: error del servidor (ej. 404)
            const resp = xhr.responseJSON;
            Swal.fire({
                icon: "warning",
                title: "Mapeo no registrado",
                text: resp?.message || "Debes completar primero los datos de Mapeo antes de ingresar los datos de Producción.",
            });
            limpiarModalMapeo();
        });
    });
}

function limpiarModalMapeo() {
    // Limpia todos los inputs numéricos y de texto
    $("#formMapeoCRUD input[type='number'], #formMapeoCRUD input[type='text']").val("");

    // Limpia selects (por ejemplo cajas por lote)
    $("#formMapeoCRUD select").prop("selectedIndex", 0);

    // Limpia campos calculados
    $("#densidad").val("");
    $("#racimoNacional").val("");

    // Limpia tabla (si es editable)
    $("#tablaTipoPlantaMapeo tbody input[type='number']").val("");

    // Limpia alertas o mensajes
    $("#infoTotalPlantas").hide().text("");
}

function cargarTablaProduccion() {
    const campaniaSelect = document.getElementById("select-campania").value;
   const $modal = $("#modalProduccionCampania");
    $modal.modal("show");

    // Destruir tabla previa si ya existe
    if ($.fn.DataTable.isDataTable("#tablaProduccionCampania")) {
        $("#tablaProduccionCampania").DataTable().destroy();
    }

    $("#tablaProduccionCampania").DataTable({
        ajax: {
            url: `/presupuesto-agricola/produccion_uva/api/produccion_campania/?id_campania=${campaniaSelect}`,
            dataSrc: "data"
        },
        scrollX: true,
        scrollY: "60vh",
        scrollCollapse: true,
        paging: false,
        fixedHeader: true,
        columns: [
            // { data: "ID_ASIGNACION" },
            { data: "ID_CAMPANIA" },
            // { data: "ID_USUARIO" },
            { data: "Ingeniero" },
            // { data: "ID_LOTE" },
            { data: "Lote" },
            { data: "Area" },
            { data: "Variedad" },
            { data: "HILERA" },
            { data: "PLANTA" },
            { data: "DENSIDAD" },
            { data: "TOTAL_PLANTAS" },
            { data: "RENDIMIENTO" },
            { data: "RAC_PLANTA" },
            { data: "RAC_PACKING" },
            { data: "RAC_NACIONAL" },
            { data: "PESO_RAC" },
            { data: "KG_PROYEC_LOTE" },
            { data: "KG_EXPOR_LOTE" },
            { data: "KG_DESC_CAMP_LOTE" },
            { data: "KG_DESC_PROC_LOTE" },
            { data: "KG_PROYEC_HA" },
            { data: "KG_EXPOR_HA" },
            { data: "KG_DESC_CAMP_HA" },
            { data: "KG_DESC_PROC_HA" },
            { data: "CAJ_LOTE" },
            { data: "CAJ_HA" },
            { data: "Contenedor_Cantidad" },
            { data: "PorcentajeCampania" },
            { data: "ENV_FRU_PACK" },
            { data: "TOTAL_KG_ENV" }
        ],
        columnDefs: [
            {
                targets: "_all",
                render: function (data, type, row) {
                    if (data === null || data === undefined || data === "") return "";
                    if (!isNaN(data)) return parseFloat(data).toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                    return data;
                }
            }
        ],
        language: {
            url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
            info: "Mostrando _TOTAL_ registros",
            infoEmpty: "Sin registros",
        },
        initComplete: function () {
            setTimeout(() => {
                $("#tablaProduccionCampania").DataTable().columns.adjust();
            }, 500);
        }
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
            console.log("[MAPEO] asignacion_lote resp:", resp);
            const asignaciones = getArray(resp);
            console.log("[MAPEO] asignaciones filtradas:", asignaciones);
            const lotesAsignados = asignaciones.map(a => a.ID_LOTE);
            console.log("[MAPEO] lotesAsignados:", lotesAsignados);
            if (!lotesAsignados.length) {
                $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-muted">No tienes lotes asignados en este fundo.</td></tr>`);
                if (typeof done === "function") done();
                return;
            }
            $.ajax({
                url: "/gerencia_produccion/api/lotes/",
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
                    const rows = lotes
                        .map(
                            (l, idx) => {

                                const asignacion = asignaciones.find(a => String(a.ID_LOTE) === String(l.ID_LOTE));
                                return `
                                <tr class="lote-row" data-id="${escapeHTML(l.ID_LOTE)}"
                                data-nombre="${escapeHTML(l.DESCRIPCION)}"
                                data-area="${escapeHTML(l.AREA_TOTAL)}"
                                data-asignacion="${escapeHTML(asignacion ? asignacion.ID_ASIGNACION : '')}">
                                    <td>${escapeHTML(l.DESCRIPCION)}</td>
                                    <td class="text-right">${formatNumber(l.AREA_TOTAL, 2)}</td>
                                    <td>${escapeHTML(VARIEDADES[String(l.ID_VARIEDAD)] || "—")}</td>
                                    <td>${escapeHTML(l.CECO || "—")}</td>
                                </tr>`
                            })
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
                                const asignacion = $(this).data("asignacion");
                                openMapeoModal(loteId, loteNombre, areaTotal, asignacion);
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

function recalcularRacimoNacional() {
    const racimos = parseInt($("#racimosPlanta").val()) || 0;
    const packing = parseInt($("#racimoPacking").val()) || 0;

    const nacional = racimos - packing;
    $("#racimoNacional").val(nacional >= 0 ? nacional : 0);
}