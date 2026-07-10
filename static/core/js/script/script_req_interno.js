// Variable global para la tabla
var table_show;

// Variables globales para datos del usuario
var datosUsuario = null;
var estadosPermitidos = [];
var permisoValidado = false;

// Variables globales para aprobación masiva
var registrosSeleccionados = [];
var estadoActualSeleccionado = null;

// =============================================
// FUNCIÓN PARA CARGAR ÁREAS
// =============================================
function cargarAreasReq() {
  $.get("/approve_almacen_areas", function (data) {
    $("#selectApproveAreaReq").append("<option value='0'>Todos</option>");
    console.log($("#selectApproveAreaReq").val());
    $.each(data, function (index, value) {
      $("#selectApproveAreaReq").append(
        "<option value='" +
          value["idareas"] +
          "'>" +
          value["areas"] +
          "</option>"
      );
    });

    // Después de cargar las áreas, inicializar la tabla automáticamente
    inicializarTablaReq();
  });
}

// =============================================
// FUNCIÓN PARA INICIALIZAR LA TABLA POR DEFECTO
// =============================================
function inicializarTablaReq() {
  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#panelSeleccionReq").hide();
  $("#btnAprobacionMasivaReq").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#tableApproveOrdersReq")) {
    $("#tableApproveOrdersReq").DataTable().destroy();
  }

  console.log("📊 Inicializando tabla de requerimientos internos");

  table_show = $("#tableApproveOrdersReq").DataTable({
    ajax: {
      url: "/req_interno_log_filter/0/", // 0 = Todas las áreas
      dataSrc: function (json) {
        console.log("📋 Datos recibidos del servidor:", json);
        if (json && json.length > 0) {
          console.log("📋 Primer elemento:", json[0]);
          console.log("📋 Campos del primer elemento:", {
            item: json[0].item,
            idorden: json[0].idorden,
            estado: json[0].estado,
            IDCONSUMIDOR: json[0].IDCONSUMIDOR,
          });
        }
        return json;
      },
    },
    searching: false,
    lengthChange: false,
    pageLength: 10,
    ordering: true,
    order: [[1, "desc"]],
    language: {
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      empty: "No se encontraron registros",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
    },
    columns: [
      { data: "idorden", visible: false },
      { data: "item" },
      { data: "fecha" },
      { data: "idmedida" },
      { data: "PRODUCTO" },
      { data: "cantidad" },
      { data: "observacion" },
      { data: "IDCONSUMIDOR" },
      { data: "areas" },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          // Solo mostrar checkbox para estados que se pueden aprobar
          var estado = row.estado ? row.estado.toLowerCase() : "";
          console.log(
            "🔍 Renderizando checkbox - Estado:",
            row.estado,
            "- Item:",
            row.item,
            "- ID Orden:",
            row.idorden
          );
          if (
            estado === "pe" ||
            estado === "pendiente" ||
            estado.includes("pendiente")
          ) {
            return (
              '<div class="form-check">' +
              '<input class="form-check-input row-checkbox-req" type="checkbox" ' +
              'value="' +
              row.idorden +
              '" data-estado="' +
              row.estado +
              '" data-debug="item=' +
              row.item +
              ",idorden=" +
              row.idorden +
              '">' +
              "</div>"
            );
          }
          return "";
        },
      },
    ],
    destroy: true,
    columnDefs: [
      {
        targets: "_all",
        createdCell: function (td, cellData, rowData, row, col) {
          // Agregar datos como atributos
          $(td).closest("tr").attr("data-item", rowData.item);
          $(td).closest("tr").attr("data-documento", rowData.documento);
        },
      },
    ],
    drawCallback: function () {
      // Configurar eventos de checkbox después de cada redibujado
      configurarEventosReqCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function filtrarPorAreaReq() {
  var area = $("#selectApproveAreaReq").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#panelSeleccionReq").hide();
  $("#btnAprobacionMasivaReq").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#tableApproveOrdersReq")) {
    $("#tableApproveOrdersReq").DataTable().destroy();
  }

  console.log("🔍 Filtrando área", area);

  table_show = $("#tableApproveOrdersReq").DataTable({
    ajax: {
      url: "/req_interno_log_filter/" + area + "/",
      dataSrc: function (json) {
        console.log("📋 Datos recibidos del servidor (filtro):", json);
        if (json && json.length > 0) {
          console.log("📋 Primer elemento (filtro):", json[0]);
        }
        return json;
      },
    },
    searching: false,
    lengthChange: false,
    pageLength: 10,
    ordering: true,
    order: [[1, "desc"]],
    language: {
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      empty: "No se encontraron registros",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
    },
    columns: [
      { data: "idorden", visible: false },
      { data: "item" },
      { data: "fecha" },
      { data: "idmedida" },
      { data: "PRODUCTO" },
      { data: "cantidad" },
      { data: "observacion" },
      { data: "IDCONSUMIDOR" },
      { data: "areas" },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          // Solo mostrar checkbox para estados que se pueden aprobar
          var estado = row.estado ? row.estado.toLowerCase() : "";
          console.log(
            "Estado del row filtro:",
            row.estado,
            "- Item:",
            row.item
          );
          if (
            estado === "pe" ||
            estado === "pendiente" ||
            estado.includes("pendiente")
          ) {
            return (
              '<div class="form-check">' +
              '<input class="form-check-input row-checkbox-req" type="checkbox" ' +
              'value="' +
              row.item +
              '" data-estado="' +
              row.estado +
              '">' +
              "</div>"
            );
          }
          return "";
        },
      },
    ],
    destroy: true,
    columnDefs: [
      {
        targets: "_all",
        createdCell: function (td, cellData, rowData, row, col) {
          // Agregar datos como atributos
          $(td).closest("tr").attr("data-item", rowData.item);
          $(td).closest("tr").attr("data-documento", rowData.documento);
        },
      },
    ],
    drawCallback: function () {
      // Configurar eventos de checkbox después de cada redibujado
      configurarEventosReqCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function configurarEventosReq() {
  // Remover event listeners anteriores para evitar duplicación
  $("#btnApproveFilterReq").off("click");
  $("#btnAprobacionMasivaReq").off("click");
  $("#btnSeleccionarTodosReq").off("click");
  $("#btnDeseleccionarTodosReq").off("click");

  // Evento del botón filtrar
  $("#btnApproveFilterReq").click(function () {
    filtrarPorAreaReq();
  });

  // Evento del botón de aprobación masiva
  $("#btnAprobacionMasivaReq").click(function () {
    ejecutarAprobacionMasivaReq();
  });

  // Eventos de los botones del panel de selección
  $("#btnSeleccionarTodosReq").click(function () {
    manejarSeleccionTodosReq(true);
  });

  $("#btnDeseleccionarTodosReq").click(function () {
    manejarSeleccionTodosReq(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function configurarSeleccionFilaReq() {
  // Remover event listeners anteriores para evitar duplicación
  $("#tableApproveOrdersReq tbody").off("dblclick");

  $("#tableApproveOrdersReq tbody").on("dblclick", "tr", function (e) {
    // Evitar que el doble clic active el checkbox
    if ($(e.target).is('input[type="checkbox"]')) {
      return;
    }

    var row = table_show.row(this).data();
    var idorden = row["idorden"]; // Usar idorden en lugar de item

    if (row["documento"] == "REQUERIMIENTOS INTERNOS") {
      abrirModalRequerimientoReq(idorden);
    } else if (row["documento"] == "SERVICIO") {
      abrirModalServicioReq(idorden);
    }

    // Configurar botones del modal
    configurarBotonesModalReq(idorden);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE REQUERIMIENTO
// =============================================
function abrirModalRequerimientoReq(idorden) {
  $("#modalApproveOrdersReq").modal("toggle");
  $.get("/req_interno_log_detail_purchase/" + idorden + "/", function (data) {
    $("#lblProveedorReq").html(data[0]["proveedor"]);
    $("#lblRucReq").html(data[0]["ruc"]);
    $("#lblCondicionReq").html(data[0]["formapago"]);
    $("#lblResponsableReq").html(data[0]["responsable"]);
    $("#lblTotalReq").html(data[0]["total_oc"]);
    $("#tableBodyApproveOrdersLogDetailReq").html("");
    $.each(data, function (index, value) {
      $("#tableApproveOrdersReqLogDetail").append(
        "<tr><td>" +
          value["idpedido"] +
          "</td><td>" +
          value["producto"] +
          "</td><td>" +
          value["idmedida"] +
          "</td><td>" +
          value["cantidad"] +
          "</td><td>" +
          value["consumidor"] +
          "</td></tr>"
      );
    });
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE SERVICIO
// =============================================
function abrirModalServicioReq(idorden) {
  $("#modalApproveOrdersReq").modal("toggle");
  $.get(
    "/approve_pservicios_log_detail_service-/" + idorden,
    function (data) {
      $("#tableBodyApproveOrdersLogDetailReq").html("");
      $.each(data, function (index, value) {
        $("#tableApproveOrdersReqLogDetail").append(
          "<tr><td>" +
            value["item"] +
            "</td><td>" +
            value["producto"] +
            "</td><td>" +
            value["idmedida"] +
            "</td><td>" +
            value["cantidad"] +
            "</td><td>" +
            value["precio_unitario"] +
            "</td><td>" +
            value["impuesto"] +
            "</td><td>" +
            parseFloat(value["total"]) +
            "</td></tr>"
        );
      });
    }
  );
}

// =============================================
// FUNCIÓN PARA CONFIGURAR BOTONES DEL MODAL
// =============================================
function configurarBotonesModalReq(idservicio) {
  // Remover event listeners anteriores
  $("#btn-aprobarReq").off("click");
  $("#btn-vbReq").off("click");
  $("#btn-anularReq").off("click");

  $("#btn-aprobarReq").click(function () {
    actualizarOrdenReq("aprobar", idservicio);
  });

  $("#btn-vbReq").click(function () {
    actualizarOrdenReq("vb", idservicio);
  });

  $("#btn-anularReq").click(function () {
    actualizarOrdenReq("anular", idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function actualizarOrdenReq(accion, idservicio) {
  // Realiza una solicitud AJAX al servidor para actualizar la orden de servicio
  $.ajax({
    url: "/actualizar-req-interno/" + idservicio + "/",
    type: "GET",
    data: { accion: accion },
    success: function (data) {
      $("#modalApproveOrdersReq").modal("hide");

      // Mostrar notificación de éxito
      Swal.fire({
        title: "¡Éxito!",
        text: "El requerimiento interno ha sido actualizado correctamente.",
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#28a745",
      });

      // Recargar tabla para mostrar cambios
      if (
        $("#selectApproveAreaReq").val() === "0" ||
        $("#selectApproveAreaReq").val() === null
      ) {
        inicializarTablaReq();
      } else {
        filtrarPorAreaReq();
      }
    },
    error: function (error) {
      console.error("Error al actualizar:", error);

      Swal.fire({
        title: "¡Error!",
        text: "Ocurrió un error al actualizar el requerimiento interno.",
        icon: "error",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#e74c3c",
      });
    },
  });
}

// =============================================
// FUNCIONES PARA APROBACIÓN MASIVA
// =============================================

// Función para actualizar contador de selección
function actualizarContadorSeleccionReq() {
  var cantidad = registrosSeleccionados.length;
  $("#contadorSeleccionReq").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#panelSeleccionReq").slideDown(300);
    $("#btnAprobacionMasivaReq").prop("disabled", false);
  } else {
    $("#panelSeleccionReq").slideUp(300);
    $("#btnAprobacionMasivaReq").prop("disabled", true);
    estadoActualSeleccionado = null;
  }
}

// Función para actualizar texto del botón según el estado
function actualizarTextoBtnMasivoReq(estado) {
  var texto = "";
  var icono = "";

  var estadoLower = estado ? estado.toLowerCase() : "";
  console.log(
    "🔧 Actualizando texto botón. Estado:",
    estado,
    "- Lower:",
    estadoLower
  );

  if (
    estadoLower === "pe" ||
    estadoLower === "pendiente" ||
    estadoLower.includes("pendiente")
  ) {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#btnAprobacionMasivaReq")
      .removeClass("btn-warning")
      .addClass("btn-success");
    console.log("✅ Configurando botón para aprobar");
  } else {
    console.log("❌ Estado no reconocido para botón:", estado);
  }

  $("#textoBtnMasivoReq").text(texto);
  $("#btnAprobacionMasivaReq i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
  console.log("🔧 Texto final del botón:", texto);
}

// Función para manejar selección individual
function manejarSeleccionIndividualReq(checkbox) {
  var $checkbox = $(checkbox);
  var idreqinterno = $checkbox.val(); // Cambiar nombre de variable para claridad
  var estado = $checkbox.data("estado");
  var $row = $checkbox.closest("tr");

  console.log("🔄 Manejo selección individual:", {
    idreqinterno: idreqinterno,
    valor_checkbox: $checkbox.val(),
    estado: estado,
    isChecked: $checkbox.is(":checked"),
  });

  if ($checkbox.is(":checked")) {
    // Agregar a seleccionados
    if (
      registrosSeleccionados.length === 0 ||
      estadoActualSeleccionado === estado
    ) {
      registrosSeleccionados.push({
        idorden: idreqinterno, // Mantener nombre idorden para consistencia con el resto del código
        estado: estado,
      });
      $row.addClass("row-selectedReq");

      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        console.log("🎯 Estableciendo estado actual:", estado);
        actualizarTextoBtnMasivoReq(estado);
      }
    } else {
      // Estados diferentes - no permitir selección
      $checkbox.prop("checked", false);
      Swal.fire({
        title: "⚠️ Selección no válida",
        text: "Solo puedes seleccionar registros del mismo estado para aprobación masiva.",
        icon: "warning",
        confirmButtonText: "Entendido",
        confirmButtonColor: "#f39c12",
      });
      return;
    }
  } else {
    // Remover de seleccionados
    registrosSeleccionados = registrosSeleccionados.filter(
      (item) => item.idorden !== idreqinterno
    );
    $row.removeClass("row-selectedReq");

    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = null;
    }
  }

  // Actualizar checkbox "Seleccionar Todos"
  var totalCheckboxes = $(".row-checkbox-req").length;
  var checkedCheckboxes = $(".row-checkbox-req:checked").length;

  if (checkedCheckboxes === 0) {
    $("#checkboxSelectAllReq").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#checkboxSelectAllReq").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#checkboxSelectAllReq").prop("checked", false).prop("indeterminate", true);
  }

  actualizarContadorSeleccionReq();
}

// Función para seleccionar/deseleccionar todos
function manejarSeleccionTodosReq(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $("#tableApproveOrdersReq .row-checkbox-req").each(function () {
    var $checkbox = $(this);
    var $row = $checkbox.closest("tr");

    if (seleccionar) {
      var idreqinterno = $checkbox.val(); // Cambiar nombre para claridad
      var estado = $checkbox.data("estado");

      console.log(
        "🔄 Seleccionando todos - ID:",
        idreqinterno,
        "Estado:",
        estado
      );

      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        actualizarTextoBtnMasivoReq(estado);
      }

      if (estadoActualSeleccionado === estado) {
        $checkbox.prop("checked", true);
        $row.addClass("row-selectedReq");
        registrosSeleccionados.push({
          idorden: idreqinterno, // Mantener nombre idorden para consistencia
          estado: estado,
        });
      }
    } else {
      $checkbox.prop("checked", false);
      $row.removeClass("row-selectedReq");
    }
  });

  $("#checkboxSelectAllReq")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  actualizarContadorSeleccionReq();
}

// Función para realizar aprobación masiva
function ejecutarAprobacionMasivaReq() {
  if (registrosSeleccionados.length === 0) {
    Swal.fire({
      title: "⚠️ Sin Selección",
      text: "Debes seleccionar al menos un registro para la aprobación masiva.",
      icon: "warning",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#f39c12",
    });
    return;
  }

  var accion = "";
  var textoConfirmacion = "";

  var estadoLower = estadoActualSeleccionado
    ? estadoActualSeleccionado.toLowerCase()
    : "";
  console.log(
    "🔄 Estado actual seleccionado:",
    estadoActualSeleccionado,
    "- Lower:",
    estadoLower
  );

  if (
    estadoLower === "pe" ||
    estadoLower === "pendiente" ||
    estadoLower.includes("pendiente")
  ) {
    accion = "aprobar";
    textoConfirmacion =
      "¿Estás seguro de que deseas APROBAR " +
      registrosSeleccionados.length +
      " requerimiento(s) interno(s) seleccionado(s)?";
  } else {
    Swal.fire({
      title: "⚠️ Estado no válido",
      text:
        "Estado de registro no reconocido para aprobación masiva. Estado actual: " +
        estadoActualSeleccionado,
      icon: "warning",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#f39c12",
    });
    return;
  }

  // Mostrar confirmación
  Swal.fire({
    title: "🔄 Confirmar Acción",
    text: textoConfirmacion,
    icon: "question",
    showCancelButton: true,
    confirmButtonText: "Sí, procesar",
    cancelButtonText: "Cancelar",
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
  }).then((result) => {
    if (result.isConfirmed) {
      procesarAprobacionMasivaReq(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function procesarAprobacionMasivaReq(accion) {
  var totalRegistros = registrosSeleccionados.length;
  var procesados = 0;
  var errores = 0;
  var errorDetails = [];

  // Mostrar progreso
  Swal.fire({
    title: "🔄 Procesando...",
    text: "Procesando " + totalRegistros + " registro(s). Por favor espera...",
    icon: "info",
    allowOutsideClick: false,
    showConfirmButton: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Procesar cada registro con delay para evitar sobrecarga del servidor
  var promesas = registrosSeleccionados.map(function (registro, index) {
    return new Promise(function (resolve) {
      setTimeout(function () {
        console.log(
          `🔄 Procesando registro ${index + 1}/${totalRegistros}: ID=${
            registro.idorden
          }`
        );
        $.ajax({
          url: "/actualizar-req-interno/" + registro.idorden + "/",
          type: "GET",
          data: { accion: accion },
          timeout: 10000,
          success: function (data) {
            console.log(
              `✅ Registro ${registro.idorden} procesado exitosamente:`,
              data
            );
            procesados++;
            resolve({ success: true, idorden: registro.idorden, data: data });
          },
          error: function (xhr, status, error) {
            console.error(`❌ Error procesando registro ${registro.idorden}:`, {
              status: status,
              error: error,
              responseText: xhr.responseText,
              statusCode: xhr.status,
            });
            errores++;
            errorDetails.push({
              idorden: registro.idorden,
              error: error,
              status: status,
              responseText: xhr.responseText,
              statusCode: xhr.status,
            });
            resolve({
              success: false,
              idorden: registro.idorden,
              error: error,
            });
          },
        });
      }, index * 500); // 500ms de delay entre cada request
    });
  });

  // Cuando todas las promesas se resuelvan
  Promise.all(promesas).then(function (resultados) {
    var exitosos = procesados;
    var fallidos = errores;

    console.log("📊 Resultados de aprobación masiva:");
    console.log("✅ Exitosos:", exitosos);
    console.log("❌ Fallidos:", fallidos);
    console.log("📋 Detalles de errores:", errorDetails);

    // Limpiar selecciones
    registrosSeleccionados = [];
    estadoActualSeleccionado = null;
    $("#panelSeleccionReq").hide();
    $("#btnAprobacionMasivaReq").prop("disabled", true);
    $(".row-checkbox-req").prop("checked", false);
    $("#checkboxSelectAllReq").prop("checked", false).prop("indeterminate", false);
    $(".row-selectedReq").removeClass("row-selectedReq");

    // Recargar tabla
    if (
      $("#selectApproveAreaReq").val() === "0" ||
      $("#selectApproveAreaReq").val() === null
    ) {
      inicializarTablaReq();
    } else {
      filtrarPorAreaReq();
    }

    // Mostrar resultado final
    if (fallidos === 0) {
      Swal.fire({
        title: "¡Proceso Completado!",
        text:
          "Se procesaron exitosamente " +
          exitosos +
          " requerimiento(s) interno(s).",
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#28a745",
      });
    } else if (exitosos === 0) {
      Swal.fire({
        title: "❌ Error en el Proceso",
        text: "No se pudo procesar ningún requerimiento. Revisa la conexión e intenta nuevamente.",
        icon: "error",
        confirmButtonText: "Entendido",
        confirmButtonColor: "#e74c3c",
      });
    } else {
      var detallesError = "";
      if (errorDetails.length > 0) {
        detallesError = "<br><br><small>Errores encontrados:<br>";
        errorDetails.slice(0, 3).forEach(function (error) {
          detallesError += `• ID ${error.idorden}: ${error.error}<br>`;
        });
        if (errorDetails.length > 3) {
          detallesError += `• Y ${
            errorDetails.length - 3
          } error(es) más...<br>`;
        }
        detallesError += "</small>";
      }

      Swal.fire({
        title: "⚠️ Proceso Parcial",
        html:
          "Se procesaron <b>" +
          exitosos +
          "</b> requerimiento(s) exitosamente.<br>" +
          "Fallaron <b>" +
          fallidos +
          "</b> requerimiento(s).<br><br>" +
          "Revisa los requerimientos restantes manualmente." +
          detallesError,
        icon: "warning",
        confirmButtonText: "Entendido",
        confirmButtonColor: "#f39c12",
      });
    }
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function configurarEventosReqCheckbox() {
  // Remover event listeners anteriores para evitar duplicación
  $(".row-checkbox-req").off("change");
  $("#checkboxSelectAllReq").off("change");

  // Evento para checkboxes individuales
  $(".row-checkbox-req").change(function () {
    manejarSeleccionIndividualReq(this);
  });

  // Evento para checkbox "Seleccionar Todos"
  $("#checkboxSelectAllReq").change(function () {
    var isChecked = $(this).is(":checked");
    manejarSeleccionTodosReq(isChecked);
  });
}




// =============================================
// INIT PARA USO EN TABS/PARTIALS (NO AUTOEJECUTA)
// Llama esto DESPUÉS de inyectar el partial en el DOM.
// Ejemplo: window.initRequerimientoModule();
// =============================================
window.initRequerimientoModule = function () {
  console.log("🚀 Inicializando requerimiento (modo TAB/PARTIAL)");

  // Carga combos / data inicial
  cargarAreasReq();

  // Binds (tus .off() evitan duplicados)
  configurarEventosReq();
  configurarSeleccionFilaReq();

  // Carga inicial de tabla (usa filtro por área por defecto)
  // filtrarPorAreaReq();
};
