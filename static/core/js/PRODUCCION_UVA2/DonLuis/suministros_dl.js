/*-- =====================================================================================================================================================
-- Modulo	            : COSTOS
-- Autor			        : JHON GUTIERREZ
-- Fecha de creación  : 2024-10-18
-- Descripción		    : Controla la logica del los de suministros   
-- Parámetros		      : 
-- =====================================================================================================================================================
-- Resumen de modificaciones:
--  
-- =====================================================================================================================================================
-- PRECUPUSTO DON LUIS  utiles_oficinaModal
-- =====================================================================================================================================================*/

$(document).ready(function () {
  $("#aplicar_cantidad_masiva_computo").click(() =>
    aplicarCantidadMasiva("computo")
  );
  $("#aplicar_cantidad_masiva_otros").click(() =>
    aplicarCantidadMasiva("otros")
  );
  $("#aplicar_cantidad_masiva_construccion").click(() =>
    aplicarCantidadMasiva("construccion")
  );
  $("#aplicar_cantidad_masiva_agricultura").click(() =>
    aplicarCantidadMasiva("agricultura")
  );
  $("#aplicar_cantidad_masiva_proteccion").click(() =>
    aplicarCantidadMasiva("proteccion")
  );
  $("#aplicar_cantidad_masiva_uit").click(() => aplicarCantidadMasiva("uit"));
  $("#aplicar_cantidad_masiva_utiles").click(() =>
    aplicarCantidadMasiva("utiles")
  );
  $("#aplicar_cantidad_masiva_combustibles").click(() =>
    aplicarCantidadMasiva("")
  );
  $("#aplicar_cantidad_masiva_repuestos").click(() =>
    aplicarCantidadMasiva("repuestos")
  );
  //===================================================================

  $("#addMaterialModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addUtilesOficinaModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addEqipocomputoModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addOtrosSuministrosModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addMaterialConstruccionModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addRepuestosAccesoriosModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addEquiposuitModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addMaterialAgriculturaModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  $("#addEquipoProteccionModal").on("hidden.bs.modal", function () {
    resetearFormularioSuministros();
  });

  //===============================================
  $('input[type="number"]').attr({
    step: "0.01",
    min: "0",
  });

  $(".sidebar-trigger").off();
  // Eventos para recalcular totales
  $('[data-target="#combustiblesModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto, 100);
  });

  $('[data-target="#utiles_oficinaModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_UtilesOficina, 100);
  });

  $('[data-target="#equipo_computoModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_EquiposComputo, 100);
  });

  $('[data-target="#otros_suministrosModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_OtrosSuministros, 100);
  });

  $('[data-target="#material_construccionModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_MaterialConstruccion, 100);
  });

  $('[data-target="#repuestos_accesoriosModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_RepuestosAccesorios, 100);
  });

  $('[data-target="#equipos_uitModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_EquiposUIT, 100);
  });

  $('[data-target="#material_agriculturaModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_MaterialAgricultura, 100);
  });

  $('[data-target="#equipo_proteccionModal"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_EquiposProteccion, 100);
  });

  //=================================================================================================

  // Agregar esto al inicio de la función initPresupuestoMateriales
  $(".cantidad-mes").attr("step", "0.01");
  $(".cantidad-mes_utiles").attr("step", "0.01");
  $(".cantidad-mes_computo").attr("step", "0.01");
  $(".cantidad-mes_otros").attr("step", "0.01");
  $(".cantidad-mes-construccion").attr("step", "0.01");
  $(".cantidad-mes-repuestos").attr("step", "0.01");
  $(".cantidad-mes-uit").attr("step", "0.01");
  $(".cantidad-mes-agricultura").attr("step", "0.01");
  $(".cantidad-mes-proteccion").attr("step", "0.01");
  //=================================================================================================

  // Deshabilitar todos los campos de cantidad por defecto
  $(".cantidad-mes").prop("disabled", true);
  $(".cantidad-mes-utiles").prop("disabled", true);
  $(".cantidad-mes-computo").prop("disabled", true);
  $(".cantidad-mes-otros").prop("disabled", true);
  $(".cantidad-mes-construccion").prop("disabled", true);
  $(".cantidad-mes-uit").prop("disabled", true);
  $(".cantidad-mes-agricultura").prop("disabled", true);
  $(".cantidad-mes-proteccion").prop("disabled", true);
  $(".cantidad-mes-repuestos").prop("disabled", true);

  // Manejar cambios en los switches para cada tipo
  $('input[type="checkbox"][id$="_switch"]').change(function () {
    var mesId = this.id.replace("_switch", "");
    $("#" + mesId + "_cantidad").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_utiles"]').change(function () {
    var mesId = this.id.replace("_switch_utiles", "");
    $("#" + mesId + "_cantidad_utiles").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_computo"]').change(function () {
    var mesId = this.id.replace("_switch_computo", "");
    $("#" + mesId + "_cantidad_computo").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_otros"]').change(function () {
    var mesId = this.id.replace("_switch_otros", "");
    $("#" + mesId + "_cantidad_otros").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_construccion"]').change(function () {
    var mesId = this.id.replace("_switch_construccion", "");
    $("#" + mesId + "_cantidad_construccion").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_repuestos"]').change(function () {
    var mesId = this.id.replace("_switch_repuestos", "");
    $("#" + mesId + "_cantidad_repuestos").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_uit"]').change(function () {
    var mesId = this.id.replace("_switch_uit", "");
    $("#" + mesId + "_cantidad_uit").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_agricultura"]').change(function () {
    var mesId = this.id.replace("_switch_agricultura", "");
    $("#" + mesId + "_cantidad_agricultura").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_proteccion"]').change(function () {
    var mesId = this.id.replace("_switch_proteccion", "");
    $("#" + mesId + "_cantidad_proteccion").prop("disabled", !this.checked);
  });

  //=================================================================================================
  $('input[type="checkbox"]').change(function () {
    var mesId = this.id.replace("_switch", "");
    $("#" + mesId + "_cantidad").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_utiles"]').change(function () {
    var mesId = this.id.replace("_switch_utiles", "");
    $("#" + mesId + "_cantidad_utiles").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_computo"]').change(function () {
    var mesId = this.id.replace("_switch_computo", "");
    $("#" + mesId + "_cantidad_computo").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_otros"]').change(function () {
    var mesId = this.id.replace("_switch_otros", "");
    $("#" + mesId + "_cantidad_otros").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_construccion"]').change(function () {
    var mesId = this.id.replace("_switch_construccion", "");
    $("#" + mesId + "_cantidad_construccion").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_repuestos"]').change(function () {
    var mesId = this.id.replace("_switch_repuestos", "");
    $("#" + mesId + "_cantidad_repuestos").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_uit"]').change(function () {
    var mesId = this.id.replace("_switch_uit", "");
    $("#" + mesId + "_cantidad_uit").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_agricultura"]').change(function () {
    var mesId = this.id.replace("_switch_agricultura", "");
    $("#" + mesId + "_cantidad_agricultura").prop("disabled", !this.checked);
  });

  $('input[type="checkbox"][id$="_switch_proteccion"]').change(function () {
    var mesId = this.id.replace("_switch_proteccion", "");
    $("#" + mesId + "_cantidad_proteccion").prop("disabled", !this.checked);
  });
  //==================================================================================================
  initPresupuestoMateriales();
  initPresupuestoUtilesOficina();
  initPresupuestoEquiposComputo();
  initPresupuestoOtrosSuministros();
  initPresupuestoMaterialConstruccion();
  initPresupuestoRepuestosAccesorios();
  initPresupuestoEquiposUIT();
  initPresupuestoMaterialAgricultura();
  initPresupuestoEquiposProteccion();
  actualizarConsolidadoMateriales();
  //==================================================================================================

  // Inicializar autocompletado
  inicializarAutocomplete("#descripcion", "#idproducto");

  inicializarAutocomplete_UtilesOficina(
    "#descripcion_utiles",
    "#idproducto_utiles"
  );

  inicializarAutocomplete_EquiposComputo(
    "#descripcion_computo",
    "#idproducto_computo"
  );

  inicializarAutocomplete_OtrosSuministros(
    "#descripcion_otros",
    "#idproducto_otros"
  );

  inicializarAutocomplete_MaterialConstruccion(
    "#descripcion_construccion",
    "#idproducto_construccion"
  );

  inicializarAutocomplete_RepuestosAccesorios(
    "#descripcion_repuestos",
    "#idproducto_repuestos"
  );

  inicializarAutocomplete_EquiposUIT("#descripcion_uit", "#idproducto_uit");

  inicializarAutocomplete_MaterialAgricultura(
    "#descripcion_agricultura",
    "#idproducto_agricultura"
  );

  inicializarAutocomplete_EquiposProteccion(
    "#descripcion_proteccion",
    "#idproducto_proteccion"
  );

  //==================================================================================================

  // Eventos para recalcular totales
  $("#precio_unitario").on("input", calcularTotales);
  $(".cantidad-mes").on("input", calcularTotales);
  $('input[type="checkbox"]').on("change", calcularTotales);

  $("#precio_unitario_utiles").on("input", calcularTotales_UtilesOficina);
  $(".cantidad-mes_utiles").on("input", calcularTotales_UtilesOficina);
  $('input[type="checkbox"]').on("change", calcularTotales_UtilesOficina);
  $('input[type="checkbox"]').on("change", calcularTotales_UtilesOficina);

  $("#precio_unitario_computo").on("input", calcularTotales_EquiposComputo);
  $(".cantidad-mes_computo").on("input", calcularTotales_EquiposComputo);
  $('input[type="checkbox"][id$="_switch_computo"]').on(
    "change",
    calcularTotales_EquiposComputo
  );

  $("#precio_unitario_otros").on("input", calcularTotales_OtrosSuministros);
  $(".cantidad-mes_otros").on("input", calcularTotales_OtrosSuministros);
  $('input[type="checkbox"][id$="_switch_otros"]').on(
    "change",
    calcularTotales_OtrosSuministros
  );

  $("#precio_unitario_construccion").on(
    "input",
    calcularTotales_MaterialConstruccion
  );
  $(".cantidad-mes-construccion").on(
    "input",
    calcularTotales_MaterialConstruccion
  );
  $('input[type="checkbox"][id$="_switch_construccion"]').on(
    "change",
    calcularTotales_MaterialConstruccion
  );

  $("#precio_unitario_repuestos").on(
    "input",
    calcularTotales_RepuestosAccesorios
  );
  $(".cantidad-mes-repuestos").on("input", calcularTotales_RepuestosAccesorios);
  $('input[type="checkbox"][id$="_switch_repuestos"]').on(
    "change",
    calcularTotales_RepuestosAccesorios
  );

  $("#precio_unitario_uit").on("input", calcularTotales_EquiposUIT);
  $(".cantidad-mes-uit").on("input", calcularTotales_EquiposUIT);
  $('input[type="checkbox"][id$="_switch_uit"]').on(
    "change",
    calcularTotales_EquiposUIT
  );

  $("#precio_unitario_agricultura").on(
    "input",
    calcularTotales_MaterialAgricultura
  );
  $(".cantidad-mes-agricultura").on(
    "input",
    calcularTotales_MaterialAgricultura
  );
  $('input[type="checkbox"][id$="_switch_agricultura"]').on(
    "change",
    calcularTotales_MaterialAgricultura
  );

  $("#precio_unitario_proteccion").on(
    "input",
    calcularTotales_EquiposProteccion
  );
  $(".cantidad-mes-proteccion").on("input", calcularTotales_EquiposProteccion);
  $('input[type="checkbox"][id$="_switch_proteccion"]').on(
    "change",
    calcularTotales_EquiposProteccion
  );

  //==================================================================================================

  // Restaurar la pestaña activa
  restaurarPestaña();

  // Guardar la pestaña activa cuando se cambia
  $(".nav-tabs a").on("shown.bs.tab", function (e) {
    var activeTab = $(e.target).attr("href");
    localStorage.setItem("activeTab", activeTab);
  });

  // Delegación de eventos unificada
  $(document).on("input", '[id^="precio_unitario_"]', function () {
    const tipo = this.id.split("_").pop();
    $(`#precio_total_${tipo}`).text(recalcularTotal(tipo));
  });

  $(document).on("change", '[id$="_switch_"]', function () {
    const [mes, tipo] = this.id.split("_switch_");
    $(`#${mes}_cantidad_${tipo}`).prop("disabled", !this.checked);
    recalcularTotal(tipo);
  });

  // Función de recálculo genérica
  function recalcularTotal(tipo) {
    let total = 0;
    $(`.cantidad-mes-${tipo}`).each(function () {
      if ($(this).is(":enabled")) {
        total += parseFloat($(this).val()) || 0;
      }
    });
    return total * (parseFloat($(`#precio_unitario_${tipo}`).val()) || 0);
  }
});

function restaurarPestaña() {
  var activeTab = localStorage.getItem("activeTab");
  if (activeTab) {
    $('.nav-tabs a[href="' + activeTab + '"]').tab("show");
  }
}

//==================================================================================================

function calcularTotalPresupuesto() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor").text(
          formatearMonedaPEN(data["TIC_combustiblesylubricantes"] || "0.00")
        );

        $("#stats_materialoficina").text(
          formatearMonedaPEN(data["TIC_combustiblesylubricantes"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de materiales de oficina",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

function calcularTotalPresupuesto_UtilesOficina() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_utiles").text(
          formatearMonedaPEN(data["TIC_utilesoficina"] || "0.00")
        );
        $("#stats_utilesoficina").text(
          formatearMonedaPEN(data["TIC_utilesoficina"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de utiles de oficina",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

function calcularTotalPresupuesto_EquiposComputo() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_computo").text(
          formatearMonedaPEN(data["TIC_equiposcomputo"] || "0.00")
        );
        $("#stats_equiposcomputo").text(
          formatearMonedaPEN(data["TIC_equiposcomputo"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de equipos de computo",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

function calcularTotalPresupuesto_OtrosSuministros() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_otros").text(
          formatearMonedaPEN(data["TIC_otrossuministros"] || "0.00")
        );
        $("#stats_otrossuministros").text(
          formatearMonedaPEN(data["TIC_otrossuministros"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de otros suministros",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

function calcularTotalPresupuesto_MaterialConstruccion() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_construccion").text(
          formatearMonedaPEN(data["TIC_materialesconstruccion"] || "0.00")
        );
        $("#stats_materialesconstruccion").text(
          formatearMonedaPEN(data["TIC_materialesconstruccion"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de material de construccion",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

function calcularTotalPresupuesto_RepuestosAccesorios() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_repuestos").text(
          formatearMonedaPEN(data["TIC_repuestosaccesorios"] || "0.00")
        );
        $("#stats_repuestosaccesorios").text(
          formatearMonedaPEN(data["TIC_repuestosaccesorios"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de repuestos y accesorios",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

function calcularTotalPresupuesto_EquiposUIT() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_uit").text(
          formatearMonedaPEN(data["TIC_equiposuit"] || "0.00")
        );
        $("#stats_equiposuit").text(
          formatearMonedaPEN(data["TIC_equiposuit"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de equipos de uit",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

function calcularTotalPresupuesto_MaterialAgricultura() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_agricultura").text(
          formatearMonedaPEN(data["TIC_materialesagricultura"] || "0.00")
        );
        $("#stats_materialesagricultura").text(
          formatearMonedaPEN(data["TIC_materialesagricultura"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de material de agricultura",
          icon: "error",
        });
      },
    });
  });
}

function calcularTotalPresupuesto_EquiposProteccion() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        $("#totalPresupuestoValor_proteccion").text(
          formatearMonedaPEN(data["TIC_equiposproteccion"] || "0.00")
        );
        $("#stats_equiposproteccion").text(
          formatearMonedaPEN(data["TIC_equiposproteccion"] || "0.00")
        );
        actualizarConsolidadoMateriales();
        resolve();
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Error al obtener el total de los suministros de utiles de oficina",
          icon: "error",
        });
        reject(error);
      },
    });
  });
}

//EVENTO PARA RECARGAR TODOS LOS DATOS DE LOS SUMINISTROS
$("#recargarTodosSuministros").on("click", function () {
  Swal.fire({
    title: "Actualizando datos...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  Promise.all([
    calcularTotalPresupuesto(),
    calcularTotalPresupuesto_UtilesOficina(),
    calcularTotalPresupuesto_EquiposComputo(),
    calcularTotalPresupuesto_OtrosSuministros(),
    calcularTotalPresupuesto_MaterialConstruccion(),
    calcularTotalPresupuesto_RepuestosAccesorios(),
    calcularTotalPresupuesto_EquiposUIT(),
    calcularTotalPresupuesto_MaterialAgricultura(),
    calcularTotalPresupuesto_EquiposProteccion(),
  ])
    .then(() => {
      actualizarConsolidadoMateriales();
      return new Promise((resolve) => setTimeout(resolve, 500)); // Pequeño delay para asegurar que todo se actualizó
    })
    .then(() => {
      Swal.fire({
        icon: "success",
        title: "¡Datos actualizados!",
        text: "Los totales han sido recalculados correctamente",
        timer: 2000,
        showConfirmButton: false,
      });
    })
    .catch((error) => {
      console.error("Error durante la actualización:", error);
      Swal.fire({
        icon: "warning",
        title: "Error",
        text: "Hubo un problema al actualizar los datos. Por favor, intente nuevamente.",
      });
    });
});

//==================================================================================================

//INICIALIZAR AUTOCOMPLETE
function inicializarAutocomplete(descripcionSelector, idProductoSelector) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_UtilesOficina(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_utiles/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_utiles")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_utiles")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_UtilesOficina();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_EquiposComputo(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_computo/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_computo")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_computo")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_EquiposComputo();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_OtrosSuministros(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_otros_suministros/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_otros")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_otros")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_OtrosSuministros();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_MaterialConstruccion(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_material_construccion/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_construccion")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_construccion")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_MaterialConstruccion();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_RepuestosAccesorios(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_repuestos_accesorios/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_repuestos")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_repuestos")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_RepuestosAccesorios();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_EquiposUIT(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_equipos_uit/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_uit")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_uit")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_EquiposUIT();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_MaterialAgricultura(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_materiales_agricultura/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value.trim(),
                value: item.value.trim(),
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_agricultura")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_agricultura")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_MaterialAgricultura();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

function inicializarAutocomplete_EquiposProteccion(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_productos_equipos_proteccion/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Error al obtener los datos del producto: " + error,
              icon: "error",
            });
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_proteccion")
            .val("")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario")
            .focus();

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
            confirmButtonText: "Entendido",
          });
        } else {
          $("#precio_unitario_proteccion")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio")
            .attr("placeholder", "");
        }

        calcularTotales_EquiposProteccion();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : '<span class="badge bg-info">Último precio: S/ ' +
        item.ultimo_precio.toFixed(2) +
        "</span>";

    return $("<li>")
      .append(
        '<div class="autocomplete-item">' +
          '<div class="item-description">' +
          item.label +
          "</div>" +
          '<div class="item-price">' +
          precioText +
          "</div>" +
          "</div>"
      )
      .appendTo(ul);
  };
}

//======================================  ============================================================

//CALCULAR TOTALES MATERIALES DE OFICINA
function calcularTotales() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario").val()) || 0;

  $(".cantidad-mes").each(function () {
    var mes = this.id.replace("_cantidad", "");
    if ($("#" + mes + "_switch").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total").text(cantidadTotal);
  $("#precio_total").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_UtilesOficina() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_utiles").val()) || 0;

  $(".cantidad-mes-utiles").each(function () {
    var mes = this.id.replace("_cantidad_utiles", "");
    if ($("#" + mes + "_switch_utiles").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_utiles").text(cantidadTotal);
  $("#precio_total_utiles").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_EquiposComputo() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_computo").val()) || 0;

  $(".cantidad-mes-computo").each(function () {
    var mes = this.id.replace("_cantidad_computo", "");
    if ($("#" + mes + "_switch_computo").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_computo").text(cantidadTotal);
  $("#precio_total_computo").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_OtrosSuministros() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_otros").val()) || 0;

  $(".cantidad-mes-otros").each(function () {
    var mes = this.id.replace("_cantidad_otros", "");
    if ($("#" + mes + "_switch_otros").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_otros").text(cantidadTotal);
  $("#precio_total_otros").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_MaterialConstruccion() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario =
    parseFloat($("#precio_unitario_construccion").val()) || 0;

  $(".cantidad-mes-construccion").each(function () {
    var mes = this.id.replace("_cantidad_construccion", "");
    if ($("#" + mes + "_switch_construccion").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_construccion").text(cantidadTotal);
  $("#precio_total_construccion").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_RepuestosAccesorios() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_repuestos").val()) || 0;

  $(".cantidad-mes-repuestos").each(function () {
    var mes = this.id.replace("_cantidad_repuestos", "");
    if ($("#" + mes + "_switch_repuestos").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_repuestos").text(cantidadTotal);
  $("#precio_total_repuestos").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_EquiposUIT() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_uit").val()) || 0;

  $(".cantidad-mes-uit").each(function () {
    var mes = this.id.replace("_cantidad_uit", "");
    if ($("#" + mes + "_switch_uit").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_uit").text(cantidadTotal);
  $("#precio_total_uit").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_MaterialAgricultura() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_agricultura").val()) || 0;

  $(".cantidad-mes-agricultura").each(function () {
    var mes = this.id.replace("_cantidad_agricultura", "");
    if ($("#" + mes + "_switch_agricultura").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_agricultura").text(cantidadTotal);
  $("#precio_total_agricultura").text("S/ " + precioTotal.toFixed(2));
}

function calcularTotales_EquiposProteccion() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_proteccion").val()) || 0;

  $(".cantidad-mes-proteccion").each(function () {
    var mes = this.id.replace("_cantidad_proteccion", "");
    if ($("#" + mes + "_switch_proteccion").is(":checked")) {
      var cantidad = parseFloat($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_proteccion").text(cantidadTotal);
  $("#precio_total_proteccion").text("S/ " + precioTotal.toFixed(2));
}

//==================================================================================================

//PRESUPUESTO COMBUSTIBLES Y LUBRICANTES
function initPresupuestoMateriales() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#materialOficinaTable")) {
    return;
  }
  
  // Inicializar DataTable
  var table = $("#materialOficinaTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto();
      actualizarConsolidadoMateriales();
    },
    // boton de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_COMBUSTIBLES_LUBRICANTES",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_COMBUSTIBLES_LUBRICANTES",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,

    serverSide: false,
    autoWidth: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    // ajax para obtener los datos de la tabla
    ajax: {
      url: "/produccionuva2/produccionuva2_combustibles-lubricantes/",
      dataSrc: "data",
    },

    fixedColumns: {
      right: 1, // Fija la última columna (acciones) a la derecha
    },
    columns: [
      { data: "id", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },

      {
        data: "enero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },
      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: 2,
        width: "600px",
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],

    // Otras opciones de configuración de DataTables
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  // evento de clic para el botón de eliminar
  $("#materialOficinaTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_material(id, "material-oficina");
  });

  // Evento de clic para el botón de editar
  $("#materialOficinaTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_MaterialOficina(id);
  });

  // REGISTRAR COMBUSTIBLES Y LUBRICANTES
  $("#registerMaterialForm").on("submit", function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto").val().trim(),
      descripcion: $("#descripcion").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario").val()) || 0,
    };

    // verificar que la cantidad total sea mayor a cero
    var cantidadTotal = parseFloat($("#cantidad_total").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      let productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      // Verificar si se ha seleccionado un producto válido
      if (productoExistente) {
        Swal.fire({
          title: "¡Atención!",
          text: "Este producto ya está registrado en el presupuesto. Por favor, seleccione otro producto.",
          icon: "warning",
          confirmButtonText: "Entendido",
        });

        return;
      }
    }

    // Obtener los meses
    let meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch").is(":checked");
      var cantidad = switchChecked ? $("#" + mes + "_cantidad").val() : "0";
      jsonData[mes + "_cantidad"] = cantidad;
    });

    // Enviar datos al servidor
    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_combustibles-lubricantes/" +
          formId +
          "/"
        : "/produccionuva2/produccionuva2_combustibles-lubricantes/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),

      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addMaterialModal").modal("hide");
            $("#registerMaterialForm")[0].reset();
            $("#registerMaterialForm").removeAttr("data-id");
            $("#submitBtn").text("Agregar");
            calcularTotales();
            calcularTotalPresupuesto();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
          return;
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });

    // Reset del formulario

    resetearFormularioSuministros();
  });

  // Calcular el total inicial
  calcularTotalPresupuesto();
  actualizarConsolidadoMateriales();
}

function initPresupuestoUtilesOficina() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#utilesOficinaTable")) {
    return;
  }
  
  // Inicializar DataTable
  var table = $("#utilesOficinaTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_UtilesOficina();
      actualizarConsolidadoMateriales();
    },
    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_UTILES_OFICINA",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_UTILES_OFICINA",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,
    serverSide: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    // ajax para obtener los datos de la tabla
    ajax: {
      url: "/produccionuva2/produccionuva2_utiles-oficina/",
      dataSrc: "data",
    },
    columns: [
      { data: "id", title: "ID", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          // Simplemente usar el índice de la fila + 1
          return meta.row + 1;
        },
      },
      { data: "idproducto" },
      { data: "descripcion" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },

      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },
      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      { targets: [0, 1], className: "dt-body-rigth" },
      { targets: "_all", className: "dt-body-left" },
    ],
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    destroy: true,
  });

  // Agregar evento de clic para el botón de eliminar
  $("#utilesOficinaTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_utiles(id, "utiles-oficina");
  });

  // Evento de clic para el botón de editar
  $("#utilesOficinaTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_utiles(id);
  });

  /* registrar  */
  $("#registerMaterialForm_utiles").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_utiles").val().trim(),
      descripcion: $("#descripcion_utiles").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_utiles").val()) || 0,
    };

    var cantidadTotal = parseFloat($("#cantidad_total_utiles").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    // Solo verificar producto existente si es una nueva adición, no una actualización
    if (!isUpdate) {
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_utiles").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_utiles").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_utiles-oficina/" + formId + "/"
        : "/produccionuva2/produccionuva2_utiles-oficina/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addUtilesOficinaModal").modal("hide");
            $("#registerMaterialForm_utiles")[0].reset();
            $("#registerMaterialForm_utiles").removeAttr("data-id");
            $("#submitBtn_utiles").text("Agregar");
            calcularTotales_UtilesOficina();
            calcularTotalPresupuesto_UtilesOficina();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  // Agregar evento para resetear el formulario cuando se cierre el modal
  $("#addUtilesOficinaModal").on("hidden.bs.modal", function () {
    $("#registerMaterialForm_utiles")[0].reset();
    $("#registerMaterialForm_utiles").removeAttr("data-id");
    $("#submitBtn_utiles").text("Agregar");
    $(".cantidad-mes-utiles").prop("disabled", true);
    $('input[type="checkbox"][id$="_switch_utiles"]').prop("checked", false);
  });

  // Calcular el total inicial
  calcularTotalPresupuesto_UtilesOficina();
  actualizarConsolidadoMateriales();

  // Función para actualizar totales
  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario = parseFloat($("#precio_unitario_utiles").val()) || 0;

    $(".cantidad-mes-utiles").each(function () {
      var mes = this.id.replace("_cantidad_utiles", "");
      if ($("#" + mes + "_switch_utiles").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_utiles").text(cantidadTotal);
    $("#precio_total_utiles").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_utiles").on("input", actualizarTotales);
  $(".cantidad-mes-utiles").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_utiles"]').on("change", function () {
    var mesId = this.id.replace("_switch_utiles", "");
    $("#" + mesId + "_cantidad_utiles").prop("disabled", !this.checked);
    actualizarTotales();
  });

  // Calcular totales iniciales
  actualizarTotales();
}

function initPresupuestoEquiposComputo() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#equipoComputoTable")) {
    return;
  }
  
  var table = $("#equipoComputoTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_EquiposComputo();
      actualizarConsolidadoMateriales();
    },

    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_EQUIPOS_COMPUTO",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_EQUIPOS_COMPUTO",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,
    fixedColumns: true,
    serverSide: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    ajax: {
      url: "/produccionuva2/produccionuva2_equipos-computo/",
      dataSrc: "data",
    },
    columns: [
      { data: "id", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },

      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: [0, 1, 2],
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  // Agregar evento de clic para el botón de eliminar
  $("#equipoComputoTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_computo(id, "equipos-computo");
  });

  // Evento de clic para el botón de editar
  $("#equipoComputoTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_computo(id);
  });

  $("#registerMaterialForm_computo").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_computo").val().trim(),
      descripcion: $("#descripcion_computo").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_computo").val()) || 0,
    };

    var cantidadTotal = parseFloat($("#cantidad_total_computo").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      // Verificar si el producto ya está registrado
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_computo").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_computo").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_equipos-computo/" + formId + "/"
        : "/produccionuva2/produccionuva2_equipos-computo/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addEquipoComputoModal").modal("hide");
            $("#registerMaterialForm_computo")[0].reset();
            $("#registerMaterialForm_computo").removeAttr("data-id");
            $("#submitBtn_computo").text("Agregar");
            calcularTotales_EquiposComputo();
            calcularTotalPresupuesto_EquiposComputo();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  calcularTotalPresupuesto_EquiposComputo();
  actualizarConsolidadoMateriales();

  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario = parseFloat($("#precio_unitario_computo").val()) || 0;

    $(".cantidad-mes-computo").each(function () {
      var mes = this.id.replace("_cantidad_computo", "");
      if ($("#" + mes + "_switch_computo").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_computo").text(cantidadTotal);
    $("#precio_total_computo").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_computo").on("input", actualizarTotales);
  $(".cantidad-mes-computo").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_computo"]').on("change", function () {
    var mesId = this.id.replace("_switch_computo", "");
    $("#" + mesId + "_cantidad_computo").prop("disabled", !this.checked);
    actualizarTotales();
  });

  actualizarTotales();
}

function initPresupuestoOtrosSuministros() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#otrosSuministrosTable")) {
    return;
  }
  
  var table = $("#otrosSuministrosTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_OtrosSuministros();
      actualizarConsolidadoMateriales();
    },

    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_OTROS_SUMINISTROS",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_OTROS_SUMINISTROS",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,
    fixedColumns: true,
    serverSide: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    ajax: {
      url: "/produccionuva2/produccionuva2_otros-suministros/",
      dataSrc: "data",
    },
    columns: [
      { data: "id", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },
      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: [0, 1, 2],
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  $("#otrosSuministrosTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_otros_suministros(id, "otros-suministros");
  });

  // Evento de clic para el botón de editar
  $("#otrosSuministrosTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_otros_suministros(id);
  });

  $("#registerMaterialForm_otros").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_otros").val().trim(),
      descripcion: $("#descripcion_otros").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_otros").val()) || 0,
    };

    var cantidadTotal = parseFloat($("#cantidad_total_otros").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      // Verificar si el producto ya está registrado
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_otros").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_otros").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_otros-suministros/" + formId + "/"
        : "/produccionuva2/produccionuva2_otros-suministros/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addOtrosSuministrosModal").modal("hide");
            $("#registerMaterialForm_otros")[0].reset();
            $("#registerMaterialForm_otros").removeAttr("data-id");
            $("#submitBtn_otros").text("Agregar");
            calcularTotales_OtrosSuministros();
            calcularTotalPresupuesto_OtrosSuministros();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  calcularTotalPresupuesto_OtrosSuministros();
  actualizarConsolidadoMateriales();

  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario = parseFloat($("#precio_unitario_otros").val()) || 0;

    $(".cantidad-mes-otros").each(function () {
      var mes = this.id.replace("_cantidad_otros", "");
      if ($("#" + mes + "_switch_otros").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_otros").text(cantidadTotal);
    $("#precio_total_otros").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_otros").on("input", actualizarTotales);
  $(".cantidad-mes-otros").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_otros"]').on("change", function () {
    var mesId = this.id.replace("_switch_otros", "");
    $("#" + mesId + "_cantidad_otros").prop("disabled", !this.checked);
    actualizarTotales();
  });

  actualizarTotales();
}

function initPresupuestoMaterialConstruccion() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#materialConstruccionTable")) {
    return;
  }
  
  var table = $("#materialConstruccionTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_MaterialConstruccion();
      actualizarConsolidadoMateriales();
    },

    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_MATERIALES_CONSTRUCCION",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_MATERIALES_CONSTRUCCION",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,
    fixedColumns: true,
    serverSide: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    ajax: {
      url: "/produccionuva2/produccionuva2_material-construccion/",
      dataSrc: "data",
    },
    columns: [
      { data: "id", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },

      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: [0, 1, 2],
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  // evento de clic para el botón de eliminar
  $("#materialConstruccionTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_construccion(id, "material-construccion");
  });

  // Evento de clic para el botón de editar
  $("#materialConstruccionTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_construccion(id);
  });

  $("#registerMaterialForm_construccion").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_construccion").val().trim(),
      descripcion: $("#descripcion_construccion").val().trim(),
      precio_unitario:
        parseFloat($("#precio_unitario_construccion").val()) || 0,
    };

    var cantidadTotal =
      parseFloat($("#cantidad_total_construccion").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      // Verificar si el producto ya está registrado
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_construccion").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_construccion").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_material-construccion/" + formId + "/"
        : "/produccionuva2/produccionuva2_material-construccion/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addMaterialConstruccionModal").modal("hide");
            $("#registerMaterialForm_construccion")[0].reset();
            $("#registerMaterialForm_construccion").removeAttr("data-id");
            $("#submitBtn_construccion").text("Agregar");
            calcularTotales_MaterialConstruccion();
            calcularTotalPresupuesto_MaterialConstruccion();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  calcularTotalPresupuesto_MaterialConstruccion();
  actualizarConsolidadoMateriales();

  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario =
      parseFloat($("#precio_unitario_construccion").val()) || 0;

    $(".cantidad-mes-construccion").each(function () {
      var mes = this.id.replace("_cantidad_construccion", "");
      if ($("#" + mes + "_switch_construccion").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_construccion").text(cantidadTotal);
    $("#precio_total_construccion").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_construccion").on("input", actualizarTotales);
  $(".cantidad-mes-construccion").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_construccion"]').on(
    "change",
    function () {
      var mesId = this.id.replace("_switch_construccion", "");
      $("#" + mesId + "_cantidad_construccion").prop("disabled", !this.checked);
      actualizarTotales();
    }
  );

  actualizarTotales();
}

function initPresupuestoRepuestosAccesorios() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#repuestosAccesoriosTable")) {
    return;
  }
  
  var table = $("#repuestosAccesoriosTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_RepuestosAccesorios();
      actualizarConsolidadoMateriales();
    },

    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_REPUESTOS_ACCESORIOS",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_REPUESTOS_ACCESORIOS",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,
    serverSide: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    ajax: {
      url: "/produccionuva2/produccionuva2_repuestos-accesorios/",
      dataSrc: "data",
    },
    columns: [
      { data: "id", title: "ID", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },
      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: [0, 1, 2],
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  // evento de clic para el botón de eliminar
  $("#repuestosAccesoriosTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_accesorios(id, "repuestos-accesorios");
  });

  // Evento de clic para el botón de editar
  $("#repuestosAccesoriosTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_repuestos(id);
  });

  $("#registerMaterialForm_repuestos").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_repuestos").val().trim(),
      descripcion: $("#descripcion_repuestos").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_repuestos").val()) || 0,
    };

    var cantidadTotal = parseFloat($("#cantidad_total_repuestos").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      // Verificar si el producto ya está registrado
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_repuestos").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_repuestos").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_repuestos-accesorios/" + formId + "/"
        : "/produccionuva2/produccionuva2_repuestos-accesorios/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addRepuestosAccesoriosModal").modal("hide");
            $("#registerMaterialForm_repuestos")[0].reset();
            $("#registerMaterialForm_repuestos").removeAttr("data-id");
            $("#submitBtn_repuestos").text("Agregar");
            calcularTotales_RepuestosAccesorios();
            calcularTotalPresupuesto_RepuestosAccesorios();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  calcularTotalPresupuesto_RepuestosAccesorios();
  actualizarConsolidadoMateriales();

  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario = parseFloat($("#precio_unitario_repuestos").val()) || 0;

    $(".cantidad-mes-repuestos").each(function () {
      var mes = this.id.replace("_cantidad_repuestos", "");
      if ($("#" + mes + "_switch_repuestos").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_repuestos").text(cantidadTotal);
    $("#precio_total_repuestos").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_repuestos").on("input", actualizarTotales);
  $(".cantidad-mes-repuestos").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_repuestos"]').on(
    "change",
    function () {
      var mesId = this.id.replace("_switch_repuestos", "");
      $("#" + mesId + "_cantidad_repuestos").prop("disabled", !this.checked);
      actualizarTotales();
    }
  );

  actualizarTotales();
}

function initPresupuestoEquiposUIT() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#equiposuitTable")) {
    return;
  }
  
  var table = $("#equiposuitTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_EquiposUIT();
      actualizarConsolidadoMateriales();
    },

    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_EQUIPOS_UIT",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_EQUIPOS_UIT",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    autoWidth: false,
    scrollCollapse: true,

    serverSide: false,
    searching: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    ajax: {
      url: "/produccionuva2/produccionuva2_equipos-uit/",
      dataSrc: "data",
    },

    fixedColumns: {
      right: 1, // Fija la última columna (acciones) a la derecha
    },

    columns: [
      { data: "id", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },

      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },
      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: [0, 1, 2],
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],

    responsive: true,
    ordering: true,
    order: [[0, "desc"]],

    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  // evento de clic para el botón de eliminar
  $("#equiposuitTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_uit(id, "equipos-uit");
  });

  // Evento de clic para el botón de editar
  $("#equiposuitTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_uit(id);
  });

  $("#registerMaterialForm_uit").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_uit").val().trim(),
      descripcion: $("#descripcion_uit").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_uit").val()) || 0,
    };

    var cantidadTotal = parseFloat($("#cantidad_total_uit").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      // Verificar si el producto ya está registrado
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_uit").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_uit").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_equipos-uit/" + formId + "/"
        : "/produccionuva2/produccionuva2_equipos-uit/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addEquiposuitModal").modal("hide");
            $("#registerMaterialForm_uit")[0].reset();
            $("#registerMaterialForm_uit").removeAttr("data-id");
            $("#submitBtn_uit").text("Agregar");
            calcularTotales_EquiposUIT();
            calcularTotalPresupuesto_EquiposUIT();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  calcularTotalPresupuesto_EquiposUIT();
  actualizarConsolidadoMateriales();

  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario = parseFloat($("#precio_unitario_uit").val()) || 0;

    $(".cantidad-mes-uit").each(function () {
      var mes = this.id.replace("_cantidad_uit", "");
      if ($("#" + mes + "_switch_uit").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_uit").text(cantidadTotal);
    $("#precio_total_uit").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_uit").on("input", actualizarTotales);
  $(".cantidad-mes-uit").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_uit"]').on("change", function () {
    var mesId = this.id.replace("_switch_uit", "");
    $("#" + mesId + "_cantidad_uit").prop("disabled", !this.checked);
    actualizarTotales();
  });

  actualizarTotales();
}

function initPresupuestoMaterialAgricultura() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#materialagriculturaTable")) {
    return;
  }
  
  var table = $("#materialagriculturaTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_MaterialAgricultura();
      actualizarConsolidadoMateriales();
    },

    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_MATERIALES_AGRICULTURA",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_MATERIALES_AGRICULTURA",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,
    serverSide: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    ajax: {
      url: "/produccionuva2/produccionuva2_materiales-agricultura/",
      dataSrc: "data",
    },
    fixedColumns: {
      right: 1, // Fija la última columna (acciones) a la derecha
    },
    columns: [
      { data: "id", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },
      {
        data: null,
        className: "sticky-col",
        title: "Acciones",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: [0, 1, 2],
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  // evento de clic para el botón de eliminar
  $("#materialagriculturaTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_agricultura(id, "materiales-agricultura");
  });

  // Evento de clic para el botón de editar
  $("#materialagriculturaTable tbody").on("click", ".edit-btn", function () {
    var id = $(this).data("id");
    editarProducto_agricultura(id);
  });

  $("#registerMaterialForm_agricultura").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_agricultura").val().trim(),
      descripcion: $("#descripcion_agricultura").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_agricultura").val()) || 0,
    };

    var cantidadTotal =
      parseFloat($("#cantidad_total_agricultura").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      // Verificar si el producto ya está registrado
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_agricultura").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_agricultura").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_materiales-agricultura/" +
          formId +
          "/"
        : "/produccionuva2/produccionuva2_materiales-agricultura/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addMaterialAgriculturaModal").modal("hide");
            $("#registerMaterialForm_agricultura")[0].reset();
            $("#registerMaterialForm_agricultura").removeAttr("data-id");
            $("#submitBtn_agricultura").text("Agregar");
            calcularTotales_MaterialAgricultura();
            calcularTotalPresupuesto_MaterialAgricultura();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  calcularTotalPresupuesto_MaterialAgricultura();
  actualizarConsolidadoMateriales();

  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario =
      parseFloat($("#precio_unitario_agricultura").val()) || 0;

    $(".cantidad-mes-agricultura").each(function () {
      var mes = this.id.replace("_cantidad_agricultura", "");
      if ($("#" + mes + "_switch_agricultura").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_agricultura").text(cantidadTotal);
    $("#precio_total_agricultura").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_agricultura").on("input", actualizarTotales);
  $(".cantidad-mes-agricultura").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_agricultura"]').on(
    "change",
    function () {
      var mesId = this.id.replace("_switch_agricultura", "");
      $("#" + mesId + "_cantidad_agricultura").prop("disabled", !this.checked);
      actualizarTotales();
    }
  );

  actualizarTotales();
}

function initPresupuestoEquiposProteccion() {
  // Evitar reinicialización si la tabla ya existe
  if ($.fn.DataTable.isDataTable("#equipoProteccionTable")) {
    return;
  }
  
  var table = $("#equipoProteccionTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_EquiposProteccion();
      actualizarConsolidadoMateriales();
    },

    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_EQUIPOS_PROTECCION",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_EQUIPOS_PROTECCION",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    scrollCollapse: true,
    fixedColumns: true,
    serverSide: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    ajax: {
      url: "/produccionuva2/produccionuva2_equipos-proteccion/",
      dataSrc: "data",
    },
    columns: [
      { data: "id", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },
      { data: "idproducto", className: "text-left" },
      { data: "descripcion", className: "text-left" },
      {
        data: "enero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "enero_precio",
        render: function (data) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "febrero_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "marzo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "abril_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "mayo_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "junio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "julio_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "agosto_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "septiembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "octubre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "noviembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_cantidad",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: "diciembre_precio",
        render: function (data, type, row) {
          return parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });

          return "S/" + total.toFixed(2);
        },
      },

      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return (
            '<div class="d-flex justify-content-around">' +
            '<button class="btn  btn-danger delete-btn " data-id="' +
            row.id +
            '" title="Eliminar">' +
            '<i class="fas fa-trash fa-sm"></i>' +
            "</button>" +
            '<button class="btn  btn-primary edit-btn " data-id="' +
            row.id +
            '" title="Editar">' +
            '<i class="fas fa-edit fa-sm"></i>' +
            "</button>" +
            "</div>"
          );
        },
        orderable: false,
      },
    ],
    columnDefs: [
      {
        targets: [0, 1, 2],
        className: "dt-body-left",
      },
      {
        targets: "_all",
        className: "dt-body-right",
      },
    ],
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      url: dataTableEsUrl,
    },
    destroy: true,
  });

  // evento de clic para el botón de eliminar
  $("#equipoProteccionTable tbody").on("click", ".delete-btn", function () {
    var id = $(this).data("id");
    eliminarProducto_proteccion(id, "equipos-proteccion");
  });

  // Evento de clic para el botón de editar
  $("#equipoProteccionTable tbody").on("click", ".edit-btn", function () {
    let id = $(this).data("id");
    editarProducto_proteccion(id);
  });

  $("#registerMaterialForm_proteccion").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_proteccion").val().trim(),
      descripcion: $("#descripcion_proteccion").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_proteccion").val()) || 0,
    };

    var cantidadTotal = parseFloat($("#cantidad_total_proteccion").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    if (!isUpdate) {
      // Verificar si el producto ya está registrado
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ];

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_proteccion").is(":checked");
      var cantidad = switchChecked
        ? parseFloat($("#" + mes + "_cantidad_proteccion").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate
        ? "/produccionuva2/produccionuva2_equipos-proteccion/" + formId + "/"
        : "/produccionuva2/produccionuva2_equipos-proteccion/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addEquipoProteccionModal").modal("hide");
            $("#registerMaterialForm_proteccion")[0].reset();
            $("#registerMaterialForm_proteccion").removeAttr("data-id");
            $("#submitBtn_proteccion").text("Agregar");
            calcularTotales_EquiposProteccion();
            calcularTotalPresupuesto_EquiposProteccion();
            actualizarConsolidadoMateriales();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  calcularTotalPresupuesto_EquiposProteccion();
  actualizarConsolidadoMateriales();

  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario =
      parseFloat($("#precio_unitario_proteccion").val()) || 0;

    $(".cantidad-mes-proteccion").each(function () {
      var mes = this.id.replace("_cantidad_proteccion", "");
      if ($("#" + mes + "_switch_proteccion").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_proteccion").text(cantidadTotal);
    $("#precio_total_proteccion").text("S/" + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_proteccion").on("input", actualizarTotales);
  $(".cantidad-mes-proteccion").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_proteccion"]').on(
    "change",
    function () {
      var mesId = this.id.replace("_switch_proteccion", "");
      $("#" + mesId + "_cantidad_proteccion").prop("disabled", !this.checked);
      actualizarTotales();
    }
  );

  actualizarTotales();
}

//==================================================================================================
//==================================================================================================
function eliminarProducto_utiles(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#utilesOficinaTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_UtilesOficina();
              calcularTotalPresupuesto_UtilesOficina();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_computo(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#equipoComputoTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_EquiposComputo();
              calcularTotalPresupuesto_EquiposComputo();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_otros_suministros(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#otrosSuministrosTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_OtrosSuministros();
              calcularTotalPresupuesto_OtrosSuministros();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_material(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#materialOficinaTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_MaterialesOficina();
              calcularTotalPresupuesto_MaterialesOficina();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_construccion(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#materialConstruccionTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_MaterialesConstruccion();
              calcularTotalPresupuesto_MaterialesConstruccion();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_accesorios(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#repuestosAccesoriosTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_RepuestosAccesorios();
              calcularTotalPresupuesto_RepuestosAccesorios();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_uit(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#equiposuitTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_EquiposUIT();
              calcularTotalPresupuesto_EquiposUIT();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_agricultura(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#materialagriculturaTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_MaterialesAgricultura();
              calcularTotalPresupuesto_MaterialesAgricultura();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

function eliminarProducto_proteccion(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#equipoProteccionTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_EquiposProteccion();
              calcularTotalPresupuesto_EquiposProteccion();
              actualizarConsolidadoMateriales();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

/* ====================================================================================== 
   ================================MODULO DE EDITAR ===================================== 
  /* ====================================================================================== */

function editarProducto_utiles(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_utiles-oficina/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_utiles").val(data.idproducto);
      $("#descripcion_utiles").val(data.descripcion);
      $("#precio_unitario_utiles").val(data.precio_unitario);

      // Asegurar que el precio unitario esté bloqueado en modo edición
      $("#precio_unitario_utiles").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_utiles").val(cantidad);
        $("#" + mes + "_switch_utiles").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_utiles").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_utiles").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_utiles").attr("data-id", id);

      // Abrir el modal
      $("#addUtilesOficinaModal").modal("show");
      calcularTotales_UtilesOficina();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_MaterialOficina(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_combustibles-lubricantes/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto").val(data.idproducto);
      $("#descripcion").val(data.descripcion);
      $("#precio_unitario").val(data.precio_unitario);

      // Asegurar que el precio unitario esté bloqueado en modo edición
      $("#precio_unitario").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad").val(cantidad);
        $("#" + mes + "_switch").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm").attr("data-id", id);

      // Abrir el modal
      $("#addMaterialModal").modal("show");
      calcularTotales();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_computo(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_equipos-computo/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_computo").val(data.idproducto);
      $("#descripcion_computo").val(data.descripcion);
      $("#precio_unitario_computo").val(data.precio_unitario);

      $("#precio_unitario_computo").prop("readonly", true);
      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_computo").val(cantidad);
        $("#" + mes + "_switch_computo").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_computo").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_computo").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_computo").attr("data-id", id);

      // Abrir el modal
      $("#addEqipocomputoModal").modal("show");
      calcularTotales_EquiposComputo();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_otros_suministros(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_otros-suministros/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_otros").val(data.idproducto);
      $("#descripcion_otros").val(data.descripcion);
      $("#precio_unitario_otros").val(data.precio_unitario);

      $("#precio_unitario_otros").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_otros").val(cantidad);
        $("#" + mes + "_switch_otros").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_otros").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_otros").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_otros").attr("data-id", id);

      // Abrir el modal
      $("#addOtrosSuministrosModal").modal("show");
      calcularTotales_OtrosSuministros();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_construccion(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_material-construccion/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_construccion").val(data.idproducto);
      $("#descripcion_construccion").val(data.descripcion);
      $("#precio_unitario_construccion").val(data.precio_unitario);

      $("#precio_unitario_construccion").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_construccion").val(cantidad);
        $("#" + mes + "_switch_construccion").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_construccion").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_construccion").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_construccion").attr("data-id", id);

      // Abrir el modal
      $("#addMaterialConstruccionModal").modal("show");
      calcularTotales_MaterialConstruccion();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_repuestos(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_repuestos-accesorios/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_repuestos").val(data.idproducto);
      $("#descripcion_repuestos").val(data.descripcion);
      $("#precio_unitario_repuestos").val(data.precio_unitario);

      $("#precio_unitario_repuestos").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_repuestos").val(cantidad);
        $("#" + mes + "_switch_repuestos").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_repuestos").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_repuestos").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_repuestos").attr("data-id", id);

      // Abrir el modal
      $("#addRepuestosAccesoriosModal").modal("show");
      calcularTotales_RepuestosAccesorios();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_uit(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_equipos-uit/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_uit").val(data.idproducto);
      $("#descripcion_uit").val(data.descripcion);
      $("#precio_unitario_uit").val(data.precio_unitario);

      $("#precio_unitario_uit").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_uit").val(cantidad);
        $("#" + mes + "_switch_uit").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_uit").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_uit").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_uit").attr("data-id", id);

      // Abrir el modal
      $("#addEquiposuitModal").modal("show");
      calcularTotales_EquiposUIT();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_agricultura(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_materiales-agricultura/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_agricultura").val(data.idproducto);
      $("#descripcion_agricultura").val(data.descripcion);
      $("#precio_unitario_agricultura").val(data.precio_unitario);

      $("#precio_unitario_agricultura").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_agricultura").val(cantidad);
        $("#" + mes + "_switch_agricultura").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_agricultura").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_agricultura").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_agricultura").attr("data-id", id);

      // Abrir el modal
      $("#addMaterialAgriculturaModal").modal("show");
      calcularTotales_MaterialAgricultura();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function editarProducto_proteccion(id) {
  $.ajax({
    url: "/produccionuva2/produccionuva2_equipos-proteccion/" + id + "/",
    type: "GET",
    success: function (data) {
      // Llenar el formulario con los datos del producto

      $("#idproducto_proteccion").val(data.idproducto);
      $("#descripcion_proteccion").val(data.descripcion);
      $("#precio_unitario_proteccion").val(data.precio_unitario);

      $("#precio_unitario_proteccion").prop("readonly", true);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"];
        $("#" + mes + "_cantidad_proteccion").val(cantidad);
        $("#" + mes + "_switch_proteccion").prop("checked", cantidad > 0);
        $("#" + mes + "_cantidad_proteccion").prop("disabled", cantidad == 0);
      });

      // Cambiar el texto del botón de submit
      $("#submitBtn_proteccion").text("Actualizar Presupuesto");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_proteccion").attr("data-id", id);

      // Abrir el modal
      $("#addEquipoProteccionModal").modal("show");
      calcularTotales_EquiposProteccion();
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

function formatearMonedaPEN(monto) {
  return new Intl.NumberFormat("es-PE", {
    style: "currency",
    currency: "PEN",
    minimumFractionDigits: 2,
  })
    .format(monto)
    .replace("PEN", "S/")
    .replace("S/.", "S/");
}

//==================================================================================================
// BOTON ACTUALIZAR EL WIDGET CONSOLIDADO DE MATERIALES
//==================================================================================================

function actualizarConsolidadoMateriales() {
  var yearVal = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();
  $.ajax({
    url: `/produccionuva2/produccionuva2_suministros_totals_dl/?year=${yearVal}`,
    type: "GET",
    dataType: "json",
    success: function (data) {
      // Sumar todos los valores, reemplazando null por 0
      const totalConsolidado =
        parseFloat(data.TIC_equiposcomputo || 0) +
        parseFloat(data.TIC_equiposproteccion || 0) +
        parseFloat(data.TIC_equiposuit || 0) +
        parseFloat(data.TIC_materialesagricultura || 0) +
        parseFloat(data.TIC_materialesconstruccion || 0) +
        parseFloat(data.TIC_combustiblesylubricantes || 0) +
        parseFloat(data.TIC_otrossuministros || 0) +
        parseFloat(data.TIC_repuestosaccesorios || 0) +
        parseFloat(data.TIC_utilesoficina || 0);

      // Actualizar el widget consolidado
      $("#stats_materiales_consolidado").html(
        formatearMonedaPEN(totalConsolidado)
      );
    },
    error: function (xhr, status, error) {
      $("#stats_materiales_consolidado").html("S/ 0.00");
    },
  });
}

function resetearFormularioSuministros() {
  // Deshabilitar todos los campos de cantidad
  $(".cantidad-mes").prop("disabled", true);
  $(".cantidad-mes-utiles").prop("disabled", true);
  $(".cantidad-mes-computo").prop("disabled", true);
  $(".cantidad-mes-otros").prop("disabled", true);
  $(".cantidad-mes-construccion").prop("disabled", true);
  $(".cantidad-mes-uit").prop("disabled", true);
  $(".cantidad-mes-agricultura").prop("disabled", true);
  $(".cantidad-mes-proteccion").prop("disabled", true);
  $(".cantidad-mes-repuestos").prop("disabled", true);

  // Resetear formulario base
  $("#registerMaterialForm")[0].reset();
  $("#registerMaterialForm_utiles")[0].reset();
  $("#registerMaterialForm_computo")[0].reset();
  $("#registerMaterialForm_otros")[0].reset();
  $("#registerMaterialForm_construccion")[0].reset();
  $("#registerMaterialForm_uit")[0].reset();
  $("#registerMaterialForm_agricultura")[0].reset();
  $("#registerMaterialForm_proteccion")[0].reset();
  $("#registerMaterialForm_repuestos")[0].reset();

  $("#registerMaterialForm").removeAttr("data-id");
  $("#registerMaterialForm_utiles").removeAttr("data-id");
  $("#registerMaterialForm_computo").removeAttr("data-id");
  $("#registerMaterialForm_otros").removeAttr("data-id");
  $("#registerMaterialForm_construccion").removeAttr("data-id");
  $("#registerMaterialForm_uit").removeAttr("data-id");
  $("#registerMaterialForm_agricultura").removeAttr("data-id");
  $("#registerMaterialForm_proteccion").removeAttr("data-id");
  $("#registerMaterialForm_repuestos").removeAttr("data-id");

  // Limpiar campos específicos
  $("#descripcion").val("");
  $("#idproducto").val("");
  $("#precio_unitario").val("");

  $("#descripcion_utiles").val("");
  $("#descripcion_computo").val("");
  $("#descripcion_otros").val("");
  $("#descripcion_construccion").val("");
  $("#descripcion_uit").val("");
  $("#descripcion_agricultura").val("");
  $("#descripcion_proteccion").val("");
  $("#descripcion_repuestos").val("");

  $("#idproducto_utiles").val("");
  $("#idproducto_computo").val("");
  $("#idproducto_otros").val("");
  $("#idproducto_construccion").val("");
  $("#idproducto_uit").val("");
  $("#idproducto_agricultura").val("");
  $("#idproducto_proteccion").val("");
  $("#idproducto_repuestos").val("");

  $("#precio_unitario_utiles").val("");
  $("#precio_unitario_computo").val("");
  $("#precio_unitario_otros").val("");
  $("#precio_unitario_construccion").val("");
  $("#precio_unitario_uit").val("");
  $("#precio_unitario_agricultura").val("");
  $("#precio_unitario_proteccion").val("");
  $("#precio_unitario_repuestos").val("");

  // Resetear totales
  $("#cantidad_total").text("0");
  $("#precio_total").text("S/. 0.00");

  // Resetear todos los meses
  [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
  ].forEach(function (mes) {
    // Desactivar switches
    $(`#${mes}_switch`).prop("checked", false);
    $(`#${mes}_switch_utiles`).prop("checked", false);
    $(`#${mes}_switch_computo`).prop("checked", false);
    $(`#${mes}_switch_otros`).prop("checked", false);
    $(`#${mes}_switch_construccion`).prop("checked", false);
    $(`#${mes}_switch_uit`).prop("checked", false);
    $(`#${mes}_switch_agricultura`).prop("checked", false);
    $(`#${mes}_switch_proteccion`).prop("checked", false);
    $(`#${mes}_switch_repuestos`).prop("checked", false);
    // Limpiar valores de cantidad
    $(`#${mes}_cantidad`).val("");
    $(`#${mes}_cantidad_utiles`).val("");
    $(`#${mes}_cantidad_computo`).val("");
    $(`#${mes}_cantidad_otros`).val("");
    $(`#${mes}_cantidad_construccion`).val("");
    $(`#${mes}_cantidad_uit`).val("");
    $(`#${mes}_cantidad_agricultura`).val("");
    $(`#${mes}_cantidad_proteccion`).val("");
    $(`#${mes}_cantidad_repuestos`).val("");
  });

  $("#registerMaterialForm").on("reset", function () {
    $("#precio_unitario")
      .prop("readonly", true)
      .removeClass("editable-precio")
      .attr("placeholder", "")
      .val("");
  });

  $("#submitBtn").text("Guardar");
  $("#submitBtn_utiles").text("Guardar");
  $("#submitBtn_computo").text("Guardar");
  $("#submitBtn_otros").text("Guardar");
  $("#submitBtn_construccion").text("Guardar");
  $("#submitBtn_uit").text("Guardar");
  $("#submitBtn_agricultura").text("Guardar");
  $("#submitBtn_proteccion").text("Guardar");
  $("#submitBtn_repuestos").text("Guardar");

  // Remover los data-id de los formularios
  $("#registerMaterialForm").removeAttr("data-id");
  $("#registerMaterialForm_utiles").removeAttr("data-id");
  $("#registerMaterialForm_computo").removeAttr("data-id");
  $("#registerMaterialForm_otros").removeAttr("data-id");
  $("#registerMaterialForm_construccion").removeAttr("data-id");
  $("#registerMaterialForm_uit").removeAttr("data-id");
  $("#registerMaterialForm_agricultura").removeAttr("data-id");
  $("#registerMaterialForm_proteccion").removeAttr("data-id");
  $("#registerMaterialForm_repuestos").removeAttr("data-id");
}

function aplicarCantidadMasiva(tipo) {
  // Obtener el valor del input correcto según el tipo
  let cantidad = $(`#cantidad_masiva_${tipo}`).val();
  let inputPrefix;

  if (tipo === "") {
    // Caso especial para combustibles
    cantidad = $("#cantidad_masiva").val();
    inputPrefix = ""; // Para que use solo "_cantidad"
  } else {
    cantidad = $(`#cantidad_masiva_${tipo}`).val();
    inputPrefix = `_${tipo}`; // Para usar "_utiles", "_computo", etc.
  }

  if (!cantidad || parseFloat(cantidad) <= 0) {
    Swal.fire({
      icon: "error",
      title: "Cantidad inválida",
      text: "Por favor, ingrese una cantidad válida mayor a 0",
    });
    return;
  }

  Swal.fire({
    title: "¿Aplicar a todos los meses?",
    text: `Se aplicará la cantidad de ${cantidad} a todos los meses. ¿Desea continuar?`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, aplicar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      const meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];

      meses.forEach((mes) => {
        // Activar el switch y establecer la cantidad usando el prefijo correcto
        if (tipo === "") {
          // Para combustibles
          $(`#${mes}_switch`).prop("checked", true);
          $(`#${mes}_cantidad`).prop("disabled", false).val(cantidad);
        } else {
          // Para otros tipos
          $(`#${mes}_switch_${tipo}`).prop("checked", true);
          $(`#${mes}_cantidad_${tipo}`).prop("disabled", false).val(cantidad);
        }
      });

      // Actualizar totales según el tipo
      switch (tipo) {
        case "":
          calcularTotales();
          calcularTotalPresupuesto();
          break;
        case "utiles":
          calcularTotales_UtilesOficina();
          calcularTotalPresupuesto_UtilesOficina();
          break;
        case "computo":
          calcularTotales_EquiposComputo();
          calcularTotalPresupuesto_EquiposComputo();
          break;
        case "otros":
          calcularTotales_OtrosSuministros();
          calcularTotalPresupuesto_OtrosSuministros();
          break;
        case "construccion":
          calcularTotales_MaterialConstruccion();
          calcularTotalPresupuesto_MaterialConstruccion();
          break;
        case "agricultura":
          calcularTotales_MaterialAgricultura();
          calcularTotalPresupuesto_MaterialAgricultura();
          break;
        case "proteccion":
          calcularTotales_EquiposProteccion();
          calcularTotalPresupuesto_EquiposProteccion();
          break;
        case "repuestos":
          calcularTotales_RepuestosAccesorios();
          calcularTotalPresupuesto_RepuestosAccesorios();
          break;
        case "uit":
          calcularTotales_EquiposUIT();
          calcularTotalPresupuesto_EquiposUIT();
          break;
      }

      // Limpiar el input de cantidad masiva
      $(`#cantidad_masiva_${tipo}`).val("");

      Swal.fire({
        icon: "success",
        title: "Cantidades aplicadas",
        text: "Se han aplicado las cantidades a todos los meses correctamente",
        showConfirmButton: false,
        timer: 1500,
      });
    }
  });
}

// Función factory para inicializar presupuestos
function initPresupuesto(config) {
  const {
    tipo,
    selectorPrecio,
    selectorCantidad,
    urlEndpoint,
    totalSelector,
    statsSelector,
  } = config;

  return function () {
    const table = $(`#${tipo}Table`).DataTable({
      /* Config común...*/
    });

    // Función reusable para actualizar totales
    const actualizarTotales = () => {
      let cantidadTotal = 0;
      let precioTotal = 0;
      const precioUnitario = parseFloat($(selectorPrecio).val()) || 0;

      $(`.cantidad-mes-${tipo}`).each(function () {
        const mes = this.id.replace(`_cantidad_${tipo}`, "");
        if ($(`#${mes}_switch_${tipo}`).is(":checked")) {
          const cantidad = parseInt($(this).val()) || 0;
          cantidadTotal += cantidad;
          precioTotal += cantidad * precioUnitario;
        }
      });

      $(`#cantidad_total_${tipo}`).text(cantidadTotal);
      $(`#precio_total_${tipo}`).text(`S/${precioTotal.toFixed(2)}`);
    };

    // Eventos unificados
    $(selectorPrecio).on("input", actualizarTotales);
    $(`.cantidad-mes-${tipo}`).on("input", actualizarTotales);
    $(`input[type="checkbox"][id$="_switch_${tipo}"]`).on(
      "change",
      function () {
        const mesId = this.id.replace(`_switch_${tipo}`, "");
        $(`#${mesId}_cantidad_${tipo}`).prop("disabled", !this.checked);
        actualizarTotales();
      }
    );

    // AJAX reusable
    const calcularTotalPresupuesto = () => {
      return new Promise((resolve, reject) => {
        $.ajax({
          url: "/produccionuva2/produccionuva2_suministros_totals_dl/",
          type: "GET",
          dataType: "json",
          success: function (data) {
            $(totalSelector).text(
              formatearMonedaPEN(data[urlEndpoint] || "0.00")
            );
            $(statsSelector).text(
              formatearMonedaPEN(data[urlEndpoint] || "0.00")
            );
            actualizarConsolidadoMateriales();
            resolve();
          },
          error: function (xhr, status, error) {
            handleError(`Error al obtener total de ${tipo}`, error);
            reject(error);
          },
        });
      });
    };

    // Inicialización
    actualizarTotales();
    calcularTotalPresupuesto();
    actualizarConsolidadoMateriales();
  };
}

// Uso para cada tipo
const initConfigs = [
  {
    tipo: "utiles",
    selectorPrecio: "#precio_unitario_utiles",
    urlEndpoint: "TIC_utilesoficina",
    totalSelector: "#totalPresupuestoValor_utiles",
    statsSelector: "#stats_utilesoficina",
  },
  {
    tipo: "computo",
    selectorPrecio: "#precio_unitario_computo",
    urlEndpoint: "TIC_equiposcomputo",
    totalSelector: "#totalPresupuestoValor_computo",
    statsSelector: "#stats_equiposcomputo",
  },
  // ... Configuraciones para otros tipos
];

initConfigs.forEach((config) => {
  initPresupuesto(config)();
});

function createAutocomplete(config) {
  const { descripcionSelector, idProductoSelector, endpoint } = config;

  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: `/rrhh/${endpoint}/`,
          data: { term: request.term },
          success: function (data) {
            response(data.items);
          },
        });
      },
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);
        $(`${descripcionSelector}`).val(ui.item.label);
        return false;
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    const precioText = item.sin_precio_historico
      ? '<span class="badge bg-warning text-dark">Sin precio histórico</span>'
      : `<span class="badge bg-info">Último precio: S/ ${item.ultimo_precio.toFixed(
          2
        )}</span>`;

    return $("<li>")
      .append(
        `
      <div class="autocomplete-item">
        <div class="item-description">${item.label}</div>
        <div class="item-price">${precioText}</div>
      </div>
    `
      )
      .appendTo(ul);
  };
}

// Configuraciones de autocompletado
const autocompleteConfigs = [
  {
    descripcionSelector: "#descripcion_utiles",
    idProductoSelector: "#idproducto_utiles",
    endpoint: "autocomplete_utiles_oficina",
  },
  {
    descripcionSelector: "#descripcion_computo",
    idProductoSelector: "#idproducto_computo",
    endpoint: "autocomplete_equipos_computo",
  },
  // ... otras configuraciones
];

autocompleteConfigs.forEach(createAutocomplete);
