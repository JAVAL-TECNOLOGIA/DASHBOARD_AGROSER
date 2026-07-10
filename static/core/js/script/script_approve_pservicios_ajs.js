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
function AJPSvalidarPermisosPorCargo(idCargo) {
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
function AJPSobtenerUrlConEstados(area) {
  if (!permisoValidado || estadosPermitidos.length === 0) {
    // Si no hay permisos, retornar URL que no devuelva datos
    return "/approve_pservicios_log_filter_ajs/" + area + "/SINPERMISOS/";
  }

  // Construir URL con estados permitidos
  var estadosStr = estadosPermitidos.join(",");
  return "/approve_pservicios_log_filter_ajs/" + area + "/" + estadosStr + "/";
}
// =============================================
function AJPScargarAreas() {
  $.get("/approve_almacen_areas_ajs", function (data) {
    $("#AJPSselectApproveArea").append("<option value='0'>Todos</option>");
    $.each(data, function (index, value) {
      $("#AJPSselectApproveArea").append(
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
function AJPSinicializarTabla() {
  // Validar permisos antes de cargar datos
  if (!permisoValidado) {
    console.warn("⚠️ No se pueden cargar datos: permisos no validados");
    return;
  }

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#AJPSpanelSeleccion").hide();
  $("#AJPSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#AJPStableApproveOrders")) {
    $("#AJPStableApproveOrders").DataTable().clear().destroy();
    $("#AJPStableApproveOrders tbody").empty();
  }

  var urlConEstados = AJPSobtenerUrlConEstados(0); // 0 = Todas las áreas

  console.log("📊 Inicializando tabla con URL:", urlConEstados);

  table_show = $("#AJPStableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-PSAJS" value="' +
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
      AJPSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function AJPSfiltrarPorArea() {
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

  var area = $("#AJPSselectApproveArea").val() || 0;

  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#AJPSpanelSeleccion").hide();
  $("#AJPSbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#AJPStableApproveOrders")) {
    $("#AJPStableApproveOrders").DataTable().clear().destroy();
    $("#AJPStableApproveOrders tbody").empty();
  }

  var urlConEstados = AJPSobtenerUrlConEstados(area);

  console.log("🔍 Filtrando área", area, "con URL:", urlConEstados);

  table_show = $("#AJPStableApproveOrders").DataTable({
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
            '<input type="checkbox" class="form-check-input row-checkbox-PSAJS" value="' +
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
      AJPSconfigurarEventosCheckbox();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function AJPSconfigurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#AJPSbtnApproveFilter").off("click");
  $("#AJPSbtnAprobacionMasiva").off("click");
  $("#AJPSbtnSeleccionarTodos").off("click");
  $("#AJPSbtnDeseleccionarTodos").off("click");

  // Evento del botón filtrar
  $("#AJPSbtnApproveFilter").click(function () {
    AJPSfiltrarPorArea();
  });

  // Evento del botón de aprobación masiva
  $("#AJPSbtnAprobacionMasiva").click(function () {
    AJPSejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#AJPSbtnSeleccionarTodos").click(function () {
    AJPSmanejarSeleccionTodos(true);
  });

  $("#AJPSbtnDeseleccionarTodos").click(function () {
    AJPSmanejarSeleccionTodos(false);
  });
}

// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function AJPSconfigurarSeleccionFila() {
  // Remover event listeners anteriores para evitar duplicación
  $("#AJPStableApproveOrders tbody").off("dblclick");

  $("#AJPStableApproveOrders tbody").on("dblclick", "tr", function (e) {
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
    $("#AJPSbtn-aprobar, #AJPSbtn-vb, #AJPSbtn-anular").off("click");

    if (documento == "COMPRA") {
      AJPSabrirModalCompra(idservicio);
    } else if (documento == "SERVICIO") {
      AJPSabrirModalServicio(idservicio);
    }

    // Configurar botones del modal
    AJPSconfigurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE COMPRA
// =============================================
function AJPSabrirModalCompra(idorden) {
  $("#AJPSmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_almacen_log_detail_purchase_ajs/" + idorden + "/",
    function (data) {
      $("#AJPSlblProveedor").html(data[0]["proveedor"]);
      $("#AJPSlblRuc").html(data[0]["ruc"]);
      $("#AJPSlblCondicion").html(data[0]["formapago"]);
      $("#AJPSlblResponsable").html(data[0]["responsable"]);
      $("#AJPSlblTotal").html(data[0]["total_oc"]);
      $("#AJPStableBodyApproveOrdersLogDetail").html("");
      $.each(data, function (index, value) {
        $("#AJPStableApproveOrdersLogDetail").append(
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
function AJPSabrirModalServicio(idorden) {
  $("#AJPSmodalApproveOrders").modal("toggle");
  $.get(
    "/approve_pservicios_log_detail_service_ajs/" + idorden,
    function (data) {
      $("#AJPSlblArea").html(data[0]["area"]);
      $("#AJPSlblEstado").html(data[0]["estado"].toUpperCase());
      $("#AJPSlblObservacion").html(data[0]["observacion"]);
      $("#AJPSlblResponsable").html(data[0]["responsable"]);
      $("#AJPSlblTotal").html(data[0]["sumaTotal"]);
      $("#AJPStableBodyApproveOrdersLogDetail").html("");
      $.each(data, function (index, value) {
        $("#AJPStableApproveOrdersLogDetail").append(
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
    }
  );
}

// =============================================
// FUNCIÓN PARA CONFIGURAR BOTONES DEL MODAL
// =============================================
function AJPSconfigurarBotonesModal(idservicio) {
  $("#AJPSbtn-aprobar").click(function () {
    AJPSactualizarOrden("aprobar", idservicio);
  });

  $("#AJPSbtn-vb").click(function () {
    AJPSactualizarOrden("vb", idservicio);
  });

  $("#AJPSbtn-anular").click(function () {
    AJPSactualizarOrden("anular", idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function AJPSactualizarOrden(accion, idservicio) {
  $.ajax({
    url: "/actualizar-orden-pservicios_ajs/" + idservicio + "/",
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
      AJPSinicializarTabla();
      $("#AJPSmodalApproveOrders").modal("hide");
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
function AJPSextraerDatosUsuario() {
  let usuario = $("#AJPSUser").val();
  let userId = $("#AJPSUserId").val();

  console.log("Usuario logueado:", usuario);
  console.log("AJPSUser ID logueado:", userId);

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
          const tienePermisos = AJPSvalidarPermisosPorCargo(
            usuarioEncontrado.IDCARGO
          );

          if (tienePermisos) {
            // Solo inicializar la tabla si tiene permisos
            setTimeout(function () {
              AJPSinicializarTabla();
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
function AJPSactualizarContadorSeleccion() {
  var cantidad = registrosSeleccionados.length;
  $("#AJPScontadorSeleccion").text(
    cantidad +
      " registro" +
      (cantidad !== 1 ? "s" : "") +
      " seleccionado" +
      (cantidad !== 1 ? "s" : "")
  );

  // Mostrar/ocultar panel de selección
  if (cantidad > 0) {
    $("#AJPSpanelSeleccion").slideDown(300);
    $("#AJPSbtnAprobacionMasiva").prop("disabled", false);
  } else {
    $("#AJPSpanelSeleccion").slideUp(300);
    $("#AJPSbtnAprobacionMasiva").prop("disabled", true);
    estadoActualSeleccionado = null;
  }
}

// Función para actualizar texto del botón según el estado
function AJPSactualizarTextoBtnMasivo(estado) {
  var texto = "";
  var icono = "";

  if (estado === "V1") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#AJPSbtnAprobacionMasiva")
      .removeClass("btn-warning")
      .addClass("btn-success");
  } else if (estado === "PE") {
    texto = "Dar Visto Bueno";
    icono = "fa-eye";
    $("#AJPSbtnAprobacionMasiva")
      .removeClass("btn-success")
      .addClass("btn-warning");
  }

  $("#AJPStextoBtnMasivo").text(texto);
  $("#AJPSbtnAprobacionMasiva i")
    .removeClass()
    .addClass("fa " + icono + " mr-1");
}

// Función para manejar selección individual
function AJPSmanejarSeleccionIndividual(checkbox) {
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
      AJPSactualizarTextoBtnMasivo(estado);

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
  var totalCheckboxes = $(".row-checkbox-PSAJS").length;
  var checkedCheckboxes = $(".row-checkbox-PSAJS:checked").length;

  if (checkedCheckboxes === 0) {
    $("#AJPScheckboxSelectAll").prop("indeterminate", false).prop("checked", false);
  } else if (checkedCheckboxes === totalCheckboxes) {
    $("#AJPScheckboxSelectAll").prop("indeterminate", false).prop("checked", true);
  } else {
    $("#AJPScheckboxSelectAll").prop("indeterminate", true).prop("checked", false);
  }

  AJPSactualizarContadorSeleccion();
}

// Función para seleccionar/deseleccionar todos
function AJPSmanejarSeleccionTodos(seleccionar) {
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;

  $(".row-checkbox-PSAJS").each(function () {
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
          AJPSactualizarTextoBtnMasivo(estado);
        }
      }
    } else {
      $checkbox.prop("checked", false);
      $row.removeClass("row-selected");
    }
  });

  $("#AJPScheckboxSelectAll")
    .prop("checked", seleccionar)
    .prop("indeterminate", false);
  AJPSactualizarContadorSeleccion();
}

// Función para realizar aprobación masiva
function AJPSejecutarAprobacionMasiva() {
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
      AJPSprocesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function AJPSprocesarAprobacionMasiva(accion) {
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
          url: "/actualizar-orden-pservicios_ajs/" + registro.idorden + "/",
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
    $("#AJPSpanelSeleccion").hide();
    $("#AJPSbtnAprobacionMasiva").prop("disabled", true);

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
        AJPSinicializarTabla();
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
        AJPSinicializarTabla();
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
        AJPSinicializarTabla();
      });
    }
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function AJPSconfigurarEventosCheckbox() {
  // Eventos para checkboxes individuales
  $(".row-checkbox-PSAJS")
    .off("change")
    .on("change", function () {
      AJPSmanejarSeleccionIndividual(this);
    });

  // Evento para checkbox "Seleccionar Todos" del header
  $("#AJPScheckboxSelectAll")
    .off("change")
    .on("change", function () {
      var seleccionar = $(this).is(":checked");
      AJPSmanejarSeleccionTodos(seleccionar);
    });
}

// =============================================
// INICIALIZACIÓN CUANDO EL DOCUMENTO ESTÉ LISTO
// =============================================
window.initPServiciosAJSModule = function (scope) {
      const $scope = $(scope || document);
  // 2) evita duplicar handlers si cambias de tab
  $(document).off("show.bs.modal", "#AJPSmodalApproveOrders");
  $(document).off("hide.bs.modal", "#AJPSmodalApproveOrders");

  // 3) MutationObserver para AJPSlblEstado
  const observerEstado = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.target.id === "AJPSlblEstado") {
        const estado = (mutation.target.textContent || "").trim();
        if (!estado) return;

        $("#AJPSbuttons-loading").addClass("d-none");
        const estadoLower = estado.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#AJPSbtn-aprobar").removeClass("d-none");
        } else {
          $("#AJPSbtn-aprobar").addClass("d-none");
        }
        console.log(' -1 AJPSmodalApproveOrders show.bs.modal');
      }
    });
  });
  // 4) Evento al abrir modal
  $(document).on("show.bs.modal", "#AJPSmodalApproveOrders", function () {
    $("#AJPSbuttons-loading").removeClass("d-none");
    $("#AJPSbtn-aprobar").addClass("d-none");

    const elementoEstado = document.getElementById("AJPSlblEstado");
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

        $("#AJPSbuttons-loading").addClass("d-none");

        const estadoLower = estadoActual.toLowerCase();
        if (estadoLower === "pendiente" || estadoLower === "vº bº 1" || estadoLower === "pe") {
          $("#AJPSbtn-aprobar").removeClass("d-none");
        } else {
          $("#AJPSbtn-aprobar").addClass("d-none");
        }
      }, 500);
    }
  });

  // 5) Evento al cerrar modal
 $(document).on("hide.bs.modal", "#AJPSmodalApproveOrders", function () {
  observerEstado.disconnect();
});
  
   // Carga combos / data inicial
   AJPScargarAreas();

   // Binds (tus .off() evitan duplicados)
   AJPSconfigurarEventos();
   AJPSconfigurarSeleccionFila();

   // Carga inicial de tabla (usa filtro por área por defecto)
   //PCPSPSCVAJPSfiltrarPorArea();
   AJPSextraerDatosUsuario();
};