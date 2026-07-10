// Variables globales para mantener el estado
let usuarioActual = null;
let areaUsuario = null;
let esJefe = false;

// Función para configurar el campo evaluador
function configurarCampoEvaluador(usuario) {
  const selectEvaluador = document.getElementById("evaluador");

  // Limpiar opciones existentes
  selectEvaluador.innerHTML =
    '<option value="">Seleccione evaluador...</option>';

  // Crear y agregar la opción con el nombre del evaluador
  const optionEvaluador = new Option(
    `${usuario.first_name} ${usuario.last_name}`,
    usuario.id,
    true,
    true
  );
  selectEvaluador.appendChild(optionEvaluador);

  // Deshabilitar el select
  selectEvaluador.disabled = true;
}

// Función para cargar usuarios de la misma área en el campo evaluado
function cargarUsuariosArea(usuarios) {
  const selectEvaluado = document.getElementById("evaluado");

  // Limpiar opciones existentes
  selectEvaluado.innerHTML = '<option value="">Seleccione empleado...</option>';

  // Filtrar usuarios de la misma área, excluyendo al usuario actual
  const usuariosArea = usuarios.filter(
    (usuario) =>
      usuario.id_area === areaUsuario && // Misma área
      usuario.id !== usuarioActual.id && // No es el usuario actual
      usuario.estado === true // Usuario activo
  );

  // Ordenar alfabéticamente por nombre
  usuariosArea.sort((a, b) =>
    `${a.first_name} ${a.last_name}`.localeCompare(
      `${b.first_name} ${b.last_name}`
    )
  );

  // Agregar cada usuario como opción
  usuariosArea.forEach((usuario) => {
    const option = new Option(
      `${usuario.first_name} ${usuario.last_name}`,
      usuario.id
    );
    selectEvaluado.appendChild(option);
  });

  // Para debug
  console.log("Usuarios del área:", usuariosArea);
}

async function cargarDatosEvaluador(idUsuario) {
  try {
    // Cargar datos del usuario y su área
    const responseUsuario = await fetch(`/rrhh/usuario-area/`);
    const dataUsuario = await responseUsuario.json();

    if (dataUsuario.status === "success" && dataUsuario.data.length > 0) {
      // Buscar el usuario actual en la lista de usuarios
      const usuario = dataUsuario.data.find(
        (user) => user.id.toString() === idUsuario
      );

      if (usuario) {
        usuarioActual = usuario;

        // Debug: Mostrar información del usuario encontrado
        console.log("Usuario encontrado:", {
          nombre: `${usuario.first_name} ${usuario.last_name}`,
          id: usuario.id,
          id_area: usuario.id_area,
        });

        // Validar que id_area exista y sea un número
        if (usuario.id_area && !isNaN(usuario.id_area)) {
          areaUsuario = parseInt(usuario.id_area);
          console.log("ID del área del usuario (parseado):", areaUsuario);

          // Cargar datos de las áreas
          const responseAreas = await fetch(`/rrhh/areas/`);
          const dataAreas = await responseAreas.json();
          console.log("Areas", dataAreas);

          if (dataAreas.data) {
            const area = dataAreas.data.find((a) => a.id_area == areaUsuario);
            console.log("Área encontrada:", area);

            if (area) {
              $("#nombre_area").val(area.nombre_area);
              console.log("Valor asignado al campo área:", area.nombre_area);
            } else {
              console.error("Área no encontrada para ID:", areaUsuario);
              $("#nombre_area").val("Área no encontrada");
            }
          }
        } else {
          console.error("ID de área inválido o no presente:", {
            id_area: usuario.id_area,
            tipo: typeof usuario.id_area,
          });
          $("#nombre_area").val("ID de área inválido");
        }

        esJefe = usuario.es_jefe;
        configurarCampoEvaluador(usuario);
        cargarUsuariosArea(dataUsuario.data);
      } else {
        console.error("No se encontró usuario con ID:", idUsuario);
        mostrarError("Usuario no encontrado");
        $("#nombre_area").val("");
      }
    } else {
      console.error("Respuesta de API sin datos:", dataUsuario);
      mostrarError("No se encontraron datos de usuarios");
      $("#nombre_area").val("");
    }
  } catch (error) {
    console.error("Error al cargar datos del evaluador:", error);
    mostrarError("Error al cargar datos del evaluador");
    $("#nombre_area").val("Error al cargar datos");
  }
}

// Función de utilidad para mostrar errores
function mostrarError(mensaje) {
  Swal.fire({
    icon: "error",
    title: "Error",
    text: mensaje,
  });
}

/*#########################################################
/* CARGAR PREGUNTAS DE EVALUACIÓN */
/*#########################################################*/

// Función para cargar las preguntas desde la API
async function cargarPreguntas() {
  try {
    const response = await fetch("/rrhh/preguntas/");
    const data = await response.json();

    if (data.data) {
      // Filtrar solo preguntas de tipo DESEMPEÑO (id_tipo_preguntas = 1)
      const preguntasDesempeno = data.data.filter(
        (pregunta) => pregunta.id_tipo_preguntas === 1
      );

      // Agrupar preguntas por categoría
      const preguntasPorCategoria = {
        PRODUCTIVIDAD: {
          id: "collapseProductividad",
          nombre: "Productividad",
          icono: "fas fa-chart-line",
          preguntas: [],
        },
        "CONDUCTA LABORAL": {
          id: "collapseConducta",
          nombre: "Conducta Laboral",
          icono: "fas fa-user-tie",
          preguntas: [],
        },
        "PARTICIPACION EN ACTIVIDADES": {
          id: "collapseParticipacion",
          nombre: "Participación en Actividades",
          icono: "fas fa-users",
          preguntas: [],
        },
      };

      // Organizar preguntas por categoría (solo una vez)
      preguntasDesempeno.forEach((pregunta) => {
        if (preguntasPorCategoria[pregunta.categoria]) {
          preguntasPorCategoria[pregunta.categoria].preguntas.push(pregunta);
        }
      });

      // Mostrar preguntas en cada sección del acordeón
      Object.entries(preguntasPorCategoria).forEach(([categoria, datos]) => {
        const contenedor = document.querySelector(`#${datos.id} .card-body`);
        if (contenedor) {
          contenedor.innerHTML = ""; // Limpiar contenedor

          if (datos.preguntas.length === 0) {
            contenedor.innerHTML =
              '<p class="text-muted">No hay preguntas disponibles para esta categoría</p>';
            return;
          }

          datos.preguntas.forEach((pregunta) => {
            contenedor.appendChild(crearElementoPregunta(pregunta));
          });
        }
      });
    }
  } catch (error) {
    console.error("Error al cargar preguntas:", error);
    mostrarError("Error al cargar las preguntas de evaluación");
  }
}

//  PROCESAR SELECCION DE VALORACIONES

function crearElementoPregunta(pregunta) {
  const preguntaDiv = document.createElement("div");
  preguntaDiv.className = "criterio-evaluacion mb-4";

  preguntaDiv.innerHTML = `
        <label>${pregunta.descripcion}</label>
        <div class="btn-group btn-group-toggle w-100" data-toggle="buttons">
            <label class="btn btn-outline-danger">
                <input type="radio" name="pregunta_${pregunta.id}" value="baja"> Baja
            </label>
            <label class="btn btn-outline-warning">
                <input type="radio" name="pregunta_${pregunta.id}" value="aceptable"> Aceptable
            </label>
            <label class="btn btn-outline-success">
                <input type="radio" name="pregunta_${pregunta.id}" value="alta"> Alta
            </label>
            <label class="btn btn-outline-secondary">
                <input type="radio" name="pregunta_${pregunta.id}" value="na"> N/A
            </label>
        </div>
    `;

  // Actualizar el event listener para manejar las nuevas valoraciones

  const radios = preguntaDiv.querySelectorAll('input[type="radio"]');
  radios.forEach((radio) => {
    radio.addEventListener("change", function () {
      console.log(
        "Valoración seleccionada:",
        this.value,
        "para pregunta:",
        pregunta.id
      );
      calcularTotalDesempeno();
    });
  });

  return preguntaDiv;
}

//#################################################################################
// SECCION DE HABILIDADES
//#################################################################################

// Función para cargar las preguntas de habilidades
async function cargarPreguntasHabilidades() {
  try {
    const response = await fetch("/rrhh/preguntas/");
    const data = await response.json();

    if (data.data) {
      // Filtrar solo las preguntas de tipo HABILIDADES (id_tipo_preguntas = 2)
      const preguntasHabilidades = data.data.filter(
        (pregunta) => pregunta.id_tipo_preguntas === 2
      );

      const contenedor = document.querySelector(
        "#acordeonHabilidades .card-body"
      );
      if (contenedor) {
        contenedor.innerHTML = ""; // Limpiar contenedor

        if (preguntasHabilidades.length === 0) {
          contenedor.innerHTML =
            '<p class="text-muted">No hay preguntas de habilidades disponibles</p>';
          return;
        }

        // Crear elementos para cada pregunta
        preguntasHabilidades.forEach((pregunta) => {
          contenedor.appendChild(crearElementoPreguntaHabilidad(pregunta));
        });
      }
    }
  } catch (error) {
    console.error("Error al cargar preguntas de habilidades:", error);
    mostrarError("Error al cargar las preguntas de habilidades");
  }
}

// Función para crear el elemento de una pregunta de habilidad
function crearElementoPreguntaHabilidad(pregunta) {
  const preguntaDiv = document.createElement("div");
  preguntaDiv.className = "criterio-evaluacion mb-4";

  preguntaDiv.innerHTML = `
      <div class="pregunta-container">
          <label class="font-weight-bold">${pregunta.descripcion}</label>
          <div class="btn-group btn-group-toggle w-100" data-toggle="buttons">
              <label class="btn btn-outline-danger radio_habilidad">
                  <input type="radio" name="habilidad_${pregunta.id}" value="baja"> Baja
              </label>
              <label class="btn btn-outline-warning radio_habilidad">

                  <input type="radio"  name="habilidad_${pregunta.id}" value="aceptable"> Aceptable

              </label>
              <label class="btn btn-outline-success radio_habilidad">
                  <input type="radio"  name="habilidad_${pregunta.id}" value="alta"> Alta
              </label>
              <label class="btn btn-outline-secondary radio_habilidad">
                  <input type="radio"  name="habilidad_${pregunta.id}" value="na"> N/A
              </label>
          </div>
      </div>
  `;

  // Actualizar event listener para cálculo de promedios
  const radios = preguntaDiv.querySelectorAll('input[type="radio"]');
  radios.forEach((radio) => {
    radio.addEventListener("change", () => {
      calcularPromedioHabilidades();
    });
  });

  return preguntaDiv;
}

// Función para procesar las habilidades
function procesarHabilidades() {
  return Array.from(
    document.querySelectorAll("#acordeonHabilidades .criterio-evaluacion")
  ).map((elemento) => {
    const idPregunta = parseInt(
      elemento.querySelector('input[type="radio"]').name.split("_")[1]
    );
    const valoracion =
      elemento.querySelector('input[type="radio"]:checked')?.value || "na";

    return {
      id_pregunta: idPregunta,
      valoracion_baja: valoracion === "baja" ? 1 : 0,
      valoracion_aceptable: valoracion === "aceptable" ? 1 : 0,
      valoracion_alta: valoracion === "alta" ? 1 : 0,
      valoracion_na: valoracion === "na" ? 1 : 0,
    };
  });
}

//#################################################################################
// SECCION DE OBJETIVOS
//#################################################################################

// Objetivos
const objetivos = [];
document.querySelectorAll("#objetivos tbody tr").forEach((fila, index) => {
  const id = index + 1;
  const radioSeleccionado = fila.querySelector(
    `input[name="valoracion_${id}"]:checked`
  );

  const objetivo = {
    obj_descripcion: fila.querySelector(`input[name="obj_descripcion_${id}"]`)
      .value,
    valoracion_cumplio: 0,
    valoracion_regular: 0,
    valoracion_negativo: 0,
  };

  if (radioSeleccionado) {
    switch (radioSeleccionado.value) {
      case "cumplio":
        objetivo.valoracion_cumplio = 1;
        break;
      case "regular":
        objetivo.valoracion_regular = 1;
        break;
      case "negativo":
        objetivo.valoracion_negativo = 1;
        break;
    }
  }

  objetivos.push(objetivo);
});

function validarObjetivos(objetivos) {
  let valido = true;

  objetivos.forEach((objetivo, index) => {
    // Validar descripción
    if (!objetivo.obj_descripcion.trim()) {
      mostrarError(`El objetivo ${index + 1} no tiene descripción`);
      valido = false;
    }

    // Validar solo una opción seleccionada
    const total =
      objetivo.valoracion_cumplio +
      objetivo.valoracion_regular +
      objetivo.valoracion_negativo;
    if (total !== 1) {
      mostrarError(
        `Debe seleccionar una valoración para el objetivo ${index + 1}`
      );
      valido = false;
    }
  });

  return valido;
}

//########################################################
// funcion para recopilar los datos de la evaluacion antes de guardar
//########################################################

function recopilarDatosFormulario() {
  try {
    const datosCompletos = {
      evaluacion: {
        fecha_evaluacion: $("#fechaEvaluacion").val(),
        periodo: $("#periodo").val(),
        id_evaluador: parseInt($("#evaluador").val()),
        id_evaluado: parseInt($("#evaluado").val()),
        id_area: areaUsuario,
        fortalezas: $("#fortalezas").val() || "",
        areas_mejora: $("#areas_mejora").val() || "",
      },
      objetivos: procesarObjetivos(),
      habilidades: procesarHabilidades(),
      desempeno: procesarDesempeno(),
    };

    // Debug: Mostrar datos en consola
    console.log("Datos recopilados:", JSON.stringify(datosCompletos, null, 2));
    return datosCompletos;
  } catch (error) {
    console.error("Error al recopilar datos:", error);
    mostrarError("Error al recopilar los datos del formulario");
    return null;
  }
}

function procesarObjetivos() {
  const objetivos = [];
  $("#objetivos tbody tr").each(function (index) {
    const descripcion = $(this)
      .find(`input[name="obj_descripcion_${index + 1}"]`)
      .val();
    const valorSeleccionada = $(this)
      .find(`input[name="valoracion_${index + 1}"]:checked`)
      .val();

    objetivos.push({
      obj_descripcion: descripcion || "",
      valoracion_cumplio: valorSeleccionada === "cumplio" ? 1 : 0,
      valoracion_regular: valorSeleccionada === "regular" ? 1 : 0,
      valoracion_negativo: valorSeleccionada === "negativo" ? 1 : 0,
    });
  });
  return objetivos;
}

function procesarHabilidades() {
  const habilidades = [];
  $("#acordeonHabilidades .criterio-evaluacion").each(function () {
    const radioName = $(this).find('input[type="radio"]').first().attr("name");
    const idPregunta = radioName ? parseInt(radioName.split("_")[1]) : 0;
    const valorSeleccionada = $(this).find('input[type="radio"]:checked').val();

    habilidades.push({
      id_pregunta: idPregunta,
      valoracion_baja: valorSeleccionada === "baja" ? 1 : 0,
      valoracion_aceptable: valorSeleccionada === "aceptable" ? 1 : 0,
      valoracion_alta: valorSeleccionada === "alta" ? 1 : 0,
      valoracion_na: valorSeleccionada === "na" ? 1 : 0,
    });
  });
  return habilidades;
}

function procesarDesempeno() {
  const desempeno = [];
  $(".tab-pane#desempeno .criterio-evaluacion").each(function () {
    const radioName = $(this).find('input[type="radio"]').first().attr("name");
    const idPregunta = radioName ? parseInt(radioName.split("_")[1]) : 0;
    const valorSeleccionada = $(this).find('input[type="radio"]:checked').val();

    desempeno.push({
      id_pregunta: idPregunta,
      valoracion_baja: valorSeleccionada === "baja" ? 1 : 0,
      valoracion_aceptable: valorSeleccionada === "aceptable" ? 1 : 0,
      valoracion_alta: valorSeleccionada === "alta" ? 1 : 0,
      valoracion_na: valorSeleccionada === "na" ? 1 : 0,
    });
  });
  return desempeno;
}

// Función para obtener el token CSRF de las cookies
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

async function guardarEvaluacion() {
  try {
    const evaluacionId = $("#evaluacionForm").data("evaluacion-id");
    const esEdicion = !!evaluacionId;

    // Obtener el ID del usuario actual del input hidden
    const idUsuarioActual = $("#usuario_id").val();

    // Recopilar datos del formulario
    const datosEvaluacion = {
      evaluacion: {
        fecha_evaluacion:
          $("#fechaEvaluacion").val() || new Date().toISOString().split("T")[0],
        periodo: $("#periodo").val(),
        id_evaluador: parseInt(idUsuarioActual), // Usar el ID del usuario actual
        id_evaluado: parseInt($("#evaluado").val()),
        id_area: parseInt(areaUsuario), // Usar la variable global que ya tienes definida
        fortalezas: $("#fortalezas").val() || "",
        areas_mejora: $("#areas_mejora").val() || "",
        estado: "1",
      },
      objetivos: [],
      habilidades: [],
      desempeno: [],
    };

    // Validar que tengamos todos los datos necesarios
    if (!datosEvaluacion.evaluacion.id_evaluador) {
      throw new Error("No se pudo obtener el ID del evaluador");
    }
    if (!datosEvaluacion.evaluacion.id_evaluado) {
      throw new Error("No se ha seleccionado un evaluado");
    }
    if (!datosEvaluacion.evaluacion.id_area) {
      throw new Error("No se pudo obtener el ID del área");
    }

    // Recopilar objetivos
    $("#objetivos tbody tr").each(function (index) {
      const objetivo = {
        obj_descripcion:
          $(this)
            .find(`input[name="obj_descripcion_${index + 1}"]`)
            .val() || "",
        valoracion_cumplio: $(this)
          .find(`input[name="valoracion_${index + 1}"][value="cumplio"]`)
          .prop("checked")
          ? 1
          : 0,
        valoracion_regular: $(this)
          .find(`input[name="valoracion_${index + 1}"][value="regular"]`)
          .prop("checked")
          ? 1
          : 0,
        valoracion_negativo: $(this)
          .find(`input[name="valoracion_${index + 1}"][value="negativo"]`)
          .prop("checked")
          ? 1
          : 0,
      };

      if (esEdicion) {
        objetivo.id = index + 1;
      }

      datosEvaluacion.objetivos.push(objetivo);
    });

    // Recopilar habilidades
    $('[name^="habilidad_"]').each(function () {
      const habilidadId = this.name.split("_")[1];
      if (
        !datosEvaluacion.habilidades.find(
          (h) => h.id_pregunta === parseInt(habilidadId)
        )
      ) {
        const habilidad = {
          id_pregunta: parseInt(habilidadId),
          valoracion_baja: $(
            `input[name="habilidad_${habilidadId}"][value="baja"]`
          ).prop("checked")
            ? 1
            : 0,
          valoracion_aceptable: $(
            `input[name="habilidad_${habilidadId}"][value="aceptable"]`
          ).prop("checked")
            ? 1
            : 0,
          valoracion_alta: $(
            `input[name="habilidad_${habilidadId}"][value="alta"]`
          ).prop("checked")
            ? 1
            : 0,
          valoracion_na: $(
            `input[name="habilidad_${habilidadId}"][value="na"]`
          ).prop("checked")
            ? 1
            : 0,
        };

        if (esEdicion) {
          habilidad.id = parseInt(habilidadId);
        }

        datosEvaluacion.habilidades.push(habilidad);
      }
    });

    // Recopilar desempeño
    $('[name^="pregunta_"]').each(function () {
      const preguntaId = this.name.split("_")[1];
      if (
        !datosEvaluacion.desempeno.find(
          (d) => d.id_pregunta === parseInt(preguntaId)
        )
      ) {
        const desempeno = {
          id_pregunta: parseInt(preguntaId),
          valoracion_baja: $(
            `input[name="pregunta_${preguntaId}"][value="baja"]`
          ).prop("checked")
            ? 1
            : 0,
          valoracion_aceptable: $(
            `input[name="pregunta_${preguntaId}"][value="aceptable"]`
          ).prop("checked")
            ? 1
            : 0,
          valoracion_alta: $(
            `input[name="pregunta_${preguntaId}"][value="alta"]`
          ).prop("checked")
            ? 1
            : 0,
          valoracion_na: $(
            `input[name="pregunta_${preguntaId}"][value="na"]`
          ).prop("checked")
            ? 1
            : 0,
        };

        if (esEdicion) {
          desempeno.id = parseInt(preguntaId);
        }

        datosEvaluacion.desempeno.push(desempeno);
      }
    });

    // Log para depuración
    console.log("Datos a enviar al backend:", {
      método: esEdicion ? "PUT" : "POST",
      url: esEdicion
        ? `/rrhh/evaluaciones/${evaluacionId}/`
        : "/rrhh/evaluaciones/",
      datos: datosEvaluacion,
    });

    const url = esEdicion
      ? `/rrhh/evaluaciones/${evaluacionId}/`
      : "/rrhh/evaluaciones/";
    const response = await fetch(url, {
      method: esEdicion ? "PUT" : "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"), // Asegúrate de tener esta función definida
      },
      body: JSON.stringify(datosEvaluacion),
    });

    const result = await response.json();
    console.log("Respuesta del backend:", result);

    if (result.status === "success") {
      Swal.fire({
        title: "Éxito",
        text: `Evaluación ${
          esEdicion ? "actualizada" : "guardada"
        } correctamente`,
        icon: "success",
      }).then(() => {
        $("#modalEvaluacion").modal("hide");
        resetearFormulario();
        inicializarTablaEvaluaciones();
      });
    } else {
      throw new Error(
        result.message ||
          `Error al ${esEdicion ? "actualizar" : "guardar"} la evaluación`
      );
    }
  } catch (error) {
    console.error("Error:", error);
    Swal.fire({
      title: "Error",
      text:
        error.message ||
        `Error al ${evaluacionId ? "actualizar" : "guardar"} la evaluación`,
      icon: "error",
    });
  }
}

function mostrarExito(mensaje) {
  console.log(mensaje);
  alert(mensaje); // Temporal, reemplazar con un sistema de notificaciones mejor
}

//########################################################
// TABLA DE EVALUACIONES
//########################################################

function inicializarTablaEvaluaciones() {
  var table = $("#tablaEvaluaciones").DataTable({
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
        // Botón de Excel
        extend: "excelHtml5",
        title: "Reporte_Evaluaciones_Desempeño",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        exportOptions: {
          columns: ":visible",
        },
      },
      {
        // Botón de PDF
        extend: "pdfHtml5",
        title: "Reporte_Evaluaciones_Desempeño",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A4",
        customize: function (doc) {
          doc.defaultStyle.fontSize = 8;
          doc.styles.tableHeader.fontSize = 9;
          doc.styles.title.fontSize = 12;
          doc.pageMargins = [20, 20, 20, 20];
        },
        exportOptions: {
          columns: ":visible",
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

    searching: false,

    // Idioma
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json",
    },

    // Ajax para obtener datos
    ajax: {
      url: "/rrhh/evaluaciones-general/",
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
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return `<span class="small-text">${meta.row + 1}</span>`;
        },
      },
      {
        data: "evaluador_nombre",

        render: function (data, type, row) {
          if (type === "display") {
            // Obtenemos el primer nombre y el primer apellido
            const primerNombre = row.evaluador_nombre.split(" ")[0];
            const primerApellido = row.evaluador_apellido.split(" ")[0];

            // Creamos las iniciales con el primer nombre y primer apellido
            const iniciales = (
              primerNombre.charAt(0) + primerApellido.charAt(0)
            ).toUpperCase();
            // Creamos el nombre corto
            const nombreCorto = `${primerNombre} ${primerApellido}`;

            const stringToGradient = (str) => {
              let hash = 0;
              for (let i = 0; i < str.length; i++) {
                hash = str.charCodeAt(i) + ((hash << 5) - hash);
              }
              const h1 = Math.abs(hash) % 360;
              const h2 = (h1 + 40) % 360;
              return `linear-gradient(135deg, hsl(${h1}, 70%, 60%) 0%, hsl(${h2}, 70%, 45%) 100%)`;
            };

            const backgroundGradient = stringToGradient(nombreCorto);

            return `
                  <div class="d-flex align-items-center">
                      <div class="modern-avatar small-avatar" 
                           style="background: ${backgroundGradient};">
                          <span class="initials small-text">${iniciales}</span>
                          <div class="avatar-status"></div>
                      </div>
                      <div class="user-info">
                          <div class="user-name small-text">${nombreCorto}</div>
                          <div class="user-role smaller-text">Evaluador</div>
                      </div>
                  </div>`;
          }
          return data;
        },
      },
      {
        data: "evaluado_nombre",

        render: function (data, type, row) {
          if (type === "display") {
            // Obtenemos el primer nombre y el primer apellido
            const primerNombre = row.evaluado_nombre.split(" ")[0];
            const primerApellido = row.evaluado_apellido.split(" ")[0];

            // Creamos las iniciales con el primer nombre y primer apellido
            const iniciales = (
              primerNombre.charAt(0) + primerApellido.charAt(0)
            ).toUpperCase();
            // Creamos el nombre corto
            const nombreCorto = `${primerNombre} ${primerApellido}`;

            const stringToGradient = (str) => {
              let hash = 0;
              for (let i = 0; i < str.length; i++) {
                hash = str.charCodeAt(i) + ((hash << 5) - hash);
              }
              const h1 = Math.abs(hash) % 360;
              const h2 = (h1 + 40) % 360;
              return `linear-gradient(135deg, hsl(${h1}, 70%, 60%) 0%, hsl(${h2}, 70%, 45%) 100%)`;
            };

            const backgroundGradient = stringToGradient(nombreCorto);

            return `
                  <div class="d-flex align-items-center">
                      <div class="modern-avatar small-avatar" 
                           style="background: ${backgroundGradient};">
                          <span class="initials small-text">${iniciales}</span>
                          <div class="avatar-status-evaluado"></div>
                      </div>
                      <div class="user-info">
                          <div class="user-name small-text">${nombreCorto}</div>
                          <div class="user-role smaller-text">Evaluado</div>
                      </div>
                  </div>`;
          }
          return data;
        },
      },
      {
        data: "fecha_evaluacion",
        render: function (data, type, row) {
          if (type === "display") {
            const fecha = new Date(data);
            const mes = fecha.toLocaleString("es", { month: "short" });
            const dia = fecha.getDate();
            return `<span class="small-text">${dia} ${mes}</span>`;
          }
          return data;
        },
      },

      {
        data: "periodo",
        render: function (data, type, row) {
          if (type === "display") {
            return `<span class="small-text">${data}</span>`;
          }
          return data;
        },
      },
      {
        data: "total_desempeno",
        render: function (data, type, row) {
          if (type === "display") {
            return `<span class="small-text">${data}</span>`;
          }
          return data;
        },
      },
      {
        data: "total_habilidades",
        render: function (data, type, row) {
          if (type === "display") {
            return `<span class="small-text">${data}</span>`;
          }
          return data;
        },
      },
      {
        data: "porcentaje_objetivos",
        render: function (data, type, row) {
          if (type === "display") {
            return `<span class="small-text">${data}</span>`;
          }
          return data;
        },
      },
      {
        data: "promedio",
        render: function (data, type, row) {
          if (type === "sort" || type === "type") {
            return parseFloat(data);
          }
          const promedio = parseFloat(data).toFixed(1);
          let badgeClass = "";

          if (promedio >= 4.5 && promedio <= 5.0) {
            badgeClass = "success";
          } else if (promedio >= 3.1 && promedio < 4.4) {
            badgeClass = "primary";
          } else if (promedio >= 2.6 && promedio < 3.0) {
            badgeClass = "warning";
          } else {
            badgeClass = "danger";
          }

          return `
            <span class="badge badge-${badgeClass} badge-pill small-badge">
              ${promedio}
            </span>`;
        },
      },
      {
        data: null,
        className: "text-center",
        orderable: false,
        render: function (data, type, row) {
          return `
            <div class="btn-group btn-group-sm" role="group">
              <button type="button" class="btn btn-xs btn-warning btn-editar" 
                      data-id="${row.id}" title="Editar">
                <i class="fas fa-edit fa-sm"></i>
              </button>
              <button type="button" class="btn btn-xs btn-danger btn-eliminar" 
                      data-id="${row.id}" title="Eliminar">
                <i class="fas fa-trash fa-sm"></i>
              </button>
            </div>`;
        },
      },
    ],

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
}

// Manejador del evento click para el botón editar

// Variable global para almacenar las preguntas
async function cargarPreguntasEdicion(datosEvaluacion) {
  try {
    const response = await fetch("/rrhh/preguntas/");
    const data = await response.json();

    if (data.data) {
      // Filtrar preguntas por tipo
      const preguntasDesempeno = data.data.filter(
        (pregunta) => pregunta.id_tipo_preguntas === 1
      );
      const preguntasHabilidades = data.data.filter(
        (pregunta) => pregunta.id_tipo_preguntas === 2
      );

      // Marcar valoraciones de desempeño
      if (datosEvaluacion.desempeno) {
        datosEvaluacion.desempeno.forEach((item) => {
          const pregunta = preguntasDesempeno.find(
            (p) => p.id === item.id_pregunta
          );
          if (pregunta) {
            const radioName = `pregunta_${item.id_pregunta}`;
            Object.entries(item.valoraciones).forEach(([valor, estado]) => {
              if (estado === 1) {
                const radioButton = $(
                  `input[name="${radioName}"][value="${valor}"]`
                );
                radioButton.prop("checked", true);
                radioButton.closest(".btn").addClass("active");
              }
            });
          }
        });
      }

      // Marcar valoraciones de habilidades
      if (datosEvaluacion.habilidades) {
        datosEvaluacion.habilidades.forEach((item) => {
          const pregunta = preguntasHabilidades.find(
            (p) => p.id === item.id_pregunta
          );
          if (pregunta) {
            const radioName = `habilidad_${item.id_pregunta}`;
            Object.entries(item.valoraciones).forEach(([valor, estado]) => {
              if (estado === 1) {
                const radioButton = $(
                  `input[name="${radioName}"][value="${valor}"]`
                );
                radioButton.prop("checked", true);
                radioButton.closest(".btn").addClass("active");
              }
            });
          }
        });
      }
    }
  } catch (error) {
    console.error("Error al cargar preguntas para edición:", error);
    mostrarError("Error al cargar las preguntas para edición");
  }
}

async function llenarFormularioEvaluacion(data) {
  console.log("Datos a llenar:", data);

  // Limpiar formulario primero
  $("#evaluacionForm")[0].reset();

  // Datos básicos de la evaluación
  $("#fortalezas").val(data.fortalezas || "");
  $("#areas_mejora").val(data.areas_mejora || "");
  $("#fechaEvaluacion").val(data.fecha_evaluacion || "");
  $("#periodo").val(data.periodo || "");

  // Cargar evaluadores
  $.ajax({
    url: "/rrhh/usuario-area/",
    type: "GET",
    dataSrc: "data",
    success: function (response) {
      console.log("Response usuarios:", response);

      if (response.status === "success" && response.data) {
        // Buscar el usuario que coincida con el id_evaluador
        const usuarioEncontrado = response.data.find(
          (usuario) => usuario.id === data.id_evaluador
        );

        if (usuarioEncontrado) {
          // Crear el nombre completo
          const nombreCompleto = `${usuarioEncontrado.first_name} ${usuarioEncontrado.last_name}`;

          // Verificar si la opción ya existe en el select
          if (
            $(`#evaluador option[value='${usuarioEncontrado.id}']`).length === 0
          ) {
            // Si no existe, agregar la nueva opción
            $("#evaluador").append(
              new Option(nombreCompleto, usuarioEncontrado.id)
            );
          }

          // Seleccionar el evaluador en el select
          $("#evaluador").val(usuarioEncontrado.id);

          console.log("Usuario encontrado:", {
            id: usuarioEncontrado.id,
            nombre: nombreCompleto,
            area: usuarioEncontrado.id_area,
          });
        } else {
          console.warn(
            "No se encontró el evaluador con ID:",
            data.id_evaluador
          );
        }
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al cargar usuarios:", error);
    },
  });

  $("#evaluador").val(data.id_evaluador || "");

  $("#evaluado").val(data.id_evaluado || "");
  $("#area").val(data.id_area || "");

  // Cargar y marcar las preguntas para edición
  await cargarPreguntasEdicion(data);

  // Llenar objetivos
  if (data.objetivos && Array.isArray(data.objetivos)) {
    data.objetivos.forEach((objetivo, index) => {
      if (index < 3) {
        $(`input[name="obj_descripcion_${index + 1}"]`).val(
          objetivo.descripcion || ""
        );
        Object.entries(objetivo.valoraciones).forEach(([valor, estado]) => {
          if (estado === 1) {
            const radioButton = $(
              `input[name="valoracion_${index + 1}"][value="${valor}"]`
            );
            radioButton.prop("checked", true);
            radioButton.closest(".btn").addClass("active");
          }
        });
      }
    });
  }

  // Guardar el ID de la evaluación para el PUT
  $("#evaluacionForm").data("evaluacion-id", data.id);

  // Recalcular promedios

  calcularPromedioObjetivos();
}

// Función para cargar los datos de la evaluación

async function cargarEvaluacion(id) {
  try {
    const response = await fetch(`/rrhh/evaluaciones/${id}/`);
    console.log("Response status:", response.status); // Debug: ver status de la respuesta

    const data = await response.json();
    console.log("Datos recibidos de la API:", data); // Debug: ver datos completos

    if (data.status === "success") {
      console.log("Datos a llenar en el formulario:", data.data); // Debug: ver datos que pasaremos al formulario
      llenarFormularioEvaluacion(data.data);
    } else {
      throw new Error(data.message || "Error al cargar la evaluación");
    }
  } catch (error) {
    console.error("Error detallado:", error); // Debug: ver error detallado
    Swal.fire({
      title: "Error",
      text: "No se pudo cargar la evaluación",
      icon: "error",
    });
  }
}

function resetearFormulario() {
  // Resetear campos de texto y áreas de texto
  $("#evaluacionForm")[0].reset();
  $("#fortalezas").val("");
  $("#areas_mejora").val("");

  // Resetear los objetivos
  for (let i = 1; i <= 3; i++) {
    $(`input[name="obj_descripcion_${i}"]`).val("");
    $(`input[name="valoracion_${i}"]`).prop("checked", false);
    $(`input[name="valoracion_${i}"]`).closest(".btn").removeClass("active");
  }

  // Resetear valoraciones de desempeño
  $('[name^="pregunta_"]').each(function () {
    $(this).prop("checked", false);
    $(this).closest(".btn").removeClass("active");
  });

  // Resetear valoraciones de habilidades
  $('[name^="habilidad_"]').each(function () {
    $(this).prop("checked", false);
    $(this).closest(".btn").removeClass("active");
  });

  // Limpiar el ID de evaluación almacenado
  $("#evaluacionForm").removeData("evaluacion-id");

  // Resetear los promedios si existen
  $("#promedioDesempeno").text("0.00");
  $("#promedioHabilidades").text("0.00");
  $("#promedioObjetivos").text("0.00");
  $("#promedioTotal").text("0.00");
}

//########################################################
// funcionalidad de eliminar evaluaciones
//########################################################

// Función para eliminar una evaluación
async function eliminarEvaluacion(id) {
  try {
    // Mostrar confirmación antes de eliminar
    const confirmacion = await Swal.fire({
      title: "¿Está seguro?",
      text: "Esta acción no se puede deshacer",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    });

    if (!confirmacion.isConfirmed) {
      return;
    }

    const response = await fetch(`/rrhh/evaluaciones/${id}/`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    const result = await response.json();

    if (result.status === "success") {
      Swal.fire({
        title: "Eliminado",
        text: "La evaluación ha sido eliminada correctamente",
        icon: "success",
      });

      // Actualizar la tabla de evaluaciones
      inicializarTablaEvaluaciones();
    } else {
      throw new Error(result.message || "Error al eliminar la evaluación");
    }
  } catch (error) {
    console.error("Error:", error);
    Swal.fire({
      title: "Error",
      text: error.message || "No se pudo eliminar la evaluación",
      icon: "error",
    });
  }
}

//########################################################
// CALCULO DE TOTALES
//########################################################
//HABILIDADES

function calcularSumaHabilidades() {
  // Obtener todos los radio buttons seleccionados
  const radiosSeleccionados = $(
    '#acordeonHabilidades input[type="radio"]:checked'
  );
  let sumaTotal = 0;
  let cantidadSeleccionada = 0;

  // Recorrer cada radio button seleccionado y sumar su valor
  radiosSeleccionados.each(function () {
    const valorSeleccionado = $(this).val();

    // Sumar el valor correspondiente
    switch (valorSeleccionado) {
      case "baja":
        sumaTotal += 1;
        cantidadSeleccionada++;
        break;
      case "aceptable":
        sumaTotal += 3;
        cantidadSeleccionada++;
        break;
      case "alta":
        sumaTotal += 5;
        cantidadSeleccionada++;
        break;
      case "na":
        // No sumamos nada para N/A
        break;
    }
  });

  // Debug para verificar la suma
  console.log("Cálculo de Habilidades:", {
    totalSelecciones: radiosSeleccionados.length,
    seleccionesValidas: cantidadSeleccionada,
    sumaTotal: sumaTotal,
    detalleSelecciones: Array.from(radiosSeleccionados).map((radio) => ({
      pregunta: $(radio).attr("name"),
      valor: $(radio).val(),
      puntaje:
        radio.value === "baja"
          ? 1
          : radio.value === "aceptable"
          ? 3
          : radio.value === "alta"
          ? 5
          : 0,
    })),
  });

  // Actualizar el valor en la tarjeta
  $("#promedioHabilidades").text(sumaTotal.toFixed(1));
}

//DESEMPEÑO
function calcularTotalDesempeno() {
  // Obtener todos los radio buttons seleccionados en las tres secciones de desempeño
  const radiosSeleccionados = $(
    "#collapseProductividad, #collapseConducta, #collapseParticipacion"
  ).find('input[type="radio"]:checked');

  let sumaTotal = 0;
  let totalSelecciones = 0;

  // Recorrer cada radio button seleccionado y sumar su valor
  radiosSeleccionados.each(function () {
    const valorSeleccionado = $(this).val();

    // Sumar el valor correspondiente
    switch (valorSeleccionado) {
      case "baja":
        sumaTotal += 1;
        totalSelecciones++;
        break;
      case "aceptable":
        sumaTotal += 3;
        totalSelecciones++;
        break;
      case "alta":
        sumaTotal += 5;
        totalSelecciones++;
        break;
      case "na":
        // No sumamos nada para N/A
        break;
    }
  });

  // Debug para verificar los cálculos
  console.log("Cálculo de Desempeño:", {
    totalSelecciones: totalSelecciones,
    sumaTotal: sumaTotal,
    detalleSelecciones: Array.from(radiosSeleccionados).map((radio) => ({
      pregunta: $(radio).attr("name"),
      valor: $(radio).val(),
      puntaje:
        radio.value === "baja"
          ? 1
          : radio.value === "aceptable"
          ? 3
          : radio.value === "alta"
          ? 5
          : 0,
    })),
  });

  // Actualizar el valor en la tarjeta de desempeño
  $("#promedioDesempeno").text(sumaTotal.toFixed(1));
}

//########################################################
//OBJETIVOS
//########################################################

function calcularPorcentajesObjetivos() {
  let sumaTotal = 0;
  let objetivosCalificados = 0;

  // Recorrer cada objetivo (1 al 3)
  for (let i = 1; i <= 3; i++) {
    const radioSeleccionado = document.querySelector(
      `input[name="valoracion_${i}"]:checked`
    );
    const porcentajeSpan = document.getElementById(`porcentaje_${i}`);

    if (radioSeleccionado) {
      let porcentaje = 0;

      // Asignar porcentaje según la valoración
      switch (radioSeleccionado.value) {
        case "negativo":
          porcentaje = 85; // Menos del 90%
          break;
        case "regular":
          porcentaje = 95; // Entre 90% y 100%
          break;
        case "cumplio":
          porcentaje = 105; // Entre 101% y 110%
          break;
      }

      // Actualizar el porcentaje en la columna
      porcentajeSpan.textContent = `${porcentaje}%`;

      // Sumar al total
      sumaTotal += porcentaje;
      objetivosCalificados++;
    }
  }

  // Calcular y mostrar el promedio total
  const promedioTotal =
    objetivosCalificados > 0
      ? (sumaTotal / objetivosCalificados).toFixed(1)
      : 0;

  // Actualizar el porcentaje total
  document.getElementById("porcentajeTotal").textContent = `${promedioTotal}%`;

  // Debug para verificar cálculos
  console.log("Cálculo de Objetivos:", {
    sumaTotal,
    objetivosCalificados,
    promedioTotal,
  });
}

//########################################################
// Event Listeners
//########################################################

document.addEventListener("DOMContentLoaded", function () {
  cargarPreguntas();
  cargarPreguntasHabilidades();
  inicializarTablaEvaluaciones();

  // Prevenir el envío tradicional del formulario
  $("#evaluacionForm").on("submit", function (e) {
    e.preventDefault();
  });

  $("#tablaEvaluaciones").on("click", ".btn-eliminar", function (e) {
    e.preventDefault();
    const id = $(this).data("id");
    eliminarEvaluacion(id);
  });

  // Agregar evento para resetear el formulario cuando se cierra el modal
  $("#modalEvaluacion").on("hidden.bs.modal", function () {
    resetearFormulario();
  });

  // Agregar evento para resetear el formulario cuando se abre el modal para nueva evaluación
  $("#btnNuevaEvaluacion").on("click", function () {
    resetearFormulario();

    const idUsuarioActual = $("#usuario_id").val();
    cargarDatosEvaluador(idUsuarioActual);

    const fechaHoy = new Date().toISOString().split("T")[0];
    $("#fechaEvaluacion").val(fechaHoy);
    $("#fechaEvaluacion").attr("max", fechaHoy);
  });

  //############################################################
  // Habilidades
  //############################################################
  // Event delegation para capturar clicks en los radio buttons
  $("#acordeonHabilidades").on("change", 'input[type="radio"]', function () {
    console.log("Radio seleccionado:", $(this).val());
    calcularSumaHabilidades();
  });

  // Alternativa: capturar clicks en los labels de los botones
  $("#acordeonHabilidades").on("click", ".btn-group label", function () {
    console.log("Botón clickeado");
    setTimeout(calcularSumaHabilidades, 100); // Pequeño delay para asegurar que el radio se actualizó
  });

  //############################################################
  // Desempeño
  //############################################################
  $("#acordeonEvaluacion").on("change", 'input[type="radio"]', function () {
    console.log("Radio de desempeño seleccionado:", $(this).val());
    calcularTotalDesempeno();
  });

  //############################################################
  // Objetivos
  //############################################################
  $("#objetivos").on("change", 'input[type="radio"]', function () {
    const valorSeleccionado = $(this).val();
    const numeroObjetivo = $(this).attr("name").split("_")[1];

    console.log(
      `Objetivo ${numeroObjetivo} - Valoración seleccionada: ${valorSeleccionado}`
    );
    calcularPorcentajesObjetivos();
  });

  $("#tablaEvaluaciones").on("click", ".btn-editar", async function () {
    const id = $(this).data("id");

    $("#modalEvaluacion").modal("show");
    cargarEvaluacion(id);
  });

  $("#btnGuardarEvaluacion").on("click", guardarEvaluacion);
});
