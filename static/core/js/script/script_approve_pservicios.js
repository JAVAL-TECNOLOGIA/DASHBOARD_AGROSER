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
function PSvalidarPermisosPorCargo(idCargo) {
  console.log("🔍 Validando permisos para IDCARGO:", idCargo);

  switch (parseInt(idCargo)) {
    case 8:
      // IDCARGO 8: Solo registros con estado "V1"
      estadosPermitidos = ["V1"];
      permisoValidado = true;
      console.log("✅ Usuario con IDCARGO 8: Puede ver registros en estado V1");
      return true;

    case 7:
    case 6:
      // IDCARGO 7 o 6: Solo registros con estado "PE" (Pendiente)
      estadosPermitidos = ["PE"];
      permisoValidado = true;
      console.log(
        "✅ Usuario con IDCARGO",
        idCargo + ": Puede ver registros en estado PE"
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
function PSobtenerUrlConEstados(area) {
  if (!permisoValidado || estadosPermitidos.length === 0) {
    // Si no hay permisos, retornar URL que no devuelva datos
    return "/approve_pservicios_log_filter/" + area + "/SINPERMISOS/";
  }

  // Construir URL con estados permitidos
  var estadosStr = estadosPermitidos.join(",");
  return "/approve_pservicios_log_filter/" + area + "/" + estadosStr + "/";
}
// =============================================
function PScargarAreas() {
  $.get("/approve_almacen_areas", function (data) {
    $("#PSselectApproveArea").append("<option value='0'>Todos</option>");
    $.each(data, function (index, value) {
      $("#PSselectApproveArea").append(
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
function PSinicializarTabla() {
  // Validar permisos antes de cargar datos
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden cargar datos: permisos no validados");
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#PSpanelSeleccion").hide();
  $("#PSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#PStableApproveOrders")) {
    $("#PStableApproveOrders").DataTable().clear().destroy();
    $("#PStableApproveOrders tbody").empty();
  }

  var urlConEstados = PSobtenerUrlConEstados(0); // 0 = Todas las áreas

  console.log("📊 Inicializando tabla con URL:", urlConEstados);

  table_show = $("#PStableApproveOrders").DataTable({
    ajax: {
      url: urlConEstados,
      dataSrc: "",
    },
    searching: false,
    lengthChange: false,
    pageLength: 10,
    ordering: true,
    order: [[1, "desc"]], // Ordenar por item (columna 1, ya que checkbox es 0)
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
      { data: "item" }, // 1 - Item
      {
        data: "estado",
        render: function (data, type, row) {
          return (
            '<span class="badge badge-primary" style="font-size: 1em;">' +
            data +
            "</span>"
          );
        },
      }, // 2 - Estado
      { data: "fecha" },
      { data: "moneda" }, // 5 - Moneda
      { data: "total" }, // 6 - Importe
      { data: "servicio_descripcion" }, // 8 - Servicio
      { data: "observaciones" },
      { data: "area" }, // 7 - Área
      { data: "idconsumidor" },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-PS" value="' +
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
      PSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function PSfiltrarPorArea() {
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

  var area = $("#PSselectApproveArea").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#PSpanelSeleccion").hide();
  $("#PSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#PStableApproveOrders")) {
    $("#PStableApproveOrders").DataTable().clear().destroy();
    $("#PStableApproveOrders tbody").empty();
  }

  var urlConEstados = PSobtenerUrlConEstados(area);

  console.log("🔍 Filtrando área", area, "con URL:", urlConEstados);

  table_show = $("#PStableApproveOrders").DataTable({
    ajax: {
      url: urlConEstados,
      dataSrc: "",
    },
    searching: false,
    lengthChange: false,
    pageLength: 10,
    ordering: true,
    order: [[1, "desc"]], // Ordenar por item (columna 1, ya que checkbox es 0)
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
      { data: "item" }, // 1 - Item
      {
        data: "estado",
        render: function (data, type, row) {
          return (
            '<span class="badge badge-primary" style="font-size: 1em;">' +
            data +
            "</span>"
          );
        },
      }, // 2 - Estado
      { data: "fecha" },
      { data: "moneda" }, // 5 - Moneda
      { data: "total" }, // 6 - Importe
      { data: "servicio_descripcion" }, // 8 - Servicio
      { data: "observaciones" },
      { data: "area" }, // 7 - Área
      { data: "idconsumidor" },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-PS" value="' +
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
      PSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function PSconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#PSbtnApproveFilter").off("click");
  $("#PSbtnAprobacionMasiva").off("click");
  $("#PSbtnSeleccionarTodos").off("click");
  $("#PSbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#PSbtnApproveFilter").click(function () {
    PSfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#PSbtnAprobacionMasiva").click(function () {
    PSejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#PSbtnSeleccionarTodos").click(function () {
    PSmanejarSeleccionTodos(true);
  });

  $("#PSbtnDeseleccionarTodos").click(function () {
    PSmanejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function PSconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#PStableApproveOrders tbody").off("dblclick");

  $("#PStableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Prevenir el doble click si se hizo click en un checkbox
    if (
      $(e.target).hasClass("form-check-input") ||
      $(e.target).closest(".form-check").length > 0
    ) {
      return;
    }

    var row = table_show.row(this).data();
    var $tr = $(this);

    // Obtener los datos desde los atributos data o desde row data
    var idservicio = $tr.attr("data-idorden") || row["idorden"];
    var documento = $tr.attr("data-documento") || row["documento"];

    // Remover event listeners anteriores de los botones para evitar duplicación
    $("#PSbtn-aprobar, #PSbtn-vb, #PSbtn-anular").off("click");

    if (documento == "COMPRA") {
      PSabrirModalCompra(idservicio);
    } else if (documento == "SERVICIO") {
      PSabrirModalServicio(idservicio);
    }

    // Configurar botones del modal
    PSconfigurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE COMPRA
// =============================================
function PSabrirModalCompra(idorden) {
  $("#PSmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_almacen_log_detail_purchase/" + idorden + "/",
    function (data) {
      $("#PSlblProveedor").html(data[0]["proveedor"]);
      $("#PSlblRuc").html(data[0]["ruc"]);
      $("#PSlblCondicion").html(data[0]["formapago"]);
      $("#PSlblResponsable").html(data[0]["responsable"]);
      $("#PSlblTotal").html(data[0]["total_oc"]);
      $("#PStableBodyApproveOrdersLogDetail").html("");
      $.each(data, function (index, value) {
        $("#PStableApproveOrdersLogDetail").append(
          "<tr><td>" +
            value["consumidor"] +
            "</td><td>" +
            value["idproducto"] +
            "</td><td>" +
            value["producto"] +
            "</td><td>" +
            value["idmedida"] +
            "</td><td>" +
            value["cantidad"] +
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
function PSabrirModalServicio(idorden) {
  $("#PSmodalApproveOrders").modal("toggle");
  $.get("/approve_pservicios_log_detail_service/" + idorden, function (data) {
    $("#PSlblArea").html(data[0]["area"]);
    $("#PSlblEstado").html(data[0]["estado"].toUpperCase());
    $("#PSlblObservacion").html(data[0]["observacion"]);
    $("#PSlblResponsable").html(data[0]["responsable"]);
    $("#PSlblTotal").html(data[0]["sumaTotal"]);
    $("#PStableBodyApproveOrdersLogDetail").html("");
    $.each(data, function (index, value) {
      $("#PStableApproveOrdersLogDetail").append(
        "<tr><td>" +
          value["consumidor"] +
          "</td><td>" +
          value["idproducto"] +
          "</td><td>" +
          value["producto"] +
          "</td><td>" +
          value["idmedida"] +
          "</td><td>" +
          value["cantidad"] +
          "</td><td>" +
          value["moneda"] +
          "</td><td>" +
          value["precio"] +
          "</td><td>" +
          value["total"] +
          "</td></tr>"
      );
    });
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR BOTONES DEL MODAL
// =============================================
function PSconfigurarBotonesModal(idservicio) {
  $("#PSbtn-aprobar").click(function () {
    PSactualizarOrden("aprobar", idservicio);
  });

  $("#PSbtn-vb").click(function () {
    PSactualizarOrden("vb", idservicio);
  });

  $("#PSbtn-anular").click(function () {
    PSactualizarOrden("anular", idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function PSactualizarOrden(accion, idservicio) {
  $.ajax({
    url: "/actualizar-orden-pservicios/" + idservicio + "/",
    type: "GET",
    data: { accion: accion },
    timeout: 15000, // 15 segundos de timeout
    success: function (data, textStatus, xhr) {
      console.log("✅ Orden actualizada correctamente:", idservicio);
      console.log("Respuesta del servidor:", data);
      console.log("Status HTTP:", xhr.status);

      // Verificar si la respuesta es JSON con success: true
      let mensaje = "El Pedido de Servicio ha sido actualizado exitosamente.";

      if (typeof data === "object" && data.success) {
        mensaje = data.message || mensaje;
      } else if (
        typeof data === "string" &&
        data.includes("ha sido actualizado")
      ) {
        mensaje = data;
      }

      Swal.fire({
        title: "¡Éxito!",
        text: mensaje,
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#3085d6",
      });

      // Recargar tabla solo después de completar la acción individual
      PSinicializarTabla();
      $("#PSmodalApproveOrders").modal("hide");
    },
    error: function (xhr, status, error) {
      console.error("❌ Error al actualizar orden:", idservicio);
      console.error("Status:", status);
      console.error("Error:", error);
      console.error("Response:", xhr.responseText);
      console.error("Status HTTP:", xhr.status);

      var mensaje = "Ocurrió un error al actualizar el pedido de Servicio.";

      if (status === "timeout") {
        mensaje =
          "La operación tardó demasiado tiempo. Verifica si el registro se actualizó correctamente.";
      } else if (xhr.status === 500) {
        // Intentar parsear la respuesta JSON de error
        try {
          var errorData = JSON.parse(xhr.responseText);
          mensaje =
            "Error del servidor: " +
            (errorData.error || "Error interno del servidor");
        } catch (e) {
          mensaje = "Error interno del servidor. Contacta al administrador.";
        }
      } else if (xhr.status === 404) {
        mensaje = "El pedido no fue encontrado o la URL es incorrecta.";
      } else if (xhr.status === 400) {
        // Intentar parsear la respuesta JSON de error
        try {
          var errorData = JSON.parse(xhr.responseText);
          mensaje =
            "Solicitud incorrecta: " +
            (errorData.error || "Error en la solicitud");
        } catch (e) {
          mensaje = "Error en la solicitud. Verifica los datos enviados.";
        }
      } else if (xhr.status === 0) {
        mensaje = "Error de conexión. Verifica tu conexión a internet.";
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

// =============================================
// FUNCIÓN PARA EXTRAER DATOS DEL USUARIO
// =============================================
function PSextraerDatosUsuario() {
  let usuario = $("#PSUser").val();
  let userId = $("#PSUserId").val();

  console.log("Usuario logueado:", usuario);
  console.log("PSUser ID logueado:", userId);

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
          const tienePermisos = PSvalidarPermisosPorCargo(
            usuarioEncontrado.IDCARGO
          );

          if (tienePermisos) {
            // Solo inicializar la tabla si tiene permisos
            setTimeout(function () {
              PSinicializarTabla();
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
function PSactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#PScontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#PSpanelSeleccion").slideDown(300);
    $("#PSbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#PSpanelSeleccion").slideUp(300);
    $("#PSbtnAprobacionMasiva").prop("disabled", true);
    estadoActualSeleccionado = null;
  }
}

// Función para actualizar texto del botón según el estado
function PSactualizarTextoBtnMasivo(estado) {
  var texto = "";
  var icono = "";

  if (estado === "V1") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#PSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  } else if (estado === "PE") {
    texto = "Dar Visto Bueno";
    icono = "fa-eye";
    $("#PSbtnAprobacionMasiva")
      .removeClass("btn-success")
      .addClass("btn-warning");
  }

  $("#PStextoBtnMasivo").text(texto);
  $("#PSbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
}

// Función para manejar selección individual
function PSmanejarSeleccionIndividual(checkbox) {
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
        row: $row,
      });

      estadoActualSeleccionado = estado;
      $row.addClass("row-selected");
      PSactualizarTextoBtnMasivo(estado);

      console.log("✅ Registro seleccionado:", idorden, "Estado:", estado);
    } else {
      // No permitir selección de estados diferentes
      $checkbox.prop("checked", false);
      Swal.fire({
        title: "⚠️ Selección no válida",
        text:
          "No puedes seleccionar registros con estados diferentes. Actual: " +
          estadoActualSeleccionado,
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

    console.log("❌ Registro deseleccionado:", idorden);
  }

  // Actualizar checkbox "Seleccionar Todos"
  var totalCheckboxes = $(".row-checkbox-PS").length;
  var checkedCheckboxes = $(".row-checkbox-PS:checked").length;

  if (checkedCheckboxes === 0) {
    $("#PScheckboxSelectAll").prop("indeterminate", false).prop("checked", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#PScheckboxSelectAll").prop("indeterminate", false).prop("checked", true);
  } else {
    $("#PScheckboxSelectAll").prop("indeterminate", true).prop("checked", false);
  }

  PSactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function PSmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-PS").each(function () {
    var $checkbox = $(this);
    var $row = $checkbox.closest("tr");

    if (seleccionar) {
      var estado = $checkbox.data("estado");
      var idorden = $checkbox.val();

      // Solo seleccionar si es el primer registro o tiene el mismo estado
      if (
        estadoActualSeleccionado === null ||
        estadoActualSeleccionado === estado
      ) {
        $checkbox.prop("checked", true);
        $row.addClass("row-selected");

        registrosSeleccionados.push({
          idorden: idorden,
          estado: estado,
          row: $row,
        });

        if (estadoActualSeleccionado === null) {
          estadoActualSeleccionado = estado;
          PSactualizarTextoBtnMasivo(estado);
        }
      }
    } else {
      $checkbox.prop("checked", false);
      $row.removeClass("row-selected");
    }
  });

  $("#PScheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  PSactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function PSejecutarAprobacionMasiva() {
  if (registrosSeleccionados.length === 0) {
    Swal.fire({
      title: "⚠️ Sin Selección",
      text: "No hay registros seleccionados para procesar.",
      icon: "warning",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#f39c12",
    });
    return;
  }

  var accion = "";
  var textoConfirmacion = "";

  if (estadoActualSeleccionado === "V1") {
    accion = "aprobar";
    textoConfirmacion =
      "¿Estás seguro de que deseas aprobar " +
      registrosSeleccionados.length +
      " registro(s)?";
  } else if (estadoActualSeleccionado === "PE") {
    accion = "vb";
    textoConfirmacion =
      "¿Estás seguro de que deseas dar visto bueno a " +
      registrosSeleccionados.length +
      " registro(s)?";
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
      PSprocesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function PSprocesarAprobacionMasiva(accion) {
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
    return new Promise((resolve) => {
      // Agregar delay progresivo entre requests
      setTimeout(() => {
        $.ajax({
          url: "/actualizar-orden-pservicios/" + registro.idorden + "/",
          type: "GET",
          data: { accion: accion },
          timeout: 15000, // 15 segundos de timeout
        })
          .done(function (response, textStatus, xhr) {
            procesados++;
            console.log("✅ Registro procesado:", registro.idorden);
            console.log("Respuesta:", response);
            console.log("Status HTTP:", xhr.status);

            // Verificar si la respuesta indica éxito
            let exitoso = false;
            if (typeof response === "object" && response.success) {
              exitoso = true;
            } else if (
              typeof response === "string" &&
              response.includes("ha sido actualizado")
            ) {
              exitoso = true;
            }

            resolve({
              success: exitoso,
              idorden: registro.idorden,
              response: response,
            });
          })
          .fail(function (xhr, status, error) {
            errores++;
            var errorMsg = "Error desconocido";

            console.error("❌ Error procesando registro:", registro.idorden);
            console.error("Status:", status, "Error:", error);
            console.error("Response:", xhr.responseText);
            console.error("Status HTTP:", xhr.status);

            if (status === "timeout") {
              errorMsg = "Timeout - La operación puede haberse completado";
            } else if (xhr.status === 500) {
              try {
                var errorData = JSON.parse(xhr.responseText);
                errorMsg =
                  "Error del servidor: " + (errorData.error || "Error interno");
              } catch (e) {
                errorMsg = "Error interno del servidor";
              }
            } else if (xhr.status === 404) {
              errorMsg = "Registro no encontrado o URL incorrecta";
            } else if (xhr.status === 400) {
              try {
                var errorData = JSON.parse(xhr.responseText);
                errorMsg =
                  "Solicitud incorrecta: " +
                  (errorData.error || "Error en datos");
              } catch (e) {
                errorMsg = "Error en la solicitud";
              }
            } else if (xhr.status === 0) {
              errorMsg = "Error de conexión";
            } else {
              errorMsg = status + " - " + error;
            }

            errorDetails.push({
              idorden: registro.idorden,
              error: errorMsg,
            });

            resolve({
              success: false,
              idorden: registro.idorden,
              error: errorMsg,
            });
          });
      }, index * 300); // 300ms de delay entre cada request
    });
  });

  // Cuando todas las promesas se resuelvan
  Promise.all(promesas).then(function (resultados) {
    // Limpiar selección
    registrosSeleccionados = [];
    estadoActualSeleccionado = null;
    $("#PSpanelSeleccion").hide();
    $("#PSbtnAprobacionMasiva").prop("disabled", true);

    // Mostrar resultado detallado
    if (errores === 0) {
      Swal.fire({
        title: "✅ Éxito Total",
        text: "Se procesaron correctamente " + procesados + " registro(s).",
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#28a745",
      }).then(() => {
        // Recargar tabla una sola vez al final
        PSinicializarTabla();
      });
    } else if (procesados > 0) {
      // Mostrar detalles de errores si los hay
      let detalleErrores = "";
      if (errorDetails.length > 0 && errorDetails.length <= 5) {
        detalleErrores = "\n\nErrores encontrados:\n";
        errorDetails.forEach(function (error, index) {
          detalleErrores += `- ID ${error.idorden}: ${error.error}\n`;
        });
      } else if (errorDetails.length > 5) {
        detalleErrores = `\n\nSe encontraron ${errorDetails.length} errores. Revisa la consola para más detalles.`;
      }

      Swal.fire({
        title: "⚠️ Procesado con Errores",
        text:
          "Se procesaron " +
          procesados +
          " registro(s) correctamente y " +
          errores +
          " con errores." +
          detalleErrores,
        icon: "warning",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#f39c12",
      }).then(() => {
        // Recargar tabla una sola vez al final
        PSinicializarTabla();
      });
    } else {
      Swal.fire({
        title: "❌ Error Total",
        text: "No se pudo procesar ningún registro. Todos fallaron.",
        icon: "error",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#e74c3c",
      }).then(() => {
        // Recargar tabla una sola vez al final
        PSinicializarTabla();
      });
    }
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function PSconfigurarEventosCheckbox() {
  // Eventos para checkboxes individuales
  $(".row-checkbox-PS")
    .off("change")
    .on("change", function () {
      PSmanejarSeleccionIndividual(this);
    });

  // Evento para checkbox "Seleccionar Todos" del header
  $("#PScheckboxSelectAll")
    .off("change")
    .on("change", function () {
      var seleccionar = $(this).is(":checked");
      PSmanejarSeleccionTodos(seleccionar);
    });
}

// =============================================
// INIT PARA USO EN TABS/PARTIALS (NO AUTOEJECUTA)
// Llama esto DESPUÉS de inyectar el partial en el DOM.
// Ejemplo: window.initPServiciosModule();
// =============================================
window.initPServiciosModule = function (scope) {
      const $scope = $(scope || document);
  // 2) evita duplicar handlers si cambias de tab
  $(document).off("show.bs.modal", "#PSmodalApproveOrders");
  $(document).off("hide.bs.modal", "#PSmodalApproveOrders");

  // 3) MutationObserver para lblEstado
  const observerEstado = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.target.id === "PSlblEstado") {
        const estado = (mutation.target.textContent || "").trim();
        if (!estado) return;

        $("#PSbuttons-loading").addClass("d-none");
        const estadoLower = estado.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#PSbtn-aprobar").removeClass("d-none");
        } else {
          $("#PSbtn-aprobar").addClass("d-none");
        }
        console.log(' -1 PSmodalApproveOrders show.bs.modal');
      }
    });
  });
  // 4) Evento al abrir modal
  $(document).on("show.bs.modal", "#PSmodalApproveOrders", function () {
    $("#PSbuttons-loading").removeClass("d-none");
    $("#PSbtn-aprobar").addClass("d-none");

    const elementoEstado = document.getElementById("PSlblEstado");
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

        $("#PSbuttons-loading").addClass("d-none");

        const estadoLower = estadoActual.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#PSbtn-aprobar").removeClass("d-none");
        } else {
          $("#PSbtn-aprobar").addClass("d-none");
        }
      }, 500);
    }
  });

  // 5) Evento al cerrar modal
 $(document).on("hide.bs.modal", "#PSmodalApproveOrders", function () {
  observerEstado.disconnect();
});
  
   // Carga combos / data inicial
   PScargarAreas();

   // Binds (tus .off() evitan duplicados)
   PSconfigurarEventos();
   PSconfigurarSeleccionFila();

   // Carga inicial de tabla (usa filtro por área por defecto)
   //PCPSfiltrarPorArea();
   PSextraerDatosUsuario();
};