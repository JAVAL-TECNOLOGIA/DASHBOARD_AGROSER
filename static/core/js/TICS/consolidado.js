/**
 * Formateador de moneda en soles.
 */
const formatoSoles = new Intl.NumberFormat("es-PE", {
  style: "currency",
  currency: "PEN",
  minimumFractionDigits: 2,
});

/**
 * Función genérica para hacer peticiones con reintentos.
 * @param {string}  url           - URL a la cual se hará la petición.
 * @param {number}  maxIntentos   - Número máximo de reintentos.
 * @param {number}  delayReintento- Tiempo (ms) entre cada reintento.
 * @returns {Promise}             - Resuelve con el response de la petición exitosa o rechaza con el error.
 */
function fetchDataConReintento(url, maxIntentos = 5, delayReintento = 2000) {
  let intentosRealizados = 0;

  return new Promise((resolve, reject) => {
    const realizarPeticion = () => {
      $.ajax({
        url: url,
        type: "GET",
        dataType: "json",
        success: function (response) {
          resolve(response);
        },
        error: function (xhr, status, error) {
          intentosRealizados++;
          console.warn(`Error al llamar a ${url}:`, { xhr, status, error });
          if (intentosRealizados < maxIntentos) {
            setTimeout(realizarPeticion, delayReintento);
          } else {
            reject(
              new Error(
                `Se alcanzó el máximo de intentos (${maxIntentos}) para: ${url}`
              )
            );
          }
        },
      });
    };

    realizarPeticion();
  });
}

/**
 * Dada la respuesta de la API, busca el registro de "Total Anual" y
 * retorna el valor 'Consolidado_Mes' parseado a número.
 * @param {Object} response - Respuesta en formato JSON de la API.
 * @returns {number}        - Valor numérico de 'Consolidado_Mes' o 0.
 */
function extraerTotalAnual(response) {
  if (!response || !response.data || !Array.isArray(response.data)) return 0;
  const totalAnual = response.data.find((item) => item.Mes === "Total Anual");
  if (!totalAnual) return 0;
  return parseFloat(totalAnual.Consolidado_Mes || 0) || 0;
}

/**
 * Obtiene el consolidado de Sueldos y Salarios de manera asíncrona.
 * Aplica reintentos y actualiza el DOM si se obtiene un valor > 0.
 */
async function obtenerConsolidadoSueldosSalarios() {
  try {
    const year = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();
    // Primer fetch: sueldos
    const responseSueldos = await fetchDataConReintento(
      `/api_sueldo_mensual/?year=${year}`,
      5,
      2000
    );
    let totalSueldos = extraerTotalAnual(responseSueldos);

    // Si el total de sueldos es 0, opcionalmente podríamos forzar un reintento manual,
    // pero dado que ya tenemos reintentos en fetchDataConReintento,
    // únicamente avisamos si recibimos 0 tras intentar 5 veces.
    if (totalSueldos === 0) {
      console.warn("No se pudo obtener un valor válido para sueldos.");
    }
    // Segundo fetch: salarios
    const responseSalarios = await fetchDataConReintento(
      `/api_salario_mensual/?year=${year}`,
      5,
      2000
    );
    let totalSalarios = extraerTotalAnual(responseSalarios);

    // Sumar ambos
    const totalConsolidado = totalSueldos + totalSalarios;
    $("#stats_consolidado_sueldos").text(formatoSoles.format(totalConsolidado));

    // Si es mayor que cero, actualizamos el total general
    if (totalConsolidado > 0) {
      actualizarTotalGeneral();
    }
  } catch (error) {
    console.error("Error en la obtención de sueldos/salarios:", error);
    // Si falló completamente, mostrar 0 para no dejar datos viejos.
    $("#stats_consolidado_sueldos").text(formatoSoles.format(0));
  }
}

/**
 * Lee el valor numérico de un elemento que contiene formato en soles (ej. "S/. 1,234.56").
 * Si no se puede parsear, retorna 0.
 * @param {string} selector - Selector jQuery del elemento.
 * @returns {number}        - Valor numérico parseado.
 */
function obtenerValorNumerico(selector) {
  const elemento = $(selector);
  if (!elemento.length) {
    console.warn(`Elemento no encontrado: ${selector}`);
    return 0;
  }
  // Remover "S/." o "S/" y comas
  const texto = elemento.text().replace("S/.", "").replace("S/", "").trim();
  const valor = parseFloat(texto.replace(/,/g, "")) || 0;

  // Log de debugging
  console.log(`Valor extraído de ${selector}:`, {
    textoOriginal: elemento.text(),
    textoLimpio: texto,
    valorNumerico: valor,
  });

  return valor;
}

/**
 * Actualiza el total general sumando todos los componentes:
 * servicios, materiales, sueldos+salarios y capex.
 */
function actualizarTotalGeneral() {
  const servicios = obtenerValorNumerico("#stats_serviciosterceros_consolidado");
  const materiales = obtenerValorNumerico("#stats_materiales_consolidado");
  const sueldosSalarios = obtenerValorNumerico("#stats_consolidado_sueldos");
  const capex = obtenerValorNumerico("#stats_capex");

  // Si alguno es 0, asumimos que todavía no está listo. Puedes ajustar la condición según tu caso.
  // if (!servicios || !materiales || !sueldosSalarios || !capex) {
  //   console.warn("Algunos valores aún no están disponibles, esperando...");
  //   return;
  // }

  const totalGeneral = servicios + materiales + sueldosSalarios + capex;
  $("#stats_total_consolidado").text(formatoSoles.format(totalGeneral));
}

$(document).ready(function () {
  // Llamamos a la función principal para cargar sueldos y salarios
  obtenerConsolidadoSueldosSalarios();
  // Llamamos al menos una vez para ver si hay valores iniciales
  actualizarTotalGeneral();
});

/**
 * Manejador del botón para recargar Sueldos y Salarios.
 */
$("#recargarConsolidadoSueldosSalarios").on("click", function (e) {
  e.stopPropagation();
  $(this).find("i").addClass("fa-spin");

  obtenerConsolidadoSueldosSalarios().finally(() => {
    // Quitamos la animación del ícono
    setTimeout(() => {
      $(this).find("i").removeClass("fa-spin");
    }, 1000);
  });
});

/**
 * Manejador del botón para recargar el Total Consolidado.
 */
$("#recargarTotalConsolidado").on("click", function (e) {
  e.preventDefault();
  $(this).find("i").addClass("fa-spin");

  actualizarTotalGeneral();

  setTimeout(() => {
    $(this).find("i").removeClass("fa-spin");
  }, 1000);
});

/**
 * Cada vez que cambien los valores de estos elementos,
 * volvemos a intentar actualizar el total general.
 */
$(
  "#stats_serviciosterceros_consolidado, #stats_materiales_consolidado, #stats_consolidado_sueldos, #stats_capex"
).on("DOMSubtreeModified", function () {
  actualizarTotalGeneral();
});



$("#recargarTodo").on("click", function () {

  const icono = $(this).find("i");
  icono.addClass("fa-spin");

  if (typeof obtenerServicios === "function") {
    obtenerServicios();
  }

  if (typeof obtenerMateriales === "function") {
    obtenerMateriales();
  }

  if (typeof obtenerConsolidadoSueldosSalarios === "function") {
    obtenerConsolidadoSueldosSalarios();
  }

  if (typeof obtenerCapex === "function") {
    obtenerCapex();
  }

  setTimeout(function () {
    actualizarTotalGeneral();
    icono.removeClass("fa-spin");
  }, 2000);

});