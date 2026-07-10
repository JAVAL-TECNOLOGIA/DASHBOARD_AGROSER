// Funciones para la Fase Final de Evaluaciones
$(document).ready(function() {
    console.log("Inicializando Fase Final...");
    inicializarTablaEvaluacionesFinal();

    // Listener para el filtro de campaña
    $('#filtroCampaniaDesempeno').on('change', function() {
        if (tablaEvaluacionesFinal) {
            var periodo = $('#filtroCampaniaDesempeno').val() || new Date().getFullYear();
            var nuevaUrl = '/rrhh/api/fase-final/?id_area=13&campania=' + periodo;
            tablaEvaluacionesFinal.ajax.url(nuevaUrl).load();
        }
    });

    // Inicializar eventos de los inputs de avance final
    initializarEventosAvanceFinal();

    // Manejar evento del modal para evitar advertencias de aria-hidden
    $('#Modal_Seguimiento_Avance_Final').on('hide.bs.modal', function () {
        // Remover focus de todos los elementos dentro del modal antes de ocultarlo
        $(this).find("input, textarea, button, select").blur();
    });
});

// Variable global para la tabla de fase final
let tablaEvaluacionesFinal;

//########################################################
// INICIALIZAR TABLA DE EVALUACIONES - FASE FINAL
//########################################################
function inicializarTablaEvaluacionesFinal() {
    var periodo = $('#filtroCampaniaDesempeno').val() || new Date().getFullYear();
    var urlAjax = '/rrhh/api/fase-final/?id_area=13&campania=' + periodo;
    tablaEvaluacionesFinal = $("#tablaEvaluaciones_final").DataTable({
        dom: "Bfrtip",
        buttons: [
            {
                text: '<i class="fas fa-sync-alt"></i>',
                className: "btn-sm btn-secondary",
                action: function (e, dt, node, config) {
                    // Añadir animación de giro
                    $(node).find("i").addClass("fa-spin");
                    
                    // Recargar datos desde la API
                    cargarDatosFaseFinal();
                    
                    setTimeout(() => {
                        $(node).find("i").removeClass("fa-spin");
                    }, 1000);
                }
            },
            // Botón Exportar a Excel eliminado por requerimiento
            
        ],
        
        // Configuración para Ajax
        ajax: {
            url: urlAjax,
            type: 'GET',
            dataSrc: function(json) {
                console.log("Datos recibidos de la API Fase Final:", json);
                if (json.status === 'success') {
                    return json.data;
                } else {
                    console.error("Error en la respuesta de la API:", json.message);
                    mostrarMensajeFinal('Error al cargar datos: ' + json.message, 'error');
                    return [];
                }
            },
            error: function(xhr, error, thrown) {
                // Ignorar errores por abort o reload
                if (error === 'abort') {
                    return;
                }

                console.error("Error real en la petición AJAX:", error, thrown);
                mostrarMensajeFinal('Error de conexión al cargar datos', 'error');
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
                            <div class="modern-avatar bg-success mr-2">
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
                            <div class="modern-avatar bg-primary mr-2">
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
                data: 'porcentaje_intermedio',
                title: 'Avance Intermedio',
                className: 'text-center',
                render: function(data, type, row) {
                    // Usar el porcentaje_intermedio sin redondear para mantener consistencia con fase intermedia
                    const porcentaje = Math.floor(data || 0);
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
                            <div class="progress-bar ${progressClass}" style="width: ${porcentaje}%">${porcentaje}%</div>
                        </div>
                    `;
                }
            },
            { 
                data: 'porcentaje_general',
                title: 'Avance Final',
                className: 'text-center',
                render: function(data, type, row) {
                    const porcentaje = data || 0;
                    let progressClass = 'bg-secondary';
                    if (porcentaje >= 101) {
                        progressClass = 'bg-purple';
                    } else if (porcentaje >= 75 && porcentaje <= 100) {
                        progressClass = 'bg-gradient-success';
                    } else if (porcentaje >= 50) {
                        progressClass = 'bg-gradient-info';
                    } else if (porcentaje >= 25) {
                        progressClass = 'bg-gradient-warning';
                    } else if (porcentaje > 0) {
                        progressClass = 'bg-gradient-danger';
                    }
                    return `
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar ${progressClass}" style="width: ${porcentaje}%">${porcentaje}%</div>
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
                            <button type="button" class="btn btn-success btn-sm" 
                                    onclick="abrirModalSeguimientoAvanceFinal(${row.id_evaluacion})" 
                                    title="Registrar Avance Final">
                                <i class="fas fa-flag-checkered"></i>
                            </button>
                            <button type="button" class="btn btn-primary btn-sm" 
                                    onclick="EmailManagerRRHH.generarEnviarPDFEvaluacionFinal(${row.id_evaluacion})" 
                                    title="Generar PDF Final y enviar">
                                <i class='bxr bx-envelope-open'></i> 
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
            processing: "Cargando datos de evaluaciones finales...",
            emptyTable: "No hay evaluaciones disponibles",
            zeroRecords: "No se encontraron evaluaciones que coincidan"
        },
        
        rowCallback: function(row, data) {
            // Agregar evento de doble clic a toda la fila
            $(row).attr('ondblclick', `abrirModalSeguimientoAvanceFinal(${data.id_evaluacion})`);
            $(row).css('cursor', 'pointer');
        },
        
        initComplete: function (settings, json) {
            console.log("Tabla de fase final inicializada correctamente");
            console.log("Total de registros cargados:", this.api().data().length);
        },
        
        destroy: true
    });
    
    return tablaEvaluacionesFinal;
}

//########################################################
// FUNCIÓN PARA CARGAR DATOS DESDE LA API
//########################################################
function cargarDatosFaseFinal() {
    console.log("Recargando datos de la API Fase Final...");
    
    if (tablaEvaluacionesFinal) {
        tablaEvaluacionesFinal.ajax.reload(function(json) {
            console.log("Datos recargados:", json);
            mostrarMensajeFinal('Datos actualizados correctamente', 'success');
        }, false);
    }
}

//########################################################
// FUNCIONES PARA MODAL DE AVANCE FINAL
//########################################################

// Variable global para el ID de evaluación actual final
let evaluacionActualFinal = null;

// Función para abrir el modal de avance final
function abrirModalSeguimientoAvanceFinal(id_evaluacion) {
    console.log("Abriendo modal de avance final para evaluación:", id_evaluacion);
    
    // Asignar ID de evaluación ANTES de resetear
    evaluacionActualFinal = id_evaluacion;
    
    // Resetear el modal PERO SIN limpiar la variable evaluacionActualFinal
    resetModalSeguimientoAvanceFinal();
    
    // Cargar datos del evaluado
    cargarDatosSeguimientoAvanceFinal(id_evaluacion);
    
    // Mostrar el modal
    $("#Modal_Seguimiento_Avance_Final").modal("show");
}

//########################################################
// FUNCIÓN PARA RESETEAR EL MODAL DE SEGUIMIENTO DE AVANCE FINAL
//########################################################
function resetModalSeguimientoAvanceFinal() {
    // Resetear información del evaluado
    $("#evaluado_periodo_final").text("- -");
    $("#nombre_final").text("");
    $("#evaluado_cargo_final").text("");
    $("#evaluado_area_final").text("");
    $("#evaluador_nombre_final").text("");
    
    // Resetear avatar con iniciales por defecto
    $(".modern-avatar .initials").text("--");
    
    // Resetear avance general y final
    $("#avance_general_final").css("width", "0%").text("0%");
    $("#avance_final_final").css("width", "0%").text("0%");
    
    // Resetear contadores de pestañas
    $("#count_objetivos_final").text("0");
    $("#count_competencias_final").text("0");
    
    // Limpiar tablas de objetivos y competencias
    $("#tabla_objetivos_avance_final").empty();
    $("#tabla_competencias_avance_final").empty();
    
    // Limpiar comentarios generales
    $("#comentarios_objetivos_general_final").val("");
    
    // Resetear pestañas - activar la primera pestaña
    $("#objetivos-avance-final-tab").addClass("active");
    $("#competencias-avance-final-tab").removeClass("active");
    $("#objetivos-avance-final").addClass("show active");
    $("#competencias-avance-final").removeClass("show active");
    
    console.log("Modal de seguimiento de avance final reseteado");
}

function cargarDatosSeguimientoAvanceFinal(id_evaluacion) {
    
    var campania = $('#filtroCampaniaDesempeno').val() || 'CAMP' + new Date().getFullYear();
    // Extraer solo el año si viene en formato CAMP2026
    var periodo = campania.startsWith('CAMP') ? campania.replace('CAMP', '') : campania;
    
    $.ajax({
        url: `/rrhh/api/fase-final/?id_area=13&campania=${periodo}`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log('Response cargarDatosSeguimientoAvanceFinal /rrhh/api/fase-final/');
            console.log(response);
            console.log(response);
            // Filtrar la lista por el objeto que tenga el id de evaluación actual
            const datosFiltrados = response.data.filter(item => item.id_evaluacion === id_evaluacion);
            
            mostrarInformacionEvaluadoFinal(datosFiltrados);
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar datos de seguimiento de avance final:", error);
            mostrarMensajeFinal('Error de conexión al cargar datos', 'error');
        }
    });
}

function mostrarInformacionEvaluadoFinal(datos) {
    console.log("Datos del evaluado final:", datos);
    if (datos.length > 0) {
        const evaluado = datos[0];
        console.log("Evaluado seleccionado final:", evaluado);
        $("#evaluado_periodo_final").text(evaluado.periodo);
        $("#nombre_final").text(evaluado.nombre_evaluado);
        $("#evaluado_cargo_final").text(evaluado.apellido_evaluado);
        $("#evaluado_area_final").text(evaluado.nombre_area);
        $("#evaluador_nombre_final").text(evaluado.nombre_evaluador);
        
        // Mostrar avatar con iniciales
        const iniciales = evaluado.nombre_evaluado.split(" ").map(n => n.charAt(0)).join("").toUpperCase();
        $(".modern-avatar .initials").text(iniciales);
        
        // Mostrar avance final con color
        $("#avance_general_final")
            .css("width", evaluado.porcentaje_general + "%")
            .text(evaluado.porcentaje_general + "%")
            .removeClass("bg-purple bg-success bg-info bg-warning bg-danger bg-secondary")
            .addClass(
                evaluado.porcentaje_general >= 101 ? "bg-purple" :
                (evaluado.porcentaje_general >= 75 && evaluado.porcentaje_general <= 100) ? "bg-success" :
                evaluado.porcentaje_general >= 50 ? "bg-info" :
                evaluado.porcentaje_general >= 25 ? "bg-warning" :
                evaluado.porcentaje_general > 0 ? "bg-danger" : "bg-secondary"
            );
        
        // Mostrar contadores de pestañas
        $("#count_objetivos_final").text(evaluado.total_objetivos);
        $("#count_competencias_final").text(evaluado.total_competencias);
        
        // Cargar tablas de objetivos y competencias finales
        cargarTablaObjetivosAvanceFinal(evaluado.id_evaluacion);
        cargarTablaCompetenciasAvanceFinal(evaluado.id_evaluacion);
        
        // Cargar comentarios existentes
        cargarComentariosExistentesFinal(evaluado.id_evaluacion);
    } else {
        console.warn("No se encontraron datos para el evaluado final.");
    }
}

//########################################################
// FUNCIÓN PARA CARGAR COMENTARIOS EXISTENTES FINAL
//########################################################
function cargarComentariosExistentesFinal(id_evaluacion) {
    console.log("Cargando comentarios existentes finales para evaluación:", id_evaluacion);
    
    $.ajax({
        url: `/rrhh/api/detalles-evaluacion-final/?id_evaluacion=${id_evaluacion}&cargar_comentarios=true`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Comentarios finales recibidos:", response);
            
            if (response.status === 'success' && response.comentarios) {
                // Cargar comentarios de objetivos finales
                if (response.comentarios.comentarios_objetivos_general_final) {
                    $("#comentarios_objetivos_general_final").val(response.comentarios.comentarios_objetivos_general_final);
                }
                

                
                console.log("Comentarios finales cargados exitosamente");
            } else {
                console.log("No se encontraron comentarios finales existentes");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar comentarios finales existentes:", error);
            // No mostrar error al usuario, ya que es funcionalidad secundaria
        }
    });
}

function cargarTablaObjetivosAvanceFinal(id_evaluacion) {
    console.log("Cargando tabla de objetivos finales para evaluación:", id_evaluacion);
    
    $.ajax({
        url: `/rrhh/api/detalles-evaluacion-final/?id_evaluacion=${id_evaluacion}&tipo=1`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Datos de objetivos finales recibidos:", response);
            
            if (response.status === 'success' && response.data && response.data.length > 0) {
                // Limpiar la tabla antes de cargar nuevos datos
                $("#tabla_objetivos_avance_final").empty();
                
                // Generar las filas de la tabla
                let filas = '';
                
                response.data.forEach(function(objetivo, index) {
                    // Obtener valores para el cálculo
                    const avanceIntermedio = objetivo.porcentaje_actual || 0;
                    const porc_etapa_final = objetivo.porc_etapa_final || 0;
                    // Calcular el nuevo avance final que ingresó el usuario
                    const nuevoAvanceFinal = Math.max(0, porc_etapa_final - avanceIntermedio);
                    // El avance actual es el porc_etapa_final (la suma guardada)
                    const avanceActual = porc_etapa_final;
                    // Calcular el máximo permitido para el input
                    const maxAvanceFinal = Math.max(0, 130 - (objetivo.porcentaje_actual || 0));
                    
                    // Determinar el color de la barra de progreso según el avance actual
                    let progressClass = 'bg-secondary';
                    if (avanceActual >= 101) {
                        progressClass = 'bg-purple'; // sobresaliente morado
                    } else if (avanceActual >= 75 && avanceActual <= 100) {
                        progressClass = 'bg-success';
                    } else if (avanceActual >= 50) {
                        progressClass = 'bg-info';
                    } else if (avanceActual >= 25) {
                        progressClass = 'bg-warning';
                    } else if (avanceActual > 0) {
                        progressClass = 'bg-danger';
                    }
                    
                    // Formatear las fechas
                    const fechaInicio = objetivo.fecha_inicio_formato || objetivo.fecha_inicio || 'N/A';
                    const fechaFin = objetivo.fecha_fin_formato || objetivo.fecha_fin || 'N/A';
                    
                    filas += `
                        <tr data-objetivo-final-id="${objetivo.id || index + 1}">
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
                                <textarea class="form-control form-control-sm" rows="2" id="comentarios_objetivos_final_${objetivo.id || index + 1}" placeholder="Comentarios finales">${objetivo.coment_objetivo_ff || objetivo.comentarios || ''}</textarea>
                            </td>
                            <td>
                                <div class="progress" style="height: 15px;">
                                    <div class="progress-bar bg-info" style="width: ${objetivo.porcentaje_actual || 0}%">
                                        ${objetivo.porcentaje_actual || 0}%
                                    </div>
                                </div>
                            </td>
                            <td>
                        <input type="number" class="form-control form-control-sm avance-input-final" 
                            value="${nuevoAvanceFinal > 0 ? nuevoAvanceFinal : ''}" min="0" max="${maxAvanceFinal}" placeholder="0"
                            data-objetivo-final-id="${objetivo.id || index + 1}">
                            </td>
                            <td>
                                <div class="progress" style="height: 20px;">
                                    <div class="progress-bar ${progressClass}" style="width: ${avanceActual}%">
                                        ${avanceActual}%
                                    </div>
                                </div>
                            </td>
                        </tr>
                    `;
                });
                
                // Insertar las filas en la tabla
                $("#tabla_objetivos_avance_final").html(filas);
                
                // Actualizar el contador en la pestaña
                $("#count_objetivos_final").text(response.data.length);
                
                console.log(`Se cargaron ${response.data.length} objetivos finales en la tabla`);
                
            } else {
                // Si no hay datos, mostrar mensaje
                $("#tabla_objetivos_avance_final").html(`
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">
                            <i class="fas fa-info-circle mr-2"></i>
                            No se encontraron objetivos para esta evaluación
                        </td>
                    </tr>
                `);
                
                $("#count_objetivos_final").text("0");
                console.log("No se encontraron objetivos finales para la evaluación");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar datos de objetivos finales:", error);
            
            // Mostrar mensaje de error en la tabla
            $("#tabla_objetivos_avance_final").html(`
                <tr>
                    <td colspan="8" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Error al cargar los objetivos. Por favor, inténtelo de nuevo.
                    </td>
                </tr>
            `);
            
            $("#count_objetivos_final").text("0");
            mostrarMensajeFinal('Error al cargar objetivos finales: ' + error, 'error');
        }
    });
}

function cargarTablaCompetenciasAvanceFinal(id_evaluacion) {
    console.log("Cargando tabla de competencias finales para evaluación:", id_evaluacion);
    
    $.ajax({
        url: `/rrhh/api/detalles-evaluacion-final/?id_evaluacion=${id_evaluacion}&tipo=2`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Datos de competencias finales recibidos:", response);
            
            if (response.status === 'success' && response.data && response.data.length > 0) {
                // Limpiar la tabla antes de cargar nuevos datos
                $("#tabla_competencias_avance_final").empty();
                
                // Generar las filas de la tabla
                let filas = '';
                
                response.data.forEach(function(competencia, index) {
                    // Obtener valores para el cálculo
                    const avanceIntermedio = competencia.porcentaje_actual || 0;
                    const porc_etapa_final = competencia.porc_etapa_final || 0;
                    // Calcular el nuevo avance final que ingresó el usuario
                    const nuevoAvanceFinal = Math.max(0, porc_etapa_final - avanceIntermedio);
                    // El avance actual es el porc_etapa_final (la suma guardada)
                    const avanceActual = porc_etapa_final;
                    // Calcular el máximo permitido para el input
                    const maxAvanceFinal = Math.max(0, 130 - (competencia.porcentaje_actual || 0));
                    
                    // Determinar el color de la barra de progreso según el avance actual
                    let progressClass = 'bg-secondary';
                    if (avanceActual >= 101) {
                        progressClass = 'bg-purple'; // sobresaliente morado
                    } else if (avanceActual >= 75) {
                        progressClass = 'bg-success';
                    } else if (avanceActual >= 50) {
                        progressClass = 'bg-info';
                    } else if (avanceActual >= 25) {
                        progressClass = 'bg-warning';
                    } else if (avanceActual > 0) {
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
                        <tr data-competencia-final-id="${competencia.id || index + 1}">
                            <td>
                                <strong>${competencia.nombre_competencia || 'Competencia sin nombre'}</strong>
                                <br><small class="text-muted">${competencia.descripcion_competencia || 'Sin descripción'}</small>
                            </td>
                            <td>
                                <span class="badge ${badgeClass}">${competencia.tipo_competencia || 'General'}</span>
                            </td>
                            <td>${competencia.meta || 'Sin meta definida'}</td>
                            <td>
                                <textarea class="form-control form-control-sm" rows="2" id="comentarios_competencias_final_${competencia.id || index + 1}" placeholder="Comentarios finales">${competencia.coment_competencia_ff || ''}</textarea>
                            </td>
                            <td>
                                <div class="progress" style="height: 15px;">
                                    <div class="progress-bar bg-info" style="width: ${competencia.porcentaje_actual || 0}%">
                                        ${competencia.porcentaje_actual || 0}%
                                    </div>
                                </div>
                            </td>
                            <td>
                        <input type="number" class="form-control form-control-sm avance-input-final" 
                            value="${nuevoAvanceFinal > 0 ? nuevoAvanceFinal : ''}" min="0" max="${maxAvanceFinal}" placeholder="0"
                            data-competencia-final-id="${competencia.id || index + 1}">
                            </td>
                            <td>
                                <div class="progress" style="height: 20px;">
                                    <div class="progress-bar ${progressClass}" style="width: ${avanceActual}%">
                                        ${avanceActual}%
                                    </div>
                                </div>
                            </td>
                        </tr>
                    `;
                });
                
                // Insertar las filas en la tabla
                $("#tabla_competencias_avance_final").html(filas);
                
                // Actualizar el contador en la pestaña
                $("#count_competencias_final").text(response.data.length);
                
                console.log(`Se cargaron ${response.data.length} competencias finales en la tabla`);
                
            } else {
                // Si no hay datos, mostrar mensaje
                $("#tabla_competencias_avance_final").html(`
                    <tr>
                        <td colspan="7" class="text-center text-muted py-4">
                            <i class="fas fa-info-circle mr-2"></i>
                            No se encontraron competencias para esta evaluación
                        </td>
                    </tr>
                `);
                
                $("#count_competencias_final").text("0");
                console.log("No se encontraron competencias finales para la evaluación");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar datos de competencias finales:", error);
            
            // Mostrar mensaje de error en la tabla
            $("#tabla_competencias_avance_final").html(`
                <tr>
                    <td colspan="7" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Error al cargar las competencias. Por favor, inténtelo de nuevo.
                    </td>
                </tr>
            `);
            
            $("#count_competencias_final").text("0");
            mostrarMensajeFinal('Error al cargar competencias finales: ' + error, 'error');
        }
    });
}

//########################################################
// FUNCIONES PARA ACTUALIZAR OBJETIVOS Y COMPETENCIAS FINALES
//########################################################

/**
 * Función para guardar avances finales de objetivos
 */
function guardarAvanceObjetivosFinal() {
    console.log("Iniciando guardado de avance final de objetivos...");
    console.log("Evaluación actual (objetivos final):", evaluacionActualFinal);
    
    // Recopilar todos los inputs de objetivos modificados
    const actualizaciones = [];
    
    $("#tabla_objetivos_avance_final input.avance-input-final").each(function() {
        const input = $(this);
        const objetivoId = input.data('objetivo-final-id');
        const nuevoAvanceFinal = parseFloat(input.val()) || 0;
        
        // Obtener el avance intermedio de la misma fila
        const fila = input.closest('tr');
        const avanceIntermedioElement = fila.find('td').eq(5).find('.progress-bar');
        let avanceIntermedio = 0;
        if (avanceIntermedioElement.length > 0) {
            const texto = avanceIntermedioElement.text().replace('%', '');
            avanceIntermedio = parseFloat(texto) || 0;
        }
        
        // Calcular el porcentaje final real (Avance Intermedio + Nuevo Avance Final)
        const porcentajeFinal = Math.min(avanceIntermedio + nuevoAvanceFinal, 130);

        // Añadir el campo de comentarios finales
        const comentariosFinal = $(`#comentarios_objetivos_final_${objetivoId}`).val() || '';
        console.log("Comentarios finales del objetivo ID " + objetivoId + ":", comentariosFinal);
        console.log(`Calculando: ${avanceIntermedio}% + ${nuevoAvanceFinal}% = ${porcentajeFinal}%`);
        
        // Validar que el nuevo avance esté en el rango válido
        if (nuevoAvanceFinal < 0 || nuevoAvanceFinal > 130) {
            mostrarMensajeFinal(`El nuevo avance del objetivo ID ${objetivoId} debe estar entre 0 y 130`, 'warning');
            return;
        }

        actualizaciones.push({
            id: objetivoId,
            porc_etapa_final: porcentajeFinal,
            coment_objetivo_ff: comentariosFinal
        });
    });
    
    if (actualizaciones.length === 0) {
        mostrarMensajeFinal('No hay objetivos para actualizar', 'info');
        return;
    }
    
    // Verificar que tenemos el ID de evaluación
    if (!evaluacionActualFinal) {
        console.error("ERROR: evaluacionActualFinal es null al guardar objetivos");
        mostrarMensajeFinal('Error: No se pudo identificar la evaluación', 'error');
        return;
    }
    
    // Obtener comentarios generales finales para objetivos
    const comentariosObjetivosFinal = $("#comentarios_objetivos_general_final").val() || '';
    
    // Enviar actualizaciones al servidor incluyendo comentarios
    actualizarAvancesFinalEnServidor(1, actualizaciones, 'objetivos', null, {
        comentarios_objetivos_general_final: comentariosObjetivosFinal,
        id_evaluacion: evaluacionActualFinal
    });
}

/**
 * Función para guardar avances finales de competencias
 */
function guardarAvanceCompetenciasFinal() {
    console.log("Iniciando guardado de avance final de competencias...");
    console.log("Evaluación actual (competencias final):", evaluacionActualFinal);
    
    // Recopilar todos los inputs de competencias modificados
    const actualizaciones = [];
    
    $("#tabla_competencias_avance_final input.avance-input-final").each(function() {
        const input = $(this);
        const competenciaId = input.data('competencia-final-id');
        const nuevoAvanceFinal = parseFloat(input.val()) || 0;
        
        // Obtener el avance intermedio de la misma fila
        const fila = input.closest('tr');
        const avanceIntermedioElement = fila.find('td').eq(4).find('.progress-bar');
        let avanceIntermedio = 0;
        if (avanceIntermedioElement.length > 0) {
            const texto = avanceIntermedioElement.text().replace('%', '');
            avanceIntermedio = parseFloat(texto) || 0;
        }
        
        // Calcular el porcentaje final real (Avance Intermedio + Nuevo Avance Final)
        const porcentajeFinal = Math.min(avanceIntermedio + nuevoAvanceFinal, 130);
        
        // Añadir el campo de comentarios finales
        const comentariosFinalComp = $(`#comentarios_competencias_final_${competenciaId}`).val() || '';
        console.log("Comentarios finales de la competencia ID " + competenciaId + ":", comentariosFinalComp);
        console.log(`Calculando: ${avanceIntermedio}% + ${nuevoAvanceFinal}% = ${porcentajeFinal}%`);

        // Validar que el nuevo avance esté en el rango válido
        if (nuevoAvanceFinal < 0 || nuevoAvanceFinal > 130) {
            mostrarMensajeFinal(`El nuevo avance de la competencia ID ${competenciaId} debe estar entre 0 y 130`, 'warning');
            return;
        }

        actualizaciones.push({
            id: competenciaId,
            porc_etapa_final: porcentajeFinal,
            coment_competencia_ff: comentariosFinalComp
        });
    });
    
    if (actualizaciones.length === 0) {
        mostrarMensajeFinal('No hay competencias para actualizar', 'info');
        return;
    }
    
    // Verificar que tenemos el ID de evaluación
    if (!evaluacionActualFinal) {
        console.error("ERROR: evaluacionActualFinal es null al guardar competencias");
        mostrarMensajeFinal('Error: No se pudo identificar la evaluación', 'error');
        return;
    }
    
    // Enviar actualizaciones al servidor
    actualizarAvancesFinalEnServidor(2, actualizaciones, 'competencias', null, {
        id_evaluacion: evaluacionActualFinal
    });
}



/**
 * Función genérica para enviar actualizaciones finales al servidor
 */
function actualizarAvancesFinalEnServidor(tipo, actualizaciones, tipoNombre, callback, comentarios = {}) {
    console.log(`Enviando ${actualizaciones.length} actualizaciones finales de ${tipoNombre} al servidor...`);
    
    // Mostrar indicador de carga
    const btnGuardar = tipo === 1 ? 
        $('button[onclick="guardarAvanceObjetivosFinal()"]') : 
        $('button[onclick="guardarAvanceCompetenciasFinal()"]');
    
    const textoOriginal = btnGuardar.html();
    btnGuardar.prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-1"></i>Guardando...');
    
    // Preparar datos para enviar incluyendo comentarios
    const dataToSend = {
        tipo: tipo,
        actualizaciones: actualizaciones,
        ...comentarios  // Spread operator para incluir comentarios e id_evaluacion
    };
    
    console.log("Datos finales a enviar:", dataToSend);
    
    $.ajax({
        url: '/rrhh/api/detalles-evaluacion-final/',
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(dataToSend),
        success: function(response) {
            console.log(`Respuesta del servidor para ${tipoNombre} finales:`, response);
            
            if (response.status === 'success') {
                let mensaje = `${tipoNombre.charAt(0).toUpperCase() + tipoNombre.slice(1)} finales actualizados exitosamente`;
                if (response.data.comentarios_actualizados) {
                    mensaje += ' y comentarios finales guardados';
                }
                mostrarMensajeFinal(mensaje, 'success');
                
                // Actualizar las barras de progreso en la tabla
                actualizarBarrasProgresoFinal(tipo, actualizaciones);
                
                if (callback) callback(true);
                
            } else if (response.status === 'partial_success') {
                const exitosas = response.data.exitosas;
                const fallidas = response.data.fallidas;
                let mensaje = `${tipoNombre} finales: ${exitosas} actualizados, ${fallidas} con errores`;
                if (response.data.comentarios_actualizados) {
                    mensaje += ' y comentarios finales guardados';
                }
                mostrarMensajeFinal(mensaje, 'warning');
                
                if (callback) callback(true);
                
            } else {
                mostrarMensajeFinal(`Error al actualizar ${tipoNombre} finales: ${response.message}`, 'error');
                if (callback) callback(false);
            }
        },
        error: function(xhr, status, error) {
            console.error(`Error al actualizar ${tipoNombre} finales:`, error);
            let mensaje = `Error de conexión al actualizar ${tipoNombre} finales`;
            
            if (xhr.responseJSON && xhr.responseJSON.message) {
                mensaje = `Error al actualizar ${tipoNombre} finales: ${xhr.responseJSON.message}`;
            }
            
            mostrarMensajeFinal(mensaje, 'error');
            if (callback) callback(false);
        },
        complete: function() {
            // Restaurar el botón
            btnGuardar.prop('disabled', false).html(textoOriginal);
        }
    });
}

/**
 * Función para actualizar las barras de progreso finales en la tabla después de guardar
 */
function actualizarBarrasProgresoFinal(tipo, actualizaciones) {
    const tablaSelector = tipo === 1 ? "#tabla_objetivos_avance_final" : "#tabla_competencias_avance_final";
    
    actualizaciones.forEach(function(item) {
        const fila = $(`${tablaSelector} tr[data-${tipo === 1 ? 'objetivo-final' : 'competencia-final'}-id="${item.id}"]`);
        
        if (fila.length > 0) {
            // Actualizar la barra de progreso final
            const progressBar = fila.find('.progress-bar').eq(1); // Segunda barra (final)
            const nuevoAncho = item.porc_etapa_final + '%';
            
            progressBar.css('width', nuevoAncho).text(nuevoAncho);
            
            // Actualizar color de la barra según el porcentaje final
            progressBar.removeClass('bg-secondary bg-danger bg-warning bg-info bg-success');
            if (item.porc_etapa_final >= 75) {
                progressBar.addClass('bg-success');
            } else if (item.porc_etapa_final >= 50) {
                progressBar.addClass('bg-info');
            } else if (item.porc_etapa_final >= 25) {
                progressBar.addClass('bg-warning');
            } else if (item.porc_etapa_final > 0) {
                progressBar.addClass('bg-danger');
            } else {
                progressBar.addClass('bg-secondary');
            }
        }
    });
}

//########################################################
// FUNCIONES DE UTILIDAD PARA EVENTOS FINALES
//########################################################

/**
 * Inicializar eventos de los inputs de avance final
 */
function initializarEventosAvanceFinal() {
    // Agregar eventos a los inputs cuando se cargan dinámicamente
    $(document).on('input', '.avance-input-final', function() {
        const input = $(this);
        let valor = parseFloat(input.val()) || 0;
        // Obtener el máximo permitido dinámicamente
        let max = parseFloat(input.attr('max'));
        if (isNaN(max)) max = 130;
        // Validar rango
        if (valor < 0) {
            valor = 0;
            input.val(0);
        } else if (valor > max) {
            valor = max;
            input.val(max);
        }
        // Calcular y actualizar el Avance Actual (Avance Intermedio + Nuevo Avance Final)
        const fila = input.closest('tr');
        calcularAvanceActual(fila, valor);
        // Agregar clase visual para indicar cambio
        input.addClass('changed');
    });
    
    // Evento para tecla Enter en inputs
    $(document).on('keypress', '.avance-input-final', function(e) {
        if (e.which === 13) { // Enter
            $(this).blur(); // Quitar foco del input
        }
    });
}

/**
 * Calcular y actualizar el Avance Actual (Avance Intermedio + Nuevo Avance Final)
 * @param {jQuery} fila - La fila de la tabla
 * @param {number} nuevoAvance - El nuevo avance final ingresado
 */
function calcularAvanceActual(fila, nuevoAvance) {
    try {
        // Buscar la barra de progreso del Avance Intermedio (columna 6 en objetivos, columna 5 en competencias)
        let avanceIntermedioElement = fila.find('td').eq(5).find('.progress-bar');
        
        // Si no encuentra en la posición 5, buscar en la posición 4 (para competencias)
        if (avanceIntermedioElement.length === 0) {
            avanceIntermedioElement = fila.find('td').eq(4).find('.progress-bar');
        }
        
        // Obtener el porcentaje del avance intermedio
        let avanceIntermedio = 0;
        if (avanceIntermedioElement.length > 0) {
            const texto = avanceIntermedioElement.text().replace('%', '');
            avanceIntermedio = parseFloat(texto) || 0;
        }
        
        // Calcular el avance actual (suma)
        const avanceActual = avanceIntermedio + nuevoAvance;
        // Limitar el avance actual a máximo 130%
        const avanceActualLimitado = Math.min(avanceActual, 130);
        
        // Buscar la barra de progreso del Avance Actual (última columna)
        const avanceActualElement = fila.find('td').last().find('.progress-bar');
        
        if (avanceActualElement.length > 0) {
            // Actualizar el ancho y texto de la barra de progreso
            avanceActualElement.css('width', avanceActualLimitado + '%');
            avanceActualElement.text(avanceActualLimitado + '%');
            
            // Actualizar el color según el porcentaje
            let progressClass = 'bg-secondary';
            if (avanceActualLimitado >= 101) {
                progressClass = 'bg-purple';
            } else if (avanceActualLimitado >= 75 && avanceActualLimitado <= 100) {
                progressClass = 'bg-success';
            } else if (avanceActualLimitado >= 50) {
                progressClass = 'bg-info';
            } else if (avanceActualLimitado >= 25) {
                progressClass = 'bg-warning';
            } else if (avanceActualLimitado > 0) {
                progressClass = 'bg-danger';
            }
            
            // Remover clases anteriores y agregar la nueva
            avanceActualElement.removeClass('bg-purple bg-success bg-info bg-warning bg-danger bg-secondary');
            avanceActualElement.addClass(progressClass);
        }
        
        console.log(`Avance calculado: ${avanceIntermedio}% + ${nuevoAvance}% = ${avanceActualLimitado}%`);
        
    } catch (error) {
        console.error('Error al calcular avance actual:', error);
    }
}

//########################################################
// FUNCIÓN PARA MOSTRAR MENSAJES AL USUARIO FINAL
//########################################################

/**
 * Función para mostrar mensajes al usuario usando SweetAlert2 o alert básico
 * @param {string} mensaje - El mensaje a mostrar
 * @param {string} tipo - Tipo de mensaje: 'success', 'error', 'warning', 'info'
 */
function mostrarMensajeFinal(mensaje, tipo = 'info') {
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
