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
function AJOSvalidarPermisosPorCargo(idCargo) {
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
function AJOSobtenerUrlConEstados(area) {
  if (!permisoValidado || estadosPermitidos.length === 0) {
    // Si no hay permisos, retornar URL que no devuelva datos
    return "/approve_servicios_log_filter_ajs/" + area + "/SINPERMISOS/";
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

  return "/approve_servicios_log_filter_ajs/" + area + "/" + estadosStr + "/";
}

// =============================================
// FUNCIÓN PARA CARGAR ÁREAS
// =============================================
function AJOScargarAreas() {
  $.get("/approve_orders_areas", function (data) {
    $("#AJOSselectApproveArea").append("<option value='0'>Todos</option>");
    $.each(data, function (index, value) {
      $("#AJOSselectApproveArea").append(
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
function AJOSinicializarTabla() {
  // Validar permisos antes de cargar datos
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden cargar datos: permisos no validados");
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#AJOSpanelSeleccion").hide();
  $("#AJOSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#AJOStableApproveOrders")) {
    $("#AJOStableApproveOrders").DataTable().clear().destroy();
    $("#AJOStableApproveOrders tbody").empty();
  }

  var urlConEstados = AJOSobtenerUrlConEstados(0); // 0 = Todas las áreas

  table_show = $("#AJOStableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-OSAJS" value="' +
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
      AJOSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function AJOSfiltrarPorArea() {
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

  var area = $("#AJOSselectApproveArea").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#AJOSpanelSeleccion").hide();
  $("#AJOSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#AJOStableApproveOrders")) {
    $("#AJOStableApproveOrders").DataTable().clear().destroy();
    $("#AJOStableApproveOrders tbody").empty();
  }

  var urlConEstados = AJOSobtenerUrlConEstados(area);

  table_show = $("#AJOStableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-OSAJS" value="' +
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
      AJOSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function AJOSconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#AJOSbtnApproveShow").off("click");
  $("#AJOSbtnAprobacionMasiva").off("click");
  $("#AJOSbtnSeleccionarTodos").off("click");
  $("#AJOSbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#AJOSbtnApproveShow").click(function () {
    AJOSfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#AJOSbtnAprobacionMasiva").click(function () {
    AJOSejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#AJOSbtnSeleccionarTodos").click(function () {
    AJOSmanejarSeleccionTodos(true);
  });

  $("#AJOSbtnDeseleccionarTodos").click(function () {
    AJOSmanejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function AJOSconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#AJOStableApproveOrders tbody").off("dblclick");

  $("#AJOStableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Prevenir que el doble click active checkbox
    e.preventDefault();

    var row = table_show.row(this).data();
    var idservicio = row["idorden"];

    if (row["documento"] == "COMPRA") {
      AJOSabrirModalCompra(idservicio);
    } else if (row["documento"] == "SERVICIO") {
      AJOSabrirModalServicio(idservicio);
    }

    // Configurar botones del modal
    AJOSconfigurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE COMPRA
// =============================================
function AJOSabrirModalCompra(idorden) {
  $("#AJOSmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_orders_log_detail_purchase_ajs/" + idorden + "/",
    function (data) {
      $("#AJOSlblProveedor").html(data[0]["proveedor"]);
      $("#AJOSlblRuc").html(data[0]["ruc"]);
      $("#AJOSlblCondicion").html(data[0]["formapago"]);
      $("#AJOSlblResponsable").html(data[0]["responsable"]);
      $("#AJOSlblArea").html(data[0]["area"]);
      $("#AJOSlblSerieNumero").html(data[0]["serie_numero"]);
      $("#AJOSlblTotal").html(data[0]["total_oc"]);
      $("#AJOStableBodyApproveOrdersLogDetail").html("");

      $.each(data, function (index, value) {
        $("#AJOStableApproveOrdersLogDetail").append(
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
function AJOSabrirModalServicio(idorden) {
  $("#AJOSmodalApproveOrders").modal("toggle");
  $.get("/approve_orders_log_detail_service_ajs/" + idorden, function (data) {
    $("#AJOSlblEstado").html(data[0]["estado"].toUpperCase());
    $("#AJOSlblResponsable").html(data[0]["responsable"]);
    $("#AJOSlblProveedor").html(data[0]["proveedor"]);
    $("#AJOSlblCondicion").html(data[0]["condicion"]);
    $("#AJOSlblSerieNumero").html(data[0]["serie_numero"]);
    $("#AJOSlblArea").html(data[0]["area"]);
    $("#AJOSlblRuc").html(data[0]["ruc"]);
    $("#AJOSlblTotal").html(data[0]["total_os"]);
    $("#AJOStableBodyApproveOrdersLogDetail").html("");

    $.each(data, function (index, value) {
      $("#AJOStableApproveOrdersLogDetail").append(
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
function AJOSconfigurarBotonesModal(idservicio) {
  $("#AJOSbtn-aprobar")
    .off("click")
    .click(function () {
      AJOSactualizarOrden("aprobar", idservicio);
    });

  $("#btn-vb")
    .off("click")
    .click(function () {
      AJOSactualizarOrden("vb", idservicio);
    });

  $("#btn-anular")
    .off("click")
    .click(function () {
      AJOSactualizarOrden("anular", idservicio);
    });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function AJOSactualizarOrden(accion, idservicio) {
  $.ajax({
    url: "/actualizar-orden-servicio_ajs/" + idservicio + "/",
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
        $("#AJOSmodalApproveOrders").modal("hide");
        // Recargar la tabla
        if ($.fn.DataTable.isDataTable("#AJOStableApproveOrders")) {
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
function AJOSextraerDatosUsuario() {
  let usuario = $("#AJOSUser").val();
  let userId = $("#AJOSUserId").val();

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
          const tienePermisos = AJOSvalidarPermisosPorCargo(
            usuarioEncontrado.IDCARGO
          );

          if (tienePermisos) {
            // Solo inicializar la tabla si tiene permisos
            setTimeout(function () {
              AJOSinicializarTabla();
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
function AJOSactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#AJOScontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#AJOSpanelSeleccion").show();
    $("#AJOSbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#AJOSpanelSeleccion").hide();
    $("#AJOSbtnAprobacionMasiva").prop("disabled", true);

    // Resetear el botón a su estado original cuando no hay selecciones
    $("#AJOStextoBtnMasivo").text("Aprobar Masivo");
    $("#AJOSbtnAprobacionMasiva i")
      .removeClass()
      .addClass("fa fa-check-circle mr-1");
    $("#AJOSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }
}

// Función para actualizar texto del botón según el estado
function AJOSactualizarTextoBtnMasivo(estado) {
  var texto = "";
  var icono = "";

  if (estado === "V1") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#AJOSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  } else if (estado === "PENDIENTE" || estado === "PE") {
    texto = "Dar Visto Bueno";
    icono = "fa-eye";
    $("#AJOSbtnAprobacionMasiva")
      .removeClass("btn-success")
      .addClass("btn-warning");
  } else {
    texto = "Acción Masiva";
    icono = "fa-check-circle";
    $("#AJOSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }

  $("#AJOStextoBtnMasivo").text(texto);
  $("#AJOSbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
}

// Función para manejar selección individual
function AJOSmanejarSeleccionIndividual(checkbox) {
  var $checkbox = $(checkbox);
  var idorden = $checkbox.val();
  var estado = $checkbox.data("estado");
  var $row = $checkbox.closest("tr");

  if ($checkbox.is(":checked")) {
    // Verificar si es el primer registro o si tiene el mismo estado
    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = estado;
      AJOSactualizarTextoBtnMasivo(estado);
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
  var totalCheckboxes = $(".row-checkbox-OSAJS").length;
  var checkedCheckboxes = $(".row-checkbox-OSAJS:checked").length;

  if (checkedCheckboxes === 0) {
    $("#AJOScheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#AJOScheckboxSelectAll").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#AJOScheckboxSelectAll").prop("checked", false).prop("indeterminate", true);
  }

  AJOSactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function AJOSmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-OSAJS").each(function () {
    var $checkbox = $(this);
    var estado = $checkbox.data("estado");

    if (seleccionar) {
      // Al seleccionar todos, usar el estado del primer checkbox
      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        AJOSactualizarTextoBtnMasivo(estado);
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

  $("#AJOScheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  AJOSactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function AJOSejecutarAprobacionMasiva() {
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
      AJOSprocesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function AJOSprocesarAprobacionMasiva(accion) {
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
          url: "/actualizar-orden-servicio_ajs/" + registro.idorden + "/",
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
      $("#AJOSpanelSeleccion").hide();
      $("#AJOSbtnAprobacionMasiva").prop("disabled", true);

      // Recargar la tabla
      if ($.fn.DataTable.isDataTable("#AJOStableApproveOrders")) {
        table_show.ajax.reload();
      }
    });
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function AJOSconfigurarEventosCheckbox() {
  // Eventos para checkboxes individuales
  $(".row-checkbox-OSAJS")
    .off("change")
    .on("change", function () {
      AJOSmanejarSeleccionIndividual(this);
    });

  // Evento para checkbox "Seleccionar Todos" del header
  $("#AJOScheckboxSelectAll")
    .off("change")
    .on("change", function () {
      AJOSmanejarSeleccionTodos($(this).is(":checked"));
    });
}

// =============================================
// INICIALIZACIÓN CUANDO EL DOCUMENTO ESTÉ LISTO
// =============================================
window.initOServiciosAJSModule = function (scope) {
      const $scope = $(scope || document);
  // 2) evita duplicar handlers si cambias de tab
  $(document).off("show.bs.modal", "#AJOSmodalApproveOrders");
  $(document).off("hide.bs.modal", "#AJOSmodalApproveOrders");

  // 3) MutationObserver para OCAJOSlblEstado
  const observerEstado = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.target.id === "AJOSlblEstado") {
        const estado = (mutation.target.textContent || "").trim();
        if (!estado) return;

        $("#AJOSbuttons-loading").addClass("d-none");
        const estadoLower = estado.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#AJOSbtn-aprobar").removeClass("d-none");
        } else {
          $("#AJOSbtn-aprobar").addClass("d-none");
        }
        console.log(' -1 AJOSmodalApproveOrders show.bs.modal');
      }
    });
  });
  // 4) Evento al abrir modal
  $(document).on("show.bs.modal", "#AJOSmodalApproveOrders", function () {
    $("#AJOSbuttons-loading").removeClass("d-none");
    $("#AJOSbtn-aprobar").addClass("d-none");

    const elementoEstado = document.getElementById("AJOSlblEstado");
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

        $("#AJOSbuttons-loading").addClass("d-none");

        const estadoLower = estadoActual.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#AJOSbtn-aprobar").removeClass("d-none");
        } else {
          $("#AJOSbtn-aprobar").addClass("d-none");
        }
      }, 500);
    }
  });

  // 5) Evento al cerrar modal
 $(document).on("hide.bs.modal", "#AJOSmodalApproveOrders", function () {
  observerEstado.disconnect();
});
  
   // Carga combos / data inicial
   AJOScargarAreas();

   // Binds (tus .off() evitan duplicados)
   AJOSconfigurarEventos();
   AJOSconfigurarSeleccionFila();
   // Carga inicial de tabla (usa filtro por área por defecto)
   //PCPSOCAJOSfiltrarPorArea();
   AJOSextraerDatosUsuario();
};