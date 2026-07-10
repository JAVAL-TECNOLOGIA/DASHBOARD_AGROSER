    // Diccionario de variedades (ID: DESCRIPCION)
    const VARIEDADES = {
        1: "SWEET GLOBE",
        2: "AUTUMN CRISP",
        3: "MOSCATEL",
        4: "SUGRA 56"
    };
    // static/core/js/PRODUCCION_UVA1/DonLuis/mapeo_dl.js
    // MAPEO: Fundos (cards) -> Modal con Lotes

    (function ($) {
    // Diccionario de empresas (IDEMPRESA: DESCRIPCION)
    const EMPRESAS = {
        1: "SOCIEDAD AGRICOLA DON LUIS S.A",
        2: "INVERSIONES AJS S.A.C",
        3: "AGROINDUSTRIA CAMPOVERDE S.A.C"
    };
    "use strict";

    // ======= Helpers =======
    const COLORS = ["bg-green", "bg-blue", "bg-purple", "bg-orange", "bg-black", "bg-warning"];
    const $cards = $("#mapeo-cards");
    const $search = $("#mapeo-search");
    const $reload = $("#mapeo-reload");
    const $modal = $("#mapeoLotesModal");
    const $modalTitle = $("#mapeoLotesModalLabel");
    const $modalReload = $("#mapeo-modal-reload");
    const $table = $("#mapeoLotesTable");

    const escapeHTML = (s) =>
        String(s ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

  const formatNumber = (n, d = 0) =>
    Number(n || 0).toLocaleString("es-PE", {
      minimumFractionDigits: d,
      maximumFractionDigits: d,
    });

    const skeleton = (n = 6) =>
        Array.from({ length: n })
        .map(
            () => `
        <div class="col-md-4 col-sm-6 mb-3">
            <div class="widget widget-stats ${COLORS[Math.floor(Math.random()*COLORS.length)]}">
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

    // ======= Estado =======
    let currentFundo = { id: null, nombre: "" };
    let lotesDT = null;
    let debounceTimer = null;

    // ======= Init =======
    $(document).ready(function () {
        // Carga inicial de fundos
        loadFundos();

        // Carga al entrar por hash o al hacer click en la pestaña
        if (location.hash === "#default-tab-mapeo") loadFundos();

        $('a[href="#default-tab-mapeo"]').on("shown.bs.tab", function () {
        loadFundos();
        });

        // Búsqueda con debounce
        $search.on("input", function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => loadFundos($search.val().trim()), 300);
        });

        // Botón recargar lista de fundos
        $reload.on("click", function (e) {
        e.preventDefault();
        const $i = $(this).find("i");
        $i.addClass("fa-spin");
        loadFundos($search.val().trim(), () => setTimeout(() => $i.removeClass("fa-spin"), 600));
        });

        // Botón recargar lotes dentro del modal
        $modalReload.on("click", function (e) {
        e.preventDefault();
        const $btn = $(this);
        $btn.addClass("disabled");
        $modal.append('<div class="panel-loader"><span class="spinner-border spinner-border-sm"></span></div>');
        loadLotes(currentFundo.id, () => {
            setTimeout(() => {
            $modal.find(".panel-loader").remove();
            $btn.removeClass("disabled");
            }, 400);
        });
        });

        $modal.on("hidden.bs.modal", function () {
        if (lotesDT) {
            lotesDT.destroy();
            lotesDT = null;
        }
        $table.find("tbody").empty();
        });
    });

    // ======= Fundos (cards) =======
    function loadFundos(q = "", done) {
        $cards.html(skeleton());
        $cards.html(skeleton());
        const campaniaSelect = document.getElementById("select-campania").value;
        $.ajax({
            url: "/produccionuva1/api/fundos_por_usuario/?campania=" + campaniaSelect,
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
                                fecha: $("#fechaMapeo").val(),
                                hilera: $("#hilera").val(),
                                planta: $("#planta").val(),
                                densidad: $("#densidad").val(),
                                plantas: plantas   // <-- aquí va el objeto armado
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
                            url: "/presupuesto-agricola/api/mapeo_nuevo/",
                            type: "POST",
                            contentType: "application/json",
                            data: JSON.stringify(data),
                            success: function (resp) {
                                Swal.fire({ icon: 'success', title: 'Guardado', text: 'Mapeo guardado correctamente.' });
                                limpiarModalMapeo();
                                $("#modalMapeoCRUD").modal("hide");
                            },
                            error: function (xhr) {
                                Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo guardar el mapeo.' });
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

    document.addEventListener("DOMContentLoaded", function() {
  const selectCampania = document.getElementById("select-campania");

  selectCampania.addEventListener("change", function() {
    loadFundos();
  });
});

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

    function recalcularDensidad() {
    const hilera = parseFloat($("#hilera").val()) || 0;
    const planta = parseFloat($("#planta").val()) || 0;

    if (hilera > 0 && planta > 0) {
        const densidad = 10000 / (hilera * planta);
        $("#densidad").val(densidad.toFixed(2));
        recalcularAreaProductiva(); // también recalcula el área productiva
    } else {
        $("#densidad").val("");
    }
}

function recalcularAreaProductiva() {
    const densidad = parseFloat($("#densidad").val()) || 0;
    const productivas = parseInt($("#tablaTipoPlantaMapeo input[name='productiva']").val()) || 0;

    if (densidad > 0) {
        const area = productivas / densidad;
        $("#areaProductiva").val(area.toFixed(2));
    } else {
        $("#areaProductiva").val("");
    }
}

function recalcularTotalPlantas() {
    let total = 0;
    $("#tablaTipoPlantaMapeo input.cantidad-mapeo").each(function () {
        total += parseInt($(this).val()) || 0;
    });
    $("#totalPlantas").val(total);
}

function recalcularRacimoNacional() {
    const racimos = parseInt($("#racimosPlanta").val()) || 0;
    const packing = parseInt($("#racimoPacking").val()) || 0;

    const nacional = racimos - packing;
    $("#racimoNacional").val(nacional >= 0 ? nacional : 0);
}

// Eventos
$("#hilera, #planta").on("input", recalcularDensidad);
$("#tablaTipoPlantaMapeo").on("input", "input.cantidad-mapeo", function () {
    recalcularTotalPlantas();
    recalcularAreaProductiva();
});
$("#racimosPlanta, #racimoPacking").on("input", recalcularRacimoNacional);

    // ======= Modal de Lotes =======
    function openLotesModal(fundoId, nombre, campania) {
        console.log("[MAPEO] openLotesModal fundoId:", fundoId, "nombre:", nombre);
        currentFundo = { id: fundoId, nombre };
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

        console.log("[MAPEO] loadLotes llamado", { fundoId, currentFundo, table: $table });

        const userId = window.USER_ID;
        console.log("[MAPEO] USER_ID:", userId);
        if (!userId) {
            $table.find("tbody").html(`<tr><td colspan="4" class="text-center text-danger">No se pudo determinar el usuario actual.</td></tr>`);
            if (typeof done === "function") done();
            return;
        }

        $.ajax({
            url: "/gerencia_produccion/api/asignacion_lote/",
            type: "GET",
            success: function (resp) {
                console.log("[MAPEO] asignacion_lote resp:", resp);
                const asignaciones = getArray(resp).filter(a => String(a.ID_RESPONSABLE) === String(userId) && String(a.ID_CAMPANIA) === String(campania));
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
                                (l, idx) => `
                                <tr class="lote-row" data-id="${escapeHTML(l.ID_LOTE)}" data-nombre="${escapeHTML(l.DESCRIPCION)}" data-area="${escapeHTML(l.AREA_TOTAL)}">
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
                                    excelStyles: [{ template: "green_medium" }],
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
                            language: { url: window.dataTableEsUrl || "" },
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
                                openMapeoModal(loteId, loteNombre, areaTotal);
                            });
                        }
                        bindLoteRowClick();
                        $table.on('draw.dt', function() {
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

    function loadLotes(fundoId, done) {
        if (lotesDT) {
            lotesDT.destroy();
            lotesDT = null;
        }
        $table.find("tbody").html(`
            <tr><td colspan="4" class="text-center">
                <span class="spinner-border spinner-border-sm"></span> Cargando lotes...</td></tr>`);

        console.log("[MAPEO] loadLotes llamado", { fundoId, currentFundo, table: $table });

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
                const asignaciones = getArray(resp).filter(a => String(a.ID_RESPONSABLE) === String(userId));
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
                                (l, idx) => `
                                <tr class="lote-row" data-id="${escapeHTML(l.ID_LOTE)}" data-nombre="${escapeHTML(l.DESCRIPCION)}" data-area="${escapeHTML(l.AREA_TOTAL)}">
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
                                    excelStyles: [{ template: "green_medium" }],
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
                            language: { url: window.dataTableEsUrl || "" },
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
                  openMapeoModal(loteId, loteNombre, areaTotal);
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

    // ======= Modal CRUD MAPEO DE PLANTAS POR LOTE =======
    function openMapeoModal(loteId, loteNombre, areaTotal) {
        const $modal = $("#modalMapeoCRUD");
        $modal.modal("show");
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
            const asign = asignaciones.find(a => String(a.ID_LOTE) === String(loteId) && String(a.ID_RESPONSABLE) === String(userId));
            if (asign) idAsignacion = asign.ID_ASIGNACION;
            $modal.find("#ID_ASIGNACION").val(idAsignacion);
            $.getJSON(`/produccionuva1/api/mapeo_nuevo/?id_asignacion=${idAsignacion}`, function (mapeo) {
                if (mapeo.ok && mapeo.found) {
                    const data = mapeo.data;
                    // === Mapeo ===
                    $("#hilera").val(data.HILERA);
                    $("#planta").val(data.PLANTA);
                    $("#densidad").val(data.DENSIDAD);
                    $("#fechaMapeo").val(data.FECHA ? data.FECHA.split("T")[0] : "");

                    // === Producción ===
                    $("#rendimiento").val(data.RENDIMIENTO);
                    $("#racimosPlanta").val(data.RAC_PLANTA);
                    $("#racimoPacking").val(data.RAC_PACKING);
                    $("#racimoNacional").val(data.RAC_NACIONAL);
                    $("#pesoRacimo").val(data.PESO_RAC);
                    $("#cajasLote").val(data.CAJAS);

                    // === Tipos de plantas ===
                    $("#productiva").val(data.PLANTA_PRODUCTIVA);
                    $("#formacion").val(data.PLANTA_FORMACION);
                    $("#muertas").val(data.PLANTA_MUERTAS);
                    $("#ausentes").val(data.PLANTA_AUSENTE);
                    $("#enferma").val(data.PLANTA_ENFERMA);
                    $("#cordon").val(data.PLANTA_CORDON);
                    $("#moscatel_roja").val(data.PLANTA_OTRA_VARIEDAD);
                    $("#moscatel_negra").val(data.PLANTA_NO_PRODUCTIVAS);
                } else {
                limpiarModalMapeo(); // si no existe, modal limpia
                }
            });
        });
    }

          function actualizarTotalesYPorcentajes() {
                let total = 0;
                $tbody
                  .find("tr:not(.fila-agregar) .cantidad-mapeo")
                  .each(function () {
                    total += Number($(this).val()) || 0;
                  });
                $tbody.find("tr:not(.fila-agregar)").each(function () {
                  const $row = $(this);
                  const cantidad =
                    Number($row.find(".cantidad-mapeo").val()) || 0;
                  const porcentaje = total
                    ? ((cantidad / total) * 100).toFixed(2)
                    : "";
                  $row.find(".porcentaje-mapeo").text(porcentaje);
                });
                $modal
                  .find("#infoTotalPlantas")
                  .show()
                  .text(`Total plantas: ${total}`);
              }

              $tbody
                .off("input.mapeo change.mapeo")
                .on(
                  "input.mapeo change.mapeo",
                  ".cantidad-mapeo, .tipo-planta-select",
                  function () {
                    actualizarTotalesYPorcentajes();
                  }
                );

              $tbody
                .off("click.borrar")
                .on("click.borrar", ".btn-borrar-mapeo", function () {
                  $(this).closest("tr").remove();
                  actualizarTotalesYPorcentajes();
                });

              // Botón "Agregar" fijo arriba de la tabla
              $modal
                .off("click.agregar")
                .on("click.agregar", "#btnAgregarPlanta", function () {
                  const $row = $tbody.find(".fila-agregar");
                  const id_planta = $row.find(".tipo-planta-select").val();
                  const cantidad =
                    Number($row.find(".cantidad-mapeo").val()) || 0;

                  if (!id_planta || cantidad <= 0) {
                    Swal.fire({
                      icon: "warning",
                      title: "Completa los campos",
                      text: "Selecciona tipo de planta y cantidad.",
                    });
                    return;
                  }

                  // Evitar duplicados
                  let existe = false;
                  $tbody.find("tr:not(.fila-agregar)").each(function () {
                    if ($(this).find(".tipo-planta-select").val() == id_planta)
                      existe = true;
                  });
                  if (existe) {
                    Swal.fire({
                      icon: "warning",
                      title: "Ya existe",
                      text: "Este tipo de planta ya está agregado.",
                    });
                    return;
                  }

                  // Insertar nueva fila antes de la fila de agregar
                  const nuevaFila = `<tr data-tipo="${id_planta}">
        <td><select class="form-control tipo-planta-select">${renderTipoOptions(
          id_planta
        )}</select></td>
        <td><input type="number" min="0" class="form-control cantidad-mapeo" value="${cantidad}"></td>
        <td class="porcentaje-mapeo"></td>
        <td><button type="button" class="btn btn-danger btn-sm btn-borrar-mapeo"><i class="fa fa-trash"></i></button></td>
    </tr>`;
                  $row.before(nuevaFila);

                  // Limpiar fila agregar
                  $row.find(".tipo-planta-select").val("");
                  $row.find(".cantidad-mapeo").val("");

                  actualizarTotalesYPorcentajes();
                });

              actualizarTotalesYPorcentajes();

    })(jQuery);
