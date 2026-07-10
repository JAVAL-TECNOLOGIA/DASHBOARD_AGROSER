$(document).ready(function () {
  var table = $("#tableinversionesajs").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "REPORTES DE PROVISIONES INVERSIONES AJS",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          // Add an excelStyles definition
          {
            template: "green_medium", // Apply the 'green_medium' template
          },
          {
            cells: "sh", // Use Smart References (s) to target the header row (h)
            style: {
              // The style definition
              font: {
                // Style the font
                size: 12, // Size 14
                b: false, // Turn off the default bolding of the header row
              },
              fill: {
                // Style the cell fill
                pattern: {
                  // Add a pattern (default is solid)
                  color: "74ac48", // Define the fill color
                },
              },
            },
          },
        ],
      },
    ],
    sScrollX: "200%",
    sScrollXInner: "250%",
    autoWidth: true,
    scrollX: true,
    scrollCollapse: true,

    fixedColumns: true,
    ajax: {
      url: "/provisison_inversionesajs_script/",
      dataSrc: "",
    },
    searching: false,
    lengthChange: false,
    pageLength: 15,
    ordering: true,
    order: [[1, "desc"]],
    language: {
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
    },
    columns: [
      { data: "fecharegistro" },
      { data: "vencimiento" },
      { data: "diascreditos" },
      { data: "ruc" },
      { data: "razon_social" },
      { data: "iddocumento" },
      { data: "serie" },
      { data: "numero" },
      { data: "glosa" },
      { data: "idmoneda" },
      { data: "moneda" },
      { data: "importe" },
      { data: "porcentaje" },
      { data: "importe_total" },
    ],
    destroy: true,
  });

  // Filtro por fecha de vencimiento
  $("#vencimiento_filter_ajs").on("change", function () {
    var filterValue = this.value;
    var filterMonth = filterValue.split("-")[1];
    var filterYear = filterValue.split("-")[0];

    table.rows().every(function () {
      var data = this.data();
      var vencimiento = data.vencimiento; // Asumiendo que la fecha de vencimiento está en el campo 'vencimiento'
      var vencimientoMonth = vencimiento.split("-")[1];
      var vencimientoYear = vencimiento.split("-")[2];

      if (vencimientoMonth === filterMonth && vencimientoYear === filterYear) {
        $(this.node()).show();
      } else {
        $(this.node()).hide();
      }
    });
  });
});
