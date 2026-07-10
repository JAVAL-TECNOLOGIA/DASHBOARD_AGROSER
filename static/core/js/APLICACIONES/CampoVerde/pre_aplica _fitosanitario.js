$(document).ready(function () {
  // Boton para eliminar producto

  // Inicializar tablas de programas
  initTablaProgramasPlantines_SG();
  initTablaProgramasPostCosecha_SG();
  initTablaProgramasCosecha_SG();
  initTablaProgramasPlantines_AC();
  initTablaProgramasPostCosecha_AC();
  initTablaProgramasCosecha_AC();
  initTablaProgramasPlantines_MC();
  initTablaProgramasPostCosecha_MC();
  initTablaProgramasCosecha_MC();
  initTablaProgramasPlantines_SUGRA56();
  initTablaProgramasPostCosecha_SUGRA56();
  initTablaProgramasCosecha_SUGRA56();

  // Inicializar controladores de eventos
  initEventListeners();

  // Inicializar eventos para el formulario de productos
  initEventosFormularioProducto();

  $(document).on("click", ".btn-editar-producto", function () {
    const idProducto = $(this).data("id");
    editarProducto(idProducto);
  });
});

// ============================================================================
// INICIALIZACIÓN DE EVENTOS
// ============================================================================
function initEventListeners() {
  // Botones para abrir modal de creación de programas
  $("#btnCrearProgramaSGPlantines").click(() =>
    abrirModalCrearPrograma(1, 1, "Plantines")
  );
  $("#btnCrearProgramaSGPostCosecha").click(() =>
    abrirModalCrearPrograma(2, 1, "Post Cosecha")
  );
  $("#btnCrearProgramaSGCosecha").click(() =>
    abrirModalCrearPrograma(3, 1, "Producción")
  );
  $("#btnCrearProgramaACPlantines").click(() =>
    abrirModalCrearPrograma(1, 2, "Plantines")
  );
  $("#btnCrearProgramaACPostCosecha").click(() =>
    abrirModalCrearPrograma(2, 2, "Post Cosecha")
  );
  $("#btnCrearProgramaACCosecha").click(() =>
    abrirModalCrearPrograma(3, 2, "Producción")
  );
  $("#btnCrearProgramaMCPlantines").click(() =>
    abrirModalCrearPrograma(1, 3, "Plantines")
  );
  $("#btnCrearProgramaMCPostCosecha").click(() =>
    abrirModalCrearPrograma(2, 3, "PobtnGuardarProductost Cosecha")
  );
  $("#btnCrearProgramaMCCosecha").click(() =>
    abrirModalCrearPrograma(3, 3, "Producción")
  );
  $("#btnCrearProgramaSG56Plantines").click(() =>
    abrirModalCrearPrograma(1, 4, "Plantines")
  );
  $("#btnCrearProgramaSG56PostCosecha").click(() =>
    abrirModalCrearPrograma(2, 4, "Post Cosecha")
  );
  $("#btnCrearProgramaSG56Cosecha").click(() =>
    abrirModalCrearPrograma(3, 4, "Producción")
  );

  // Botón para guardar programa
  $("#btnGuardarPrograma").click(guardarProgramaFitosanitario);

  // Boton para guardar programa de producción
  $("#btnGuardarProgramaProduccion").click(
    guardarProgramaFitosanitarioProduccion
  );

  // Evento para guardar producto
  $("#btnGuardarProducto").on("click", guardarProducto);
}

/**
 * Formatea un valor numérico como moneda en dólares con separadores de miles
 * @param {number|string} valor - El valor a formatear
 * @returns {string} - El valor formateado como moneda (ej: "$1,234.56")
 */
function formatearMoneda(valor) {
  // Convertir a número si es string
  const numero = parseFloat(valor) || 0;

  // Formatear con separadores de miles y dos decimales
  return (
    "$" +
    numero.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 3,
    })
  );
}

// ============================================================================
// INICIALIZACIÓN DE DATATABLES
// ============================================================================

/**
 * Inicializa la tabla de programas para Plantines - Sweet Globe
 */

// ============================================================================
// FUNCIONES DE ACTUALIZACIÓN DE ESTADÍSTICAS
// ============================================================================

/**
 * Actualiza las estadísticas para Plantines - Sweet Globe
 */
function actualizarEstadisticasPlantines_SG(datos) {
  // Calcular número de registros
  const numRegistros = datos.length;

  $("#resumen_programas_plantines_SG").text(numRegistros);

  // Variables para almacenar totales
  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;
  let contadorProgramasConDetalles = 0;

  // Función para procesar todos los programas secuencialmente
  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          // Obtener detalles del programa
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            contadorProgramasConDetalles++;

            // Calcular totales para este programa
            let precioPorLtKgPrograma = 0;
            let precioPorHaPrograma = 0;

            response.data.forEach((producto) => {
              // Sumar precio por lt-kg
              if (producto.PRECIO) {
                precioPorLtKgPrograma += parseFloat(producto.PRECIO);
              }

              // Sumar precio por hectárea
              if (producto.PRECIO_HA) {
                precioPorHaPrograma += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });

            // Acumular los totales
            precioTotalPorLtKg += precioPorLtKgPrograma;
            precioTotalPorHa += precioPorHaPrograma;
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    // Actualizar la interfaz con los totales calculados
    $("#resumen_precio_plantines_SG").text(
      /* `$ ${precioTotalPorLtKg.toFixed(3)}` */
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_plantines_SG").text(formatearMoneda(precioTotalPorHa));
  };

  // Iniciar el procesamiento de programas
  if (numRegistros > 0) {
    mostrarCargando(); // Muestra indicador de carga si existe
    procesarProgramas().finally(() => {
      ocultarCargando(); // Oculta indicador de carga al finalizar
    });
  } else {
    // Si no hay registros, mostrar valores en cero
    $("#resumen_precio_plantines_SG").text("$ 0.00");
    $("#resumen_costo_plantines_SG").text("$ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Post Cosecha - Sweet Globe
 */
function actualizarEstadisticasPostCosecha_SG(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_postcosecha_SG").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_postcosecha_SG").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_postcosecha_SG").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_postcosecha_SG").text("$ 0.00");
    $("#resumen_costo_postcosecha_SG").text("$ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Producción - Sweet Globe
 */
function actualizarEstadisticasProduccion_SG(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_produccion_SG").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_produccion_SG").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_produccion_SG").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_produccion_SG").text("$ 0.00");
    $("#resumen_costo_produccion_SG").text("$ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Plantines - Autumn Crisp
 */
function actualizarEstadisticasPlantines_AC(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_plantines_AC").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_plantines_AC").text(formatearMoneda(precioTotalPorLtKg));
    $("#resumen_costo_plantines_AC").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_plantines_AC").text("$ 0.00");
    $("#resumen_costo_plantines_AC").text("$ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Post Cosecha - Autumn Crisp
 */
function actualizarEstadisticasPostCosecha_AC(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_postcosecha_AC").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_postcosecha_AC").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_postcosecha_AC").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_postcosecha_AC").text("0.00");
    $("#resumen_costo_postcosecha_AC").text("S/ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Producción - Autumn Crisp
 */
function actualizarEstadisticasProduccion_AC(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_produccion_AC").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_produccion_AC").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_produccion_AC").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_produccion_AC").text("0.00");
    $("#resumen_costo_produccion_AC").text("S/ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Plantines - Moscatel
 */
function actualizarEstadisticasPlantines_MC(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_plantines_MC").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_plantines_MC").text(formatearMoneda(precioTotalPorLtKg));
    $("#resumen_costo_plantines_MC").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_plantines_MC").text("0.00");
    $("#resumen_costo_plantines_MC").text("S/ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Post Cosecha - Moscatel
 */
function actualizarEstadisticasPostCosecha_MC(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_postcosecha_MC").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_postcosecha_MC").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_postcosecha_MC").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_postcosecha_MC").text("0.00");
    $("#resumen_costo_postcosecha_MC").text("S/ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Producción - Moscatel
 */
function actualizarEstadisticasProduccion_MC(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_produccion_MC").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_produccion_MC").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_produccion_MC").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_produccion_MC").text("0.00");
    $("#resumen_costo_produccion_MC").text("S/ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Plantines - Sugra 56
 */
function actualizarEstadisticasPlantines_SG56(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_plantines_SG56").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_plantines_SG56").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_plantines_SG56").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_plantines_SG56").text("0.00");
    $("#resumen_costo_plantines_SG56").text("S/ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Post Cosecha - Sugra 56
 */
function actualizarEstadisticasPostCosecha_SG56(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_postcosecha_SG56").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_postcosecha_SG56").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_postcosecha_SG56").text(
      formatearMoneda(precioTotalPorHa)
    );
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_postcosecha_SG56").text("0.00");
    $("#resumen_costo_postcosecha_SG56").text("S/ 0.00");
  }
}

/**
 * Actualiza las estadísticas para Producción - Sugra 56
 */
function actualizarEstadisticasProduccion_SG56(datos) {
  const numRegistros = datos.length;
  $("#resumen_programas_produccion_SG56").text(numRegistros);

  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;

  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        try {
          const response = await $.ajax({
            url: `/aplicaciones/programas_cv/${programa.ID}/detalles/`,
            type: "GET",
            dataType: "json",
          });

          if (
            response.status === "success" &&
            response.data &&
            response.data.length > 0
          ) {
            response.data.forEach((producto) => {
              if (producto.PRECIO) {
                precioTotalPorLtKg += parseFloat(producto.PRECIO);
              }
              if (producto.PRECIO_HA) {
                precioTotalPorHa += parseFloat(
                  producto.PRECIO_HA * producto.PRECIO
                );
              }
            });
          }
        } catch (error) {
          console.error(
            `Error al obtener detalles del programa ${programa.ID}:`,
            error
          );
        }
      }
    }

    $("#resumen_precio_produccion_SG56").text(
      formatearMoneda(precioTotalPorLtKg)
    );
    $("#resumen_costo_produccion_SG56").text(formatearMoneda(precioTotalPorHa));
  };

  if (numRegistros > 0) {
    mostrarCargando();
    procesarProgramas().finally(() => {
      ocultarCargando();
    });
  } else {
    $("#resumen_precio_produccion_SG56").text("0.00");
    $("#resumen_costo_produccion_SG56").text("S/ 0.00");
  }
}

// ============================================================================
// INICIALIZACIÓN DE DATATABLES
// ============================================================================

function initTablaProgramasPlantines_SG() {
  const tabla = $("#tablaPrograma_plantines_SG").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    pageLength: 5, // Número máximo de filas por página

    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 1;
        d.idvariedad = 1;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPlantines_SG(datos);

        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Plantines SG:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_plantines_SG tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_plantines_SG tbody").on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el ID de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarPrograma").attr("data-id", idPrograma);
    $("#btnEliminarPrograma").attr("data-id", idPrograma);
    $("#btnDetallesPrograma").attr("data-id", idPrograma);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualPrograma");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");
  });

  // Ocultar el menú al hacer clic en cualquier parte
  $(document).on("click", function () {
    $("#menuContextualPrograma").hide();
  });

  // Configurar eventos para los botones del menú contextual
  $("#btnEditarPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");
    editarPrograma(idPrograma);
  });

  $("#btnEliminarPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");
    confirmarEliminarPrograma(idPrograma);
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

/**
 * Inicializa la tabla de programas para Post Cosecha - Sweet Globe
 */

function initTablaProgramasPostCosecha_SG() {
  const tabla = $("#tablaPrograma_post_cosecha_SG").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 2;
        d.idvariedad = 1;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPostCosecha_SG(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Post Cosecha SG:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_post_cosecha_SG tbody").on(
    "contextmenu",
    "tr",
    function (e) {
      e.preventDefault(); // Prevenir el menú contextual del navegador

      // Obtener el ID de la fila seleccionada
      const filaSeleccionada = tabla.row(this).data();
      if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

      const idPrograma = filaSeleccionada.ID;

      // Guardar el ID en los botones del menú para usarlo después
      $("#btnEditarPrograma").attr("data-id", idPrograma);
      $("#btnEliminarPrograma").attr("data-id", idPrograma);
      $("#btnDetallesPrograma").attr("data-id", idPrograma);

      // Mostrar el menú contextual en la posición del clic
      const menuContextual = $("#menuContextualPrograma");
      menuContextual.css({
        display: "block",
        left: e.pageX,
        top: e.pageY,
      });

      // Resaltar la fila seleccionada
      $(this).addClass("table-primary").siblings().removeClass("table-primary");
    }
  );

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_post_cosecha_SG tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

/**
 * Inicializa la tabla de programas para Producción - Sweet Globe
 */

function initTablaProgramasCosecha_SG() {
  const tabla = $("#tablaPrograma_cosecha_SG").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 3;
        d.idvariedad = 1;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasProduccion_SG(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Producción SG:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_cosecha_SG tbody").on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el ID de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarPrograma").attr("data-id", idPrograma);
    $("#btnEliminarPrograma").attr("data-id", idPrograma);
    $("#btnDetallesPrograma").attr("data-id", idPrograma);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualPrograma");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");
  });

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_cosecha_SG tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasPlantines_AC() {
  const tabla = $("#tablaPrograma_plantines_AC").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 1;
        d.idvariedad = 2;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPlantines_AC(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Plantines AC:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_plantines_AC tbody").on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el ID de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarPrograma").attr("data-id", idPrograma);
    $("#btnEliminarPrograma").attr("data-id", idPrograma);
    $("#btnDetallesPrograma").attr("data-id", idPrograma);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualPrograma");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");
  });

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_plantines_AC tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasPostCosecha_AC() {
  const tabla = $("#tablaPrograma_postcosecha_AC").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 2;
        d.idvariedad = 2;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPostCosecha_AC(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Post Cosecha AC:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_postcosecha_AC tbody").on(
    "contextmenu",
    "tr",
    function (e) {
      e.preventDefault(); // Prevenir el menú contextual del navegador

      // Obtener el ID de la fila seleccionada
      const filaSeleccionada = tabla.row(this).data();
      if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

      const idPrograma = filaSeleccionada.ID;

      // Guardar el ID en los botones del menú para usarlo después
      $("#btnEditarPrograma").attr("data-id", idPrograma);
      $("#btnEliminarPrograma").attr("data-id", idPrograma);
      $("#btnDetallesPrograma").attr("data-id", idPrograma);

      // Mostrar el menú contextual en la posición del clic
      const menuContextual = $("#menuContextualPrograma");
      menuContextual.css({
        display: "block",
        left: e.pageX,
        top: e.pageY,
      });

      // Resaltar la fila seleccionada
      $(this).addClass("table-primary").siblings().removeClass("table-primary");
    }
  );

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_postcosecha_AC tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasCosecha_AC() {
  const tabla = $("#tablaPrograma_cosecha_AC").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 3;
        d.idvariedad = 2;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasProduccion_AC(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Producción AC:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_cosecha_AC tbody").on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el ID de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarPrograma").attr("data-id", idPrograma);
    $("#btnEliminarPrograma").attr("data-id", idPrograma);
    $("#btnDetallesPrograma").attr("data-id", idPrograma);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualPrograma");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");
  });

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_cosecha_AC tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasPlantines_MC() {
  const tabla = $("#tablaPrograma_plantines_MC").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 1;
        d.idvariedad = 3;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPlantines_MC(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Plantines MC:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_plantines_MC tbody").on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el ID de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarPrograma").attr("data-id", idPrograma);
    $("#btnEliminarPrograma").attr("data-id", idPrograma);
    $("#btnDetallesPrograma").attr("data-id", idPrograma);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualPrograma");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");
  });

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_plantines_MC tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasPostCosecha_MC() {
  const tabla = $("#tablaPrograma_postcosecha_MC").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 2;
        d.idvariedad = 3;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPostCosecha_MC(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Post Cosecha MC:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_postcosecha_MC tbody").on(
    "contextmenu",
    "tr",
    function (e) {
      e.preventDefault(); // Prevenir el menú contextual del navegador

      // Obtener el ID de la fila seleccionada
      const filaSeleccionada = tabla.row(this).data();
      if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

      const idPrograma = filaSeleccionada.ID;

      // Guardar el ID en los botones del menú para usarlo después
      $("#btnEditarPrograma").attr("data-id", idPrograma);
      $("#btnEliminarPrograma").attr("data-id", idPrograma);
      $("#btnDetallesPrograma").attr("data-id", idPrograma);

      // Mostrar el menú contextual en la posición del clic
      const menuContextual = $("#menuContextualPrograma");
      menuContextual.css({
        display: "block",
        left: e.pageX,
        top: e.pageY,
      });

      // Resaltar la fila seleccionada
      $(this).addClass("table-primary").siblings().removeClass("table-primary");
    }
  );

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_postcosecha_MC tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasCosecha_MC() {
  const tabla = $("#tablaPrograma_cosecha_MC").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 3;
        d.idvariedad = 3;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasProduccion_MC(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Producción MC:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_cosecha_MC tbody").on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el ID de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarPrograma").attr("data-id", idPrograma);
    $("#btnEliminarPrograma").attr("data-id", idPrograma);
    $("#btnDetallesPrograma").attr("data-id", idPrograma);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualPrograma");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");
  });

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_cosecha_MC tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasPlantines_SUGRA56() {
  const tabla = $("#tablaPrograma_plantines_SG56").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 1;
        d.idvariedad = 4;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPlantines_SG56(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Plantines SUGRA 56:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_plantines_SG56 tbody").on(
    "contextmenu",
    "tr",
    function (e) {
      e.preventDefault(); // Prevenir el menú contextual del navegador

      // Obtener el ID de la fila seleccionada
      const filaSeleccionada = tabla.row(this).data();
      if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

      const idPrograma = filaSeleccionada.ID;

      // Guardar el ID en los botones del menú para usarlo después
      $("#btnEditarPrograma").attr("data-id", idPrograma);
      $("#btnEliminarPrograma").attr("data-id", idPrograma);
      $("#btnDetallesPrograma").attr("data-id", idPrograma);

      // Mostrar el menú contextual en la posición del clic
      const menuContextual = $("#menuContextualPrograma");
      menuContextual.css({
        display: "block",
        left: e.pageX,
        top: e.pageY,
      });

      // Resaltar la fila seleccionada
      $(this).addClass("table-primary").siblings().removeClass("table-primary");
    }
  );

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_plantines_SG56 tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasPostCosecha_SUGRA56() {
  const tabla = $("#tablaPrograma_postcosecha_SG56").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 2;
        d.idvariedad = 4;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasPostCosecha_SG56(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Post Cosecha SUGRA 56:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_postcosecha_SG56 tbody").on(
    "contextmenu",
    "tr",
    function (e) {
      e.preventDefault(); // Prevenir el menú contextual del navegador

      // Obtener el ID de la fila seleccionada
      const filaSeleccionada = tabla.row(this).data();
      if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

      const idPrograma = filaSeleccionada.ID;

      // Guardar el ID en los botones del menú para usarlo después
      $("#btnEditarPrograma").attr("data-id", idPrograma);
      $("#btnEliminarPrograma").attr("data-id", idPrograma);
      $("#btnDetallesPrograma").attr("data-id", idPrograma);

      // Mostrar el menú contextual en la posición del clic
      const menuContextual = $("#menuContextualPrograma");
      menuContextual.css({
        display: "block",
        left: e.pageX,
        top: e.pageY,
      });

      // Resaltar la fila seleccionada
      $(this).addClass("table-primary").siblings().removeClass("table-primary");
    }
  );

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_postcosecha_SG56 tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

function initTablaProgramasCosecha_SUGRA56() {
  const tabla = $("#tablaPrograma_cosecha_SG56").DataTable({
    destroy: true,
    responsive: true,
    autoWidth: false,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/aplicaciones/programas_cv/",
      type: "GET",
      data: function (d) {
        d.idfase = 3;
        d.idvariedad = 4;
        d.idcampania = $("#filtroAnioPresupuesto").val();
        return d;
      },
      dataSrc: function (json) {
        const datos = json.data || [];
        // Actualizar estadísticas cuando se cargan los datos
        actualizarEstadisticasProduccion_SG56(datos);
        return datos;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de Producción SUGRA 56:",
          error,
          thrown
        );
      },
    },
    columns: [
      /* {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      }, */
      { data: "NOMBRE_PROGRAMA" },
      { data: "FECHA_INICIO" },
      { data: "FECHA_FIN" },
    ],
    // Agregar clase a las filas para mejor estilo con hover
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      // Agregar el ID como atributo data para identificar la fila
      $(row).attr("data-id", data.ID);
    },
  });

  // Configurar evento de clic derecho en las filas
  $("#tablaPrograma_cosecha_SG56 tbody").on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el ID de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarPrograma").attr("data-id", idPrograma);
    $("#btnEliminarPrograma").attr("data-id", idPrograma);
    $("#btnDetallesPrograma").attr("data-id", idPrograma);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualPrograma");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");
  });

  // NUEVO: Configurar evento de doble clic en las filas// NUEVO: Configurar evento de doble clic en las filas
  $("#tablaPrograma_cosecha_SG56 tbody").on("dblclick", "tr", function () {
    const filaSeleccionada = tabla.row(this).data();

    if (!filaSeleccionada) return; // Si no hay datos, no hacer nada

    const idPrograma = filaSeleccionada.ID;
    // Llamar a la función para ver detalles
    verDetallesPrograma(idPrograma); // Sweet Globe (1), Plantines (1)
  });

  // botones para abrir modal de detalles
  $("#btnDetallesPrograma").on("click", function () {
    const idPrograma = $(this).attr("data-id");

    verDetallesPrograma(idPrograma);
  });
}

// ============================================================================
// FUNCIONES PARA MANEJO DE PROGRAMAS
// ============================================================================

/**
 * Abre el modal para crear un nuevo programa fitosanitario
 * @param {number} idFase - ID de la fase (1: Plantines, 2: Post Cosecha, 3: Producción)
 * @param {number} idVariedad - ID de la variedad (1: Sweet Globe, etc.)
 * @param {string} nombreFase - Nombre de la fase para mostrar en el título
 */
function abrirModalCrearPrograma(idFase, idVariedad, nombreFase) {
  // Resetear formularios
  resetearFormularioPrograma();
  resetearFormularioProgramaProduccion();

  // Si es la fase de Producción (3), usar el modal específico
  if (idFase === 3) {
    // Configurar campos ocultos para el modal de producción
    $("#modalIdFaseProduccion").val(idFase);
    $("#modalIdVariedadProduccion").val(idVariedad);

    // Personalizar título del modal según fase
    $("#modalCrearProgramaProduccionLabel").html(`
      <i class="fas fa-plus-circle mr-2"></i> Crear Programa Fitosanitario - ${nombreFase}
    `);

    // Abrir modal de producción
    $("#modalCrearProgramaProduccion").modal("show");
  } else {
    // Para el resto de fases (Plantines y Post Cosecha), usar el modal general

    // Configurar campos ocultos
    $("#modalIdFase").val(idFase);
    $("#modalIdVariedad").val(idVariedad);

    // Personalizar título del modal según fase
    $("#modalCrearProgramaLabel").html(`
      <i class="fas fa-plus-circle mr-2"></i> Crear Programa Fitosanitario - ${nombreFase}
    `);

    // Abrir modal general
    $("#modalCrearPrograma").modal("show");
  }
}

/**
 * Resetea los campos del formulario de creación de programa
 */
function resetearFormularioPrograma() {
  // Resetear valores del formulario
  $("#formCrearPrograma")[0].reset();

  // Resetear atributos de modo de edición
  $("#formCrearPrograma").removeAttr("data-modo");
  $("#formCrearPrograma").removeAttr("data-id");

  // Resetear estilo y texto del botón guardar
  $("#btnGuardarPrograma")
    .html('<i class="fas fa-save mr-1"></i> Guardar Programa')
    .removeClass("btn-success")
    .addClass("btn-primary");

  // Establecer valores predeterminados
  const hoy = new Date().toISOString().split("T")[0];
  $("#fechaInicio").val(hoy);
}

/**
 * Resetea los campos del formulario de creación de programa para producción
 */
function resetearFormularioProgramaProduccion() {
  // Resetear valores del formulario
  $("#formCrearProgramaProduccion")[0].reset();

  // Resetear atributos de modo de edición
  $("#formCrearProgramaProduccion").removeAttr("data-modo");
  $("#formCrearProgramaProduccion").removeAttr("data-id");

  // Resetear estilo y texto del botón guardar
  $("#btnGuardarProgramaProduccion")
    .html('<i class="fas fa-save mr-1"></i> Guardar Programa')
    .removeClass("btn-success")
    .addClass("btn-primary");

  // Obtener fecha actual para fecha de inicio
  const hoy = new Date();
  const fechaInicio = hoy.toISOString().split("T")[0];

  // Obtener fecha para mañana (fecha de fin)
  const mañana = new Date();
  mañana.setDate(hoy.getDate() + 1);
  const fechaFin = mañana.toISOString().split("T")[0];

  // Establecer valores predeterminados
  $("#fechaInicioProduccion").val(fechaInicio);
  $("#fechaFinProduccion").val(fechaFin);
}
/**
 * Guarda un nuevo programa fitosanitario mediante AJAX
 */

function guardarProgramaFitosanitario() {
  // Validar formulario
  if (!validarFormularioPrograma()) {
    return;
  }

  // Obtener datos del formulario
  const formData = obtenerDatosFormularioPrograma();
  
  // Determinar si estamos en modo edición o creación
  const modoEdicion = $("#formCrearPrograma").attr("data-modo") === "edicion";
  const idPrograma = modoEdicion
    ? $("#formCrearPrograma").attr("data-id")
    : null;

  // Cerrar el modal del formulario
  $("#modalCrearPrograma").modal("hide");

  // Mostrar el modal de carga directamente aquí
  // Swal.fire({
  //   title: "Guardando...",
  //   text: "Por favor espere",
  //   allowOutsideClick: false,
  //   allowEscapeKey: false,
  //   showConfirmButton: false,
  //   didOpen: () => {
  //     Swal.showLoading();
  //   },
  // });

  // Configurar y ejecutar la petición AJAX
  $.ajax({
    url: modoEdicion
      ? `/aplicaciones/programas_cv/${idPrograma}/`
      : "/aplicaciones/programas_cv/",
    type: modoEdicion ? "PUT" : "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      // Cerrar el modal de carga y eliminar cualquier residuo en el DOM
      Swal.close();

      // recargar tabla inmediatamente
      recargarTablaSegunFase(formData.idfase, formData.idvariedad);

      // mostrar mensaje sin bloquear flujo
      Swal.fire({
        icon: "success",
        title: "¡Éxito!",
        text: modoEdicion
          ? "Programa actualizado correctamente"
          : "Programa creado correctamente",
        timer: 1200,
        showConfirmButton: false
      });
      // Pequeño tiempo de espera para asegurar que el modal anterior se ha cerrado completamente
      // setTimeout(() => {
      //   // Mostrar mensaje de éxito
      //   Swal.fire({
      //     icon: "success",
      //     title: "¡Éxito!",
      //     text: modoEdicion
      //       ? "Programa actualizado correctamente"
      //       : "Programa creado correctamente",
      //     timer: 1500,
      //     showConfirmButton: false,
      //   }).then(() => {
      //     // Recargar tabla después de que se cierre el mensaje de éxito
      //     recargarTablaSegunFase(formData.idfase, formData.idvariedad);
      //   });
      // }, 300);
    },
    error: function (xhr, status, error) {
      console.error("Error en la petición:", { xhr, status, error });

      // Cerrar el modal de carga y eliminar cualquier residuo en el DOM
      Swal.close();


      // Pequeño tiempo de espera para asegurar que el modal anterior se ha cerrado completamente
      setTimeout(() => {
        // Mostrar mensaje de error
        let errorMessage = "Ocurrió un error. Intente nuevamente.";
        try {
          const response = JSON.parse(xhr.responseText);
          if (response && response.message) {
            errorMessage = response.message;
          }
        } catch (e) {
          console.error("Error al parsear respuesta:", e);
        }

        Swal.fire({
          icon: "error",
          title: "Error",
          text: errorMessage,
        });
      }, 300);
    },
  });
}

/**
 * Guarda un nuevo programa fitosanitario de producción mediante AJAX
 */
function guardarProgramaFitosanitarioProduccion() {
  // Validar formulario
  if (!validarFormularioProgramaProduccion()) {
    return;
  }

  // Obtener datos del formulario
  const formData = obtenerDatosFormularioProgramaProduccion();

  // Determinar si estamos en modo edición o creación
  const modoEdicion =
    $("#formCrearProgramaProduccion").attr("data-modo") === "edicion";
  const idPrograma = modoEdicion
    ? $("#formCrearProgramaProduccion").attr("data-id")
    : null;

  // Cerrar el modal del formulario
  $("#modalCrearProgramaProduccion").modal("hide");

  // Mostrar el modal de carga directamente aquí
  // Swal.fire({
  //   title: "Guardando...",
  //   text: "Por favor espere",
  //   allowOutsideClick: false,
  //   allowEscapeKey: false,
  //   showConfirmButton: false,
  //   didOpen: () => {
  //     Swal.showLoading();
  //   },
  // });

  // Configurar y ejecutar la petición AJAX
  $.ajax({
    url: modoEdicion
      ? `/aplicaciones/programas_cv/${idPrograma}/`
      : "/aplicaciones/programas_cv/",
    type: modoEdicion ? "PUT" : "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      // Cerrar el modal de carga y eliminar cualquier residuo en el DOM
      Swal.close();

      // recargar tabla inmediatamente
      recargarTablaSegunFase(formData.idfase, formData.idvariedad);

      // mostrar mensaje sin bloquear flujo
      Swal.fire({
        icon: "success",
        title: "¡Éxito!",
        text: modoEdicion
          ? "Programa actualizado correctamente"
          : "Programa creado correctamente",
        timer: 1200,
        showConfirmButton: false
      });

      
      // recargar tabla inmediatamente
      recargarTablaSegunFase(formData.idfase, formData.idvariedad);

      // mostrar mensaje sin bloquear flujo
      Swal.fire({
        icon: "success",
        title: "¡Éxito!",
        text: modoEdicion
          ? "Programa actualizado correctamente"
          : "Programa creado correctamente",
        timer: 1200,
        showConfirmButton: false
      });

      // Pequeño tiempo de espera para asegurar que el modal anterior se ha cerrado completamente
      // setTimeout(() => {
      //   // Mostrar mensaje de éxito
      //   Swal.fire({
      //     icon: "success",
      //     title: "¡Éxito!",
      //     text: modoEdicion
      //       ? "Programa de producción actualizado correctamente"
      //       : "Programa de producción creado correctamente",
      //     timer: 1500,
      //     showConfirmButton: false,
      //   }).then(() => {
      //     // Recargar tabla después de que se cierre el mensaje de éxito
      //     recargarTablaSegunFase(formData.idfase, formData.idvariedad);
      //   });
      // }, 300);
    },
    error: function (xhr, status, error) {
      console.error("Error en la petición:", { xhr, status, error });

      // Cerrar el modal de carga y eliminar cualquier residuo en el DOM
      Swal.close();

      // Pequeño tiempo de espera para asegurar que el modal anterior se ha cerrado completamente
      setTimeout(() => {
        // Mostrar mensaje de error
        let errorMessage = "Ocurrió un error. Intente nuevamente.";
        try {
          const response = JSON.parse(xhr.responseText);
          if (response && response.message) {
            errorMessage = response.message;
          }
        } catch (e) {
          console.error("Error al parsear respuesta:", e);
        }

        Swal.fire({
          icon: "error",
          title: "Error",
          text: errorMessage,
        });
      }, 300);
    },
  });
}

/**
 * Valida que el formulario de producción tenga todos los campos requeridos
 * @returns {boolean} true si el formulario es válido
 */

function validarFormularioProgramaProduccion() {
  const nombrePrograma = $("#nombreProgramaProduccion").val().trim();
  const tratamiento = $("#tratamientoProduccion").val().trim();
  const fechaInicio = $("#fechaInicioProduccion").val();
  const fechaFin = $("#fechaFinProduccion").val();

  // Validar campos requeridos (solo nombre y tratamiento)
  if (!nombrePrograma || !tratamiento) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Por favor, complete los campos obligatorios (Nombre del Programa y Tratamiento).",
    });
    return false;
  }

  // Validar fechas solo si ambas están presentes
  if (fechaInicio && fechaFin && fechaInicio > fechaFin) {
    Swal.fire({
      icon: "warning",
      title: "Fechas inválidas",
      text: "La fecha de inicio no puede ser posterior a la fecha de fin.",
    });
    return false;
  }

  return true;
}

/**
 * Obtiene los datos del formulario de producción formateados para enviar al servidor
 * @returns {Object} Objeto con los datos del formulario
 */
function obtenerDatosFormularioProgramaProduccion() {
  return {
    nombre_programa: $("#nombreProgramaProduccion").val().trim(),
    tratamiento: $("#tratamientoProduccion").val().trim(),
    fecha_inicio: formatearFecha($("#fechaInicioProduccion").val()),
    fecha_fin: formatearFecha($("#fechaFinProduccion").val()),
    descripcion: $("#descripcion_programa_produccion").val().trim(),
    idfase: $("#modalIdFaseProduccion").val(),
    idvariedad: $("#modalIdVariedadProduccion").val(),
    idcampania: $("#filtroAnioPresupuesto").val(),
  };
}

/**
 * Prepara el formulario de producción para edición
 * @param {number} idPrograma - ID del programa que se está editando
 */
function prepararFormularioEdicionProduccion(idPrograma) {
  // Marcar el formulario en modo edición
  $("#formCrearProgramaProduccion").attr("data-modo", "edicion");
  $("#formCrearProgramaProduccion").attr("data-id", idPrograma);

  // Cambiar texto y comportamiento del botón guardar
  $("#btnGuardarProgramaProduccion")
    .html('<i class="fas fa-save mr-1"></i> Actualizar Programa')
    .removeClass("btn-primary")
    .addClass("btn-success");
}

/**
 * Carga los datos del programa en el formulario de producción para edición
 * @param {Object} datos - Datos del programa
 */
function cargarDatosEnFormularioProduccion(datos) {
  // Resetear formulario antes de cargar nuevos datos
  resetearFormularioProgramaProduccion();

  // Preparar el formulario para edición
  prepararFormularioEdicionProduccion(datos.ID);

  // Llenar campos con datos del programa
  $("#modalIdFaseProduccion").val(datos.IDFASE);
  $("#modalIdVariedadProduccion").val(datos.IDVARIEDAD);
  $("#nombreProgramaProduccion").val(datos.NOMBRE_PROGRAMA);
  $("#tratamientoProduccion").val(datos.TRATAMIENTO || "");

  // Convertir fechas de DD/MM/YYYY a YYYY-MM-DD para input type="date"
  $("#fechaInicioProduccion").val(
    convertirFechaParaFormulario(datos.FECHA_INICIO)
  );
  $("#fechaFinProduccion").val(convertirFechaParaFormulario(datos.FECHA_FIN));
  $("#descripcion_programa_produccion").val(datos.DESCRIPCION || "");

  // Personalizar título del modal para edición
  const nombreFase = datos.FASE_DESCRIPCION || obtenerNombreFase(datos.IDFASE);
  $("#modalCrearProgramaProduccionLabel").html(`
    <i class="fas fa-edit mr-2"></i> Editar Programa Fitosanitario - ${nombreFase}
  `);

  // Mostrar modal
  $("#modalCrearProgramaProduccion").modal("show");
}

/**
 * Valida que el formulario tenga todos los campos requeridos
 * @returns {boolean} true si el formulario es válido
 */
function validarFormularioPrograma() {
  const nombrePrograma = $("#nombrePrograma").val().trim();

  // Validar campos requeridos
  if (!nombrePrograma) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Por favor, complete todos los campos obligatorios (*).",
    });
    return false;
  }

  // Validar fechas
  if (fechaInicio > fechaFin) {
    Swal.fire({
      icon: "warning",
      title: "Fechas inválidas",
      text: "La fecha de inicio no puede ser posterior a la fecha de fin.",
    });
    return false;
  }

  return true;
}

/**
 * Obtiene los datos del formulario formateados para enviar al servidor
 * @returns {Object} Objeto con los datos del formulario
 */
function obtenerDatosFormularioPrograma() {
  return {
    nombre_programa: $("#nombrePrograma").val().trim(),
    fecha_inicio: formatearFecha($("#fechaInicio").val()),
    fecha_fin: formatearFecha($("#fechaFin").val()),
    descripcion: $("#descripcion_programa").val().trim(),
    idfase: $("#modalIdFase").val(),
    idvariedad: $("#modalIdVariedad").val(),
    idcampania: $("#filtroAnioPresupuesto").val(),
  };
}

/**
 * Formatea una fecha de formato YYYY-MM-DD a DD/MM/YYYY
 * @param {string} fechaInput - Fecha en formato YYYY-MM-DD
 * @returns {string} Fecha en formato DD/MM/YYYY
 */
function formatearFecha(fechaInput) {
  if (!fechaInput) return "";

  const fecha = new Date(fechaInput);
  const dia = fecha.getDate().toString().padStart(2, "0");
  const mes = (fecha.getMonth() + 1).toString().padStart(2, "0");
  const anio = fecha.getFullYear();

  return `${dia}/${mes}/${anio}`;
}

/**
 * Muestra un indicador de carga mientras se procesa la solicitud
 */

function mostrarCargando() {
  // Cerrar cualquier modal de SweetAlert que pudiera estar abierto
  Swal.close();

  // Primero ocultamos el modal de creación de programa
  $("#modalCrearPrograma").modal("hide");

  // Pequeño timeout para asegurar que el modal se ha cerrado completamente
  setTimeout(() => {
    Swal.fire({
      title: "Guardando...",
      text: "Por favor espere",
      allowOutsideClick: false,
      allowEscapeKey: false,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading();
      },
      // Identificador único para este modal de carga
      customClass: {
        container: "swal-overlay-z-index modal-cargando-programa",
      },
    });
  }, 300);
}
/**
 * Oculta el indicador de carga
 */

function ocultarCargando() {
  // Cerrar específicamente el modal de carga con una pequeña espera
  // para asegurar que cualquier animación en curso se complete
  setTimeout(() => {
    // Cerrar el modal de SweetAlert
    Swal.close();

    // Eliminar manualmente cualquier residuo de modal que pueda quedar en el DOM
    $(".modal-cargando-programa").remove();
    $(".swal2-container").remove();
    $(".swal2-shown").removeClass("swal2-shown");

    // Restaurar el desplazamiento del cuerpo si estaba bloqueado
    $("body").removeClass("swal2-height-auto");
    $("body").css("overflow", "");
    $("body").css("padding-right", "");
  }, 100);
}

/**
 * Procesa la respuesta del servidor después de guardar un programa
 * @param {Object} response - Respuesta del servidor
 * @param {number} idFase - ID de la fase
 * @param {number} idVariedad - ID de la variedad
 */
function procesarRespuestaGuardado(response, idFase, idVariedad) {
  if (response.status === "success") {
    Swal.fire({
      icon: "success",
      title: "¡Programa guardado!",
      text: "El programa fitosanitario se ha registrado correctamente.",
      timer: 1500,
      showConfirmButton: false,
    }).then(() => {

      // cerrar modal
      $("#modalCrearPrograma").modal("hide");

      // 🔥 recargar tabla después del mensaje
      recargarTablaSegunFase(idFase, idVariedad);

    });
  } else {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: response.message || "Ocurrió un error al guardar el programa",
    });
  }
}

/**
 * Maneja errores durante el guardado de un programa
 * @param {Object} xhr - Objeto XMLHttpRequest
 * @param {string} status - Estado de la solicitud
 * @param {string} error - Mensaje de error
 */
function manejarErrorGuardado(xhr, status, error) {
  console.error("Error en AJAX:", status, error);

  Swal.fire({
    icon: "error",
    title: "Error de conexión",
    text: "No se pudo guardar el programa. Verifique su conexión o contacte al administrador.",
  });
}

/**
 * Recarga la tabla correspondiente según la fase y variedad
 * @param {number} idFase - ID de la fase
 * @param {number} idVariedad - ID de la variedad
 */
function recargarTablaSegunFase(idFase, idVariedad) {
  let selector = "";

  // Determinar qué tabla recargar basado en fase y variedad
  if (idFase == 1 && idVariedad == 1) {
    // Plantines - Sweet Globe
    selector = "#tablaPrograma_plantines_SG";
  } else if (idFase == 2 && idVariedad == 1) {
    // Post Cosecha - Sweet Globe
    selector = "#tablaPrograma_post_cosecha_SG";
  } else if (idFase == 3 && idVariedad == 1) {
    // Producción - Sweet Globe
    selector = "#tablaPrograma_cosecha_SG";
  } else if (idFase == 1 && idVariedad == 2) {
    // Plantines - Autumn Crisp
    selector = "#tablaPrograma_plantines_AC";
  } else if (idFase == 2 && idVariedad == 2) {
    // Post Cosecha - Autumn Crisp
    selector = "#tablaPrograma_postcosecha_AC";
  } else if (idFase == 3 && idVariedad == 2) {
    // Producción - Autumn Crisp
    selector = "#tablaPrograma_cosecha_AC";
  } else if (idFase == 1 && idVariedad == 3) {
    // Plantines - Moscatel
    selector = "#tablaPrograma_plantines_MC";
  } else if (idFase == 2 && idVariedad == 3) {
    // Post Cosecha - Moscatel
    selector = "#tablaPrograma_postcosecha_MC";
  } else if (idFase == 3 && idVariedad == 3) {
    // Producción - Moscatel
    selector = "#tablaPrograma_cosecha_MC";
  } else if (idFase == 1 && idVariedad == 4) {
    // Plantines - SUGRA 56
    selector = "#tablaPrograma_plantines_SG56";
  } else if (idFase == 2 && idVariedad == 4) {
    // Post Cosecha - SUGRA 56
    selector = "#tablaPrograma_postcosecha_SG56";
  } else if (idFase == 3 && idVariedad == 4) {
    // Producción - SUGRA 56
    selector = "#tablaPrograma_cosecha_SG56";
  }

  // Recargar tabla si existe
  if (selector && $.fn.DataTable.isDataTable(selector)) {
    $(selector).DataTable().ajax.reload();
  }
}

//#############################################################################
// ELIMINAR PROGRAMA
//#############################################################################
/**
 * Confirma y procesa la eliminación de un programa fitosanitario
 * @param {number} idPrograma - ID del programa a eliminar
 */
function confirmarEliminarPrograma(idPrograma) {
  if (!idPrograma) return;

  Swal.fire({
    title: "¿Está seguro?",
    text: "Esta acción no se puede revertir",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
    customClass: {
      popup: "swal-custom-popup",
      title: "swal-title",
      content: "swal-content",
      confirmButton: "btn btn-primary mr-3",
      cancelButton: "btn btn-danger ml-3",
      icon: "swal-icon",
      actions: "d-flex justify-content-around mt-3",
    },
    buttonsStyling: false,
    iconHtml:
      '<div class="custom-icon-warning"><i class="fas fa-exclamation"></i></div>',
    width: "450px",
    padding: "2.5rem",
    backdrop: `rgba(0,0,0,0.4)`,
  }).then((result) => {
    if (result.isConfirmed) {
      eliminarPrograma(idPrograma);
    }
  });
}

/**
 * Realiza la petición AJAX para eliminar un programa
 * @param {number} idPrograma - ID del programa a eliminar
 */

/* 
function eliminarPrograma(idPrograma) {
  console.log("Eliminando producto:", idPrograma);

  // DIAGNÓSTICO: Mostrar información sobre elementos SweetAlert2 en el DOM
  console.log("=== DIAGNÓSTICO DE ELEMENTOS SWEETALERT2 EN EL DOM ===");
  console.log("Elementos .swal2-container:", $(".swal2-container").length);
  if ($(".swal2-container").length > 0) {
    $(".swal2-container").each(function (index) {
      console.log(`SweetAlert2 Container #${index + 1}:`);
      console.log("  - Visible:", $(this).is(":visible"));
      console.log("  - z-index:", $(this).css("z-index"));
      console.log("  - Position:", $(this).css("position"));
      console.log("  - Classes:", $(this).attr("class"));
      console.log("  - HTML:", $(this).html().substring(0, 150) + "...");

      // Verificar si contiene un popup
      const popup = $(this).find(".swal2-popup");
      if (popup.length > 0) {
        console.log("  - Popup visible:", popup.is(":visible"));
        console.log("  - Popup z-index:", popup.css("z-index"));
      } else {
        console.log("  - No contiene popup");
      }
    });
  }

  // DIAGNÓSTICO: Verificar capas modales de Bootstrap
  console.log("Elementos .modal-backdrop:", $(".modal-backdrop").length);
  if ($(".modal-backdrop").length > 0) {
    $(".modal-backdrop").each(function (index) {
      console.log(`Modal Backdrop #${index + 1}:`);
      console.log("  - Visible:", $(this).is(":visible"));
      console.log("  - z-index:", $(this).css("z-index"));
    });
  }

  // DIAGNÓSTICO: Verificar estado del body
  console.log("Body classes:", $("body").attr("class"));

  // Limpieza completa del DOM de SweetAlert2 y modales
  $(".swal2-container").remove();
  $(".modal-backdrop").remove();
  $(".swal2-shown").removeClass("swal2-shown");
  $("body").removeClass("swal2-height-auto modal-open");
  $("#swal-custom-styles").remove();
  document.documentElement.style.overflow = "";
  document.documentElement.style.paddingRight = "";

  // Agregar estilos con z-index muy altos para asegurar visibilidad
  $("head").append(`
    <style id="swal-custom-styles">
      .swal-z-index-highest {
        z-index: 9999 !important;
      }
      .swal2-backdrop {
        z-index: 9998 !important;
      }
      .swal2-popup {
        z-index: 10000 !important;
      }
    </style>
  `);

  // Asegurar que el modal de productos esté cerrado
  $("#modalProducto").modal("hide");

  // Retraso para asegurar actualización del DOM
  setTimeout(() => {
    // DIAGNÓSTICO: Verificar estado del DOM antes de mostrar el nuevo SweetAlert
    console.log("=== DIAGNÓSTICO ANTES DE MOSTRAR SWEETALERT ===");
    console.log(
      "Elementos .swal2-container después de limpieza:",
      $(".swal2-container").length
    );
    console.log(
      "Elementos .modal-backdrop después de limpieza:",
      $(".modal-backdrop").length
    );
    console.log("Body classes después de limpieza:", $("body").attr("class"));

    Swal.fire({
      title: "¿Estás seguro?",
      text: "Esta acción eliminará el producto seleccionado.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
      customClass: {
        container: "swal-z-index-highest",
      },
      heightAuto: false,
    }).then((result) => {
      // DIAGNÓSTICO: Verificar estado después de mostrar el SweetAlert
      console.log("=== DIAGNÓSTICO DESPUÉS DE INTERACTUAR CON SWEETALERT ===");
      console.log("Result:", result);
      console.log("Elementos .swal2-container:", $(".swal2-container").length);

      if (result.isConfirmed) {
        // Limpiar cualquier residuo de SweetAlert2 antes de mostrar otro
        $(".swal2-container").remove();

        // Mostrar indicador de carga
        Swal.fire({
          title: "Eliminando...",
          text: "Por favor espere",
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();

            // DIAGNÓSTICO: Verificar estado en didOpen
            console.log("=== DIAGNÓSTICO EN DIDOPEN DEL LOADING ===");
            console.log(
              "Elementos .swal2-container en didOpen:",
              $(".swal2-container").length
            );
            console.log("Body classes en didOpen:", $("body").attr("class"));
          },
          customClass: {
            container: "swal-z-index-highest",
          },
          heightAuto: false,
        });

        $.ajax({
          url: `/aplicaciones/programas_cv/detalles/${idPrograma}/`,
          type: "DELETE",
          success: function (response) {
            // DIAGNÓSTICO: Verificar estado antes de limpiar
            console.log("=== DIAGNÓSTICO ANTES DE LIMPIAR DESPUÉS DE AJAX ===");
            console.log(
              "Elementos .swal2-container antes de limpiar:",
              $(".swal2-container").length
            );

            // Limpieza completa del DOM
            $(".swal2-container").remove();
            $(".modal-backdrop").remove();
            $(".swal2-shown").removeClass("swal2-shown");
            $("body").removeClass("swal2-height-auto modal-open");
            $("#swal-custom-styles").remove();
            document.documentElement.style.overflow = "";
            document.documentElement.style.paddingRight = "";

            // Cerrar Swal actual
            Swal.close();

            // DIAGNÓSTICO: Verificar estado después de limpiar
            console.log(
              "=== DIAGNÓSTICO DESPUÉS DE LIMPIAR DESPUÉS DE AJAX ==="
            );
            console.log(
              "Elementos .swal2-container después de limpiar:",
              $(".swal2-container").length
            );

            // Retraso para asegurar actualización del DOM
            setTimeout(() => {
              if (response.status === "success") {
                // Asegurar que los estilos personalizados estén presentes
                if (!$("#swal-custom-styles").length) {
                  $("head").append(`
                    <style id="swal-custom-styles">
                      .swal-z-index-highest {
                        z-index: 9999 !important;
                      }
                      .swal2-popup {
                        z-index: 10000 !important;
                      }
                    </style>
                  `);
                }

                Swal.fire({
                  icon: "success",
                  title: "¡Éxito!",
                  text: "Producto eliminado correctamente",
                  timer: 1500,
                  showConfirmButton: false,
                  customClass: {
                    container: "swal-z-index-highest",
                  },
                  heightAuto: false,
                  didOpen: () => {
                    // DIAGNÓSTICO: Verificar estado en didOpen del éxito
                    console.log("=== DIAGNÓSTICO EN DIDOPEN DEL ÉXITO ===");
                    console.log(
                      "Elementos .swal2-container en didOpen del éxito:",
                      $(".swal2-container").length
                    );
                  },
                });

                // Obtener el ID del programa actual
                const programaId = $(
                  "#modalDetalleProductos_sweet_globe_plantines"
                ).attr("data-programa-id");

                // Recargar la tabla de productos
                obtenerProductosPrograma(programaId);
              } else {
                // Si el backend devuelve un error aunque el status sea 200
                Swal.fire({
                  icon: "error",
                  title: "Error",
                  text:
                    response.message ||
                    "Ocurrió un error al eliminar el producto.",
                  customClass: {
                    container: "swal-z-index-highest",
                  },
                  heightAuto: false,
                  didOpen: () => {
                    // DIAGNÓSTICO: Verificar estado en didOpen del error
                    console.log("=== DIAGNÓSTICO EN DIDOPEN DEL ERROR ===");
                    console.log(
                      "Elementos .swal2-container en didOpen del error:",
                      $(".swal2-container").length
                    );
                  },
                });
              }
            }, 300);
          },
          error: function (xhr, status, error) {
            // DIAGNÓSTICO: Verificar estado en caso de error AJAX
            console.log("=== DIAGNÓSTICO EN CASO DE ERROR AJAX ===");
            console.log(
              "Elementos .swal2-container en error AJAX:",
              $(".swal2-container").length
            );

            // Limpieza completa del DOM
            $(".swal2-container").remove();
            $(".modal-backdrop").remove();
            $(".swal2-shown").removeClass("swal2-shown");
            $("body").removeClass("swal2-height-auto modal-open");
            $("#swal-custom-styles").remove();
            document.documentElement.style.overflow = "";
            document.documentElement.style.paddingRight = "";

            // Cerrar Swal actual
            Swal.close();

            // Retraso para asegurar actualización del DOM
            setTimeout(() => {
              let errorMessage =
                "Ocurrió un error al eliminar el producto. Intente nuevamente.";

              try {
                // Intentar parsear la respuesta JSON
                const response = JSON.parse(xhr.responseText);
                if (response && response.message) {
                  errorMessage = response.message;

                  // Mensaje específico para el error de formato de string
                  if (response.message.includes("string formatting")) {
                    errorMessage =
                      "Error de formato en la consulta SQL. Contacte al administrador del sistema.";

                    // Registrar información adicional para depuración
                    console.error(
                      "Error SQL de formateo. Posiblemente inconsistencia entre marcadores ? y %s en la consulta."
                    );
                  }
                }
              } catch (e) {
                console.error("Error al parsear respuesta:", e);
              }

              // Asegurar que los estilos personalizados estén presentes
              if (!$("#swal-custom-styles").length) {
                $("head").append(`
                  <style id="swal-custom-styles">
                    .swal-z-index-highest {
                      z-index: 9999 !important;
                    }
                    .swal2-popup {
                      z-index: 10000 !important;
                    }
                  </style>
                `);
              }

              Swal.fire({
                icon: "error",
                title: "Error",
                text: errorMessage,
                customClass: {
                  container: "swal-z-index-highest",
                },
                heightAuto: false,
                didOpen: () => {
                  // DIAGNÓSTICO: Verificar estado en didOpen del error de AJAX
                  console.log(
                    "=== DIAGNÓSTICO EN DIDOPEN DEL ERROR DE AJAX ==="
                  );
                  console.log(
                    "Elementos .swal2-container en didOpen del error de AJAX:",
                    $(".swal2-container").length
                  );
                },
              });

              console.error("Error al eliminar producto:", error);
            }, 300);
          },
        });
      }
    });
  }, 100);
}
 */

function eliminarPrograma(idPrograma) {
  // Mostrar indicador de carga
  Swal.fire({
    title: "Eliminando...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Realizar petición AJAX
  $.ajax({
    url: `/aplicaciones/programas_cv/${idPrograma}/`,
    type: "DELETE",
    success: function (response) {
      // Cerrar el modal de carga y eliminar cualquier residuo en el DOM
      Swal.close();
      $(".swal2-container").remove();
      $(".swal2-shown").removeClass("swal2-shown");
      $("body").removeClass("swal2-height-auto");

      // Pequeño tiempo de espera para asegurar que el modal anterior se ha cerrado completamente
      setTimeout(() => {
        if (response.status === "success") {
          // Mostrar mensaje de éxito
          Swal.fire({
            icon: "success",
            title: "¡Programa eliminado!",
            text: "El programa fitosanitario ha sido eliminado correctamente.",
            timer: 1500,
            showConfirmButton: false,
          });

          // Recargar todas las tablas de programas ya que no sabemos cuál es la activa
          recargarTablasProgramas();
        } else {
          // Mostrar mensaje de error
          Swal.fire({
            icon: "error",
            title: "Error",
            text:
              response.message || "Ocurrió un error al eliminar el programa",
          });
        }
      }, 300);
    },
    error: function (xhr, status, error) {
      // Cerrar el modal de carga y eliminar cualquier residuo en el DOM
      Swal.close();
      $(".swal2-container").remove();
      $(".swal2-shown").removeClass("swal2-shown");
      $("body").removeClass("swal2-height-auto");

      // Pequeño tiempo de espera para asegurar que el modal anterior se ha cerrado completamente
      setTimeout(() => {
        // Verificar si hay un mensaje específico en la respuesta
        let errorMessage =
          "No se pudo eliminar el programa. Verifique su conexión o contacte al administrador.";

        try {
          const response = JSON.parse(xhr.responseText);
          if (response && response.message) {
            errorMessage = response.message;
          }
        } catch (e) {
          console.error("Error al parsear respuesta:", e);
        }

        // Mostrar mensaje de error
        Swal.fire({
          icon: "error",
          title: "Error",
          text: errorMessage,
        });

        // Registrar error en consola para depuración
        console.error("Error al eliminar programa:", error);
      }, 300);
    },
  });
}

/**
 * Recarga todas las tablas de programas fitosanitarios
 */
function recargarTablasProgramas() {
  // Array con los selectores de todas las tablas
  const tablas = [
    "#tablaPrograma_plantines_SG",
    "#tablaPrograma_post_cosecha_SG",
    "#tablaPrograma_cosecha_SG",
    "#tablaPrograma_plantines_AC",
    "#tablaPrograma_postcosecha_AC",
    "#tablaPrograma_cosecha_AC",
    "#tablaPrograma_plantines_MC",
    "#tablaPrograma_postcosecha_MC",
    "#tablaPrograma_cosecha_MC",
    "#tablaPrograma_plantines_SG56",
    "#tablaPrograma_postcosecha_SG56",
    "#tablaPrograma_cosecha_SG56",
  ];

  // Recargar cada tabla
  tablas.forEach((selector) => {
    if ($.fn.DataTable.isDataTable(selector)) {
      $(selector).DataTable().ajax.reload();
    }
  });
}

//#############################################################################
// EDITAR PROGRAMA
//#############################################################################

/**
 * Abre el modal para editar un programa existente
 * @param {number} idPrograma - ID del programa a editar
 */

/**
 * Abre el formulario para editar un programa existente
 * @param {number} idPrograma - ID del programa a editar
 */
function editarPrograma(idPrograma) {
  if (!idPrograma) return;

  // Mostrar indicador de carga
  Swal.fire({
    title: "Cargando datos...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Obtener datos del programa
  $.ajax({
    url: `/aplicaciones/programas_cv/${idPrograma}/`,
    type: "GET",
    success: function (response) {
      Swal.close();

      if (response.data) {
        // Determinar a qué fase pertenece el programa
        const idFase = parseInt(response.data.IDFASE);

        // Si es fase de Producción (3), usar el formulario específico
        if (idFase === 3) {
          cargarDatosEnFormularioProduccion(response.data);
        } else {
          // Para otras fases, usar el formulario general
          cargarDatosEnFormulario(response.data);
        }
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudo cargar la información del programa",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.close();

      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al cargar los datos del programa. Intente nuevamente.",
      });

      console.error("Error al cargar programa:", error);
    },
  });
}

/**
 * Carga los datos del programa en el formulario para edición
 * @param {Object} datos - Datos del programa
 */
function cargarDatosEnFormulario(datos) {
  // Resetear formulario antes de cargar nuevos datos
  resetearFormularioPrograma();

  // Preparar el formulario para edición
  prepararFormularioEdicion(datos.ID);

  // Llenar campos con datos del programa
  $("#modalIdFase").val(datos.IDFASE);
  $("#modalIdVariedad").val(datos.IDVARIEDAD);
  $("#nombrePrograma").val(datos.NOMBRE_PROGRAMA);

  // Convertir fechas de DD/MM/YYYY a YYYY-MM-DD para input type="date"
  $("#fechaInicio").val(convertirFechaParaFormulario(datos.FECHA_INICIO));
  $("#fechaFin").val(convertirFechaParaFormulario(datos.FECHA_FIN));
  $("#descripcion_programa").val(datos.DESCRIPCION || "");

  // Personalizar título del modal para edición
  const nombreFase = datos.FASE_DESCRIPCION || obtenerNombreFase(datos.IDFASE);
  $("#modalCrearProgramaLabel").html(`
    <i class="fas fa-edit mr-2"></i> Editar Programa Fitosanitario - ${nombreFase}
  `);

  // Mostrar modal
  $("#modalCrearPrograma").modal("show");
}

/**
 * Convierte una fecha del formato DD/MM/YYYY al formato YYYY-MM-DD para inputs HTML
 * @param {string} fecha - Fecha en formato DD/MM/YYYY
 * @returns {string} Fecha en formato YYYY-MM-DD
 */
function convertirFechaParaFormulario(fecha) {
  if (!fecha) return "";

  // Verificar formato de fecha (DD/MM/YYYY)
  const partes = fecha.split("/");
  if (partes.length !== 3) return "";

  const dia = partes[0];
  const mes = partes[1];
  const anio = partes[2];

  return `${anio}-${mes}-${dia}`;
}

/**
 * Prepara el formulario para modo edición
 * @param {number} idPrograma - ID del programa que se está editando
 */
function prepararFormularioEdicion(idPrograma) {
  // Agregar atributo con el ID del programa que se está editando
  $("#formCrearPrograma").attr("data-modo", "edicion");
  $("#formCrearPrograma").attr("data-id", idPrograma);

  // Cambiar texto y comportamiento del botón guardar
  $("#btnGuardarPrograma")
    .html('<i class="fas fa-save mr-1"></i> Actualizar Programa')
    .removeClass("btn-primary")
    .addClass("btn-success");
}

/**
 * Obtiene el nombre de una fase por su ID
 * @param {number} idFase - ID de la fase
 * @returns {string} Nombre de la fase
 */
function obtenerNombreFase(idFase) {
  const fases = {
    1: "Plantines",
    2: "Post Cosecha",
    3: "Producción",
  };

  return fases[idFase] || "Desconocido";
}

//#############################################################################
// DETALLES DEL PROGRAMA
//#############################################################################

/**
 * Abre el modal de detalles de un programa y carga sus productos
 * @param {number} idPrograma - ID del programa a visualizar
 */
function verDetallesPrograma(idPrograma) {
  if (!idPrograma) {
    console.error("ID de programa no proporcionado");
    return;
  }

  // Guardar el ID del programa en un atributo del modal para usarlo después
  $("#modalDetalleProductos_sweet_globe_plantines").attr(
    "data-programa-id",
    idPrograma
  );

  // Mostrar indicador de carga
  Swal.fire({
    title: "Cargando detalles...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Obtener datos del programa
  $.ajax({
    url: `/aplicaciones/programas_cv/${idPrograma}/`,
    type: "GET",
    success: function (responseProgramas) {
      if (responseProgramas.data) {
        const programa = responseProgramas.data;
        // Llenar los datos básicos del programa en el modal
        $("#nombreProgramaDetalle_plantines_SG").text(programa.NOMBRE_PROGRAMA);
        $("#fechaInicioProgramaDetalle_plantines_SG").text(
          programa.FECHA_INICIO
        );
        $("#fechaFinProgramaDetalle_plantines_SG").text(programa.FECHA_FIN);
        $("#descripcionProgramaDetalle_plantines_SG").text(
          programa.DESCRIPCION || "Sin descripción"
        );

        // Configurar el botón para agregar nuevo producto
        $("#btnNuevoProductoSGPlantines")
          .off("click")
          .on("click", function () {
            abrirModalNuevoProducto(idPrograma);
          });

        // Obtener los productos asociados al programa
        obtenerProductosPrograma(idPrograma);
      } else {
        Swal.close();
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudo cargar la información del programa",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.close();
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al cargar los datos del programa. Intente nuevamente.",
      });
      console.error("Error al cargar programa:", error);
    },
  });
}

/**
 * Obtiene los productos asociados a un programa y los muestra en la tabla
 * @param {number} idPrograma - ID del programa
 */
function obtenerProductosPrograma(idPrograma) {
  $.ajax({
    url: `/aplicaciones/programas_cv/${idPrograma}/detalles/`,
    type: "GET",
    success: function (responseDetalles) {
      Swal.close();

      if (responseDetalles.status === "success") {
        const productos = responseDetalles.data || [];

        // Actualizar contador de productos
        $("#totalProductosProgramaDetalle").text(productos.length);

        // Calcular costo total
        let costoTotal = 0;
        productos.forEach((item) => {
          costoTotal += parseFloat(item.PRECIO_HA || 0);
        });

        $("#costoTotalProgramaDetalle").text(`$ ${costoTotal.toFixed(2)}`);
        $("#totalCostoProductos").text(costoTotal.toFixed(3));

        // Inicializar o actualizar la tabla de productos
        initTablaDetalleProductos(productos);

        // Mostrar el modal
        $("#modalDetalleProductos_sweet_globe_plantines").modal("show");
      } else {
        Swal.fire({
          icon: "warning",
          title: "Sin productos",
          text: "Este programa no tiene productos registrados",
        });

        // Mostrar el modal con tabla vacía
        initTablaDetalleProductos([]);
        $("#modalDetalleProductos_sweet_globe_plantines").modal("show");
      }
    },
    error: function (xhr, status, error) {
      Swal.close();
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al cargar los productos del programa. Intente nuevamente.",
      });
      console.error("Error al cargar productos del programa:", error);
    },
  });
}

/**
 * Inicializa o actualiza la tabla de detalle de productos
 * @param {Array} productos - Array de productos a mostrar
 */

function initTablaDetalleProductos(productos) {
  // Destruir la tabla si ya existe
  if ($.fn.DataTable.isDataTable("#tablaDetalleProductos_plantines_SG")) {
    $("#tablaDetalleProductos_plantines_SG").DataTable().destroy();
  }

  // Limpiar el cuerpo de la tabla
  $("#detalleProductosBody").empty();

  // Inicializar tabla con DataTables
  const tabla = $("#tablaDetalleProductos_plantines_SG").DataTable({
    responsive: true,
    autoWidth: false,
    data: productos,
    columns: [
      {
        // Numeración
        data: null,
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
        className: "text-center",
      },
      { data: "DIA", className: "text-center" },
      { data: "SUBGRUPO" },
      { data: "IDPRODUCTO" },
      { data: "OBJETIVO" },
      { data: "PRODUCTO" },
      { data: "MATERIA_ACTIVA" },
      { data: "DOSIS", className: "text-center" },
      { data: "UND", className: "text-center" },
      { data: "MOJAMIENTO", className: "text-center" },
      { data: "NECESIDAD_HA", className: "text-center" },
      { data: "UND2", className: "text-center" },
      {
        data: "PRECIO",
        className: "text-center",
        render: function (data) {
          return parseFloat(data || 0).toFixed(2);
        },
      },
      {
        data: "PRECIO_HA",
        className: "text-center",
        render: function (data) {
          return parseFloat(data || 0).toFixed(2);
        },
      },
      { data: "OBSERVACIONES" },
      {
        // Columna de acciones
        data: null,
        className: "text-center",
        render: function (data, type, row) {
          return `
            <div class="btn-group btn-group-sm">

              
              <button type="button" class="btn btn-info btn-editar-producto" data-id="${row.ID}" title="Editar">
                <i class="fas fa-edit"></i>
              </button>

              
              <button type="button" class="btn btn-danger btn-eliminar-producto" data-id="${row.ID}" title="Eliminar">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          `;
        },
      },
    ],
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    dom:
      "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
      "<'row'<'col-sm-12'tr>>" +
      "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
    order: [[1, "asc"]], // Ordenar por la columna DIA ascendente
  });

  // Configurar eventos para los botones de editar y eliminar
  $("#tablaDetalleProductos tbody").on(
    "click",
    ".btn-editar-producto",
    function () {
      const idProducto = $(this).data("id");
      editarProducto(idProducto);
    }
  );

  // Asociar eventos a los botones de la tabla después de inicializarla
  $("#tablaDetalleProductos_plantines_SG").on(
    "click",
    ".btn-eliminar-producto",
    function () {
      const idProducto = $(this).data("id");
      eliminarProducto(idProducto);
    }
  );
}

/**
 * Abre el modal para agregar un nuevo producto al programa
 * @param {number} idPrograma - ID del programa al que se agregará el producto
 */
function abrirModalNuevoProducto(idPrograma) {
  // Resetear formulario
  resetearFormularioProducto();

  // Asignar el ID del programa al campo oculto
  $("#programaId").val(idPrograma);

  // Personalizar título del modal
  $("#modalProductoLabel").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar Producto al Programa'
  );

  // Abrir modal
  $("#modalProducto").modal("show");
}

/**
 * Resetea los campos del formulario de producto
 */
function resetearFormularioProducto() {
  // Resetear valores del formulario
  $("#formProducto")[0].reset();

  // Inicializar valores predeterminados
  $("#diaProducto").val(0);
  $("#mojamientoProducto").val(0);

  // Eliminar cualquier atributo de modo de edición anterior
  $("#formProducto").removeAttr("data-id");
  $("#productoId").val("");

  // Resetear estilo y texto del botón guardar
  $("#btnGuardarProducto")
    .html('<i class="fas fa-save mr-1"></i> Guardar Producto')
    .removeClass("btn-success")
    .addClass("btn-primary");

  // Eliminar cualquier dropdown de sugerencias que pudiera estar abierto
  $("#sugerenciasProducto").remove();

  // Calcular valores iniciales para los campos calculados
  calcularNecesidadHa();
  calcularPrecioHa();
}

/**
 * Calcula la necesidad por hectárea basado en dosis y mojamiento
 */
function calcularNecesidadHa() {
  // Obtener valores actuales
  const dosis = parseFloat($("#dosisProducto").val()) || 0;
  const mojamiento = parseFloat($("#mojamientoProducto").val()) || 0;

  // Necesidad por ha = (dosis * mojamiento) / 100
  const necesidadHa = (dosis * mojamiento) / 100;

  // Actualizar el campo de necesidad
  $("#necesidadProducto").val(necesidadHa.toFixed(5));

  // Mantener la misma unidad
  $("#unidadNecesidadProducto").val($("#unidadProducto").val());

  // Recalcular precio/ha cuando cambia la necesidad
  calcularPrecioHa();
}

/**
 * Calcula el precio por hectárea basado en necesidad y precio unitario
 */
function calcularPrecioHa() {
  const necesidadHa = parseFloat($("#necesidadProducto").val()) || 0;
  const precioUnitario = parseFloat($("#precioProducto").val()) || 0;

  // Precio por ha = necesidad * precio unitario
  const precioHa = necesidadHa * precioUnitario;

  $("#precioHaProducto").val(precioHa.toFixed(2));
}

/**
 * Inicializa los eventos para el formulario de productos
 */
function initEventosFormularioProducto() {
  // Eventos para cálculos automáticos
  $("#dosisProducto, #mojamientoProducto").on("input", calcularNecesidadHa);
  $("#precioProducto").on("input", calcularPrecioHa);

  // Evento para el cambio de unidad
  $("#unidadProducto").on("change", function () {
    $("#unidadNecesidadProducto").val($(this).val());
    calcularNecesidadHa();
  });

  // Agregar inicialización del autocompletado para objetivo
  agregarEstilosAutocompletado();
  initAutocompletadoObjetivo();

  // Inicializar el autocompletado para productos
  initAutocompletadoProducto();
}

/**
 * Inicializa el autocompletado para el campo de producto
 * Permite buscar productos mientras el usuario escribe
 */

function initAutocompletadoProducto() {
  // Añadir placeholder más descriptivo
  $("#nombreProducto")
    .attr(
      "placeholder",
      "Escriba para buscar y autocompletar todos los campos..."
    )
    .attr("autocomplete", "off") // Desactivar autocompletado del navegador
    .addClass("autocomplete-primary"); // Agregar clase para destacar este campo como principal

  // Añadir un icono al campo para indicar que es un campo con búsqueda
  const inputContainer = $("#nombreProducto").parent();

  // Solo agregar el icono si no existe ya
  if (inputContainer.find(".input-icon-search").length === 0) {
    $("#nombreProducto").css({
      "padding-left": "30px",
    });

    $("<i>")
      .addClass("fas fa-search input-icon-search")
      .css({
        position: "absolute",
        left: "10px",
        top: "50%",
        transform: "translateY(-50%)",
        color: "#adb5bd",
        fontSize: "14px",
        pointerEvents: "none", // Evitar que el icono interfiera con el input
        transition: "all 0.2s ease",
      })
      .prependTo(inputContainer);

    // Agregar etiqueta informativa sobre autocomplete debajo del campo
    const infoLabel = $("<small>")
      .addClass("text-primary autocomplete-info")
      .html(
        "<i class='fas fa-info-circle mr-1'></i>Este campo autocompleta el resto del formulario"
      )
      .css({
        display: "block",
        marginTop: "5px",
        fontSize: "85%",
        width: "100%",
        textAlign: "left",
        clear: "both",
      });

    // Insertar después del input en lugar de dentro del contenedor
    $("#nombreProducto").after(infoLabel);
  }

  // Agregar evento para cambiar el color del icono al enfocar el input
  $("#nombreProducto")
    .on("focus", function () {
      inputContainer.find(".input-icon-search").css("color", "#007bff");
    })
    .on("blur", function () {
      inputContainer.find(".input-icon-search").css("color", "#adb5bd");
    });

  // Agregar evento de input para búsqueda automática con mejor experiencia de usuario
  $("#nombreProducto").on("input", function () {
    const termino = $(this).val().trim();

    // Cambiar el icono mientras se escribe
    if (termino.length > 0) {
      inputContainer
        .find(".input-icon-search")
        .removeClass("fa-search")
        .addClass("fa-keyboard");
    } else {
      inputContainer
        .find(".input-icon-search")
        .removeClass("fa-keyboard")
        .addClass("fa-search");
    }

    // Eliminar el dropdown existente si el campo está vacío
    if (termino.length === 0) {
      $("#sugerenciasProducto").remove();
      return;
    }

    // Solo buscar si hay al menos 3 caracteres
    if (termino.length >= 3) {
      // Limpiar cualquier timeout anterior para evitar múltiples peticiones
      if (window.timeoutProducto) {
        clearTimeout(window.timeoutProducto);
      }

      // Mostrar un pequeño indicador visual de que se está buscando
      $(this).addClass("loading");

      // Cambiar el ícono a uno de carga
      inputContainer
        .find(".input-icon-search")
        .removeClass("fa-keyboard")
        .addClass("fa-spinner fa-spin");

      // Esperar un breve período antes de realizar la búsqueda para evitar demasiadas peticiones
      window.timeoutProducto = setTimeout(function () {
        buscarProductosAutomatico(termino);
      }, 400);
    }
  });

  // Agregar evento para cerrar el dropdown al presionar Escape
  $("#nombreProducto").on("keydown", function (e) {
    if (e.key === "Escape") {
      $("#sugerenciasProducto").remove();
    }
  });
}

/**
 * Busca productos automáticamente mientras el usuario escribe
 * @param {string} termino - Texto que se está buscando
 */
function buscarProductosAutomatico(termino) {
  // Preparar los parámetros de búsqueda
  const params = {
    idgrupo: 2400, // Valor fijo según requerimiento
  };

  // Determinar si el término parece ser un ID de producto (solo números)
  if (/^\d+$/.test(termino)) {
    params.idproducto = termino; // Es un número, buscar por ID
  } else {
    params.descripcion = termino; // Es texto, buscar por descripción
  }

  // Opcional: obtener el subgrupo seleccionado si existe
  const subgrupoSeleccionado =
    $("#subGrupoProductoAuto").val() || $("#subGrupoProducto").val();
  if (subgrupoSeleccionado) {
    // Obtener el mapeo de subgrupos si está disponible
    const subgruposMap = $("#subGrupoProducto").data("subgrupos-map") || {};
    const idSubgrupo = subgruposMap[subgrupoSeleccionado];

    // Solo agregar el parámetro si se encontró un ID de subgrupo
    if (idSubgrupo) {
      params.idsubgrupo = idSubgrupo;
    }
  }

  // Realizar petición AJAX para buscar productos
  $.ajax({
    url: "/aplicaciones/productos/",
    type: "GET",
    data: params,
    success: function (response) {
      // Quitar clase de cargando
      $("#nombreProducto").removeClass("loading");

      // Restaurar icono original
      $("#nombreProducto")
        .parent()
        .find(".input-icon-search")
        .removeClass("fa-spinner fa-spin")
        .addClass("fa-keyboard");

      // Verificar si hay datos en la respuesta
      if (response && response.data && response.data.length > 0) {
        // Si hay solo un producto y es una coincidencia exacta, seleccionarlo automáticamente
        if (
          response.data.length === 1 &&
          (response.data[0].IDPRODUCTO === termino ||
            response.data[0].DESCRIPCION.toLowerCase() ===
              termino.toLowerCase())
        ) {
          seleccionarProducto(response.data[0]);
        } else {
          // Mostrar sugerencias en un dropdown personalizado
          mostrarSugerenciasProductos(response.data);
        }
      } else {
        // Si no hay resultados, mostrar mensaje informativo en un dropdown
        mostrarMensajeNoResultados(termino);
      }
    },
    error: function (xhr, status, error) {
      // Quitar clase de cargando
      $("#nombreProducto").removeClass("loading");
      // Restaurar icono original
      $("#nombreProducto")
        .parent()
        .find(".input-icon-search")
        .removeClass("fa-spinner fa-spin")
        .addClass("fa-keyboard");

      console.error("Error al buscar productos:", error);
    },
  });
}

/**
 * Muestra un mensaje cuando no se encuentran productos
 * @param {string} termino - Término buscado
 */
function mostrarMensajeNoResultados(termino) {
  // Remover cualquier dropdown existente
  $("#sugerenciasProducto").remove();

  // Crear dropdown con mensaje
  const dropdown = $("<div>")
    .attr("id", "sugerenciasProducto")
    .addClass("productos-dropdown")
    .css({
      position: "absolute",
      width: $("#nombreProducto").outerWidth(),
      zIndex: 9999,
      backgroundColor: "white",
      border: "1px solid #ced4da",
      borderRadius: "8px",
      boxShadow: "0 6px 16px rgba(0,0,0,.15)",
      marginTop: "5px",
    });

  dropdown.append(
    $("<div>").addClass("p-3 text-center").html(`
        <div class="text-muted mb-2">
          <i class="fas fa-search mr-2"></i>No se encontraron productos
        </div>
        <small class="d-block">Intente con otro término o consulte el catálogo completo</small>
      `)
  );

  // Agregar al DOM
  const inputContainer = $("#nombreProducto").closest(".form-group");
  inputContainer.css("position", "relative");
  inputContainer.append(dropdown);

  // Cerrar al hacer clic fuera
  $(document).on("click", function (e) {
    if (!$(e.target).closest("#nombreProducto, #sugerenciasProducto").length) {
      dropdown.remove();
    }
  });
}

/**
 * Muestra sugerencias de productos en un dropdown personalizado
 * @param {Array} productos - Lista de productos encontrados
 */
function mostrarSugerenciasProductos(productos) {
  // Remover cualquier dropdown existente
  $("#sugerenciasProducto").remove();

  // Crear el dropdown
  const dropdown = $("<div>")
    .attr("id", "sugerenciasProducto")
    .addClass("productos-dropdown")
    .css({
      position: "absolute",
      width: $("#nombreProducto").outerWidth() + 50, // Ancho un poco mayor para mejor visualización
      maxHeight: "300px", // Mayor altura para mostrar más elementos
      overflowY: "auto",
      zIndex: 9999,
      backgroundColor: "white",
      border: "1px solid #ced4da",
      borderRadius: "8px", // Esquinas más redondeadas
      boxShadow: "0 6px 16px rgba(0,0,0,.15)", // Sombra más pronunciada
      marginTop: "40px", // Importante: espacio para que no tape el campo de entrada
      left: "0",
    });

  // Agregar título al dropdown
  dropdown.append(
    $("<div>")
      .addClass("productos-dropdown-header")
      .css({
        padding: "6px 10px",
        borderBottom: "1px solid #e9ecef",
        fontWeight: "bold",
        backgroundColor: "#f8f9fa",
        color: "#495057",
        fontSize: "10px", // Reducido de 12px a 10px
        borderTopLeftRadius: "8px",
        borderTopRightRadius: "8px",
      })
      .html(
        `<i class="fas fa-list mr-1"></i>Productos encontrados (${productos.length})`
      )
  );

  // Agregar elementos al dropdown con mejor diseño
  productos.forEach((producto) => {
    const idProducto = producto.IDPRODUCTO ? producto.IDPRODUCTO.trim() : "";
    const descripcion = producto.DESCRIPCION ? producto.DESCRIPCION.trim() : "";
    const materiaActiva = producto.MATERIA_ACTIVA
      ? producto.MATERIA_ACTIVA.trim()
      : "Sin información";
    const idMedida = producto.IDMEDIDA ? producto.IDMEDIDA.trim() : "-";
    const ultimoPrecio = producto.ultimo_precio
      ? parseFloat(producto.ultimo_precio).toFixed(2)
      : "0.00";

    const item = $("<div>")
      .addClass("producto-item")
      .css({
        padding: "5px 8px", // Reducido de 6px a 5px
        borderBottom: "1px solid #f0f0f0",
        cursor: "pointer",
        transition: "all 0.2s ease",
      })
      .html(
        `
        <div class="d-flex justify-content-between align-items-start mb-1">
          <div class="d-flex align-items-center" style="max-width: 85%;">
            <div class="badge badge-primary mr-1" style="min-width: 75px; font-size: 9px; overflow: visible; white-space: nowrap;">${idProducto}</div>
            <div class="producto-nombre" style="color: #2c3e50; font-size: 10px; font-weight: 500; overflow: hidden; text-overflow: ellipsis;">${descripcion}</div>
        </div>
          <div class="badge badge-info" style="font-size: 8px; margin-left: 2px;">${idMedida}</div>
        </div>
        <div class="d-flex justify-content-between" style="margin-left: 75px; font-size: 9px;">
          <div class="text-muted" style="max-width: 65%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            <i class="fas fa-flask mr-1" style="color: #6c757d; font-size: 8px;"></i>${materiaActiva}
          </div>
          <div style="color: #28a745; font-weight: 500; min-width: 50px; text-align: right;">
            <i class="fas fa-dollar-sign mr-1" style="font-size: 8px;"></i>${ultimoPrecio}
          </div>
        </div>
      `
      )
      .hover(
        function () {
          $(this).css({
            backgroundColor: "#f8f9fa",
            transform: "translateX(5px)",
          });
        },
        function () {
          $(this).css({
            backgroundColor: "",
            transform: "translateX(0)",
          });
        }
      )
      .on("click", function () {
        seleccionarProducto(producto);
        dropdown.remove();
      });

    dropdown.append(item);
  });

  // Agregar pie del dropdown con instrucciones
  if (productos.length > 0) {
    dropdown.append(
      $("<div>")
        .addClass("productos-dropdown-footer")
        .css({
          padding: "5px 10px", // Reducido de 6px a 5px
          borderTop: "1px solid #e9ecef",
          fontSize: "9px", // Reducido de 10px a 9px
          color: "#6c757d",
          textAlign: "center",
          backgroundColor: "#f8f9fa",
          borderBottomLeftRadius: "8px",
          borderBottomRightRadius: "8px",
        })
        .html(
          '<i class="fas fa-info-circle mr-1"></i>Haga clic en un producto para seleccionarlo'
        )
    );
  } else {
    // Mensaje cuando no hay productos
    dropdown.append(
      $("<div>")
        .addClass("productos-dropdown-empty")
        .css({
          padding: "10px", // Reducido de 12px a 10px
          textAlign: "center",
          color: "#6c757d",
          fontSize: "10px", // Reducido de 11px a 10px
        })
        .html('<i class="fas fa-search mr-2"></i>No se encontraron productos')
    );
  }

  // Agregar el dropdown al DOM, cerca pero no dentro del contenedor del input
  const inputContainer = $("#nombreProducto").closest(".form-group");
  inputContainer.css("position", "relative");
  inputContainer.append(dropdown);

  // Agregar estilos personalizados para la barra de desplazamiento
  const scrollbarStyles = `
    <style>
      #sugerenciasProducto::-webkit-scrollbar {
        width: 6px;
      }
      #sugerenciasProducto::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
      }
      #sugerenciasProducto::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 10px;
      }
      #sugerenciasProducto::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
      }
    </style>
  `;
  $("head").append(scrollbarStyles);

  // Cerrar el dropdown al hacer clic fuera de él
  $(document).on("click", function (e) {
    if (!$(e.target).closest("#nombreProducto, #sugerenciasProducto").length) {
      dropdown.remove();
      $("head style").last().remove(); // Eliminar los estilos personalizados del scrollbar
    }
  });
}

/**
 * Función modificada para resetear el formulario de producto
 */
function resetearFormularioProducto() {
  // Resetear valores del formulario
  $("#formProducto")[0].reset();

  // Inicializar valores predeterminados
  $("#diaProducto").val(0);
  $("#mojamientoProducto").val(0);

  // Eliminar cualquier atributo de modo de edición anterior
  $("#formProducto").removeAttr("data-id");
  $("#productoId").val("");

  // Resetear estilo y texto del botón guardar
  $("#btnGuardarProducto")
    .html('<i class="fas fa-save mr-1"></i> Guardar Producto')
    .removeClass("btn-success")
    .addClass("btn-primary");

  // Eliminar cualquier dropdown de sugerencias que pudiera estar abierto
  $("#sugerenciasProducto").remove();

  // Resetear la marca de edición manual para el campo necesidadProducto
  $("#necesidadProducto").data("editado", false);

  // Calcular valores iniciales para los campos calculados
  calcularNecesidadHa();
  calcularPrecioHa();
}

/**
 * Función modificada para seleccionar y completar datos del producto
 */
function seleccionarProducto(producto) {
  // Limpiar espacios en blanco de los campos
  const idProducto = producto.IDPRODUCTO ? producto.IDPRODUCTO.trim() : "";
  const descripcion = producto.DESCRIPCION ? producto.DESCRIPCION.trim() : "";
  const materiaActiva = producto.MATERIA_ACTIVA
    ? producto.MATERIA_ACTIVA.trim()
    : "";
  const idMedida = producto.IDMEDIDA ? producto.IDMEDIDA.trim() : "";
  const ultimoPrecio = producto.ultimo_precio
    ? parseFloat(producto.ultimo_precio)
    : 0;

  // Obtener descripción del subgrupo de las posibles propiedades que lo pueden contener
  let descripcionSubgrupo = "";
  if (producto.DESCRIPCION_SUBGRUPO) {
    descripcionSubgrupo = producto.DESCRIPCION_SUBGRUPO;
  } else if (producto.SUBGRUPO) {
    descripcionSubgrupo = producto.SUBGRUPO;
  } else if (producto.DESC_SUBGRUPO) {
    descripcionSubgrupo = producto.DESC_SUBGRUPO;
  }

  console.log("Datos del producto seleccionado:", producto);

  // Llenar campos del formulario con los datos del producto principal
  $("#nombreProducto").val(descripcion);
  $("#materiaActivaProducto").val(materiaActiva);
  $("#subGrupoProducto").val(descripcionSubgrupo);
  $("#precioProducto").val(ultimoPrecio.toFixed(3));

  // Guardar IDs en campos ocultos
  if ($("#productoId").length) {
    $("#productoId").val(idProducto);
  }
  $("#idProductoAPI").val(idProducto);

  // Resetear el estado de edición de campos
  $("#formProducto").data("campo_editado", "");

  // Configurar la unidad de medida según el producto
  if (idMedida) {
    const unidadFormateada = idMedida.trim().toUpperCase();
    if (unidadFormateada.includes("LT") || unidadFormateada.includes("L")) {
      $("#unidadProducto").val("LT");
      $("#unidadNecesidadProducto").val("LT");
    } else if (unidadFormateada.includes("KG")) {
      $("#unidadProducto").val("kg");
      $("#unidadNecesidadProducto").val("kg");
    }
  }

  // Consultar datos adicionales de la API APL_APIPRODUCTOS para autocompletar el resto de campos
  if (idProducto) {
    $("#nombreProducto").addClass("loading");

    obtenerDatosProductoApl(idProducto)
      .then((datosApl) => {
        $("#nombreProducto").removeClass("loading");

        if (datosApl) {
          console.log("Datos adicionales del producto:", datosApl);

          // Autocompletar todos los campos restantes con los datos de la API
          $("#idProductoAPI").val(datosApl.IDPRODUCTO || idProducto);
          $("#objetivoProducto").val(datosApl.OBJETIVO || "");
          $("#dosisProducto").val(datosApl.DOSIS || "");
          $("#mojamientoProducto").val(datosApl.MOJAMIENTO || "");
          $("#observacionesProducto").val(datosApl.OBSERVACIONES || "");

          // Actualizar campo de subgrupo si viene de la API
          if (datosApl.SUBGRUPOPROGRAMA) {
            $("#subGrupoProducto").val(datosApl.SUBGRUPOPROGRAMA);
            // Si existe el campo de autocompletado, actualizarlo también
            if ($("#subGrupoProductoAuto").length) {
              $("#subGrupoProductoAuto").val(datosApl.SUBGRUPOPROGRAMA);
            }
          }

          // Actualizar precio si viene de la API
          /* if (datosApl.PRECIO) {
            $("#precioProducto").val(parseFloat(datosApl.PRECIO).toFixed(3));
          } */

          // Actualizar unidad según la API
          if (datosApl.UND) {
            const unidad = datosApl.UND.trim().toUpperCase();
            if (unidad.includes("LT") || unidad.includes("L")) {
              $("#unidadProducto").val("LT");
              $("#unidadNecesidadProducto").val("LT");
            } else if (unidad.includes("KG")) {
              $("#unidadProducto").val("kg");
              $("#unidadNecesidadProducto").val("kg");
            }
          }

          // Resetear el estado de edición
          $("#formProducto").data("campo_editado", "");

          // Recalcular campos automáticos
          calcularNecesidadHa();
          calcularPrecioHa();
        }
      })
      .catch((error) => {
        $("#nombreProducto").removeClass("loading");
        console.error("Error al obtener datos adicionales:", error);
      });
  }

  // Recalcular campos automáticos
  calcularNecesidadHa();
  calcularPrecioHa();

  // Notificación de éxito
  Swal.fire({
    icon: "success",
    title: "Producto seleccionado",
    text: `Se ha seleccionado el producto: ${descripcion}`,
    timer: 1500,
    showConfirmButton: false,
  });
}

/**
 * Agregar estilos específicos para el dropdown de productos
 */
function agregarEstilosAutocompletado() {
  // Verificar si los estilos ya existen
  if ($("#estilos-autocompletado").length === 0) {
    $("head").append(`
      <style id="estilos-autocompletado">
          /* Estilos para jQuery UI Autocomplete */
          .ui-autocomplete {
              max-height: 250px;
              overflow-y: auto;
              overflow-x: hidden;
              z-index: 9999 !important;
              border: 1px solid #ddd;
              box-shadow: 0 6px 12px rgba(0,0,0,.1);
              border-radius: 0 0 8px 8px;
              background-color: white;
              padding: 5px 0;
          }
          
          .ui-autocomplete .ui-menu-item {
              padding: 0;
              margin: 0;
          }
          
          .autocomplete-item {
              padding: 10px 15px;
              cursor: pointer;
              font-size: 13px;
              transition: all 0.2s ease;
              display: block;
              border-bottom: 1px solid #f5f5f5;
          }
          
          .ui-autocomplete .ui-menu-item:last-child .autocomplete-item {
              border-bottom: none;
          }
          
          .ui-autocomplete .ui-menu-item:hover .autocomplete-item,
          .ui-autocomplete .ui-menu-item.ui-state-focus .autocomplete-item,
          .ui-autocomplete .ui-menu-item.ui-state-active .autocomplete-item {
              background-color: #f8f9fa;
              color: #007bff;
              transform: translateX(3px);
          }
          
          /* Estilos para el indicador de carga en campos de entrada */
          input.loading {
              background-image: url('/static/core/img/loading.gif');
              background-size: 20px 20px;
              background-position: right 10px center;
              background-repeat: no-repeat;
              padding-right: 40px;
              transition: all 0.3s ease;
          }
          
          /* Estilos para los dropdowns personalizados */
          .productos-dropdown {
              animation: fadeInDown 0.3s ease forwards;
          }
          
          .producto-item {
              border-left: 3px solid transparent;
          }
          
          .producto-item:hover {
              border-left: 3px solid #007bff;
          }
          
          /* Animaciones */
          @keyframes fadeInDown {
              from {
                  opacity: 0;
                  transform: translateY(-10px);
              }
              to {
                  opacity: 1;
                  transform: translateY(0);
              }
          }
          
          /* Estilos para el contenedor de sugerencias de subgrupo */
          #sugerenciasSubgrupo {
              max-height: 250px;
              border-radius: 8px;
              margin-top: 5px;
              box-shadow: 0 6px 16px rgba(0,0,0,.1);
              border: 1px solid #ddd;
          }
          
          #sugerenciasSubgrupo .autocomplete-suggestion {
              padding: 10px 15px;
              transition: all 0.2s ease;
              border-bottom: 1px solid #f5f5f5;
          }
          
          #sugerenciasSubgrupo .autocomplete-suggestion:last-child {
              border-bottom: none;
          }
          
          #sugerenciasSubgrupo .autocomplete-suggestion:hover {
              background-color: #f8f9fa;
              color: #007bff;
              transform: translateX(3px);
          }
          
          /* Mejoras en los inputs */
          input[type="text"], 
          input[type="number"],
          select {
              transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
          }
          
          input[type="text"]:focus, 
          input[type="number"]:focus,
          select:focus {
              border-color: #80bdff;
              box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.15);
          }
      </style>
    `);
  }
}

/* ############################################################################ */
/* GUARDAR PRODUCTO */
/* ############################################################################ */

// let isSubmitting = false;

function guardarProducto() {
  // Evitar múltiples envíos
  if (isSubmitting) {
    console.log("Ya hay una solicitud en proceso");
    return;
  }

  // Validar formulario
  if (!validarFormularioProducto()) {
    return;
  }

  isSubmitting = true;

  // Obtener datos del formulario
  const formData = obtenerDatosFormularioProducto();

  // Determinar si es edición o creación
  const idProducto = $("#formProducto").attr("data-id");
  const esEdicion = !!idProducto;

  // Limpieza completa del DOM de SweetAlert2 y modales
  $(".swal2-container").remove();
  $(".modal-backdrop").remove();
  $("body").removeClass("swal2-shown swal2-height-auto modal-open");
  $("#swal-custom-styles").remove();
  document.documentElement.style.overflow = "";
  document.documentElement.style.paddingRight = "";

  // Mostrar indicador de carga simple
  Swal.fire({
    title: "Guardando producto...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
    customClass: {
      container: "swal-z-index-highest",
    },
    backdrop: `rgba(0,0,0,0.4)`,
    heightAuto: false,
  });

  // Configurar parámetros de la petición según el modo
  const ajaxConfig = {
    url: esEdicion
      ? `/aplicaciones/programas_cv/detalles/${idProducto}/`
      : "/aplicaciones/programas_cv/detalles/",
    type: esEdicion ? "PUT" : "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      isSubmitting = false;

      // Limpieza completa antes de cerrar
      $(".swal2-container").remove();
      $(".modal-backdrop").remove();
      $("body").removeClass("swal2-shown swal2-height-auto modal-open");
      document.documentElement.style.overflow = "";
      document.documentElement.style.paddingRight = "";

      // Cerrar Swal actual
      Swal.close();

      // Retraso para asegurar actualización del DOM
      setTimeout(() => {
        if (response.status === "success") {
          // Recargar productos del programa
          const idPrograma = $(
            "#modalDetalleProductos_sweet_globe_plantines"
          ).attr("data-programa-id");

          // Cerrar modal de producto
          $("#modalProducto").modal("hide");

          // Limpieza adicional después de cerrar el modal
          $(".modal-backdrop").remove();
          $("body").removeClass("modal-open");
          document.documentElement.style.overflow = "";
          document.documentElement.style.paddingRight = "";

          // Agregar estilos para SweetAlert2
          if (!$("#swal-custom-styles").length) {
            $("head").append(`
              <style id="swal-custom-styles">
                .swal-z-index-highest {
                  z-index: 9999 !important;
                }
                .swal2-popup {
                  z-index: 10000 !important;
                }
              </style>
            `);
          }

          // Mostrar alerta de éxito
          Swal.fire({
            icon: "success",
            title: "¡Éxito!",
            text: esEdicion
              ? "Producto actualizado correctamente"
              : "Producto agregado correctamente",
            timer: 1800,
            showConfirmButton: false,
            customClass: {
              container: "swal-z-index-highest",
            },
            heightAuto: false,
          }).then(() => {
            // Recargar productos después de cerrar el alert
            obtenerProductosPrograma(idPrograma);
          });
        } else {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: response.message || "No se pudo guardar el producto",
            customClass: {
              container: "swal-z-index-highest",
            },
            heightAuto: false,
          });
        }
      }, 300);
    },
    error: function (xhr, status, error) {
      isSubmitting = false;

      // Limpieza completa del DOM
      $(".swal2-container").remove();
      $(".modal-backdrop").remove();
      $(".swal2-shown").removeClass("swal2-shown");
      $("body").removeClass("swal2-height-auto modal-open");
      $("#swal-custom-styles").remove();
      document.documentElement.style.overflow = "";
      document.documentElement.style.paddingRight = "";

      // Cerrar Swal actual
      Swal.close();

      // Retraso para asegurar actualización del DOM
      setTimeout(() => {
        let errorMessage = "Error al guardar el producto. Intente nuevamente.";
        try {
          const response = JSON.parse(xhr.responseText);
          if (response && response.message) {
            errorMessage = response.message;
          }
        } catch (e) {
          console.error("Error al parsear respuesta:", e);
        }

        // Agregar estilos para SweetAlert2
        if (!$("#swal-custom-styles").length) {
          $("head").append(`
            <style id="swal-custom-styles">
              .swal-z-index-highest {
                z-index: 9999 !important;
              }
              .swal2-popup {
                z-index: 10000 !important;
              }
            </style>
          `);
        }

        Swal.fire({
          icon: "error",
          title: "Error",
          text: errorMessage,
          customClass: {
            container: "swal-z-index-highest",
          },
          heightAuto: false,
        });

        console.error("Error al guardar producto:", error);
      }, 300);
    },
  };

  // Enviar petición AJAX
  $.ajax(ajaxConfig);
}

/**
 * Valida que el formulario de producto tenga todos los campos requeridos
 * @returns {boolean} true si el formulario es válido
 */
function validarFormularioProducto() {
  // Validar campos requeridos
  const camposRequeridos = [
    { id: "programaId", nombre: "ID del programa" },
    { id: "subGrupoProducto", nombre: "Sub Grupo" },
    { id: "objetivoProducto", nombre: "Objetivo" },
    { id: "nombreProducto", nombre: "Producto" },
    { id: "materiaActivaProducto", nombre: "Materia Activa" },
    { id: "dosisProducto", nombre: "Dosis/100L" },
    { id: "mojamientoProducto", nombre: "Mojamiento" },
    { id: "precioProducto", nombre: "Precio/lt-kg" },
  ];

  let camposFaltantes = [];

  camposRequeridos.forEach((campo) => {
    const valor = $(`#${campo.id}`).val();
    // Para el campo diaProducto, permitir que sea 0
    if (campo.id === "diaProducto") {
      if (valor === "" || valor === undefined || valor === null) {
        camposFaltantes.push(campo.nombre);
        $(`#${campo.id}`).addClass("is-invalid");
      } else {
        $(`#${campo.id}`).removeClass("is-invalid");
      }
    } else if (!valor) {
      camposFaltantes.push(campo.nombre);
      $(`#${campo.id}`).addClass("is-invalid");
    } else {
      $(`#${campo.id}`).removeClass("is-invalid");
    }
  });

  if (camposFaltantes.length > 0) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: `Por favor, complete los siguientes campos: ${camposFaltantes.join(
        ", "
      )}.`,
    });
    return false;
  }

  return true;
}

/**
 * Obtiene los datos del formulario de producto formateados para enviar al servidor
 * @returns {Object} Objeto con los datos del formulario
 */
function obtenerDatosFormularioProducto() {
  // Obtener y convertir el ID del programa
  const programaId = parseInt($("#programaId").val()) || 0;

  return {
    IDPROGRAMAAAPL: programaId,
    DIA: parseInt($("#diaProducto").val()) || 0,
    SUBGRUPO: $("#subGrupoProducto").val() || "",
    OBJETIVO: $("#objetivoProducto").val() || "",
    PRODUCTO: $("#nombreProducto").val() || "",
    MATERIA_ACTIVA: $("#materiaActivaProducto").val() || "",
    DOSIS: parseFloat($("#dosisProducto").val()) || 0,
    UND: $("#unidadProducto").val() || "",
    MOJAMIENTO: parseFloat($("#mojamientoProducto").val()) || 0,
    NECESIDAD_HA: parseFloat($("#necesidadProducto").val()) || 0,
    UND2: $("#unidadNecesidadProducto").val() || "",
    PRECIO: parseFloat($("#precioProducto").val()) || 0,
    PRECIO_HA: parseFloat($("#precioHaProducto").val()) || 0,
    OBSERVACIONES: $("#observacionesProducto").val() || "",
    TRATAMIENTO: $("#tratamientoProducto").val() || "",
    FECHA_INTERVALO: $("#fechaIntervaloProducto").val()
      ? moment($("#fechaIntervaloProducto").val(), "YYYY-MM-DD").format(
          "YYYY-MM-DD HH:mm:ss"
        )
      : null,
    IDPRODUCTO: $("#idProductoAPI").val() || "", // Nuevo campo para el IDPRODUCTO
  };
}

/* ############################################################################ */
/* ELIMINAR PRODUCTO */
/* ############################################################################ */

function eliminarProducto(idProducto) {
  // Verificar si ya hay una operación de eliminación en curso
  if (window.isDeleting) {
    console.log(
      "Ya hay una operación de eliminación en curso. Ignorando solicitud."
    );
    return;
  }

  // Marcar que hay una operación en curso
  window.isDeleting = true;

  console.log("Eliminando producto:", idProducto);

  // Usar confirm() para la confirmación del usuario con un mensaje más claro
  const mensajeConfirmacion = `¿Está seguro que desea eliminar este producto?

ID del Producto: ${idProducto}

Esta acción no se puede deshacer.`;

  if (confirm(mensajeConfirmacion)) {
    // Opcional: podrías mostrar un loader/spinner aquí si la operación es larga,
    // pero alert() bloqueará la UI igualmente.

    $.ajax({
      url: `/aplicaciones/programas_cv/detalles/${idProducto}/`,
      type: "DELETE",
      success: function (response) {
        if (response.status === "success") {
          // No mostrar alert si es exitoso, solo recargar la tabla.
          console.log("Producto eliminado correctamente.");
          const programaId = $(
            "#modalDetalleProductos_sweet_globe_plantines"
          ).attr("data-programa-id");
          obtenerProductosPrograma(programaId);
        } else {
          // Mostrar alert solo si hay error
          alert(
            "Error al eliminar el producto: " +
              (response.message || "Ocurrió un error.")
          );
        }
        window.isDeleting = false; // Desbloquear
      },
      error: function (xhr, status, error) {
        let errorMessage =
          "Ocurrió un error al eliminar el producto. Intente nuevamente.";
        try {
          const responseError = JSON.parse(xhr.responseText);
          if (responseError && responseError.message) {
            errorMessage = responseError.message;
          }
        } catch (e) {
          console.error("Error al parsear respuesta de error:", e);
        }
        // Mostrar alert solo si hay error
        alert("Error en la solicitud: " + errorMessage);
        console.error("Error al eliminar producto:", error);
        window.isDeleting = false; // Desbloquear
      },
    });
  } else {
    // El usuario canceló la eliminación
    console.log("Eliminación cancelada por el usuario.");
    window.isDeleting = false; // Desbloquear
  }
}

//#############################################################################
// SUBGRUPOS
//#############################################################################

/**
 * Inicializa el autocompletado para el campo de subgrupo
 */
function initAutocompletadoSubGrupo() {
  // Primero eliminar cualquier autocompletado existente para evitar duplicados
  removeAutocompletadoSubGrupo();

  // Obtener el campo de entrada de subgrupo
  const inputSubgrupo = $("#subGrupoProducto");

  // Convertir el select en un input text para autocompletado
  const valorActual = inputSubgrupo.val();

  // Crear un contenedor para el autocompletado
  const contenedorAutocompletado = $("<div>").addClass(
    "autocomplete-container position-relative"
  );
  inputSubgrupo.wrap(contenedorAutocompletado);

  // Ocultar el select original (lo mantenemos para compatibilidad)
  inputSubgrupo.hide();

  // Crear el input de autocompletado
  const inputAutocompletado = $("<input>")
    .attr("type", "text")
    .attr("id", "subGrupoProductoAuto")
    .addClass("form-control")
    .attr("placeholder", "Escriba para buscar un subgrupo...")
    .val(valorActual);

  // Agregar el input antes del select
  inputSubgrupo.before(inputAutocompletado);

  // Crear el contenedor de sugerencias
  const contenedorSugerencias = $("<div>")
    .addClass("autocomplete-suggestions")
    .attr("id", "sugerenciasSubgrupo")
    .css({
      position: "absolute",
      width: "100%",
      maxHeight: "200px",
      overflowY: "auto",
      zIndex: 1050,
      border: "1px solid #ced4da",
      borderTop: "none",
      borderRadius: "0 0 0.25rem 0.25rem",
      backgroundColor: "white",
      display: "none",
    });

  // Agregar el contenedor después del input
  inputAutocompletado.after(contenedorSugerencias);

  // Cargar los subgrupos desde la API
  $.ajax({
    url: "/aplicaciones/subgrupos/",
    type: "GET",
    success: function (response) {
      let subgrupos = [];
      let subgruposMap = {};

      // Procesar datos recibidos
      if (response.data && response.data.length > 0) {
        subgrupos = response.data.map((item) => ({
          id: item.IDSUBGRUPO,
          descripcion: item.DESCRIPCION,
        }));

        // Crear mapeo de descripción a ID
        response.data.forEach(function (subgrupo) {
          subgruposMap[subgrupo.DESCRIPCION] = subgrupo.IDSUBGRUPO;
        });
      } else {
        // Usar valores predeterminados si no hay datos
        const subgruposDefault = [
          { DESCRIPCION: "INSECTICIDA", IDSUBGRUPO: "001" },
          { DESCRIPCION: "FUNGICIDA", IDSUBGRUPO: "002" },
          { DESCRIPCION: "ADHERENTE", IDSUBGRUPO: "003" },
          { DESCRIPCION: "MISCELANEOS", IDSUBGRUPO: "004" },
          { DESCRIPCION: "FOLIARES", IDSUBGRUPO: "005" },
        ];

        subgrupos = subgruposDefault.map((item) => ({
          id: item.IDSUBGRUPO,
          descripcion: item.DESCRIPCION,
        }));

        // Crear mapeo de descripción a ID
        subgruposDefault.forEach(function (subgrupo) {
          subgruposMap[subgrupo.DESCRIPCION] = subgrupo.IDSUBGRUPO;
        });
      }

      // Guardar el mapeo de subgrupos para uso posterior
      inputSubgrupo.data("subgrupos-map", subgruposMap);
      inputSubgrupo.data("subgrupos-lista", subgrupos);

      // Eventos para el autocompletado
      inputAutocompletado.off("input").on("input", function () {
        const valor = $(this).val().toLowerCase();

        // Si hay valor, mostrar sugerencias filtradas
        if (valor) {
          // Filtrar subgrupos
          const sugerenciasFiltradas = subgrupos.filter((item) =>
            item.descripcion.toLowerCase().includes(valor)
          );

          // Mostrar sugerencias
          mostrarSugerencias(sugerenciasFiltradas);
        } else {
          // Si no hay valor, ocultar sugerencias
          contenedorSugerencias.empty().hide();
        }
      });

      // Si ya hay un valor, replicarlo al autocompletado
      if (valorActual) {
        inputAutocompletado.val(valorActual);
        // Habilitar botón de búsqueda
        $("#btnBuscarProducto").prop("disabled", false);
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al cargar subgrupos para autocompletado:", error);

      // En caso de error, usar valores predeterminados
      const subgruposDefault = [
        { DESCRIPCION: "INSECTICIDA", IDSUBGRUPO: "001" },
        { DESCRIPCION: "FUNGICIDA", IDSUBGRUPO: "002" },
        { DESCRIPCION: "ADHERENTE", IDSUBGRUPO: "003" },
        { DESCRIPCION: "MISCELANEOS", IDSUBGRUPO: "004" },
        { DESCRIPCION: "FOLIARES", IDSUBGRUPO: "005" },
      ];

      let subgruposMap = {};
      const subgrupos = subgruposDefault.map((item) => ({
        id: item.IDSUBGRUPO,
        descripcion: item.DESCRIPCION,
      }));

      subgruposDefault.forEach(function (subgrupo) {
        subgruposMap[subgrupo.DESCRIPCION] = subgrupo.IDSUBGRUPO;
      });

      // Guardar el mapeo
      inputSubgrupo.data("subgrupos-map", subgruposMap);
      inputSubgrupo.data("subgrupos-lista", subgrupos);
    },
  });
}

/**
 * Elimina el autocompletado existente para evitar duplicados
 */
function removeAutocompletadoSubGrupo() {
  // Primero verificamos si ya existe el autocompletado
  if ($("#subGrupoProductoAuto").length) {
    // Mostrar el select original
    $("#subGrupoProducto").show();

    // Si el select está dentro de un contenedor de autocompletado, desenvolverlo
    if ($("#subGrupoProducto").parent().hasClass("autocomplete-container")) {
      $("#subGrupoProducto").unwrap();
    }

    // Eliminar el input de autocompletado y las sugerencias
    $("#subGrupoProductoAuto").remove();
    $("#sugerenciasSubgrupo").remove();
  }
}

/**
 * Carga los subgrupos desde la API para autocompletado
 */
function cargarSubgrupos() {
  // Inicializar el autocompletado
  initAutocompletadoSubGrupo();

  // Ocultar sugerencias al hacer clic fuera del campo
  $(document)
    .off("click.subgrupo")
    .on("click.subgrupo", function (e) {
      if (!$(e.target).closest(".autocomplete-container").length) {
        $("#sugerenciasSubgrupo").hide();
      }
    });
}

/**
 * Muestra las sugerencias del autocompletado
 * @param {Array} sugerencias - Lista de sugerencias filtradas
 */
function mostrarSugerencias(sugerencias) {
  const contenedorSugerencias = $("#sugerenciasSubgrupo");
  contenedorSugerencias.empty();

  if (sugerencias.length > 0) {
    sugerencias.forEach((item) => {
      const sugerencia = $("<div>")
        .addClass("autocomplete-suggestion p-2 hover-bg-light cursor-pointer")
        .text(item.descripcion)
        .data("id", item.id)
        .css({
          cursor: "pointer",
        })
        .hover(
          function () {
            $(this).addClass("bg-light");
          },
          function () {
            $(this).removeClass("bg-light");
          }
        )
        .on("click", function () {
          // Al hacer clic, establecer el valor y ocultar sugerencias
          $("#subGrupoProductoAuto").val(item.descripcion);
          $("#subGrupoProducto").val(item.descripcion);
          contenedorSugerencias.hide();
        });

      contenedorSugerencias.append(sugerencia);
    });

    contenedorSugerencias.show();
  } else {
    contenedorSugerencias.hide();
  }
}

// Implementar la función para buscar productos
function buscarProductos() {
  // Obtener el nombre del producto o dejarlo vacío si no hay valor
  const nombreProducto = $("#nombreProducto").val() || "";

  // Obtener el subgrupo seleccionado (del campo de autocompletado)
  const subgrupoSeleccionado = $("#subGrupoProductoAuto").val();

  // Si no hay subgrupo seleccionado, no continuar
  if (!subgrupoSeleccionado) {
    Swal.fire({
      icon: "warning",
      title: "Seleccione un subgrupo",
      text: "Debe seleccionar un subgrupo antes de buscar productos.",
    });
    return;
  }

  // Obtener el mapeo de subgrupos y buscar el ID del subgrupo
  const subgruposMap = $("#subGrupoProducto").data("subgrupos-map") || {};
  const idSubgrupo = subgruposMap[subgrupoSeleccionado] || "009"; // Valor por defecto

  // Mostrar indicador de carga
  Swal.fire({
    title: "Buscando productos...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Realizar petición AJAX para buscar productos
  $.ajax({
    url: "/aplicaciones/productos/",
    type: "GET",
    data: {
      descripcion: nombreProducto,
      idgrupo: 2400, // Valor fijo según requerimiento
      idsubgrupo: idSubgrupo,
    },
    success: function (response) {
      Swal.close();

      // Verificar si hay datos en la respuesta
      if (response && response.data && response.data.length > 0) {
        // Si hay productos, mostrar modal con los resultados
        mostrarResultadosProductos(response.data);
      } else {
        // Si no hay productos, mostrar mensaje
        Swal.fire({
          icon: "info",
          title: "Sin resultados",
          text: "No se encontraron productos con los criterios especificados.",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.close();
      console.error("Error al buscar productos:", error);
      Swal.fire({
        icon: "error",
        title: "Error en la búsqueda",
        text: "Ocurrió un error al buscar productos. Intente nuevamente.",
      });
    },
  });
}

// Función para mostrar resultados en un modal con diseño moderno y responsive
function mostrarResultadosProductos(productos) {
  // Si solo hay un producto, seleccionarlo automáticamente
  if (productos.length === 1) {
    seleccionarProducto(productos[0]);
    return;
  }

  // Crear tarjetas para cada producto con diseño moderno
  let contenidoHTML = `
    <div class="mb-3">
      <div class="input-group input-group-sm mb-2">
        <div class="input-group-prepend">
          <span class="input-group-text bg-primary text-white">
            <i class="fas fa-filter"></i>
          </span>
        </div>
        <input type="text" id="filtroProductos" class="form-control" placeholder="Filtrar productos...">
      </div>
    </div>
    <div class="productos-grid">
  `;

  productos.forEach((producto, index) => {
    // Limpiar espacios en los campos
    const idProducto = producto.IDPRODUCTO ? producto.IDPRODUCTO.trim() : "";
    const descripcion = producto.DESCRIPCION ? producto.DESCRIPCION.trim() : "";
    const materiaActiva = producto.MATERIA_ACTIVA
      ? producto.MATERIA_ACTIVA.trim()
      : "-";
    const idMedida = producto.IDMEDIDA ? producto.IDMEDIDA.trim() : "-";
    const ultimoPrecio = producto.ultimo_precio
      ? parseFloat(producto.ultimo_precio).toFixed(2)
      : "0.00";

    contenidoHTML += `
      <div class="producto-card" data-index="${index}">
        <div class="producto-header">
          <span class="badge badge-primary">${idProducto}</span>
        </div>
        <div class="producto-body">
          <h6 class="producto-titulo">${descripcion}</h6>
          <p class="producto-materia"><span>Materia activa:</span> ${materiaActiva}</p>
          <p class="producto-info"><span>Unidad:</span> ${idMedida}</p>
          <p class="producto-precio"><span>Precio USD:</span> $${ultimoPrecio}</p>
        </div>
        <div class="producto-footer">
          <button class="btn btn-primary btn-block btn-sm btn-seleccionar-producto" data-index="${index}">
            <i class="fas fa-check mr-1"></i> Seleccionar
          </button>
        </div>
      </div>
    `;
  });

  contenidoHTML += `
    </div>
    <div class="text-muted small mt-2 text-right">Total: ${productos.length} productos</div>
  `;

  // CSS personalizado para el diseño de tarjetas
  const customStyles = `
    <style>
      .productos-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 12px;
        max-height: 350px;
        overflow-y: auto;
        padding-right: 5px;
      }
      
      .producto-card {
        display: flex;
        flex-direction: column;
        border: 1px solid rgba(0,0,0,.125);
        border-radius: 4px;
        transition: all 0.2s ease;
        background-color: #fff;
        height: 100%;
      }
      
      .producto-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,.1);
        border-color: #3490dc;
      }
      
      .producto-header {
        padding: 8px 12px;
        background-color: #f8f9fa;
        border-bottom: 1px solid rgba(0,0,0,.125);
      }
      
      .producto-body {
        padding: 12px;
        flex-grow: 1;
      }
      
      .producto-footer {
        padding: 8px 12px;
        border-top: 1px solid rgba(0,0,0,.125);
      }
      
      .producto-titulo {
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 6px;
        color: #2d3748;
        line-height: 1.3;
      }
      
      .producto-materia, .producto-info, .producto-precio {
        font-size: 0.75rem;
        margin-bottom: 4px;
        color: #718096;
      }
      
      .producto-materia span, .producto-info span, .producto-precio span {
        font-weight: 600;
        color: #4a5568;
      }
      
      .producto-precio {
        color: #2d3748;
        font-weight: 500;
      }
      
      /* Estilo para la barra de desplazamiento */
      .productos-grid::-webkit-scrollbar {
        width: 6px;
      }
      
      .productos-grid::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
      }
      
      .productos-grid::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 10px;
      }
      
      .productos-grid::-webkit-scrollbar-thumb:hover {
        background: #999;
      }
      
      /* Estilo para el filtro */
      #filtroProductos:focus {
        box-shadow: none;
        border-color: #3490dc;
      }
    </style>
  `;

  // Mostrar modal con resultados y estilo mejorado
  Swal.fire({
    title:
      '<span style="font-size: 1.1rem;"><i class="fas fa-layer-group mr-2 text-primary"></i>Seleccione un producto</span>',
    html: customStyles + contenidoHTML,
    width: "auto",
    padding: "1rem",
    showCloseButton: true,
    showConfirmButton: false,
    customClass: {
      container: "swal-modern-container",
      popup: "swal-modern-popup",
    },
    didOpen: () => {
      // Aplicar estilos adicionales al contenedor del modal
      $(".swal2-popup").css({
        "max-width": "800px",
        width: "95%",
        "font-size": "0.9rem",
        "border-radius": "8px",
      });

      // Implementar funcionalidad de filtrado
      $("#filtroProductos").on("input", function () {
        const filtro = $(this).val().toLowerCase();
        $(".producto-card").each(function () {
          const index = $(this).data("index");
          const producto = productos[index];
          const descripcion = producto.DESCRIPCION
            ? producto.DESCRIPCION.toLowerCase()
            : "";
          const materiaActiva = producto.MATERIA_ACTIVA
            ? producto.MATERIA_ACTIVA.toLowerCase()
            : "";
          const idProducto = producto.IDPRODUCTO
            ? producto.IDPRODUCTO.toLowerCase()
            : "";

          const coincide =
            descripcion.includes(filtro) ||
            materiaActiva.includes(filtro) ||
            idProducto.includes(filtro);

          $(this).toggle(coincide);
        });
      });

      // Asignar evento click a los botones de seleccionar
      $(".btn-seleccionar-producto").on("click", function () {
        const index = $(this).data("index");
        seleccionarProducto(productos[index]);
        Swal.close();
      });

      // Hacer que toda la tarjeta sea clickeable
      $(".producto-card").on("click", function (e) {
        // Si se hizo clic en la tarjeta pero no en el botón directamente
        if (
          !$(e.target).hasClass("btn-seleccionar-producto") &&
          !$(e.target).parent().hasClass("btn-seleccionar-producto")
        ) {
          const index = $(this).data("index");
          seleccionarProducto(productos[index]);
          Swal.close();
        }
      });
    },
  });
}

// Ya existe una implementación de esta función al inicio del archivo

// ############################################################################
// Editar producto
// ############################################################################

/**
 * Abre el modal para editar un producto existente y carga sus datos
 * @param {number} idProducto - ID del producto a editar
 */
function editarProducto(idProducto) {
  if (!idProducto) return;

  // Mostrar indicador de carga
  Swal.fire({
    title: "Cargando datos...",
    text: "Por favor espere",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Obtener datos del producto
  $.ajax({
    url: `/aplicaciones/programas_cv/detalles/${idProducto}/`,
    type: "GET",
    success: function (response) {
      Swal.close();

      if (response.status === "success" && response.data) {
        // Llenar el formulario con los datos del producto
        prepararFormularioEdicionProducto(idProducto, response.data);
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudo cargar la información del producto",
        });
      }
    },
    error: function (xhr, status, error) {
      Swal.close();
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al cargar los datos del producto. Intente nuevamente.",
      });
      console.error("Error al cargar producto:", error);
    },
  });
}

/**
 * Prepara el formulario para editar un producto existente
 * @param {number} idProducto - ID del producto que se está editando
 * @param {Object} datos - Datos del producto a editar
 */
function prepararFormularioEdicionProducto(idProducto, datos) {
  // Resetear formulario antes de cargar los datos
  resetearFormularioProducto();

  // Configurar el formulario en modo edición
  $("#formProducto").attr("data-id", idProducto);
  $("#productoId").val(idProducto);
  $("#programaId").val(datos.IDPROGRAMAAAPL);

  // Guardar el IDPRODUCTO en el campo oculto para la API
  $("#idProductoAPI").val(datos.IDPRODUCTO || "");

  // Llenar los campos con los datos del producto
  $("#diaProducto").val(datos.DIA);
  $("#subGrupoProducto").val(datos.SUBGRUPO);
  $("#objetivoProducto").val(datos.OBJETIVO);
  $("#nombreProducto").val(datos.PRODUCTO);
  $("#materiaActivaProducto").val(datos.MATERIA_ACTIVA);
  $("#dosisProducto").val(datos.DOSIS);
  $("#unidadProducto").val(datos.UND);
  $("#mojamientoProducto").val(datos.MOJAMIENTO);
  $("#necesidadProducto").val(datos.NECESIDAD_HA);
  $("#unidadNecesidadProducto").val(datos.UND2);
  $("#precioProducto").val(datos.PRECIO);
  $("#precioHaProducto").val(datos.PRECIO_HA);
  $("#observacionesProducto").val(datos.OBSERVACIONES);

  // Si hay campos adicionales, también cargarlos
  if (datos.TRATAMIENTO) {
    $("#tratamientoProducto").val(datos.TRATAMIENTO);
  }

  if (datos.FECHA_INTERVALO) {
    // Convertir fecha al formato adecuado para input type="date"
    const fecha = moment(datos.FECHA_INTERVALO).format("YYYY-MM-DD");
    $("#fechaIntervaloProducto").val(fecha);
  }

  // Cambiar el título del modal y el texto del botón
  $("#modalProductoLabel").html(
    '<i class="fas fa-edit mr-2"></i> Editar Producto'
  );
  $("#btnGuardarProducto")
    .html('<i class="fas fa-save mr-1"></i> Actualizar Producto')
    .removeClass("btn-primary")
    .addClass("btn-success");

  // Mostrar el modal
  $("#modalProducto").modal("show");
}

// ############################################################################
// API OBJETIVOS
// ############################################################################

/**
 * Inicializa el autocompletado para el campo de objetivo
 * Permite buscar objetivos mientras el usuario escribe
 */

function initAutocompletadoObjetivo() {
  $("#objetivoProducto")
    .autocomplete({
      source: function (request, response) {
        // Mostrar indicador de carga
        $("#objetivoProducto").addClass("loading");

        // Llamada AJAX al endpoint de búsqueda de objetivos
        $.ajax({
          url: "/aplicaciones/api/objetivos-apl/",
          dataType: "json",
          data: {
            term: request.term,
          },
          success: function (data) {
            // Quitar indicador de carga
            $("#objetivoProducto").removeClass("loading");

            // Mostrar resultados en el dropdown
            response(data);
          },
          error: function (xhr, status, error) {
            // En caso de error, quitar indicador de carga
            $("#objetivoProducto").removeClass("loading");
            console.error("Error al buscar objetivos:", error);

            // Mostrar un array vacío como respuesta para no romper el autocompletado
            response([]);
          },
        });
      },
      minLength: 2, // Comenzar a buscar después de 2 caracteres
      delay: 300, // Esperar 300ms después de la última tecla presionada
      select: function (event, ui) {
        // Cuando se selecciona un elemento
        $("#objetivoProducto").val(ui.item.value);
        return false;
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    // Personalizar la apariencia de los elementos en el dropdown
    return $("<li>")
      .append("<div class='autocomplete-item'>" + item.label + "</div>")
      .appendTo(ul);
  };
}

/**
 * Agregar estilos CSS para el indicador de carga y los elementos del autocompletado
 */

function agregarEstilosAutocompletado() {
  // Verificar si los estilos ya existen
  if ($("#estilos-autocompletado").length === 0) {
    $("head").append(`
          <style id="estilos-autocompletado">
              .ui-autocomplete {
                  max-height: 200px;
                  overflow-y: auto;
                  overflow-x: hidden;
                  z-index: 9999 !important;
              }
              .ui-autocomplete .ui-menu-item {
                  padding: 5px;
              }
              .autocomplete-item {
                  padding: 6px 10px;
                  cursor: pointer;
              }
              .ui-autocomplete .ui-menu-item:hover {
                  background-color: #f8f9fa;
              }
              input.loading {
                  background-image: url('/static/core/img/loading.gif');
                  background-size: 20px 20px;
                  background-position: right center;
                  background-repeat: no-repeat;
                  padding-right: 30px;
              }
          </style>
      `);
  }
}

/**
 * Modificar la función existente de initEventosFormularioProducto
 * para incluir el autocompletado del objetivo
 */
function initEventosFormularioProducto() {
  // Eventos para cálculos automáticos
  $("#dosisProducto, #mojamientoProducto").on("input", calcularNecesidadHa);
  $("#precioProducto").on("input", calcularPrecioHa);
  $("#unidadProducto").on("change", function () {
    $("#unidadNecesidadProducto").val($(this).val());
    calcularNecesidadHa();
  });

  // Agregar inicialización del autocompletado para objetivo
  agregarEstilosAutocompletado();
  initAutocompletadoObjetivo();

  // Inicializar el autocompletado para productos
  initAutocompletadoProducto();
}

/**
 * Asegurarse de que al abrir el modal, se inicialice el autocompletado
 */
function abrirModalNuevoProducto(idPrograma) {
  // Código existente
  $("#modalProducto").modal("show");
  $("#modalProductoLabel").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar Producto al Programa'
  );
  resetearFormularioProducto();
  $("#programaId").val(idPrograma);

  // Asegurarnos de que los eventos se inicialicen correctamente
  initEventosFormularioProducto();
}

//#############################################################################
// EVENTOS
//#############################################################################

// BOTON CERRAR MODAL SWEET GLOBE
$('[data-click="panel-remove-generales"]').click(function (e) {
  e.stopPropagation();
  $("#modalSweetGlobe").modal("hide");
  $("#modalShineMuscat").modal("hide");
  $("#modalMoscatel").modal("hide");
  $("#modalAutumnCrisp").modal("hide");
});

// BOTON CERRAR MODAL CREAR PROGRAMA
$('[data-click="panel-remove-crear-programa"]').click(function (e) {
  e.stopPropagation();
  $("#modalCrearPrograma").modal("hide");
});

// BOTON CERRAR MODAL CREAR PROGRAMA PRODUCCIÓN
$('[data-click="panel-remove-crear-programa-produccion"]').click(function (e) {
  e.stopPropagation();
  $("#modalCrearProgramaProduccion").modal("hide");
});

// BOTON CERRAR MODAL DETALLE PRODUCTOS
$('[data-click="panel-remove-detalle-productos"]').click(function (e) {
  e.stopPropagation();
  $("#modalDetalleProductos_sweet_globe_plantines").modal("hide");
});

/**
 * Función para obtener datos adicionales del producto desde la API APL_APIPRODUCTOS
 * @param {string} idProducto - ID del producto a consultar
 * @returns {Promise} - Promesa que resuelve con los datos del producto
 */
function obtenerDatosProductoApl(idProducto) {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/aplicaciones/aplproductos/",
      type: "GET",
      data: {
        idproducto: idProducto,
      },
      success: function (response) {
        if (
          response.status === "success" &&
          response.data &&
          response.data.length > 0
        ) {
          resolve(response.data[0]);
        } else {
          resolve(null); // No se encontraron datos
        }
      },
      error: function (xhr, status, error) {
        console.error(
          "Error al obtener datos adicionales del producto:",
          error
        );
        reject(error);
      },
    });
  });
}
