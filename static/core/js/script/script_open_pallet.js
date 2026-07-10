
//función para ejecturar el script de liberación de pallets
function open_pallet_script() {

    $.ajax ({
        url: "/open_pallet_script/" + $("#txtNroPallet").val() + "/",        
        type: "post",
        data: $("#formOpenPallet").serialize(),
        success: function(result){
            console.log(result, "success");
        },
        error: function (jqXhr, textStatus, errorMessage) {
            console.log("error");
        }
    });
}

//función de validación para el script de liberación de pallets
$("#btnOpenPallet").click(function(e){
    nro_pallet = $("#txtNroPallet").val();
    if (nro_pallet == "") {
        swal({
			title: 'Ingrese un número de paleta!',
			icon: 'error',
			buttons: {
				cancel: {
					text: 'Aceptar',
					value: null,
					visible: true,
					className: 'btn btn-default',
					closeModal: true,
				}
			}
		});
    } else {
        $.ajax({
            type: "GET",
            url : "/open_pallet_script_valid/" + nro_pallet +"/",
            success : function(data){                
                if (Object.values(data[0]) == 1){
                    swal({
                        title: 'Está seguro que se desea liberar el pallet?',
                        text: 'El pallet, "'+ nro_pallet +'" será liberado, recuerde que este procedo se debe hacer mucho cuidado!',
                        icon: 'info',
                        buttons: {
                            cancel: {
                                text: 'Cancelar',
                                value: null,
                                visible: true,
                                className: 'btn btn-default',
                                closeModal: true,
                            },
                            confirm: {
                                text: 'Aceptar',
                                value: true,
                                visible: true,
                                className: 'btn btn-primary',
                                closeModal: true
                            }
                        }
                    }).then(
                        function(){
                            $.ajax({
                                type: "GET",
                                data : {nro_pallet : nro_pallet},
                                url : "/open_pallet_script/" + nro_pallet +"/",
                                success: function(data) {
                                    console.log("This is the returned data: " + JSON.stringify(data));
                                    swal({
                                        title: 'La palleta ha sido liberada con éxito.',
                                        icon: 'success',
                                        buttons: {
                                            confirm: {
                                                text: 'Aceptar',
                                                value: true,
                                                visible: true,
                                                className: 'btn btn-success',
                                                closeModal: true
                                            }
                                        }
                                    });
                                    $("#txtNroPallet").val("");
                                },
                                error: function(error){
                                    console.log("Here is the error res: " + JSON.stringify(error));
                                    swal({
                                        title: 'Ocurrió un error al actualizar el pallet.',
                                        icon: 'error',
                                        buttons: {
                                            confirm: {
                                                text: 'Salir',
                                                value: true,
                                                visible: true,
                                                className: 'btn btn-danger',
                                                closeModal: true
                                            }
                                        }
                                    })
                                }
                            });
                        }
                    );
                } else {
                    swal({
                        title: 'El pallet ingresado no existe!',
                        icon: 'error',
                        buttons: {
                            cancel: {
                                text: 'Aceptar',
                                value: null,
                                visible: true,
                                className: 'btn btn-default',
                                closeModal: true,
                            }
                        }
                    });
                }
            },
            error : function(error){
                console.log("This is the error data: " + JSON.stringify(error));
            }
        });
    }
});

// Convierte los carácteres en mayúscula
function mayus(e) {
    e.value = e.value.toUpperCase();
}

