function returnListUser(){
	$.ajax({
		url : "/list_user/",
		type : "get",
		dataType : "json",
		success : function(response){
			if ($.fn.DataTable.isDataTable("#tableListUser")) {
				$("#tableListUser").DataTable().destroy();
			}						
			$("#tableListUser tbody").html("");
			$.each(response, function(index, value){
				$("#tableListUser tbody").append(
					'<tr>'+
						'<td>'+value['first_name']+'</td>'+
						'<td>'+value['last_name']+'</td>'+
						'<td>'+value['username'].toUpperCase()+'</td>'+
						'<td>'+value['email']+'</td>'+
						'<td>'+(value['active'] == true ? "Activo" : "Inactivo")+'</td>'+
						'<td>'+
							'<a href="#" class="btn btn-xs btn-warning" onclick="modal_update_user(\'/update_user/'+value['pk']+'/\')"><i class="far fa-edit"></i></a> '+	
							'<a href="#" class="btn btn-xs btn-info" onclick="modal_update_password(\'/update_password/' + value['pk'] + '/\')"><i class="fas fa-key"></i></a>' +
							/**+'<a href="#" class="btn btn-xs btn-danger" onclick="modal_disable_user(\'/disable_user/'+value['pk']+'/\')"><i class="fa fa-eye-slash"></i></a>'**/
						'</td>'+
					'</tr>'
				);
			});
		}
	});
}

returnListUser();