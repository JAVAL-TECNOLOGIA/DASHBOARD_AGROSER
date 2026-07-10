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
function OSVvalidarPermisosPorCargo(idCargo) {
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
function OSVobtenerUrlConEstados(area) {
  if (!permisoValidado || estadosPermitidos.length === 0) {
    // Si no hay permisos, retornar URL que no devuelva datos
    return "/approve_servicios_log_filter_cv/" + area + "/SINPERMISOS/";
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

  return "/approve_servicios_log_filter_cv/" + area + "/" + estadosStr + "/";
}

// =============================================
// FUNCIÓN PARA CARGAR ÁREAS
// =============================================
function OSVcargarAreas() {
  $.get("/approve_orders_areas", function (data) {
    $("#OSVselectApproveArea").append("<option value='0'>Todos</option>");
    $.each(data, function (index, value) {
      $("#OSVselectApproveArea").append(
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
function OSVinicializarTabla() {
  // Validar permisos antes de cargar datos
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden cargar datos: permisos no validados");
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#OSVpanelSeleccion").hide();
  $("#OSVbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#OSVtableApproveOrders")) {
    $("#OSVtableApproveOrders").DataTable().clear().destroy();
    $("#OSVtableApproveOrders tbody").empty();
  }

  var urlConEstados = OSVobtenerUrlConEstados(0); // 0 = Todas las áreas

  table_show = $("#OSVtableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-OSV" value="' +
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
      OSVconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function OSVfiltrarPorArea() {
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

  var area = $("#OSVselectApproveArea").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#OSVpanelSeleccion").hide();
  $("#OSVbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#OSVtableApproveOrders")) {
    $("#OSVtableApproveOrders").DataTable().clear().destroy();
    $("#OSVtableApproveOrders tbody").empty();
  }

  var urlConEstados = OSVobtenerUrlConEstados(area);

  table_show = $("#OSVtableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-OSV" value="' +
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
      OSVconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function OSVconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#OSVbtnApproveShow").off("click");
  $("#OSVbtnAprobacionMasiva").off("click");
  $("#OSVbtnApproveShow").off("click");
  $("#OSVbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#OSVbtnApproveShow").click(function () {
    OSVfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#OSVbtnAprobacionMasiva").click(function () {
    OSVejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#OSVbtnApproveShow").click(function () {
    OSVmanejarSeleccionTodos(true);
  });

  $("#OSVbtnDeseleccionarTodos").click(function () {
    OSVmanejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function OSVconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#OSVtableApproveOrders tbody").off("dblclick");

  $("#OSVtableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Prevenir que el doble click active checkbox
    e.preventDefault();

    var row = table_show.row(this).data();
    var idservicio = row["idorden"];

    if (row["documento"] == "COMPRA") {
      OSVabrirModalCompra(idservicio);
    } else if (row["documento"] == "SERVICIO") {
      OSVabrirModalServicio(idservicio);
    }

    // Configurar botones del modal
    OSVconfigurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE COMPRA
// =============================================
function OSVabrirModalCompra(idorden) {
  $("#OSVmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_orders_log_detail_purchase_cv/" + idorden + "/",
    function (data) {
      $("#OSVlblProveedor").html(data[0]["proveedor"]);
      $("#OSVlblRuc").html(data[0]["ruc"]);
      $("#OSVlblCondicion").html(data[0]["formapago"]);
      $("#OSVlblResponsable").html(data[0]["responsable"]);
      $("#OSVlblArea").html(data[0]["area"]);
      $("#OSVlblSerieNumero").html(data[0]["serie_numero"]);
      $("#OSVlblTotal").html(data[0]["total_oc"]);
      $("#OSVtableBodyApproveOrdersLogDetail").html("");

      $.each(data, function (index, value) {
        $("#OSVtableApproveOrdersLogDetail").append(
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
function OSVabrirModalServicio(idorden) {
  $("#OSVmodalApproveOrders").modal("toggle");
  $.get("/approve_orders_log_detail_service_cv/" + idorden, function (data) {
    $("#OSVlblEstado").html(data[0]["estado"].toUpperCase());
    $("#OSVlblResponsable").html(data[0]["responsable"]);
    $("#OSVlblProveedor").html(data[0]["proveedor"]);
    $("#OSVlblCondicion").html(data[0]["condicion"]);
    $("#OSVlblSerieNumero").html(data[0]["serie_numero"]);
    $("#OSVlblArea").html(data[0]["area"]);
    $("#OSVlblRuc").html(data[0]["ruc"]);
    $("#OSVlblTotal").html(data[0]["total_os"]);
    $("#OSVtableBodyApproveOrdersLogDetail").html("");

    $.each(data, function (index, value) {
      $("#OSVtableApproveOrdersLogDetail").append(
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
function OSVconfigurarBotonesModal(idservicio) {
  $("#OSVbtn-aprobar")
    .off("click")
    .click(function () {
      OSVactualizarOrden("aprobar", idservicio);
    });

  $("#OSVbtn-vb")
    .off("click")
    .click(function () {
      OSVactualizarOrden("vb", idservicio);
    });

  $("#OSVbtn-anular")
    .off("click")
    .click(function () {
      OSVactualizarOrden("anular", idservicio);
    });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function OSVactualizarOrden(accion, idservicio) {
  $.ajax({
    url: "/actualizar-orden-servicio_cv/" + idservicio + "/",
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
        $("#OSVmodalApproveOrders").modal("hide");
        // Recargar la tabla
        if ($.fn.DataTable.isDataTable("#OSVtableApproveOrders")) {
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
function OSVextraerDatosUsuario() {
  let usuario = $("#OSVUser").val();
  let userId = $("#OSVUserId").val();

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
          const tienePermisos = OSVvalidarPermisosPorCargo(
            usuarioEncontrado.IDCARGO
          );

          if (tienePermisos) {
            // Solo inicializar la tabla si tiene permisos
            setTimeout(function () {
              OSVinicializarTabla();
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
function OSVactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#OSVcontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#OSVpanelSeleccion").show();
    $("#OSVbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#OSVpanelSeleccion").hide();
    $("#OSVbtnAprobacionMasiva").prop("disabled", true);

    // Resetear el botón a su estado original cuando no hay selecciones
    $("#OSVtextoBtnMasivo").text("Aprobar Masivo");
    $("#OSVbtnAprobacionMasiva i")
      .removeClass()
      .addClass("fa fa-check-circle mr-1");
    $("#OSVbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }
}

// Función para actualizar texto del botón según el estado
function actualizarTextoBtnMasivo(estado) {
  var texto = "";
  var icono = "";

  if (estado === "V1") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#OSVbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  } else if (estado === "PENDIENTE" || estado === "PE") {
    texto = "Dar Visto Bueno";
    icono = "fa-eye";
    $("#OSVbtnAprobacionMasiva")
      .removeClass("btn-success")
      .addClass("btn-warning");
  } else {
    texto = "Acción Masiva";
    icono = "fa-check-circle";
    $("#OSVbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }

  $("#OSVtextoBtnMasivo").text(texto);
  $("#OSVbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
}

// Función para manejar selección individual
function manejarSeleccionIndividual(checkbox) {
  var $checkbox = $(checkbox);
  var idorden = $checkbox.val();
  var estado = $checkbox.data("estado");
  var $row = $checkbox.closest("tr");

  if ($checkbox.is(":checked")) {
    // Verificar si es el primer registro o si tiene el mismo estado
    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = estado;
      actualizarTextoBtnMasivo(estado);
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
  var totalCheckboxes = $(".row-checkbox-OSV").length;
  var checkedCheckboxes = $(".row-checkbox-OSV:checked").length;

  if (checkedCheckboxes === 0) {
    $("#OSVcheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#OSVcheckboxSelectAll").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#OSVcheckboxSelectAll").prop("checked", false).prop("indeterminate", true);
  }

  OSVactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function OSVmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-OSV").each(function () {
    var $checkbox = $(this);
    var estado = $checkbox.data("estado");

    if (seleccionar) {
      // Al seleccionar todos, usar el estado del primer checkbox
      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        actualizarTextoBtnMasivo(estado);
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

  $("#OSVcheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  OSVactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function OSVejecutarAprobacionMasiva() {
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
    return new Promise(function (resolve, reject) {
      // Delay progresivo para cada request
      setTimeout(function () {
        $.ajax({
          url: "/actualizar-orden-servicio_cv/" + registro.idorden + "/",
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
      $("#OSVpanelSeleccion").hide();
      $("#OSVbtnAprobacionMasiva").prop("disabled", true);

      // Recargar la tabla
      if ($.fn.DataTable.isDataTable("#OSVtableApproveOrders")) {
        table_show.ajax.reload();
      }
    });
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function OSVconfigurarEventosCheckbox() {
  // Eventos para checkboxes individuales
  $(".row-checkbox-OSV")
    .off("change")
    .on("change", function () {
      manejarSeleccionIndividual(this);
    });

  // Evento para checkbox "Seleccionar Todos" del header
  $("#OSVcheckboxSelectAll")
    .off("change")
    .on("change", function () {
      OSVmanejarSeleccionTodos($(this).is(":checked"));
    });
}

// =============================================
// INICIALIZACIÓN CUANDO EL DOCUMENTO ESTÉ LISTO
// =============================================
window.initOServiciosCVModule = function (scope) {
      const $scope = $(scope || document);
  // 2) evita duplicar handlers si cambias de tab
  $(document).off("show.bs.modal", "#OSVmodalApproveOrders");
  $(document).off("hide.bs.modal", "#OSVmodalApproveOrders");

  // 3) MutationObserver para OClblEstado
  const observerEstado = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.target.id === "OSVlblEstado") {
        const estado = (mutation.target.textContent || "").trim();
        if (!estado) return;

        $("#OSVbuttons-loading").addClass("d-none");
        const estadoLower = estado.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#OSVbtn-aprobar").removeClass("d-none");
        } else {
          $("#OSVbtn-aprobar").addClass("d-none");
        }
        console.log(' -1 OSVmodalApproveOrders show.bs.modal');
      }
    });
  });
  // 4) Evento al abrir modal
  $(document).on("show.bs.modal", "#OSVmodalApproveOrders", function () {
    $("#OSVbuttons-loading").removeClass("d-none");
    $("#OSVbtn-aprobar").addClass("d-none");

    const elementoEstado = document.getElementById("OSVlblEstado");
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

        $("#OSVbuttons-loading").addClass("d-none");

        const estadoLower = estadoActual.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#OSVbtn-aprobar").removeClass("d-none");
        } else {
          $("#OSVbtn-aprobar").addClass("d-none");
        }
      }, 500);
    }
  });

  // 5) Evento al cerrar modal
 $(document).on("hide.bs.modal", "#OSVmodalApproveOrders", function () {
  observerEstado.disconnect();
});
  
   // Carga combos / data inicial
   OSVcargarAreas();

   // Binds (tus .off() evitan duplicados)
   OSVconfigurarEventos();
   OSVconfigurarSeleccionFila();
   // Carga inicial de tabla (usa filtro por área por defecto)
   //PCPSOCfiltrarPorArea();
   OSVextraerDatosUsuario();
};