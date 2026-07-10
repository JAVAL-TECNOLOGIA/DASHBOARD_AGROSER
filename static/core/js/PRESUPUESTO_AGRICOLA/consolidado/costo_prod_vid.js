$(document).ready(function () {
    $('#tablaConsolidadoProduccion').DataTable({
        scrollX: true,
        paging: true,
        searching: true,
        ordering: true,
        pageLength: 20,
        language: {
            url: "//cdn.datatables.net/plug-ins/1.10.20/i18n/Spanish.json",
            emptyTable: "No hay datos disponibles",
            zeroRecords: "No se encontraron resultados",
            infoEmpty: "Sin registros para mostrar",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
        }
    });

    console.log("thead:", $('#tablaConsolidadoProduccion thead tr:last th').length);
console.log("tbody:", $('#tablaConsolidadoProduccion tbody tr:first td').length);
});