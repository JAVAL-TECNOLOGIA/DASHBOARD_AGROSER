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
function CVcargarAreas() {
  // Evita cargar 2 veces si ya se cargó en esta sesión
  if ($("#CVselectApproveArea").data("loaded") === true) return;

$.get("/approve_almacen_areas", function (data) {
  $("#CVselectApproveArea").append("<option value='0'>Todos</option>");
  console.log($("#CVselectApproveArea").val());
  $.each(data, function (index, value) {
    $("#CVselectApproveArea").append(
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
function CVreturnApproveOrders() {
  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#CVpanelSeleccion").hide();
  $("#CVbtnAprobacionMasiva").prop("disabled", true);

  // Destruir la tabla existente si existe
  if ($.fn.DataTable.isDataTable("#CVtableApproveOrders")) {
    $("#CVtableApproveOrders").DataTable().destroy();
  }

  console.log("📊 Inicializando tabla de fitosanidad");

  table_show = $("#CVtableApproveOrders").DataTable({
    ajax: {
      url: "/approve_almacen_log/",
      dataSrc: function (json) {
        console.log("📦 Datos recibidos del servidor:", json);
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
      { data: "item", visible: false },
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
      { data: "documento" },
      { data: "num_documento" },
      { data: "area" },
      { data: "idorden", visible: false },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-FICV" ' +
            'data-id="' +
            row.idorden +
            '" data-estado="' +
            row.estado +
            '">' +
            '<label class="form-check-label"></label>' +
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
          // Agregar data attributes para facilitar la selección
          $(td).attr("data-row-id", rowData.idorden);
          $(td).attr("data-row-estado", rowData.estado);
        },
      },
    ],
    drawCallback: function () {
      // Configurar eventos de checkbox después de cada redibujado
      CVconfigurarEventosCheckbox();
      // Mantener selecciones anteriores
      CVmantenerSelecciones();
    },
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function CVreturnApproveOrdersFilter() {
  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#CVpanelSeleccion").hide();
  $("#CVbtnAprobacionMasiva").prop("disabled", true);

  documento = $("#CVselectApproveDocument").val();
  serie = $("#CVtxtApproveSerie").val();
  number = $("#CVtxtApproveNumber").val();
  area = $("#CVselectApproveArea").val() || 0; // Si no hay valor, usar 0

  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable("#CVtableApproveOrders")) {
    $("#CVtableApproveOrders").DataTable().destroy();
  }

  console.log("🔍 Filtrando fitosanidad área:", area);

  table_show = $("#CVtableApproveOrders").DataTable({
    ajax: {
      url: "/fitosanidad_log_filter_CV/" + area + "/",
      dataSrc: function (json) {
        console.log("📦 Datos filtrados recibidos:", json);
        return json;
      },
      error: function (xhr, error, code) {
        console.error("❌ Error al cargar datos:", error, code);
        console.error("❌ Respuesta del servidor:", xhr.responseText);
        alert(
          "Error al cargar los datos de fitosanidad. Revisa la consola para más detalles."
        );
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
      { data: "item", visible: true },
      { data: "fecha" },
      { data: "fecha_apl" },
      { data: "descripcion_producto" },
      { data: "descripcion_iac" },
      { data: "consumidor" },
      { data: "area" },
      {
        data: null,
        orderable: false,
        className: "text-center",
        width: "50px",
        render: function (data, type, row) {
          return (
            '<div class="form-check">' +
            '<input type="checkbox" class="form-check-input row-checkbox-FICV" ' +
            'data-id="' +
            row.idorden +
            '" data-estado="' +
            row.estado +
            '">' +
            '<label class="form-check-label"></label>' +
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
          // Agregar data attributes para facilitar la selección
          $(td).attr("data-row-id", rowData.idorden);
          $(td).attr("data-row-estado", rowData.estado);
        },
      },
    ],
    drawCallback: function () {
      // Configurar eventos de checkbox después de cada redibujado
      CVconfigurarEventosCheckbox();
      // Mantener selecciones anteriores
      CVmantenerSelecciones();
    },
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function CVreturnApproveOrdersDoc() {
  // Remover event listeners anteriores para evitar duplicación
  $("#CVbtnApproveShow").off("click");
  $("#CVbtnAprobacionMasiva").off("click");
  $("#CVbtnSeleccionarTodos").off("click");
  $("#CVbtnDeseleccionarTodos").off("click");

  $("#CVbtnApproveShow").click(function () {
    $("#CVtableApproveOrders tbody").html("");
    if ($("#CVchkShowInputsApproveOrders").prop("checked")) {
      CVreturnApproveOrders();
    } else {
      $("#CVtableApproveOrders tbody").html("");
      CVreturnApproveOrdersFilter();
    }
  });

  // Evento del botón de aprobación masiva
  $("#CVbtnAprobacionMasiva").click(function () {
    CVejecutarAprobacionMasiva();
  });

  // Eventos de los botones del panel de selección
  $("#CVbtnSeleccionarTodos").click(function () {
    CVmanejarSeleccionTodos(true);
  });

  $("#CVbtnDeseleccionarTodos").click(function () {
    CVmanejarSeleccionTodos(false);
  });
}
/*** CVreturnApproveOrders(url_aof, $("#CVselectApproveArea").val()); */
// =============================================
// FUNCIÓN PARA MANEJAR DOBLE CLICK EN FILAS
// =============================================
function CVselectRowLot() {
  // Remover event listeners anteriores para evitar duplicación
  $("#CVtableApproveOrders tbody").off("dblclick");

  $("#CVtableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Evitar que el doble click active el checkbox
    e.stopPropagation();

    var row = table_show.row(this).data();
    var idservicio = row["idorden"];

    // Para fitosanidad, siempre usar la API específica
    if (row["documento"] == "FITOSANIDAD") {
      $("#CVmodalApproveOrders").modal("toggle");
      console.log("🔍 Consultando detalle de fitosanidad para ID:", idservicio);

      $.get(
        "/approve_orders_log_detail_fitosanidad_CV/" + idservicio + "/",
        function (data) {
          console.log("📋 Datos de fitosanidad recibidos:", data);

          if (data && data.length > 0) {
            // Mostrar información del primer registro (área y responsable)
            $("#CVlblArea").html(data[0]["AREA"] || "-");
            $("#CVlblResponsable").html(data[0]["RESPONSABLE"] || "-");

            // Limpiar tabla de detalles
            $("#CVtableBodyApproveOrdersLogDetail").html("");

            // Llenar tabla con todos los productos
            $.each(data, function (index, value) {
              $("#CVtableApproveOrdersLogDetail").append(
                "<tr>" +
                  "<td>" +
                  (value["fecha_apl"] || "-") +
                  "</td>" +
                  "<td>" +
                  (value["IDCONSUMIDOR"] || "-") +
                  "</td>" +
                  "<td>" +
                  (value["IDPRODUCTO"] || "-") +
                  "</td>" +
                  "<td>" +
                  (value["DESCRIPCION"] || "-") +
                  "</td>" +
                  "<td>" +
                  (value["IDMEDIDA"] || "-") +
                  "</td>" +
                  "<td>" +
                  (value["CANTIDAD"] || "0") +
                  "</td>" +
                  "</tr>"
              );
            });
          } else {
            console.log("⚠️ No se encontraron datos para este registro");
            $("#CVlblArea").html("-");
            $("#CVlblResponsable").html("-");
            $("#CVtableBodyApproveOrdersLogDetail").html(
              '<tr><td colspan="6" class="text-center">No se encontraron detalles</td></tr>'
            );
          }
        }
      ).fail(function (xhr, status, error) {
        console.error("❌ Error al consultar detalle de fitosanidad:", error);
        $("#CVlblArea").html("-");
        $("#CVlblResponsable").html("-");
        $("#CVtableBodyApproveOrdersLogDetail").html(
          '<tr><td colspan="6" class="text-center text-danger">Error al cargar detalles</td></tr>'
        );
      });
    }

    // Configurar botones del modal
    CVconfigurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR BOTONES DEL MODAL
// =============================================
function CVconfigurarBotonesModal(idservicio) {
  // Remover event listeners anteriores
  $("#CVbtn-aprobar").off("click");
  $("#CVbtn-vb").off("click");
  $("#CVbtn-anular").off("click");

  $("#CVbtn-aprobar").click(function () {
    CVactualizarOrden("aprobar", idservicio);
  });

  $("#CVbtn-vb").click(function () {
    CVactualizarOrden("vb", idservicio);
  });

  $("#CVbtn-anular").click(function () {
    CVactualizarOrden("anular", idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ACTUALIZAR ORDEN
// =============================================
function CVactualizarOrden(accion, idservicio) {
  // Realiza una solicitud AJAX al servidor para actualizar la orden de servicio
  $.ajax({
    url: "/actualizar-orden-fitosanidad-CV/" + idservicio + "/",
    type: "GET", // Utiliza GET o POST según tu vista UpdateOrdenServicio
    data: { accion: accion },
    success: function (data) {
      reqinterno = JSON.stringify(data);
      reqinterno = reqinterno.substring(1, reqinterno.length - 1);
      //reqinterno = {"idreqinterno":"_6TC0UO78K43514","iddocumento":"REQ","idsucursal":"001","idalmacen":"001","serie":"0001","numero":"0021548","fecha":"20240124","estado":"AP","idarea":"003       ","idresponsable":"000025","dreqinterno":[{"item":"001","idproducto":"24000010086","descripcion":"CROP + PLUS","idmedida":"LTS","cantidad":1,"idconsumidor":"FLACA6"}]}
      console.log(reqinterno);
      // Configuración de la solicitud
      const requestOptions = {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // Ajusta el tipo de contenido según las necesidades de la API
          // Puedes agregar otros encabezados según los requisitos de la API
        },
        body: reqinterno, //JSON.stringify(data), // Convierte los datos a formato JSON
      };

      // URL del servicio que quieres consumir
      const url = "http://38.250.176.121:9000/api/crtReqinterno?dbName=CAMPOVERDE";
      // Realizar la solicitud POST
      fetch(url, requestOptions)
        .then((response) => response.json()) // Puedes cambiar a .text() si la respuesta no es JSON
        .then((data1) => {
          // Hacer algo con la respuesta
          console.log("Respuesta exitosa:", data1);
        })
        .catch((error) => {
          // Manejar errores
          console.error("Error en la solicitud:", error);
        });
      // muestra un mensaje de éxito u otra acción adecuada

      Swal.fire({
        icon: "success",
        title: "Actualización exitosa",
        text: "El requerimiento ha sido actualizado correctamente.",
        confirmButtonText: "Aceptar",
      });

      $("#CVmodalApproveOrders").modal("hide");
      // actualizar tabla
      $("#CVtableApproveOrders").DataTable().ajax.reload();
    },
    error: function (error) {
      // Maneja cualquier error, muestra un mensaje de error u otra acción adecuada
      alert("Ocurrió un error al actualizar el pedido de Servicio.");
    },
  });
}

// =============================================
// FUNCIONES PARA APROBACIÓN MASIVA
// =============================================

// Función para actualizar contador de selección
function CVactualizarContadorSeleccion() {
  var count = registrosSeleccionados.length;
  $("#CVcontadorSeleccion").text(
    count +
      " registro" +
      (count !== 1 ? "s" : "") +
      " seleccionado" +
      (count !== 1 ? "s" : "")
  );

  if (count > 0) {
    $("#CVpanelSeleccion").show();
    $("#CVbtnAprobacionMasiva").prop("disabled", false);

    // Mostrar información del estado seleccionado
    if (estadoActualSeleccionado) {
      var estadoTexto = "";
      switch (estadoActualSeleccionado) {
        case "PE":
          estadoTexto = " (Estado: Pendiente)";
          break;
        case "V1":
          estadoTexto = " (Estado: VoBo)";
          break;
        case "AP":
          estadoTexto = " (Estado: Aprobado)";
          break;
        case "AN":
          estadoTexto = " (Estado: Anulado)";
          break;
        default:
          estadoTexto = " (Estado: " + estadoActualSeleccionado + ")";
      }
      $("#CVestadoSeleccionInfo").text(estadoTexto);
      CVactualizarTextoBtnMasivo(estadoActualSeleccionado);
    }
  } else {
    $("#CVpanelSeleccion").hide();
    $("#CVbtnAprobacionMasiva").prop("disabled", true);
    estadoActualSeleccionado = null;
  }
}

// Función para actualizar texto del botón según el estado
function CVactualizarTextoBtnMasivo(estado) {
  var textoBoton = "Aprobar Masivo";
  var iconoBoton = "fa-check-circle";
  var colorBoton = "btn-success";

  // Remover clases de color anteriores
  $("#CVbtnAprobacionMasiva").removeClass(
    "btn-success btn-info btn-danger btn-warning"
  );
  $("#CVbtnAprobacionMasiva i").removeClass(
    "fa-check-circle fa-info-circle fa-times-circle"
  );

  switch (estado) {
    case "PE":
      textoBoton = "Aprobar Masivo";
      iconoBoton = "fa-check-circle";
      colorBoton = "btn-success";
      break;
    case "V1":
      textoBoton = "Aprobar Masivo";
      iconoBoton = "fa-check-circle";
      colorBoton = "btn-success";
      break;
    default:
      textoBoton = "Aprobar Masivo";
      iconoBoton = "fa-check-circle";
      colorBoton = "btn-success";
  }

  $("#CVbtnAprobacionMasiva")
    .addClass(colorBoton)
    .html('<i class="fa ' + iconoBoton + ' mr-1"></i> ' + textoBoton);
}

// Función para manejar selección individual
function CVmanejarSeleccionIndividual(checkbox) {
  var $checkbox = $(checkbox);
  var idRegistro = $checkbox.data("id");
  var estadoRegistro = $checkbox.data("estado");
  var $fila = $checkbox.closest("tr");

  console.log(
    "🔄 Selección individual:",
    idRegistro,
    "Estado:",
    estadoRegistro,
    "Checked:",
    $checkbox.is(":checked")
  );

  if ($checkbox.is(":checked")) {
    // Verificar si es la primera selección o si el estado coincide
    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = estadoRegistro;
    } else if (estadoActualSeleccionado !== estadoRegistro) {
      // Estado diferente, no permitir selección
      $checkbox.prop("checked", false);
      Swal.fire({
        icon: "warning",
        title: "Selección no válida",
        text: "Solo puedes seleccionar registros con el mismo estado para aprobación masiva.",
        confirmButtonText: "Entendido",
      });
      return;
    }

    // Agregar a la lista de seleccionados
    if (registrosSeleccionados.indexOf(idRegistro) === -1) {
      registrosSeleccionados.push(idRegistro);
      $fila.addClass("row-selected");
    }
  } else {
    // Remover de la lista de seleccionados
    var index = registrosSeleccionados.indexOf(idRegistro);
    if (index > -1) {
      registrosSeleccionados.splice(index, 1);
      $fila.removeClass("row-selected");
    }

    // Si no hay más selecciones, resetear el estado
    if (registrosSeleccionados.length === 0) {
      estadoActualSeleccionado = null;
    }
  }

  CVactualizarContadorSeleccion();
  console.log("📊 Registros seleccionados:", registrosSeleccionados);
}

// Función para seleccionar/deseleccionar todos
function CVmanejarSeleccionTodos(seleccionar) {
  console.log("🔄 Seleccionar todos:", seleccionar);

  if (seleccionar) {
    // Determinar el estado predominante si no hay selecciones previas
    if (registrosSeleccionados.length === 0) {
      var estadosDisponibles = [];
      $(".row-checkbox-FICV").each(function () {
        var estado = $(this).data("estado");
        if (estadosDisponibles.indexOf(estado) === -1) {
          estadosDisponibles.push(estado);
        }
      });

      // Si hay múltiples estados, preguntar al usuario
      if (estadosDisponibles.length > 1) {
        Swal.fire({
          title: "Seleccionar Estado",
          text: "Hay registros con diferentes estados. ¿Cuál estado deseas seleccionar para aprobación masiva?",
          icon: "question",
          showCancelButton: true,
          confirmButtonText: "Pendientes",
          cancelButtonText: "Cancelar",
          showDenyButton: true,
          denyButtonText: "Otros",
        }).then((result) => {
          if (result.isConfirmed) {
            CVseleccionarPorEstado("PE");
          } else if (result.isDenied) {
            // Mostrar opciones adicionales
            var options = estadosDisponibles.map((estado) => {
              var texto = estado;
              switch (estado) {
                case "PE":
                  texto = "Pendiente";
                  break;
                case "V1":
                  texto = "VoBo";
                  break;
                case "AP":
                  texto = "Aprobado";
                  break;
                case "AN":
                  texto = "Anulado";
                  break;
              }
              return { value: estado, text: texto };
            });

            Swal.fire({
              title: "Selecciona un estado",
              input: "select",
              inputOptions: options.reduce((obj, item) => {
                obj[item.value] = item.text;
                return obj;
              }, {}),
              inputPlaceholder: "Selecciona un estado",
              showCancelButton: true,
              inputValidator: (value) => {
                if (!value) {
                  return "Debes seleccionar un estado";
                }
              },
            }).then((result) => {
              if (result.isConfirmed) {
                CVseleccionarPorEstado(result.value);
              }
            });
          }
        });
        return;
      } else {
        estadoActualSeleccionado = estadosDisponibles[0];
      }
    }

    CVseleccionarPorEstado(estadoActualSeleccionado);
  } else {
    // Deseleccionar todos
    $(".row-checkbox-FICV").prop("checked", false);
    $(".row-selected").removeClass("row-selected");
    registrosSeleccionados = [];
    estadoActualSeleccionado = null;
    CVactualizarContadorSeleccion();
  }
}

// Función auxiliar para seleccionar por estado
function CVseleccionarPorEstado(estado) {
  console.log("🎯 Seleccionando por estado:", estado);
  estadoActualSeleccionado = estado;
  registrosSeleccionados = [];

  $(".row-checkbox-FICV").each(function () {
    var $checkbox = $(this);
    var estadoRegistro = $checkbox.data("estado");
    var idRegistro = $checkbox.data("id");
    var $fila = $checkbox.closest("tr");

    if (estadoRegistro === estado) {
      $checkbox.prop("checked", true);
      $fila.addClass("row-selected");
      if (registrosSeleccionados.indexOf(idRegistro) === -1) {
        registrosSeleccionados.push(idRegistro);
      }
    } else {
      $checkbox.prop("checked", false);
      $fila.removeClass("row-selected");
    }
  });

  CVactualizarContadorSeleccion();
}

// Función para mantener selecciones después del redibujado de la tabla
function CVmantenerSelecciones() {
  $(".row-checkbox-FICV").each(function () {
    var $checkbox = $(this);
    var idRegistro = $checkbox.data("id");
    var $fila = $checkbox.closest("tr");

    if (registrosSeleccionados.indexOf(idRegistro) !== -1) {
      $checkbox.prop("checked", true);
      $fila.addClass("row-selected");
    }
  });
}

// Función para realizar aprobación masiva
function CVejecutarAprobacionMasiva() {
  if (registrosSeleccionados.length === 0) {
    Swal.fire({
      icon: "warning",
      title: "Sin selección",
      text: "Debes seleccionar al menos un registro para aprobar.",
      confirmButtonText: "Entendido",
    });
    return;
  }

  var accion = "aprobar"; // Solo aprobación para fitosanidad
  var accionTexto = "aprobar";

  Swal.fire({
    title: "¿Confirmar aprobación masiva?",
    text: `¿Estás seguro de que deseas ${accionTexto} ${
      registrosSeleccionados.length
    } registro${registrosSeleccionados.length !== 1 ? "s" : ""}?`,
    icon: "question",
    showCancelButton: true,
    confirmButtonColor: "#28a745",
    cancelButtonColor: "#6c757d",
    confirmButtonText: "Sí, " + accionTexto,
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      CVprocesarAprobacionMasiva(accion);
    }
  });
}

// Función para procesar la aprobación masiva
function CVprocesarAprobacionMasiva(accion) {
  console.log(
    "🚀 Iniciando aprobación masiva:",
    accion,
    registrosSeleccionados
  );

  var totalRegistros = registrosSeleccionados.length;
  var procesados = 0;
  var exitosos = 0;
  var errores = [];

  // Mostrar indicador de progreso
  Swal.fire({
    title: "Procesando...",
    text: `Procesando ${totalRegistros} registro${
      totalRegistros !== 1 ? "s" : ""
    }...`,
    allowOutsideClick: false,
    allowEscapeKey: false,
    showConfirmButton: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Procesar cada registro secuencialmente
  function CVprocesarSiguiente(index) {
    if (index >= registrosSeleccionados.length) {
      // Todos los registros procesados
      CVmostrarResultadoFinal();
      return;
    }

    var idservicio = registrosSeleccionados[index];
    console.log(`📋 Procesando ${index + 1}/${totalRegistros}: ${idservicio}`);

    // Actualizar el texto del progress
    Swal.update({
      text: `Procesando ${index + 1} de ${totalRegistros} registros...`,
    });

    $.ajax({
      url: "/actualizar-orden-fitosanidad/" + idservicio + "/",
      type: "GET",
      data: { accion: accion },
      success: function (data) {
        console.log(`✅ Éxito ${index + 1}/${totalRegistros}:`, idservicio);

        reqinterno = JSON.stringify(data);
        reqinterno = reqinterno.substring(1, reqinterno.length - 1);
        //reqinterno = {"idreqinterno":"_6TC0UO78K43514","iddocumento":"REQ","idsucursal":"001","idalmacen":"001","serie":"0001","numero":"0021548","fecha":"20240124","estado":"AP","idarea":"003       ","idresponsable":"000025","dreqinterno":[{"item":"001","idproducto":"24000010086","descripcion":"CROP + PLUS","idmedida":"LTS","cantidad":1,"idconsumidor":"FLACA6"}]}
        console.log(reqinterno);
        // Configuración de la solicitud
        const requestOptions = {
          method: "POST",
          headers: {
            "Content-Type": "application/json", // Ajusta el tipo de contenido según las necesidades de la API
            // Puedes agregar otros encabezados según los requisitos de la API
          },
          body: reqinterno, //JSON.stringify(data), // Convierte los datos a formato JSON
        };

        // URL del servicio que quieres consumir
        const url =
          "http://192.168.0.5:9000/api/crtReqinterno?dbName=CAMPOVERDE";
        // Realizar la solicitud POST
        fetch(url, requestOptions)
          .then((response) => response.json()) // Puedes cambiar a .text() si la respuesta no es JSON
          .then((data1) => {
            // Hacer algo con la respuesta
            console.log("Respuesta exitosa:", data1);
          })
          .catch((error) => {
            // Manejar errores
            console.error("Error en la solicitud:", error);
          });
        // muestra un mensaje de éxito u otra acción adecuada

        exitosos++;
        procesados++;
        // Procesar siguiente registro
        setTimeout(() => CVprocesarSiguiente(index + 1), 100);
      },
      error: function (xhr, status, error) {
        console.log(
          `❌ Error ${index + 1}/${totalRegistros}:`,
          idservicio,
          error
        );
        errores.push({
          id: idservicio,
          error: error || "Error desconocido",
        });
        procesados++;
        // Procesar siguiente registro
        setTimeout(() => CVprocesarSiguiente(index + 1), 100);
      },
    });
  }

  function CVmostrarResultadoFinal() {
    var iconoResultado =
      exitosos === totalRegistros
        ? "success"
        : exitosos > 0
        ? "warning"
        : "error";
    var tituloResultado =
      exitosos === totalRegistros
        ? "¡Aprobación completada!"
        : exitosos > 0
        ? "Aprobación parcial"
        : "Error en la aprobación";

    var mensajeDetalle = `✅ Exitosos: ${exitosos}\n❌ Errores: ${errores.length}`;

    if (errores.length > 0) {
      mensajeDetalle += "\n\nErrores encontrados:\n";
      errores.forEach((error) => {
        mensajeDetalle += `• ID ${error.id}: ${error.error}\n`;
      });
    }

    Swal.fire({
      icon: iconoResultado,
      title: tituloResultado,
      text: mensajeDetalle,
      confirmButtonText: "Aceptar",
    }).then(() => {
      // Limpiar selecciones y recargar tabla
      registrosSeleccionados = [];
      estadoActualSeleccionado = null;
      $("#CVpanelSeleccion").hide();
      $("#CVbtnAprobacionMasiva").prop("disabled", true);

      // Recargar la tabla
      if (table_show) {
        table_show.ajax.reload();
      }
    });
  }

  // Iniciar el procesamiento
  CVprocesarSiguiente(0);
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS DE CHECKBOX
// =============================================
function CVconfigurarEventosCheckbox() {
  // Remover event listeners anteriores para evitar duplicación
  $(".row-checkbox-FICV").off("change");
  $("#CVcheckboxSelectAll").off("change");

  // Evento para checkboxes individuales
  $(".row-checkbox-FICV").on("change", function (e) {
    e.stopPropagation(); // Evitar que se propague el evento
    CVmanejarSeleccionIndividual(this);
  });

  // Evento para checkbox maestro
  $("#CVcheckboxSelectAll").on("change", function () {
    CVmanejarSeleccionTodos($(this).is(":checked"));
  });

  // Prevenir que el click en la celda del checkbox active el evento de la fila
  $(".form-check").on("click", function (e) {
    e.stopPropagation();
  });
}

// =============================================
// INICIALIZACIÓN CUANDO EL DOCUMENTO ESTÉ LISTO
// =============================================
window.initFitosanidadCVModule = function () {
  console.log("🚀 Inicializando fitosanidad (modo TAB/PARTIAL)");

  // Carga combos / data inicial
  CVcargarAreas();

  // Binds (tus .off() evitan duplicados)
  CVreturnApproveOrdersDoc();
  CVselectRowLot();

  // Carga inicial de tabla (usa filtro por área por defecto)
  CVreturnApproveOrdersFilter();
};
