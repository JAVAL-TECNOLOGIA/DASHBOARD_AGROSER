// Inicializar App y cargar líneas al inicio
$(document).ready(function(){
    App.init();
    cargarLineas();

    // Inicializar botones de copiar
    var clipboard = new ClipboardJS('.copy-btn');

    // ===============================
    // BOTÓN PARA EXPORTAR A VCF
    // ===============================
    $('#btnExportVCF').on('click', function() {
        var data = window.tableLineas.rows().data(); // TODAS las filas
        let contactos = [];
        for (let i = 0; i < data.length; i++) {
            contactos.push({
                nombres_apellidos: data[i][2],
                telefono: data[i][1].trim(),
                correo: data[i][5],
                cargo: data[i][3],
                area: data[i][4]
            });
        }
        descargarVCard(contactos);
    });
});

// =========================
// CARGAR DATOS EN LA TABLA
// =========================
function cargarLineas(){
    $.get('/api-linea-celulares/', function(response){
        let tbody = '';
        response.data.forEach(function(linea){
            tbody += `<tr>
                <td>${linea.ID_LN}</td>
                <td>
                    ${linea.TELEFONO} 
                </td>
                <td>${linea.NOMBRES_APELLIDOS}</td>
                <td>${linea.CARGO || ''}</td>
                <td>${linea.AREA || ''}</td>
                <td>${linea.CORREO || ''}</td>
            </tr>`;
        });
        $('#tableLineasCelulares tbody').html(tbody);

        if ($.fn.DataTable.isDataTable('#tableLineasCelulares')) {
            $('#tableLineasCelulares').DataTable().destroy();
        }
        window.tableLineas = $('#tableLineasCelulares').DataTable({  // <-- guardamos la instancia
            responsive: true,
            pageLength: 15, // mostrar 25 filas por página
            lengthMenu: [10, 25, 50, 100] // opciones del selector de cantidad de filas
            // dom: 'Bfrtip',
            // buttons: [
            //     {
            //         extend: 'csvHtml5',
            //         text: '📥 Exportar CSV',
            //         className: 'btn btn-primary',
            //         filename: 'lineas_celulares',
            //         exportOptions: { columns: ':not(:last-child)' },
            //         enabled: false // lo mantiene inactivo, no visible
            //     }
            // ]
        });
    });
}

// =========================
// MODAL CREAR
// =========================
function modal_create_linea(){
    let html = `<form id="formCreateLinea">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h4 class="modal-title">Agregar Línea Celular</h4>
                    <button type="button" class="close" data-dismiss="modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group"><label>Teléfono</label>
                        <input type="text" name="telefono" class="form-control" maxlength="9" required></div>
                    <div class="form-group"><label>Nombres y Apellidos</label>
                        <input type="text" name="nombres_apellidos" class="form-control" required></div>
                    <div class="form-group"><label>Cargo</label>
                        <input type="text" name="cargo" class="form-control"></div>
                    <div class="form-group"><label>Área</label>
                        <input type="text" name="area" class="form-control"></div>
                    <div class="form-group"><label>Correo</label>
                        <input type="email" name="correo" class="form-control" required></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" onclick="saveCreateLinea()">Guardar</button>
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
                </div>
            </div>
        </div>
    </form>`;
    $('#modalCreateLinea').html(html).modal('show');
}

function saveCreateLinea(){
    let data = {
        telefono: $('#formCreateLinea [name="telefono"]').val(),
        nombres_apellidos: $('#formCreateLinea [name="nombres_apellidos"]').val(),
        cargo: $('#formCreateLinea [name="cargo"]').val(),
        area: $('#formCreateLinea [name="area"]').val(),
        correo: $('#formCreateLinea [name="correo"]').val()
    };
    $.ajax({
        url: '/api-linea-celulares/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response){
            $('#modalCreateLinea').modal('hide');
            swal('Línea registrada!', '', 'success');
            cargarLineas();
        },
        error: function(error){
            console.log(error.responseText);
            alert('Error al crear línea');
        }
    });
}

// =========================
// MODAL EDITAR
// =========================
function modal_update_linea(id){
    $.get(`/api-linea-celulares/${id}/`, function(linea){
        let html = `<form id="formUpdateLinea">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h4 class="modal-title">Editar Línea Celular</h4>
                        <button type="button" class="close" data-dismiss="modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group"><label>ID</label>
                            <input type="text" class="form-control" value="${linea.ID_LN}" readonly></div>
                        <div class="form-group"><label>Teléfono</label>
                            <input type="text" name="telefono" class="form-control" value="${linea.TELEFONO}" required></div>
                        <div class="form-group"><label>Nombres y Apellidos</label>
                            <input type="text" name="nombres_apellidos" class="form-control" value="${linea.NOMBRES_APELLIDOS}" required></div>
                        <div class="form-group"><label>Cargo</label>
                            <input type="text" name="cargo" class="form-control" value="${linea.CARGO || ''}"></div>
                        <div class="form-group"><label>Área</label>
                            <input type="text" name="area" class="form-control" value="${linea.AREA || ''}"></div>
                        <div class="form-group"><label>Correo</label>
                            <input type="email" name="correo" class="form-control" value="${linea.CORREO || ''}" required></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="saveUpdateLinea(${id})">Guardar</button>
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
                    </div>
                </div>
            </div>
        </form>`;
        $('#modalUpdateLinea').html(html).modal('show');
    });
}

function saveUpdateLinea(id){
    let data = {
        telefono: $('#formUpdateLinea [name="telefono"]').val(),
        nombres_apellidos: $('#formUpdateLinea [name="nombres_apellidos"]').val(),
        cargo: $('#formUpdateLinea [name="cargo"]').val(),
        area: $('#formUpdateLinea [name="area"]').val(),
        correo: $('#formUpdateLinea [name="correo"]').val()
    };
    $.ajax({
        url: `/api-linea-celulares/${id}/`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response){
            $('#modalUpdateLinea').modal('hide');
            swal('Línea actualizada!', '', 'success');
            cargarLineas();
        },
        error: function(error){
            console.log(error.responseText);
            alert('Error al actualizar línea');
        }
    });
}

// =========================
// MODAL ELIMINAR
// =========================
function modal_delete_linea(id){
    let html = `<div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title">Eliminar Línea</h4>
                <button type="button" class="close" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">¿Estás seguro de eliminar esta línea?</div>
            <div class="modal-footer">
                <button type="button" class="btn btn-danger" onclick="deleteLinea(${id})">Eliminar</button>
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
            </div>
        </div>
    </div>`;
    $('#modalDeleteLinea').html(html).modal('show');
}

function deleteLinea(id){
    $.ajax({
        url: `/api-linea-celulares/${id}/`,
        type: 'DELETE',
        success: function(response){
            $('#modalDeleteLinea').modal('hide');
            swal('Línea eliminada!', '', 'success');
            cargarLineas();
        },
        error: function(error){
            alert('Error al eliminar línea');
        }
    });
}


function descargarVCard(contactos) {
    let vcfContent = '';

    contactos.forEach(c => {
        vcfContent += `BEGIN:VCARD
VERSION:3.0
FN:${c.nombres_apellidos}
TEL;TYPE=CELL:${c.telefono}
EMAIL:${c.correo || ''}
ORG:${c.area || ''}
TITLE:${c.cargo || ''}
END:VCARD
`;
    });

    // Crear archivo y descargar
    const blob = new Blob([vcfContent], { type: 'text/vcard' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'lineas_celulares.vcf';
    a.click();
    URL.revokeObjectURL(url);
}
