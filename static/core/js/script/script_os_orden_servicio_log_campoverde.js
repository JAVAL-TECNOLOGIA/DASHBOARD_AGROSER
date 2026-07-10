function returnApproveOrders(){
    table_show = $("#tableOCcampoverde").DataTable({
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5', 
                title: 'REPORTES DE ORDENES DE SERVICIO - CAMPO VERDE.',
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
        
        ajax : {
            url: '/order_os_log_campoverde_script/',
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
                    {'data':'estado'},
                    {'data':'documento'},
                    {'data':'razon_social'}, 
                    {'data':'idproducto'},
                    {'data':'producto'},
                    {'data':'unidad'},
                    {'data':'cantidad'}, 
                    {'data':'precio_unitario'},
                    {'data':'total'},
                    {'data':'moneda'},
                    {'data':'idconsumidor'},
                    {'data':'consumidor'},
                    {'data':'sucursal'},
                    {'data':'almacen'},
                    {'data':'fecha'},
                    {'data':'periodo'}
                ],
                destroy: true,
    });    
}

returnApproveOrders();