
$.get("../approve_orders_areas", function(data){
    $("#selectApproveArea").append("<option value='0'>Todos</option>");
    console.log($("#selectApproveArea").val());
    $.each(data, function(index,value){
        $("#selectApproveArea").append("<option value='"+value['idarea']+"'>"+value['descripcion']+"</option>")
    });
});


function returnApproveOrders(){
    table_show = $("#tableApproveOrders").DataTable({
        ajax : {
            url: '/approve_orders_log/',
            dataSrc: "",
        },
        searching: false,
        lengthChange: false,
        pageLength: 10,
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
                    {'data':'fecha'},
                    {'data':'documento'}, 
                    {'data':'num_documento'},
                    {'data':'moneda'},
                    {'data':'total'}, 
                    {'data':'proveedor'},
                    {'data':'estado'}, 
                    {'data':'area'},
                    {'data':'idorden', "visible": false}
                ],
                destroy: true,
    });    
}


function returnApproveOrdersFilter(){

    documento = $("#selectApproveDocument").val();
    serie = $("#txtApproveSerie").val();
    number = $("#txtApproveNumber").val();
    area = $("#selectApproveArea").val();

    table_show = $("#tableApproveOrders").DataTable({
        ajax : {
            url: '/approve_orders_log_filter/' + area + '/',
            dataSrc: "",
        },
        searching: false,
        lengthChange: false,
        pageLength: 10,
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
                    {'data':'fecha'},
                    {'data':'documento'}, 
                    {'data':'num_documento'},
                    {'data':'moneda'},
                    {'data':'total'}, 
                    {'data':'proveedor'},
                    {'data':'estado'}, 
                    {'data':'area'},
                    {'data':'idorden', "visible": false}
                ],
                destroy: true,
    });    
}


function returnApproveOrdersDoc(){
    $("#btnApproveShow").click(function(){
        $("#tableApproveOrders tbody").html('');
        if ($("#chkShowInputsApproveOrders").prop('checked')){
            returnApproveOrders();
        } else {
            $("#tableApproveOrders tbody").html('');                
            returnApproveOrdersFilter();
        }
    });
}
/*** returnApproveOrders(url_aof, $("#selectApproveArea").val()); */
function selectRowLot() {
    $('#tableApproveOrders tbody').on('dblclick', 'tr', function() {
        var row = table_show.row(this).data();
        var idservicio = row['idorden'];  
        if (row['documento'] == 'COMPRA'){
            $('#modalApproveOrders').modal('toggle');
            $.get("../approve_orders_log_detail_purchase/" + row['idorden']+"/", function(data){ 
                $("#lblProveedor").html(data[0]['proveedor']);
                $("#lblRuc").html(data[0]['ruc']);
                $("#lblCondicion").html(data[0]['formapago']);
                $("#lblResponsable").html(data[0]['responsable']);
                $("#lblTotal").html(data[0]['total_oc']);
                $("#tableBodyApproveOrdersLogDetail").html('');
                $.each(data, function(index,value){
                    //total = total +(Math.round(value['total'] * 100) / 100);
                    $("#tableApproveOrdersLogDetail").append("<tr><td>"+value['item']+"</td><td>"+value['producto']+"</td><td>"+value['idmedida']+"</td><td>"+value['cantidad']+"</td><td>"+value['precio_unitario']+"</td><td>"+value['impuesto']+"</td><td>"+parseFloat(value['total'])+"</td></tr>");
                });
            });
        } else {
            if (row['documento'] == 'SERVICIO') {
                $('#modalApproveOrders').modal('toggle');
                $.get("../approve_orders_log_detail_service/" + row['idorden'], function(data){      
                    $("#tableBodyApproveOrdersLogDetail").html('');
                    $.each(data, function(index,value){
                        $("#tableApproveOrdersLogDetail").append("<tr><td>"+value['item']+"</td><td>"+value['producto']+"</td><td>"+value['idmedida']+"</td><td>"+value['cantidad']+"</td><td>"+value['precio_unitario']+"</td><td>"+value['impuesto']+"</td><td>"+parseFloat(value['total'])+"</td></tr>");
                    });
                });
            } 
        }
        $('#btn-aprobar').click(function () {
            actualizarOrden('aprobar', idservicio);
        });

        $('#btn-vb').click(function () {
            actualizarOrden('vb', idservicio);
        });

        $('#btn-anular').click(function () {
            actualizarOrden('anular', idservicio);
        });
    });
}
function actualizarOrden(accion, idservicio) {
    // Realiza una solicitud AJAX al servidor para actualizar la orden de servicio
    $.ajax({
        url: '/actualizar-orden-servicio/' + idservicio + '/',
        type: 'GET', // Utiliza GET o POST según tu vista UpdateOrdenServicio
        data: { accion: accion },
        success: function (data) {
            // muestra un mensaje de éxito u otra acción adecuada
            alert('La orden de ha sido actualizada exitosamente.');
            window.location.reload();
        },
        error: function (error) {
            // Maneja cualquier error, muestra un mensaje de error u otra acción adecuada
            alert('Ocurrió un error al actualizar la orden.');
        }
    });
}



returnApproveOrdersDoc();
selectRowLot();