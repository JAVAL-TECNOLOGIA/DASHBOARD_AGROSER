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
function cargarAreas() {
  $.get("../approve_almacen_areas", function (data) {
    $("#selectApproveArea").append("<option value='0'>Todos</option>");
    console.log($("#selectApproveArea").val());
    $.each(data, function (index, value) {
      $("#selectApproveArea").append(
        "<option value='" + value["idareas"] + "'>" + value["areas"] + "</option>"
      );
    });
    
    // Después de cargar las áreas, inicializar la tabla automáticamente
    inicializarTabla();
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
  if ($.fn.DataTable.isDataTable('#tableApproveOrders')) {
    $('#tableApproveOrders').DataTable().destroy();
  }

  console.log("📊 Inicializando tabla de requerimientos internos");

  table_show = $("#tableApproveOrders").DataTable({
    ajax: {
      url: "/req_interno_log_filter/0/", // 0 = Todas las áreas
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
      { data: "item", visible: false },
      {
        data: "estado",
        render: function (data, type, row) {
          let badgeClass = '';
          let estadoTexto = data;
          
          switch(data) {
            case 'PE':
            case 'PENDIENTE':
              badgeClass = 'badge-warning';
              estadoTexto = 'PENDIENTE';
              break;
            case 'AP':
            case 'APROBADO':
              badgeClass = 'badge-success';
              estadoTexto = 'APROBADO';
              break;
            case 'AN':
            case 'ANULADO':
              badgeClass = 'badge-danger';
              estadoTexto = 'ANULADO';
              break;
            default:
              badgeClass = 'badge-secondary';
              estadoTexto = data;
          }
          
          return '<span class="badge ' + badgeClass + '" style="font-size: 1em;">' + estadoTexto + '</span>';
        }
      },
      { data: "fecha" },
      { data: "documento", visible: false },
      { data: "num_documento", visible: false },
      { data: "IDCONSUMIDOR" },
      { data: "observacion" },
      { data: "areas" },
      { data: "total", visible: false },
      { 
        data: null,
        orderable: false,
        className: 'text-center',
        width: '50px',
        render: function (data, type, row) {
          // Solo mostrar checkbox para estados que se pueden aprobar
          if (row.estado === 'PE' || row.estado === 'PENDIENTE') {
            return '<div class="form-check">' +
                     '<input class="form-check-input row-checkbox" type="checkbox" ' +
                     'value="' + row.item + '" data-estado="' + row.estado + '">' +
                   '</div>';
          }
          return '';
        }
      },
    ],
    destroy: true,
    columnDefs: [
      {
        targets: '_all',
        createdCell: function (td, cellData, rowData, row, col) {
          // Agregar datos como atributos
          $(td).closest('tr').attr('data-item', rowData.item);
          $(td).closest('tr').attr('data-documento', rowData.documento);
        }
      }
    ],
    drawCallback: function() {
      // Configurar eventos de checkbox después de cada redibujado
      configurarEventosCheckbox();
    }
  });
}

// =============================================
// FUNCIÓN PARA FILTRAR POR ÁREA
// =============================================
function filtrarPorArea() {
  var area = $("#selectApproveArea").val() || 0;
  
  // Limpiar selecciones anteriores
  registrosSeleccionados = [];
  estadoActualSeleccionado = null;
  $("#panelSeleccion").hide();
  $("#btnAprobacionMasiva").prop("disabled", true);
  
  // Destruir la tabla existente
  if ($.fn.DataTable.isDataTable('#tableApproveOrders')) {
    $('#tableApproveOrders').DataTable().destroy();
  }

  console.log("🔍 Filtrando área", area);

  table_show = $("#tableApproveOrders").DataTable({
    ajax: {
      url: "/req_interno_log_filter/" + area + "/",
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
      { data: "item", visible: false },
      {
        data: "estado",
        render: function (data, type, row) {
          let badgeClass = '';
          let estadoTexto = data;
          
          switch(data) {
            case 'PE':
            case 'PENDIENTE':
              badgeClass = 'badge-warning';
              estadoTexto = 'PENDIENTE';
              break;
            case 'AP':
            case 'APROBADO':
              badgeClass = 'badge-success';
              estadoTexto = 'APROBADO';
              break;
            case 'AN':
            case 'ANULADO':
              badgeClass = 'badge-danger';
              estadoTexto = 'ANULADO';
              break;
            default:
              badgeClass = 'badge-secondary';
              estadoTexto = data;
          }
          
          return '<span class="badge ' + badgeClass + '" style="font-size: 1em;">' + estadoTexto + '</span>';
        }
      },
      { data: "fecha" },
      { data: "documento", visible: false },
      { data: "num_documento", visible: false },
      { data: "IDCONSUMIDOR" },
      { data: "observacion" },
      { data: "areas" },
      { data: "total", visible: false },
      { 
        data: null,
        orderable: false,
        className: 'text-center',
        width: '50px',
        render: function (data, type, row) {
          // Solo mostrar checkbox para estados que se pueden aprobar
          if (row.estado === 'PE' || row.estado === 'PENDIENTE') {
            return '<div class="form-check">' +
                     '<input class="form-check-input row-checkbox" type="checkbox" ' +
                     'value="' + row.item + '" data-estado="' + row.estado + '">' +
                   '</div>';
          }
          return '';
        }
      },
    ],
    destroy: true,
    columnDefs: [
      {
        targets: '_all',
        createdCell: function (td, cellData, rowData, row, col) {
          // Agregar datos como atributos
          $(td).closest('tr').attr('data-item', rowData.item);
          $(td).closest('tr').attr('data-documento', rowData.documento);
        }
      }
    ],
    drawCallback: function() {
      // Configurar eventos de checkbox después de cada redibujado
      configurarEventosCheckbox();
    }
  });
}

// =============================================
// FUNCIÓN PARA CONFIGURAR EVENTOS
// =============================================
function configurarEventos() {
  // Remover event listeners anteriores para evitar duplicación
  $("#btnApproveFilter").off('click');
  $("#btnAprobacionMasiva").off('click');
  $("#btnSeleccionarTodos").off('click');
  $("#btnDeseleccionarTodos").off('click');
  
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
  $("#tableApproveOrders tbody").off('dblclick');
  
  $("#tableApproveOrders tbody").on("dblclick", "tr", function (e) {
    // Evitar que el doble clic active el checkbox
    if ($(e.target).is('input[type="checkbox"]')) {
      return;
    }
    
    var row = table_show.row(this).data();
    var idservicio = row["item"];
    
    if (row["documento"] == "REQUERIMIENTOS INTERNOS") {
      abrirModalRequerimiento(idservicio);
    } else if (row["documento"] == "SERVICIO") {
      abrirModalServicio(idservicio);
    }
    
    // Configurar botones del modal
    configurarBotonesModal(idservicio);
  });
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE REQUERIMIENTO
// =============================================
function abrirModalRequerimiento(idorden) {
  $("#modalApproveOrders").modal("toggle");
  $.get(
    "../req_interno_log_detail_purchase/" + idorden + "/",
    function (data) {
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
    }
  );
}

// =============================================
// FUNCIÓN PARA ABRIR MODAL DE SERVICIO
// =============================================
function abrirModalServicio(idorden) {
  $("#modalApproveOrders").modal("toggle");
  $.get(
    "../approve_pservicios_log_detail_service-/" + idorden,
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
  $("#btn-aprobar").off('click');
  $("#btn-vb").off('click');
  $("#btn-anular").off('click');
  
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
      if ($("#selectApproveArea").val() === '0' || $("#selectApproveArea").val() === null) {
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
  $("#contadorSeleccion").text(cantidad + " registro" + (cantidad !== 1 ? "s" : "") + " seleccionado" + (cantidad !== 1 ? "s" : ""));
  
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
  
  if (estado === "PE" || estado === "PENDIENTE") {
    texto = "Aprobar Masivo";
    icono = "fa-check-circle";
    $("#btnAprobacionMasiva").removeClass("btn-warning").addClass("btn-success");
  }
  
  $("#textoBtnMasivo").text(texto);
  $("#btnAprobacionMasiva i").removeClass().addClass("fa " + icono + " mr-1");
}

// Función para manejar selección individual
function manejarSeleccionIndividual(checkbox) {
  var $checkbox = $(checkbox);
  var idorden = $checkbox.val();
  var estado = $checkbox.data("estado");
  var $row = $checkbox.closest("tr");
  
  if ($checkbox.is(":checked")) {
    // Agregar a seleccionados
    if (registrosSeleccionados.length === 0 || estadoActualSeleccionado === estado) {
      registrosSeleccionados.push({
        idorden: idorden,
        estado: estado
      });
      $row.addClass("row-selected");
      
      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
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
    registrosSeleccionados = registrosSeleccionados.filter(item => item.idorden !== idorden);
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
  
  $(".row-checkbox").each(function() {
    var $checkbox = $(this);
    var $row = $checkbox.closest("tr");
    
    if (seleccionar) {
      var idorden = $checkbox.val();
      var estado = $checkbox.data("estado");
      
      if (estadoActualSeleccionado === null) {
        estadoActualSeleccionado = estado;
        actualizarTextoBtnMasivo(estado);
      }
      
      if (estadoActualSeleccionado === estado) {
        $checkbox.prop("checked", true);
        $row.addClass("row-selected");
        registrosSeleccionados.push({
          idorden: idorden,
          estado: estado
        });
      }
    } else {
      $checkbox.prop("checked", false);
      $row.removeClass("row-selected");
    }
  });
  
  $("#checkboxSelectAll").prop("checked", seleccionar).prop("indeterminate", false);
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
  
  if (estadoActualSeleccionado === "PE" || estadoActualSeleccionado === "PENDIENTE") {
    accion = "aprobar";
    textoConfirmacion = "¿Estás seguro de que deseas APROBAR " + registrosSeleccionados.length + " requerimiento(s) interno(s) seleccionado(s)?";
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
    }
  });
  
  // Procesar cada registro con delay para evitar sobrecarga del servidor
  var promesas = registrosSeleccionados.map(function(registro, index) {
    return new Promise(function(resolve) {
      setTimeout(function() {
        $.ajax({
          url: "/actualizar-req-interno/" + registro.idorden + "/",
          type: "GET",
          data: { accion: accion },
          timeout: 10000,
          success: function(data) {
            procesados++;
            resolve({ success: true, idorden: registro.idorden });
          },
          error: function(xhr, status, error) {
            errores++;
            errorDetails.push({
              idorden: registro.idorden,
              error: error,
              status: status
            });
            resolve({ success: false, idorden: registro.idorden, error: error });
          }
        });
      }, index * 500); // 500ms de delay entre cada request
    });
  });
  
  // Cuando todas las promesas se resuelvan
  Promise.all(promesas).then(function(resultados) {
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
    if ($("#selectApproveArea").val() === '0' || $("#selectApproveArea").val() === null) {
      inicializarTabla();
    } else {
      filtrarPorArea();
    }
    
    // Mostrar resultado final
    if (fallidos === 0) {
      Swal.fire({
        title: "¡Proceso Completado!",
        text: "Se procesaron exitosamente " + exitosos + " requerimiento(s) interno(s).",
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
      Swal.fire({
        title: "⚠️ Proceso Parcial",
        html: "Se procesaron <b>" + exitosos + "</b> requerimiento(s) exitosamente.<br>" +
              "Fallaron <b>" + fallidos + "</b> requerimiento(s).<br><br>" +
              "Revisa los requerimientos restantes manualmente.",
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
  $(".row-checkbox").off('change');
  $("#checkboxSelectAll").off('change');
  
  // Evento para checkboxes individuales
  $(".row-checkbox").change(function() {
    manejarSeleccionIndividual(this);
  });
  
  // Evento para checkbox "Seleccionar Todos"
  $("#checkboxSelectAll").change(function() {
    var isChecked = $(this).is(':checked');
    manejarSeleccionTodos(isChecked);
  });
}

// =============================================
// INICIALIZACIÓN CUANDO EL DOCUMENTO ESTÉ LISTO
// =============================================
$(document).ready(function() {
  // Cargar áreas e inicializar tabla automáticamente
  cargarAreas();
  
  // Configurar eventos
  configurarEventos();
  
  // Configurar selección de filas
  configurarSeleccionFila();
});
