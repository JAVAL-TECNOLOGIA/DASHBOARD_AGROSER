// Funciones para la Fase Intermedia de Evaluaciones

// Variable global para la tabla
let tablaEvaluacionesIntermedio;

// Variable para controlar si la tabla ya fue inicializada
let tablaIntermedioInicializada = false;

$(document).ready(function() {
    console.log("Script de Fase Intermedia cargado");
    
    // Inicializar eventos de los inputs de avance
    initializarEventosAvance();
    
    // Inicializar eventos del modal rápido
    initializarEventosAvanceRapido();
    
    // Inicializar la tabla inmediatamente
    // DataTables maneja correctamente las tablas en tabs ocultos
    console.log("Inicializando tabla de Fase Intermedia...");
    inicializarTablaEvaluacionesIntermedio();
    tablaIntermedioInicializada = true;

    // Listener para el filtro de campaña
    $('#filtroCampaniaDesempeno').on('change', function() {
        if (tablaEvaluacionesIntermedio) {
            var periodo = $('#filtroCampaniaDesempeno').val() || new Date().getFullYear();
            var nuevaUrl = '/gerencia_produccion/api/fase-intermedia/?id_area=21&campania=' + periodo;
            tablaEvaluacionesIntermedio.ajax.url(nuevaUrl).load();
        }
    });
    
    // Ajustar columnas cuando el tab se muestra
    $('a[href="#default-tab-2"]').on('shown.bs.tab', function (e) {
        console.log("Tab Fase Intermedia mostrado, ajustando columnas...");
        if (tablaEvaluacionesIntermedio) {
            setTimeout(function() {
                tablaEvaluacionesIntermedio.columns.adjust().draw();
            }, 200);
        }
    });
});

//########################################################
// INICIALIZAR TABLA DE EVALUACIONES - FASE INTERMEDIA
//########################################################
function inicializarTablaEvaluacionesIntermedio() {
    var periodo = $('#filtroCampaniaDesempeno').val() || new Date().getFullYear();
    var urlAjax = '/gerencia_produccion/api/fase-intermedia/?id_area=21&campania=' + periodo;
    tablaEvaluacionesIntermedio = $("#tablaEvaluaciones_intermedio").DataTable({
        dom: "Bfrtip",
        buttons: [
            {
                text: '<i class="fas fa-sync-alt"></i>',
                className: "btn-sm btn-secondary",
                action: function (e, dt, node, config) {
                    // Añadir animación de giro
                    $(node).find("i").addClass("fa-spin");
                    
                    // Recargar datos desde la API
                    cargarDatosFaseIntermedia();
                    
                    setTimeout(() => {
                        $(node).find("i").removeClass("fa-spin");
                    }, 1000);
                }
            },
            {
                extend: 'excelHtml5',
                text: '<i class="fas fa-file-excel"></i> Exportar a Excel',
                className: "btn-sm btn-success",
                exportOptions: {
                    columns: ':visible'
                }
            }
            
        ],
        
        // Configuración para Ajax
        ajax: {
            url: urlAjax,
            type: 'GET',
            dataSrc: function(json) {
                console.log("Datos recibidos de la API:", json);
                if (json.status === 'success') {
                    return json.data;
                } else {
                    console.error("Error en la respuesta de la API:", json.message);
                    mostrarMensaje('Error al cargar datos: ' + json.message, 'error');
                    return [];
                }
            },
            error: function(xhr, error, thrown) {
                if (error === 'abort') {
                    console.warn('Petición AJAX abortada, no se muestra mensaje de error');
                    return;
                }
                console.error("Error en la petición AJAX:", error, thrown);
                mostrarMensaje('Error de conexión al cargar datos', 'error');
            }

        },
        
        // Definición de columnas
        columns: [
            { 
                data: 'id_evaluacion',
                title: 'ID',
                visible: false
            },
            { 
                data: null,
                title: 'Evaluado',
                render: function(data, type, row) {
                    const nombreCompleto = `${row.nombre_evaluado || ''} ${row.apellido_evaluado || ''}`.trim();
                    const iniciales = nombreCompleto.split(' ').map(n => n.charAt(0)).join('').substring(0, 2).toUpperCase();
                    
                    return `
                        <div class="d-flex align-items-center">
                            <div class="modern-avatar bg-primary mr-2">
                                <span class="initials">${iniciales}</span>
                            </div>
                            <div class="user-info">
                                <div class="user-name">${nombreCompleto}</div>
                                <div class="user-role">${row.email_evaluado || 'Evaluado'}</div>
                            </div>
                        </div>
                    `;
                }
            },
            { 
                data: null,
                title: 'Evaluador',
                render: function(data, type, row) {
                    const nombreCompleto = `${row.nombre_evaluador || ''} ${row.apellido_evaluador || ''}`.trim();
                    const iniciales = nombreCompleto.split(' ').map(n => n.charAt(0)).join('').substring(0, 2).toUpperCase();
                    
                    return `
                        <div class="d-flex align-items-center">
                            <div class="modern-avatar bg-success mr-2">
                                <span class="initials">${iniciales}</span>
                            </div>
                            <div class="user-info">
                                <div class="user-name">${nombreCompleto}</div>
                                <div class="user-role">Supervisor</div>
                            </div>
                        </div>
                    `;
                }
            },
            { 
                data: 'periodo',
                title: 'Período'
            },
            { 
                data: 'nombre_area',
                title: 'Área'
            },
            { 
                data: null,
                title: 'Objetivos',
                render: function(data, type, row) {
                    const totalObjetivos = row.total_objetivos || 0;
                    const porcentaje = row.porcentaje_objetivos || 0;
                    
                    let badgeClass = 'badge-secondary';
                    let progressClass = 'bg-secondary';
                    
                    if (porcentaje >= 75) {
                        badgeClass = 'badge-success';
                        progressClass = 'bg-success';
                    } else if (porcentaje >= 50) {
                        badgeClass = 'badge-info';
                        progressClass = 'bg-info';
                    } else if (porcentaje >= 25) {
                        badgeClass = 'badge-warning';
                        progressClass = 'bg-warning';
                    } else if (porcentaje > 0) {
                        badgeClass = 'badge-danger';
                        progressClass = 'bg-danger';
                    }
                    
                    return `
                        <span class="badge ${badgeClass}">${totalObjetivos} Objetivos</span>
                        <div class="progress mt-1" style="height: 5px;">
                            <div class="progress-bar ${progressClass}" style="width: ${porcentaje}%"></div>
                        </div>
                        <small class="text-muted">${porcentaje}% completado</small>
                    `;
                }
            },
            { 
                data: null,
                title: 'Competencias',
                render: function(data, type, row) {
                    const totalCompetencias = row.total_competencias || 0;
                    const porcentaje = row.porcentaje_competencias || 0;
                    
                    let badgeClass = 'badge-secondary';
                    let progressClass = 'bg-secondary';
                    
                    if (porcentaje >= 75) {
                        badgeClass = 'badge-success';
                        progressClass = 'bg-success';
                    } else if (porcentaje >= 50) {
                        badgeClass = 'badge-info';
                        progressClass = 'bg-info';
                    } else if (porcentaje >= 25) {
                        badgeClass = 'badge-warning';
                        progressClass = 'bg-warning';
                    } else if (porcentaje > 0) {
                        badgeClass = 'badge-danger';
                        progressClass = 'bg-danger';
                    }
                    
                    return `
                        <span class="badge ${badgeClass}">${totalCompetencias} Competencias</span>
                        <div class="progress mt-1" style="height: 5px;">
                            <div class="progress-bar ${progressClass}" style="width: ${porcentaje}%"></div>
                        </div>
                        <small class="text-muted">${porcentaje}% completado</small>
                    `;
                }
            },
            { 
                data: 'porcentaje_general',
                title: 'Avance General',
                className: 'text-center',
                render: function(data, type, row) {
                    const porcentaje = data || 0;
                    let progressClass = 'bg-secondary';
                    
                    if (porcentaje >= 75) {
                        progressClass = 'bg-gradient-success';
                    } else if (porcentaje >= 50) {
                        progressClass = 'bg-gradient-primary';
                    } else if (porcentaje >= 25) {
                        progressClass = 'bg-gradient-warning';
                    } else if (porcentaje > 0) {
                        progressClass = 'bg-gradient-danger';
                    }
                    
                    return `
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated ${progressClass}" style="width: ${porcentaje}%">${porcentaje}%</div>
                        </div>
                    `;
                }
            },
            { 
                data: 'estado_avance',
                title: 'Estado',
                render: function(data, type, row) {
                    let badgeClass = 'badge-secondary';
                    
                    switch(data) {
                        case 'Completado':
                            badgeClass = 'badge-success';
                            break;
                        case 'En Progreso':
                            badgeClass = 'badge-warning';
                            break;
                        case 'Pendiente':
                            badgeClass = 'badge-info';
                            break;
                        case 'Sin Datos':
                            badgeClass = 'badge-secondary';
                            break;
                    }
                    
                    return `<span class="badge ${badgeClass}">${data || 'Sin Estado'}</span>`;
                }
            },
            { 
                data: null,
                title: 'Acciones',
                orderable: false,
                className: 'text-center',
                
                render: function(data, type, row) {
                    return `
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-secondary btn-sm" 
                                    onclick="abrirModalSeguimientoAvance(${row.id_evaluacion})" 
                                    title="Registrar Avance">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn btn-success btn-sm" 
                                    onclick="EmailManagerGereProd.generarEnviarPDFEvaluacion(${row.id_evaluacion})" 
                                    title="Generar pdf y enviar">
                                <i class='bxr  bx-envelope-open'  ></i> 
                            </button>
                        </div>
                    `;
                }
            }
        ],
        
        scrollX:    true,
        scrollCollapse: false,
        pageLength: 10,
        responsive: true,
        processing: true,
        
        language: {
            url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json",
            processing: "Cargando datos de evaluaciones...",
            emptyTable: "No hay evaluaciones disponibles",
            zeroRecords: "No se encontraron evaluaciones que coincidan"
        },
        
        rowCallback: function(row, data) {
            // Agregar evento de doble clic a toda la fila
            //$(row).attr('data-evaluacion-id', data.id_evaluacion);
            $(row).attr('ondblclick', `abrirModalSeguimientoAvance(${data.id_evaluacion})`);
            $(row).css('cursor', 'pointer');
        },
        
        initComplete: function (settings, json) {
            console.log("Tabla de fase intermedia inicializada correctamente");
            console.log("Total de registros cargados:", this.api().data().length);
        },
        
        destroy: true
    });
    
    return tablaEvaluacionesIntermedio;
}

//########################################################
// FUNCIÓN PARA CARGAR DATOS DESDE LA API
//########################################################
function cargarDatosFaseIntermedia() {
    console.log("Recargando datos de la API...");
    
    if (tablaEvaluacionesIntermedio) {
        tablaEvaluacionesIntermedio.ajax.reload(function(json) {
            console.log("Datos recargados:", json);
            mostrarMensaje('Datos actualizados correctamente', 'success');
        }, false);
    }
}

//########################################################
// FUNCIONES PARA MODAL DE AVANCE RÁPIDO (DOBLE CLICK)
//########################################################

// Variable global para el ID de evaluación actual
let evaluacionActualRapido = null;

// Función para abrir el modal de avance rápido
function abrirModalSeguimientoAvance(id_evaluacion) {
    console.log("Abriendo modal de avance rápido para evaluación:", id_evaluacion);
    
    // Asignar ID de evaluación ANTES de resetear
    evaluacionActualRapido = id_evaluacion;
    
    // Resetear el modal PERO SIN limpiar la variable evaluacionActualRapido
    resetModalseguimiento_avance();
    
    // Cargar datos del evaluado
    cargarDatosSeguimientoAvance(id_evaluacion);
    
    // Mostrar el modal
    $("#Modal_Seguimiento_Avance").modal("show");
}

// Alias para compatibilidad con botones de acciones
function abrirSeguimientoAvance(id_evaluacion) {
    return abrirModalSeguimientoAvance(id_evaluacion);
}

//########################################################
// FUNCIÓN PARA RESETEAR EL MODAL DE SEGUIMIENTO DE AVANCE
//########################################################
function resetModalseguimiento_avance() {
    // Resetear información del evaluado
    $("#evaluado_periodo").text("- -");
    $("#evaluado_nombre").text("");
    $("#evaluado_cargo").text("");
    $("#evaluado_area").text("");
    $("#evaluador_nombre").text("");
    
    // Resetear avatar con iniciales por defecto
    $(".modern-avatar .initials").text("--");
    
    // Resetear avance general
    $("#avance_general").css("width", "0%").text("0%");
    
    // Resetear contadores de pestañas
    $("#count_objetivos").text("0");
    $("#count_competencias").text("0");
    
    // Limpiar tablas de objetivos y competencias
    $("#tabla_objetivos_avance").empty();
    $("#tabla_competencias_avance").empty();
    
    // Limpiar comentarios generales
    $("#comentarios_objetivos_general").val("");
    $("#comentarios_competencias_general").val("");
    
    // Resetear pestañas - activar la primera pestaña
    $("#objetivos-avance-tab").addClass("active");
    $("#competencias-avance-tab").removeClass("active");
    $("#objetivos-avance").addClass("show active");
    $("#competencias-avance").removeClass("show active");
    
    // NO resetear evaluacionActualRapido aquí - se maneja en abrirModalSeguimientoAvance
    
    console.log("Modal de seguimiento de avance reseteado");
}

function cargarDatosSeguimientoAvance(id_evaluacion) {
    
    var periodo = $('#filtroCampaniaDesempeno').val() || new Date().getFullYear();
    
    $.ajax({
        url: `/gerencia_produccion/api/fase-intermedia/?campania=${periodo}`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {

            // devemos filtrar la lista porel objeto que tenga el id de evaluación actual
            const datosFiltrados = response.data.filter(item => item.id_evaluacion === id_evaluacion);
            
            mostrarInformacionEvaluado(datosFiltrados);
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar datos de seguimiento de avance:", error);
            mostrarMensaje('Error de conexión al cargar datos', 'error');
        }
    });


}


function mostrarInformacionEvaluado(datos) {

    console.log("Datos del evaluado:", datos);
    if (datos.length > 0) {
        const evaluado = datos[0];
        console.log("Evaluado seleccionado:", evaluado);
        $("#evaluado_periodo").text(evaluado.periodo);
        $("#nombre").text(evaluado.nombre_evaluado);
        $("#evaluado_cargo").text(evaluado.apellido_evaluado);
        $("#evaluado_area").text(evaluado.nombre_area);
        $("#evaluador_nombre").text(evaluado.nombre_evaluador);
        
        // Mostrar avatar con iniciales
        const iniciales = evaluado.nombre_evaluado.split(" ").map(n => n.charAt(0)).join("").toUpperCase();
        $(".modern-avatar .initials").text(iniciales);
        
        // Mostrar avance general
        $("#avance_general").css("width", evaluado.porcentaje_general + "%").text(evaluado.porcentaje_general + "%");
        
        // Mostrar contadores de pestañas
        $("#count_objetivos").text(evaluado.count_objetivos);
        $("#count_competencias").text(evaluado.count_competencias);
        
        // Cargar tablas de objetivos y competencias
        cargarTablaObjetivosAvance(evaluado.id_evaluacion);
        cargarTablaCompetenciasAvance(evaluado.id_evaluacion);
        
        // Cargar comentarios existentes
        cargarComentariosExistentes(evaluado.id_evaluacion);
    } else {
        console.warn("No se encontraron datos para el evaluado.");
    }
}

//########################################################
// FUNCIÓN PARA CARGAR COMENTARIOS EXISTENTES
//########################################################
function cargarComentariosExistentes(id_evaluacion) {
    console.log("Cargando comentarios existentes para evaluación:", id_evaluacion);
    
    $.ajax({
        url: `/gerencia_produccion/api/detalles-evaluacion/?id_evaluacion=${id_evaluacion}&cargar_comentarios=true`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Comentarios recibidos:", response);
            
            if (response.status === 'success' && response.comentarios) {
                // Cargar comentarios de objetivos
                if (response.comentarios.comentarios_objetivos_general) {
                    $("#comentarios_objetivos_general").val(response.comentarios.comentarios_objetivos_general);
                }
                
                // Cargar comentarios de competencias
                if (response.comentarios.comentarios_competencias_general) {
                    $("#comentarios_competencias_general").val(response.comentarios.comentarios_competencias_general);
                }
                
                console.log("Comentarios cargados exitosamente");
            } else {
                console.log("No se encontraron comentarios existentes");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar comentarios existentes:", error);
            // No mostrar error al usuario, ya que es funcionalidad secundaria
        }
    });
}




function cargarTablaObjetivosAvance(id_evaluacion) {
    console.log("Cargando tabla de objetivos para evaluación:", id_evaluacion);
    
    $.ajax({
        url: `/gerencia_produccion/api/detalles-evaluacion/?id_evaluacion=${id_evaluacion}&tipo=1`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Datos de objetivos recibidos:", response);
            
            if (response.status === 'success' && response.data && response.data.length > 0) {
                // Limpiar la tabla antes de cargar nuevos datos
                $("#tabla_objetivos_avance").empty();
                
                // Generar las filas de la tabla
                let filas = '';
                
                response.data.forEach(function(objetivo, index) {
                    // Determinar el color de la barra de progreso según el porcentaje
                    let progressClass = 'bg-secondary';
                    if (objetivo.porcentaje_actual >= 75) {
                        progressClass = 'bg-success';
                    } else if (objetivo.porcentaje_actual >= 50) {
                        progressClass = 'bg-info';
                    } else if (objetivo.porcentaje_actual >= 25) {
                        progressClass = 'bg-warning';
                    } else if (objetivo.porcentaje_actual > 0) {
                        progressClass = 'bg-danger';
                    }
                    
                    // Formatear las fechas
                    const fechaInicio = objetivo.fecha_inicio_formato || objetivo.fecha_inicio || 'N/A';
                    const fechaFin = objetivo.fecha_fin_formato || objetivo.fecha_fin || 'N/A';
                    
                    filas += `
                        <tr data-objetivo-id="${objetivo.id || index + 1}">
                            <td>
                                <strong>${objetivo.nombre_objetivo || objetivo.descripcion || 'Objetivo sin nombre'}</strong>
                                <br><small class="text-muted">${objetivo.descripcion || objetivo.detalle || 'Sin descripción'}</small>
                            </td>
                            <td>
                                <small class="text-muted">Inicio:</small> ${fechaInicio}
                                <br><small class="text-muted">Fin:</small> ${fechaFin}
                            </td>
                            <td>
                                <span class="badge badge-secondary">${objetivo.indicador || 'Sin indicador'}</span>
                            </td>
                            <td>${objetivo.meta || 'Sin meta definida'}</td>
                            <td>
                                <textarea class="form-control form-control-sm" rows="2" id="comentarios_objetivos_${objetivo.id || index + 1}" placeholder="Comentarios">${objetivo.comentarios_objetivos || ''}</textarea>
                            </td>
                            <td>
                                <div class="progress" style="height: 20px;">
                                    <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated ${progressClass}" style="width: ${objetivo.porcentaje_actual || 0}%">
                                        ${objetivo.porcentaje_actual || 0}%
                                    </div>
                                </div>
                            </td>
                            <td>
                                <input type="number" class="form-control form-control-sm avance-input" 
                                       value="${objetivo.porcentaje_actual || 0}" min="0" max="100" 
                                       data-objetivo-id="${objetivo.id || index + 1}">
                            </td>
                        </tr>
                    `;
                });
                
                // Insertar las filas en la tabla
                $("#tabla_objetivos_avance").html(filas);
                
                // Actualizar el contador en la pestaña
                $("#count_objetivos").text(response.data.length);
                
                console.log(`Se cargaron ${response.data.length} objetivos en la tabla`);
                
            } else {
                // Si no hay datos, mostrar mensaje
                $("#tabla_objetivos_avance").html(`
                    <tr>
                        <td colspan="6" class="text-center text-muted py-4">
                            <i class="fas fa-info-circle mr-2"></i>
                            No se encontraron objetivos para esta evaluación
                        </td>
                    </tr>
                `);
                
                $("#count_objetivos").text("0");
                console.log("No se encontraron objetivos para la evaluación");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar datos de objetivos:", error);
            
            // Mostrar mensaje de error en la tabla
            $("#tabla_objetivos_avance").html(`
                <tr>
                    <td colspan="6" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Error al cargar los objetivos. Por favor, inténtelo de nuevo.
                    </td>
                </tr>
            `);
            
            $("#count_objetivos").text("0");
            mostrarMensaje('Error al cargar objetivos: ' + error, 'error');
        }
    });
}





function cargarTablaCompetenciasAvance(id_evaluacion) {
    console.log("Cargando tabla de competencias para evaluación:", id_evaluacion);
    
    $.ajax({
        url: `/gerencia_produccion/api/detalles-evaluacion/?id_evaluacion=${id_evaluacion}&tipo=2`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Datos de competencias recibidos:", response);
            
            if (response.status === 'success' && response.data && response.data.length > 0) {
                // Limpiar la tabla antes de cargar nuevos datos
                $("#tabla_competencias_avance").empty();
                
                // Generar las filas de la tabla
                let filas = '';
                
                response.data.forEach(function(competencia, index) {
                    // Determinar el color de la barra de progreso según el porcentaje
                    let progressClass = 'bg-secondary';
                    if (competencia.porcentaje_actual >= 75) {
                        progressClass = 'bg-success';
                    } else if (competencia.porcentaje_actual >= 50) {
                        progressClass = 'bg-info';
                    } else if (competencia.porcentaje_actual >= 25) {
                        progressClass = 'bg-warning';
                    } else if (competencia.porcentaje_actual > 0) {
                        progressClass = 'bg-danger';
                    }
                    
                    // Determinar el color del badge según el tipo de competencia
                    let badgeClass = 'badge-secondary';
                    switch(competencia.tipo_competencia) {
                        case 'ESENCIAL':
                            badgeClass = 'badge-primary';
                            break;
                        case 'TECNICA':
                            badgeClass = 'badge-info';
                            break;
                        case 'INTERPERSONAL':
                            badgeClass = 'badge-success';
                            break;
                        case 'GERENCIAL':
                            badgeClass = 'badge-warning';
                            break;
                        default:
                            badgeClass = 'badge-secondary';
                    }
                    
                    filas += `
                        <tr data-competencia-id="${competencia.id}">
                            <td>
                                <strong>${competencia.nombre_competencia || 'Competencia sin nombre'}</strong>
                                <br><small class="text-muted">${competencia.descripcion_competencia || 'Sin descripción'}</small>
                            </td>
                            <td>
                                <span class="badge ${badgeClass}">${competencia.tipo_competencia || 'General'}</span>
                            </td>
                            <td>${competencia.meta || 'Sin meta definida'}</td>
                            <td><small>${competencia.comentarios || 'Sin comentarios'}</small></td>
                            <td>
                                <textarea class="form-control form-control-sm" rows="2" id="comentarios_competencias_${competencia.id || index + 1}" placeholder="Comentarios">${competencia.comentarios_competencias || ''}</textarea>
                            </td>
                            <td>
                                <div class="progress" style="height: 20px;">
                                    <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated ${progressClass}" style="width: ${competencia.porcentaje_actual || 0}%">
                                        ${competencia.porcentaje_actual || 0}%
                                    </div>
                                </div>
                            </td>
                            <td>
                                <input type="number" class="form-control form-control-sm avance-input" 
                                       value="${competencia.porcentaje_actual || 0}" min="0" max="100" 
                                       data-competencia-id="${competencia.id}">
                            </td>
                        </tr>
                    `;
                });
                
                // Insertar las filas en la tabla
                $("#tabla_competencias_avance").html(filas);
                
                // Actualizar el contador en la pestaña
                $("#count_competencias").text(response.data.length);
                
                console.log(`Se cargaron ${response.data.length} competencias en la tabla`);
                
            } else {
                // Si no hay datos, mostrar mensaje
                $("#tabla_competencias_avance").html(`
                    <tr>
                        <td colspan="6" class="text-center text-muted py-4">
                            <i class="fas fa-info-circle mr-2"></i>
                            No se encontraron competencias para esta evaluación
                        </td>
                    </tr>
                `);
                
                $("#count_competencias").text("0");
                console.log("No se encontraron competencias para la evaluación");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar datos de competencias:", error);
            
            // Mostrar mensaje de error en la tabla
            $("#tabla_competencias_avance").html(`
                <tr>
                    <td colspan="6" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Error al cargar las competencias. Por favor, inténtelo de nuevo.
                    </td>
                </tr>
            `);
            
            $("#count_competencias").text("0");
            mostrarMensaje('Error al cargar competencias: ' + error, 'error');
        }
    });
}

//########################################################
// FUNCIONES PARA ACTUALIZAR OBJETIVOS Y COMPETENCIAS
//########################################################

/**
 * Función para guardar avances de objetivos
 * Recopila todos los valores de los inputs de objetivos y los envía al servidor
 */
function guardarAvanceObjetivos() {
    console.log("Iniciando guardado de avance de objetivos...");
    console.log("Evaluación actual (objetivos):", evaluacionActualRapido);
    

    // Recopilar todos los inputs de objetivos modificados
    const actualizaciones = [];
    
    $("#tabla_objetivos_avance input.avance-input").each(function() {
        const input = $(this);
        const objetivoId = input.data('objetivo-id');
        const porcentajeActual = parseFloat(input.val()) || 0;

        // añadir el campo de comentarios
        const comentarios = $(`#comentarios_objetivos_${objetivoId}`).val() || '';
        console.log("Comentarios del objetivo ID " + objetivoId + ":", comentarios);
        
        // Validar que el porcentaje esté en el rango válido
        if (porcentajeActual < 0 || porcentajeActual > 100) {
            mostrarMensaje(`El porcentaje del objetivo ID ${objetivoId} debe estar entre 0 y 100`, 'warning');
            return;
        }
        
        actualizaciones.push({
            id: objetivoId,
            porcentaje_avance: porcentajeActual,
            comentarios_objetivos: comentarios
        });
    });
    
    if (actualizaciones.length === 0) {
        mostrarMensaje('No hay objetivos para actualizar', 'info');
        return;
    }
    
    // Verificar que tenemos el ID de evaluación
    if (!evaluacionActualRapido) {
        console.error("ERROR: evaluacionActualRapido es null al guardar objetivos");
        mostrarMensaje('Error: No se pudo identificar la evaluación', 'error');
        return;
    }
    
    // Obtener comentarios generales para objetivos
    const comentariosObjetivos = $("#comentarios_objetivos_general").val() || '';
    
    // Enviar actualizaciones al servidor incluyendo comentarios
    actualizarAvancesEnServidor(1, actualizaciones, 'objetivos', null, {
        comentarios_objetivos_general: comentariosObjetivos,
        id_evaluacion: evaluacionActualRapido
    });
}

/**
 * Función para guardar avances de competencias
 * Recopila todos los valores de los inputs de competencias y los envía al servidor
 */
function guardarAvanceCompetencias() {
    console.log("Iniciando guardado de avance de competencias...");
    console.log("Evaluación actual (competencias):", evaluacionActualRapido);
    
    // Recopilar todos los inputs de competencias modificados
    const actualizaciones = [];
    
    $("#tabla_competencias_avance input.avance-input").each(function() {
        const input = $(this);
        const competenciaId = input.data('competencia-id');
        const porcentajeActual = parseFloat(input.val()) || 0;
        
        // añadir el campo de comentarios
        const comentarioscompetencias = $(`#comentarios_competencias_${competenciaId}`).val() || '';
        console.log("Comentarios de la competencia ID " + competenciaId + ":", comentarioscompetencias);

        // Validar que el porcentaje esté en el rango válido
        if (porcentajeActual < 0 || porcentajeActual > 100) {
            mostrarMensaje(`El porcentaje de la competencia ID ${competenciaId} debe estar entre 0 y 100`, 'warning');
            return;
        }
        
        actualizaciones.push({
            id: competenciaId,
            porcentaje_avance: porcentajeActual,
            comentarios_competencias: comentarioscompetencias
        });
    });
    
    if (actualizaciones.length === 0) {
        mostrarMensaje('No hay competencias para actualizar', 'info');
        return;
    }
    
    // Verificar que tenemos el ID de evaluación
    if (!evaluacionActualRapido) {
        console.error("ERROR: evaluacionActualRapido es null al guardar competencias");
        mostrarMensaje('Error: No se pudo identificar la evaluación', 'error');
        return;
    }
    
    // Obtener comentarios generales para competencias
    const comentariosCompetencias = $("#comentarios_competencias_general").val() || '';
    
    // Enviar actualizaciones al servidor incluyendo comentarios
    actualizarAvancesEnServidor(2, actualizaciones, 'competencias', null, {
        comentarios_competencias_general: comentariosCompetencias,
        id_evaluacion: evaluacionActualRapido
    });
}

/**
 * Función para guardar todos los avances (objetivos y competencias)
 */
function guardarTodoElAvance() {
    console.log("Iniciando guardado de todos los avances...");
    
    // Primero intentar guardar objetivos
    const actualizacionesObjetivos = [];
    $("#tabla_objetivos_avance input.avance-input").each(function() {
        const input = $(this);
        const objetivoId = input.data('objetivo-id');
        const porcentajeActual = parseFloat(input.val()) || 0;
        
        if (porcentajeActual >= 0 && porcentajeActual <= 100) {
            actualizacionesObjetivos.push({
                id: objetivoId,
                porcentaje_avance: porcentajeActual
            });
        }
    });
    
    // Luego recopilar competencias
    const actualizacionesCompetencias = [];
    $("#tabla_competencias_avance input.avance-input").each(function() {
        const input = $(this);
        const competenciaId = input.data('competencia-id');
        const porcentajeActual = parseFloat(input.val()) || 0;
        
        if (porcentajeActual >= 0 && porcentajeActual <= 100) {
            actualizacionesCompetencias.push({
                id: competenciaId,
                porcentaje_avance: porcentajeActual
            });
        }
    });
    
    // Obtener comentarios generales
    const comentariosObjetivos = $("#comentarios_objetivos_general").val() || '';
    const comentariosCompetencias = $("#comentarios_competencias_general").val() || '';
    
    // Contador para manejar las actualizaciones asíncronas
    let actualizacionesPendientes = 0;
    let actualizacionesExitosas = 0;
    let actualizacionesFallidas = 0;
    
    // Función para verificar si todas las actualizaciones han terminado
    function verificarFinalizacion() {
        if (actualizacionesPendientes === 0) {
            if (actualizacionesFallidas === 0) {
                mostrarMensaje('Todos los avances se guardaron exitosamente', 'success');
                
                // Cerrar el modal después de 1 segundo
                setTimeout(() => {
                    $("#Modal_Seguimiento_Avance").modal("hide");
                    
                    // Reinicializar la tabla principal para refrescar los datos
                    if (tablaEvaluacionesIntermedio) {
                        tablaEvaluacionesIntermedio.destroy();
                    }
                    inicializarTablaEvaluacionesIntermedio();
                    
                }, 1000);
            } else {
                mostrarMensaje(`Guardado completado con ${actualizacionesExitosas} exitosas y ${actualizacionesFallidas} con errores`, 'warning');
                
                // Aún cerrar el modal y actualizar la tabla aunque haya algunos errores
                setTimeout(() => {
                    $("#Modal_Seguimiento_Avance").modal("hide");
                    
                    // Reinicializar la tabla principal para refrescar los datos
                    if (tablaEvaluacionesIntermedio) {
                        tablaEvaluacionesIntermedio.destroy();
                    }
                    inicializarTablaEvaluacionesIntermedio();
                    
                }, 1500);
            }
        }
    }
    
    // Enviar objetivos si hay datos
    if (actualizacionesObjetivos.length > 0) {
        actualizacionesPendientes++;
        actualizarAvancesEnServidor(1, actualizacionesObjetivos, 'objetivos', function(success) {
            actualizacionesPendientes--;
            if (success) {
                actualizacionesExitosas++;
            } else {
                actualizacionesFallidas++;
            }
            verificarFinalizacion();
        }, {
            comentarios_objetivos_general: comentariosObjetivos,
            id_evaluacion: evaluacionActualRapido
        });
    }
    
    // Enviar competencias si hay datos
    if (actualizacionesCompetencias.length > 0) {
        actualizacionesPendientes++;
        actualizarAvancesEnServidor(2, actualizacionesCompetencias, 'competencias', function(success) {
            actualizacionesPendientes--;
            if (success) {
                actualizacionesExitosas++;
            } else {
                actualizacionesFallidas++;
            }
            verificarFinalizacion();
        }, {
            comentarios_competencias_general: comentariosCompetencias,
            id_evaluacion: evaluacionActualRapido
        });
    }
    
    // Si no hay nada que actualizar
    if (actualizacionesPendientes === 0) {
        mostrarMensaje('No hay cambios para guardar', 'info');
    }
}

/**
 * Función genérica para enviar actualizaciones al servidor
 * @param {number} tipo - 1 para objetivos, 2 para competencias
 * @param {Array} actualizaciones - Array de objetos con id y porcentaje_avance
 * @param {string} tipoNombre - Nombre descriptivo del tipo (objetivos/competencias)
 * @param {Function} callback - Función callback opcional para manejar el resultado
 * @param {Object} comentarios - Objeto con comentarios generales e id_evaluacion
 */
function actualizarAvancesEnServidor(tipo, actualizaciones, tipoNombre, callback, comentarios = {}) {
    console.log(`Enviando ${actualizaciones.length} actualizaciones de ${tipoNombre} al servidor...`);
    
    // Mostrar indicador de carga
    const btnGuardar = tipo === 1 ? 
        $('button[onclick="guardarAvanceObjetivos()"]') : 
        $('button[onclick="guardarAvanceCompetencias()"]');
    
    const textoOriginal = btnGuardar.html();
    btnGuardar.prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-1"></i>Guardando...');
    
    // Preparar datos para enviar incluyendo comentarios
    const dataToSend = {
        tipo: tipo,
        actualizaciones: actualizaciones,
        ...comentarios  // Spread operator para incluir comentarios e id_evaluacion
    };
    
    console.log("Datos a enviar:", dataToSend);
    
    $.ajax({
        url: '/gerencia_produccion/api/detalles-evaluacion/',
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(dataToSend),
        success: function(response) {
            console.log(`Respuesta del servidor para ${tipoNombre}:`, response);
            
            if (response.status === 'success') {
                let mensaje = `${tipoNombre.charAt(0).toUpperCase() + tipoNombre.slice(1)} actualizados exitosamente`;
                if (response.data.comentarios_actualizados) {
                    mensaje += ' y comentarios guardados';
                }
                mostrarMensaje(mensaje, 'success');
                
                // Actualizar las barras de progreso en la tabla
                actualizarBarrasProgreso(tipo, actualizaciones);
                
                if (callback) callback(true);
                
            } else if (response.status === 'partial_success') {
                const exitosas = response.data.exitosas;
                const fallidas = response.data.fallidas;
                let mensaje = `${tipoNombre}: ${exitosas} actualizados, ${fallidas} con errores`;
                if (response.data.comentarios_actualizados) {
                    mensaje += ' y comentarios guardados';
                }
                mostrarMensaje(mensaje, 'warning');
                
                // Actualizar solo las barras de progreso exitosas
                const exitososIds = response.data.actualizaciones_exitosas.map(item => item.id);
                const actualizacionesExitosas = actualizaciones.filter(item => exitososIds.includes(item.id));
                actualizarBarrasProgreso(tipo, actualizacionesExitosas);
                
                if (callback) callback(true);
                
            } else {
                mostrarMensaje(`Error al actualizar ${tipoNombre}: ${response.message}`, 'error');
                if (callback) callback(false);
            }
        },
        error: function(xhr, status, error) {
            console.error(`Error al actualizar ${tipoNombre}:`, error);
            let mensaje = `Error de conexión al actualizar ${tipoNombre}`;
            
            if (xhr.responseJSON && xhr.responseJSON.message) {
                mensaje = `Error al actualizar ${tipoNombre}: ${xhr.responseJSON.message}`;
            }
            
            mostrarMensaje(mensaje, 'error');
            if (callback) callback(false);
        },
        complete: function() {
            // Restaurar el botón
            btnGuardar.prop('disabled', false).html(textoOriginal);
        }
    });
}

/**
 * Función para actualizar las barras de progreso en la tabla después de guardar
 * @param {number} tipo - 1 para objetivos, 2 para competencias
 * @param {Array} actualizaciones - Array de actualizaciones exitosas
 */
function actualizarBarrasProgreso(tipo, actualizaciones) {
    const tablaSelector = tipo === 1 ? "#tabla_objetivos_avance" : "#tabla_competencias_avance";
    
    actualizaciones.forEach(function(item) {
        const fila = $(`${tablaSelector} tr[data-${tipo === 1 ? 'objetivo' : 'competencia'}-id="${item.id}"]`);
        
        if (fila.length > 0) {
            // Actualizar la barra de progreso
            const progressBar = fila.find('.progress-bar');
            const nuevoAncho = item.porcentaje_avance + '%';
            
            progressBar.css('width', nuevoAncho).text(nuevoAncho);
            
            // Actualizar color de la barra según el porcentaje
            progressBar.removeClass('bg-secondary bg-danger bg-warning bg-info bg-success');
            if (item.porcentaje_avance >= 75) {
                progressBar.addClass('bg-success');
            } else if (item.porcentaje_avance >= 50) {
                progressBar.addClass('bg-info');
            } else if (item.porcentaje_avance >= 25) {
                progressBar.addClass('bg-warning');
            } else if (item.porcentaje_avance > 0) {
                progressBar.addClass('bg-danger');
            } else {
                progressBar.addClass('bg-secondary');
            }
        }
    });
}

//########################################################
// FUNCIONES DE UTILIDAD PARA EVENTOS
//########################################################

/**
 * Inicializar eventos de los inputs de avance
 */
function initializarEventosAvance() {
    // Agregar eventos a los inputs cuando se cargan dinámicamente
    $(document).on('input', '.avance-input', function() {
        const input = $(this);
        const valor = parseFloat(input.val());
        
        // Validar rango
        if (valor < 0) {
            input.val(0);
        } else if (valor > 100) {
            input.val(100);
        }
        
        // Agregar clase visual para indicar cambio
        input.addClass('changed');
    });
    
    // Evento para tecla Enter en inputs
    $(document).on('keypress', '.avance-input', function(e) {
        if (e.which === 13) { // Enter
            $(this).blur(); // Quitar foco del input
        }
    });
}

/**
 * Inicializar eventos del modal rápido (placeholder)
 */
function initializarEventosAvanceRapido() {
    // Aquí se pueden agregar eventos específicos del modal rápido
    console.log("Eventos del modal rápido inicializados");
}

//########################################################
// FUNCIÓN PARA MOSTRAR MENSAJES AL USUARIO
//########################################################

/**
 * Función para mostrar mensajes al usuario usando SweetAlert2 o alert básico
 * @param {string} mensaje - El mensaje a mostrar
 * @param {string} tipo - Tipo de mensaje: 'success', 'error', 'warning', 'info'
 */
function mostrarMensaje(mensaje, tipo = 'info') {
    // Verificar si SweetAlert2 está disponible
    if (typeof Swal !== 'undefined') {
        let icon;
        let title;
        
        switch(tipo) {
            case 'success':
                icon = 'success';
                title = 'Éxito';
                break;
            case 'error':
                icon = 'error';
                title = 'Error';
                break;
            case 'warning':
                icon = 'warning';
                title = 'Advertencia';
                break;
            case 'info':
            default:
                icon = 'info';
                title = 'Información';
                break;
        }
        
        Swal.fire({
            title: title,
            text: mensaje,
            icon: icon,
            timer: tipo === 'success' ? 3000 : 0,
            showConfirmButton: tipo !== 'success',
            toast: tipo === 'success',
            position: tipo === 'success' ? 'top-end' : 'center'
        });
    } else {
        // Fallback a alert básico si SweetAlert2 no está disponible
        alert(`${tipo.toUpperCase()}: ${mensaje}`);
    }
    
    // También logear en consola
    console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
}
