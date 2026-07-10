// JS para la Hoja 07: Tabla Completa de Mapeo
console.log('Mapeo JS cargado');
$(document).ready(function() {
    console.log('DOM listo, inicializando tabla mapeo');
    cargarTablaMapeo();
    $('#recargarTablaMapeo').on('click', function() {
        console.log('Recargando tabla mapeo');
        cargarTablaMapeo();
    });
});

function cargarTablaMapeo() {
    const campaniaSelect = document.getElementById("select-campania").value;
    $('#tablaMapeoCompleta').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: '/produccionuva1/api/mapeo_todo/?campania=' + campaniaSelect,
            dataSrc: function(json) {
                console.log('Respuesta AJAX mapeo:', json);
                return json.data;
            }
        },
        columns: [
            { data: 'ID_MAPEO' },
            { data: 'FECHA' },
            { data: 'ID_ASIGNACION' },
            { data: 'HILERA' },
            { data: 'PLANTA' },
            { data: 'DENSIDAD' },
            { data: 'PLANTA_PRODUCTIVA' },
            { data: 'PLANTA_FORMACION' },
            { data: 'PLANTA_ENFERMA' },
            { data: 'PLANTA_CORDON' },
            { data: 'PLANTA_MUERTAS' },
            { data: 'PLANTA_AUSENTE' },
            { data: 'PLANTA_OTRA_VARIEDAD' },
            { data: 'PLANTA_NO_PRODUCTIVAS' },
            { data: 'AREA_PRODUCTIVA' },
            { data: 'TOTAL_PLANTAS' }
        ],
        language: {
            url: window.dataTableEsUrl
        }
    });
}
