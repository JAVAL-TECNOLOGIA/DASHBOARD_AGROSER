$(document).ready(function () {
// Tabla: Compras de Uva
   /* $('#tablaComprasCostos').DataTable({
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
    });*/

     $('#tablaComprasCostos').DataTable({
        ajax: {
            url: "api/compras/lotes/",
            dataSrc: 'data'
        },
        processing: true,
        deferRender: true,
        scrollX: true,
        pageLength: 25,
        order: [],

        columns: [
            { data: 'sector' },
            { data: 'condicion' },
            { data: 'lote' },
            { data: 'area_total' },
            { data: 'variedad' },
            { data: 'plantas_lote' },
            { data: 'plantas_ha' },

            { data: 'compost_guano' },
            { data: 'sulfato_calcio' },
            { data: 'total_mo' },

            { data: 'en_formacion_agro' },
            { data: 'en_formacion_ferti' },
            { data: 'en_formacion_total' },

            { data: 'post_agro' },
            { data: 'post_ferti' },
            { data: 'post_total' },

            { data: 'repoda' },
            { data: 'prod_agro' },
            { data: 'prod_ferti' },
            { data: 'prod_total' },

            { data: 'combustible' },
            { data: 'plantulas' },
            { data: 'repuestos' },

            { data: 'total_lote' }
        ],

        language: {
            url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json"
        },
        columnDefs: [
            { targets: [7,8,9], className: 'col-mo text-center' },
            { targets: [10,11,12], className: 'col-formacion text-center' },
            { targets: [13,14,15], className: 'col-post text-center' },
            { targets: [16,17,18,19], className: 'col-produccion text-center' },
            { targets: [23], className: 'col-total text-center' }
        ],

       /* columnDefs: [
            { targets: -1, className: 'font-weight-bold text-success' },
            { targets: '_all', className: 'text-center' }
        ]*/
    });

    console.log("thead:", $('#tablaComprasUva thead tr:last th').length);
console.log("tbody:", $('#tablaComprasUva tbody tr:first td').length);
});