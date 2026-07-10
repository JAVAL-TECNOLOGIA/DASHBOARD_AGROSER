$("#btnPalletLogShow").click(function(){

    from = formatStringToDate($("#txtPalletLogFrom").val());
    until = formatStringToDate($("#txtPalletLogUntil").val());

    from_format = from.getDate() + "-" + (from.getMonth() + 1) + "-" + from.getFullYear();
    until_format = until.getDate() + "-" + (until.getMonth() + 1) + "-" + until.getFullYear();

    table_show = $("#tablePalletizingLog").DataTable({
        ajax : {
            url: '/palletizing_log_script/' + from_format +'/' + until_format +'/',
            dataSrc: "",
        },
        searching: false,
        lengthChange: false,
        pageLength: 10,
        order: [[ 0, "desc" ]],
        destroy: true,
        language: {
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            paginate: {
                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"
            },
        },
        columns : [{"data":"FECHA"}, {'data':'ENVASE'},{'data':'RAZON_SOCIAL'},{'data':'TIPO'},{'data':'NROPALETA'}, {'data':'CALIBRE'},{'data':'CANTIDAD'}, {'data':'ESTADO'}],
    });
    selectRowLot();
});



function selectRowLot() {
    $('#tablePalletizingLog tbody').on('dblclick', 'tr', function() {
        var row = table_show.row(this).data();    
        $('#modalPalletizingLogDetail').modal('toggle');
        $.get("../palletizing_log_script_detail/" + row['NROPALETA'], function(data){
            cantidad = 0;
            $("#lblPackage").html(data[0]['PRODUCTO']);
            $("#lblNroPallet").html(data[0]['NROPALETA']);  
            $("#lblClienteDestino").html(data[0]['CLIENTE_DESTINO']);  
            $("#lblCantidad").html(cantidad);   
            console.log(data);         
            $("#tableBodyPalletizingLogDetails").html('');
            $.each(data, function(index,value){
                cantidad = cantidad + parseInt(value['CANTIDAD']);
                $("#tablePalletizingLogDetails").append("<tr><td>"+value['ITEM']+"</td><td>"+value['RAZONSOCIAL']+"</td><td>"+value['FECHA']+"</td><td>"+value['TAG']+"</td><td>"+value['PRODUCTO']+"</td><td>"+value['CALIBRE']+"</td><td>"+value['PRESENTACION']+"</td><td>"+value['CANTIDAD']+"</td></tr>");
            });
            $("#lblCantidad").html(cantidad); 
            $("#pdfBarcode").barcode(data[0]['NROPALETA'],"code128",{fontSize:0,barHeight:80});
        });
    });
}

function formatStringToDate(text) {
    var myDate = text.split('/');
    return new Date(myDate[2], myDate[1] - 1, myDate[0]);
}

