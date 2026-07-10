document.getElementById("filterButton").addEventListener("click", function () {
  var year = document.getElementById("year").value;
  var month = document.getElementById("month").value;
  var reportType = document.getElementById("reportType").value;

  if (year && month && reportType) {
    $.ajax({
      url: "/script_contabilidad_libro_af/",
      data: { year: year, month: month, reportType: reportType },
      success: function (data) {
        // Procesa los datos recibidos y actualiza la interfaz de usuario
        console.log(data);
        // Destruir la tabla existente si ya está inicializada
        if ($.fn.DataTable.isDataTable("#tb_conta_libro_af")) {
          $("#tb_conta_libro_af").DataTable().clear().destroy();
        }
        // Inicializar la tabla con los nuevos datos
        initializeDataTable(data);
      },
      error: function (xhr, status, error) {
        console.error("Error:", error);
        console.error("Response:", xhr.responseText);
      },
    });
  } else {
    alert("Por favor, ingrese el año, el mes y seleccione el tipo de reporte.");
  }
});

function initializeDataTable(data) {
  $("#tb_conta_libro_af").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "REPORTES_DISTRIBUCION_COSTOS_DETALLADO- CAMPO VERDE",
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
                size: 14,
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
    processing: true,
    data: data, // Usar los datos recibidos en la llamada AJAX
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
      { data: "IDTIPOACTIVO" },
      { data: "DSC_TIPOACTIVO" },
      { data: "IDACTIVO" },
      { data: "CODALTERNO" },
      { data: "CODMANUAL" },
      { data: "IDCTAACTIVO" },
      { data: "DESCRIPCION" },
      { data: "FECHACOMPRA" },
      { data: "FECHAACTIVACION" },
      { data: "IDMARCA" },
      { data: "MARCA" },
      { data: "IDMODELO" },
      { data: "MODELO" },
      { data: "SERIE" },
      { data: "FUNCION" },
      { data: "VIDAUTIL" },
      { data: "IDMEDIDA" },
      { data: "TASA_ANUAL" },
      { data: "HCOMPRASMOF" },
      { data: "HCOMPRASMEX" },
      { data: "ACOMPRASMOF" },
      { data: "ACOMPRASMEX" },
      { data: "MCOMPRASMOF" },
      { data: "MCOMPRASMEX" },
      { data: "AINFLACION" },
      { data: "HBAJAMOF" },
      { data: "HBAJAMEX" },
      { data: "OAJUSTESMOF" },
      { data: "OAJUSTESMEX" },
      { data: "LIBACTIMOF" },
      { data: "LIBACTIMEX" },
      { data: "HDEPRECIACIONESMOF" },
      { data: "HDEPRECIACIONESMEX" },
      { data: "ADEPRECIACIONESMOF" },
      { data: "ADEPRECIACIONESMEX" },
      { data: "BDEPRECIACIONESMOF" },
      { data: "BDEPRECIACIONESMEX" },
      { data: "ODEPRECIACIONESMOF" },
      { data: "ODEPRECIACIONESMEX" },
      { data: "DLIBACTIMOF" },
      { data: "DLIBACTIMEX" },
      { data: "ULTIMO_CCOSTO" },
      { data: "DSC_CUENTA" },
      { data: "DSC_UBICACION" },
      { data: "PROVEEDOR" },
      { data: "DSC_FACTURA" },
      { data: "CANTIDADI" },
      { data: "CANTIDADS" },
      { data: "CANTIDAD" },
      { data: "IDPRODUCTO" },
    ],
  });
}

// Inicializar la tabla por primera vez sin datos
initializeDataTable([]);
