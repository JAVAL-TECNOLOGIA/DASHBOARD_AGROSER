function cargarEvaluadosYArea() {
  // Primera petición: obtener usuarios y área del usuario logueado
  $.ajax({
    url: "/rrhh/usuario-area/",
    type: "GET",
    success: function (responseUsuarios) {
      if (responseUsuarios.status === "success") {
        // Obtener el ID del usuario logueado
        const idUsuarioLogueado = $("#id_evaluador").val();

        console.log("ID Usuario Logueado:", idUsuarioLogueado);

        if (!idUsuarioLogueado) {
          console.error("No se pudo obtener el ID del usuario logueado");
          Swal.fire({
            icon: "warning",
            title: "Error",
            text: "No se pudo identificar al usuario actual",
          });
          return;
        }

        // Encontrar el usuario logueado y su área
        const usuarioLogueado = responseUsuarios.data.find(
          (usuario) => usuario.id.toString() === idUsuarioLogueado.toString()
        );

        if (!usuarioLogueado) {
          console.error("No se encontró el usuario en la respuesta");
          Swal.fire({
            icon: "warning",
            title: "Error",
            text: "No se encontró información del usuario",
          });
          return;
        }

        console.log("Usuario logueado:", usuarioLogueado);

        // Segunda petición: obtener todas las áreas
        $.ajax({
          url: "/rrhh/areas/",
          type: "GET",
          success: function (responseAreas) {
            console.log("Respuesta de áreas:", responseAreas);

            // Encontrar el nombre del área del usuario
            const areaUsuario = responseAreas.data.find(
              (area) => area.id_area === usuarioLogueado.id_area
            );

            console.log("Área del usuario:", areaUsuario);

            if (areaUsuario) {
              // Actualizar el select de área y seleccionar el valor
              const selectArea = $("#id_area");
              selectArea.empty();

              // Agregar opciones al select
              selectArea.append(`
                  <option value="${areaUsuario.id_area}">${areaUsuario.nombre_area}</option>
                `);

              // Seleccionar el área del usuario
              selectArea.val(areaUsuario.id_area);
            } else {
              console.error("No se encontró el área del usuario");
            }

            // Tercera petición: obtener usuarios según jerarquía
            console.log(
              "Solicitando usuarios por jerarquía para ID:",
              idUsuarioLogueado
            );

            // Asegurar que el ID de usuario es un número
            const idUsuarioNumerico = parseInt(idUsuarioLogueado, 10);

            if (isNaN(idUsuarioNumerico)) {
              console.error(
                "ID de usuario no es un número válido:",
                idUsuarioLogueado
              );
              return;
            }

            $.ajax({
              url: "/rrhh/usuarios-jerarquia/",
              type: "GET",
              data: { id_usuario: idUsuarioNumerico },
              success: function (responseJerarquia) {
                console.log("Respuesta de jerarquía:", responseJerarquia);

                // Verificar si hay datos
                if (
                  responseJerarquia.status === "success" &&
                  responseJerarquia.data &&
                  responseJerarquia.data.length > 0
                ) {
                  console.log(
                    "Ejemplo de usuario devuelto:",
                    responseJerarquia.data[0]
                  );

                  // Actualizar el select de evaluados
                  const selectEvaluado = $("#id_evaluado");
                  selectEvaluado.empty();

                  // Agregar opción por defecto
                  selectEvaluado.append(`
                      <option value="">Seleccione evaluado</option>
                    `);

                  // Agregar cada usuario según jerarquía
                  responseJerarquia.data.forEach(function (usuario) {
                    // Usar los nombres de campo exactos según el procedimiento almacenado
                    const idUsuario = usuario.id_usuario || usuario.id || "";
                    const nombre =
                      usuario.nombre_usuario || usuario.first_name || "";
                    const apellido =
                      usuario.apellido_usuario || usuario.last_name || "";
                    const cargo = usuario.cargo_descripcion || "";

                    selectEvaluado.append(`
                        <option value="${idUsuario}">
                            ${nombre} ${apellido} ${cargo ? `(${cargo})` : ""}
                        </option>
                      `);
                  });
                } else {
                  console.warn(
                    "No hay usuarios disponibles según la jerarquía"
                  );

                  // Si no hay usuarios por jerarquía, cargar usuarios de la misma área como fallback
                  const usuariosArea = responseUsuarios.data.filter(
                    (usuario) =>
                      usuario.id_area === usuarioLogueado.id_area &&
                      usuario.id.toString() !== idUsuarioLogueado
                  );

                  console.log("Usuarios del área (fallback):", usuariosArea);

                  // Cargar select de evaluados con usuarios del área
                  const selectEvaluado = $("#id_evaluado");
                  selectEvaluado.empty();
                  selectEvaluado.append(`
                      <option value="">Seleccione evaluado</option>
                    `);

                  usuariosArea.forEach((usuario) => {
                    selectEvaluado.append(`
                        <option value="${usuario.id}">
                            ${usuario.first_name} ${usuario.last_name}
                        </option>
                      `);
                  });
                }
              },
              error: function (xhr, status, error) {
                console.error(
                  "Error en la solicitud de usuarios por jerarquía:",
                  error
                );
                console.error("Estado HTTP:", xhr.status);
                console.error("Respuesta:", xhr.responseText);

                // En caso de error, cargar usuarios de la misma área como fallback
                const usuariosArea = responseUsuarios.data.filter(
                  (usuario) =>
                    usuario.id_area === usuarioLogueado.id_area &&
                    usuario.id.toString() !== idUsuarioLogueado
                );

                // Cargar select de evaluados
                const selectEvaluado = $("#id_evaluado");
                selectEvaluado.empty();
                selectEvaluado.append(`
              <option value="">Seleccione evaluado</option>
            `);

                usuariosArea.forEach((usuario) => {
                  selectEvaluado.append(`
                <option value="${usuario.id}">
                    ${usuario.first_name} ${usuario.last_name}
                </option>
              `);
                });
              },
            });
          },
          error: function (xhr, status, error) {
            console.error("Error en la solicitud de áreas:", error);
            console.error("Respuesta:", xhr.responseText);

            Swal.fire({
              icon: "error",
              title: "Error",
              text: "No se pudo obtener la información de las áreas",
            });
          },
        });
      } else {
        console.error(
          "Error en la respuesta de usuarios:",
          responseUsuarios.message
        );
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudieron cargar los usuarios",
        });
      }
    },
    error: function (xhr, status, error) {
      console.error("Error en la solicitud de usuarios:", error);
      console.error("Respuesta:", xhr.responseText);

      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudieron cargar los datos",
      });
    },
  });
}

//########################################################
//TABLA DE OBJETIVOS
//########################################################

function inicializarTablaEvaluaciones_objetivos() {
  var table = $("#tablaEvaluaciones_objetivos").DataTable({
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
        // Botón Nueva Evaluación (destacado)
        text: '<i class="fas fa-plus-circle"></i> Añadir evaluación',
        className: "btn btn-primary btn-nueva-evaluacion ms-3",

        attr: {
          "data-toggle": "modal",
          "data-target": "#Modal_Objetivos",
        },

        action: function (e, dt, node, config) {
          resetModalObjetivos();
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

    searching: true,

    // Idioma
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json",
    },

    // Ajax para obtener datos
    ajax: {
      url: "/logistica/objetivos_evaluacion/",
      type: "GET",
      data: function (d) {
        const $filtro = $('#filtroCampaniaDesempeno');

        let campania = ($filtro.length && $filtro.val())
          ? $filtro.val()
          : ('CAMP' + new Date().getFullYear());

        d.campania = campania.startsWith('CAMP') ? campania.replace('CAMP', '') : campania;
      },
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
      {
        title: "Enviar",
        data: null,
        orderable: false,
        render: function (data, type, row) {
          return `
                <div class="btn-group btn-group-sm" role="group" style="display: flex; justify-content: center;">
                    <button type="button" 
                            class="btn btn-info btn-ls" 
                            onclick="EmailManagerLogistica.generarEnviarPDFEvaluacion(${row.id})" 
                            title="Generar PDF y enviar por correo"
                            data-id-evaluacion="${row.id}">
                        <i class='bx bx-envelope-open'></i> 
                    </button>
                </div>`;
        },
      },
    ],

    createdRow: function (row, data, dataIndex) {
      $(row).css("cursor", "pointer"); // Cambia el cursor a pointer para indicar que es clickeable
      $(row).on("dblclick", function () {
        // Guardar el ID de evaluación en localStorage (como respaldo)
        // Guardar el ID de evaluación en localStorage
        localStorage.setItem("preselectedEvaluacionId", data.id);
        console.log("ID de evaluación guardado en localStorage:", data.id);

        objetivoDetalles(data.id);
      });
    },

    initComplete: function (settings, json) {
      table.columns.adjust().responsive.recalc();

      $(window).on("resize", function () {
        table.columns.adjust().responsive.recalc();
      });
    },

    destroy: true,
  });

  $('a[data-toggle="tab"]').on("shown.bs.tab", function () {
    table.columns.adjust().responsive.recalc();
  });

  return table;
}

//########################################################################################
//DETALLES DE OBJETIVOS
//########################################################################################

function inicializarTablaDetallesObjetivos(id_evaluacion) {
  var table = $("#tablaDetallesObjetivos").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        // Botón de recarga
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
        text: '<i class="fas fa-plus-circle"></i> Añadir Objetivo',
        className: "btn btn-primary btn-nuevo-objetivo ms-3",
        action: function (e, dt, node, config) {
          $("#id_evaluacion_detalle").val(id_evaluacion); // Guardamos el id_evaluacion
          $("#Modal_Nuevo_Objetivo_Detalle").modal("show");
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
      url: "/logistica/detalles_objetivos/",
      type: "GET",
      dataSrc: function (json) {
        // Filtrar los datos por id_evaluacion
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
            const iniciales = data
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
        title: "Fecha Inicio",
        data: "fecha_inicio",
      },
      {
        title: "Fecha Fin",
        data: "fecha_fin",
      },
      {
        title: "Indicador",
        data: "indicador",
      },

      {
        title: "Descripción",
        data: "descripcion",
      },
      {
        title: "Meta",
        data: "meta",
        render: function (data, type, row) {
          return `<div class="small">${data || ""}</div>`;
        },
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
                    <button type="button" class="btn btn-warning btn-sm" onclick="editarObjetivo(${row.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-danger btn-sm" onclick="eliminarObjetivo(${row.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>`;
        },
      },
    ],

    destroy: true,
  });

  // Ajustar cuando el modal se está mostrando
  $("#Modal_Detalles_Objetivos").on("show.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });

  // Ajustar cuando el modal ya está visible
  $("#Modal_Detalles_Objetivos").on("shown.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });

  return table;
}

// Función para manejar el doble click
function objetivoDetalles(id_evaluacion) {
  // Guardar el ID de evaluación en localStorage (como respaldo)
  localStorage.setItem("preselectedEvaluacionId", id_evaluacion);
  console.log("ID de evaluación guardado en objetivoDetalles:", id_evaluacion);

  // Guardar el ID de evaluación en una variable de datos del modal
  $("#Modal_Detalles_Objetivos").data("id-evaluacion", id_evaluacion);

  $("#Modal_Detalles_Objetivos").modal("show");
  inicializarTablaDetallesObjetivos(id_evaluacion);
}

//########################################################
//OBJETIVOS
//########################################################

let contadorObjetivos = 1;

function crearNuevoObjetivo() {
  contadorObjetivos++;

  const nuevoObjetivo = `
  <div class="card-body objetivo" id="objetivo-${contadorObjetivos}">
    <div class="card mb-0 shadow-sm border-left-primary">
      <div class="card-header bg-light d-flex justify-content-between align-items-center">
        <h5 class="text-primary mb-0"><i class="fas fa-star"></i> Objetivo ${contadorObjetivos}</h5>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarObjetivoForm(${contadorObjetivos})">
          <i class="fas fa-trash"></i> Eliminar
        </button>
      </div>
      <div class="card-body">
        <form id="form-objetivo-${contadorObjetivos}">
          <div class="form-group">
            <label>Descripción del Objetivo</label>
            <textarea class="form-control objetivo-descripcion" rows="3"
              placeholder="Describe el objetivo específico y medible" required></textarea>
          </div>
          <div class="form-row">
            <div class="col">
              <label>Fecha Inicio</label>
              <input type="date" class="form-control objetivo-fecha-inicio" required>
            </div>
            <div class="col">
              <label>Fecha Fin</label>
              <input type="date" class="form-control objetivo-fecha-fin" required>
            </div>
          </div>
          <div class="form-group mt-3">
            <label>Indicador de Medición</label>
            <input type="text" class="form-control objetivo-indicador" 
              placeholder="Ej: % de cumplimiento, cantidad, etc." required>
          </div>
          <div class="form-group mt-3">
            <label>Meta</label>
            <textarea class="form-control objetivo-meta" rows="2"
                placeholder="Describe la meta a alcanzar con este objetivo" required></textarea>
          </div>
          <div class="form-group mt-3" style="display: none;">
            <label>Evaluación</label>
            <div class="btn-group btn-group-toggle d-flex" data-toggle="buttons">
              <label class="btn btn-outline-danger flex-fill">
                <input type="radio" name="evaluacion-${contadorObjetivos}" 
                  class="evaluacion" value="no_cumple"> No Cumple
              </label>
              <label class="btn btn-outline-primary flex-fill">
                <input type="radio" name="evaluacion-${contadorObjetivos}" 
                  class="evaluacion" value="cumple"> Cumple
              </label>
              <label class="btn btn-outline-success flex-fill">
                <input type="radio" name="evaluacion-${contadorObjetivos}" 
                  class="evaluacion" value="excede"> Excede
              </label>
              <label class="btn btn-outline-warning flex-fill">
                <input type="radio" name="evaluacion-${contadorObjetivos}" 
                  class="evaluacion" value="sobresaliente"> Sobresaliente
              </label>
            </div>
          </div>
        </form>
      </div>
          </div>
      </div>
  `;

  $("#contenedor-objetivos").append(nuevoObjetivo);

  // Manejar el cambio de evaluación
  $(`#objetivo-${contadorObjetivos} .evaluacion`).on("change", function () {
    const form = $(this).closest("form");
    const valorSeleccionado = $(this).val();

    // Resetear todos los valores a 0
    form.data("no_cumple", 0);
    form.data("cumple", 0);
    form.data("excede", 0);
    form.data("sobresaliente", 0);

    // Establecer el valor seleccionado a 1
    form.data(valorSeleccionado, 1);
  });

  // Agregar eventos para validar fechas cuando cambien
  const nuevoObjetivoDiv = $(`#objetivo-${contadorObjetivos}`);

  nuevoObjetivoDiv
    .find(".objetivo-fecha-inicio, .objetivo-fecha-fin")
    .on("change", function () {
      validarFechasObjetivo(nuevoObjetivoDiv);
    });

  // Inicializar como no válido hasta que se ingresen fechas
  nuevoObjetivoDiv.data("fechas-validas", false);
}

// También necesitamos agregar la función para eliminar un objetivo específico
function eliminarObjetivoForm(id) {
  // Confirmar antes de eliminar
  Swal.fire({
    title: "¿Eliminar objetivo?",
    text: `¿Está seguro que desea eliminar el Objetivo ${id}?`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#dc3545",
    cancelButtonColor: "#6c757d",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Eliminar el elemento del DOM
      $(`#objetivo-${id}`).remove();

      // Renumerar los objetivos restantes
      renumerarObjetivos();

      // Notificar al usuario
      Swal.fire({
        icon: "success",
        title: "Objetivo eliminado",
        showConfirmButton: false,
        timer: 1500,
      });
    }
  });
}

// Función para renumerar los objetivos después de eliminar alguno
function renumerarObjetivos() {
  let nuevoIndice = 1;

  // Seleccionar todos los objetivos existentes
  const objetivos = document.querySelectorAll(".objetivo");

  objetivos.forEach((objetivo) => {
    // Obtener el ID actual
    const idActual = objetivo.id.split("-")[1];

    // Actualizar el título del objetivo
    const titulo = objetivo.querySelector("h5");
    if (titulo) {
      titulo.innerHTML = `<i class="fas fa-star"></i> Objetivo ${nuevoIndice}`;
    }

    // Actualizar el ID del contenedor
    objetivo.id = `objetivo-${nuevoIndice}`;

    // Actualizar el ID del formulario
    const form = objetivo.querySelector(`#form-objetivo-${idActual}`);
    if (form) {
      form.id = `form-objetivo-${nuevoIndice}`;

      // Actualizar los nombres de los radio buttons
      const radios = form.querySelectorAll('input[type="radio"]');
      radios.forEach((radio) => {
        radio.name = `evaluacion-${nuevoIndice}`;
      });
    }

    // Actualizar el botón de eliminar
    const btnEliminar = objetivo.querySelector(
      'button[onclick^="eliminarObjetivoForm"]'
    );
    if (btnEliminar) {
      btnEliminar.setAttribute(
        "onclick",
        `eliminarObjetivoForm(${nuevoIndice})`
      );
    }

    nuevoIndice++;
  });

  // Actualizar el contador global
  contadorObjetivos = nuevoIndice - 1;
}

//GUARDAR NUEVO OBJETIVO

function guardarObjetivoYSiguiente() {
  // Recopilar datos de la evaluación
  const datosEvaluacion = {
    id_evaluador: $("#id_evaluador").val(),
    id_evaluado: $("#id_evaluado").val(),
    periodo: $("#periodo_objetivos option:selected").val(),
    id_area: $("#id_area option:selected").val(),
  };

  // Validación de datos de evaluación
  if (
    !datosEvaluacion.id_evaluador ||
    !datosEvaluacion.id_evaluado ||
    !datosEvaluacion.periodo ||
    !datosEvaluacion.id_area
  ) {
    Swal.fire({
      icon: "warning",
      title: "Campos Incompletos",
      text: "Por favor, complete todos los campos de la evaluación",
      confirmButtonText: "Aceptar",
    });
    return;
  }

  // Validar todas las fechas de objetivos
  const fechasValidas = validarFechasTodosObjetivos();

  if (!fechasValidas) {
    Swal.fire({
      icon: "error",
      title: "Fechas inválidas",
      text: "Por favor revise las fechas de los objetivos",
    });
    return;
  }

  // Verificar si ya existe una evaluación para este evaluado en el mismo periodo
  const periodoARegistrar = datosEvaluacion.periodo;

  // Verificar si ya existe una evaluación para este evaluado
  $.ajax({
    url: "/losgistica/objetivos_evaluacion/?campania="+ periodoARegistrar,
    type: "GET",
    success: function (response) {
      if (response.status === "success") {
        // Convertir a número para hacer la comparación correcta
        const idEvaluadoARegistrar = parseInt(datosEvaluacion.id_evaluado);

        // Buscar si existe una evaluación para este evaluado usando id_evaluado
        const evaluacionExistente = response.data.find(
          (eval) => parseInt(eval.id_evaluado) === idEvaluadoARegistrar &&
                    eval.periodo === periodoARegistrar
        );

        if (evaluacionExistente) {
          // Ya existe una evaluación, preguntamos si quiere continuar a la parte de competencias
          Swal.fire({
            icon: "info",
            title: "Evaluación Existente",
            text: `Ya existe una evaluación para este colaborador en el periodo ${periodoARegistrar}. ¿Desea ir directamente a registrar competencias?`,
            showCancelButton: true,
            confirmButtonText: "Sí, ir a competencias",
            cancelButtonText: "No, cancelar",
            confirmButtonColor: "#28a745",
          }).then((result) => {
            if (result.isConfirmed) {
              // Cerrar el modal actual
              $("#Modal_Objetivos").modal("hide");

              // Abrir el modal de competencias y pre-seleccionar el evaluado
              setTimeout(() => {
                abrirModalCompetenciasConEvaluado(datosEvaluacion.id_evaluado);
              }, 500);
            }
          });
          return;
        }

        // Si no existe evaluación, continuar con el proceso de guardado
        continuarGuardadoYSiguiente(datosEvaluacion);
      } else {
        // Si hay un error en la respuesta, continuar de todas formas
        console.warn("No se pudo verificar evaluaciones existentes, continuando...");
        continuarGuardadoYSiguiente(datosEvaluacion);
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al verificar evaluaciones:", error);
      console.error("Respuesta del servidor:", xhr.responseText);
      
      // En lugar de mostrar error, continuar con el guardado
      // El backend hará la validación final
      Swal.fire({
        icon: "warning",
        title: "Advertencia",
        text: "No se pudo verificar evaluaciones previas. ¿Desea continuar de todas formas?",
        showCancelButton: true,
        confirmButtonText: "Sí, continuar",
        cancelButtonText: "No, cancelar",
        confirmButtonColor: "#ffc107",
      }).then((result) => {
        if (result.isConfirmed) {
          continuarGuardadoYSiguiente(datosEvaluacion);
        }
      });
    },
  });
}

function continuarGuardadoYSiguiente(datosEvaluacion) {
  const objetivos = [];

  // Recopilar datos de TODOS los objetivos
  $("[id^='objetivo-']").each(function () {
    const form = $(this).find("form");

    const objetivo = {
      descripcion: form.find(".objetivo-descripcion").val(),
      fecha_inicio: form.find(".objetivo-fecha-inicio").val(),
      fecha_fin: form.find(".objetivo-fecha-fin").val(),
      indicador: form.find(".objetivo-indicador").val(),
      meta: form.find(".objetivo-meta").val(),
      no_cumple:
        form.find(`input[name^='evaluacion-']:checked`).val() === "no_cumple"
          ? 1
          : 0,
      cumple:
        form.find(`input[name^='evaluacion-']:checked`).val() === "cumple"
          ? 1
          : 0,
      excede:
        form.find(`input[name^='evaluacion-']:checked`).val() === "excede"
          ? 1
          : 0,
      sobresaliente:
        form.find(`input[name^='evaluacion-']:checked`).val() ===
        "sobresaliente"
          ? 1
          : 0,
    };

    if (
      objetivo.descripcion &&
      objetivo.fecha_inicio &&
      objetivo.fecha_fin &&
      objetivo.indicador
    ) {
      objetivos.push(objetivo);
    }
  });

  if (objetivos.length === 0) {
    Swal.fire({
      icon: "warning",
      title: "Campos Incompletos",
      text: "Por favor, complete al menos un objetivo con todos sus campos",
      confirmButtonText: "Aceptar",
    });
    return;
  }

  const datosCompletos = {
    ...datosEvaluacion,
    objetivos: objetivos,
  };

  // Mostrar loading mientras se guarda
  Swal.fire({
    title: "Guardando objetivos...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Enviar al servidor
  $.ajax({
    url: "/logistica/detalles_objetivos/",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(datosCompletos),
    headers: {
      "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
    },
    success: function (response) {
      if (response.status === "success") {
        // Si la respuesta no incluye el ID de evaluación, lo buscamos
        if (!response.data || !response.data.id_evaluacion) {
          // Buscar el ID de la evaluación recién creada
          $.ajax({
            url: "/logistica/objetivos_evaluacion/",
            type: "GET",
            success: function (responseEvaluaciones) {
              if (responseEvaluaciones.status === "success") {
                // Buscar la evaluación del evaluado actual
                const idEvaluado = datosEvaluacion.id_evaluado;
                const evaluacion = responseEvaluaciones.data.find(
                  (item) =>
                    item.id_evaluado.toString() === idEvaluado.toString()
                );

                if (evaluacion) {
                  const idEvaluacion = evaluacion.id;

                  // Cerrar el modal de loading
                  Swal.close();

                  // Guardar ID de evaluación para competencias
                  localStorage.setItem("preselectedEvaluacionId", idEvaluacion);

                  // Mostrar mensaje de éxito
                  Swal.fire({
                    icon: "success",
                    title: "¡Éxito!",
                    text: "Objetivos guardados correctamente. Continuando con competencias...",
                    showConfirmButton: false,
                    timer: 1500,
                  });

                  // Cerrar modal y actualizar tabla
                  $("#Modal_Objetivos").modal("hide");
                  if (
                    typeof inicializarTablaEvaluaciones_objetivos === "function"
                  ) {
                    inicializarTablaEvaluaciones_objetivos();
                  }

                  // Abrir modal de competencias
                  setTimeout(() => {
                    abrirModalCompetenciasConEvaluado(idEvaluado, idEvaluacion);
                  }, 1600);
                } else {
                  Swal.fire({
                    icon: "warning",
                    title: "Advertencia",
                    text: "No se pudo encontrar la información de la evaluación. Intente nuevamente.",
                    confirmButtonText: "Aceptar",
                  });
                }
              }
            },
            error: function (xhr, status, error) {
              Swal.fire({
                icon: "error",
                title: "Error",
                text: "Error al recuperar datos de la evaluación",
                confirmButtonText: "Aceptar",
                confirmButtonColor: "#dc3545",
              });
            },
          });
        } else {
          // Si la respuesta incluye el ID de evaluación, lo usamos directamente
          const idEvaluacion = response.data.id_evaluacion;

          // Cerrar el modal de loading
          Swal.close();

          // Guardar ID de evaluación para competencias
          localStorage.setItem("preselectedEvaluacionId", idEvaluacion);

          // Mostrar mensaje de éxito
          Swal.fire({
            icon: "success",
            title: "¡Éxito!",
            text: "Objetivos guardados correctamente. Continuando con competencias...",
            showConfirmButton: false,
            timer: 1500,
          });

          // Cerrar modal y actualizar tabla
          $("#Modal_Objetivos").modal("hide");
          if (typeof inicializarTablaEvaluaciones_objetivos === "function") {
            inicializarTablaEvaluaciones_objetivos();
          }

          // Abrir modal de competencias
          setTimeout(() => {
            abrirModalCompetenciasConEvaluado(
              datosEvaluacion.id_evaluado,
              idEvaluacion
            );
          }, 1600);
        }
      } else {
        // Cerrar el modal de loading
        Swal.close();

        // Mostrar mensaje de error
        Swal.fire({
          icon: "error",
          title: "Error",
          text: response.message || "Error al guardar los objetivos",
          confirmButtonText: "Aceptar",
          confirmButtonColor: "#dc3545",
        });
      }
    },
    error: function (xhr, status, error) {
      // Cerrar el modal de loading
      Swal.close();

      // Mostrar mensaje de error
      Swal.fire({
        icon: "error",
        title: "¡Error!",
        text: "Hubo un problema al guardar los objetivos. Por favor, inténtelo nuevamente.",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#dc3545",
      });
    },
  });
}

function abrirModalCompetenciasConEvaluado(idEvaluado, idEvaluacion) {
  console.log("ID de la evaluación antes de guardar:", idEvaluacion);

  // Guardar el ID de la evaluación en localStorage
  localStorage.setItem("preselectedEvaluacionId", idEvaluacion);

  // Abrir el modal de competencias
  $("#modalCompetencias").modal("show");
}

//##############################################################
function guardarNuevoObjetivoDetalle() {
  // Obtener el valor de evaluación seleccionado
  const evaluacionSeleccionada = $(
    'input[name="evaluacion_detalle"]:checked'
  ).val();

  // Crear objeto con los datos del formulario
  const nuevoObjetivo = {
    id_evaluacion: $("#id_evaluacion_detalle").val(),
    descripcion: $("#descripcion_detalle").val(),
    fecha_inicio: $("#fecha_inicio_detalle").val(),
    fecha_fin: $("#fecha_fin_detalle").val(),
    indicador: $("#indicador_detalle").val(),
    meta: $("#meta_detalle").val(),
    no_cumple: evaluacionSeleccionada === "no_cumple" ? 1 : 0,
    cumple: evaluacionSeleccionada === "cumple" ? 1 : 0,
    excede: evaluacionSeleccionada === "excede" ? 1 : 0,
    sobresaliente: evaluacionSeleccionada === "sobresaliente" ? 1 : 0,
  };

  // Validar que todos los campos requeridos estén llenos
  if (
    !nuevoObjetivo.descripcion ||
    !nuevoObjetivo.fecha_inicio ||
    !nuevoObjetivo.fecha_fin ||
    !nuevoObjetivo.indicador
  ) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Por favor, complete todos los campos requeridos",
    });
    return;
  }

  // Enviar datos al servidor
  $.ajax({
    url: "/logistica/detalles_objetivos/",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(nuevoObjetivo),
    success: function (response) {
      if (response.status === "success") {
        Swal.fire({
          icon: "success",
          title: "Éxito",
          text: "Objetivo guardado correctamente",
        }).then(() => {
          // Cerrar el modal
          $("#Modal_Nuevo_Objetivo_Detalle").modal("hide");
          // Limpiar el formulario
          $("#form-nuevo-objetivo-detalle")[0].reset();
          // Recargar la tabla de detalles
          $("#tablaDetallesObjetivos").DataTable().ajax.reload();
        });

        // Actualizar ambas tablas después de guardar exitosamente
        $("#tablaObjetivos").DataTable().ajax.reload();
        $("#tablaDetallesObjetivos").DataTable().ajax.reload();
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: response.message || "Error al guardar el objetivo",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text:
          "Error al guardar el objetivo: " +
          (xhr.responseJSON?.message || error),
      });
    },
  });
}

/*  ELIMINAR OBJETIVO */

function eliminarObjetivo(id) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "Si es el último objetivo, se eliminará la evaluación completa (siempre que no haya competencias asociadas)",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: `/logistica/detalles_objetivos/${id}/`,
        type: "DELETE",
        headers: {
          "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
          let mensaje = response.message;
          let icono = "success";

          // Si se eliminó también la evaluación, personalizar el mensaje
          if (response.data.evaluacion_eliminada) {
            mensaje = "Se eliminó el objetivo y la evaluación completa";
          }

          Swal.fire({
            icon: icono,
            title: "¡Eliminado!",
            text: mensaje,
            showConfirmButton: false,
            timer: 1500,
          }).then(() => {
            // Recargar ambas tablas después de la eliminación
            $("#tablaObjetivos").DataTable().ajax.reload();
            $("#tablaDetallesObjetivos").DataTable().ajax.reload();

            // Recargar la tabla de evaluaciones si existe la función
            if (typeof inicializarTablaEvaluaciones_objetivos === "function") {
              inicializarTablaEvaluaciones_objetivos();
            }
          });
        },
        error: function (xhr, status, error) {
          let errorMessage = "Error al eliminar el objetivo";

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
            confirmButtonColor: "#d33",
          });
        },
      });
    }
  });
}

/* EDITAR OBJETIVO*/

// Función para editar objetivo
function editarObjetivo(id) {
  // Mostrar loading
  Swal.fire({
    title: "Cargando...",
    html: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Realizar la petición AJAX para obtener los datos del objetivo
  $.ajax({
    url: `/logistica/detalles_objetivos/${id}/`,
    type: "GET",

    success: function (response) {
      // Cerrar loading
      Swal.close();

      if (response.status === "success") {
        const objetivo = response.data[0]; // Acceder al primer elemento del array

        // Llenar los campos ocultos
        $("#edit_objetivo_id").val(objetivo.id);
        $("#edit_id_evaluado").val(objetivo.id_evaluacion);

        // Hacer petición para obtener datos del evaluado
        $.ajax({
          url: "/logistica/detalles_objetivos/",
          type: "GET",
          success: function (response) {
            const evaluado = response.data.find((item) => item.id === id);
            if (evaluado) {
              $("#edit_evaluado_nombre").val(
                `${evaluado.nombre_evaluado} ${evaluado.apellido_evaluado}`
              );
            }
          },
        });

        // Llenar los campos editables
        $("#edit_descripcion").val(objetivo.descripcion);
        $("#edit_fecha_inicio").val(objetivo.fecha_inicio);
        $("#edit_fecha_fin").val(objetivo.fecha_fin);
        $("#edit_indicador").val(objetivo.indicador);
        $("#edit_meta").val(objetivo.meta);

        // Primero, desmarcar todos los radio buttons y quitar la clase active
        $('input[name="edit_evaluacion"]')
          .prop("checked", false)
          .closest("label")
          .removeClass("active");

        // Luego, marcar solo si el valor es 1
        if (objetivo.no_cumple === 1) {
          $('input[name="edit_evaluacion"][value="no_cumple"]')
            .prop("checked", true)
            .closest("label")
            .addClass("active");
        } else if (objetivo.cumple === 1) {
          $('input[name="edit_evaluacion"][value="cumple"]')
            .prop("checked", true)
            .closest("label")
            .addClass("active");
        } else if (objetivo.excede === 1) {
          $('input[name="edit_evaluacion"][value="excede"]')
            .prop("checked", true)
            .closest("label")
            .addClass("active");
        } else if (objetivo.sobresaliente === 1) {
          $('input[name="edit_evaluacion"][value="sobresaliente"]')
            .prop("checked", true)
            .closest("label")
            .addClass("active");
        }

        // Mostrar el modal
        $("#Modal_Editar_Objetivo").modal("show");
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text:
            response.message || "No se pudo cargar la información del objetivo",
        });
      }
    },
    error: function (xhr, status, error) {
      // Cerrar loading
      Swal.close();

      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo cargar la información del objetivo",
      });
    },
  });
}

function actualizarObjetivo() {
  // Obtener los valores del formulario
  const datosObjetivo = {
    id: $("#edit_objetivo_id").val(),
    id_evaluacion: $("#edit_id_evaluado").val(),
    descripcion: $("#edit_descripcion").val().trim(),
    fecha_inicio: $("#edit_fecha_inicio").val(),
    fecha_fin: $("#edit_fecha_fin").val(),
    indicador: $("#edit_indicador").val().trim(),
    meta: $("#edit_meta").val().trim(),
    no_cumple: 0,
    cumple: 0,
    excede: 0,
    sobresaliente: 0,
  };

  // Obtener el valor de la evaluación seleccionada
  const evaluacionSeleccionada = $(
    'input[name="edit_evaluacion"]:checked'
  ).val();
  if (evaluacionSeleccionada) {
    datosObjetivo[evaluacionSeleccionada] = 1;
  }

  // Validación de campos requeridos
  if (
    !datosObjetivo.descripcion ||
    !datosObjetivo.fecha_inicio ||
    !datosObjetivo.fecha_fin ||
    !datosObjetivo.indicador
  ) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Por favor complete todos los campos requeridos",
    });
    return;
  }

  // Mostrar loading
  Swal.fire({
    title: "Guardando cambios...",
    html: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Realizar la petición AJAX
  $.ajax({
    url: `/logistica/detalles_objetivos/${datosObjetivo.id}/`,
    type: "PUT",
    contentType: "application/json",
    data: JSON.stringify(datosObjetivo),
    headers: {
      "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
    },
    success: function (response) {
      Swal.close();

      if (response.status === "success") {
        // Cerrar el modal
        $("#Modal_Editar_Objetivo").modal("hide");

        // Mostrar mensaje de éxito
        Swal.fire({
          icon: "success",
          title: "¡Actualizado!",
          text: "El objetivo se actualizó correctamente",
          showConfirmButton: false,
          timer: 1500,
        });

        // Recargar la tabla
        if (typeof inicializarTablaEvaluaciones_objetivos === "function") {
          inicializarTablaEvaluaciones_objetivos();
        }

        // Actualizar la tabla de detalles si existe
        if ($.fn.DataTable.isDataTable("#tablaDetallesObjetivos")) {
          $("#tablaDetallesObjetivos").DataTable().ajax.reload();
        }
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: response.message || "No se pudo actualizar el objetivo",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.close();

      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo actualizar el objetivo. Por favor, intente nuevamente.",
      });
    },
  });
}

function resetModalObjetivos() {
  // Resetear solo los campos que deben limpiarse
  $("#id_evaluado").val("");
  // Tomar el período del filtro principal automáticamente
  const periodoFiltro = $('#filtroCampaniaDesempeno').val() || new Date().getFullYear();
  $("#periodo_objetivos").val(periodoFiltro);

  // Eliminar todos los objetivos excepto el primero
  $(".objetivo").not("#objetivo-1").remove();

  // Limpiar los campos del primer objetivo
  const primerObjetivo = $("#objetivo-1");
  primerObjetivo.find("textarea.objetivo-descripcion").val("");
  primerObjetivo.find("input.objetivo-fecha-inicio").val("");
  primerObjetivo.find("input.objetivo-fecha-fin").val("");
  primerObjetivo.find("input.objetivo-indicador").val("");
  primerObjetivo.find("textarea.objetivo-meta").val("");
  primerObjetivo.find("input[type='radio']").prop("checked", false);
  primerObjetivo.find(".btn-group label").removeClass("active");

  // Si el primer objetivo no tiene el botón Eliminar (porque es el objetivo inicial del HTML),
  // asegurarnos de que se vea igual que los otros objetivos
  if (primerObjetivo.find(".card-header button").length === 0) {
    primerObjetivo
      .find(".card-header")
      .addClass("d-flex justify-content-between align-items-center");
    primerObjetivo.find(".card-header").append(`
      <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarObjetivoForm(1)" style="display:none;">
        <i class="fas fa-trash"></i> Eliminar
      </button>
    `);
  }

  // Resetear el contador de objetivos
  contadorObjetivos = 1;
}

/*###################################################*/
/* VALIDAR FECHAS DE OBJETIVOS */
/*###################################################*/

function validarFechasObjetivo(objetivoDiv) {
  const objetivoForm = objetivoDiv.find("form");
  const objetivoId = objetivoDiv.attr("id").split("-")[1];

  // Obtener los campos de fecha
  const fechaInicioInput = objetivoForm.find(".objetivo-fecha-inicio");
  const fechaFinInput = objetivoForm.find(".objetivo-fecha-fin");

  // Obtener los valores
  const fechaInicio = fechaInicioInput.val();
  const fechaFin = fechaFinInput.val();

  // Obtener el periodo seleccionado
  const periodo = $("#periodo_objetivos").val();
  let anioPeriodo = new Date().getFullYear(); // Valor por defecto: año actual

  // Si hay un periodo seleccionado, usarlo
  if (periodo) {
    anioPeriodo = parseInt(periodo);
  }

  // Fecha actual para comparar
  const fechaActual = new Date();
  fechaActual.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fechas

  // Crear objetos Date para las fechas ingresadas
  const fechaInicioObj = fechaInicio ? new Date(fechaInicio) : null;
  const fechaFinObj = fechaFin ? new Date(fechaFin) : null;

  // Límites del periodo
  const inicioAno = new Date(anioPeriodo, 0, 1); // 1 de enero del periodo
  const finAno = new Date(anioPeriodo, 11, 31); // 31 de diciembre del periodo

  // Eliminar mensajes de error previos
  objetivoForm.find(".fecha-error").remove();
  objetivoForm.find(".fecha-success").remove();

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
        `<div class="fecha-error text-danger small">La fecha de inicio debe estar dentro del periodo ${anioPeriodo}</div>`
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
        `<div class="fecha-error text-danger small">La fecha de fin debe estar dentro del periodo ${anioPeriodo}</div>`
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

  // Actualizar el estado de validación en el div del objetivo
  objetivoDiv.data("fechas-validas", esValido);

  return esValido;
}

function validarFechasTodosObjetivos() {
  let todasValidas = true;

  // Recorrer todos los objetivos y validar sus fechas
  $(".objetivo").each(function () {
    const esValido = validarFechasObjetivo($(this));
    if (!esValido) {
      todasValidas = false;
    }
  });

  return todasValidas;
}

const EmailManagerLogistica = {
  // Configuración del módulo específica para Almacén
  config: {
    endpoints: {
      evaluaciones: "/logistica/objetivos_evaluacion/",
      detallesObjetivos: "/logistica/detalles_objetivos/",
    },
    scripts: {
      competenciasPaths: [
        "/static/core/js/LOGISTICA/DonLuis/rrhh_ev_competencias.js",
        
      ],
    },
    messages: {
      confirmation: {
        title: "Confirmación - LOGISTICA",
        text: "¿Desea generar el PDF de esta evaluación y enviarlo por correo desde el módulo de RRHH?",
        confirmButtonText: "Sí, generar y enviar",
        cancelButtonText: "Cancelar",
      },
      loading: {
        title: "Procesando - LOGISTICA",
        text: "Generando PDF desde LOGISTICA y preparando envío...",
      },
      errors: {
        invalidId: "No se pudo identificar la evaluación en LOGISTICA",
        scriptLoad: "No se pudo cargar el script necesario para generar el PDF",
        functionNotFound:
          "No se pudo cargar la funcionalidad de generación de PDF",
      },
    },
    metadata: {
      modulo: "LOGISTICA",
      version: "1.0.0",
      descripcion:
        "Gestión de correos para evaluaciones de objetivos - LOGISTICA",
    },
  },

  /**
   * Valida que el ID de evaluación sea válido
   * @param {number|string} idEvaluacion - ID de la evaluación
   * @returns {boolean} - True si es válido, false en caso contrario
   */
  validarIdEvaluacion(idEvaluacion) {
    return idEvaluacion && !isNaN(parseInt(idEvaluacion));
  },

  /**
   * Muestra mensajes de error de forma consistente
   * @param {string} mensaje - Mensaje a mostrar
   */
  mostrarError(mensaje) {
    Swal.fire({
      icon: "error",
      title: "Error - Gerencia",
      text: mensaje,
      confirmButtonColor: "#dc3545",
      footer: `<small>Módulo: ${this.config.metadata.modulo}</small>`,
    });
  },

  /**
   * Muestra el diálogo de confirmación antes de generar el PDF
   * @param {function} callback - Función a ejecutar si el usuario confirma
   */
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
      if (result.isConfirmed) {
        callback();
      }
    });
  },

  /**
   * Muestra el indicador de carga mientras se procesa
   */
  mostrarCarga() {
    const { loading } = this.config.messages;

    Swal.fire({
      title: loading.title,
      text: loading.text,
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });
  },

  /**
   * Verifica si la función de generación de PDF está disponible
   * @returns {boolean} - True si está disponible, false en caso contrario
   */
  esFuncionPDFDisponible() {
    return typeof generarPDFEvaluacion === "function";
  },

  /**
   * Intenta cargar los scripts de competencias de forma secuencial
   * @param {number} idEvaluacion - ID de la evaluación
   * @param {number} intentoActual - Intento actual (para recursión)
   */
  cargarScriptCompetencias(idEvaluacion, intentoActual = 0) {
    const { scripts } = this.config;

    if (intentoActual >= scripts.competenciasPaths.length) {
      this.mostrarError(this.config.messages.errors.scriptLoad);
      return;
    }

    const scriptPath = scripts.competenciasPaths[intentoActual];

    // Log del intento de carga específico para Almacén
    console.log(
      `[Almacén] Intentando cargar script ${intentoActual + 1}/${
        scripts.competenciasPaths.length
      }: ${scriptPath}`
    );

    $.getScript(scriptPath)
      .done(() => {
        console.log(`[Almacén] Script cargado exitosamente: ${scriptPath}`);
        if (this.esFuncionPDFDisponible()) {
          this.ejecutarGeneracionPDF(idEvaluacion);
        } else {
          // Intentar con el siguiente script
          this.cargarScriptCompetencias(idEvaluacion, intentoActual + 1);
        }
      })
      .fail(() => {
        console.warn(`[Almacén] Falló la carga del script: ${scriptPath}`);
        // Intentar con el siguiente script
        this.cargarScriptCompetencias(idEvaluacion, intentoActual + 1);
      });
  },

  /**
   * Ejecuta la generación del PDF una vez que la función está disponible
   * @param {number} idEvaluacion - ID de la evaluación
   */
  ejecutarGeneracionPDF(idEvaluacion) {
    if (this.esFuncionPDFDisponible()) {
      console.log(
        `[Almacén] Ejecutando generación de PDF para evaluación ID: ${idEvaluacion}`
      );
      generarPDFEvaluacion(idEvaluacion);
    } else {
      this.mostrarError(this.config.messages.errors.functionNotFound);
    }
  },

  /**
   * Procesa la generación y envío del PDF
   * @param {number} idEvaluacion - ID de la evaluación
   */
  procesarGeneracionPDF(idEvaluacion) {
    this.mostrarCarga();

    if (this.esFuncionPDFDisponible()) {
      // La función ya está disponible, ejecutar directamente
      console.log(`[Almacén] Función PDF disponible, ejecutando directamente`);
      this.ejecutarGeneracionPDF(idEvaluacion);
    } else {
      // Necesitamos cargar los scripts
      console.log(`[Almacén] Función PDF no disponible, cargando scripts...`);
      this.cargarScriptCompetencias(idEvaluacion);
    }
  },

  /**
   * Función principal para generar PDF y enviar por correo
   * @param {number} idEvaluacion - ID de la evaluación
   */
  generarEnviarPDFEvaluacion(idEvaluacion) {
    

    // Validar entrada
    if (!this.validarIdEvaluacion(idEvaluacion)) {
      this.mostrarError(this.config.messages.errors.invalidId);
      return;
    }

    // Convertir a número para asegurar tipo correcto
    const id = parseInt(idEvaluacion);

    // Mostrar confirmación y proceder si el usuario acepta
    this.mostrarConfirmacion(() => {
      this.procesarGeneracionPDF(id);
    });
  },

  /**
   * Registra eventos globales para tracking y analytics
   */
  registrarEventosGlobales() {
    // Registrar clicks en botones de envío para analytics específicos de Almacén
    $(document).on("click", "[data-id-evaluacion]", function () {
      const idEvaluacion = $(this).data("id-evaluacion");
      console.log(
        `[Almacén] Usuario intentó enviar PDF para evaluación ID: ${idEvaluacion}`
      );

      // Aquí se puede añadir lógica de analytics específica para Almacén
      if (typeof gtag !== "undefined") {
        gtag("event", "pdf_email_request", {
          event_category: "almacen",
          event_label: "evaluacion_objetivos",
          value: idEvaluacion,
        });
      }
    });
  },

  /**
   * Método para extender la configuración de manera dinámica
   * @param {Object} nuevaConfig - Nueva configuración a añadir
   */
  extenderConfiguracion(nuevaConfig) {
    this.config = { ...this.config, ...nuevaConfig };
    console.log(
      `[Almacén] Configuración de EmailManager actualizada`,
      nuevaConfig
    );
  },

  /**
   * Método para obtener estadísticas de uso (extensible)
   */
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

  /**
   * Método para verificar la salud del módulo
   */
  verificarSalud() {
    const salud = {
      modulo: this.config.metadata.modulo,
      estado: "OK",
      problemas: [],
      recomendaciones: [],
    };

    // Verificar jQuery
    if (typeof $ === "undefined") {
      salud.estado = "ERROR";
      salud.problemas.push("jQuery no está disponible");
    }

    // Verificar SweetAlert2
    if (typeof Swal === "undefined") {
      salud.estado = "ERROR";
      salud.problemas.push("SweetAlert2 no está disponible");
    }

    // Verificar función PDF
    if (!this.esFuncionPDFDisponible()) {
      salud.estado = "WARNING";
      salud.problemas.push("Función de generación de PDF no disponible");
      salud.recomendaciones.push(
        "Los scripts de competencias se cargarán dinámicamente cuando sea necesario"
      );
    }

    return salud;
  },

  /**
   * Registra eventos globales para el módulo
   */
  inicializar() {
    console.log(`[Almacén] EmailManager inicializado correctamente`);
    console.log(`[Almacén] Configuración:`, this.config.metadata);

    // Verificar salud del módulo
    const salud = this.verificarSalud();
    console.log(`[Almacén] Estado del módulo:`, salud);

    if (salud.estado === "ERROR") {
      console.error(`[Almacén] Errores críticos detectados:`, salud.problemas);
    } else if (salud.estado === "WARNING") {
      console.warn(`[Almacén] Advertencias detectadas:`, salud.problemas);
    }

    // Registrar eventos globales
    this.registrarEventosGlobales();

    // Estadísticas iniciales
    const stats = this.obtenerEstadisticas();
    console.log(`[Almacén] Estadísticas del módulo:`, stats);
  },
};



document.addEventListener("DOMContentLoaded", function () {

  // Inicializar el módulo de gestión de correos electrónicos para LOGISTICA
  EmailManagerLogistica.inicializar();
  // Inicializar la tabla de evaluaciones de objetivos
  inicializarTablaEvaluaciones_objetivos();

  // Cargar evaluados y área
  cargarEvaluadosYArea();

  // Cargar usuarios evaluados
  cargarUsuariosEvaluados();

  // Inicializar validación para objetivos cuando se muestra el modal
  $("#Modal_Objetivos").on("shown.bs.modal", function () {
    // Inicializar la validación para el primer objetivo
    const primerObjetivo = $("#objetivo-1");

    // Agregar eventos para validar fechas cuando cambien
    primerObjetivo
      .find(".objetivo-fecha-inicio, .objetivo-fecha-fin")
      .on("change", function () {
        validarFechasObjetivo(primerObjetivo);
      });

    // Inicializar como no válido hasta que se ingresen fechas
    primerObjetivo.data("fechas-validas", false);

    // Validar fechas cada vez que cambia el periodo
    $("#periodo_objetivos")
      .off("change")
      .on("change", function () {
        // Validar fechas de todos los objetivos cuando cambia el periodo
        validarFechasTodosObjetivos();
      });
  });

  // Resetear el modal cuando se cierra
  $("#Modal_Objetivos").on("hidden.bs.modal", function () {
    resetModalObjetivos();
  });

  // Usar el evento correcto para las pestañas de Bootstrap
  $("#competencias-tab").on("shown.bs.tab", function (e) {
    // Obtener el ID de evaluación guardado en el modal
    const id_evaluacion = $("#Modal_Detalles_Objetivos").data("id-evaluacion");

    // Inicializar la tabla de detalles de competencias
    inicializarTablaDetallesCompetencias(id_evaluacion);
  });

  // Inicializar validación de fechas para edición de objetivos
  $("#Modal_Editar_Objetivo").on("shown.bs.modal", function () {
    // Agregar eventos para validar fechas cuando se editan
    $("#edit_fecha_inicio, #edit_fecha_fin").on("change", function () {
      validarFechasObjetivoEdicion();
    });
  });

  // Inicializar validación para objetivo nuevo en detalles
  $("#Modal_Nuevo_Objetivo_Detalle").on("shown.bs.modal", function () {
    // Agregar eventos para validar fechas
    $("#fecha_inicio_detalle, #fecha_fin_detalle").on("change", function () {
      validarFechasObjetivoDetalle();
    });
  });
});
