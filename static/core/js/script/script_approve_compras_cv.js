// Variable global para la tabla
var table_show;

// Variables globales para datos del usuario
var datosUsuario = null;
var estadosPermitidos = [];
var permisoValidado = false;

// Variables globales para aprobación masiva
var registrosSeleccionados = [];
var estadoActualSeleccionado = null;

// CARGO que solo puede ver Producción Maquila
const CARGO_PRODUCCION_CV = 7;

// ÁREA permitida para ese cargo
const AREA_PRODUCCION_MAQUILA_CV = '017';

function CVesCargoProduccion() {
  return datosUsuario && parseInt(datosUsuario.idCargo) === CARGO_PRODUCCION_CV;
}

const CARGO_GERENCIA_CV = 8; // 👈 usa el ID real de gerencia

function CVesGerencia() {
  return datosUsuario && parseInt(datosUsuario.idCargo) === CARGO_GERENCIA_CV;
}

// =============================================
// FUNCIÓN PARA VALIDAR PERMISOS SEGÚN CARGO
// =============================================
function OCVvalidarPermisosPorCargo(idCargo) {
  console.log("🔍 Validando permisos para IDCARGO:", idCargo);

  switch (parseInt(idCargo)) {
    case 8:
      // IDCARGO 8: Solo puede ver registros con estado V1
      estadosPermitidos = ["V1"];
      permisoValidado = true;
      console.log("✅ Usuario con IDCARGO 8: Permisos para ver solo V1");
      return true;

    case 7:
      // IDCARGO 7 y 6: Solo pueden ver registros en estado PENDIENTE (PE)
      estadosPermitidos = ["PENDIENTE", "V1"];
      permisoValidado = true;
      console.log(
        "✅ Usuario con IDCARGO",
        idCargo + ": Permisos para ver solo PENDIENTE"
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
function OCVobtenerUrlConEstados(area) {
  if (!permisoValidado || estadosPermitidos.length === 0) {
    // Si no hay permisos, retornar URL que no devuelva datos
    return "/approve_compras_log_filter_cv/" + area + "/SINPERMISOS/";
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

  console.log(
    "🔗 URL generada para área",
    area + ":",
    "/approve_compras_log_filter_cv/" + area + "/" + estadosStr + "/"
  );
  console.log("📋 Estados permitidos:", estadosPermitidos);
  console.log("🔄 Estados mapeados:", estadosMapeados);

  return "/approve_compras_log_filter_cv/" + area + "/" + estadosStr + "/";
}

// =============================================
// FUNCIÓN PARA CARGAR ÁREAS
// =============================================
function OCVcargarAreas() {
  $.get("/approve_orders_areas", function (data) {
    $("#OCVselectApproveArea").append("<option value='0'>Todos</option>");
    /* console.log($("#OCVselectApproveArea").val()); */
    $.each(data, function (index, value) {
      $("#OCVselectApproveArea").append(
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
function OCVinicializarTabla() {
  // Validar permisos antes de cargar datos
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden cargar datos: permisos no validados");
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#OCVpanelSeleccion").hide();
  $("#OCVbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#OCVtableApproveOrders")) {
    $("#OCVtableApproveOrders").DataTable().clear().destroy();
    $("#OCVtableApproveOrders tbody").empty();
  }

  //var urlConEstados = OCVobtenerUrlConEstados(0); // 0 = Todas las áreas

  let area = 0; // 0 = todas las áreas

  if (CVesCargoProduccion()) {
    area = AREA_PRODUCCION_MAQUILA_CV;

    $("#OCVselectApproveArea")
      .val(area)
      .prop("disabled", true);
  } 
  else if (CVesGerencia()) {
    area = 0; // 🔥 gerencia ve todo

    $("#OCVselectApproveArea")
      .prop("disabled", false);
  }

  var urlConEstados = OCVobtenerUrlConEstados(area);

  console.log("🚀 Inicializando tabla con URL:", urlConEstados);

  table_show = $("#OCVtableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-OCV" value="' +
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
      OCVconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function OCVfiltrarPorArea() {
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

  //var area = $("#OCVselectApproveArea").val() || 0;

  let area = 0;

  if (CVesCargoProduccion()) {
    area = AREA_PRODUCCION_MAQUILA_CV;
  }
  else if (CVesGerencia()) {
    area = $("#OCVselectApproveArea").val() || 0;
  }
  else {
    area = $("#OCVselectApproveArea").val() || 0;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#OCVpanelSeleccion").hide();
  $("#OCVbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#OCVtableApproveOrders")) {
    $("#OCVtableApproveOrders").DataTable().clear().destroy();
    $("#OCVtableApproveOrders tbody").empty();
  }

  var urlConEstados = OCVobtenerUrlConEstados(area);

  console.log("🔍 Filtrando por área:", area, "con URL:", urlConEstados);

  table_show = $("#OCVtableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-OCV" value="' +
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
      OCVconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function OCVconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#OCVbtnApproveShow").off("click");
  $("#OCVbtnAprobacionMasiva").off("click");
  $("#OCVbtnSeleccionarTodos").off("click");
  $("#OCVbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#OCVbtnApproveShow").click(function () {
    OCVfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#OCVbtnAprobacionMasiva").click(function () {
    OCVejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#OCVbtnSeleccionarTodos").click(function () {
    OCVmanejarSeleccionTodos(true);
  });

  $("#OCVbtnDeseleccionarTodos").click(function () {
    OCVmanejarSeleccionTodos(false);
  });
}
// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function OCVconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#OCVtableApproveOrders tbody").off("dblclick");

  $("#OCVtableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Prevenir que el doble click active checkbox
    e.preventDefault();

    var row = table_show.row(this).data();
    var idservicio = row["idorden"];

    if (row["documento"] == "COMPRA") {
      OCVabrirModalCompra(idservicio);
    } else if (row["documento"] == "SERVICIO") {
      OCVabrirModalServicio(idservicio);
    }

    // Configurar botones del modal
    OCVconfigurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE COMPRA
// =============================================
function OCVabrirModalCompra(idorden) {
  $("#OCVmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_orders_log_detail_purchase_cv/" + idorden + "/",
    function (data) {
      $("#OCVlblEstado").html(data[0]["estado"]);
      $("#OCVlblProveedor").html(data[0]["proveedor"]);
      $("#OCVlblRuc").html(data[0]["ruc"]);
      $("#OCVlblCondicion").html(data[0]["formapago"]);
      $("#OCVlblResponsable").html(data[0]["responsable"]);
      $("#OCVlblArea").html(data[0]["area"]);
      $("#OCVlblSerieNumero").html(data[0]["SerieNumero"]);
      $("#OCVlblTotal").html(data[0]["total_oc"]);
      $("#OCVtableBodyApproveOrdersLogDetail").html("");

      $.each(data, function (index, value) {
        //total = total +(Math.round(value['total'] * 100) / 100);
        $("#OCVtableApproveOrdersLogDetail").append(
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
function OCVabrirModalServicio(idorden) {
  $("#OCVmodalApproveOrders").modal("toggle");
  $.get("../approve_orders_log_detail_service/" + idorden, function (data) {
    $("#OCVlblEstado").html(data[0]["estado"].toUpperCase());
    $("#OCVlblResponsable").html(data[0]["responsable"]);
    $("#OCVlblProveedor").html(data[0]["proveedor"]);
    $("#OCVlblCondicion").html(data[0]["condicion"]);
    $("#OCVlblSerieNumero").html(data[0]["serie_numero"]);
    $("#OCVlblArea").html(data[0]["area"]);
    $("#OCVlblRuc").html(data[0]["ruc"]);
    $("#OCVlblTotal").html(data[0]["total_os"]);
    $("#OCVtableBodyApproveOrdersLogDetail").html("");

    $.each(data, function (index, value) {
      $("#OCVtableApproveOrdersLogDetail").append(
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
function OCVconfigurarBotonesModal(idservicio) {
  $("#OCVbtn-aprobar")
    .off("click")
    .click(function () {
      OCVactualizarOrden("aprobar", idservicio);
    });

  $("#OCVbtn-vb")
    .off("click")
    .click(function () {
      OCVactualizarOrden("vb", idservicio);
    });

  $("#OCVbtn-anular")
    .off("click")
    .click(function () {
      OCVactualizarOrden("anular", idservicio);
    });
}
// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function OCVactualizarOrden(accion, idservicio) {
  $.ajax({
    url: "/actualizar-orden-compra-cv/" + idservicio + "/",
    type: "GET",
    data: { accion: accion },
    timeout: 15000,
    success: function (data, textStatus, xhr) {
      var mensaje = "La orden ha sido actualizada exitosamente";
      if (accion === "aprobar") {
        mensaje = "La orden de compra ha sido APROBADA exitosamente";
      } else if (accion === "vb") {
        mensaje = "La orden de compra ha recibido VISTO BUENO exitosamente";
      } else if (accion === "anular") {
        mensaje = "La orden de compra ha sido ANULADA exitosamente";
      }

      Swal.fire({
        title: "¡Éxito!",
        text: mensaje,
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#3085d6",
      }).then(function () {
        // Cerrar modal y recargar datos
        $("#OCVmodalApproveOrders").modal("hide");
        OCVfiltrarPorArea(); // Recargar la tabla con los filtros actuales
      });
    },
    error: function (xhr, status, error) {
      var mensaje = "Ocurrió un error al actualizar la orden";
      if (xhr.status === 403) {
        mensaje = "No tienes permisos para realizar esta acción";
      } else if (xhr.status === 404) {
        mensaje = "La orden no fue encontrada";
      } else if (xhr.status === 500) {
        mensaje = "Error interno del servidor. Contacta al administrador.";
      } else if (status === "timeout") {
        mensaje = "La operación tardó demasiado tiempo. Inténtalo nuevamente.";
      }

      Swal.fire({
        title: "¡Error!",
        text: mensaje,
        icon: "error",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#d33",
      });
    },
  });
}

// =============================================
// FUNCIÓN PARA EXTRAER DATOS DEL USUARIO
// =============================================
function OCVextraerDatosUsuario() {
  let usuario = $("#OCVUser").val();
  let userId = $("#OCVUserId").val();

  console.log("👤 Usuario extraído del DOM:", usuario);
  console.log("🆔 OCVUserId extraído del DOM:", userId);

  // Verificar que tenemos el ID del usuario
  if (!userId) {
    console.error("❌ No se pudo obtener el ID del usuario del DOM");
    Swal.fire({
      title: "❌ Error de Sesión",
      text: "No se pudo identificar al usuario actual. Por favor, inicia sesión nuevamente.",
      icon: "error",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#e74c3c",
    });
    return;
  }

  // Consulta AJAX a la API para obtener datos de todos los usuarios (sin filtros)
  $.ajax({
    url: "/rrhh/usuario-area/",
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log("📡 Respuesta de la API:", response);

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
            return false; // Salir del bucle cuando se encuentra
          }
        });

        if (usuarioEncontrado) {
          console.log("✅ Usuario encontrado en la API:", usuarioEncontrado);

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

          console.log(
            "📋 Datos del usuario almacenados globalmente:",
            datosUsuario
          );

          // Validar permisos según el cargo
          const tienePermisos = OCVvalidarPermisosPorCargo(
            usuarioEncontrado.IDCARGO
          );

          if (tienePermisos) {
            console.log("🔓 Permisos validados - Inicializando tabla");
            // Solo inicializar la tabla si tiene permisos
            setTimeout(function () {
              OCVinicializarTabla();
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
function OCVactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#OCVcontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#OCVpanelSeleccion").show();
    $("#OCVbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#OCVpanelSeleccion").hide();
    $("#OCVbtnAprobacionMasiva").prop("disabled", true);

    // Resetear el botón a su estado original cuando no hay selecciones
    $("#OCVtextoBtnMasivo").text("Aprobar Masivo");
    $("#OCVbtnAprobacionMasiva i")
      .removeClass()
      .addClass("fa fa-check-circle mr-1");
    $("#OCVbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  }
}

// Función para actualizar texto del botón según el estado
function OCVactualizarTextoBtnMasivo(estado) {
  var texto = "";
  var icono = "";

  console.log("🔄 Actualizando texto del botón para estado:", estado);

  if (estado === "V1") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#OCVbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  } else if (estado === "PENDIENTE" || estado === "PE") {
    texto = "VB Masivo";
    icono = "fa-eye";
    $("#OCVbtnAprobacionMasiva")
      .removeClass("btn-success")
      .addClass("btn-warning");
  } else {
    texto = "Procesar Masivo";
    icono = "fa-cogs";
    $("#OCVbtnAprobacionMasiva")
      .removeClass("btn-success btn-warning")
      .addClass("btn-info");
  }

  $("#OCVtextoBtnMasivo").text(texto);
  $("#OCVbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");

  console.log("✅ Texto del botón actualizado a:", texto);
}

// Función para manejar selección individual
function OCVmanejarSeleccionIndividual(checkbox) {
  var $checkbox = $(checkbox);
  var idorden = $checkbox.val();
  var estado = $checkbox.data("estado");
  var $row = $checkbox.closest("tr");

  if ($checkbox.is(":checked")) {
    // Verificar si es el primer registro o si tiene el mismo estado
    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = estado;
      OCVactualizarTextoBtnMasivo(estado);
    } else if (estadoActualSeleccionado !== estado) {
      // Desmarcar el checkbox si el estado es diferente
      $checkbox.prop("checked", false);

      Swal.fire({
        title: "⚠️ Estados Diferentes",
        text:
          "Solo puedes seleccionar registros con el mismo estado. Estado actual: " +
          estadoActualSeleccionado,
        icon: "warning",
        confirmButtonText: "Entendido",
        confirmButtonColor: "#f39c12",
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
  var totalCheckboxes = $(".row-checkbox-OCV").length;
  var checkedCheckboxes = $(".row-checkbox-OCV:checked").length;

  if (checkedCheckboxes === 0) {
    $("#OCVcheckboxSelectAll").prop("checked", false).prop("indeterminate", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#OCVcheckboxSelectAll").prop("checked", true).prop("indeterminate", false);
  } else {
    $("#OCVcheckboxSelectAll").prop("checked", false).prop("indeterminate", true);
  }

  OCVactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function OCVmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-OCV").each(function () {
    var $checkbox = $(this);
    var estado = $checkbox.data("estado");
    var idorden = $checkbox.val();
    var $row = $checkbox.closest("tr");

    if (seleccionar) {
      if (registrosSeleccionados.length === 0) {
        estadoActualSeleccionado = estado;
        OCVactualizarTextoBtnMasivo(estado);
      }

      // Solo seleccionar si tiene el mismo estado que el primero
      if (estadoActualSeleccionado === estado) {
        $checkbox.prop("checked", true);
        registrosSeleccionados.push({
          idorden: idorden,
          estado: estado,
        });
        $row.addClass("row-selected");
      }
    } else {
      $checkbox.prop("checked", false);
      $row.removeClass("row-selected");
    }
  });

  $("#OCVcheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  OCVactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function OCVejecutarAprobacionMasiva() {
  if (registrosSeleccionados.length === 0) {
    Swal.fire({
      title: "⚠️ Sin Selección",
      text: "Debes seleccionar al menos un registro para procesar.",
      icon: "warning",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#f39c12",
    });
    return;
  }

  var accion = "";
  var textoConfirmacion = "";

  console.log(
    "🚀 Ejecutando aprobación masiva para estado:",
    estadoActualSeleccionado
  );

  if (estadoActualSeleccionado === "V1") {
    accion = "aprobar";
    textoConfirmacion =
      "¿Estás seguro de APROBAR " +
      registrosSeleccionados.length +
      " orden(es) de compra?";
  } else if (
    estadoActualSeleccionado === "PENDIENTE" ||
    estadoActualSeleccionado === "PE"
  ) {
    accion = "vb";
    textoConfirmacion =
      "¿Estás seguro de dar VISTO BUENO a " +
      registrosSeleccionados.length +
      " orden(es) de compra?";
  } else {
    Swal.fire({
      title: "⚠️ Estado No Válido",
      text: "El estado seleccionado no permite aprobación masiva.",
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
      OCVprocesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function OCVprocesarAprobacionMasiva(accion) {
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
          url: "/actualizar-orden-compra-cv/" + registro.idorden + "/",
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
              error: xhr.status + ": " + error,
            });
            resolve({
              success: false,
              idorden: registro.idorden,
              error: error,
            });
          },
        });
      }, index * 200); // Delay de 200ms entre cada petición
    });
  });

  // Cuando todas las promesas se resuelvan
  Promise.all(promesas).then(function (resultados) {
    var titulo = "";
    var mensaje = "";
    var icono = "";

    if (errores === 0) {
      titulo = "✅ Éxito Total";
      mensaje =
        "Se procesaron exitosamente " +
        procesados +
        " de " +
        totalRegistros +
        " registros.";
      icono = "success";
    } else if (procesados > 0) {
      titulo = "⚠️ Éxito Parcial";
      mensaje =
        "Se procesaron " +
        procesados +
        " de " +
        totalRegistros +
        " registros. " +
        errores +
        " fallaron.";
      icono = "warning";
    } else {
      titulo = "❌ Error Total";
      mensaje = "No se pudo procesar ningún registro. Todos fallaron.";
      icono = "error";
    }

    Swal.fire({
      title: titulo,
      text: mensaje,
      icon: icono,
      confirmButtonText: "Aceptar",
      confirmButtonColor: "#3085d6",
    }).then(function () {
      // Limpiar selecciones y recargar tabla
      registrosSeleccionados = [];
      estadoActualSeleccionado = null;
      $("#OCVpanelSeleccion").hide();
      $("#OCVbtnAprobacionMasiva").prop("disabled", true);

      OCVfiltrarPorArea(); // Recargar la tabla
    });
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function OCVconfigurarEventosCheckbox() {
  // Eventos para checkboxes individuales
  $(".row-checkbox-OCV")
    .off("change")
    .on("change", function () {
      OCVmanejarSeleccionIndividual(this);
    });

  // Evento para checkbox "Seleccionar Todos" del header
  $("#OCVcheckboxSelectAll")
    .off("change")
    .on("change", function () {
      var isChecked = $(this).is(":checked");
      OCVmanejarSeleccionTodos(isChecked);
    });
}

// =============================================
// INICIALIZACIÓN CUANDO EL DOCUMENTO ESTÉ LISTO
// =============================================
window.initOComprasCVModule = function (scope) {
      const $scope = $(scope || document);
  // 2) evita duplicar handlers si cambias de tab
  $(document).off("show.bs.modal", "#OCVmodalApproveOrders");
  $(document).off("hide.bs.modal", "#OCVmodalApproveOrders");

  // 3) MutationObserver para OCOCVlblEstado
  const observerEstado = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.target.id === "OCVlblEstado") {
        const estado = (mutation.target.textContent || "").trim();
        if (!estado) return;

        $("#OCVbuttons-loading").addClass("d-none");
        const estadoLower = estado.toLowerCase();
        // if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
        //   $("#OCVbtn-aprobar").removeClass("d-none");
        // } else {
        //   $("#OCVbtn-aprobar").addClass("d-none");
        // }
        // console.log(' -1 OCVmodalApproveOrders show.bs.modal');

        $("#OCVbtn-aprobar").addClass("d-none");
        $("#OCVbtn-vb").addClass("d-none");

        // Mostramos según estado
        if (estadoLower === "pendiente" || estadoLower === "pe") {
          $("#OCVbtn-vb").removeClass("d-none"); // VISTO BUENO
        } else if (estadoLower === "vº bº 1") {
          $("#OCVbtn-aprobar").removeClass("d-none"); // APROBAR
        }
        console.log(' -1 PSOCmodalApproveOrders show.bs.modal');
      }
    });
  });
  // 4) Evento al abrir modal
  $(document).on("show.bs.modal", "#OCVmodalApproveOrders", function () {
    $("#OCVbuttons-loading").removeClass("d-none");
    $("#OCVbtn-aprobar").addClass("d-none");

    const elementoEstado = document.getElementById("OCVlblEstado");
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

        $("#OCVbuttons-loading").addClass("d-none");

        const estadoLower = estadoActual.toLowerCase();
        // if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
        //   $("#OCVbtn-aprobar").removeClass("d-none");
        // } else {
        //   $("#OCVbtn-aprobar").addClass("d-none");
        // }

        // Ocultamos ambos botones primero
        $("#OCVbtn-aprobar").addClass("d-none");
        $("#OCVbtn-vb").addClass("d-none");

        // Mostramos según estado
        if (estadoLower === "pendiente" || estadoLower === "pe") {
          $("#OCVbtn-vb").removeClass("d-none"); // VISTO BUENO
        } else if (estadoLower === "vº bº 1") {
          $("#OCVbtn-aprobar").removeClass("d-none"); // APROBAR
        }
      }, 500);
    }
  });

  // 5) Evento al cerrar modal
 $(document).on("hide.bs.modal", "#OCVmodalApproveOrders", function () {
  observerEstado.disconnect();
});
  
   // Carga combos / data inicial
   OCVcargarAreas();

   // Binds (tus .off() evitan duplicados)
   OCVconfigurarEventos();
   OCVconfigurarSeleccionFila();

   // Carga inicial de tabla (usa filtro por área por defecto)
   //PCPSOCOCVfiltrarPorArea();
   OCVextraerDatosUsuario();
};