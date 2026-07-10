/*###################################################*/
/* TABLA DE COMPETENCIAS */
/*###################################################*/
function inicializarTablaEvaluaciones_competencia() {
  var table = $("#tablaEvaluaciones_competencias").DataTable({
    // Configuración de botones
    dom: "Bfrtip",
    buttons: [
      {
        // Botón de recarga
        text: '<i class="fas fa-sync-alt"></i>',
        className: "btn-sm btn-secondary",
        action: function (e, dt, node, config) {
          // Añadir animación de giro
          $(node).find("i").addClass("fa-spin");

          // Recargar la tabla
          dt.ajax.reload(function () {
            // Callback después de la recarga
            setTimeout(() => {
              $(node).find("i").removeClass("fa-spin");
            }, 1000);
          });
        },
      },
      {
        // Botón para añadir competencias
        text: '<i class="fas fa-plus-circle"></i> Añadir Competencias',
        className: "btn-sm btn-primary ",
        action: function (e, dt, node, config) {
          // Resetear el modal antes de abrirlo
          resetModalCompetencias();
          // Cargar los evaluados en el select
          cargarEvaluados();
          // Abrir el modal de competencias
          $("#modalCompetencias").modal("show");
        },
      },
    ],

    scrollX: false,
    scrollY: "250px",
    scrollCollapse: false,
    autoWidth: false,
    pageLength: 9,
    responsive: true,
    serverSide: false,
    order: [[0, "desc"]],
    searching: false,

    // Idioma
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json",
    },

    // Ajax para obtener datos
    ajax: {
      url: "/rrhh/resumen_competencias/",
      type: "GET",
      dataSrc: "data",
    },

    // Configuración de estilos responsivos
    columnDefs: [
      {
        targets: "_all",
        className: "text-nowrap",
        render: function (data, type, row, meta) {
          if (type === "display" && data !== null) {
            return `<span class="table-text">${data}</span>`;
          }
          return data;
        },
      },
    ],

    // Definición de columnas
    columns: [
      {
        title: "ID Evaluación",
        data: "id",
        visible: false,
      },
      {
        title: "Evaluado",
        data: "evaluado",
        render: function (data, type, row) {
          if (type === "display") {
            const iniciales = data
              .split(" ")
              .map((n) => n.charAt(0))
              .join("")
              .toUpperCase();

            const stringToGradient = (str) => {
              let hash = 0;
              for (let i = 0; i < str.length; i++) {
                hash = str.charCodeAt(i) + ((hash << 2) - hash);
              }
              const h1 = Math.abs(hash) % 360;
              const h2 = (h1 + 40) % 360;
              return `linear-gradient(135deg, hsl(${h1}, 70%, 60%) 0%, hsl(${h2}, 70%, 45%) 100%)`;
            };

            const backgroundGradient = stringToGradient(data);

            return `
                        <div class="d-flex align-items-center">
                            <div class="modern-avatar small-avatar" 
                                 style="background: ${backgroundGradient};">
                                <span class="initials small-text">${iniciales}</span>
                                <div class="avatar-status"></div>
                            </div>
                            <div class="user-info">
                                <div class="user-name small-text">${data}</div>
                                <div class="user-role smaller-text">${row.nombre_area}</div>
                            </div>
                        </div>`;
          }
          return data;
        },
      },
      {
        title: "Evaluador",
        data: "evaluador",
        render: function (data, type, row) {
          if (type === "display") {
            const iniciales = data
              .split(" ")
              .map((n) => n.charAt(0))
              .join("")
              .toUpperCase();

            const stringToGradient = (str) => {
              let hash = 0;
              for (let i = 0; i < str.length; i++) {
                hash = str.charCodeAt(i) + ((hash << 2) - hash);
              }
              const h1 = Math.abs(hash) % 360;
              const h2 = (h1 + 40) % 360;
              return `linear-gradient(135deg, hsl(${h1}, 70%, 60%) 0%, hsl(${h2}, 70%, 45%) 100%)`;
            };

            const backgroundGradient = stringToGradient(data);

            return `
                        <div class="d-flex align-items-center">
                            <div class="modern-avatar small-avatar" 
                                 style="background: ${backgroundGradient};">
                                <span class="initials small-text">${iniciales}</span>
                                <div class="avatar-status"></div>
                            </div>
                            <div class="user-info">
                                <div class="user-name small-text">${data}</div>
                            </div>
                        </div>`;
          }
          return data;
        },
      },
      {
        title: "Periodo",
        data: "periodo",
      },
      {
        title: "Área",
        data: "nombre_area",
      },
      {
        title: "Promedio",
        data: "promedio_porcentaje",
        render: function (data, type, row) {
          if (type === "display") {
            return `${data}%`;
          }
          return data;
        },
      },
    ],

    initComplete: function (settings, json) {
      // Recalcular columnas después de inicializar
      table.columns.adjust().responsive.recalc();

      // Forzar un recálculo adicional después de un breve retraso
      setTimeout(function () {
        table.columns.adjust().responsive.recalc();
      }, 500);
    },

    // Agregar createdRow para el doble click
    createdRow: function (row, data, dataIndex) {
      $(row).css("cursor", "pointer"); // Cambia el cursor a pointer
      $(row).on("dblclick", function () {
        competenciaDetalles(data.id);
      });
    },

    destroy: true,
  });

  $('a[data-toggle="tab"]').on("shown.bs.tab", function () {
    table.columns.adjust().responsive.recalc();
  });
}

/*###################################################*/
/* TABLA DE DETALLES DE COMPETENCIAS */
/*###################################################*/

function inicializarTablaDetallesCompetencias(id_evaluacion) {
  $("#Modal_Detalles_Objetivos").data("id-evaluacion", id_evaluacion);

  // Inicializar la tabla de detalles de competencias
  var table = $("#tablaDetallesCompetencias").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        text: '<i class="fas fa-sync-alt"></i>',
        className: "btn-sm btn-secondary",
        action: function (e, dt, node, config) {
          $(node).find("i").addClass("fa-spin");
          dt.ajax.reload(function () {
            setTimeout(() => {
              $(node).find("i").removeClass("fa-spin");
            }, 1000);
          });
        },
      },

      {
        text: '<i class="fas fa-plus-circle"></i> Agregar Competencia',
        className: "btn btn-primary btn-nuevo-objetivo ms-3",
        action: function (e, dt, node, config) {
          agregarCompetenciaDesdeObjetivos();
        },
      },
    ],

    scrollX: false,
    scrollY: "250px",
    scrollCollapse: false,
    autoWidth: false,
    responsive: true,
    serverSide: false,

    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json",
    },

    ajax: {
      url: "/almacen/detalles_competencias/",
      type: "GET",
      dataSrc: function (json) {
        return json.data.filter((item) => item.id_evaluacion === id_evaluacion);
      },
    },

    columns: [
      {
        title: "ID",
        data: "id",
        visible: false,
      },
      {
        title: "Evaluado",
        data: "nombre_evaluado",
        render: function (data, type, row) {
          if (type === "display") {
            // Obtenemos las iniciales del nombre completo
            const nombreCompleto =
              row.nombre_evaluado + " " + row.apellido_evaluado.split(" ")[0];
            const iniciales = nombreCompleto
              .split(" ")
              .map((n) => n.charAt(0))
              .join("")
              .toUpperCase();

            // Función para generar el gradiente
            const stringToGradient = (str) => {
              let hash = 0;
              for (let i = 0; i < str.length; i++) {
                hash = str.charCodeAt(i) + ((hash << 2) - hash);
              }
              const h1 = Math.abs(hash) % 360;
              const h2 = (h1 + 40) % 360;
              return `linear-gradient(135deg, hsl(${h1}, 70%, 60%) 0%, hsl(${h2}, 70%, 45%) 100%)`;
            };

            const backgroundGradient = stringToGradient(nombreCompleto);

            return `
                        <div class="d-flex align-items-center">
                            <div class="modern-avatar small-avatar" 
                                 style="background: ${backgroundGradient};">
                                <span class="initials small-text">${iniciales}</span>
                                <div class="avatar-status"></div>
                            </div>
                            <div class="user-info">
                                <div class="user-name small-text">${nombreCompleto}</div>
                                <div class="user-role smaller-text">${row.nombre_area}</div>
                            </div>
                        </div>`;
          }
          return data;
        },
      },
      {
        title: "Competencia",
        data: "nombre_competencia",
      },
      {
        title: "Meta",
        data: "meta",
      },
      {
        title: "Comentarios",
        data: "comentarios",
      },
      {
        title: "Estado",
        data: null,
        render: function (data, type, row) {
          if (row.no_cumple === 1) return "No Cumple";
          if (row.cumple === 1) return "Cumple";
          if (row.excede === 1) return "Excede";
          if (row.sobresaliente === 1) return "Sobresaliente";
          return "Sin evaluar";
        },
      },
      {
        title: "Acciones",
        data: null,
        orderable: false,
        render: function (data, type, row) {
          return `
                  <div class="btn-group btn-group-sm" role="group">
                      <button type="button" class="btn btn-warning btn-sm" onclick="editarCompetencia(${row.id})">
                          <i class="fas fa-edit"></i>
                      </button>
                      <button type="button" class="btn btn-danger btn-sm" onclick="eliminarCompetencia(${row.id})">
                          <i class="fas fa-trash"></i>
                      </button>
                  </div>`;
        },
      },
    ],

    initComplete: function (settings, json) {
      setTimeout(function () {
        table.columns.adjust();
      }, 100);
    },

    destroy: true,
  });

  // Ajustar cuando el modal se está mostrando
  $("#Modal_Detalles_Competencias").on("show.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });

  // Ajustar cuando el modal ya está visible
  $("#Modal_Detalles_Competencias").on("shown.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });

  return table;
}

// Función para abrir el modal de agregar competencia en detalle
function abrirModalAgregarCompetenciaDetalle(idEvaluacion, nombreEvaluado) {
  if (!idEvaluacion) {
    /* idEvaluacion = $("#Modal_Detalles_Objetivos").data("id-evaluacion"); */

    if (!idEvaluacion) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo obtener el ID de evaluación",
        confirmButtonColor: "#dc3545",
      });
      return;
    }
  }
  // Establecer el nombre y ID del evaluado
  $("#modalAgregarCompetenciaDetalle").modal("show");
  $("#evaluadoNombreDetalle").val(nombreEvaluado);
  $("#evaluadoIdDetalle").val(idEvaluacion);

  // Resetear el formulario
  $("#form-competencia-detalle")[0].reset();

  // Desmarcar todos los radio buttons
  $('input[name="nivel-detalle"]').prop("checked", false);
  $('input[name="nivel-detalle"]').parent().removeClass("active");

  // Verificar si ya existen competencias para este evaluado
  $.ajax({
    url: "/almacen/detalles_competencias/",
    type: "GET",
    success: function (response) {
      if (response.status === "success") {
        // Filtrar las competencias del evaluado
        const competenciasExistentes = response.data.filter(
          (item) => item.id_evaluacion === idEvaluacion
        );

        // Obtener los tipos de competencia ya registrados
        const tiposRegistrados = competenciasExistentes.map(
          (item) => item.id_tipo_competencia
        );

        // Deshabilitar las opciones ya registradas en el select
        $("#competencia-tipo-detalle option").each(function () {
          const tipoId = parseInt($(this).val());
          if (tiposRegistrados.includes(tipoId)) {
            $(this).prop("disabled", true);
            $(this).text($(this).text() + " (Ya registrada)");
          } else {
            $(this).prop("disabled", false);
            $(this).text($(this).text().replace(" (Ya registrada)", ""));
          }
        });

        // Seleccionar la primera opción disponible
        const primeraDisponible = $(
          "#competencia-tipo-detalle option:not(:disabled)"
        ).first();
        if (primeraDisponible.length) {
          $("#competencia-tipo-detalle").val(primeraDisponible.val());
        }
      }

      // Abrir el modal
      $("#modalAgregarCompetenciaDetalle").modal("show");
    },
    error: function (xhr, status, error) {
      // Abrir el modal de todos modos
      $("#modalAgregarCompetenciaDetalle").modal("show");
    },
  });
}

// Función para manejar el doble click
function competenciaDetalles(id_evaluacion) {
  $("#Modal_Detalles_Competencias").modal("show");
  inicializarTablaDetallesCompetencias(id_evaluacion);

  // Guardar el id_evaluacion para usarlo en el botón de agregar competencia
  $("#Modal_Detalles_Competencias").data("id-evaluacion", id_evaluacion);
}

// Función para obtener las competencias seleccionadas
function obtenerCompetenciasSeleccionadas() {
  const competencias = [];
  const checkboxes = document.querySelectorAll(".custom-control-input:checked");

  checkboxes.forEach((checkbox) => {
    competencias.push({
      id: checkbox.id,
      nombre: checkbox.nextElementSibling.textContent.trim(),
    });
  });

  return competencias;
}

// Función para guardar una competencia desde el detalle
function guardarCompetenciaDetalle() {
  // Obtener el ID de evaluación
  const idEvaluacion = $("#evaluadoIdDetalle").val();

  // Validar que exista un ID de evaluación
  if (!idEvaluacion) {
    Swal.fire({
      icon: "warning",
      title: "Atención",
      text: "No se ha seleccionado un evaluado",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  // Obtener los datos del formulario
  // Comprobar varios posibles selectores para el tipo de competencia
  let tipoCompetencia = $("#competencia-tipo-detalle").val();

  // Si no se encuentra, intentar con otros selectores comunes
  if (!tipoCompetencia) {
    tipoCompetencia =
      $(".competencia-tipo").val() ||
      $("#tipo-competencia").val() ||
      $("select[name='tipo_competencia']").val();
  }

  // Debug: mostrar en consola
  console.log("Tipo de competencia seleccionado:", tipoCompetencia);
  console.log("Elementos del select:", {
    "competencia-tipo-detalle": $("#competencia-tipo-detalle").length
      ? $("#competencia-tipo-detalle").val()
      : "no existe",
    "competencia-tipo": $(".competencia-tipo").length
      ? $(".competencia-tipo").val()
      : "no existe",
    "tipo-competencia": $("#tipo-competencia").length
      ? $("#tipo-competencia").val()
      : "no existe",
    "select tipo_competencia": $("select[name='tipo_competencia']").length
      ? $("select[name='tipo_competencia']").val()
      : "no existe",
  });

  // Validar que se haya seleccionado un tipo de competencia
  if (!tipoCompetencia) {
    Swal.fire({
      icon: "warning",
      title: "Atención",
      text: "Debe seleccionar un tipo de competencia",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  const meta = $("#competencia-meta-detalle").val().trim();
  const fechaInicio = $("#competencia-fecha-inicio-detalle").val();
  const fechaFin = $("#competencia-fecha-fin-detalle").val();
  const comentarios = $("#competencia-comentarios-detalle").val().trim();

  // Obtener el nivel seleccionado
  const nivelSeleccionado = $('input[name="nivel-detalle"]:checked').val();

  // Validar campos requeridos
  if (!meta) {
    Swal.fire({
      icon: "warning",
      title: "Atención",
      text: "Debe ingresar la meta para la competencia",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  if (!fechaInicio) {
    Swal.fire({
      icon: "warning",
      title: "Atención",
      text: "Debe seleccionar la fecha de inicio",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  if (!fechaFin) {
    Swal.fire({
      icon: "warning",
      title: "Atención",
      text: "Debe seleccionar la fecha de fin",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  // Crear objeto con los valores de cumplimiento (todos en 0 si no hay selección)
  const nivelesCumplimiento = {
    no_cumple: nivelSeleccionado === "no_cumple" ? 1 : 0,
    cumple: nivelSeleccionado === "cumple" ? 1 : 0,
    excede: nivelSeleccionado === "excede" ? 1 : 0,
    sobresaliente: nivelSeleccionado === "sobresaliente" ? 1 : 0,
  };

  // Crear objeto con los datos de la competencia
  const competencia = {
    id_tipo_competencia: tipoCompetencia, // Asegurarse de que este valor sea correcto
    meta: meta,
    fecha_inicio: fechaInicio,
    fecha_fin: fechaFin,
    comentarios: comentarios || "",
    ...nivelesCumplimiento,
  };

  // Debug para verificar datos que se enviarán
  console.log("Datos de competencia a enviar:", competencia);

  // Crear el objeto final con el id_evaluacion y el array de competencias
  const datosEnvio = {
    id_evaluacion: idEvaluacion,
    competencias: [competencia],
  };

  // Mostrar loader
  Swal.fire({
    title: "Guardando competencia",
    text: "Por favor espere...",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Enviar datos al servidor
  $.ajax({
    url: "/almacen/detalles_competencias/",
    type: "POST",
    data: JSON.stringify(datosEnvio),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: function (response) {
      if (response.status === "success") {
        Swal.fire({
          icon: "success",
          title: "¡Éxito!",
          text: "La competencia se ha guardado correctamente",
          confirmButtonColor: "#28a745",
        }).then(() => {
          // Cerrar el modal
          $("#modalAgregarCompetenciaDetalle").modal("hide");

          // Recargar la tabla de detalles
          $("#tablaDetallesCompetencias").DataTable().ajax.reload();
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text:
            response.message || "Ocurrió un error al guardar la competencia",
          confirmButtonColor: "#dc3545",
        });
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al guardar competencia:", xhr.responseText);
      let mensajeError = "Ocurrió un error al conectar con el servidor";

      try {
        if (xhr.responseText) {
          const respuesta = JSON.parse(xhr.responseText);
          mensajeError = respuesta.message || mensajeError;
        }
      } catch (e) {
        console.error("Error al parsear respuesta:", e);
      }

      Swal.fire({
        icon: "error",
        title: "Error",
        text: mensajeError,
        confirmButtonColor: "#dc3545",
      });
    },
  });
}

function recopilarDatosCompetencias() {
  // Obtener el id_evaluacion seleccionado
  const id_evaluacion = $("#evaluadoSelect").val();

  // Validar que se haya seleccionado un evaluado
  if (!id_evaluacion) {
    Swal.fire({
      icon: "warning",
      title: "Atención",
      text: "Debe seleccionar un evaluado",
      confirmButtonColor: "#ffc107",
    });
    return null;
  }

  // Array para almacenar las competencias
  const competencias = [];
  let hayErrores = false;

  // Recorrer todas las competencias en el contenedor
  $(".competencia").each(function () {
    const competenciaDiv = $(this);
    const competenciaForm = competenciaDiv.find("form");
    const competenciaId = competenciaDiv.attr("id").split("-")[1];

    // Obtener el tipo de competencia del select
    const tipoCompetencia = competenciaForm.find(".competencia-tipo").val();

    // Obtener la meta
    const meta = competenciaForm.find(".competencia-meta").val().trim();

    // Obtener las fechas
    const fechaInicio = competenciaForm.find(".competencia-fecha-inicio").val();
    const fechaFin = competenciaForm.find(".competencia-fecha-fin").val();

    // Obtener los comentarios
    const comentarios = competenciaForm
      .find(".competencia-comentarios")
      .val()
      .trim();

    // Obtener el nivel seleccionado (ahora opcional)
    const nivelSeleccionadoInput = competenciaForm.find(
      `input[name="nivel-${competenciaId}"]:checked`
    );
    const nivelSeleccionado =
      nivelSeleccionadoInput.length > 0 ? nivelSeleccionadoInput.val() : null;

    // Validar campos requeridos (solo meta y fechas)
    if (!meta) {
      Swal.fire({
        icon: "warning",
        title: "Atención",
        text: `Debe ingresar la meta para la Competencia ${competenciaId}`,
        confirmButtonColor: "#ffc107",
      });
      hayErrores = true;
      return false; // Salir del bucle each
    }

    if (!fechaInicio) {
      Swal.fire({
        icon: "warning",
        title: "Atención",
        text: `Debe seleccionar la fecha de inicio para la Competencia ${competenciaId}`,
        confirmButtonColor: "#ffc107",
      });
      hayErrores = true;
      return false; // Salir del bucle each
    }

    if (!fechaFin) {
      Swal.fire({
        icon: "warning",
        title: "Atención",
        text: `Debe seleccionar la fecha de fin para la Competencia ${competenciaId}`,
        confirmButtonColor: "#ffc107",
      });
      hayErrores = true;
      return false; // Salir del bucle each
    }

    // Crear objeto con los valores de cumplimiento (todos en 0 si no hay selección)
    const nivelesCumplimiento = {
      no_cumple: nivelSeleccionado === "no_cumple" ? 1 : 0,
      cumple: nivelSeleccionado === "cumple" ? 1 : 0,
      excede: nivelSeleccionado === "excede" ? 1 : 0,
      sobresaliente: nivelSeleccionado === "sobresaliente" ? 1 : 0,
    };

    // Crear objeto con los datos de la competencia
    const competencia = {
      id_tipo_competencia: tipoCompetencia,
      meta: meta,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      comentarios: comentarios || "",
      ...nivelesCumplimiento,
    };

    competencias.push(competencia);
  });

  // Si hay errores, detener el proceso
  if (hayErrores) {
    return null;
  }

  // Verificar si se agregaron competencias después de validar

  if (competencias.length === 0) {
    Swal.fire({
      icon: "warning",
      title: "Atención",
      text: "Debe agregar al menos una competencia",
      confirmButtonColor: "#ffc107",
    });
    return null;
  }

  // Crear el objeto final con el id_evaluacion y el array de competencias
  const datosEnvio = {
    id_evaluacion: id_evaluacion,
    competencias: competencias,
  };

  return datosEnvio;
}

function guardarCompetencias() {
  // Validar todas las competencias
  const todasValidadas = validarTodasLasCompetencias();

  if (!todasValidadas) {
    Swal.fire({
      icon: "error",
      title: "Fechas inválidas",
      text: "Por favor corrija las fechas en todas las competencias antes de guardar",
    });
    return;
  }

  // Recopilar los datos de las competencias
  const datos = recopilarDatosCompetencias();

  // Verificar si se obtuvieron datos válidos
  if (!datos) {
    // Si no hay datos válidos, la función recopilarDatosCompetencias ya muestra un mensaje
    return;
  }

  // Obtener el ID del evaluado seleccionado
  const evaluadoId = datos.id_evaluacion;

  // Primero verificar si ya existen competencias para este evaluado
  $.ajax({
    url: "/almacen/detalles_competencias/",
    type: "GET",
    success: function (response) {
      // Filtrar las competencias del evaluado seleccionado
      const competenciasExistentes = response.data.filter(
        (item) => item.id_evaluacion == evaluadoId
      );

      if (competenciasExistentes.length > 0) {
        // Ya existen competencias para este evaluado
        const nombreEvaluado = $("#evaluadoSelect option:selected").text();

        Swal.fire({
          icon: "warning",
          title: "Competencias existentes",
          text: `Ya existen competencias registradas para ${nombreEvaluado}. Por favor, edite las existentes o elimínelas antes de agregar nuevas.`,
          confirmButtonColor: "#ffc107",
        });
        return;
      }

      // Si no existen competencias, proceder con el guardado
      enviarCompetencias(datos);
    },
    error: function (xhr, status, error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Ocurrió un error al verificar competencias existentes",
        confirmButtonColor: "#dc3545",
      });
    },
  });
}

// Función para enviar las competencias al servidor
function enviarCompetencias(datos) {
  // Mostrar loader
  Swal.fire({
    title: "Guardando competencias",
    text: "Por favor espere...",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Enviar datos al servidor
  $.ajax({
    url: "/almacen/detalles_competencias/",
    type: "POST",
    data: JSON.stringify(datos),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: function (response) {
      if (response.status === "success") {
        Swal.fire({
          icon: "success",
          title: "¡Éxito!",
          text: "Las competencias se han guardado correctamente",
          confirmButtonColor: "#28a745",
        }).then(() => {
          // Cerrar el modal
          $("#modalCompetencias").modal("hide");

          // Recargar la tabla de evaluaciones
          $("#tablaEvaluaciones_competencias").DataTable().ajax.reload();

          // Resetear el formulario
          resetModalCompetencias();

          // Obtener información detallada de objetivos y competencias
          consultarDetallesEvaluacion(datos.id_evaluacion);
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text:
            response.message || "Ocurrió un error al guardar las competencias",
          confirmButtonColor: "#dc3545",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Ocurrió un error al conectar con el servidor",
        confirmButtonColor: "#dc3545",
      });
    },
  });
}

function consultarDetallesEvaluacion(id_evaluacion) {
  // Primero consultamos los objetivos
  $.ajax({
    url: "/almacen/detalles_objetivos/",
    type: "GET",
    dataType: "json",
    success: function (responseObjetivos) {
      // La API de objetivos devuelve la estructura con data.0, data.1, etc.
      if (!responseObjetivos.data) {
        return;
      }

      // Filtrar objetivos por id_evaluacion
      const objetivosFiltrados = responseObjetivos.data.filter(
        (obj) => obj.id_evaluacion == id_evaluacion
      );

      // Luego consultamos las competencias
      $.ajax({
        url: "/almacen/detalles_competencias/",
        type: "GET",
        dataType: "json",
        success: function (responseCompetencias) {
          // Filtrar competencias por id_evaluacion
          const competenciasFiltradas = responseCompetencias.data.filter(
            (comp) => comp.id_evaluacion == id_evaluacion
          );

          // Mostrar resumen completo
          console.log("RESUMEN COMPLETO DE EVALUACIÓN:", {
            id_evaluacion: id_evaluacion,
            objetivos: objetivosFiltrados,
            competencias: competenciasFiltradas,
            total_objetivos: objetivosFiltrados.length,
            total_competencias: competenciasFiltradas.length,
          });

          // Mostrar mensaje informativo con opción para generar PDF
          Swal.fire({
            icon: "info",
            title: "Detalles consultados",
            text: `Se han consultado los detalles para la evaluación ID ${id_evaluacion}: ${objetivosFiltrados.length} objetivos y ${competenciasFiltradas.length} competencias.`,
            showCancelButton: true,
            confirmButtonText: "Generar PDF",
            cancelButtonText: "Cerrar",
            confirmButtonColor: "#3085d6",
          }).then((result) => {
            if (result.isConfirmed) {
              generarPDFEvaluacion(id_evaluacion);
            }
          });
        },
        error: function (error) {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Ocurrió un error al obtener los detalles de las competencias",
            confirmButtonColor: "#dc3545",
          });
        },
      });
    },
    error: function (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Ocurrió un error al obtener los detalles de los objetivos",
        confirmButtonColor: "#dc3545",
      });
      console.error("Error al obtener datos de objetivos:", error);
    },
  });
}

function generarPDFEvaluacion(id_evaluacion) {
  // Mostrar loading mientras se genera el PDF
  Swal.fire({
    title: "Generando PDF",
    text: "Recopilando información, por favor espere...",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Primero, consultamos la API de evaluaciones
  $.ajax({
    url: "/rrhh/rrhh_evaluaciones/",
    type: "GET",
    dataType: "json",
    success: function (responseEvaluaciones) {
      if (!responseEvaluaciones.data) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudieron obtener los datos de evaluaciones",
        });
        return;
      }

      // Filtrar la evaluación específica por id_evaluacion
      const evaluacionActual = responseEvaluaciones.data.find(
        (eval) => eval.id == id_evaluacion
      );

      if (!evaluacionActual) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se encontró la evaluación específica",
        });
        return;
      }

      // Extraer id_evaluador e id_evaluado
      const id_evaluador = evaluacionActual.id_evaluador;
      const id_evaluado = evaluacionActual.id_evaluado;
      const comentario_objetivo = evaluacionActual.comentarios_objetivosgeneral;
      const comentario_competencia = evaluacionActual.comentarios_competencias_general;

      // Consultar la API de usuarios para obtener los DNIs
      $.ajax({
        url: "/rrhh/usuarios/",
        type: "GET",
        dataType: "json",
        success: function (responseUsuarios) {
          if (!responseUsuarios.data) {
            console.error("No se pudieron obtener los datos de usuarios");
            return;
          }

          // Buscar el evaluador y el evaluado en la lista de usuarios
          const evaluador = responseUsuarios.data.find(
            (user) => user.id == id_evaluador
          );
          const evaluado = responseUsuarios.data.find(
            (user) => user.id == id_evaluado
          );

          // Variables para almacenar los datos personales
          let datosPersonalEvaluado = null;
          let datosPersonalEvaluador = null;

          // Función para continuar con el flujo después de obtener los datos personales
          const continuarFlujo = () => {
            // Consultamos los objetivos
            $.ajax({
              url: "/almacen/detalles_objetivos/",
              type: "GET",
              dataType: "json",
              success: function (responseObjetivos) {
                if (!responseObjetivos.data) {
                  Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: "No se pudieron obtener los datos de objetivos",
                  });
                  return;
                }

                const objetivos = responseObjetivos.data.filter(
                  (obj) => obj.id_evaluacion == id_evaluacion
                );

                // Consultamos las competencias
                $.ajax({
                  url: "/almacen/detalles_competencias/",
                  type: "GET",
                  dataType: "json",
                  success: function (responseCompetencias) {
                    if (!responseCompetencias.data) {
                      Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: "No se pudieron obtener los datos de competencias",
                      });
                      return;
                    }

                    const competencias = responseCompetencias.data.filter(
                      (comp) => comp.id_evaluacion == id_evaluacion
                    );

                    if (objetivos.length === 0 && competencias.length === 0) {
                      Swal.fire({
                        icon: "warning",
                        title: "Sin datos",
                        text: "No se encontró información para esta evaluación",
                      });
                      return;
                    }

                    // Crear objeto con todos los datos necesarios
                    const datosCompletos = {
                      ...objetivos[0],
                      datosPersonalEvaluado: datosPersonalEvaluado,
                      datosPersonalEvaluador: datosPersonalEvaluador,
                      comentario_objetivo: comentario_objetivo,
                      comentario_competencia: comentario_competencia,
                      periodo: evaluacionActual.periodo,
                      fecha_evaluacion: evaluacionActual.fecha_evaluacion,
                    };

                    // Crear el PDF con todos los datos
                    crearContenidoPDF(datosCompletos, objetivos, competencias);
                  },
                  error: function (error) {
                    Swal.fire({
                      icon: "error",
                      title: "Error",
                      text: "Error al obtener datos de competencias",
                    });
                  },
                });
              },
              error: function (error) {
                Swal.fire({
                  icon: "error",
                  title: "Error",
                  text: "Error al obtener datos de objetivos",
                });
              },
            });
          };

          // Contador para controlar cuándo se han completado ambas consultas
          let consultasCompletadas = 0;

          // Consultar datos personales del evaluado
          if (evaluado && evaluado.dni) {
            $.ajax({
              url: `/rrhh/datos_personal_por_dni/?dni=${evaluado.dni}`,
              type: "GET",
              success: function (response) {
                if (response.status === "success" && response.data.length > 0) {
                  datosPersonalEvaluado = response.data[0];
                }
                consultasCompletadas++;
                if (consultasCompletadas === 2) continuarFlujo();
              },
              error: function (error) {
                console.error("Error al obtener datos del evaluado:", error);
                consultasCompletadas++;
                if (consultasCompletadas === 2) continuarFlujo();
              },
            });
          } else {
            consultasCompletadas++;
          }

          // Consultar datos personales del evaluador
          if (evaluador && evaluador.dni) {
            $.ajax({
              url: `/rrhh/datos_personal_por_dni/?dni=${evaluador.dni}`,
              type: "GET",
              success: function (response) {
                if (response.status === "success" && response.data.length > 0) {
                  datosPersonalEvaluador = response.data[0];
                }
                consultasCompletadas++;
                if (consultasCompletadas === 2) continuarFlujo();
              },
              error: function (error) {
                console.error("Error al obtener datos del evaluador:", error);
                consultasCompletadas++;
                if (consultasCompletadas === 2) continuarFlujo();
              },
            });
          } else {
            consultasCompletadas++;
          }
        },
        error: function (error) {
          console.error("Error al obtener datos de usuarios:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Error al obtener datos de usuarios",
          });
        },
      });
    },
    error: function (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al obtener datos de evaluaciones",
      });
    },
  });
}


function crearContenidoPDF(datosEvaluado, objetivos, competencias) {

  
  try {
    // Crear nueva instancia de jsPDF
    const pdf = new window.jspdf.jsPDF("p", "mm", "a4");

    // Obtener dimensiones del PDF
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();

    // Contador para páginas
    let paginaActual = 1;
    const totalPaginas =
      1 + objetivos.length + (competencias ? competencias.length : 0);

    // Modificar la función agregarEncabezado para recibir datosEvaluado como parámetro
    function agregarEncabezado(datosEvaluadoParam = null) {
      // Usar los datos pasados como parámetro o caer en los datos generales
      const datos = datosEvaluadoParam || datosEvaluado;

      console.log("Ejecutando agregarEncabezado con datos:", datos);

      // IMPORTANTE: Forzar el restablecimiento completo del contexto gráfico
      pdf.setFillColor(255, 255, 255);
      pdf.setDrawColor(0, 0, 0);
      pdf.setTextColor(0, 0, 0); // CRÍTICO: Asegurarnos que el texto sea negro

      // Estructura del encabezado según la imagen
      const margenLateral = 15;
      const anchoUtil = pdfWidth - margenLateral * 2;

      // Primera fila con logos y tabla de información
      const altoFilaLogos = 20;
      const anchoCeldaLogo = Math.floor(anchoUtil * 0.35);
      const anchoTablaInfo = Math.floor(anchoUtil * 0.3);

      // Posiciones X
      const posXLogoIzq = margenLateral;
      const posXLogoDer = margenLateral + anchoCeldaLogo;
      const posXTabla = margenLateral + anchoCeldaLogo * 2;

      // IMPORTANTE: Dibujar todos los elementos explícitamente
      // Dibujar rectángulos de la primera fila
      pdf.setDrawColor(0, 0, 0);
      pdf.rect(posXLogoIzq, 10, anchoCeldaLogo, altoFilaLogos, "S"); // Logo Don Luis
      pdf.rect(posXLogoDer, 10, anchoCeldaLogo, altoFilaLogos, "S"); // Logo Campo Verde
      pdf.rect(posXTabla, 10, anchoTablaInfo, altoFilaLogos, "S"); // Tabla información

      // Agregar logos
      const margenLogo = 2;
      const altoLogo = 15;

      // Logo Don Luis
      try {
        pdf.addImage(
          "/static/assets/img/logo/logo_pngdl.png",
          "PNG",
          posXLogoIzq + 20,
          11,
          anchoCeldaLogo - 45,
          altoLogo - 1
        );
      } catch (e) {
        pdf.addImage(
          "/static/assets/img/logo/lododl.webp",
          "WEBP",
          posXLogoIzq + 15,
          11,
          anchoCeldaLogo - 30,
          altoLogo - 1
        );
      }

      // Texto bajo el logo Don Luis
      pdf.setFontSize(6);
      pdf.setFont("helvetica", "normal");
      pdf.text(
        "SOCIEDAD AGRÍCOLA DON LUIS S.A.",
        posXLogoIzq + anchoCeldaLogo / 2,
        10 + altoFilaLogos - 2,
        {
          align: "center",
        }
      );

      // Logo Campo Verde
      pdf.addImage(
        "/static/assets/img/logo/Logoacv.webp",
        "WEBP",
        posXLogoDer + 15,
        11,
        anchoCeldaLogo - 30,
        altoLogo - 1
      );

      // Texto bajo el logo Campo Verde
      pdf.text(
        "AGROINDUSTRIA CAMPO VERDE S.A.C.",
        posXLogoDer + anchoCeldaLogo / 2,
        10 + altoFilaLogos - 2,
        {
          align: "center",
        }
      );

      // Tabla de información (derecha)
      const infoItems = [
        {
          label: "Código:",
          value:
            datos && datos.id_evaluacion
              ? `EVAL-${datos.id_evaluacion}`
              : "N/A",
        },
        { label: "Versión:", value: "01" },
        { label: "Fecha :", value: "01.01.2024" },
        { label: "páginas:", value: `${paginaActual} de ${totalPaginas}` },
      ];

      // IMPORTANTE: Asegurar que el texto sea negro antes de dibujar los textos de la tabla
      pdf.setTextColor(0, 0, 0);

      // Crear filas de la tabla de información
      const altoFilaInfo = altoFilaLogos / infoItems.length;
      const medioCelda = Math.floor(anchoTablaInfo / 2);

      for (let i = 0; i < infoItems.length; i++) {
        // Línea horizontal inferior
        if (i < infoItems.length) {
          pdf.line(
            posXTabla,
            10 + (i + 1) * altoFilaInfo,
            posXTabla + anchoTablaInfo,
            10 + (i + 1) * altoFilaInfo
          );
        }

        // Línea vertical división
        pdf.line(
          posXTabla + medioCelda,
          10 + i * altoFilaInfo,
          posXTabla + medioCelda,
          10 + (i + 1) * altoFilaInfo
        );

        // Textos
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

      // IMPORTANTE: Asegurarse de que el título siempre se dibuje
      // Segunda fila: Título (ocupa todo el ancho)
      const altoFilaTitulo = 15;
      pdf.setDrawColor(0, 0, 0);
      pdf.rect(
        margenLateral,
        10 + altoFilaLogos,
        anchoUtil,
        altoFilaTitulo,
        "S"
      );

      // Título
      pdf.setFontSize(11);
      pdf.setFont("helvetica", "bold");
      pdf.text(
        "DEFINICIÓN DE OBJETIVOS, COMPETENCIAS Y ACCIONES DE",
        margenLateral + anchoUtil / 2,
        10 + altoFilaLogos + 8,
        {
          align: "center",
        }
      );
      pdf.text(
        "DESARROLLO",
        margenLateral + anchoUtil / 2,
        10 + altoFilaLogos + 14,
        {
          align: "center",
        }
      );

      // Devolver la posición Y donde empieza el contenido
      return 10 + altoFilaLogos + altoFilaTitulo + 5;
    }

    // Función para agregar pie de página con onda azul
    function agregarPieDePagina(esUltimaPagina) {
      // Agregar imagen de onda azul en la parte inferior
      pdf.addImage(
        "/static/assets/img/logo/pie_pagina.png", // Usar la imagen específica mencionada
        "PNG",
        0,
        pdfHeight - 40, // Posición Y más arriba para dar más altura
        pdfWidth,
        40 // Aumentar la altura de la imagen
      );

      // Agregar texto #creciendojuntos
      pdf.setTextColor(255, 255, 255); // Color blanco para mejor contraste sobre fondo azul
      pdf.setFontSize(10);
      pdf.setFont("helvetica", "bold");
      pdf.text("#creciendojuntos", pdfWidth / 2, pdfHeight - 5, {
        align: "center",
      });
    }

    // Función para crear una sección con título azul
    function crearTituloSeccion(texto, yPos) {
      pdf.setFillColor(52, 101, 164); // Color azul (#3465a4)
      pdf.setDrawColor(52, 101, 164);
      pdf.rect(10, yPos, pdfWidth - 20, 7, "F");

      pdf.setTextColor(255, 255, 255); // Texto blanco
      pdf.setFontSize(10);
      pdf.setFont("helvetica", "bold");
      pdf.text(texto, 12, yPos + 5);

      // CRÍTICO: Siempre restablecer el color a negro después
      pdf.setTextColor(0, 0, 0);

      return yPos + 10;
    }

    // PRIMERA PÁGINA: Información del empleado y evaluador
    let yPos = agregarEncabezado(datosEvaluado);

    // Sección 1: Información del empleado
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
        pdf.text(`5. Revisión Intermedia (${objetivo.porc_cumplimiento  || " -- "}%)`, 12, yPos + 5);
        pdf.text(
         "6. Revisión final ( -- %)",
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

        // Siempre agregar pie de página sin importar si es la última o no
        agregarPieDePagina(true);
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
        pdf.text(`4. Revisión Intermedia (${competencia.porc_cumplimiento || " -- "}%)`, 12, yPos + 5);
        pdf.text(
          "5. Revisión final ( -- %)",
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

    // Guardar el PDF con un nombre descriptivo
    const nombrePDF = `Evaluacion_ID${
      datosEvaluado.id_evaluacion
    }_${datosEvaluado.nombre_evaluado.replace(/\s+/g, "_")}_${
      datosEvaluado.periodo
    }.pdf`;

    const pdfBlob = pdf.output("blob");

    pdf.save(nombrePDF);

    // Mostrar mensaje de éxito
    Swal.fire({
      icon: "success",
      title: "PDF Generado",
      text: `Se ha generado el PDF "${nombrePDF}" correctamente. ¿Desea enviarlo por correo al evaluado?`,
      showCancelButton: true,
      confirmButtonText: "Sí, enviar por correo",
      cancelButtonText: "No, solo guardar",
      confirmButtonColor: "#28a745",
      cancelButtonColor: "#6c757d",
    }).then((result) => {
      if (result.isConfirmed) {
        enviarPDFPorCorreo(datosEvaluado, nombrePDF, pdfBlob);
      }
    });
  } catch (error) {
    console.error("Error al generar PDF:", error);
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "No se pudo generar el PDF: " + error.message,
    });
  }
}

// Nueva función para enviar el PDF por correo
function enviarPDFPorCorreo(datosEvaluado, nombrePDF, pdfBlob) {
  console.log("Función enviarPDFPorCorreo iniciada");
  console.log("Datos evaluado:", datosEvaluado);
  console.log("Nombre PDF:", nombrePDF);
  console.log("PDF Blob disponible:", pdfBlob instanceof Blob);

  // Mostrar modal para completar información del correo
  Swal.fire({
    title: "Enviar evaluación por correo",
    html: `
      <form id="emailForm" class="text-left">
        <div class="form-group mb-3">
          <label for="destinatario">Correo del evaluado:</label>
          <input type="email" id="destinatario" class="form-control" value="${datosEvaluado.email}" placeholder="correo@ejemplo.com" required>
        </div>
        <div class="form-group mb-3">
          <label for="asunto">Asunto:</label>
          <input type="text" id="asunto" class="form-control" 
                 value="Evaluación de desempeño - ${datosEvaluado.periodo}" required>
        </div>
        <div class="form-group mb-3">
          <label for="mensaje">Mensaje:</label>
          <textarea id="mensaje" class="form-control" rows="4" required>Estimado/a ${datosEvaluado.nombre_evaluado},

Adjunto encontrará su evaluación de desempeño correspondiente al período ${datosEvaluado.periodo}.

Saludos cordiales,
Departamento de Recursos Humanos</textarea>
        </div>
      </form>
    `,
    showCancelButton: true,
    confirmButtonText: "Enviar",
    cancelButtonText: "Cancelar",
    confirmButtonColor: "#28a745",
    cancelButtonColor: "#6c757d",
    preConfirm: () => {
      const form = document.getElementById("emailForm");
      if (!form.checkValidity()) {
        form.reportValidity();
        return false;
      }
      return {
        destinatario: document.getElementById("destinatario").value,
        asunto: document.getElementById("asunto").value,
        mensaje: document.getElementById("mensaje").value,
      };
    },
  }).then((result) => {
    if (result.isConfirmed) {
      const datos = result.value;

      // Crear un FormData para enviar el archivo
      const formData = new FormData();
      formData.append("destinatario", datos.destinatario);
      formData.append("asunto", datos.asunto);
      formData.append("mensaje", datos.mensaje);
      formData.append("archivo_pdf", pdfBlob, nombrePDF);
      formData.append("id_evaluacion", datosEvaluado.id_evaluacion);

      // Mostrar loading mientras se envía el correo
      Swal.fire({
        title: "Enviando correo",
        text: "Por favor espere...",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Enviar la solicitud al servidor
      $.ajax({
        url: "/rrhh/enviar_evaluacion_correo/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        success: function (response) {
          if (response.status === "success") {
            Swal.fire({
              icon: "success",
              title: "¡Correo enviado!",
              text: `La evaluación ha sido enviada correctamente a ${datos.destinatario}`,
              confirmButtonColor: "#28a745",
            });
          } else {
            console.error("Error reportado por el servidor:", response);
            Swal.fire({
              icon: "error",
              title: "Error",
              text: response.message || "Ocurrió un error al enviar el correo",
              confirmButtonColor: "#dc3545",
            });
          }
        },
        error: function (xhr, status, error) {
          console.error("Error al enviar correo:", error);
          let errorMessage = "Error en la conexión al enviar el correo";

          try {
            const response = JSON.parse(xhr.responseText);
            errorMessage = response.message || errorMessage;
          } catch (e) {
            console.error("Error al procesar la respuesta:", e);
          }

          Swal.fire({
            icon: "error",
            title: "Error",
            text: errorMessage,
            confirmButtonColor: "#dc3545",
          });
        },
      });
    }
  });
}


// Función auxiliar para obtener el token CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Función para limpiar el formulario después de guardar
function limpiarFormularioCompetencias() {
  // Limpiar el select de evaluado
  $("#evaluadoSelect").val("");

  // Desmarcar todos los checkboxes de competencias
  $(".custom-control-input").prop("checked", false);

  // Limpiar todas las metas y comentarios
  $(".competencia-meta").val("");
  $("textarea").val("");

  // Desmarcar todos los radio buttons
  $('input[type="radio"]').prop("checked", false);

  // Volver al paso 1
  $("#paso2Competencias").hide();
  $("#paso1Competencias").show();
}

// Función para validar fechas en tiempo real

function validarFechasCompetencia(competenciaDiv) {
  const competenciaForm = competenciaDiv.find("form");
  const competenciaId = competenciaDiv.attr("id").split("-")[1];

  // Obtener los campos de fecha
  const fechaInicioInput = competenciaForm.find(".competencia-fecha-inicio");
  const fechaFinInput = competenciaForm.find(".competencia-fecha-fin");

  // Obtener los valores
  const fechaInicio = fechaInicioInput.val();
  const fechaFin = fechaFinInput.val();

  // Obtener el periodo del evaluado (asumimos que está en un campo oculto o en el título)
  const periodoTexto = $("#evaluadoSelect option:selected").text();
  let periodo = new Date().getFullYear(); // Valor por defecto: año actual

  // Intentar extraer el año del periodo del texto del evaluado seleccionado
  if (periodoTexto) {
    const match = periodoTexto.match(/\b(20\d{2})\b/); // Buscar un año en formato 20XX
    if (match) {
      periodo = parseInt(match[1]);
    }
  }

  // Fecha actual para comparar
  const fechaActual = new Date();
  fechaActual.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fechas

  // Crear objetos Date para las fechas ingresadas
  const fechaInicioObj = fechaInicio ? new Date(fechaInicio) : null;
  const fechaFinObj = fechaFin ? new Date(fechaFin) : null;

  // Límites del periodo
  const inicioAno = new Date(periodo, 0, 1); // 1 de enero del periodo
  const finAno = new Date(periodo, 11, 31); // 31 de diciembre del periodo

  // Eliminar mensajes de error previos
  competenciaForm.find(".fecha-error").remove();
  competenciaForm.find(".fecha-success").remove();

  // Resetear estilos
  fechaInicioInput.removeClass("is-invalid is-valid");
  fechaFinInput.removeClass("is-invalid is-valid");

  let esValido = true;

  // Validar fecha de inicio
  if (fechaInicio) {
    if (fechaInicioObj < fechaActual) {
      // Fecha de inicio anterior a la fecha actual
      fechaInicioInput.addClass("is-invalid");
      fechaInicioInput.after(
        `<div class="fecha-error text-danger small">La fecha de inicio no puede ser anterior a la fecha actual</div>`
      );
      esValido = false;
    } else if (fechaInicioObj < inicioAno || fechaInicioObj > finAno) {
      // Fecha de inicio fuera del periodo
      fechaInicioInput.addClass("is-invalid");
      fechaInicioInput.after(
        `<div class="fecha-error text-danger small">La fecha de inicio debe estar dentro del periodo ${periodo}</div>`
      );
      esValido = false;
    } else {
      // Fecha de inicio válida
      fechaInicioInput.addClass("is-valid");
      fechaInicioInput.after(
        `<div class="fecha-success text-success small">Fecha de inicio válida</div>`
      );
    }
  }

  // Validar fecha de fin
  if (fechaFin) {
    if (fechaFinObj < fechaActual) {
      // Fecha de fin anterior a la fecha actual
      fechaFinInput.addClass("is-invalid");
      fechaFinInput.after(
        `<div class="fecha-error text-danger small">La fecha de fin no puede ser anterior a la fecha actual</div>`
      );
      esValido = false;
    } else if (fechaFinObj < inicioAno || fechaFinObj > finAno) {
      // Fecha de fin fuera del periodo
      fechaFinInput.addClass("is-invalid");
      fechaFinInput.after(
        `<div class="fecha-error text-danger small">La fecha de fin debe estar dentro del periodo ${periodo}</div>`
      );
      esValido = false;
    } else if (fechaInicio && fechaFinObj <= fechaInicioObj) {
      // Fecha de fin anterior o igual a la fecha de inicio
      fechaFinInput.addClass("is-invalid");
      fechaFinInput.after(
        `<div class="fecha-error text-danger small">La fecha de fin debe ser posterior a la fecha de inicio</div>`
      );
      esValido = false;
    } else {
      // Fecha de fin válida
      fechaFinInput.addClass("is-valid");
      fechaFinInput.after(
        `<div class="fecha-success text-success small">Fecha de fin válida</div>`
      );
    }
  }

  // Actualizar el estado de validación en el div de la competencia
  competenciaDiv.data("fechas-validas", esValido);

  return esValido;
}

// Función para validar todas las competencias
function validarTodasLasCompetencias() {
  let todasValidas = true;

  // Recorrer todas las competencias
  $(".competencia").each(function () {
    const competenciaDiv = $(this);
    const esValida = validarFechasCompetencia(competenciaDiv);

    if (!esValida) {
      todasValidas = false;
    }
  });

  return todasValidas;
}

/*###################################################*/
/* EDITAR COMPETENCIAS */
/*###################################################*/

//CREAR COMPETENCIAS
// Variable para llevar el conteo de competencias
let contadorCompetencias = 1;

// Función para crear una nueva competencia

function crearNuevaCompetencia() {
  contadorCompetencias++;

  const nuevaCompetencia = `
      <div class="card-body competencia" id="competencia-${contadorCompetencias}">
        <div class="card mb-0 shadow-sm border-left-primary">
          <div class="card-header bg-light d-flex justify-content-between align-items-center">
            <h5 class="text-primary mb-0"><i class="fas fa-star"></i> Competencia ${contadorCompetencias}</h5>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarCompetenciaForm(${contadorCompetencias})">
              <i class="fas fa-trash"></i> Eliminar
            </button>
          </div>
          <div class="card-body">
            <form id="form-competencia-${contadorCompetencias}">
              <div class="form-group">
                <label>Tipo de Competencia</label>
                
                <!-- Leyenda de colores -->
                <div class="d-flex justify-content-end mb-2">
                  <div class="badge badge-pill mr-2 d-flex align-items-center">
                    <span class="color-indicator esencial-indicator mr-1"></span>
                    <small>Esencial</small>
                  </div>
                  <div class="badge badge-pill d-flex align-items-center">
                    <span class="color-indicator liderazgo-indicator mr-1"></span>
                    <small>Liderazgo</small>
                  </div>
                </div>
                
                <select class="form-control competencia-tipo" required>
                  <option value="1" class="option-esencial">Compromiso con los resultados</option>
                  <option value="2" class="option-esencial">Proactividad</option>
                  <option value="3" class="option-esencial">Flexibilidad</option>
                  <option value="4" class="option-esencial">Trabajo en Equipo</option>
                  <option value="9" class="option-esencial">Capacitación</option>
                  <option value="5" class="option-liderazgo">Visión de Negocio</option>
                  <option value="6" class="option-liderazgo">Planificación y Organización</option>
                  <option value="7" class="option-liderazgo">Toma de Decisiones</option>
                  <option value="8" class="option-liderazgo">Gestión de Personas</option>
                </select>
              </div>
              <div class="form-group">
                <label>Meta de la Competencia</label>
                <textarea class="form-control competencia-meta" rows="3" 
                  placeholder="Defina el resultado esperado para esta competencia" required></textarea>
              </div>
              <div class="form-row">
                <div class="col">
                  <label>Fecha Inicio</label>
                  <input type="date" class="form-control competencia-fecha-inicio" required>
                </div>
                <div class="col">
                  <label>Fecha Fin</label>
                  <input type="date" class="form-control competencia-fecha-fin" required>
                </div>
              </div>
              <div class="form-group mt-3">
                <label>Comentarios y/o Evidencias</label>
                <textarea class="form-control competencia-comentarios" rows="3"
                  placeholder="Ingrese sus observaciones y evidencias que sustenten la evaluación..."></textarea>
              </div>
              <div class="form-group mt-3" style="display: none;">
                <label>Nivel de Cumplimiento</label>
                <div class="btn-group btn-group-toggle d-flex" data-toggle="buttons">
                  <label class="btn btn-outline-danger flex-fill ">
                    <input type="radio" name="nivel-${contadorCompetencias}" value="no_cumple" > No Cumple
                  </label>
                  <label class="btn btn-outline-primary flex-fill ">
                    <input type="radio" name="nivel-${contadorCompetencias}" value="cumple" > Cumple
                  </label>
                  <label class="btn btn-outline-success flex-fill ">
                    <input type="radio" name="nivel-${contadorCompetencias}" value="excede" > Excede
                  </label>
                  <label class="btn btn-outline-warning flex-fill ">
                    <input type="radio" name="nivel-${contadorCompetencias}" value="sobresaliente" > Sobresaliente
                  </label>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    `;

  // Agregar la nueva competencia al contenedor
  $("#contenedor-competencias").append(nuevaCompetencia);

  // Registrar la competencia recién creada
  const nuevaCompetenciaDiv = $(`#competencia-${contadorCompetencias}`);

  // Agregar eventos para validar fechas cuando cambien
  nuevaCompetenciaDiv
    .find(".competencia-fecha-inicio, .competencia-fecha-fin")
    .on("change", function () {
      validarFechasCompetencia(nuevaCompetenciaDiv);
    });

  // Inicializar como no válido hasta que se ingresen fechas
  nuevaCompetenciaDiv.data("fechas-validas", false);

  // Disparar evento para que el script de colorización se aplique
  $(document).trigger("nuevaCompetenciaCreada");
}

// Función para eliminar una competencia específica
function eliminarCompetenciaForm(id) {
  // Confirmar antes de eliminar
  Swal.fire({
    title: "¿Eliminar competencia?",
    text: `¿Está seguro que desea eliminar la Competencia ${id}?`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#dc3545",
    cancelButtonColor: "#6c757d",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Eliminar el elemento del DOM
      $(`#competencia-${id}`).remove();

      // Renumerar las competencias restantes
      renumerarCompetencias();

      // Notificar al usuario
      Swal.fire({
        icon: "success",
        title: "Competencia eliminada",
        showConfirmButton: false,
        timer: 1500,
      });
    }
  });
}

// Función para renumerar las competencias después de eliminar alguna
function renumerarCompetencias() {
  let nuevoIndice = 1;

  // Seleccionar todas las competencias existentes
  const competencias = document.querySelectorAll(".competencia");

  competencias.forEach((competencia) => {
    // Obtener el ID actual
    const idActual = competencia.id.split("-")[1];

    // Actualizar el título de la competencia
    const titulo = competencia.querySelector("h5");
    if (titulo) {
      titulo.innerHTML = `<i class="fas fa-star"></i> Competencia ${nuevoIndice}`;
    }

    // Actualizar el ID del contenedor
    competencia.id = `competencia-${nuevoIndice}`;

    // Actualizar el ID del formulario
    const form = competencia.querySelector(`#form-competencia-${idActual}`);
    if (form) {
      form.id = `form-competencia-${nuevoIndice}`;

      // Actualizar los nombres de los radio buttons
      const radios = form.querySelectorAll('input[type="radio"]');
      radios.forEach((radio) => {
        radio.name = `nivel-${nuevoIndice}`;
      });
    }

    // Actualizar el botón de eliminar
    const btnEliminar = competencia.querySelector(
      'button[onclick^="eliminarCompetenciaForm"]'
    );
    if (btnEliminar) {
      btnEliminar.setAttribute(
        "onclick",
        `eliminarCompetenciaForm(${nuevoIndice})`
      );
    }

    nuevoIndice++;
  });

  // Actualizar el contador global
  contadorCompetencias = nuevoIndice - 1;
}

// CARGAR EVALUADOS DISPONIBLES PARA COMPETENCIAS

function cargarEvaluados() {
  $.ajax({
    url: "/almacen/objetivos_evaluacion/",
    type: "GET",
    success: function (response) {
      if (response.status === "success") {
        const selectEvaluado = $("#evaluadoSelect");
        selectEvaluado.empty();
        selectEvaluado.append(
          '<option value="">Seleccione al evaluado...</option>'
        );

        // Obtener el ID de evaluación preseleccionado
        const preselectedEvaluacionId = localStorage.getItem(
          "preselectedEvaluacionId"
        );
        console.log(
          "Buscando evaluación con ID DESPUES DE GUARDAR:",
          preselectedEvaluacionId
        );

        // Obtener evaluación preseleccionada
        let evaluacionPreseleccionada = null;
        if (preselectedEvaluacionId) {
          evaluacionPreseleccionada = response.data.find(
            (item) => item.id.toString() === preselectedEvaluacionId.toString()
          );

          console.log("Evaluación encontrada:", evaluacionPreseleccionada);
        }

        // Ordenar evaluados alfabéticamente
        const evaluados = response.data.sort((a, b) =>
          a.evaluado.localeCompare(b.evaluado)
        );

        // Agregar las opciones al select
        evaluados.forEach((item) => {
          // Determinar si esta evaluación debe estar seleccionada
          const isSelected =
            evaluacionPreseleccionada &&
            item.id.toString() === preselectedEvaluacionId.toString();

          selectEvaluado.append(`
              <option value="${item.id}" ${
            isSelected ? 'selected="selected"' : ""
          }>
                  ${item.evaluado} - ${item.nombre_area}
              </option>
            `);
        });

        // Si se encontró una evaluación preseleccionada, asegurar que está seleccionada
        if (evaluacionPreseleccionada) {
          selectEvaluado.val(preselectedEvaluacionId);
          selectEvaluado.trigger("change");
          console.log("Seleccionando evaluación ID:", preselectedEvaluacionId);

          // Limpiar localStorage después de usarlo
          localStorage.removeItem("preselectedEvaluacionId");
        }
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudieron cargar los evaluados",
          confirmButtonColor: "#dc3545",
        });
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al cargar evaluados:", error);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error en la conexión al cargar evaluados",
        confirmButtonColor: "#dc3545",
      });
    },
  });
}

function editarCompetencia(id) {
  $.ajax({
    url: `/detalles_competencias/${id}/`,
    type: "GET",
    success: function (response) {
      if (response.status === "success" && response.data.length > 0) {
        const competencia = response.data[0];

        // Llenar el modal con los datos
        $("#evaluado_nombre").val(
          competencia.nombre_evaluado + " " + competencia.apellido_evaluado
        );
        $("#competencia_nombre").val(competencia.nombre_competencia);
        $("#meta_competencia").val(competencia.meta);
        $("#comentarios_competencia").val(competencia.comentarios);

        // Establecer las fechas
        if (competencia.fecha_inicio) {
          $("#competencia-fecha-inicio-edicion").val(competencia.fecha_inicio);
        }
        if (competencia.fecha_fin) {
          $("#competencia-fecha-fin-edicion").val(competencia.fecha_fin);
        }

        // Guardar los IDs necesarios en el modal
        $("#Modal_Editar_Competencia").data("competencia-id", id);
        $("#Modal_Editar_Competencia").data(
          "tipo-competencia-id",
          competencia.id_tipo_competencia
        );
        $("#Modal_Editar_Competencia").data(
          "id-evaluacion",
          competencia.id_evaluacion
        );

        // Marcar el nivel de cumplimiento
        $('input[name="nivel_cumplimiento"]').prop("checked", false);
        $('input[name="nivel_cumplimiento"]').parent().removeClass("active");

        if (competencia.no_cumple === 1) {
          $('input[value="no_cumple"]')
            .prop("checked", true)
            .parent()
            .addClass("active");
        } else if (competencia.cumple === 1) {
          $('input[value="cumple"]')
            .prop("checked", true)
            .parent()
            .addClass("active");
        } else if (competencia.excede === 1) {
          $('input[value="excede"]')
            .prop("checked", true)
            .parent()
            .addClass("active");
        } else if (competencia.sobresaliente === 1) {
          $('input[value="sobresaliente"]')
            .prop("checked", true)
            .parent()
            .addClass("active");
        }

        // Mostrar el modal
        $("#Modal_Editar_Competencia").modal("show");
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudo cargar la información de la competencia",
          confirmButtonColor: "#dc3545",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al cargar la competencia: " + error,
        confirmButtonColor: "#dc3545",
      });
    },
  });
}

function guardarEdicionCompetencia() {
  // Obtener el ID de la competencia almacenado en el modal
  const competenciaId = $("#Modal_Editar_Competencia").data("competencia-id");
  const idTipoCompetencia = $("#Modal_Editar_Competencia").data(
    "tipo-competencia-id"
  );
  const idEvaluacion = $("#Modal_Editar_Competencia").data("id-evaluacion");

  // Obtener el valor seleccionado del nivel de cumplimiento
  const nivelSeleccionado = $('input[name="nivel_cumplimiento"]:checked').val();

  // Obtener las fechas
  const fechaInicio = $("#competencia-fecha-inicio-edicion").val();
  const fechaFin = $("#competencia-fecha-fin-edicion").val();

  // Crear objeto con los valores de cumplimiento
  const nivelesCumplimiento = {
    no_cumple: nivelSeleccionado === "no_cumple" ? 1 : 0,
    cumple: nivelSeleccionado === "cumple" ? 1 : 0,
    excede: nivelSeleccionado === "excede" ? 1 : 0,
    sobresaliente: nivelSeleccionado === "sobresaliente" ? 1 : 0,
  };

  // Crear objeto con todos los datos a enviar
  const datosActualizados = {
    id_tipo_competencia: idTipoCompetencia,
    id_evaluacion: idEvaluacion,
    meta: $("#meta_competencia").val().trim(),
    fecha_inicio: fechaInicio,
    fecha_fin: fechaFin,
    comentarios: $("#comentarios_competencia").val().trim(),
    ...nivelesCumplimiento,
  };

  // Validaciones básicas
  if (!datosActualizados.meta) {
    Swal.fire({
      icon: "warning",
      title: "Campo requerido",
      text: "Por favor, ingrese la meta de la competencia",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  if (!fechaInicio) {
    Swal.fire({
      icon: "warning",
      title: "Campo requerido",
      text: "Por favor, seleccione la fecha de inicio",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  if (!fechaFin) {
    Swal.fire({
      icon: "warning",
      title: "Campo requerido",
      text: "Por favor, seleccione la fecha de fin",
      confirmButtonColor: "#ffc107",
    });
    return;
  }

  // Mostrar loading
  Swal.fire({
    title: "Guardando cambios...",
    didOpen: () => {
      Swal.showLoading();
    },
    allowOutsideClick: false,
    allowEscapeKey: false,
    allowEnterKey: false,
  });

  // Enviar datos al servidor
  $.ajax({
    url: `/detalles_competencias/${competenciaId}/`,
    type: "PUT",
    contentType: "application/json",
    data: JSON.stringify(datosActualizados),
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    success: function (response) {
      if (response.status === "success") {
        Swal.fire({
          icon: "success",
          title: "Éxito",
          text: "Competencia actualizada correctamente",
          confirmButtonColor: "#28a745",
        }).then((result) => {
          if (result.isConfirmed) {
            // Cerrar el modal
            $("#Modal_Editar_Competencia").modal("hide");
            // Recargar la tabla
            $("#tablaDetallesCompetencias").DataTable().ajax.reload();
          }
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: response.message || "Error al actualizar la competencia",
          confirmButtonColor: "#dc3545",
        });
      }
    },
    error: function (xhr, status, error) {
      let errorMessage = "Error al actualizar la competencia";
      try {
        const response = JSON.parse(xhr.responseText);
        errorMessage = response.message || errorMessage;
      } catch (e) {
        console.error("Error parsing error response:", e);
      }

      Swal.fire({
        icon: "error",
        title: "Error",
        text: errorMessage,
        confirmButtonColor: "#dc3545",
      });
    },
  });
}

function eliminarCompetencia(id) {
  $.when(
    Swal.fire({
      title: "¿Está seguro?",
      text: "¿Desea eliminar esta competencia? Esta acción no se puede revertir.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#dc3545",
      cancelButtonColor: "#6c757d",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    })
  ).then((result) => {
    if (result.isConfirmed) {
      // Mostrar loading
      $.when(
        Swal.fire({
          title: "Eliminando...",
          didOpen: () => {
            Swal.showLoading();
          },
          allowOutsideClick: false,
          allowEscapeKey: false,
          allowEnterKey: false,
        })
      );

      // Realizar la petición DELETE
      $.ajax({
        url: `/detalles_competencias/${id}/`,
        type: "DELETE",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        success: function (response) {
          if (response.status === "success") {
            $.when(
              Swal.fire({
                icon: "success",
                title: "¡Eliminado!",
                text: response.message,
                confirmButtonColor: "#28a745",
              })
            ).then(() => {
              // Recargar solo la tabla de competencias
              $("#tablaDetallesCompetencias").DataTable().ajax.reload();
              $("#tablaEvaluaciones_competencias").DataTable().ajax.reload();
            });
          } else {
            $.when(
              Swal.fire({
                icon: "error",
                title: "Error",
                text: response.message,
                confirmButtonColor: "#dc3545",
              })
            );
          }
        },
        error: function (xhr, status, error) {
          let errorMessage = "Error al eliminar la competencia";
          try {
            const response = $.parseJSON(xhr.responseText);
            errorMessage = response.message || errorMessage;
          } catch (e) {
            console.error("Error parsing error response:", e);
          }

          $.when(
            Swal.fire({
              icon: "error",
              title: "Error",
              text: errorMessage,
              confirmButtonColor: "#dc3545",
            })
          );
        },
      });
    }
  });
}

// Función para resetear el modal de competencias
function resetModalCompetencias() {
  // Limpiar el select de evaluado
  $("#evaluadoSelect").val("");

  // Mantener solo la primera competencia (template inicial)
  const competencias = $(".competencia");

  // Si hay más de una competencia, eliminar las adicionales
  if (competencias.length > 1) {
    for (let i = competencias.length - 1; i > 0; i--) {
      $(competencias[i]).remove();
    }
  }

  // Resetear los campos de la primera competencia
  const primeraCompetencia = $("#competencia-1");
  if (primeraCompetencia.length) {
    // Resetear el tipo de competencia
    primeraCompetencia.find(".competencia-tipo").val("1");

    // Limpiar la meta
    primeraCompetencia.find(".competencia-meta").val("");

    // Limpiar las fechas
    primeraCompetencia.find(".competencia-fecha-inicio").val("");
    primeraCompetencia.find(".competencia-fecha-fin").val("");

    // Limpiar los comentarios
    primeraCompetencia.find(".competencia-comentarios").val("");

    // Desmarcar todos los radio buttons
    primeraCompetencia.find('input[type="radio"]').prop("checked", false);
    primeraCompetencia.find(".btn").removeClass("active");
  }

  // Resetear el contador de competencias
  contadorCompetencias = 1;
}

// Función auxiliar para buscar y seleccionar evaluado
function buscarYSeleccionarEvaluado(idEvaluado, nombreEvaluado) {
  const selectEvaluado = $("#evaluadoSelect");

  // Intentar seleccionar por ID
  selectEvaluado.val(idEvaluado);

  // Si no funciona, intentar buscar por nombre
  if (!selectEvaluado.val()) {
    selectEvaluado.find("option").each(function () {
      const opcionTexto = $(this).text().trim();
      const nombreBuscar = nombreEvaluado.split("-")[0].trim();

      if (opcionTexto.indexOf(nombreBuscar) >= 0) {
        const idOpcion = $(this).val();
        selectEvaluado.val(idOpcion);
        console.log("Evaluado encontrado por nombre:", nombreBuscar, idOpcion);
        return false; // Salir del bucle
      }
    });
  }

  // Disparar evento change para activar cualquier listener
  selectEvaluado.trigger("change");
}
//##############################################################

document.addEventListener("DOMContentLoaded", function () {
  // Inicializar tablas y cargar datos existentes
  inicializarTablaEvaluaciones_competencia();

  // Inicializar validación para competencias cuando se muestra el modal
  $("#modalCompetencias").on("shown.bs.modal", function () {
    // Inicializar la validación para la primera competencia
    const primeraCompetencia = $("#competencia-1");

    // Agregar eventos para validar fechas cuando cambien
    primeraCompetencia
      .find(".competencia-fecha-inicio, .competencia-fecha-fin")
      .on("change", function () {
        validarFechasCompetencia(primeraCompetencia);
      });

    // Inicializar como no válido hasta que se ingresen fechas correctas
    primeraCompetencia.data("fechas-validas", false);
    cargarEvaluados();
  });

  // Inicializar validación para competencia en modalAgregarCompetenciaDetalle
  $("#modalAgregarCompetenciaDetalle").on("shown.bs.modal", function () {
    // Agregar eventos para validar fechas
    $("#competencia-fecha-inicio-detalle, #competencia-fecha-fin-detalle").on(
      "change",
      function () {
        validarFechasCompetenciaDetalle();
      }
    );
  });

  // Inicializar validación para edición de competencias
  $("#Modal_Editar_Competencia").on("shown.bs.modal", function () {
    // Agregar eventos para validar fechas
    $("#competencia-fecha-inicio-edicion, #competencia-fecha-fin-edicion").on(
      "change",
      function () {
        validarFechasCompetenciaEdicion();
      }
    );
  });

  // Manejador del modal cuando se cierra
  $("#modalCompetencias").on("hidden.bs.modal", function () {
    resetModalCompetencias();
  });
});

// Modificar el botón "Agregar Competencia" para usar la nueva lógica
function agregarCompetenciaDesdeObjetivos() {
  // Obtener el id_evaluacion guardado en localStorage
  const id_evaluacion = localStorage.getItem("preselectedEvaluacionId");
  console.log("ID de evaluación recuperado de localStorage:", id_evaluacion);

  if (!id_evaluacion) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "No se ha seleccionado ninguna evaluación",
      confirmButtonColor: "#dc3545",
    });
    return;
  }

  // Primero intentamos buscar en las competencias existentes
  $.ajax({
    url: "/almacen/detalles_competencias/",
    type: "GET",
    success: function (response) {
      if (response.status === "success" && response.data) {
        // Filtrar por id_evaluacion
        const competenciasEvaluado = response.data.filter(
          (item) => item.id_evaluacion == id_evaluacion
        );

        if (competenciasEvaluado.length > 0) {
          // Si encontramos competencias, usamos esos datos
          const evaluado = competenciasEvaluado[0];
          const nombreCompleto = `${evaluado.nombre_evaluado} ${evaluado.apellido_evaluado} - ${evaluado.nombre_area}`;

          // Abrir modal con datos del evaluado
          abrirModalAgregarCompetenciaDetalle(id_evaluacion, nombreCompleto);
        } else {
          // Si no hay competencias, buscamos en objetivos
          buscarDatosEnObjetivos(id_evaluacion);
        }
      } else {
        // Si hay error o no hay datos, buscamos en objetivos
        buscarDatosEnObjetivos(id_evaluacion);
      }
    },
    error: function () {
      // En caso de error, buscamos en objetivos
      buscarDatosEnObjetivos(id_evaluacion);
    },
  });
}

// Función para buscar datos en la API de objetivos
function buscarDatosEnObjetivos(id_evaluacion) {
  $.ajax({
    url: "/almacen/detalles_objetivos/",
    type: "GET",
    success: function (response) {
      if (response.status === "success" && response.data) {
        // Filtrar por id_evaluacion
        const objetivosEvaluado = response.data.filter(
          (item) => item.id_evaluacion == id_evaluacion
        );

        if (objetivosEvaluado.length > 0) {
          // Si encontramos objetivos, usamos esos datos
          const objetivo = objetivosEvaluado[0];
          const nombreCompleto = `${objetivo.nombre_evaluado} ${objetivo.apellido_evaluado} - ${objetivo.nombre_area}`;

          console.log("Datos recuperados de objetivos:", objetivo);
          console.log("Nombre completo:", nombreCompleto);

          // Abrir modal con datos del evaluado
          abrirModalAgregarCompetenciaDetalle(id_evaluacion, nombreCompleto);
        } else {
          // Último recurso: buscar en la tabla de evaluaciones
          buscarEnTablaEvaluaciones(id_evaluacion);
        }
      } else {
        // Si no hay datos de objetivos, intentamos con la tabla de evaluaciones
        buscarEnTablaEvaluaciones(id_evaluacion);
      }
    },
    error: function () {
      buscarEnTablaEvaluaciones(id_evaluacion);
    },
  });
}

// Función para buscar en la tabla de evaluaciones como último recurso
function buscarEnTablaEvaluaciones(id_evaluacion) {
  try {
    const tablaEvaluaciones = $("#tablaEvaluaciones_competencias").DataTable();
    const filas = tablaEvaluaciones.rows().data();

    for (let i = 0; i < filas.length; i++) {
      if (filas[i].id == id_evaluacion) {
        const nombreCompleto = `${filas[i].evaluado} - ${filas[i].nombre_area}`;
        abrirModalAgregarCompetenciaDetalle(id_evaluacion, nombreCompleto);
        return;
      }
    }

    // Si llegamos aquí, no se encontró información, pero abrimos el modal de todos modos
    Swal.fire({
      icon: "warning",
      title: "Advertencia",
      text: "No se pudo obtener el nombre del evaluado, pero puede continuar",
      confirmButtonColor: "#fd7e14",
    }).then(() => {
      abrirModalAgregarCompetenciaDetalle(
        id_evaluacion,
        "Evaluado ID: " + id_evaluacion
      );
    });
  } catch (error) {
    console.error("Error al buscar en tabla:", error);
    abrirModalAgregarCompetenciaDetalle(
      id_evaluacion,
      "Evaluado ID: " + id_evaluacion
    );
  }
}
