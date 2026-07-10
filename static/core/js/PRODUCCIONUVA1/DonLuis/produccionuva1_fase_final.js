// Funciones para la Fase Final de Evaluaciones
$(document).ready(function () {
  console.log("Inicializando Fase Final...");
  inicializarTablaEvaluacionesFinal();

  // Inicializar eventos de los inputs de avance final
  initializarEventosAvanceFinal();

  // Manejar evento del modal para evitar advertencias de aria-hidden
  $("#Modal_Seguimiento_Avance_Final").on("hide.bs.modal", function () {
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
            url: "/rrhh/api/fase-final/",
            type: "GET",
            data: function (d) {
                d.id_area = 13;
                d.campania = $('#filtroCampaniaDesempeno').val() 
                            || 'CAMP' + new Date().getFullYear();
            },
            dataSrc: function (json) {
                console.log("Datos recibidos de la API Fase Final:", json);

                if (json.status === "success") {
                    return json.data;
                } else {
                    mostrarMensajeFinal(
                        "Error al cargar datos: " + json.message,
                        "error"
                    );
                    return [];
                }
            },
            error: function () {
                mostrarMensajeFinal(
                    "Error de conexión al cargar datos",
                    "error"
                );
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
                                <div class="user-role">${
                                  row.email_evaluado || "Evaluado"
                                }</div>
                            </div>
                        </div>
                    `;
        },
      },
      {
        data: null,
        title: "Evaluador",
        render: function (data, type, row) {
          const nombreCompleto = `${row.nombre_evaluador || ""} ${
            row.apellido_evaluador || ""
          }`.trim();
          const iniciales = nombreCompleto
            .split(" ")
            .map((n) => n.charAt(0))
            .join("")
            .substring(0, 2)
            .toUpperCase();

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
        },
      },
      {
        data: "periodo",
        title: "Período",
      },
      {
        data: "nombre_area",
        title: "Área",
      },
      {
        data: null,
        title: "Objetivos",
        render: function (data, type, row) {
          const totalObjetivos = row.total_objetivos || 0;
          const porcentaje = row.porcentaje_objetivos || 0;

          let badgeClass = "badge-secondary";
          let progressClass = "bg-secondary";

          if (porcentaje >= 75) {
            badgeClass = "badge-success";
            progressClass = "bg-success";
          } else if (porcentaje >= 50) {
            badgeClass = "badge-info";
            progressClass = "bg-info";
          } else if (porcentaje >= 25) {
            badgeClass = "badge-warning";
            progressClass = "bg-warning";
          } else if (porcentaje > 0) {
            badgeClass = "badge-danger";
            progressClass = "bg-danger";
          }

          return `
                        <span class="badge ${badgeClass}">${totalObjetivos} Objetivos</span>
                        <div class="progress mt-1" style="height: 5px;">
                            <div class="progress-bar ${progressClass}" style="width: ${porcentaje}%"></div>
                        </div>
                        <small class="text-muted">${porcentaje}% completado</small>
                    `;
        },
      },
      {
        data: null,
        title: "Competencias",
        render: function (data, type, row) {
          const totalCompetencias = row.total_competencias || 0;
          const porcentaje = row.porcentaje_competencias || 0;

          let badgeClass = "badge-secondary";
          let progressClass = "bg-secondary";

          if (porcentaje >= 75) {
            badgeClass = "badge-success";
            progressClass = "bg-success";
          } else if (porcentaje >= 50) {
            badgeClass = "badge-info";
            progressClass = "bg-info";
          } else if (porcentaje >= 25) {
            badgeClass = "badge-warning";
            progressClass = "bg-warning";
          } else if (porcentaje > 0) {
            badgeClass = "badge-danger";
            progressClass = "bg-danger";
          }

          return `
                        <span class="badge ${badgeClass}">${totalCompetencias} Competencias</span>
                        <div class="progress mt-1" style="height: 5px;">
                            <div class="progress-bar ${progressClass}" style="width: ${porcentaje}%"></div>
                        </div>
                        <small class="text-muted">${porcentaje}% completado</small>
                    `;
        },
      },
      {
        data: "porcentaje_intermedio",
        title: "Avance Intermedio",
        className: "text-center",
        render: function (data, type, row) {
          // Usar el porcentaje_intermedio sin redondear para mantener consistencia con fase intermedia
          const porcentaje = Math.floor(data || 0);
          let progressClass = "bg-secondary";

          if (porcentaje >= 75) {
            progressClass = "bg-gradient-success";
          } else if (porcentaje >= 50) {
            progressClass = "bg-gradient-primary";
          } else if (porcentaje >= 25) {
            progressClass = "bg-gradient-warning";
          } else if (porcentaje > 0) {
            progressClass = "bg-gradient-danger";
          }

          return `
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated ${progressClass}" style="width: ${porcentaje}%">${porcentaje}%</div>
                        </div>
                    `;
        },
      },
      {
        data: "porcentaje_general",
        title: "Avance Final",
        className: "text-center",
        render: function (data, type, row) {
          const porcentaje = data || 0;
          let progressClass = "bg-secondary";
          if (porcentaje >= 101) {
            progressClass = "bg-purple";
          } else if (porcentaje >= 75 && porcentaje <= 100) {
            progressClass = "bg-gradient-success";
          } else if (porcentaje >= 50) {
            progressClass = "bg-gradient-info";
          } else if (porcentaje >= 25) {
            progressClass = "bg-gradient-warning";
          } else if (porcentaje > 0) {
            progressClass = "bg-gradient-danger";
          }
          return `
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated ${progressClass}" style="width: ${porcentaje}%">${porcentaje}%</div>
                        </div>
                    `;
        },
      },
      {
        data: "estado_avance",
        title: "Estado",
        render: function (data, type, row) {
          let badgeClass = "badge-secondary";

          switch (data) {
            case "Completado":
              badgeClass = "badge-success";
              break;
            case "En Progreso":
              badgeClass = "badge-warning";
              break;
            case "Pendiente":
              badgeClass = "badge-info";
              break;
            case "Sin Datos":
              badgeClass = "badge-secondary";
              break;
          }

          return `<span class="badge ${badgeClass}">${
            data || "Sin Estado"
          }</span>`;
        },
      },
      {
        data: null,
        title: "Acciones",
        orderable: false,
        className: "text-center",

        render: function (data, type, row) {
          return `
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-success btn-sm" 
                                    onclick="abrirModalSeguimientoAvanceFinal(${row.id_evaluacion})" 
                                    title="Registrar Avance Final">
                                <i class="fas fa-flag-checkered"></i>
                            </button>
                            <button type="button" class="btn btn-primary btn-sm" 
                                    onclick="EmailManagerFinal.generarEnviarPDFEvaluacionFinal(${row.id_evaluacion})" 
                                    title="Generar PDF Final y enviar">
                                <i class='bxr bx-envelope-open'></i> 
                            </button>
                        </div>
                    `;
        },
      },
    ],

    scrollX: true,
    scrollCollapse: false,
    pageLength: 10,
    responsive: true,
    processing: true,

    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json",
      processing: "Cargando datos de evaluaciones finales...",
      emptyTable: "No hay evaluaciones disponibles",
      zeroRecords: "No se encontraron evaluaciones que coincidan",
    },

    rowCallback: function (row, data) {
      // Agregar evento de doble clic a toda la fila
      $(row).attr(
        "ondblclick",
        `abrirModalSeguimientoAvanceFinal(${data.id_evaluacion})`
      );
      $(row).css("cursor", "pointer");
    },

    initComplete: function (settings, json) {
      console.log("Tabla de fase final inicializada correctamente");
      console.log("Total de registros cargados:", this.api().data().length);
    },

    destroy: true,
  });

  return tablaEvaluacionesFinal;
}

//########################################################
// FUNCIÓN PARA CARGAR DATOS DESDE LA API
//########################################################
function cargarDatosFaseFinal() {
  console.log("Recargando datos de la API Fase Final...");

  if (tablaEvaluacionesFinal) {
    tablaEvaluacionesFinal.ajax.reload(function (json) {
      console.log("Datos recargados:", json);
      mostrarMensajeFinal("Datos actualizados correctamente", "success");
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
    
    $.ajax({
        url: `/rrhh/api/fase-final/?id_area=13&campania=${campania}`,
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
    const iniciales = evaluado.nombre_evaluado
      .split(" ")
      .map((n) => n.charAt(0))
      .join("")
      .toUpperCase();
    $(".modern-avatar .initials").text(iniciales);

    // Mostrar avance final con color
    $("#avance_general_final")
      .css("width", evaluado.porcentaje_general + "%")
      .text(evaluado.porcentaje_general + "%")
      .removeClass(
        "bg-purple bg-success bg-info bg-warning bg-danger bg-secondary"
      )
      .addClass(
        evaluado.porcentaje_general >= 101
          ? "bg-purple"
          : evaluado.porcentaje_general >= 75 &&
            evaluado.porcentaje_general <= 100
          ? "bg-success"
          : evaluado.porcentaje_general >= 50
          ? "bg-info"
          : evaluado.porcentaje_general >= 25
          ? "bg-warning"
          : evaluado.porcentaje_general > 0
          ? "bg-danger"
          : "bg-secondary"
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
  console.log(
    "Cargando comentarios existentes finales para evaluación:",
    id_evaluacion
  );

  $.ajax({
    url: `/rrhh/api/detalles-evaluacion-final/?id_evaluacion=${id_evaluacion}&cargar_comentarios=true`,
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log("Comentarios finales recibidos:", response);

      if (response.status === "success" && response.comentarios) {
        // Cargar comentarios de objetivos finales
        if (response.comentarios.comentarios_objetivos_general_final) {
          $("#comentarios_objetivos_general_final").val(
            response.comentarios.comentarios_objetivos_general_final
          );
        }

        console.log("Comentarios finales cargados exitosamente");
      } else {
        console.log("No se encontraron comentarios finales existentes");
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al cargar comentarios finales existentes:", error);
      // No mostrar error al usuario, ya que es funcionalidad secundaria
    },
  });
}

function cargarTablaObjetivosAvanceFinal(id_evaluacion) {
  console.log(
    "Cargando tabla de objetivos finales para evaluación:",
    id_evaluacion
  );

  $.ajax({
    url: `/rrhh/api/detalles-evaluacion-final/?id_evaluacion=${id_evaluacion}&tipo=1`,
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log("Datos de objetivos finales recibidos:", response);

      if (
        response.status === "success" &&
        response.data &&
        response.data.length > 0
      ) {
        // Limpiar la tabla antes de cargar nuevos datos
        $("#tabla_objetivos_avance_final").empty();

        // Generar las filas de la tabla
        let filas = "";

        response.data.forEach(function (objetivo, index) {
          // Obtener valores para el cálculo
          const avanceIntermedio = objetivo.porcentaje_actual || 0;
          const porc_etapa_final = objetivo.porc_etapa_final || 0;
          // Calcular el nuevo avance final que ingresó el usuario
          const nuevoAvanceFinal = Math.max(
            0,
            porc_etapa_final - avanceIntermedio
          );
          // El avance actual es el porc_etapa_final (la suma guardada)
          const avanceActual = porc_etapa_final;
          // Calcular el máximo permitido para el input
          const maxAvanceFinal = Math.max(
            0,
            130 - (objetivo.porcentaje_actual || 0)
          );

          // Determinar el color de la barra de progreso según el avance actual
          let progressClass = "bg-secondary";
          if (avanceActual >= 101) {
            progressClass = "bg-purple"; // sobresaliente morado
          } else if (avanceActual >= 75 && avanceActual <= 100) {
            progressClass = "bg-success";
          } else if (avanceActual >= 50) {
            progressClass = "bg-info";
          } else if (avanceActual >= 25) {
            progressClass = "bg-warning";
          } else if (avanceActual > 0) {
            progressClass = "bg-danger";
          }

          // Formatear las fechas
          const fechaInicio =
            objetivo.fecha_inicio_formato || objetivo.fecha_inicio || "N/A";
          const fechaFin =
            objetivo.fecha_fin_formato || objetivo.fecha_fin || "N/A";

          filas += `
                        <tr data-objetivo-final-id="${
                          objetivo.id || index + 1
                        }">
                            <td>
                                <strong>${
                                  objetivo.nombre_objetivo ||
                                  objetivo.descripcion ||
                                  "Objetivo sin nombre"
                                }</strong>
                                <br><small class="text-muted">${
                                  objetivo.descripcion ||
                                  objetivo.detalle ||
                                  "Sin descripción"
                                }</small>
                            </td>
                            <td>
                                <small class="text-muted">Inicio:</small> ${fechaInicio}
                                <br><small class="text-muted">Fin:</small> ${fechaFin}
                            </td>
                            <td>
                                <span class="badge badge-secondary">${
                                  objetivo.indicador || "Sin indicador"
                                }</span>
                            </td>
                            <td>${objetivo.meta || "Sin meta definida"}</td>
                            <td>
                                <textarea class="form-control form-control-sm" rows="2" id="comentarios_objetivos_final_${
                                  objetivo.id || index + 1
                                }" placeholder="Comentarios finales">${
            objetivo.coment_objetivo_ff || objetivo.comentarios || ""
          }</textarea>
                            </td>
                            <td>
                                <div class="progress" style="height: 15px;">
                                    <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated" style="width: ${
                                      objetivo.porcentaje_actual || 0
                                    }%">
                                        ${objetivo.porcentaje_actual || 0}%
                                    </div>
                                </div>
                            </td>
                            <td>
                        <input type="number" class="form-control form-control-sm avance-input-final" 
                            value="${
                              nuevoAvanceFinal > 0 ? nuevoAvanceFinal : ""
                            }" min="0" max="${maxAvanceFinal}" placeholder="0"
                            data-objetivo-final-id="${
                              objetivo.id || index + 1
                            }">
                            </td>
                            <td>
                                <div class="progress" style="height: 20px;">
                                    <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated ${progressClass}" style="width: ${avanceActual}%">
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

        console.log(
          `Se cargaron ${response.data.length} objetivos finales en la tabla`
        );
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
    error: function (xhr, status, error) {
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
      mostrarMensajeFinal(
        "Error al cargar objetivos finales: " + error,
        "error"
      );
    },
  });
}

function cargarTablaCompetenciasAvanceFinal(id_evaluacion) {
  console.log(
    "Cargando tabla de competencias finales para evaluación:",
    id_evaluacion
  );

  $.ajax({
    url: `/rrhh/api/detalles-evaluacion-final/?id_evaluacion=${id_evaluacion}&tipo=2`,
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log("Datos de competencias finales recibidos:", response);

      if (
        response.status === "success" &&
        response.data &&
        response.data.length > 0
      ) {
        // Limpiar la tabla antes de cargar nuevos datos
        $("#tabla_competencias_avance_final").empty();

        // Generar las filas de la tabla
        let filas = "";

        response.data.forEach(function (competencia, index) {
          // Obtener valores para el cálculo
          const avanceIntermedio = competencia.porcentaje_actual || 0;
          const porc_etapa_final = competencia.porc_etapa_final || 0;
          // Calcular el nuevo avance final que ingresó el usuario
          const nuevoAvanceFinal = Math.max(
            0,
            porc_etapa_final - avanceIntermedio
          );
          // El avance actual es el porc_etapa_final (la suma guardada)
          const avanceActual = porc_etapa_final;
          // Calcular el máximo permitido para el input
          const maxAvanceFinal = Math.max(
            0,
            130 - (competencia.porcentaje_actual || 0)
          );

          // Determinar el color de la barra de progreso según el avance actual
          let progressClass = "bg-secondary";
          if (avanceActual >= 101) {
            progressClass = "bg-purple"; // sobresaliente morado
          } else if (avanceActual >= 75) {
            progressClass = "bg-success";
          } else if (avanceActual >= 50) {
            progressClass = "bg-info";
          } else if (avanceActual >= 25) {
            progressClass = "bg-warning";
          } else if (avanceActual > 0) {
            progressClass = "bg-danger";
          }

          // Determinar el color del badge según el tipo de competencia
          let badgeClass = "badge-secondary";
          switch (competencia.tipo_competencia) {
            case "ESENCIAL":
              badgeClass = "badge-primary";
              break;
            case "TECNICA":
              badgeClass = "badge-info";
              break;
            case "INTERPERSONAL":
              badgeClass = "badge-success";
              break;
            case "GERENCIAL":
              badgeClass = "badge-warning";
              break;
            default:
              badgeClass = "badge-secondary";
          }

          filas += `
                        <tr data-competencia-final-id="${
                          competencia.id || index + 1
                        }">
                            <td>
                                <strong>${
                                  competencia.nombre_competencia ||
                                  "Competencia sin nombre"
                                }</strong>
                                <br><small class="text-muted">${
                                  competencia.descripcion_competencia ||
                                  "Sin descripción"
                                }</small>
                            </td>
                            <td>
                                <span class="badge ${badgeClass}">${
            competencia.tipo_competencia || "General"
          }</span>
                            </td>
                            <td>${competencia.meta || "Sin meta definida"}</td>
                            <td>
                                <textarea class="form-control form-control-sm" rows="2" id="comentarios_competencias_final_${
                                  competencia.id || index + 1
                                }" placeholder="Comentarios finales">${
            competencia.coment_competencia_ff || ""
          }</textarea>
                            </td>
                            <td>
                                <div class="progress" style="height: 15px;">
                                    <div class="progress-bar bg-info" style="width: ${
                                      competencia.porcentaje_actual || 0
                                    }%">
                                        ${competencia.porcentaje_actual || 0}%
                                    </div>
                                </div>
                            </td>
                            <td>
                        <input type="number" class="form-control form-control-sm avance-input-final" 
                            value="${
                              nuevoAvanceFinal > 0 ? nuevoAvanceFinal : ""
                            }" min="0" max="${maxAvanceFinal}" placeholder="0"
                            data-competencia-final-id="${
                              competencia.id || index + 1
                            }">
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

        console.log(
          `Se cargaron ${response.data.length} competencias finales en la tabla`
        );
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
        console.log(
          "No se encontraron competencias finales para la evaluación"
        );
      }
    },
    error: function (xhr, status, error) {
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
      mostrarMensajeFinal(
        "Error al cargar competencias finales: " + error,
        "error"
      );
    },
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

  $("#tabla_objetivos_avance_final input.avance-input-final").each(function () {
    const input = $(this);
    const objetivoId = input.data("objetivo-final-id");
    const nuevoAvanceFinal = parseFloat(input.val()) || 0;

    // Obtener el avance intermedio de la misma fila
    const fila = input.closest("tr");
    const avanceIntermedioElement = fila.find("td").eq(5).find(".progress-bar");
    let avanceIntermedio = 0;
    if (avanceIntermedioElement.length > 0) {
      const texto = avanceIntermedioElement.text().replace("%", "");
      avanceIntermedio = parseFloat(texto) || 0;
    }

    // Calcular el porcentaje final real (Avance Intermedio + Nuevo Avance Final)
    const porcentajeFinal = Math.min(avanceIntermedio + nuevoAvanceFinal, 130);

    // Añadir el campo de comentarios finales
    const comentariosFinal =
      $(`#comentarios_objetivos_final_${objetivoId}`).val() || "";
    console.log(
      "Comentarios finales del objetivo ID " + objetivoId + ":",
      comentariosFinal
    );
    console.log(
      `Calculando: ${avanceIntermedio}% + ${nuevoAvanceFinal}% = ${porcentajeFinal}%`
    );

    // Validar que el nuevo avance esté en el rango válido
    if (nuevoAvanceFinal < 0 || nuevoAvanceFinal > 130) {
      mostrarMensajeFinal(
        `El nuevo avance del objetivo ID ${objetivoId} debe estar entre 0 y 130`,
        "warning"
      );
      return;
    }

    actualizaciones.push({
      id: objetivoId,
      porc_etapa_final: porcentajeFinal,
      coment_objetivo_ff: comentariosFinal,
    });
  });

  if (actualizaciones.length === 0) {
    mostrarMensajeFinal("No hay objetivos para actualizar", "info");
    return;
  }

  // Verificar que tenemos el ID de evaluación
  if (!evaluacionActualFinal) {
    console.error("ERROR: evaluacionActualFinal es null al guardar objetivos");
    mostrarMensajeFinal("Error: No se pudo identificar la evaluación", "error");
    return;
  }

  // Obtener comentarios generales finales para objetivos
  const comentariosObjetivosFinal =
    $("#comentarios_objetivos_general_final").val() || "";

  // Enviar actualizaciones al servidor incluyendo comentarios
  actualizarAvancesFinalEnServidor(1, actualizaciones, "objetivos", null, {
    comentarios_objetivos_general_final: comentariosObjetivosFinal,
    id_evaluacion: evaluacionActualFinal,
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

  $("#tabla_competencias_avance_final input.avance-input-final").each(
    function () {
      const input = $(this);
      const competenciaId = input.data("competencia-final-id");
      const nuevoAvanceFinal = parseFloat(input.val()) || 0;

      // Obtener el avance intermedio de la misma fila
      const fila = input.closest("tr");
      const avanceIntermedioElement = fila
        .find("td")
        .eq(4)
        .find(".progress-bar");
      let avanceIntermedio = 0;
      if (avanceIntermedioElement.length > 0) {
        const texto = avanceIntermedioElement.text().replace("%", "");
        avanceIntermedio = parseFloat(texto) || 0;
      }

      // Calcular el porcentaje final real (Avance Intermedio + Nuevo Avance Final)
      const porcentajeFinal = Math.min(
        avanceIntermedio + nuevoAvanceFinal,
        130
      );

      // Añadir el campo de comentarios finales
      const comentariosFinalComp =
        $(`#comentarios_competencias_final_${competenciaId}`).val() || "";
      console.log(
        "Comentarios finales de la competencia ID " + competenciaId + ":",
        comentariosFinalComp
      );
      console.log(
        `Calculando: ${avanceIntermedio}% + ${nuevoAvanceFinal}% = ${porcentajeFinal}%`
      );

      // Validar que el nuevo avance esté en el rango válido
      if (nuevoAvanceFinal < 0 || nuevoAvanceFinal > 130) {
        mostrarMensajeFinal(
          `El nuevo avance de la competencia ID ${competenciaId} debe estar entre 0 y 130`,
          "warning"
        );
        return;
      }

      actualizaciones.push({
        id: competenciaId,
        porc_etapa_final: porcentajeFinal,
        coment_competencia_ff: comentariosFinalComp,
      });
    }
  );

  if (actualizaciones.length === 0) {
    mostrarMensajeFinal("No hay competencias para actualizar", "info");
    return;
  }

  // Verificar que tenemos el ID de evaluación
  if (!evaluacionActualFinal) {
    console.error(
      "ERROR: evaluacionActualFinal es null al guardar competencias"
    );
    mostrarMensajeFinal("Error: No se pudo identificar la evaluación", "error");
    return;
  }

  // Enviar actualizaciones al servidor
  actualizarAvancesFinalEnServidor(2, actualizaciones, "competencias", null, {
    id_evaluacion: evaluacionActualFinal,
  });
}

/**
 * Función genérica para enviar actualizaciones finales al servidor
 */
function actualizarAvancesFinalEnServidor(
  tipo,
  actualizaciones,
  tipoNombre,
  callback,
  comentarios = {}
) {
  console.log(
    `Enviando ${actualizaciones.length} actualizaciones finales de ${tipoNombre} al servidor...`
  );

  // Mostrar indicador de carga
  const btnGuardar =
    tipo === 1
      ? $('button[onclick="guardarAvanceObjetivosFinal()"]')
      : $('button[onclick="guardarAvanceCompetenciasFinal()"]');

  const textoOriginal = btnGuardar.html();
  btnGuardar
    .prop("disabled", true)
    .html('<i class="fas fa-spinner fa-spin mr-1"></i>Guardando...');

  // Preparar datos para enviar incluyendo comentarios
  const dataToSend = {
    tipo: tipo,
    actualizaciones: actualizaciones,
    ...comentarios, // Spread operator para incluir comentarios e id_evaluacion
  };

  console.log("Datos finales a enviar:", dataToSend);

  $.ajax({
    url: "/rrhh/api/detalles-evaluacion-final/",
    type: "PUT",
    contentType: "application/json",
    data: JSON.stringify(dataToSend),
    success: function (response) {
      console.log(
        `Respuesta del servidor para ${tipoNombre} finales:`,
        response
      );

      if (response.status === "success") {
        let mensaje = `${
          tipoNombre.charAt(0).toUpperCase() + tipoNombre.slice(1)
        } finales actualizados exitosamente`;
        if (response.data.comentarios_actualizados) {
          mensaje += " y comentarios finales guardados";
        }
        mostrarMensajeFinal(mensaje, "success");

        // Actualizar las barras de progreso en la tabla
        actualizarBarrasProgresoFinal(tipo, actualizaciones);

        if (callback) callback(true);
      } else if (response.status === "partial_success") {
        const exitosas = response.data.exitosas;
        const fallidas = response.data.fallidas;
        let mensaje = `${tipoNombre} finales: ${exitosas} actualizados, ${fallidas} con errores`;
        if (response.data.comentarios_actualizados) {
          mensaje += " y comentarios finales guardados";
        }
        mostrarMensajeFinal(mensaje, "warning");

        if (callback) callback(true);
      } else {
        mostrarMensajeFinal(
          `Error al actualizar ${tipoNombre} finales: ${response.message}`,
          "error"
        );
        if (callback) callback(false);
      }
    },
    error: function (xhr, status, error) {
      console.error(`Error al actualizar ${tipoNombre} finales:`, error);
      let mensaje = `Error de conexión al actualizar ${tipoNombre} finales`;

      if (xhr.responseJSON && xhr.responseJSON.message) {
        mensaje = `Error al actualizar ${tipoNombre} finales: ${xhr.responseJSON.message}`;
      }

      mostrarMensajeFinal(mensaje, "error");
      if (callback) callback(false);
    },
    complete: function () {
      // Restaurar el botón
      btnGuardar.prop("disabled", false).html(textoOriginal);
    },
  });
}

/**
 * Función para actualizar las barras de progreso finales en la tabla después de guardar
 */
function actualizarBarrasProgresoFinal(tipo, actualizaciones) {
  const tablaSelector =
    tipo === 1
      ? "#tabla_objetivos_avance_final"
      : "#tabla_competencias_avance_final";

  actualizaciones.forEach(function (item) {
    const fila = $(
      `${tablaSelector} tr[data-${
        tipo === 1 ? "objetivo-final" : "competencia-final"
      }-id="${item.id}"]`
    );

    if (fila.length > 0) {
      // Actualizar la barra de progreso final
      const progressBar = fila.find(".progress-bar").eq(1); // Segunda barra (final)
      const nuevoAncho = item.porc_etapa_final + "%";

      progressBar.css("width", nuevoAncho).text(nuevoAncho);

      // Actualizar color de la barra según el porcentaje final
      progressBar.removeClass(
        "bg-secondary bg-danger bg-warning bg-info bg-success"
      );
      if (item.porc_etapa_final >= 75) {
        progressBar.addClass("bg-success");
      } else if (item.porc_etapa_final >= 50) {
        progressBar.addClass("bg-info");
      } else if (item.porc_etapa_final >= 25) {
        progressBar.addClass("bg-warning");
      } else if (item.porc_etapa_final > 0) {
        progressBar.addClass("bg-danger");
      } else {
        progressBar.addClass("bg-secondary");
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
  $(document).on("input", ".avance-input-final", function () {
    const input = $(this);
    let valor = parseFloat(input.val()) || 0;
    // Obtener el máximo permitido dinámicamente
    let max = parseFloat(input.attr("max"));
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
    const fila = input.closest("tr");
    calcularAvanceActual(fila, valor);
    // Agregar clase visual para indicar cambio
    input.addClass("changed");
  });

  // Evento para tecla Enter en inputs
  $(document).on("keypress", ".avance-input-final", function (e) {
    if (e.which === 13) {
      // Enter
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
    let avanceIntermedioElement = fila.find("td").eq(5).find(".progress-bar");

    // Si no encuentra en la posición 5, buscar en la posición 4 (para competencias)
    if (avanceIntermedioElement.length === 0) {
      avanceIntermedioElement = fila.find("td").eq(4).find(".progress-bar");
    }

    // Obtener el porcentaje del avance intermedio
    let avanceIntermedio = 0;
    if (avanceIntermedioElement.length > 0) {
      const texto = avanceIntermedioElement.text().replace("%", "");
      avanceIntermedio = parseFloat(texto) || 0;
    }

    // Calcular el avance actual (suma)
    const avanceActual = avanceIntermedio + nuevoAvance;
    // Limitar el avance actual a máximo 130%
    const avanceActualLimitado = Math.min(avanceActual, 130);

    // Buscar la barra de progreso del Avance Actual (última columna)
    const avanceActualElement = fila.find("td").last().find(".progress-bar");

    if (avanceActualElement.length > 0) {
      // Actualizar el ancho y texto de la barra de progreso
      avanceActualElement.css("width", avanceActualLimitado + "%");
      avanceActualElement.text(avanceActualLimitado + "%");

      // Actualizar el color según el porcentaje
      let progressClass = "bg-secondary";
      if (avanceActualLimitado >= 101) {
        progressClass = "bg-purple";
      } else if (avanceActualLimitado >= 75 && avanceActualLimitado <= 100) {
        progressClass = "bg-success";
      } else if (avanceActualLimitado >= 50) {
        progressClass = "bg-info";
      } else if (avanceActualLimitado >= 25) {
        progressClass = "bg-warning";
      } else if (avanceActualLimitado > 0) {
        progressClass = "bg-danger";
      }

      // Remover clases anteriores y agregar la nueva
      avanceActualElement.removeClass(
        "bg-purple bg-success bg-info bg-warning bg-danger bg-secondary"
      );
      avanceActualElement.addClass(progressClass);
    }

    console.log(
      `Avance calculado: ${avanceIntermedio}% + ${nuevoAvance}% = ${avanceActualLimitado}%`
    );
  } catch (error) {
    console.error("Error al calcular avance actual:", error);
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
function mostrarMensajeFinal(mensaje, tipo = "info") {
  // Verificar si SweetAlert2 está disponible
  if (typeof Swal !== "undefined") {
    let icon;
    let title;

    switch (tipo) {
      case "success":
        icon = "success";
        title = "Éxito";
        break;
      case "error":
        icon = "error";
        title = "Error";
        break;
      case "warning":
        icon = "warning";
        title = "Advertencia";
        break;
      case "info":
      default:
        icon = "info";
        title = "Información";
        break;
    }

    Swal.fire({
      title: title,
      text: mensaje,
      icon: icon,
      timer: tipo === "success" ? 3000 : 0,
      showConfirmButton: tipo !== "success",
      toast: tipo === "success",
      position: tipo === "success" ? "top-end" : "center",
    });
  } else {
    // Fallback a alert básico si SweetAlert2 no está disponible
    alert(`${tipo.toUpperCase()}: ${mensaje}`);
  }

  // También logear en consola
  console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
}

// FASE FINAL - FIN

const EmailManagerFinal = {
  // Configuración del módulo específica para Fase Final
  config: {
    endpoints: {
      evaluaciones: "/produccionuva1/objetivos_evaluacion/",
      detallesObjetivos: "/produccionuva1/detalles_objetivos/",
    },
    scripts: {
      competenciasPaths: [
        "/static/core/js/PRODUCCIONUVA1/DonLuis/rrhh_ev_competencias.js",
      ],
    },
    messages: {
      confirmation: {
        title: "Confirmación - Fase Final",
        text: "¿Desea generar el PDF de esta evaluación final y enviarlo por correo?",
        confirmButtonText: "Sí, generar y enviar",
        cancelButtonText: "Cancelar",
      },
      loading: {
        title: "Procesando - Fase Final",
        text: "Generando PDF de fase final y preparando envío...",
      },
      errors: {
        invalidId: "No se pudo identificar la evaluación final",
        scriptLoad:
          "No se pudo cargar el script necesario para generar el PDF final",
        functionNotFound:
          "No se pudo cargar la funcionalidad de generación de PDF final",
      },
    },
    metadata: {
      modulo: "Fase Final",
      version: "1.0.0",
      descripcion:
        "Gestión de correos para evaluaciones de cierre - Fase Final",
    },
  },

  validarIdEvaluacion(idEvaluacion) {
    return idEvaluacion && !isNaN(parseInt(idEvaluacion));
  },

  mostrarError(mensaje) {
    Swal.fire({
      icon: "error",
      title: "Error - Fase Final",
      text: mensaje,
      confirmButtonColor: "#dc3545",
      footer: `<small>Módulo: ${this.config.metadata.modulo}</small>`,
    });
  },

  mostrarConfirmacion(callback) {
    const { confirmation } = this.config.messages;

    Swal.fire({
      icon: "question",
      title: confirmation.title,
      text: confirmation.text,
      showCancelButton: true,
      confirmButtonText: confirmation.confirmButtonText,
      cancelButtonText: confirmation.cancelButtonText,
      confirmButtonColor: "#28a745",
      cancelButtonColor: "#6c757d",
      footer: `<small>Módulo: ${this.config.metadata.modulo}</small>`,
    }).then((result) => {
      if (result.isConfirmed) callback();
    });
  },

  mostrarCarga() {
    const { loading } = this.config.messages;

    Swal.fire({
      title: loading.title,
      text: loading.text,
      allowOutsideClick: false,
      didOpen: () => Swal.showLoading(),
    });
  },

  esFuncionPDFDisponible() {
    return typeof generarPDFFinal === "function";
  },

  cargarScriptCompetencias(idEvaluacion, intentoActual = 0) {
    const { scripts } = this.config;

    if (intentoActual >= scripts.competenciasPaths.length) {
      this.mostrarError(this.config.messages.errors.scriptLoad);
      return;
    }

    const scriptPath = scripts.competenciasPaths[intentoActual];

    console.log(
      `[Fase Final] Intentando cargar script ${intentoActual + 1}/${
        scripts.competenciasPaths.length
      }: ${scriptPath}`
    );

    $.getScript(scriptPath)
      .done(() => {
        console.log(`[Fase Final] Script cargado exitosamente: ${scriptPath}`);
        if (this.esFuncionPDFDisponible()) {
          this.ejecutarGeneracionPDF(idEvaluacion);
        } else {
          this.cargarScriptCompetencias(idEvaluacion, intentoActual + 1);
        }
      })
      .fail(() => {
        console.warn(`[Fase Final] Falló la carga del script: ${scriptPath}`);
        this.cargarScriptCompetencias(idEvaluacion, intentoActual + 1);
      });
  },

  ejecutarGeneracionPDF(idEvaluacion) {
    if (this.esFuncionPDFDisponible()) {
      console.log(
        `[Fase Final] Ejecutando generación de PDF para evaluación ID: ${idEvaluacion}`
      );
      generarPDFFinal(idEvaluacion);
    } else {
      this.mostrarError(this.config.messages.errors.functionNotFound);
    }
  },

  procesarGeneracionPDF(idEvaluacion) {
    this.mostrarCarga();

    if (this.esFuncionPDFDisponible()) {
      console.log(
        `[Fase Final] Función PDF disponible, ejecutando directamente`
      );
      this.ejecutarGeneracionPDF(idEvaluacion);
    } else {
      console.log(
        `[Fase Final] Función PDF no disponible, cargando scripts...`
      );
      this.cargarScriptCompetencias(idEvaluacion);
    }
  },

  generarEnviarPDFEvaluacionFinal(idEvaluacion) {
    if (!this.validarIdEvaluacion(idEvaluacion)) {
      this.mostrarError(this.config.messages.errors.invalidId);
      return;
    }

    const id = parseInt(idEvaluacion);

    this.mostrarConfirmacion(() => {
      this.procesarGeneracionPDF(id);
    });
  },

  registrarEventosGlobales() {
    $(document).on("click", "[data-id-evaluacion]", function () {
      const idEvaluacion = $(this).data("id-evaluacion");
      console.log(
        `[Fase Final] Usuario intentó enviar PDF final para evaluación ID: ${idEvaluacion}`
      );

      if (typeof gtag !== "undefined") {
        gtag("event", "pdf_email_request", {
          event_category: "fase_final",
          event_label: "evaluacion_final",
          value: idEvaluacion,
        });
      }
    });
  },

  extenderConfiguracion(nuevaConfig) {
    this.config = { ...this.config, ...nuevaConfig };
    console.log(
      `[Fase Final] Configuración de EmailManagerFinal actualizada`,
      nuevaConfig
    );
  },

  obtenerEstadisticas() {
    return {
      modulo: this.config.metadata.modulo,
      version: this.config.metadata.version,
      moduloActivo: true,
      funcionPDFDisponible: this.esFuncionPDFDisponible(),
      ultimaInicializacion: new Date().toISOString(),
      endpointsConfigrurados: Object.keys(this.config.endpoints).length,
      scriptsDisponibles: this.config.scripts.competenciasPaths.length,
    };
  },

  verificarSalud() {
    const salud = {
      modulo: this.config.metadata.modulo,
      estado: "OK",
      problemas: [],
      recomendaciones: [],
    };

    if (typeof $ === "undefined") {
      salud.estado = "ERROR";
      salud.problemas.push("jQuery no está disponible");
    }

    if (typeof Swal === "undefined") {
      salud.estado = "ERROR";
      salud.problemas.push("SweetAlert2 no está disponible");
    }

    if (!this.esFuncionPDFDisponible()) {
      salud.estado = "WARNING";
      salud.problemas.push("Función de generación de PDF no disponible");
      salud.recomendaciones.push(
        "Los scripts necesarios se cargarán dinámicamente cuando sea necesario"
      );
    }

    return salud;
  },

  inicializar() {
    console.log(`[Fase Final] EmailManagerFinal inicializado correctamente`);
    console.log(`[Fase Final] Configuración:`, this.config.metadata);

    const salud = this.verificarSalud();
    console.log(`[Fase Final] Estado del módulo:`, salud);

    if (salud.estado === "ERROR") {
      console.error(
        `[Fase Final] Errores críticos detectados:`,
        salud.problemas
      );
    } else if (salud.estado === "WARNING") {
      console.warn(`[Fase Final] Advertencias detectadas:`, salud.problemas);
    }

    this.registrarEventosGlobales();

    const stats = this.obtenerEstadisticas();
    console.log(`[Fase Final] Estadísticas del módulo:`, stats);
  },
};

function generarPDFFinal(id_evaluacion) {
  Swal.fire({
    title: "Generando PDF (Fase Final)",
    text: "Procesando información, por favor espere...",
    allowOutsideClick: false,
    didOpen: () => Swal.showLoading(),
  });

  $.ajax({
    url: "/rrhh/rrhh_evaluaciones/",
    type: "GET",
    dataType: "json",
    success: function (responseEvaluaciones) {
      if (!responseEvaluaciones.data) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudieron obtener las evaluaciones.",
        });
        return;
      }

      const evaluacionActual = responseEvaluaciones.data.find(
        (eval) => eval.id == id_evaluacion
      );

      if (!evaluacionActual) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se encontró la evaluación solicitada.",
        });
        return;
      }

      const id_evaluador = evaluacionActual.id_evaluador;
      const id_evaluado = evaluacionActual.id_evaluado;

      const comentario_objetivo = evaluacionActual.comentarios_objetivosgeneral;
      const comentario_competencia =
        evaluacionActual.comentarios_competencias_general;

      $.ajax({
        url: "/rrhh/usuarios/",
        type: "GET",
        dataType: "json",
        success: function (responseUsuarios) {
          const evaluador = responseUsuarios.data.find(
            (u) => u.id == id_evaluador
          );
          const evaluado = responseUsuarios.data.find(
            (u) => u.id == id_evaluado
          );

          let datosPersonalEvaluado = null;
          let datosPersonalEvaluador = null;

          let consultasCompletadas = 0;

          const continuarFlujo = () => {
            $.ajax({
              url: "/produccionuva1/detalles_objetivos/",
              type: "GET",
              dataType: "json",
              success: function (responseObjetivos) {
                const objetivos = responseObjetivos.data.filter(
                  (o) => o.id_evaluacion == id_evaluacion
                );

                $.ajax({
                  url: "/produccionuva1/detalles_competencias/",
                  type: "GET",
                  dataType: "json",
                  success: function (responseCompetencias) {
                    const competencias = responseCompetencias.data.filter(
                      (c) => c.id_evaluacion == id_evaluacion
                    );

                    if (objetivos.length === 0 && competencias.length === 0) {
                      Swal.fire({
                        icon: "warning",
                        title: "Sin datos",
                        text: "Esta evaluación no contiene información registrada.",
                      });
                      return;
                    }

                    const datosCompletos = {
                      ...objetivos[0],
                      datosPersonalEvaluado,
                      datosPersonalEvaluador,
                      comentario_objetivo,
                      comentario_competencia,
                      periodo: evaluacionActual.periodo,
                      fecha_evaluacion: evaluacionActual.fecha_evaluacion,
                      id_evaluacion: evaluacionActual.id,
                      nombre_evaluado:
                        datosPersonalEvaluado?.NOMBRE_COMPLETO || "Evaluado",
                      email: evaluado?.email || "",
                    };

                    crearContenidoPDFFinal(
                      datosCompletos,
                      objetivos,
                      competencias
                    );
                  },
                });
              },
            });
          };

          if (evaluado?.dni) {
            $.ajax({
              url: `/rrhh/datos_personal_por_dni/?dni=${evaluado.dni}`,
              type: "GET",
              success: function (response) {
                datosPersonalEvaluado = response.data?.[0] || null;
                if (++consultasCompletadas === 2) continuarFlujo();
              },
              error: () => {
                if (++consultasCompletadas === 2) continuarFlujo();
              },
            });
          } else consultasCompletadas++;

          if (evaluador?.dni) {
            $.ajax({
              url: `/rrhh/datos_personal_por_dni/?dni=${evaluador.dni}`,
              type: "GET",
              success: function (response) {
                datosPersonalEvaluador = response.data?.[0] || null;
                if (++consultasCompletadas === 2) continuarFlujo();
              },
              error: () => {
                if (++consultasCompletadas === 2) continuarFlujo();
              },
            });
          } else consultasCompletadas++;
        },
      });
    },
  });
}
//########################################################

function crearContenidoPDFFinal(datosEvaluado, objetivos, competencias) {
  try {
    const pdf = new window.jspdf.jsPDF("p", "mm", "a4");
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();

    let paginaActual = 1;
    const totalPaginas =
      1 + objetivos.length + (competencias ? competencias.length : 0);

    function agregarEncabezado(datos = null) {
      const d = datos || datosEvaluado;

      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(0, 0, 0);
      pdf.setTextColor(0, 0, 0);

      const margenLateral = 15;
      const anchoUtil = pdfWidth - margenLateral * 2;

      const altoFilaLogos = 20;
      const anchoCeldaLogo = Math.floor(anchoUtil * 0.35);
      const anchoTablaInfo = Math.floor(anchoUtil * 0.3);

      const posXLogoIzq = margenLateral;
      const posXLogoDer = margenLateral + anchoCeldaLogo;
      const posXTabla = margenLateral + anchoCeldaLogo * 2;

      pdf.rect(posXLogoIzq, 10, anchoCeldaLogo, altoFilaLogos, "S");
      pdf.rect(posXLogoDer, 10, anchoCeldaLogo, altoFilaLogos, "S");
      pdf.rect(posXTabla, 10, anchoTablaInfo, altoFilaLogos, "S");

      try {
        pdf.addImage(
          "/static/assets/img/logo/logo_pngdl.png",
          "PNG",
          posXLogoIzq + 20,
          11,
          anchoCeldaLogo - 45,
          14
        );
      } catch (e) {}

      pdf.setFontSize(6);
      pdf.text(
        "SOCIEDAD AGRÍCOLA DON LUIS S.A.",
        posXLogoIzq + anchoCeldaLogo / 2,
        27,
        { align: "center" }
      );

      try {
        pdf.addImage(
          "/static/assets/img/logo/Logoacv.webp",
          "WEBP",
          posXLogoDer + 15,
          11,
          anchoCeldaLogo - 30,
          14
        );
      } catch (e) {}

      pdf.text(
        "AGROINDUSTRIA CAMPO VERDE S.A.C.",
        posXLogoDer + anchoCeldaLogo / 2,
        27,
        { align: "center" }
      );

      const hoy = new Date();
      const fechaForm = `${hoy.getDate().toString().padStart(2, "0")}.${(
        hoy.getMonth() + 1
      )
        .toString()
        .padStart(2, "0")}.${hoy.getFullYear()}`;

      const infoItems = [
        {
          label: "Código:",
          value: d.id_evaluacion ? `EVAL-${d.id_evaluacion}` : "N/A",
        },
        { label: "Versión:", value: "01" },
        { label: "Fecha :", value: fechaForm },
        { label: "páginas:", value: `${paginaActual} de ${totalPaginas}` },
      ];

      pdf.setTextColor(0, 0, 0);

      const altoFilaInfo = altoFilaLogos / infoItems.length;
      const medioCelda = Math.floor(anchoTablaInfo / 2);

      for (let i = 0; i < infoItems.length; i++) {
        pdf.line(
          posXTabla,
          10 + (i + 1) * altoFilaInfo,
          posXTabla + anchoTablaInfo,
          10 + (i + 1) * altoFilaInfo
        );

        pdf.line(
          posXTabla + medioCelda,
          10 + i * altoFilaInfo,
          posXTabla + medioCelda,
          10 + (i + 1) * altoFilaInfo
        );

        pdf.text(
          infoItems[i].label,
          posXTabla + 2,
          10 + i * altoFilaInfo + altoFilaInfo * 0.6
        );
        pdf.text(
          infoItems[i].value,
          posXTabla + medioCelda + 2,
          10 + i * altoFilaInfo + altoFilaInfo * 0.6
        );
      }

      const altoFilaTitulo = 15;
      pdf.rect(
        margenLateral,
        10 + altoFilaLogos,
        anchoUtil,
        altoFilaTitulo,
        "S"
      );

      pdf.setFontSize(11);
      pdf.setFont("helvetica", "bold");
      pdf.text(
        "FASE FINAL - EVALUACIÓN DE OBJETIVOS, COMPETENCIAS Y ACCIONES",
        margenLateral + anchoUtil / 2,
        10 + altoFilaLogos + 8,
        { align: "center" }
      );
      pdf.text(
        "DE DESARROLLO",
        margenLateral + anchoUtil / 2,
        10 + altoFilaLogos + 14,
        { align: "center" }
      );

      return 10 + altoFilaLogos + altoFilaTitulo + 5;
    }

    function agregarPieDePagina() {
      pdf.addImage(
        "/static/assets/img/logo/pie_pagina.png",
        "PNG",
        0,
        pdfHeight - 40,
        pdfWidth,
        40
      );

      pdf.setTextColor(255, 255, 255);
      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(10);
      pdf.text("#creciendojuntos", pdfWidth / 2, pdfHeight - 5, {
        align: "center",
      });
    }

    function crearTituloSeccion(texto, y) {
      pdf.setFillColor(52, 101, 164);
      pdf.setDrawColor(52, 101, 164);
      pdf.rect(10, y, pdfWidth - 20, 7, "F");
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(10);
      pdf.setFont("helvetica", "bold");
      pdf.text(texto, 12, y + 5);
      pdf.setTextColor(0, 0, 0);
      return y + 10;
    }

    function calcularPuntajeFinal(objetivos, competencias) {
      let sumaObjetivos = 0;
      let cantidadObjetivos = 0;

      let sumaCompetencias = 0;
      let cantidadCompetencias = 0;

      // ===== OBJETIVOS =====
      objetivos.forEach(o => {
        const valor = parseFloat(o.porc_etapa_final);
        if (!isNaN(valor)) {
          sumaObjetivos += valor;
          cantidadObjetivos++;
        }
      });

      // ===== COMPETENCIAS =====
      competencias.forEach(c => {
        const valor = parseFloat(c.porc_etapa_final);
        if (!isNaN(valor)) {
          sumaCompetencias += valor;
          cantidadCompetencias++;
        }
      });

      // Calcular promedios individuales
      const promedioObjetivos = cantidadObjetivos > 0 
        ? sumaObjetivos / cantidadObjetivos 
        : 0;

      const promedioCompetencias = cantidadCompetencias > 0 
        ? sumaCompetencias / cantidadCompetencias 
        : 0;

      // Resultado final (50% - 50%)
      const resultadoFinal = (promedioObjetivos + promedioCompetencias) / 2;

      return Number(resultadoFinal.toFixed(2));
    }

    function obtenerMensajeDesempeno(resultadoFinal) {
      if (resultadoFinal >= 111) {
        return {
          titulo: "Modelo de Alto Desempeño",
          mensaje: "Es un modelo para sus compañeros en el cumplimiento de objetivos y práctica de competencias, y está listo para asumir mayores responsabilidades."
        };
      }

      if (resultadoFinal >= 101 && resultadoFinal <= 110) {
        return {
          titulo: "Desempeño Superior",
          mensaje: "Siempre cumple su trabajo de manera satisfactoria, excediendo casi siempre las expectativas."
        };
      }

      if (resultadoFinal === 100) {
        return {
          titulo: "Desempeño Satisfactorio",
          mensaje: "Cumple su trabajo de manera satisfactoria."
        };
      }

      return {
        titulo: "Desempeño en Desarrollo",
        mensaje: "No cumple su trabajo de manera satisfactoria."
      };
    }
    
    function obtenerColorPuntaje(puntaje) {
      if (puntaje >= 111) return [40, 167, 69];   // verde
      if (puntaje >= 101) return [255, 193, 7];   // amarillo
      if (puntaje === 100) return [0, 123, 255];  // azul
      return [220, 53, 69];                       // rojo
    }      

    // --- PÁGINA 1 (Datos del empleado + evaluador)
    let yPos = agregarEncabezado(datosEvaluado);

    yPos = crearTituloSeccion("I.- INFORMACIÓN DEL EMPLEADO:", yPos);

    // Crear tabla de información del empleado
    pdf.setFontSize(9);
    pdf.setDrawColor(0, 0, 0);

    // Fila 1
    pdf.rect(10, yPos, 25, 7, "S");
    pdf.rect(35, yPos, 85, 7, "S");
    pdf.rect(120, yPos, 35, 7, "S");
    pdf.rect(155, yPos, 45, 7, "S");

    pdf.setFont("helvetica", "bold");
    pdf.text("Nombre", 12, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(
      datosEvaluado.datosPersonalEvaluado.NOMBRE_COMPLETO || "N/A",
      37,
      yPos + 5
    );

    pdf.setFont("helvetica", "bold");
    pdf.text("Fecha de ingreso", 122, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(
      datosEvaluado.datosPersonalEvaluado.FECHA_INGRESO || "N/A",
      157,
      yPos + 5
    );

    yPos += 7;

    // Fila 2
    pdf.rect(10, yPos, 25, 7, "S");
    pdf.rect(35, yPos, 85, 7, "S");
    pdf.rect(120, yPos, 35, 7, "S");
    pdf.rect(155, yPos, 45, 7, "S");

    pdf.setFont("helvetica", "bold");
    pdf.text("Cargo", 12, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(datosEvaluado.datosPersonalEvaluado.CARGO || "N/A", 37, yPos + 5);

    pdf.setFont("helvetica", "bold");
    pdf.text("Fecha de evaluación", 122, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(datosEvaluado.fecha_evaluacion || "N/A", 157, yPos + 5);

    yPos += 7;

    // Fila 3
    pdf.rect(10, yPos, 25, 7, "S");
    pdf.rect(35, yPos, 85, 7, "S");
    pdf.rect(120, yPos, 35, 7, "S");
    pdf.rect(155, yPos, 45, 7, "S");

    pdf.setFont("helvetica", "bold");
    pdf.text("DNI", 12, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(datosEvaluado.datosPersonalEvaluado.DNI || "N/A", 37, yPos + 5);

    pdf.setFont("helvetica", "bold");
    pdf.text("Edad", 122, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(
      String(datosEvaluado.datosPersonalEvaluado.EDAD) || "N/A",
      157,
      yPos + 5
    );

    yPos += 15;

    // Sección 2: Datos del evaluador
    yPos = crearTituloSeccion("II.- DATOS DEL EVALUADOR:", yPos);

    // Crear tabla de información del evaluador
    // Fila 1
    pdf.rect(10, yPos, 25, 7, "S");
    pdf.rect(35, yPos, 85, 7, "S");
    pdf.rect(120, yPos, 35, 7, "S");
    pdf.rect(155, yPos, 45, 7, "S");

    pdf.setFont("helvetica", "bold");
    pdf.text("Nombre", 12, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(
      datosEvaluado.datosPersonalEvaluador.NOMBRE_COMPLETO || "N/A",
      37,
      yPos + 5
    );

    pdf.setFont("helvetica", "bold");
    pdf.text("Relación", 122, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(datosEvaluado.relacion || "Gerencia - Jefatura", 157, yPos + 5);

    yPos += 7;

    // Fila 2
    pdf.rect(10, yPos, 25, 7, "S");
    pdf.rect(35, yPos, 85, 7, "S");
    pdf.rect(120, yPos, 35, 7, "S");
    pdf.rect(155, yPos, 45, 7, "S");

    pdf.setFont("helvetica", "bold");
    pdf.text("Cargo", 12, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(datosEvaluado.datosPersonalEvaluador.CARGO || "N/A", 37, yPos + 5);

    pdf.setFont("helvetica", "bold");
    pdf.text("Departamento", 122, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(datosEvaluado.departamento || "Administración", 157, yPos + 5);

    yPos += 7;

    // Fila 3
    pdf.rect(10, yPos, 25, 7, "S");
    pdf.rect(35, yPos, 85, 7, "S");
    pdf.rect(120, yPos, 35, 7, "S");
    pdf.rect(155, yPos, 45, 7, "S");

    pdf.setFont("helvetica", "bold");
    pdf.text("Código", 12, yPos + 5);
    pdf.setFont("helvetica", "normal");
    pdf.text(datosEvaluado.datosPersonalEvaluador.DNI || "N/A", 37, yPos + 5);

    // Agregar pie de página solo si no hay objetivos ni competencias
    agregarPieDePagina(!objetivos || objetivos.length === 0);

    // PÁGINAS DE OBJETIVOS (UN OBJETIVO POR PÁGINA)
    if (objetivos && objetivos.length > 0) {
      objetivos.forEach((objetivo, index) => {
        pdf.addPage();
        paginaActual++;

        // Restablecer TODOS los atributos gráficos al cambiar de página
        pdf.setFillColor(255, 255, 255);
        pdf.setDrawColor(0, 0, 0);
        pdf.setTextColor(0, 0, 0); // CRÍTICO: Asegurar que el texto es negro
        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(9);

        yPos = agregarEncabezado(datosEvaluado);

        // Agregar título de sección solo en el primer objetivo
        if (index === 0) {
          yPos = crearTituloSeccion("III.- OBJETIVOS:", yPos);
        }

        // Crear título del objetivo
        pdf.setFillColor(52, 101, 164); // Color azul (#3465a4)
        pdf.setDrawColor(52, 101, 164);
        pdf.rect(10, yPos, pdfWidth - 20, 7, "F");

        pdf.setTextColor(255, 255, 255); // Texto blanco
        pdf.setFontSize(10);
        pdf.setFont("helvetica", "bold");
        pdf.text(`Objetivo ${index + 1}:`, 12, yPos + 5);

        pdf.setTextColor(0, 0, 0); // Volver a texto negro
        yPos += 10;

        // 1. Objetivo
        pdf.setFontSize(9);
        pdf.setDrawColor(0, 0, 0);
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("1. Objetivo:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text(objetivo.descripcion || "N/A", 12, yPos + 5);
        yPos += 10;

        // 2. Indicador
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("2. Indicador:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text(objetivo.indicador || "N/A", 12, yPos + 5);
        yPos += 10;

        // 3. META
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("3. META:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text(objetivo.meta || "N/A", 12, yPos + 5);
        yPos += 10;

        // 4. Fecha de Cumplimiento
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("4. Fecha de Cumplimiento:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text(objetivo.fecha_fin || "31/12/2024", 12, yPos + 5);
        yPos += 10;

        // 5-6. Revisiones
        pdf.rect(10, yPos, (pdfWidth - 20) / 2, 7, "S");
        pdf.rect(10 + (pdfWidth - 20) / 2, yPos, (pdfWidth - 20) / 2, 7, "S");
        pdf.text(
          `5. Revisión Intermedia (${objetivo.porc_cumplimiento || " -- "}%)`,
          12,
          yPos + 5
        );
        pdf.text(
          `6. Revisión final (${objetivo.porc_etapa_final || " -- "}%)`,
          10 + (pdfWidth - 20) / 2 + 2,
          yPos + 5
        );
        yPos += 7;

        // Ancho de columnas
        const colWidth = (pdfWidth - 20) / 2 - 4;

        // === Comentario Intermedio ===
        let comentarioInter = pdf.splitTextToSize(
          `Comentario Fase Intermedia: ${objetivo.comentarios_objetivos || ""}`,
          colWidth
        );

        // === Comentario Final ===
        let comentarioFinal = pdf.splitTextToSize(
          `Comentario Fase Final: ${objetivo.coment_objetivo_ff || ""}`,
          colWidth
        );

        // Calcular la altura necesaria según líneas de texto
        const lineHeight = 4.5; // altura por línea (ajustable)
        const altoInter = comentarioInter.length * lineHeight + 6; // +6 margen
        const altoFinal = comentarioFinal.length * lineHeight + 6;

        // La celda debe tener la altura del texto más alto
        const altoCelda = Math.max(altoInter, altoFinal, 30); // mínimo 30

        // Dibujar rectángulos con altura dinámica
        pdf.rect(10, yPos, (pdfWidth - 20) / 2, altoCelda, "S");
        pdf.rect(
          10 + (pdfWidth - 20) / 2,
          yPos,
          (pdfWidth - 20) / 2,
          altoCelda,
          "S"
        );

        // Imprimir textos dentro
        pdf.text(comentarioInter, 12, yPos + 5);
        pdf.text(comentarioFinal, 10 + (pdfWidth - 20) / 2 + 2, yPos + 5);

        // Mover Y según altura real
        yPos += altoCelda + 5;
      });
    }

    // PÁGINAS DE COMPROMISOS (UN COMPROMISO POR PÁGINA)
    if (competencias && competencias.length > 0) {
      competencias.forEach((competencia, index) => {
        pdf.addPage();
        paginaActual++;

        // Restablecer TODOS los atributos gráficos al cambiar de página
        pdf.setFillColor(255, 255, 255);
        pdf.setDrawColor(0, 0, 0);
        pdf.setTextColor(0, 0, 0); // CRÍTICO: Asegurar que el texto es negro
        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(9);

        yPos = agregarEncabezado(datosEvaluado);

        // Agregar título de sección solo en la primera competencia
        if (index === 0) {
          yPos = crearTituloSeccion("IV.- COMPETENCIAS:", yPos);
        }

        // Crear título del compromiso
        pdf.setFillColor(52, 101, 164); // Color azul (#3465a4)
        pdf.setDrawColor(52, 101, 164);
        pdf.rect(10, yPos, pdfWidth - 20, 7, "F");

        pdf.setTextColor(255, 255, 255); // Texto blanco
        pdf.setFontSize(10);
        pdf.setFont("helvetica", "bold");
        pdf.text(`Compromiso ${index + 1}:`, 12, yPos + 5);

        pdf.setTextColor(0, 0, 0); // Volver a texto negro
        yPos += 10;

        // 1. Descripción
        pdf.setFontSize(9);
        pdf.setDrawColor(0, 0, 0);
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("1. Competencia:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text(
          competencia.nombre_competencia || "no se encuentra la competencia",
          12,
          yPos + 5
        );
        yPos += 10;

        // 2. Objetivo
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("2. Meta:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text(competencia.meta || "no se encuentra la meta", 12, yPos + 5);
        yPos += 10;

        // 3. Comentario
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("3. Comentario:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text(competencia.comentarios || "sin comentarios", 12, yPos + 5);
        yPos += 10;

        // 3. Fecha
        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("3. Fecha de Cumplimiento:", 12, yPos + 5);
        yPos += 7;

        pdf.rect(10, yPos, pdfWidth - 20, 7, "S");
        pdf.text("31/12/2024", 12, yPos + 5);
        yPos += 10;

        // 4-5. Revisiones
        pdf.rect(10, yPos, (pdfWidth - 20) / 2, 7, "S");
        pdf.rect(10 + (pdfWidth - 20) / 2, yPos, (pdfWidth - 20) / 2, 7, "S");
        pdf.text(
          `4. Revisión Intermedia (${
            competencia.porc_cumplimiento || " -- "
          }%)`,
          12,
          yPos + 5
        );
        pdf.text(
          `5. Revisión final (${competencia.porc_etapa_final || " -- "}%)`,
          10 + (pdfWidth - 20) / 2 + 2,
          yPos + 5
        );
        yPos += 7;

        // Comentarios
        const colWidth = (pdfWidth - 20) / 2 - 4;

        // === Comentario Intermedio ===
        let comentarioInter = pdf.splitTextToSize(
          `Comentario Fase Intermedia: ${
            competencia.comentarios_competencias || ""
          }`,
          colWidth
        );

        // === Comentario Final ===
        let comentarioFinal = pdf.splitTextToSize(
          `Comentario Fase Final: ${competencia.coment_competencia_ff || ""}`,
          colWidth
        );

        // Calcular la altura necesaria según líneas de texto
        const lineHeight = 4.5; // altura por línea (ajustable)
        const altoInter = comentarioInter.length * lineHeight + 6; // +6 margen
        const altoFinal = comentarioFinal.length * lineHeight + 6;

        // La celda debe tener la altura del texto más alto
        const altoCelda = Math.max(altoInter, altoFinal, 30); // mínimo 30

        // Dibujar rectángulos con altura dinámica
        pdf.rect(10, yPos, (pdfWidth - 20) / 2, altoCelda, "S");
        pdf.rect(
          10 + (pdfWidth - 20) / 2,
          yPos,
          (pdfWidth - 20) / 2,
          altoCelda,
          "S"
        );

        // Imprimir textos dentro
        pdf.text(comentarioInter, 12, yPos + 5);
        pdf.text(comentarioFinal, 10 + (pdfWidth - 20) / 2 + 2, yPos + 5);

        // Mover Y según altura real
        yPos += altoCelda + 5;

        // Siempre agregar pie de página en la última página
        agregarPieDePagina(index === competencias.length - 1);
      });
    }

    // === NUEVA PÁGINA DE RESULTADO FINAL ===
    const puntajeFinal = calcularPuntajeFinal(objetivos, competencias);
    const evaluacion = obtenerMensajeDesempeno(puntajeFinal);
    const colorPuntaje = obtenerColorPuntaje(puntajeFinal);

    pdf.addPage();
    paginaActual++;

    // ===== LOGOS SUPERIORES =====

    // Altura del logo
    const logoAltura = 20;

    // Logo izquierda
    pdf.addImage(
      "/static/assets/img/logo/logo_pngdl.png",  // ruta
      "PNG",
      55,                // margen izquierdo
      10,                // distancia desde arriba
      25,                // ancho
      logoAltura         // alto
    );

    // ===== Nombre debajo del logo =====
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(9);
    pdf.setTextColor(60, 60, 60);

    // Centrado respecto al logo
    pdf.text(
      "SOCIEDAD AGRÍCOLA DON LUIS S.A.",  // cambia por tu empresa
      55 + (25 / 2),   // centro del logo
      10 + logoAltura + 6,  // un poco debajo del logo
      { align: "center" }
    );


    // Logo derecha
    pdf.addImage(
      "/static/assets/img/logo/Logoacv.webp",  // ruta
      "WEBP",
      pdfWidth - 90,     // margen derecho
      10,
      40,
      logoAltura
    );

    // ===== Nombre debajo del logo derecho =====
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(9);
    pdf.setTextColor(60, 60, 60);

    pdf.text(
      "AGROINDUSTRIA CAMPO VERDE S.A.C.",  // cambia por lo que quieras
      (pdfWidth - 90) + (40 / 2),   // centro del logo derecho
      10 + logoAltura + 6,
      { align: "center" }
    );

    //Linea divisoria
    pdf.setDrawColor(220, 220, 220);
    pdf.setLineWidth(0.5);
    pdf.line(30, 40, pdfWidth - 30, 40);


    // ===== CONFIGURACIÓN CÍRCULO =====
    const centerX = pdfWidth / 2;
    const centerY = pdfHeight / 2 - 35;
    const radius = 28;

    // ===== CÍRCULO BASE (más definido, menos lavado) =====
    pdf.setDrawColor(210, 210, 210);
    pdf.setLineWidth(5);
    pdf.circle(centerX, centerY, radius);

    // ===== CÍRCULO PROGRESO =====
    const porcentaje = puntajeFinal > 120 ? 120 : puntajeFinal;
    const angulo = (porcentaje / 120) * 360;

    pdf.setDrawColor(...colorPuntaje);
    pdf.setLineWidth(5);

    // Simulación progreso
    for (let i = 0; i < angulo; i += 2) {
      const rad = (i - 90) * Math.PI / 180;
      const x1 = centerX + radius * Math.cos(rad);
      const y1 = centerY + radius * Math.sin(rad);

      const x2 = centerX + (radius - 5) * Math.cos(rad);
      const y2 = centerY + (radius - 5) * Math.sin(rad);

      pdf.line(x1, y1, x2, y2);
    }

    // ===== PUNTAJE =====
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(34);
    pdf.setTextColor(...colorPuntaje);

    pdf.text(`${puntajeFinal}%`, centerX, centerY + 5, {
      align: "center"
    });

    // ===== TÍTULO DESEMPEÑO =====
    let yTexto = centerY + 45;

    pdf.setFontSize(17);
    pdf.setTextColor(40, 40, 40); // más oscuro
    pdf.text(evaluacion.titulo, pdfWidth / 2, yTexto, {
      align: "center"
    });

    // ===== MENSAJE DESCRIPTIVO =====
    yTexto += 12;

    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(11);
    pdf.setTextColor(70, 70, 70); // mejor contraste

    const mensajeSplit = pdf.splitTextToSize(
      evaluacion.mensaje,
      pdfWidth - 100
    );

    pdf.text(mensajeSplit, pdfWidth / 2, yTexto, {
      align: "center",
      maxWidth: pdfWidth - 100
    });

    // ===== TEXTO FINAL PERSONALIZADO =====
    yTexto += 18;

    pdf.setFontSize(10);
    pdf.setTextColor(60, 60, 60);

    pdf.text(
      `El colaborador ${datosEvaluado.nombre_evaluado} obtuvo un puntaje final de ${puntajeFinal}% en el periodo ${datosEvaluado.periodo}.`,
      pdfWidth / 2,
      yTexto,
      { align: "center", maxWidth: pdfWidth - 80 }
    );

    // ===== LEYENDA NIVELES =====
    const niveles = [
      { texto: "En Desarrollo (<100%)", color: [220, 53, 69] },
      { texto: "Cumple (100%)", color: [0, 123, 255] },
      { texto: "Excede (101–110%)", color: [255, 193, 7] },
      { texto: "Modelo (>111%)", color: [40, 167, 69] }
    ];

    const margenX = 30;
    const anchoDisponible = pdfWidth - (margenX * 2);
    const anchoBloque = anchoDisponible / niveles.length;
    const altoBloque = 16; // un poco más alto para texto en 2 líneas

    let yBarra = pdfHeight - 80;

    niveles.forEach((nivel, index) => {

      let x = margenX + (index * anchoBloque);

      // Fondo color
      pdf.setFillColor(...nivel.color);
      pdf.rect(x, yBarra, anchoBloque, altoBloque, "F");

      // Configuración texto
      pdf.setFontSize(7);
      pdf.setTextColor(255, 255, 255);

      // Ajustar texto al ancho del bloque (con pequeño margen interno)
      const textoAjustado = pdf.splitTextToSize(
        nivel.texto,
        anchoBloque - 6
      );

      // Centrar verticalmente dependiendo de líneas
      const alturaTexto = textoAjustado.length * 4;
      const yTexto = yBarra + (altoBloque / 2) - (alturaTexto / 2) + 3;

      pdf.text(
        textoAjustado,
        x + (anchoBloque / 2),
        yTexto,
        { align: "center" }
      );
    });

    // ===== PIE DE PÁGINA =====
    agregarPieDePagina();

    const nombrePDF = `Fase_Final_ID${
      datosEvaluado.id_evaluacion
    }_${datosEvaluado.nombre_evaluado.replace(/\s+/g, "_")}_${
      datosEvaluado.periodo
    }.pdf`;

    const pdfBlob = pdf.output("blob");

    pdf.save(nombrePDF);

    Swal.fire({
      icon: "success",
      title: "PDF Final Generado",
      text: `El PDF "${nombrePDF}" se generó correctamente. ¿Deseas enviarlo por correo?`,
      showCancelButton: true,
      confirmButtonText: "Enviar por correo",
    }).then((result) => {
      if (result.isConfirmed) {
        enviarPDFPorCorreoFinal(datosEvaluado, nombrePDF, pdfBlob);
      }
    });
  } catch (error) {
    console.error("Error al generar PDF Final:", error);
    Swal.fire({
      icon: "error",
      title: "Error",
      text: error.message,
    });
  }
}

function enviarPDFPorCorreoFinal(datosEvaluado, nombrePDF, pdfBlob) {
  Swal.fire({
    title: "Enviar evaluación final por correo",
    html: `
      <form id="emailFormFinal">
        <label>Correo del evaluado:</label>
        <input id="destinatario_final" type="email" class="form-control" value="${datosEvaluado.email}" required>

        <label>Asunto:</label>
        <input id="asunto_final" type="text" class="form-control"
        value="Fase Final - Evaluación de desempeño ${datosEvaluado.periodo}" required>

        <label>Mensaje:</label>
        <textarea id="mensaje_final" class="form-control" rows="4" required>
Estimado/a ${datosEvaluado.nombre_evaluado},

Adjunto encontrará el documento correspondiente a la FASE FINAL de su evaluación de desempeño del período ${datosEvaluado.periodo}.

Saludos cordiales,
Departamento de Recursos Humanos
        </textarea>
      </form>
    `,
    showCancelButton: true,
    confirmButtonText: "Enviar",
    preConfirm: () => {
      const f = document.getElementById("emailFormFinal");
      if (!f.checkValidity()) {
        f.reportValidity();
        return false;
      }
      return {
        correo: document.getElementById("destinatario_final").value,
        asunto: document.getElementById("asunto_final").value,
        mensaje: document.getElementById("mensaje_final").value,
      };
    },
  }).then((res) => {
    if (!res.isConfirmed) return;

    const datos = res.value;

    const formData = new FormData();
    formData.append("destinatario", datos.correo);
    formData.append("asunto", datos.asunto);
    formData.append("mensaje", datos.mensaje);
    formData.append("archivo_pdf", pdfBlob, nombrePDF);
    formData.append("id_evaluacion", datosEvaluado.id_evaluacion);

    Swal.fire({
      title: "Enviando correo...",
      allowOutsideClick: false,
      didOpen: () => Swal.showLoading(),
    });

    $.ajax({
      url: "/rrhh/enviar_evaluacion_correo/",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            icon: "success",
            title: "Correo enviado",
            text: `El archivo final fue enviado a ${datos.correo}`,
          });
        } else {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: response.message,
          });
        }
      },
      error: function (xhr) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudo enviar el correo.",
        });
      },
    });
  });
}
