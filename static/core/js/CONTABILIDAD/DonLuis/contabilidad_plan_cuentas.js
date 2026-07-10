// Función para recargar datos
function recargarDatos() {
  initPlanCuentas();
}

// Función auxiliar para renderizar valores booleanos
function renderBoolean(data) {
  return data === "1" || data === 1
    ? '<i class="fa fa-check text-success"></i>'
    : '<i class="fa fa-times text-danger"></i>';
}

$(document).ready(function () {
  // Inicializar la tabla automáticamente al cargar la página
  initPlanCuentas();
  
  $("#btn_buscar").click(function () {
    initPlanCuentas();
  });
  
  $("#btn_limpiar").click(function () {
    $("#filtrosForm")[0].reset();
    $("#filtro_empresa").val("001"); // Mantener empresa 001 seleccionada
    initPlanCuentas();
  });
});

function initPlanCuentas() {
  console.log("initPlanCuentas");
  // Inicializar DataTable
  var table = new DataTable("#tabla_plan_cuentas", {
    // boton de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "REPORTE_PLAN_DE_CUENTAS",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "REPORTE_PLAN_DE_CUENTAS",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
    ],

    scrollX: true,
    scrollY: 400,
    scrollCollapse: true,
    fixedColumns: {
      left: 3 // Fijar las primeras 3 columnas (Empresa, Cuenta, Descripción)
    },

    serverSide: false,
    autoWidth: false,
    pageLength: 25,
    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],

    // ajax para obtener los datos de la tabla
    ajax: function (data, callback, settings) {
      // Mostrar indicador de carga
      $("#loading_indicator").show();
      $("#error_message").hide();
      
      // Recuperar los datos de la API
      $.ajax({
        url: "/contabilidad/api/plan-cuentas/",
        method: "GET",
        data: {
          empresa: $("#filtro_empresa").val(),
          cuenta: $("#filtro_cuenta").val(),
          descripcion: $("#filtro_descripcion").val(),
          tipo_cuenta: $("#filtro_tipo_cuenta").val(),
        },
        success: function (response) {
          console.log("Datos recibidos de la API:", response);
          $("#loading_indicator").hide();
          
          // Actualizar contador de registros
          $("#contador_registros").text(response.total_records + " registros");
          
          // Mostrar filtros aplicados
          let filtros = [];
          if ($("#filtro_empresa").val()) filtros.push("Empresa: " + $("#filtro_empresa").val());
          if ($("#filtro_cuenta").val()) filtros.push("Cuenta: " + $("#filtro_cuenta").val());
          if ($("#filtro_descripcion").val()) filtros.push("Descripción: " + $("#filtro_descripcion").val());
          if ($("#filtro_tipo_cuenta").val()) filtros.push("Tipo: " + $("#filtro_tipo_cuenta").val());
          
          $("#filtro_actual").text(filtros.length > 0 ? "Filtros: " + filtros.join(", ") : "Sin filtros aplicados");
          
          // Mostrar los datos reales en la tabla
          callback({
            data: response.data || [],
            recordsTotal: response.total_records || 0,
            recordsFiltered: response.total_records || 0,
          });
        },
        error: function (xhr, error, thrown) {
          $("#loading_indicator").hide();
          $("#error_message").show();
          $("#error_text").text("Error al cargar los datos: " + (xhr.responseJSON?.message || error));
          
          console.error(
            "Error al recuperar los datos de la API:",
            error,
            thrown,
            xhr.responseText
          );
          callback({
            data: [],
          });
        },
      });
    },

    columns: [
      { data: "IDEMPRESA", name: "IDEMPRESA", width: "60px" },
      {
        data: "IDCUENTA",
        name: "IDCUENTA",
        width: "120px",
        render: function (data) {
          return `<code>${data ? data.trim() : ""}</code>`;
        },
      },
      { data: "DESCRIPCION", name: "DESCRIPCION", width: "25%" },
      { data: "ESTRUCTURA", name: "ESTRUCTURA", width: "100px" },
      {
        data: "TIPO_CUENTA",
        name: "TIPO_CUENTA",
        render: function (data) {
          const tipos = {
            A: "Activo",
            P: "Pasivo",
            R: "Patrimonio",
            I: "Ingresos",
            G: "Gastos",
            B: "Balance",
          };
          return `<span class="badge badge-info">${tipos[data] || data}</span>`;
        },
      },
      {
        data: "NATURALEZA",
        name: "NATURALEZA",
        render: function (data) {
          const naturalezas = {
            D: "Deudora",
            A: "Acreedora",
          };
          return naturalezas[data] || data;
        },
      },
      {
        data: "ESTADO",
        name: "ESTADO",
        render: function (data) {
          return data == "1"
            ? '<span class="badge badge-success">Activo</span>'
            : '<span class="badge badge-danger">Inactivo</span>';
        },
      },
      { data: "IDMONEDA", name: "IDMONEDA" },
      {
        data: "ES_CTACTE",
        name: "ES_CTACTE",
        render: function (data) {
          return renderBoolean(data);
        },
      },
      {
        data: "ES_MONETARIA",
        name: "ES_MONETARIA",
        render: function (data) {
          return renderBoolean(data);
        },
      },
      {
        data: "ES_TITULO",
        name: "ES_TITULO",
        render: function (data) {
          return renderBoolean(data);
        },
      },
      {
        data: "CTA_ABONO1",
        name: "CTA_ABONO1",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "CTA_ABONO2",
        name: "CTA_ABONO2",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "CTA_CARGO1",
        name: "CTA_CARGO1",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "CTA_CARGO2",
        name: "CTA_CARGO2",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "CTA_GANANCIA",
        name: "CTA_GANANCIA",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "CTA_PERDIDA",
        name: "CTA_PERDIDA",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "PIDE_CCOSTO",
        name: "PIDE_CCOSTO",
        render: function (data) {
          return data === "1" || data === 1
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "PIDE_CODIGO",
        name: "PIDE_CODIGO",
        render: function (data) {
          return data === "1" || data === 1
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "AJUSTARXTC",
        name: "AJUSTARXTC",
        render: function (data) {
          return data === "1" || data === 1
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "TIPO_AJUSTE",
        name: "TIPO_AJUSTE",
        render: function (data) {
          return data ? data.trim() : "";
        },
      },
      {
        data: "TIPO_CAMBIO",
        name: "TIPO_CAMBIO",
        render: function (data) {
          return data ? data.trim() : "";
        },
      },
      {
        data: "SINCRONIZA",
        name: "SINCRONIZA",
        render: function (data) {
          return data === "S"
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "FECHACREACION",
        name: "FECHACREACION",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "ES_INGRESO",
        name: "ES_INGRESO",
        render: function (data) {
          return data === "1" || data === 1
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "CODIGO_SAP",
        name: "CODIGO_SAP",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "IDINCISO",
        name: "IDINCISO",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "ES_COSTO",
        name: "ES_COSTO",
        render: function (data) {
          return data === "S"
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "idcuentaeqv",
        name: "idcuentaeqv",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "descreqv",
        name: "descreqv",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "PIDE_DM",
        name: "PIDE_DM",
        render: function (data) {
          return data === "1" || data === 1
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "idcuenta_sunat",
        name: "idcuenta_sunat",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "IDCLASEGASTO",
        name: "IDCLASEGASTO",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "IDPERIODOGASTO",
        name: "IDPERIODOGASTO",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "IDCLIEPROV",
        name: "IDCLIEPROV",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "IDCTA_MIG",
        name: "IDCTA_MIG",
        render: function (data) {
          return data || "";
        },
      },
      {
        data: "pide_loteref",
        name: "pide_loteref",
        render: function (data) {
          return data === "1" || data === 1
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
      {
        data: "DISTRIBUIR",
        name: "DISTRIBUIR",
        render: function (data) {
          return data === "1" || data === 1
            ? '<i class="fa fa-check text-success"></i>'
            : '<i class="fa fa-times text-danger"></i>';
        },
      },
    ],

    // Otras opciones de configuración de DataTables
    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    language: {
      processing: "Procesando...",
      search: "Buscar:",
      lengthMenu: "Mostrar _MENU_ registros",
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      infoEmpty: "Mostrando 0 a 0 de 0 registros",
      infoFiltered: "(filtrado de _MAX_ registros totales)",
      loadingRecords: "Cargando...",
      zeroRecords: "No se encontraron resultados",
      emptyTable: "No hay datos disponibles en la tabla",
      paginate: {
        first: "Primero",
        previous: "Anterior",
        next: "Siguiente",
        last: "Último"
      },
      aria: {
        sortAscending: ": activar para ordenar la columna de manera ascendente",
        sortDescending: ": activar para ordenar la columna de manera descendente"
      },
      buttons: {
        excel: "Excel",
        pdf: "PDF",
        print: "Imprimir"
      },
      searchBuilder: {
        add: "Agregar",
        condition: "Condición",
        clearAll: "Limpiar todo",
        delete: "Eliminar",
        deleteTitle: "Eliminar regla de filtro",
        data: "Columna",
        left: "Izquierda",
        leftTitle: "Criterio anterior",
        logicAnd: "Y",
        logicOr: "O",
        right: "Derecha",
        rightTitle: "Criterio siguiente",
        title: {
          0: "Constructor de búsqueda",
          _: "Constructor de búsqueda (%d)"
        },
        value: "Valor",
        valueJoiner: "y"
      }
    },
    layout: {
      top1: "searchBuilder",
    },
    destroy: true,
  });
}
