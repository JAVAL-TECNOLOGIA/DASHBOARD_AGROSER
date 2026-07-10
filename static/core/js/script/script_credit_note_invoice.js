function returnCreditNoteInvoice(){
    table_show = $("#tableCreditNoteInvoice").DataTable({
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5', 
                title: 'REPORTE DE FACTURAS / NOTAS DE CRÉDITO - EMPRESA AGRO EXPORT ICA S.A.C.',
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
                                b: true,           // Turn off the default bolding of the header row
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
            url: '/credit_note_invoice_script/',
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
                    {'data':'sucursal'},
                    {'data':'razon_social'},
                    {'data':'producto'}, 
                    {'data':'moneda'},
                    {'data':'fecha_factura'},
                    {'data':'factura'},
                    {'data':'importe_factura'}, 
                    {'data':'tcambio_factura'},
                    {'data':'fecha_nota'}, 
                    {'data':'nota'},
                    {'data':'importe_nota'},
                    {'data':'tcambio_nota'},
                    {'data':'tipo_venta'},
                    {'data':'descripcion'},
                ],
                destroy: true,
    });    
}

returnCreditNoteInvoice();