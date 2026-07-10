$(document).ready(function () {
  // Inicializar DataTables
  function returnApproveOrders() {
    $("#presupuesto_tic").DataTable({
      dom: "Bfrtip",
      buttons: [
        {
          extend: "excelHtml5",
          title: "Presupuesto - TIC",
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
      scrollX: false,
      scrollCollapse: true,
      fixedColumns: true,
      serverSide: false, // Ajusta según tu configuración
      ajax: {
        url: "/listar_presupuesto_tic/",
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
        { data: "id", visible: false },
        { data: "codigoproducto" },
        { data: "descripcion" },
        { data: "cantidad" },
        { data: "preciounitario" },
        { data: "fecha" },
        {
          data: null,
          render: function (data, type, row) {
            var cantidad = parseInt(row.cantidad, 10);
            var preciounitario = parseInt(row.preciounitario, 10);
            var total = cantidad * preciounitario;
            return total;
          },
          title: "Total",
        },
      ],
      destroy: true,
    });
  }

  returnApproveOrders();
});

// Guardar el estado de la pestaña activa en localStorage
$('a[data-toggle="tab"]').on("shown.bs.tab", function (e) {
  var activeTab = $(e.target).attr("href");
  localStorage.setItem("activeTab", activeTab);
});

// Leer el estado de la pestaña activa desde localStorage y activar la pestaña correspondiente
var activeTab = localStorage.getItem("activeTab");
if (activeTab) {
  $('a[href="' + activeTab + '"]').tab("show");
}

$(document).ready(function () {
  App.init();
});
