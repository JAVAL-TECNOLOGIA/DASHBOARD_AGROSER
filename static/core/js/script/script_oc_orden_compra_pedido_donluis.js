function returnApproveOrders(){
    table_show = $("#tablepedidodonluis").DataTable({
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5', 
                title: 'REPORTES DE PEDIDOS COMPRAS- DON LUIS',
                text:'<i class="far fa-file-excel"></i> Excel',
                className: 'btn-sm btn-success', 
                excelStyles: [                      // Add an excelStyles definition
                    {                 
                        template: 'green_medium',   // Apply the 'green_medium' template
                    },
                    {
                        cells: 'sh',                // Use Smart References (s) to target the header row (h)
                        style: {                    // The style definition
                            font: {                 // Style the font
                                size: 14,           // Size 14
                                b: false,           // Turn off the default bolding of the header row
                            },
                            fill: {                 // Style the cell fill
                                pattern: {          // Add a pattern (default is solid)
                                    color: '74ac48' // Define the fill color
                                }
                            }
                        }
                    }
                ]
            }
        ],
        sScrollX: "200%",
        sScrollXInner: "250%",
        autoWidth: true,
        scrollX: true,
        scrollCollapse: true,
        
        fixedColumns: true,
        ajax : {
            url: '/order_oc_pedido_donluis_script/',
            dataSrc: "",
        },
        searching: false,
        lengthChange: false,
        pageLength: 15,
        ordering: true,
        order: [[ 1, "desc" ]],
        language: {
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            paginate: {
                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"
            },
        },
        columns : [
                    {'data':'iddocumento_pe'},
                    {'data':'serie_pe'},
                    {'data':'numero_pe'},
                    {'data':'codigopedido'},
                    {'data':'fechapedido'}, 
                    {'data':'pedidoaprobacion'},
                    {'data':'responsables'},
                    {'data':'idproducto'},
                    {'data':'descripcionproducto'}, 
                    {'data':'cantidad'},
                    {'data':'unidadmedida'}, 
                    {'data':'itemestado'},
                    {'data':'pedidoestado'},
                    {'data':'iddocumento_oc'},
                    {'data':'serie_oc'},
                    {'data':'numero_oc'},
                    {'data':'codigocompra'},
                    {'data':'fechacompra'},
                    {'data':'compraaprobacion'},
                ],
                destroy: true,
    });    
}

returnApproveOrders();