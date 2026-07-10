function returnApproveOrders() {
  $("#fito_don_luis_almacen").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "fitosanidad - Don Luis",
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
    scrollX: true,
    scrollCollapse: true,
    fixedColumns: true,
    ajax: {
      url: "/nisira_almacen_don_luis_fito_Script/",
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
      { data: "periodo" },
      { data: "almacen" },
      { data: "documento" },
      { data: "año" },
      { data: "fecha" },
      { data: "estado" },
      { data: "item" },
      { data: "idproducto" },
      { data: "descripcion" },
      { data: "idmedida" },
      { data: "idingrediente" },
      { data: "descripcion_iac" },
      { data: "uac" },
      { data: "total" },
      { data: "totalxcil" },
      { data: "fraccionxcil" },
      { data: "documento_req" },
      { data: "doc_salida" },
    ],
    destroy: true,
  });
}

returnApproveOrders();
