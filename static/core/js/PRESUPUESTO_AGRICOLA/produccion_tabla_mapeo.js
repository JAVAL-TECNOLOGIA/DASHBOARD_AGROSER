// JS para la Hoja 07: Tabla Completa de Mapeo
console.log('Mapeo JS cargado');

let tablaMapeo = null;

$(document).ready(function() {
    console.log('DOM listo, inicializando tabla mapeo');
    
    $('#recargarTablaMapeo').on('click', function() {
        console.log('Recargando tabla mapeo');
        if (tablaMapeo) {
            tablaMapeo.ajax.reload();
        } else {
            cargarTablaMapeo();
        }
    });
});

function cargarTablaMapeo() {
    const campaniaSelect = document.getElementById("select-campania").value;
    console.log('=== DEBUG FILTRO ===');
    console.log('Campaña seleccionada:', campaniaSelect);
    console.log('URL que se enviará:', '/presupuesto-agricola/api/mapeo_todo/?campania=' + campaniaSelect);
    
    $('#tablaMapeoCompleta').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: '/presupuesto-agricola/api/mapeo_todo/?campania=' + campaniaSelect,
            dataSrc: function(json) {
                console.log('Respuesta AJAX mapeo:', json);
                console.log('Número de registros recibidos:', json.data ? json.data.length : 0);
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
            { data: 'AREA_PRODUCTIVA' },
            { data: 'TOTAL_PLANTAS' },
            { data: 'OBSERVACION' },
        ],
        language: {
            url: window.dataTableEsUrl
        }
    });
}

