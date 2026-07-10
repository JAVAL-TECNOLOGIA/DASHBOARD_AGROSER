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
function OSvalidarPermisosPorCargo(idCargo) {
  switch (parseInt(idCargo)) {
    case 8:
      // IDCARGO 8: Puede ver V1 (Vº Bº 1) y aprobar
      estadosPermitidos = ["V1"];
      permisoValidado = true;

      return true;

    case 7:
    case 6:
      // IDCARGO 6 y 7: Puede ver PENDIENTE y dar VB
      estadosPermitidos = ["PENDIENTE"];
      permisoValidado = true;

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
function OSobtenerUrlConEstados(area) {
  if (!permisoValidado || estadosPermitidos.length === 0) {
    // Si no hay permisos, retornar URL que no devuelva datos
    return "/approve_servicios_log_filter/" + area + "/SINPERMISOS/";
  }

  // Mapeo de estados frontend -> backend
  var mapeoEstados = {
    PENDIENTE: "PE",
    V1: "V1",
  };

  // Convertir estados usando el mapeo
  var estadosMapeados = estadosPermitidos.map(function (estado) {
    return mapeoEstados[estado] || estado;
  });

  // Construir URL con estados mapeados
  var estadosStr = estadosMapeados.join(",");

  return "/approve_servicios_log_filter/" + area + "/" + estadosStr + "/";
}

// =============================================
// FUNCIÓN PARA CARGAR ÁREAS
// =============================================
function OScargarAreas() {
  $.get("/approve_orders_areas", function (data) {
    $("#OSselectApproveArea").append("<option value='0'>Todos</option>");
    $.each(data, function (index, value) {
      $("#OSselectApproveArea").append(
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
function OSinicializarTabla() {
  // Validar permisos antes de cargar datos
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden cargar datos: permisos no validados");
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#OSpanelSeleccion").hide();
  $("#OSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#OStableApproveOrders")) {
    $("#OStableApproveOrders").DataTable().clear().destroy();
    $("#OStableApproveOrders tbody").empty();
  }

  var urlConEstados = OSobtenerUrlConEstados(0); // 0 = Todas las áreas

  table_show = $("#OStableApproveOrders").DataTable({
    ajax: {
      url: urlConEstados,
      dataSrc: "",
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
      { data: "item" },
      {
        data: "estado",
        render: function (data, type, row) {
          return (
            '<span class="badge badge-primary" style="font-size: 1em;">' +
            data +
            "</span>"
          );
        },
      },
      { data: "fecha" },
      { data: "comentario" },
      { data: "documento", visible: false },
      { data: "num_documento", visible: false },
      { data: "proveedor" },
      { data: "area" },
      { data: "idconsumidor" },
      { data: "moneda" },
      { data: "total" },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-OS" value="' +
            row.idorden +
            '" data-estado="' +
            row.estado +
            '">' +
            "</div>"
          );
        },
      },
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
      OSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function OSfiltrarPorArea() {
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

  var area = $("#OSselectApproveArea").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#OSpanelSeleccion").hide();
  $("#OSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#OStableApproveOrders")) {
    $("#OStableApproveOrders").DataTable().clear().destroy();
    $("#OStableApproveOrders tbody").empty();
  }

  var urlConEstados = OSobtenerUrlConEstados(area);

  table_show = $("#OStableApproveOrders").DataTable({
    ajax: {
      url: urlConEstados,
      dataSrc: "",
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
      { data: "item" },
      {
        data: "estado",
        render: function (data, type, row) {
          return (
            '<span class="badge badge-primary" style="font-size: 1em;">' +
            data +
            "</span>"
          );
        },
      },

      { data: "fecha" },
      { data: "comentario" },
      { data: "documento", visible: false },
      { data: "num_documento", visible: false },
      { data: "proveedor" },
      { data: "area" },
      { data: "idconsumidor" },
      { data: "moneda" },
      { data: "total" },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-OS" value="' +
            row.idorden +
            '" data-estado="' +
            row.estado +
            '">' +
            "</div>"
          );
        },
      },
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
      OSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function OSconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#OSbtnApproveShow").off("click");
  $("#OSbtnAprobacionMasiva").off("click");
  $("#OSbtnSeleccionarTodos").off("click");
  $("#OSbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#OSbtnApproveShow").click(function () {
    OSfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#OSbtnAprobacionMasiva").click(function () {
    OSejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#OSbtnSeleccionarTodos").click(function () {
    OSmanejarSeleccionTodos(true);
  });

  $("#OSbtnDeseleccionarTodos").click(function () {
    OSmanejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function OSconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#OStableApproveOrders tbody").off("dblclick");

  $("#OStableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Prevenir que el doble click active checkbox
    e.preventDefault();

    var row = table_show.row(this).data();
    var idservicio = row["idorden"];

    if (row["documento"] == "COMPRA") {
      OSabrirModalCompra(idservicio);
    } else if (row["documento"] == "SERVICIO") {
      OSabrirModalServicio(idservicio);
    }

    // Configurar botones del modal
    OSconfigurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE COMPRA
// =============================================
function OSabrirModalCompra(idorden) {
  $("#OSmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_orders_log_detail_purchase/" + idorden + "/",
    function (data) {
      $("#OSlblProveedor").html(data[0]["proveedor"]);
      $("#OSlblRuc").html(data[0]["ruc"]);
      $("#OSlblCondicion").html(data[0]["formapago"]);
      $("#OSlblResponsable").html(data[0]["responsable"]);
      $("#OSlblArea").html(data[0]["area"]);
      $("#OSlblSerieNumero").html(data[0]["serie_numero"]);
      $("#OSlblTotal").html(data[0]["total_oc"]);
      $("#OStableBodyApproveOrdersLogDetail").html("");

      $.each(data, function (index, value) {
        $("#OStableApproveOrdersLogDetail").append(
          "<tr><td>" +
            value["producto"] +
            "</td><td>" +
            value["idmedida"] +
            "</td><td>" +
            value["cantidad"] +
            "</td><td>" +
            value["precio_unitario"] +
            "</td><td>" +
            value["moneda"] +
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
// FUNCIÓN PARA ABRIR MODAL DE SERVICIO
// =============================================
function OSabrirModalServicio(idorden) {
  $("#OSmodalApproveOrders").modal("toggle");
  $.get("/approve_orders_log_detail_service/" + idorden, function (data) {
    $("#OSlblEstado").html(data[0]["estado"].toUpperCase());
    $("#OSlblResponsable").html(data[0]["responsable"]);
    $("#OSlblProveedor").html(data[0]["proveedor"]);
    $("#OSlblCondicion").html(data[0]["condicion"]);
    $("#OSlblSerieNumero").html(data[0]["serie_numero"]);
    $("#OSlblArea").html(data[0]["area"]);
    $("#OSlblRuc").html(data[0]["ruc"]);
    $("#OSlblTotal").html(data[0]["total_os"]);
    $("#OStableBodyApproveOrdersLogDetail").html("");

    $.each(data, function (index, value) {
      $("#OStableApproveOrdersLogDetail").append(
        "<tr><td>" +
          value["producto"] +
          "</td><td>" +
          value["idmedida"] +
          "</td><td>" +
          value["cantidad"] +
          "</td><td>" +
          value["precio_unitario"] +
          "</td><td>" +
          value["moneda"] +
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
function OSconfigurarBotonesModal(idservicio) {
  $("#btn-aprobar")
    .off("click")
    .click(function () {
      OSactualizarOrden("aprobar", idservicio);
    });

  $("#btn-vb")
    .off("click")
    .click(function () {
      OSactualizarOrden("vb", idservicio);
    });

  $("#btn-anular")
    .off("click")
    .click(function () {
      OSactualizarOrden("anular", idservicio);
    });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function OSactualizarOrden(accion, idservicio) {
  $.ajax({
    url: "/actualizar-orden-servicio/" + idservicio + "/",
    type: "GET",
    data: { accion: accion },
    timeout: 15000,
    success: function (data, textStatus, xhr) {
      var mensaje = "La orden ha sido actualizada exitosamente";
      if (accion === "aprobar") {
        mensaje = "La orden ha sido APROBADA exitosamente";
      } else if (accion === "vb") {
        mensaje = "Se ha dado VISTO BUENO a la orden";
      } else if (accion === "anular") {
        mensaje = "La orden ha sido ANULADA";
      }

      Swal.fire({
        title: "¡Éxito!",
        text: mensaje,
        icon: "success",
        showConfirmButton: false, // Oculta el botón
        timer: 1000, // Cierra en 1 segundo
        timerProgressBar: true,
      }).then(function () {
        $("#OSmodalApproveOrders").modal("hide");
        // Recargar la tabla
        if ($.fn.DataTable.isDataTable("#OStableApproveOrders")) {
          table_show.ajax.reload();
        }
      });
    },
    error: function (xhr, status, error) {
      var mensaje = "Ocurrió un error al actualizar la orden";
      if (xhr.status === 403) {
        mensaje = "No tienes permisos para realizar esta acción";
      } else if (xhr.status === 404) {
        mensaje = "La orden no fue encontrada";
      } else if (status === "timeout") {
        mensaje = "La solicitud tardó demasiado tiempo. Inténtalo nuevamente";
      }

      Swal.fire({
        title: "¡Error!",
        text: mensaje,
        icon: "error",
        showConfirmButton: false,
        timer: 1000,
        timerProgressBar: true,
      });
    },
  });
}

// =============================================
// FUNCIÓN PARA EXTRAER DATOS DEL USUARIO
// =============================================
function OSextraerDatosUsuario() {
  let usuario = $("#OSUser").val();
  let userId = $("#OSUserId").val();

  // Consulta AJAX a la API para obtener datos del usuario
  $.ajax({
    url: "/rrhh/usuario-area/",
    type: "GET",
    dataType: "json",
    success: function (response) {
      if (
        response.status === "success" &&
        response.data &&
        response.data.length > 0
      ) {
        // Buscar al usuario actual en la lista de usuarios
        let usuarioEncontrado = null;

        $.each(response.data, function (index, userData) {
          // Comparar el ID del usuario logueado con el ID de la API
          if (userData.id == userId) {
            usuarioEncontrado = userData;
            return false; // Salir del bucle when encontrado
          }
        });

        if (usuarioEncontrado) {
          // Almacenar datos del usuario globalmente
          datosUsuario = {
            usuario: usuario,
            userId: userId,
            datosCompletos: usuarioEncontrado,
            idArea: usuarioEncontrado.id_area,
            idCargo: usuarioEncontrado.IDCARGO,
            nombreCompleto:
              usuarioEncontrado.first_name + " " + usuarioEncontrado.last_name,
            email: usuarioEncontrado.email,
            produccion: usuarioEncontrado.produccion,
            estado: usuarioEncontrado.estado,
          };

          // Validar permisos según el cargo
          const tienePermisos = OSvalidarPermisosPorCargo(
            usuarioEncontrado.IDCARGO
          );

          if (tienePermisos) {
            // Solo inicializar la tabla si tiene permisos
            setTimeout(function () {
              OSinicializarTabla();
            }, 100);
          } else {
            console.warn("🚫 Usuario sin permisos - No se carga la tabla");
          }
        } else {
          console.warn("⚠️ Usuario no encontrado en la API con ID:", userId);
          // Mostrar error específico
          Swal.fire({
            title: "❌ Error",
            text: "Usuario no encontrado en el sistema. Contacta con el área TIC.",
            icon: "error",
            confirmButtonText: "Entendido",
            confirmButtonColor: "#e74c3c",
          });
        }
      } else {
        console.error("❌ Error en la respuesta de la API:", response);
        // Mostrar error de API
        Swal.fire({
          title: "❌ Error de Conexión",
          text: "Error al consultar los datos del usuario. Intenta nuevamente.",
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
function OSactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#OScontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#OSpanelSeleccion").show();
    $("#OSbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#OSpanelSeleccion").hide();
    $("#OSbtnAprobacionMasiva").prop("disabled", true);

    // Resetear el botón a su estado original cuando no hay selecciones
    $("#OStextoBtnMasivo").text("Aprobar Masivo");
    $("#OSbtnAprobacionMasiva i")
      .removeClass()
      .addClass("fa fa-check-circle mr-1");
    $("#OSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }
}

// Función para actualizar texto del botón según el estado
function OSactualizarTextoBtnMasivo(estado) {
  var texto = "";
  var icono = "";

  if (estado === "V1") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#OSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  } else if (estado === "PENDIENTE" || estado === "PE") {
    texto = "Dar Visto Bueno";
    icono = "fa-eye";
    $("#OSbtnAprobacionMasiva")
      .removeClass("btn-success")
      .addClass("btn-warning");
  } else {
    texto = "Acción Masiva";
    icono = "fa-check-circle";
    $("#OSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }

  $("#OStextoBtnMasivo").text(texto);
  $("#OSbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
}

// Función para manejar selección individual
function OSmanejarSeleccionIndividual(checkbox) {
  var $checkbox = $(checkbox);
  var idorden = $checkbox.val();
  var estado = $checkbox.data("estado");
  var $row = $checkbox.closest("tr");

  if ($checkbox.is(":checked")) {
    // Verificar si es el primer registro o si tiene el mismo estado
    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = estado;
      OSactualizarTextoBtnMasivo(estado);
    } else if (estadoActualSeleccionado !== estado) {
      // No permitir selección de registros con diferentes estados
      $checkbox.prop("checked", false);
      Swal.fire({
        title: "⚠️ Estados Diferentes",
        text:
          "Solo puedes seleccionar registros con el mismo estado. Estado actual: " +
          estadoActualSeleccionado,
        icon: "warning",
        confirmButtonText: "Entendido",
      });
      return;
    }

    // Agregar a la lista de seleccionados
    registrosSeleccionados.push({
      idorden: idorden,
      estado: estado,
    });

    $row.addClass("row-selected");
  } else {
    // Remover de la lista
    registrosSeleccionados = registrosSeleccionados.filter(function (item) {
      return item.idorden !== idorden;
    });

    $row.removeClass("row-selected");

    // Si no hay más seleccionados, resetear el estado
    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = null;
    }
  }

  // Actualizar checkbox "Seleccionar Todos"
  var totalCheckboxes = $(".row-checkbox-OS").length;
  var checkedCheckboxes = $(".row-checkbox-OS:checked").length;

  if (checkedCheckboxes === 0) {
    $("#OScheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#OScheckboxSelectAll").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#OScheckboxSelectAll").prop("checked", false).prop("indeterminate", true);
  }

  OSactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function OSmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-OS").each(function () {
    var $checkbox = $(this);
    var estado = $checkbox.data("estado");

    if (seleccionar) {
      // Al seleccionar todos, usar el estado del primer checkbox
      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        OSactualizarTextoBtnMasivo(estado);
      }

      // Solo seleccionar si tiene el mismo estado
      if (estado === estadoActualSeleccionado) {
        $checkbox.prop("checked", true);
        $checkbox.closest("tr").addClass("row-selected");
        registrosSeleccionados.push({
          idorden: $checkbox.val(),
          estado: estado,
        });
      }
    } else {
      $checkbox.prop("checked", false);
      $checkbox.closest("tr").removeClass("row-selected");
    }
  });

  $("#OScheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  OSactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function OSejecutarAprobacionMasiva() {
  if (registrosSeleccionados.length === 0) {
    Swal.fire({
      title: "⚠️ Sin Selección",
      text: "Debes seleccionar al menos un registro para procesar.",
      icon: "warning",
      confirmButtonText: "Entendido",
    });
    return;
  }

  var accion = "";
  var textoConfirmacion = "";

  if (estadoActualSeleccionado === "V1") {
    accion = "aprobar";
    textoConfirmacion =
      "¿Estás seguro de que deseas APROBAR " +
      registrosSeleccionados.length +
      " registro(s)?";
  } else if (
    estadoActualSeleccionado === "PENDIENTE" ||
    estadoActualSeleccionado === "PE"
  ) {
    accion = "vb";
    textoConfirmacion =
      "¿Estás seguro de que deseas dar VISTO BUENO a " +
      registrosSeleccionados.length +
      " registro(s)?";
  } else {
    console.error("❌ Estado no reconocido:", estadoActualSeleccionado);
    Swal.fire({
      title: "⚠️ Estado No Válido",
      text:
        "El estado seleccionado (" +
        estadoActualSeleccionado +
        ") no es válido para procesamiento masivo.",
      icon: "warning",
      confirmButtonText: "Entendido",
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
      OSprocesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function OSprocesarAprobacionMasiva(accion) {
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
    return new Promise(function (resolve, reject) {
      // Delay progresivo para cada request
      setTimeout(function () {
        $.ajax({
          url: "/actualizar-orden-servicio/" + registro.idorden + "/",
          type: "GET",
          data: { accion: accion },
          timeout: 10000,
          success: function (data) {
            procesados++;
            resolve({
              success: true,
              idorden: registro.idorden,
            });
          },
          error: function (xhr, status, error) {
            errores++;
            errorDetails.push({
              idorden: registro.idorden,
              error: xhr.status + ": " + error,
            });
            resolve({
              success: false,
              idorden: registro.idorden,
              error: error,
            });
          },
        });
      }, index * 200); // 200ms de delay entre cada request
    });
  });

  // Cuando todas las promesas se resuelvan
  Promise.all(promesas).then(function (resultados) {
    // Cerrar el modal de progreso
    Swal.close();

    // Mostrar resultado final
    var tituloFinal = "";
    var textoFinal = "";
    var iconoFinal = "";

    if (errores === 0) {
      tituloFinal = "¡Éxito Completo!";
      textoFinal = "Se procesaron exitosamente " + procesados + " registro(s).";
      iconoFinal = "success";
    } else if (procesados > 0) {
      tituloFinal = "⚠️ Procesamiento Parcial";
      textoFinal =
        "Se procesaron " +
        procesados +
        " registro(s) exitosamente y " +
        errores +
        " con errores.";
      iconoFinal = "warning";
    } else {
      tituloFinal = "❌ Error Completo";
      textoFinal = "No se pudo procesar ningún registro. Todos fallaron.";
      iconoFinal = "error";
    }

    Swal.fire({
      title: tituloFinal,
      text: textoFinal,
      icon: iconoFinal,
      showConfirmButton: false, // Oculta botón
      timer: 1000, // 1 segundo
      timerProgressBar: true,
    }).then(function () {
      // Limpiar selecciones
      registrosSeleccionados = [];
      estadoActualSeleccionado = null;
      $("#OSpanelSeleccion").hide();
      $("#OSbtnAprobacionMasiva").prop("disabled", true);

      // Recargar la tabla
      if ($.fn.DataTable.isDataTable("#OStableApproveOrders")) {
        table_show.ajax.reload();
      }
    });
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function OSconfigurarEventosCheckbox() {
  // Eventos para checkboxes individuales
  $(".row-checkbox-OS")
    .off("change")
    .on("change", function () {
      OSmanejarSeleccionIndividual(this);
    });

  // Evento para checkbox "Seleccionar Todos" del header
  $("#OScheckboxSelectAll")
    .off("change")
    .on("change", function () {
      OSmanejarSeleccionTodos($(this).is(":checked"));
    });
}

// =============================================
// INIT PARA USO EN TABS/PARTIALS (NO AUTOEJECUTA)
// Llama esto DESPUÉS de inyectar el partial en el DOM.
// Ejemplo: window.initOServicioModule();
// =============================================
window.initOServiciosModule = function (scope) {
      const $scope = $(scope || document);
  // 2) evita duplicar handlers si cambias de tab
  $(document).off("show.bs.modal", "#OSmodalApproveOrders");
  $(document).off("hide.bs.modal", "#OSmodalApproveOrders");

  // 3) MutationObserver para OClblEstado
  const observerEstado = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.target.id === "OSlblEstado") {
        const estado = (mutation.target.textContent || "").trim();
        if (!estado) return;

        $("#OSbuttons-loading").addClass("d-none");
        const estadoLower = estado.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#OSbtn-aprobar").removeClass("d-none");
        } else {
          $("#OSbtn-aprobar").addClass("d-none");
        }
        console.log(' -1 PSmodalApproveOrders show.bs.modal');
      }
    });
  });
  // 4) Evento al abrir modal
  $(document).on("show.bs.modal", "#OSmodalApproveOrders", function () {
    $("#OSbuttons-loading").removeClass("d-none");
    $("#OSbtn-aprobar").addClass("d-none");

    const elementoEstado = document.getElementById("OSlblEstado");
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

        $("#OSbuttons-loading").addClass("d-none");

        const estadoLower = estadoActual.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#OSbtn-aprobar").removeClass("d-none");
        } else {
          $("#OSbtn-aprobar").addClass("d-none");
        }
      }, 500);
    }
  });

  // 5) Evento al cerrar modal
 $(document).on("hide.bs.modal", "#OSmodalApproveOrders", function () {
  observerEstado.disconnect();
});
  
   // Carga combos / data inicial
   OScargarAreas();

   // Binds (tus .off() evitan duplicados)
   OSconfigurarEventos();
   OSconfigurarSeleccionFila();
   // Carga inicial de tabla (usa filtro por área por defecto)
   //PCPSOCfiltrarPorArea();
   OSextraerDatosUsuario();
};