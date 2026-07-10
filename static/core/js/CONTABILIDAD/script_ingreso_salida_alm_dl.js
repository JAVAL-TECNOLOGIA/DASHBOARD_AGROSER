/**
 * Script para la gestión de ingresos y salidas de almacén en Don Luis
 * Implementa la tabla con todas las columnas de la API
 * @author: Equipo de Desarrollo
 * @date: 2023-06-12
 */

// Variable global para la tabla
let tablaAlmacen;

/**
 * Inicializa la tabla DataTable con la configuración y todas las columnas de la API
 */
function inicializarTabla() {
  tablaAlmacen = $("#tabla-ingresos-salidas").DataTable({
    processing: true,
    serverSide: true,
    searching: true,
    ordering: true,
    responsive: false,
    scrollX: true,
    scrollCollapse: true,
    paging: true,
    pageLength: 10,
    pagingType: "full_numbers",
    lengthMenu: [
      [10, 25, 50, 100],
      [10, 25, 50, 100],
    ],
    language: {
      url: "/static/core/js/dataTables.spanish.json",
      paginate: {
        first: '<i class="fa fa-angle-double-left"></i>',
        last: '<i class="fa fa-angle-double-right"></i>',
        next: '<i class="fa fa-angle-right"></i>',
        previous: '<i class="fa fa-angle-left"></i>',
      },
      processing:
        "<div class='spinner-border text-primary' role='status'><span class='sr-only'>Cargando...</span></div>",
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      infoEmpty: "No hay registros disponibles",
      infoFiltered: "(filtrado de _MAX_ registros totales)",
      lengthMenu: "Mostrar _MENU_ registros por página",
      search: "Buscar:",
      zeroRecords: "No se encontraron registros coincidentes",
      buttons: {
        excel: "Exportar a Excel",
        pdf: "Exportar a PDF",
        print: "Imprimir",
      },
    },
    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>><"row"<"col-sm-12 col-md-12"B>>t<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>><"clear">',
    buttons: [
      {
        extend: "excel",
        text: '<i class="fas fa-file-excel"></i> Excel',
        className: "btn btn-success",
        title: "Ingresos y Salidas de Almacén",
        exportOptions: {
          columns: ":visible",
        },
        filename: function () {
          return "Ingresos_Salidas_Almacen_" + moment().format("YYYYMMDD");
        },
        action: function (e, dt, button, config) {
          Swal.fire({
            title: "Exportando datos",
            text: "Preparando exportación. Esto puede tomar varios minutos si hay muchos registros.",
            icon: "info",
            showCancelButton: true,
            confirmButtonText: "Continuar",
            cancelButtonText: "Cancelar",
          }).then((result) => {
            if (result.isConfirmed) {
              Swal.fire({
                title: "Exportando...",
                text: "Generando archivo Excel",
                allowOutsideClick: false,
                didOpen: () => {
                  Swal.showLoading();
                },
              });

              $.ajax({
                url: "/contabilidad/contabilidad_ingresos_salidas_almacen/exportar/",
                type: "GET",
                data: {
                  periodo: $("#filtro-periodo").val().trim(),
                  estado: $("#filtro-estado").val(),
                  operacion: $("#filtro-operacion").val(),
                },
                success: function (response) {
                  Swal.close();
                  let tempTable = $("<table></table>").DataTable({
                    data: response.data,
                    columns: dt.settings().init().columns,
                    destroy: true,
                  });

                  $.fn.dataTable.ext.buttons.excelHtml5.action.call(
                    this,
                    e,
                    tempTable,
                    button,
                    config
                  );

                  tempTable.destroy();
                },
                error: function () {
                  Swal.fire({
                    title: "Error",
                    text: "No se pudo generar el archivo Excel",
                    icon: "error",
                  });
                },
              });
            }
          });
        },
      },
    ],
    columns: [
      { data: "IDINGRESOSALIDAALM", title: "ID", width: "120px" },
      { data: "PERIODO", title: "Periodo", width: "80px" },
      {
        data: "FECHA",
        title: "Fecha",
        width: "100px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
      { data: "IDOPERACION", title: "Operación", width: "80px" },
      { data: "NUMOPERACION", title: "Núm. Operación", width: "120px" },
      { data: "GLOSA", title: "Descripción", width: "200px" },
      {
        data: "IDESTADO",
        title: "Estado",
        width: "100px",
        render: function (data) {
          let badge = "";
          switch (data) {
            case "PE":
              badge = '<span class="badge badge-warning">PENDIENTE</span>';
              break;
            case "W1":
              badge = '<span class="badge badge-success">ACEPTADO SUNAT</span>';
              break;
            case "W0":
              badge = '<span class="badge badge-info">PENDIENTE SUNAT</span>';
              break;
            case "AN":
              badge = '<span class="badge badge-danger">ANULADO</span>';
              break;
            default:
              badge = '<span class="badge badge-secondary">' + data + "</span>";
          }
          return badge;
        },
      },
      {
        data: "FECHACREACION",
        title: "Fecha Creación",
        width: "120px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
      { data: "IDEMPRESA", title: "IDEMPRESA", width: "100px" },
      { data: "IDEMISOR", title: "IDEMISOR", width: "100px" },
      { data: "IDSUBDIARIO", title: "IDSUBDIARIO", width: "100px" },
      { data: "VOUCHER", title: "VOUCHER", width: "100px" },
      { data: "IDALMACEN", title: "IDALMACEN", width: "100px" },
      { data: "IDDOCUMENTO", title: "IDDOCUMENTO", width: "100px" },
      { data: "SERIE", title: "SERIE", width: "80px" },
      { data: "NUMERO", title: "NUMERO", width: "100px" },
      { data: "IDCLIEPROV", title: "IDCLIEPROV", width: "120px" },
      { data: "IDPROYECTO", title: "IDPROYECTO", width: "100px" },
      { data: "IDRESPONSABLE", title: "IDRESPONSABLE", width: "120px" },
      { data: "IDMONEDA", title: "IDMONEDA", width: "100px" },
      { data: "TCAMBIO", title: "TCAMBIO", width: "80px" },
      { data: "TCMONEDA", title: "TCMONEDA", width: "80px" },
      { data: "IDMOTIVO", title: "IDMOTIVO", width: "100px" },
      { data: "IDALMACEND", title: "IDALMACEND", width: "100px" },
      { data: "IDDOCORIGEN", title: "IDDOCORIGEN", width: "120px" },
      { data: "SERIEDOCORIGEN", title: "SERIEDOCORIGEN", width: "120px" },
      { data: "NUMDOCORIGEN", title: "NUMDOCORIGEN", width: "120px" },
      {
        data: "FECHADOCORIGEN",
        title: "FECHADOCORIGEN",
        width: "120px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
      { data: "IDFLETE", title: "IDFLETE", width: "100px" },
      { data: "IDTRANSPORTISTA", title: "IDTRANSPORTISTA", width: "120px" },
      { data: "CERTIFTRANSPORTE", title: "CERTIFTRANSPORTE", width: "150px" },
      { data: "CERTIFTRANSPORTE1", title: "CERTIFTRANSPORTE1", width: "150px" },
      { data: "PLACA", title: "PLACA", width: "100px" },
      { data: "PLACA1", title: "PLACA1", width: "100px" },
      { data: "MARCA", title: "MARCA", width: "100px" },
      { data: "MARCA1", title: "MARCA1", width: "100px" },
      { data: "CHOFER", title: "CHOFER", width: "120px" },
      { data: "BREVETE", title: "BREVETE", width: "100px" },
      { data: "LLEVADOPOR", title: "LLEVADOPOR", width: "120px" },
      {
        data: "FECHATRASLADO",
        title: "FECHATRASLADO",
        width: "120px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
      { data: "DIRECLLEGADA", title: "DIRECLLEGADA", width: "150px" },
      { data: "PRECIOIGV", title: "PRECIOIGV", width: "100px" },
      { data: "REDONDEO", title: "REDONDEO", width: "100px" },
      { data: "TOTAL", title: "TOTAL", width: "100px" },
      { data: "ES_GASTOS", title: "ES_GASTOS", width: "100px" },
      { data: "ES_PROVISION", title: "ES_PROVISION", width: "100px" },
      { data: "ES_RIEGO", title: "ES_RIEGO", width: "100px" },
      { data: "SINCRONIZA", title: "SINCRONIZA", width: "100px" },
      { data: "IDCONTABILIZADO", title: "IDCONTABILIZADO", width: "120px" },
      { data: "IDCONSUMIDOR", title: "IDCONSUMIDOR", width: "120px" },
      { data: "IDLINEAPRODUC", title: "IDLINEAPRODUC", width: "120px" },
      { data: "IDLOTE", title: "IDLOTE", width: "100px" },
      { data: "CONTABILIZADO", title: "CONTABILIZADO", width: "120px" },
      { data: "IDSUCURSALD", title: "IDSUCURSALD", width: "120px" },
      { data: "IDDOCORIGEN2", title: "IDDOCORIGEN2", width: "120px" },
      { data: "SERIEDOCORIGEN2", title: "SERIEDOCORIGEN2", width: "140px" },
      { data: "NUMDOCORIGEN2", title: "NUMDOCORIGEN2", width: "140px" },
      {
        data: "FECHADOCORIGEN2",
        title: "FECHADOCORIGEN2",
        width: "140px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
      { data: "IDSUCURSAL", title: "IDSUCURSAL", width: "120px" },
      { data: "VENTANA", title: "VENTANA", width: "120px" },
      { data: "VVENTA", title: "VVENTA", width: "100px" },
      { data: "IMPUESTO", title: "IMPUESTO", width: "100px" },
      { data: "DESCUENTO", title: "DESCUENTO", width: "100px" },
      { data: "VOLUMEN", title: "VOLUMEN", width: "100px" },
      { data: "NUMBATCH", title: "NUMBATCH", width: "100px" },
      { data: "NUMAUTOCLAVE", title: "NUMAUTOCLAVE", width: "120px" },
      {
        data: "FECHACOSECHA",
        title: "FECHACOSECHA",
        width: "120px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
      { data: "OCCLIENTE", title: "OCCLIENTE", width: "120px" },
      { data: "OTRADIRECCION", title: "OTRADIRECCION", width: "150px" },
      { data: "IMPRESO", title: "IMPRESO", width: "100px" },
      { data: "HORA", title: "HORA", width: "100px" },
      { data: "IDMONEDA_FLETE", title: "IDMONEDA_FLETE", width: "130px" },
      { data: "IMPORTE_FLETE", title: "IMPORTE_FLETE", width: "120px" },
      { data: "PESO_TOTAL", title: "PESO_TOTAL", width: "100px" },
      { data: "IMPORTADO", title: "IMPORTADO", width: "100px" },
      { data: "IDCONTROLADOR", title: "IDCONTROLADOR", width: "120px" },
      { data: "IDCLIEPROVDEST", title: "IDCLIEPROVDEST", width: "130px" },
      { data: "IDCOMPRA", title: "IDCOMPRA", width: "100px" },
      { data: "IDUBIGEOLLEGADA", title: "IDUBIGEOLLEGADA", width: "130px" },
      { data: "IDDOCORIGEN3", title: "IDDOCORIGEN3", width: "120px" },
      { data: "SERIEDOCORIGEN3", title: "SERIEDOCORIGEN3", width: "140px" },
      { data: "NUMDOCORIGEN3", title: "NUMDOCORIGEN3", width: "140px" },
      {
        data: "FECHADOCORIGEN3",
        title: "FECHADOCORIGEN3",
        width: "140px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
      { data: "IDUNIDADNEGOCIO", title: "IDUNIDADNEGOCIO", width: "130px" },
      { data: "IDCNFDISTRIBUCION", title: "IDCNFDISTRIBUCION", width: "140px" },
      { data: "IDTURNOTRABAJO", title: "IDTURNOTRABAJO", width: "130px" },
      { data: "IDPRODUCTO", title: "IDPRODUCTO", width: "100px" },
      { data: "IDREFERENCIAPROCESO", title: "IDREFPROCESO", width: "120px" },
      { data: "IDPROCESO", title: "IDPROCESO", width: "100px" },
      { data: "IDSUBPROCESO", title: "IDSUBPROCESO", width: "120px" },
      {
        data: "FECHAEXPIRACION",
        title: "FECHAEXPIRACION",
        width: "130px",
        render: function (data) {
          if (!data) return "";
          return data ? new Date(data).toLocaleDateString("es-ES") : "";
        },
      },
    ],
    ajax: {
      url: "/contabilidad/contabilidad_ingresos_salidas_almacen/",
      type: "GET",
      data: function (d) {
        d.pagina = d.start / d.length + 1;
        d.registros = d.length;

        d.periodo = $("#filtro-periodo").val().trim();
        d.estado = $("#filtro-estado").val();
        d.operacion = $("#filtro-operacion").val();

        if (d.periodo && !/^\d{6}$/.test(d.periodo)) {
          mostrarMensaje(
            "warning",
            "El formato del periodo debe ser AAAAMM (Ejemplo: 202301)"
          );
          d.periodo = "";
        }

        localStorage.setItem("filtro_periodo", d.periodo);
        localStorage.setItem("filtro_estado", d.estado);
        localStorage.setItem("filtro_operacion", d.operacion);

        return d;
      },
      dataSrc: function (json) {
        if (json.data.length === 0) {
          setTimeout(function () {
            mostrarMensaje(
              "info",
              "No se encontraron registros con los criterios de búsqueda"
            );
          }, 500);
        }

        $("#contador-registros").text(json.total_registros || 0);

        if (json.tabla_utilizada) {
          console.log("Tabla utilizada:", json.tabla_utilizada);
        }

        return json.data;
      },
      error: function (xhr, status, error) {
        let mensajeError = "Error al cargar datos";
        if (xhr.responseJSON && xhr.responseJSON.message) {
          mensajeError += ": " + xhr.responseJSON.message;
        } else if (error) {
          mensajeError += ": " + error;
        }
        mostrarError(mensajeError);
        return [];
      },
    },
    initComplete: function () {
      tablaAlmacen.columns.adjust().draw();
      $(".dataTables_paginate .paginate_button").addClass(
        "btn btn-sm btn-outline-primary"
      );
    },
    drawCallback: function (settings) {
      var api = this.api();
      var pageInfo = api.page.info();

      $("#contador-registros").text(pageInfo.recordsTotal);
      $("#info-registros").html(
        "Mostrando página " + (pageInfo.page + 1) + " de " + pageInfo.pages
      );

      $(".dataTables_paginate .paginate_button:not(.disabled)")
        .addClass("btn-outline-primary")
        .removeClass("btn-outline-secondary");
      $(".dataTables_paginate .paginate_button.current")
        .addClass("btn-primary")
        .removeClass("btn-outline-primary");
    },
  });
}

/**
 * Aplica los filtros seleccionados y recarga la tabla
 */
function aplicarFiltros() {
  let periodo = $("#filtro-periodo").val().trim();
  if (periodo && !/^\d{6}$/.test(periodo)) {
    mostrarMensaje(
      "warning",
      "El formato del periodo debe ser AAAAMM (Ejemplo: 202301)"
    );
    return;
  }

  tablaAlmacen.ajax.reload();
}

/**
 * Carga los valores de filtros guardados en localStorage
 */
function cargarFiltrosGuardados() {
  const periodo = localStorage.getItem("filtro_periodo");
  const estado = localStorage.getItem("filtro_estado");
  const operacion = localStorage.getItem("filtro_operacion");

  if (periodo) {
    $("#filtro-periodo").val(periodo);
  }

  if (estado) {
    $("#filtro-estado").val(estado);
  }

  if (operacion) {
    $("#filtro-operacion").val(operacion);
  }
}

/**
 * Limpia los filtros aplicados
 */
function limpiarFiltros() {
  $("#filtro-periodo").val("");
  $("#filtro-estado").val("");
  $("#filtro-operacion").val("");

  localStorage.removeItem("filtro_periodo");
  localStorage.removeItem("filtro_estado");
  localStorage.removeItem("filtro_operacion");

  tablaAlmacen.ajax.reload();
}

/**
 * Muestra un mensaje de error utilizando SweetAlert2
 * @param {string} mensaje - El mensaje de error a mostrar
 */
function mostrarError(mensaje) {
  Swal.fire({
    icon: "error",
    title: "Error",
    text: mensaje,
    confirmButtonText: "Aceptar",
  });
}

/**
 * Muestra un mensaje informativo utilizando SweetAlert2
 * @param {string} tipo - El tipo de mensaje (success, info, warning, error)
 * @param {string} mensaje - El mensaje a mostrar
 */
function mostrarMensaje(tipo, mensaje) {
  Swal.fire({
    icon: tipo,
    title: tipo === "error" ? "Error" : "Información",
    text: mensaje,
    confirmButtonText: "Aceptar",
  });
}

// Función para mostrar los datos actuales en consola (depuración)
function mostrarDatosEnConsola() {
  console.log("------------ DEBUG: DATOS DE LA TABLA ------------");
  console.log("Total de registros cargados:", tablaAlmacen.data().count());

  // Obtener los datos actuales
  const datos = tablaAlmacen.data().toArray();

  if (datos.length > 0) {
    console.log("Primer registro:", datos[0]);
    console.log("Estructura del primer registro:");

    // Listar todos los campos y sus valores para el primer registro
    for (let key in datos[0]) {
      console.log(
        `Campo: ${key}, Valor: ${datos[0][key]}, Tipo: ${typeof datos[0][key]}`
      );
    }

    // Buscar todos los periodos únicos
    const periodosUnicos = [...new Set(datos.map((item) => item.PERIODO))];
    console.log("Periodos únicos en los datos:", periodosUnicos);

    // Buscar todos los estados únicos
    const estadosUnicos = [...new Set(datos.map((item) => item.IDESTADO))];
    console.log("Estados únicos en los datos:", estadosUnicos);
  }

  console.log("------------ FIN DEBUG ------------");

  return datos;
}

// Cuando el documento esté listo
$(document).ready(function () {
  // Inicialización de la aplicación
  App.init();

  // Cargar filtros guardados (si existen)
  cargarFiltrosGuardados();

  // Inicializar la tabla con la configuración definida
  inicializarTabla();

  // Evento para botón de filtrar
  $("#btn-filtrar").on("click", function () {
    aplicarFiltros();
  });

  // Evento para botón de limpiar filtros
  $("#btn-limpiar-filtros").on("click", function () {
    limpiarFiltros();
  });

  // Evento para tecla Enter en los campos de filtro
  $("#filtro-periodo, #filtro-estado, #filtro-operacion").on(
    "keyup",
    function (e) {
      if (e.key === "Enter") {
        aplicarFiltros();
      }
    }
  );

  // Añadir evento para ajustar columnas cuando cambie el tamaño de la ventana
  $(window).resize(function () {
    if (tablaAlmacen) {
      tablaAlmacen.columns.adjust();
    }
  });

  // Actualizar estilo de selección en dropdown de estado
  $("#filtro-estado").on("change", function () {
    const valor = $(this).val();
    if (valor) {
      let colorClase = "";
      switch (valor) {
        case "PE":
          colorClase = "text-warning";
          break;
        case "W1":
          colorClase = "text-success";
          break;
        case "W0":
          colorClase = "text-info";
          break;
        case "AN":
          colorClase = "text-danger";
          break;
      }

      if (colorClase) {
        $(this).addClass(colorClase);
      }
    } else {
      $(this).removeClass("text-warning text-success text-danger text-info");
    }
  });

  // Aplicar estilo inicial al selector de estado
  $("#filtro-estado").trigger("change");
});
