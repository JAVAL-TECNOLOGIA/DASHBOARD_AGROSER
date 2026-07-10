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
function cargarAreas(callback) {
  // Evita recargar si ya se llenó el combo
  if ($("#selectApproveArea").data("loaded") === true) {
    if (typeof callback === "function") callback();
    return;
  }

  $.get("/approve_almacen_areas", function (data) {
    $("#selectApproveArea").empty();
    $("#selectApproveArea").append("<option value='0'>Todos</option>");

    $.each(data, function (index, value) {
      $("#selectApproveArea").append(
        "<option value='" +
          value["idareas"] +
          "'>" +
          value["areas"] +
          "</option>"
      );
    });

    $("#selectApproveArea").data("loaded", true);

    if (typeof callback === "function") callback();
  });
}


// =============================================
// FUNCIÓN PARA INICIALIZAR LA TABLA POR DEFECTO
// =============================================
function inicializarTabla() {
  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#panelSeleccion").hide();
  $("#btnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#tableApproveOrders")) {
    $("#tableApproveOrders").DataTable().destroy();
  }

  console.log("📊 Inicializando tabla de requerimientos internos");

  table_show = $("#tableApproveOrders").DataTable({
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
              '<input class="form-check-input row-checkbox" type="checkbox" ' +
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
      configurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function filtrarPorArea() {
  var area = $("#selectApproveArea").val() || 0;

  // Guard: la tabla debe existir y estar visible (en tabs/partials)
  var $table = $("#tableApproveOrders");
  if ($table.length === 0) {
    console.warn("⚠️ #tableApproveOrders no existe aún en el DOM.");
    return;
  }
  if ($table.is(":hidden")) {
    console.warn("⏳ Tabla está oculta (tab no visible). Reintentando...");
    setTimeout(filtrarPorArea, 80);
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#panelSeleccion").hide();
  $("#btnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#tableApproveOrders")) {
    $("#tableApproveOrders").DataTable().destroy();
  }

  console.log("🔍 Filtrando área", area);

  table_show = $("#tableApproveOrders").DataTable({
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
              '<input class="form-check-input row-checkbox" type="checkbox" ' +
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
      configurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function configurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#btnApproveFilter").off("click");
  $("#btnAprobacionMasiva").off("click");
  $("#btnSeleccionarTodos").off("click");
  $("#btnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#btnApproveFilter").click(function () {
    filtrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#btnAprobacionMasiva").click(function () {
    ejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#btnSeleccionarTodos").click(function () {
    manejarSeleccionTodos(true);
  });

  $("#btnDeseleccionarTodos").click(function () {
    manejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function configurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#tableApproveOrders tbody").off("dblclick");

  $("#tableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Evitar que el doble clic active el checkbox
    if ($(e.target).is('input[type="checkbox"]')) {
      return;
    }

    var row = table_show.row(this).data();
    var idorden = row["idorden"]; // Usar idorden en lugar de item

    if (row["documento"] == "REQUERIMIENTOS INTERNOS") {
      abrirModalRequerimiento(idorden);
    } else if (row["documento"] == "SERVICIO") {
      abrirModalServicio(idorden);
    }

    // Configurar botones del modal
    configurarBotonesModal(idorden);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE REQUERIMIENTO
// =============================================
function abrirModalRequerimiento(idorden) {
  $("#modalApproveOrders").modal("toggle");
  $.get("/req_interno_log_detail_purchase/" + idorden + "/", function (data) {
    $("#lblProveedor").html(data[0]["proveedor"]);
    $("#lblRuc").html(data[0]["ruc"]);
    $("#lblCondicion").html(data[0]["formapago"]);
    $("#lblResponsable").html(data[0]["responsable"]);
    $("#lblTotal").html(data[0]["total_oc"]);
    $("#tableBodyApproveOrdersLogDetail").html("");
    $.each(data, function (index, value) {
      $("#tableApproveOrdersLogDetail").append(
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
function abrirModalServicio(idorden) {
  $("#modalApproveOrders").modal("toggle");
  $.get(
    "/approve_pservicios_log_detail_service-/" + idorden,
    function (data) {
      $("#tableBodyApproveOrdersLogDetail").html("");
      $.each(data, function (index, value) {
        $("#tableApproveOrdersLogDetail").append(
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
function configurarBotonesModal(idservicio) {
  // Remover event listeners anteriores
  $("#btn-aprobar").off("click");
  $("#btn-vb").off("click");
  $("#btn-anular").off("click");

  $("#btn-aprobar").click(function () {
    actualizarOrden("aprobar", idservicio);
  });

  $("#btn-vb").click(function () {
    actualizarOrden("vb", idservicio);
  });

  $("#btn-anular").click(function () {
    actualizarOrden("anular", idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function actualizarOrden(accion, idservicio) {
  // Realiza una solicitud AJAX al servidor para actualizar la orden de servicio
  $.ajax({
    url: "/actualizar-req-interno/" + idservicio + "/",
    type: "GET",
    data: { accion: accion },
    success: function (data) {
      $("#modalApproveOrders").modal("hide");

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
        $("#selectApproveArea").val() === "0" ||
        $("#selectApproveArea").val() === null
      ) {
        inicializarTabla();
      } else {
        filtrarPorArea();
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
function actualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#contadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#panelSeleccion").slideDown(300);
    $("#btnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#panelSeleccion").slideUp(300);
    $("#btnAprobacionMasiva").prop("disabled", true);
    estadoActualSeleccionado = null;
  }
}

// Función para actualizar texto del botón según el estado
function actualizarTextoBtnMasivo(estado) {
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
    $("#btnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
    console.log("✅ Configurando botón para aprobar");
  } else {
    console.log("❌ Estado no reconocido para botón:", estado);
  }

  $("#textoBtnMasivo").text(texto);
  $("#btnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
  console.log("🔧 Texto final del botón:", texto);
}

// Función para manejar selección individual
function manejarSeleccionIndividual(checkbox) {
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
        actualizarTextoBtnMasivo(estado);
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
  var totalCheckboxes = $(".row-checkbox").length;
  var checkedCheckboxes = $(".row-checkbox:checked").length;

  if (checkedCheckboxes === 0) {
    $("#checkboxSelectAll").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#checkboxSelectAll").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#checkboxSelectAll").prop("checked", false).prop("indeterminate", true);
  }

  actualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function manejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox").each(function () {
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
        actualizarTextoBtnMasivo(estado);
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

  $("#checkboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  actualizarContadorSeleccion();
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
    $("#panelSeleccion").hide();
    $("#btnAprobacionMasiva").prop("disabled", true);
    $(".row-checkbox").prop("checked", false);
    $("#checkboxSelectAll").prop("checked", false).prop("indeterminate", false);
    $(".row-selected").removeClass("row-selected");

    // Recargar tabla
    if (
      $("#selectApproveArea").val() === "0" ||
      $("#selectApproveArea").val() === null
    ) {
      inicializarTabla();
    } else {
      filtrarPorArea();
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
function configurarEventosCheckbox() {
  // Remover event listeners anteriores para evitar duplicación
  $(".row-checkbox").off("change");
  $("#checkboxSelectAll").off("change");

  // Evento para checkboxes individuales
  $(".row-checkbox").change(function () {
    manejarSeleccionIndividual(this);
  });

  // Evento para checkbox "Seleccionar Todos"
  $("#checkboxSelectAll").change(function () {
    var isChecked = $(this).is(":checked");
    manejarSeleccionTodos(isChecked);
  });
}




// =============================================
// INIT PARA USO EN TABS/PARTIALS (NO AUTOEJECUTA)
// Llama esto DESPUÉS de inyectar el partial en el DOM.
// Ejemplo: window.initFitosanidadModule();
// =============================================
window.initRequerimientoModule2 = function () {
  console.log("🚀 Inicializando requerimiento (modo TAB/PARTIAL)");

  // 1) Cargar áreas (async) y luego bindear eventos + cargar tabla
  cargarAreas(function () {
    // Binds (tus .off() evitan duplicados)
    configurarEventos();
    configurarSeleccionFila();

    // 2) Inicializa DataTable cuando el tab ya está visible (evita error de widths)
    setTimeout(function () {
      filtrarPorArea();

      // 3) Forzar recalculo de anchos luego de render
      setTimeout(function () {
        if ($.fn.DataTable.isDataTable("#tableApproveOrders2")) {
          var dt = $("#tableApproveOrders2").DataTable();
          dt.columns.adjust();
          if (dt.responsive && typeof dt.responsive.recalc === "function") {
            dt.responsive.recalc();
          }
        }
      }, 0);
    }, 50);
  });
};

