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
// FUNCIÓN PARA VALIDAR PERMISOS SEGÚN CARGO
// =============================================
function PCvalidarPermisosPorCargo(idCargo) {
  switch (parseInt(idCargo)) {
    case 8:
      // IDCARGO 8: Administrador/Gerencia - Puede ver PENDIENTE
      estadosPermitidos = ["PE"];
      permisoValidado = true;
      console.log("✅ Usuario con IDCARGO 8: Permisos para estados PENDIENTE");
      return true;

    case 7:
    case 6:
      // IDCARGO 7 y 6: Coordinadores - Pueden ver PENDIENTE
      estadosPermitidos = ["PE"];
      permisoValidado = true;
      console.log(
        "✅ Usuario con IDCARGO",
        idCargo + ": Permisos para estados PENDIENTE"
      );
      return true;

    default:
      // Cualquier otro IDCARGO: Sin permisos
      estadosPermitidos = [];
      permisoValidado = false;
      console.warn(
        "⚠️ Usuario con IDCARGO",
        idCargo + ": Sin permisos para ver registros"
      );

      // Mostrar notificación al usuario
      Swal.fire({
        title: "⚠️ Sin Permisos",
        text: "No tienes permisos para visualizar los registros. Consulta con el área TIC para obtener acceso.",
        icon: "warning",
        confirmButtonText: "Entendido",
        confirmButtonColor: "#f39c12",
      });

      return false;
  }
}

// =============================================
// FUNCIÓN PARA OBTENER URL CON FILTRO DE ESTADOS
// =============================================
function PCobtenerUrlConEstados(area) {
  if (!permisoValidado || estadosPermitidos.length === 0) {
    // Si no hay permisos, retornar URL que no devuelva datos
    return "/approve_almacen_log_filter/" + area + "/SINPERMISOS/";
  }

  // Para almacén solo manejamos estado PE (PENDIENTE)
  return "/approve_almacen_log_filter/" + area + "/";
}

// =============================================
// FUNCIÓN PARA CARGAR ÁREAS
// =============================================
function PCcargarAreas() {
  $.get("/approve_almacen_areas", function (data) {
    $("#PCselectApproveArea").append("<option value='0'>Todos</option>");
    $.each(data, function (index, value) {
      $("#PCselectApproveArea").append(
        "<option value='" +
          value["idarea"] +
          "'>" +
          value["descripcion"] +
          "</option>"
      );
    });
  });
}

// =============================================
// FUNCIÓN PARA INICIALIZAR LA TABLA POR DEFECTO
// =============================================
function PCinicializarTabla() {
  // Validar permisos antes de cargar datos
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden cargar datos: permisos no validados");
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#PCpanelSeleccion").hide();
  $("#PCbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#PCtableApproveOrders")) {
    $("#PCtableApproveOrders").DataTable().clear().destroy();
    $("#PCtableApproveOrders tbody").empty();
  }

  var urlConEstados = PCobtenerUrlConEstados(0); // 0 = Todas las áreas

  console.log("📊 Inicializando tabla con URL:", urlConEstados);

  table_show = $("#PCtableApproveOrders").DataTable({
    ajax: {
      url: urlConEstados,
      dataSrc: "",
    },
    searching: false,
    lengthChange: false,
    pageLength: 10,
    ordering: true,
    order: [[1, "desc"]], // Ordenar por item (columna 0)
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
      { data: "item" }, // 0 - Item
      { data: "fecha" }, // 2 - Fecha
      { data: "moneda" }, // 5 - Moneda
      { data: "total" }, // 6 - Importe
      { data: "idmedida" },
      { data: "descripcion" },
      { data: "cantidad" },
      { data: "nota" },
      { data: "idconsumidor" },
      { data: "area" }, // 7 - Área
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-PC" value="' +
            row.idorden +
            '" data-estado="' +
            row.estado +
            '">' +
            "</div>"
          );
        },
      }, // 8               // 8 - Checkbox
    ],
    destroy: true,
    columnDefs: [
      {
        targets: "_all",
        createdCell: function (td, cellData, rowData, row, col) {
          // Agregar los datos ocultos como atributos data
          $(td).closest("tr").attr("data-idorden", rowData.idorden);
          $(td).closest("tr").attr("data-documento", rowData.documento);
        },
      },
    ],
    drawCallback: function () {
      // Configurar eventos de checkbox después de cada redibujado
      PCconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function PCfiltrarPorArea() {
  // Validar permisos antes de filtrar
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden filtrar datos: permisos no validados");
    Swal.fire({
      title: "⚠️ Sin Permisos",
      text: "No tienes permisos para visualizar los registros.",
      icon: "warning",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#f39c12",
    });
    return;
  }

  var area = $("#PCselectApproveArea").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#PCpanelSeleccion").hide();
  $("#PCbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#PCtableApproveOrders")) {
    $("#PCtableApproveOrders").DataTable().clear().destroy();
    $("#PCtableApproveOrders tbody").empty();
  }

  var urlConEstados = PCobtenerUrlConEstados(area);

  console.log("🔍 Filtrando área", area, "con URL:", urlConEstados);

  table_show = $("#PCtableApproveOrders").DataTable({
    ajax: {
      url: urlConEstados,
      dataSrc: "",
    },
    searching: false,
    lengthChange: false,
    pageLength: 10,
    ordering: true,
    order: [[1, "desc"]], // Ordenar por item (columna 0)
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
      { data: "item" }, // 0 - Item
      { data: "fecha" }, // 2 - Fecha
      { data: "moneda" }, // 5 - Moneda
      { data: "total" }, // 6 - Importe
      { data: "idmedida" },
      { data: "descripcion" },
      { data: "cantidad" },
      { data: "nota" },
      { data: "idconsumidor" },
      { data: "area" }, // 7 - Área
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-PC" value="' +
            row.idorden +
            '" data-estado="' +
            row.estado +
            '">' +
            "</div>"
          );
        },
      }, // 8 - Checkbox
    ],
    destroy: true,
    columnDefs: [
      {
        targets: "_all",
        createdCell: function (td, cellData, rowData, row, col) {
          // Agregar los datos ocultos como atributos data
          $(td).closest("tr").attr("data-idorden", rowData.idorden);
          $(td).closest("tr").attr("data-documento", rowData.documento);
        },
      },
    ],
    drawCallback: function () {
      // Configurar eventos de checkbox después de cada redibujado
      PCconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function PCconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#PCbtnApproveFilter").off("click");
  $("#PCbtnAprobacionMasiva").off("click");
  $("#PCbtnSeleccionarTodos").off("click");
  $("#PCbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#PCbtnApproveFilter").click(function () {
    PCfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#PCbtnAprobacionMasiva").click(function () {
    PCejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#PCbtnSeleccionarTodos").click(function () {
    PCmanejarSeleccionTodos(true);
  });

  $("#PCbtnDeseleccionarTodos").click(function () {
    PCmanejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function PCconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#PCtableApproveOrders tbody").off("dblclick");

  $("#PCtableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Prevenir el doble click si se hizo click en un checkbox
    if (
      $(e.target).hasClass("form-check-input") ||
      $(e.target).closest(".form-check").length > 0
    ) {
      return;
    }

    console.log('dblclick PCtableApproveOrders tbody')

    var row = table_show.row(this).data();
    var $tr = $(this);

    // Obtener los datos desde los atributos data o desde row data
    var idorden = $tr.attr("data-idorden") || row["idorden"];
    var documento = $tr.attr("data-documento") || row["documento"];

    // Remover event listeners anteriores de los botones para evitar duplicación
    $("#PCbtn-aprobar").off("click");

    if (documento == "COMPRA") {
      PCabrirModalCompra(idorden);
    } else if (documento == "SERVICIO") {
      PCabrirModalServicio(idorden);
    }

    // Configurar botones del modal
    PCconfigurarBotonesModal(idorden);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE COMPRA
// =============================================
function PCabrirModalCompra(idorden) {
  $("#PCmodalApproveOrders").modal("show");
  $.get(
    "/approve_almacen_log_detail_purchase/" + idorden + "/",
    function (data) {
      $("#PClblArea").html(data[0]["area"]);
      $("#PClblObservacion").html(data[0]["observacion"]);
      $("#PClblEstado").html(data[0]["estado"]);
      $("#PClblResponsable").html(data[0]["responsable"]);
      $("#PClblTotal").html("N/A"); // No hay total en esta vista
      $("#PCtableBodyApproveOrdersLogDetail").html("");
      $.each(data, function (index, value) {
        $("#PCtableBodyApproveOrdersLogDetail").append(
          "<tr><td>" +
            value["idproducto"] +
            "</td><td>" +
            value["producto"] +
            "</td><td>" +
            value["idmedida"] +
            "</td><td>" +
            value["cantidad"] +
            "</td><td>" +
            "-" + // No hay total individual
            "</td></tr>"
        );
      });
    }
  );
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE SERVICIO
// =============================================
function PCabrirModalServicio(idorden) {
  $("#PCmodalApproveOrders").modal("show");
  $.get("/approve_orders_log_detail_service/" + idorden, function (data) {
    $("#PClblArea").html(data[0]["area"]);
    $("#PClblEstado").html(data[0]["estado"]);
    $("#PClblObservacion").html(data[0]["observacion"]);
    $("#PClblResponsable").html(data[0]["responsable"]);
    $("#PClblTotal").html(data[0]["total_os"]);
    $("#PCtableBodyApproveOrdersLogDetail").html("");
    $.each(data, function (index, value) {
      $("#PCtableApproveOrdersLogDetail").append(
        "<tr><td>" +
          value["idproducto"] +
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
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR BOTONES DEL MODAL
// =============================================
function PCconfigurarBotonesModal(idorden) {
    console.log('llega PCconfigurarBotonesModal');
  $("#PCbtn-aprobar").click(function () {
    PCactualizarOrden("aprobar", idorden);
  });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function PCactualizarOrden(accion, idorden) {
  $.ajax({
    url: "/actualizar-orden-almacen/" + idorden + "/",
    type: "GET",
    data: { accion: accion },
    timeout: 15000, // 15 segundos de timeout
    success: function (data, textStatus, xhr) {
      console.log("✅ Orden actualizada correctamente:", idorden);
      console.log("Respuesta del servidor:", data);
      console.log("Status HTTP:", xhr.status);

      // Verificar si la respuesta es JSON con success: true
      let mensaje = "El Pedido de Almacén ha sido actualizado exitosamente.";

      if (typeof data === "object" && data.success) {
        mensaje = data.message || mensaje;
      } else if (typeof data === "string") {
        // Si la respuesta es string, usar mensaje por defecto
        mensaje = "El Pedido de Almacén ha sido actualizado exitosamente.";
      }

      Swal.fire({
        title: "¡Éxito!",
        text: mensaje,
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#3085d6",
      });

      // Recargar tabla solo después de completar la acción individual
      PCinicializarTabla();
      $("#PCmodalApproveOrders").modal("hide");
    },
    error: function (xhr, status, error) {
      console.error("❌ Error al actualizar orden:", idorden);
      console.error("Status:", status);
      console.error("Error:", error);
      console.error("Response:", xhr.responseText);
      console.error("Status HTTP:", xhr.status);

      var mensaje = "Ocurrió un error al actualizar el pedido de almacén.";

      if (status === "timeout") {
        mensaje =
          "La operación tardó demasiado tiempo. Por favor, verifica el estado del pedido e intenta nuevamente.";
      } else if (xhr.status === 500) {
        mensaje =
          "Error interno del servidor. Contacta al administrador del sistema.";
      } else if (xhr.status === 404) {
        mensaje = "No se encontró el pedido especificado.";
      } else if (xhr.responseText) {
        try {
          var response = JSON.parse(xhr.responseText);
          if (response.error) {
            mensaje = response.error;
          }
        } catch (e) {
          // Si no es JSON válido, usar mensaje por defecto
        }
      }

      Swal.fire({
        title: "¡Error!",
        text: mensaje,
        icon: "error",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#e74c3c",
      });
    },
  });
}

// =============================================
// FUNCIÓN PARA EXTRAER DATOS DEL USUARIO
// =============================================
function PCextraerDatosUsuario() {
  let usuario = $("#PCUser").val();
  let userId = $("#PCUserId").val();

  console.log("Usuario logueado:", usuario);
  console.log("User ID logueado:", userId);

  // Consulta AJAX a la API para obtener datos del usuario
  $.ajax({
    url: "/rrhh/usuario-area/",
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log("📋 Respuesta de la API de usuario:", response);

      if (
        response.status === "success" &&
        response.data &&
        response.data.length > 0
      ) {
        datosUsuario = response.data[0];
        console.log("👤 Datos del usuario extraídos:", datosUsuario);

        // Validar permisos según IDCARGO
        if (PCvalidarPermisosPorCargo(datosUsuario.IDCARGO)) {
          console.log("✅ Permisos validados correctamente");
          // Inicializar la tabla automáticamente después de validar permisos
          PCinicializarTabla();
        } else {
          console.warn("⚠️ Usuario sin permisos suficientes");
        }
      } else {
        console.error("❌ No se encontraron datos del usuario");

        // Mostrar error específico
        Swal.fire({
          title: "❌ Error de Usuario",
          text: "No se pudieron cargar los datos del usuario. Contacta al administrador.",
          icon: "error",
          confirmButtonText: "Entendido",
          confirmButtonColor: "#e74c3c",
        });
      }
    },
    error: function (xhr, status, error) {
      console.error("❌ Error al consultar la API:", error);
      console.error("Status:", status);
      console.error("Response:", xhr.responseText);

      // Mostrar error de conexión
      Swal.fire({
        title: "❌ Error de Conexión",
        text: "No se pudo conectar con el servidor. Verifica tu conexión a internet.",
        icon: "error",
        confirmButtonText: "Entendido",
        confirmButtonColor: "#e74c3c",
      });
    },
  });
}

// =============================================
// FUNCIONES PARA APROBACIÓN MASIVA
// =============================================

// Función para actualizar contador de selección
function PCactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#PCcontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#PCpanelSeleccion").slideDown(300);
    $("#PCbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#PCpanelSeleccion").slideUp(300);
    $("#PCbtnAprobacionMasiva").prop("disabled", true);
    estadoActualSeleccionado = null;
  }
}

// Función para actualizar texto del botón según el estado
function PCactualizarTextoBtnMasivo(estado) {
  var texto = "";
  var icono = "";

  if (estado === "PE") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#PCbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }

  $("#PCtextoBtnMasivo").text(texto);
  $("#PCbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
}

// Función para manejar selección individual
function PCmanejarSeleccionIndividual(checkbox) {
  var $checkbox = $(checkbox);
  var idorden = $checkbox.val();
  var estado = $checkbox.data("estado");
  var $row = $checkbox.closest("tr");

  if ($checkbox.is(":checked")) {
    // Agregar a seleccionados
    if (
      registrosSeleccionados.length === 0 ||
      estadoActualSeleccionado === estado
    ) {
      registrosSeleccionados.push({
        idorden: idorden,
        estado: estado,
      });
      $row.addClass("row-selected");

      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        PCactualizarTextoBtnMasivo(estado);
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
      (item) => item.idorden !== idorden
    );
    $row.removeClass("row-selected");

    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = null;
    }
  }

  // Actualizar checkbox "Seleccionar Todos"
  var totalCheckboxes = $(".row-checkbox-PC").length;
  var checkedCheckboxes = $(".row-checkbox-PC:checked").length;

  if (checkedCheckboxes === 0) {
    $("#PCcheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#PCcheckboxSelectAll").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#PCcheckboxSelectAll").prop("checked", false).prop("indeterminate", true);
  }

  PCactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function PCmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-PC").each(function () {
    var $checkbox = $(this);
    var $row = $checkbox.closest("tr");

    if (seleccionar) {
      var idorden = $checkbox.val();
      var estado = $checkbox.data("estado");

      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        PCactualizarTextoBtnMasivo(estado);
      }

      if (estadoActualSeleccionado === estado) {
        $checkbox.prop("checked", true);
        $row.addClass("row-selected");
        registrosSeleccionados.push({
          idorden: idorden,
          estado: estado,
        });
      }
    } else {
      $checkbox.prop("checked", false);
      $row.removeClass("row-selected");
    }
  });

  $("#PCcheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  PCactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function PCejecutarAprobacionMasiva() {
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

  if (estadoActualSeleccionado === "PE") {
    accion = "aprobar";
    textoConfirmacion =
      "¿Estás seguro de que deseas APROBAR " +
      registrosSeleccionados.length +
      " pedido(s) de almacén seleccionado(s)?";
  } else {
    Swal.fire({
      title: "⚠️ Estado no válido",
      text: "Estado de registro no reconocido para aprobación masiva.",
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
      PCprocesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function PCprocesarAprobacionMasiva(accion) {
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
        $.ajax({
          url: "/actualizar-orden-almacen/" + registro.idorden + "/",
          type: "GET",
          data: { accion: accion },
          timeout: 10000,
          success: function (data) {
            procesados++;
            resolve({ success: true, idorden: registro.idorden });
          },
          error: function (xhr, status, error) {
            errores++;
            errorDetails.push({
              idorden: registro.idorden,
              error: error,
              status: status,
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
    $("#PCpanelSeleccion").hide();
    $("#PCbtnAprobacionMasiva").prop("disabled", true);
    $(".row-checkbox-PC").prop("checked", false);
    $("#PCcheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
    $(".row-selected").removeClass("row-selected");

    // Recargar tabla
    PCinicializarTabla();

    // Mostrar resultado final
    if (fallidos === 0) {
      Swal.fire({
        title: "¡Proceso Completado!",
        text:
          "Se procesaron exitosamente " + exitosos + " pedido(s) de almacén.",
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#28a745",
      });
    } else if (exitosos === 0) {
      Swal.fire({
        title: "❌ Error en el Proceso",
        text: "No se pudo procesar ningún pedido. Revisa la conexión e intenta nuevamente.",
        icon: "error",
        confirmButtonText: "Entendido",
        confirmButtonColor: "#e74c3c",
      });
    } else {
      Swal.fire({
        title: "⚠️ Proceso Parcial",
        html:
          "Se procesaron <b>" +
          exitosos +
          "</b> pedido(s) exitosamente.<br>" +
          "Fallaron <b>" +
          fallidos +
          "</b> pedido(s).<br><br>" +
          "Revisa los pedidos restantes manualmente.",
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
function PCconfigurarEventosCheckbox() {
  // Eventos para checkboxes individuales
  $(".row-checkbox-PC")
    .off("change")
    .on("change", function () {
      PCmanejarSeleccionIndividual(this);
    });

  // Evento para checkbox "Seleccionar Todos" del header
  $("#PCcheckboxSelectAll")
    .off("change")
    .on("change", function () {
      var isChecked = $(this).is(":checked");
      PCmanejarSeleccionTodos(isChecked);
    });
}

// =============================================
// INIT PARA USO EN TABS/PARTIALS (NO AUTOEJECUTA)
// Llama esto DESPUÉS de inyectar el partial en el DOM.
// Ejemplo: window.initPCompraModule();
// =============================================
window.initPComprasModule = function (scope) {

   const $scope = $(scope || document);
  // 2) evita duplicar handlers si cambias de tab
  $(document).off("show.bs.modal", "#PCmodalApproveOrders");
  $(document).off("hide.bs.modal", "#PCmodalApproveOrders");

  // 3) MutationObserver para lblEstado
  const observerEstado = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.target.id === "PClblEstado") {
        const estado = (mutation.target.textContent || "").trim();
        if (!estado) return;

        $("#PCbuttons-loading").addClass("d-none");

        const estadoLower = estado.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#PCbtn-aprobar").removeClass("d-none");
        } else {
          $("#PCbtn-aprobar").addClass("d-none");
        }
        console.log(' -1 PCmodalApproveOrders show.bs.modal');
      }
    });
  });
  // 4) Evento al abrir modal
  $(document).on("show.bs.modal", "#PCmodalApproveOrders", function () {
    $("#PCbuttons-loading").removeClass("d-none");
    $("#PCbtn-aprobar").addClass("d-none");

    const elementoEstado = document.getElementById("PClblEstado");
    if (elementoEstado) {
      observerEstado.observe(elementoEstado, {
        childList: true,
        characterData: true,
        subtree: true,
      });

      // chequeo inmediato
      setTimeout(function () {
        const estadoActual = (elementoEstado.textContent || "").trim();
        if (!estadoActual) return;

        $("#PCbuttons-loading").addClass("d-none");

        const estadoLower = estadoActual.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#PCbtn-aprobar").removeClass("d-none");
        } else {
          $("#PCbtn-aprobar").addClass("d-none");
        }
      }, 500);
    }
  });

  // 5) Evento al cerrar modal
 $(document).on("hide.bs.modal", "#PCmodalApproveOrders", function () {
  observerEstado.disconnect();
});

   // Carga combos / data inicial
   PCcargarAreas();

   // Binds (tus .off() evitan duplicados)
   PCconfigurarEventos();
   PCconfigurarSeleccionFila();

   // Carga inicial de tabla (usa filtro por área por defecto)
   //PCfiltrarPorArea();
   PCextraerDatosUsuario();
};