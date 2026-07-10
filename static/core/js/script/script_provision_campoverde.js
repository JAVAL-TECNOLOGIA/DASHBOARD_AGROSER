$(document).ready(function () {
  var table = $("#tablecampoverde").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "REPORTES DE PROVISIONES CAMPO VERDE",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
          {
            cells: "sh",
            style: {
              font: {
                size: 12,
                b: false,
              },
              fill: {
                pattern: {
                  color: "74ac48",
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
      url: "/provisison_campoverde_script/",
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
  $("#vencimiento_filter_cv").on("change", function () {
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
