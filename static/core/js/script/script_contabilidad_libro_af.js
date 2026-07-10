// Función para inicializar o actualizar la DataTable
function initializeDataTable(data) {
  // Verificar si la DataTable ya está inicializada
  if ($.fn.DataTable.isDataTable("#tb_conta_libro_af")) {
    // Si ya está inicializada, actualizar los datos
    var table = $("#tb_conta_libro_af").DataTable();
    table.clear();
    table.rows.add(data);
    table.draw();
  } else {
    // Si no está inicializada, crearla
    $("#tb_conta_libro_af").DataTable({
      // Opciones de configuración
      dom: "Bfrtip",
      buttons: [
        {
          extend: "excelHtml5",
          title: "REPORTES_DISTRIBUCION_COSTOS_DETALLADO_CAMPO_VERDE",
          text: '<i class="far fa-file-excel"></i> Excel',
          className: "btn-sm btn-success",
          // Nota: 'excelStyles' no es una opción estándar de DataTables.
          // Si necesitas estilos personalizados, considera usar otra librería o procesar el archivo después de la exportación.
        },
      ],
      scrollX: true,
      autoWidth: false,
      fixedColumns: {
        leftColumns: 1, // Por ejemplo, fija la primera columna
      },
      processing: true,
      data: data, // Datos recibidos de la llamada AJAX
      searching: false,
      lengthChange: false,
      pageLength: 5,
      ordering: true,
      order: [[1, "desc"]], // Ordenar por la segunda columna de forma descendente
      language: {
        info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
        paginate: {
          first: "Primero",
          last: "Último",
          next: "Siguiente",
          previous: "Anterior",
        },
        emptyTable: "No hay datos disponibles en la tabla",
        loadingRecords: "Cargando...",
        processing: "Procesando...",
        zeroRecords: "No se encontraron registros que coincidan",
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
}

// Evento al hacer clic en el botón de filtrar
document.getElementById("filterButton").addEventListener("click", function () {
  var year = document.getElementById("year").value.trim();
  var month = document.getElementById("month").value.trim();
  var reportType = document.getElementById("reportType").value.trim();

  if (year && month && reportType) {
    // Mostrar el spinner antes de iniciar la solicitud AJAX
    document.getElementById("spinnerOverlay").style.display = "flex";

    $.ajax({
      url: "/script_contabilidad_libro_af/", // Asegúrate de que esta URL sea correcta
      method: "GET", // O "POST" dependiendo de tu configuración en el servidor
      data: { year: year, month: month, reportType: reportType },
      dataType: "json",
      success: function (data) {
        console.log("Datos recibidos:", data);

        if (Array.isArray(data) && data.length > 0) {
          initializeDataTable(data);
        } else {
          // Si la DataTable ya está inicializada, limpiarla
          if ($.fn.DataTable.isDataTable("#tb_conta_libro_af")) {
            var table = $("#tb_conta_libro_af").DataTable();
            table.clear().draw();
          }
          alert("No se recibieron datos para mostrar.");
        }
      },
      error: function (xhr, status, error) {
        console.error("Error en la solicitud AJAX:", error);
        console.error("Respuesta del servidor:", xhr.responseText);
        alert(
          "Ocurrió un error al obtener los datos. Por favor, intenta nuevamente."
        );
      },
      complete: function () {
        // Ocultar el spinner después de que la solicitud AJAX se complete (éxito o error)
        document.getElementById("spinnerOverlay").style.display = "none";
      },
    });
  } else {
    alert("Por favor, ingrese el año, el mes y seleccione el tipo de reporte.");
  }
});

// Inicializar la tabla vacía al cargar la página
$(document).ready(function () {
  initializeDataTable([]);
});
