function returnApproveOrders(){
    table_show = $("#tableFacturaPrueba").DataTable({
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5', 
                title: 'REPORTES DE FACTURAS .',
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
        sScrollXInner: "200%",
        autoWidth: true,
        scrollX: true,
        scrollCollapse: true,
        
        ajax : {
            url: '/reporte_factura_prueba_script/',
            dataSrc: "",
        },
        searching: false,
        lengthChange: false,
        pageLength: 15,
        ordering: true,
        order: [[ 0, "desc" ]],
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
                    {'data':'item'},
                    {'data':'idcobrarpagardoc'},
                    {'data':'Sucursal'}, 
                    {'data':'Moneda'},
                    {'data':'RAZON_SOCIAL'},
                    {'data':'producto'},
                    {'data':'idlote'}, 
                    {'data':'fecha_factura'},
                    {'data':'serie_fact'}, 
                    {'data':'numero_fact'},
                    {'data':'importe_factura'},
                    {'data':'cantidad_fact'},
                    {'data':'tcambio_factura'},
                    {'data':'fecha_nota'},
                    {'data':'iddocumento'},
                    {'data':'serie_nota'},
                    {'data':'numero_nota'},
                    {'data':'importe_nota'},
                    {'data':'tcambio_nota'},
                    {'data':'Tipo de Venta'},
                    {'data':'Motivo_Nota'},
                ],
                destroy: true,
    });    
}

returnApproveOrders();