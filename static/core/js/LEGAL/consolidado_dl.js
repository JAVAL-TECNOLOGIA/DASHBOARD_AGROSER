/*******************************************
 * consolidado.js
 ********************************************/

const formatoSoles = new Intl.NumberFormat("es-PE", {
  style: "currency",
  currency: "PEN",
  minimumFractionDigits: 2,
});

/**
 * Función para peticiones AJAX con reintentos
 */
function fetchDataConReintento(url, maxIntentos = 3, delay = 2000) {
  let intentos = 0;

  return new Promise((resolve, reject) => {
    const intentar = () => {
      $.ajax({
        url,
        type: "GET",
        dataType: "json",
        success(response) {
          // Si la API responde algo como { status: "error", message: "..."}
          if (response && response.status === "error") {
            console.error(`Servidor devolvió error: ${response.message}`);
            return reject(response.message);
          }
          resolve(response);
        },
        error(xhr, status, error) {
          intentos++;
          console.warn(`Error [${xhr.status}] (intento ${intentos}) ->`, error);

          // Solo reintentamos si es 500 o 503 y no pasamos de maxIntentos
          if (
            intentos < maxIntentos &&
            (xhr.status === 500 || xhr.status === 503)
          ) {
            setTimeout(() => intentar(), delay);
          } else {
            reject(new Error(`Error: ${xhr.status} - ${error}`));
          }
        },
      });
    };
    intentar();
  });
}

/**
 * Busca en el array el elemento con Mes === "Total Anual"
 * y devuelve el valor de "Consolidado_Mes" parseado a número.
 */
function extraerTotalAnual(response) {
  if (!response || !response.data || !Array.isArray(response.data)) {
    return 0;
  }
  const totalAnual = response.data.find((item) => item.Mes === "Total Anual");
  if (!totalAnual) {
    return 0;
  }
  return parseFloat(totalAnual.Consolidado_Mes || 0) || 0;
}

/**
 * Llama a la API de costo_sueldo_mensual
 */
// async function obtenerConsolidadoSueldos() {
//   try {
//     const responseSueldos = await fetchDataConReintento(
//       "/legal/legal_sueldo_mensual/", // Ajusta si la ruta difiere
//       3,
//       2000
//     );
//     const totalSueldos = extraerTotalAnual(responseSueldos);
//     $("#stats_sueldos").text(formatoSoles.format(totalSueldos));
//     return totalSueldos;
//   } catch (error) {
//     console.error("Error al obtener sueldos:", error);
//     $("#stats_sueldos").text(formatoSoles.format(0));
//     return 0;
//   }
// }

/**
 * Llama a la API de costo_salario_mensual
 */
// async function obtenerConsolidadoSalarios() {
//   try {
//     const responseSalarios = await fetchDataConReintento(
//       "/legal/legal_salario_mensual/", // Ojo con la ruta
//       3,
//       2000
//     );
//     const totalSalarios = extraerTotalAnual(responseSalarios);
//     $("#stats_salarios").text(formatoSoles.format(totalSalarios));
//     return totalSalarios;
//   } catch (error) {
//     console.error("Error al obtener salarios:", error);
//     $("#stats_salarios").text(formatoSoles.format(0));
//     return 0;
//   }
// }

/**
 * Los suma y pone el resultado en #stats_consolidado_sueldos
 */
async function obtenerConsolidadoSueldosYSalarios() {
  try {
    const year = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();
    // Primer fetch: sueldos
    const responseSueldos = await fetchDataConReintento(
      `/legal/legal_sueldo_mensual/?year=${year}`,
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
      `/legal/legal_salario_mensual/?year=${year}`,
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
 * Obtiene un valor numérico de un elemento con formato "S/. 1,234.56".
 */
function obtenerValorNumerico(selector) {
  const elemento = $(selector);
  if (!elemento.length) {
    console.warn(`Elemento no encontrado: ${selector}`);
    return 0;
  }
  const texto = elemento
    .text()
    .replace("S/.", "")
    .replace("S/", "")
    .replace(/,/g, "")
    .trim();
  const valor = parseFloat(texto) || 0;
  return valor;
}

/**
 * Suma varios campos del DOM y los muestra en #stats_total_consolidado
 */
function actualizarTotalGeneral() {
  const servicios = obtenerValorNumerico("#stats_serviciosterceros");
  const materiales = obtenerValorNumerico("#stats_materiales_consolidado");
  const sueldosSalarios = obtenerValorNumerico("#stats_consolidado_sueldos");
  const capex = obtenerValorNumerico("#stats_capex");

  const totalGeneral = servicios + materiales + sueldosSalarios + capex;
  $("#stats_total_consolidado").text(formatoSoles.format(totalGeneral));
}

/**
 * Inicialización al cargar la página.
 */
$(document).ready(function () {
  // Cargar sueldos y salarios
  obtenerConsolidadoSueldosYSalarios().then(() => {
    // Luego calcular total general
    actualizarTotalGeneral();
  });

  // Botón recarga sueldos/salarios
  $("#recargarConsolidadoSueldosSalarios").on("click", function (e) {
    e.preventDefault();
    $(this).find("i").addClass("fa-spin");

    obtenerConsolidadoSueldosYSalarios()
      .then(() => actualizarTotalGeneral())
      .finally(() => {
        setTimeout(() => $(this).find("i").removeClass("fa-spin"), 1000);
      });
  });

  // Botón recarga total
  $("#recargarTotalConsolidado").on("click", function (e) {
    e.preventDefault();
    $(this).find("i").addClass("fa-spin");
    actualizarTotalGeneral();
    setTimeout(() => $(this).find("i").removeClass("fa-spin"), 1000);
  });

  // Cada vez que cambien #stats_serviciosterceros, etc., recalculamos
  $(
    "#stats_serviciosterceros, #stats_materiales_consolidado, #stats_consolidado_sueldos, #stats_capex"
  ).on("DOMSubtreeModified", function () {
    setTimeout(actualizarTotalGeneral, 100);
  });
});


$("#recargarTodoLE").on("click", function () {

  const icono = $(this).find("i");
  icono.addClass("fa-spin");

  if (typeof obtenerServicios === "function") {
    obtenerServicios();
  }

  if (typeof obtenerMateriales === "function") {
    obtenerMateriales();
  }

  if (typeof obtenerConsolidadoSueldosYSalarios === "function") {
    obtenerConsolidadoSueldosYSalarios();
  }

  if (typeof obtenerCapex === "function") {
    obtenerCapex();
  }

  setTimeout(function () {
    actualizarTotalGeneral();
    icono.removeClass("fa-spin");
  }, 2000);

});