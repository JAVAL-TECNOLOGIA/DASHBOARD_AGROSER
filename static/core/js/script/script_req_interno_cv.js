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
function CVREQcargarAreas() {
  $.get("/approve_almacen_areas", function (data) {
    $("#CVREQselectApproveArea").append("<option value='0'>Todos</option>");
    console.log($("#CVREQselectApproveArea").val());
    $.each(data, function (index, value) {
      $("#CVREQselectApproveArea").append(
        "<option value='" +
          value["idareas"] +
          "'>" +
          value["areas"] +
          "</option>"
      );
    });

    // Después de cargar las áreas, inicializar la tabla automáticamente
    CVREQinicializarTabla();
  });
}

// =============================================
// FUNCIÓN PARA INICIALIZAR LA TABLA POR DEFECTO
// =============================================
function CVREQinicializarTabla() {
  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#CVREQpanelSeleccion").hide();
  $("#CVREQbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#CVREQtableApproveOrders")) {
    $("#CVREQtableApproveOrders").DataTable().destroy();
  }

  console.log("📊 Inicializando tabla de requerimientos internos");

  table_show = $("#CVREQtableApproveOrders").DataTable({
    ajax: {
      url: "/req_interno_log_filter_cv/0/", // 0 = Todas las áreas
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
              '<input class="form-check-input row-checkbox-REQCV" type="checkbox" ' +
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
      CVREQconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function CVREQfiltrarPorArea() {
  var area = $("#CVREQselectApproveArea").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#CVREQpanelSeleccion").hide();
  $("#CVREQbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#CVREQtableApproveOrders")) {
    $("#CVREQtableApproveOrders").DataTable().destroy();
  }

  console.log("🔍 Filtrando área", area);

  table_show = $("#CVREQtableApproveOrders").DataTable({
    ajax: {
      url: "/req_interno_log_filter_cv/" + area + "/",
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
              '<input class="form-check-input row-checkbox-REQCV" type="checkbox" ' +
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
      CVREQconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function CVREQconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#CVREQbtnApproveFilter").off("click");
  $("#CVREQbtnAprobacionMasiva").off("click");
  $("#CVREQbtnSeleccionarTodos").off("click");
  $("#CVREQbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#CVREQbtnApproveFilter").click(function () {
    CVREQfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#CVREQbtnAprobacionMasiva").click(function () {
    ejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#CVREQbtnSeleccionarTodos").click(function () {
    CVREQmanejarSeleccionTodos(true);
  });

  $("#CVREQbtnDeseleccionarTodos").click(function () {
    CVREQmanejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function CVREQconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#CVREQtableApproveOrders tbody").off("dblclick");

  $("#CVREQtableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Evitar que el doble clic active el checkbox
    if ($(e.target).is('input[type="checkbox"]')) {
      return;
    }

    var row = table_show.row(this).data();
    var idorden = row["idorden"]; // Usar idorden en lugar de item

    if (row["documento"] == "REQUERIMIENTOS INTERNOS") {
      CVREQabrirModalRequerimiento(idorden);
    } else if (row["documento"] == "SERVICIO") {
      CVREQabrirModalServicio(idorden);
    }

    // Configurar botones del modal
    CVREQconfigurarBotonesModal(idorden);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE REQUERIMIENTO
// =============================================
function CVREQabrirModalRequerimiento(idorden) {
  $("#CVREQmodalApproveOrders").modal("toggle");
  $.get(
    "/req_interno_log_detail_purchase_cv/" + idorden + "/",
    function (data) {
      $("#CVREQlblProveedor").html(data[0]["proveedor"]);
      $("#CVREQlblRuc").html(data[0]["ruc"]);
      $("#CVREQlblCondicion").html(data[0]["formapago"]);
      $("#CVREQlblResponsable").html(data[0]["responsable"]);
      $("#CVREQlblTotal").html(data[0]["total_oc"]);
      $("#CVREQtableBodyApproveOrdersLogDetail").html("");
      $.each(data, function (index, value) {
        $("#CVREQtableApproveOrdersLogDetail").append(
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
    }
  );
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE SERVICIO
// =============================================
function CVREQabrirModalServicio(idorden) {
  $("#CVREQmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_pservicios_log_detail_service-/" + idorden,
    function (data) {
      $("#CVREQtableBodyApproveOrdersLogDetail").html("");
      $.each(data, function (index, value) {
        $("#CVREQtableApproveOrdersLogDetail").append(
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
function CVREQconfigurarBotonesModal(idservicio) {
  // Remover event listeners anteriores
  $("#CVREQbtn-aprobar").off("click");
  $("#CVREQbtn-vb").off("click");
  $("#CVREQbtn-anular").off("click");

  $("#CVREQbtn-aprobar").click(function () {
    CVREQactualizarOrden("aprobar", idservicio);
  });

  $("#CVREQbtn-vb").click(function () {
    CVREQactualizarOrden("vb", idservicio);
  });

  $("#CVREQbtn-anular").click(function () {
    CVREQactualizarOrden("anular", idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function CVREQactualizarOrden(accion, idservicio) {
  // Realiza una solicitud AJAX al servidor para actualizar la orden de servicio
  $.ajax({
    url: "/actualizar-req-interno-cv/" + idservicio + "/",
    type: "GET",
    data: { accion: accion },
    success: function (data) {
      $("#CVREQmodalApproveOrders").modal("hide");

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
        $("#CVREQselectApproveArea").val() === "0" ||
        $("#CVREQselectApproveArea").val() === null
      ) {
        CVREQinicializarTabla();
      } else {
        CVREQfiltrarPorArea();
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
function CVREQactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#CVREQcontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#CVREQpanelSeleccion").slideDown(300);
    $("#CVREQbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#CVREQpanelSeleccion").slideUp(300);
    $("#CVREQbtnAprobacionMasiva").prop("disabled", true);
    estadoActualSeleccionado = null;
  }
}

// Función para actualizar texto del botón según el estado
function CVREQactualizarTextoBtnMasivo(estado) {
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
    $("#CVREQbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
    console.log("✅ Configurando botón para aprobar");
  } else {
    console.log("❌ Estado no reconocido para botón:", estado);
  }

  $("#CVREQtextoBtnMasivo").text(texto);
  $("#CVREQbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
  console.log("🔧 Texto final del botón:", texto);
}

// Función para manejar selección individual
function CVREQmanejarSeleccionIndividual(checkbox) {
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
      $row.addClass("row-selected");

      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        console.log("🎯 Estableciendo estado actual:", estado);
        CVREQactualizarTextoBtnMasivo(estado);
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
    $row.removeClass("row-selected");

    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = null;
    }
  }

  // Actualizar checkbox "Seleccionar Todos"
  var totalCheckboxes = $(".row-checkbox-REQCV").length;
  var checkedCheckboxes = $(".row-checkbox-REQCV:checked").length;

  if (checkedCheckboxes === 0) {
    $("#CVREQcheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#CVREQcheckboxSelectAll").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#CVREQcheckboxSelectAll").prop("checked", false).prop("indeterminate", true);
  }

  CVREQactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function CVREQmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-REQCV").each(function () {
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
        CVREQactualizarTextoBtnMasivo(estado);
      }

      if (estadoActualSeleccionado === estado) {
        $checkbox.prop("checked", true);
        $row.addClass("row-selected");
        registrosSeleccionados.push({
          idorden: idreqinterno, // Mantener nombre idorden para consistencia
          estado: estado,
        });
      }
    } else {
      $checkbox.prop("checked", false);
      $row.removeClass("row-selected");
    }
  });

  $("#CVREQcheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  CVREQactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function ejecutarAprobacionMasiva() {
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
      procesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function procesarAprobacionMasiva(accion) {
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
          url: "/actualizar-req-interno-cv/" + registro.idorden + "/",
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
    $("#CVREQpanelSeleccion").hide();
    $("#CVREQbtnAprobacionMasiva").prop("disabled", true);
    $(".row-checkbox-REQCV").prop("checked", false);
    $("#CVREQcheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
    $(".row-selected").removeClass("row-selected");

    // Recargar tabla
    if (
      $("#CVREQselectApproveArea").val() === "0" ||
      $("#CVREQselectApproveArea").val() === null
    ) {
      CVREQinicializarTabla();
    } else {
      CVREQfiltrarPorArea();
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
function CVREQconfigurarEventosCheckbox() {
  // Remover event listeners anteriores para evitar duplicación
  $(".row-checkbox-REQCV").off("change");
  $("#CVREQcheckboxSelectAll").off("change");

  // Evento para checkboxes individuales
  $(".row-checkbox-REQCV").change(function () {
    CVREQmanejarSeleccionIndividual(this);
  });

  // Evento para checkbox "Seleccionar Todos"
  $("#CVREQcheckboxSelectAll").change(function () {
    var isChecked = $(this).is(":checked");
    CVREQmanejarSeleccionTodos(isChecked);
  });
}

// =============================================
// INICIALIZACIÓN CUANDO EL DOCUMENTO ESTÉ LISTO
// =============================================
window.initRequerimientoCVModule = function () {
  console.log("🚀 Inicializando requerimiento (modo TAB/PARTIAL)");

  // Carga combos / data inicial
  CVREQcargarAreas();

  // Binds (tus .off() evitan duplicados)
  CVREQconfigurarEventos();
  CVREQconfigurarSeleccionFila();

  // Carga inicial de tabla (usa filtro por área por defecto)
  // CVREQfiltrarPorAreaReq();
};