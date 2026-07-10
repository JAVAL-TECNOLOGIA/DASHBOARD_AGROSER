



// Variable global para productos seleccionados
let productosSeleccionados = [];

// Variable global para guardar datos COMPLETOS de los productos seleccionados
let productosSeleccionadosCompletos = [];

// Variable global para almacenar TODOS los datos de productos del requerimiento actual
let datosProductosCompletosAPI = [];

// Variable global para guardar datos del requerimiento seleccionado
let datosRequerimientoSeleccionado = null;

// Actualizar el evento de inicialización de la pestaña
$(document).ready(function () {
  // Guardar la referencia de la tabla en la variable global
  window.tablaSalidasInternas = AJSiniciarTablaSalInternos();
  AJSconfigurarFiltrosSalidas();

  // MODAL PARA BUSCAR REQUERIMIENTO
  $("#btn-abrir-buscador-req").on("click", function () {
    AJSabrirModalBuscarRequerimiento();
  });

  // Botón seleccionar requerimiento
  $("#AJSbtn-seleccionar-requerimiento").on("click", function () {
    const productosSeleccionadosActuales = AJSobtenerProductosSeleccionados();

    // PASO 2: Validar que hay datos del requerimiento guardados y productos seleccionados
    if (
      datosRequerimientoSeleccionado &&
      productosSeleccionadosActuales.length > 0
    ) {
      console.log("✅ Requerimiento confirmado para usar:");
      console.log("   📋 IDREQINTERNO:", datosRequerimientoSeleccionado.id);
      console.log("   📋 Datos guardados:", datosRequerimientoSeleccionado);
      console.log(
        "   📦 Productos seleccionados:",
        productosSeleccionadosActuales.length
      );

      // PASO 3: Rellenar automáticamente el componente Doc.Referencia
      AJSrellenarDocumentoReferencia(datosRequerimientoSeleccionado);

      // Transferir productos a la tabla del modal de nueva salida
      // ✅ USAR DATOS COMPLETOS en lugar de datos básicos
      AJStransferirProductosAModalSalida(
        productosSeleccionadosCompletos, // Datos completos de la API
        datosRequerimientoSeleccionado
      );

      // Cerrar el modal
      $("#AJSmodalBuscarRequerimiento").modal("hide");

      // Mostrar confirmación
      if (typeof toastr !== "undefined") {
        toastr.success(
          `${productosSeleccionadosCompletos.length} productos transferidos del requerimiento ${datosRequerimientoSeleccionado.numero}`,
          "Productos Transferidos"
        );
      }
    } else if (!datosRequerimientoSeleccionado) {
      console.warn("No hay requerimiento seleccionado");

      if (typeof toastr !== "undefined") {
        toastr.warning(
          "Por favor selecciona un requerimiento de la lista",
          "Sin Selección"
        );
      } else {
        alert("Por favor selecciona un requerimiento de la lista");
      }
    } else if (productosSeleccionadosCompletos.length === 0) {
      console.warn("No hay productos seleccionados");

      if (typeof toastr !== "undefined") {
        toastr.warning(
          "Por favor selecciona al menos un producto",
          "Sin Productos"
        );
      } else {
        alert("Por favor selecciona al menos un producto");
      }
    }
  });

  // Limpiar modal de búsqueda al cerrarse
  $("#AJSmodalBuscarRequerimiento").on("hidden.bs.modal", function () {
    AJSlimpiarModalDocumentosReferencia();
    documentoSeleccionadoActual = null;
  });

  // Botón cerrar modal
  $("#AJSbtn-cerrar-modal-salida").on("click", function () {
    $("#AJSmodalDetallesSalidaInterna").modal("hide");
  });

  // Limpiar modal al cerrarse
  $("#AJSmodalDetallesSalidaInterna").on("hidden.bs.modal", function () {
    // Limpiar todos los campos
    $("#AJSsalida-id-documento").text("-");
    $("#AJSsalida-id-documento").text("-");
    $("#AJSsalida-fecha-documento").text("-");
    $("#AJSsalida-estado-documento").text("-");
    $("#AJSsalida-empresa").val("");
    $("#AJSsalida-sucursal").val("");
    $("#AJSsalida-almacen-origen").val("");
    $("#AJSsalida-almacen-destino").val("");
    $("#AJSsalida-responsable").val("");
    $("#AJSsalida-motivo").val("");
    $("#AJSsalida-proyecto").val("");
    $("#AJSsalida-observaciones").val("");

    // Limpiar tabla de productos
    $("#AJStbody-productos-salida").html(`
      <tr>
        <td colspan="10" class="text-center text-muted py-4">
          <i class="fas fa-box-open fa-2x mb-2 d-block"></i>
          No hay productos para mostrar
        </td>
      </tr>
    `);

    // Limpiar totales
    $("#AJStotal-productos").text("-");
    $("#AJStotal-peso").text("-");
    $("#AJStotal-importe").text("-");

    console.log("Modal de detalles limpiado");
  });

  // Botón buscar documento
  $("#AJSbtn-buscar-documento").on("click", function () {
    console.log("🔍 Aplicando filtros...");
    AJSmostrarRequerimientos();
  });

  // Enter en el campo de búsqueda
  $("#AJSfiltro-numero-doc").on("keypress", function (e) {
    if (e.which === 13) {
      // Enter key
      console.log("🔍 Búsqueda con Enter...");
      AJSmostrarRequerimientos();
    }
  });

  // Cambios en filtros de estado y fechas
  $("#AJSfiltro-estado-doc, #AJSfiltro-fecha-desde, #AJSfiltro-fecha-hasta").on(
    "change",
    function () {
      console.log("🔍 Filtro cambiado, actualizando...");
      AJSmostrarRequerimientos();
    }
  );

  // Limpiar modal al cerrarse
  $("#AJSmodalBuscarRequerimiento").on("hidden.bs.modal", function () {
    console.log("🧹 Limpiando modal...");
    AJSlimpiarModalDocumentosReferencia();
    AJSlimpiarSeleccionProductos();
    // Limpiar datos del requerimiento guardados
    datosRequerimientoSeleccionado = null;
    documentoSeleccionadoActual = null;
  });

  // Manejar selección de checkbox de documentos (DELEGADO)
  $(document).on("change", ".chk-documento", function () {
    AJSmanejarSeleccionDocumento(this);
  });

  // Manejar selección de todos los documentos
  $("#AJSchk-seleccionar-todos").on("change", function () {
    AJSmanejarSeleccionTodos(this);
  });

  // Manejar selección de productos individuales (DELEGADO)
  $(document).on("change", ".chk-producto", function () {
    AJSmanejarSeleccionProducto(this);
  });

  // Manejar selección de todos los productos
  $("#AJSselectAllProductos").on("change", function () {
    AJSmanejarSeleccionTodosProductos(this);
  });

  // Limpiar tabla de productos seleccionados al cerrar modal de nueva salida
  $("#AJSmodalNuevaSalida").on("hidden.bs.modal", function () {
    AJSlimpiarTablaProductosSeleccionados();
  });

  // Inicializar campos del formulario con valores por defecto
  AJSinicializarFormularioSalida();

  // Inicializar búsqueda de responsables
  AJSinicializarBusquedaResponsables();

  // Crear función global para guardar TODOS los datos (llamada desde onclick en HTML)
  window.guardarEncabezado = function () {
    console.log("💾 ===== INICIANDO GUARDADO =====");

    // Llamar a la función específica de guardado
    AJSguardarSalidaInterna();
  };

  // Manejar clic en botón de procesar salida (DELEGADO)
  $(document).on("click", ".btn-procesar-salida", function (e) {
    e.stopPropagation(); // Evitar que se active el evento de clic de la fila

    const idIngresosAlidaAlm = $(this).data("id");
    const serie = $(this).data("serie");
    const numero = $(this).data("numero");

    console.log("🔄 Procesamiento manual solicitado para:", idIngresosAlidaAlm);

    // Confirmar antes de procesar
    Swal.fire({
      title: "¿Procesar Documento?",
      html: `
        <p>¿Desea contabilizar y centralizar el documento?</p>
        <p><strong>ID:</strong> ${idIngresosAlidaAlm}</p>
        <p><strong>Documento:</strong> ${serie}-${numero}</p>
      `,
      icon: "question",
      showCancelButton: true,
      confirmButtonColor: "#28a745",
      cancelButtonColor: "#6c757d",
      confirmButtonText: "Sí, Procesar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        // Simular datos del documento para el procesamiento
        const datosDocumento = {
          idingresosalidaalm: idIngresosAlidaAlm,
          serie: serie,
          numero: numero,
        };

        // Mostrar loading
        Swal.fire({
          title: "Procesando...",
          html: `
            <div class="text-center">
              <p>🔄 Contabilizando y centralizando documento...</p>
              <p><strong>${serie}-${numero}</strong></p>
              <div class="spinner-border text-primary mt-2" role="status">
                <span class="sr-only">Procesando...</span>
              </div>
            </div>
          `,
          allowOutsideClick: false,
          showConfirmButton: false,
        });

        // Procesar documento
        AJSprocesarContabilizacionYCentralizacion(
          idIngresosAlidaAlm,
          datosDocumento
        );
      }
    });
  });

  // Evento para actualizar el tipo de cambio al cambiar la fecha
  // Usar delegación de eventos para asegurar que funcione con modales
  $(document).on("change", "#encab-fecha", function () {
    const fecha = $(this).val();
    console.log("🔄 Cambio de fecha detectado:", fecha);
    if (fecha) {
      AJSobtenerTipoCambioPorFecha(fecha);
    } else {
      $("#AJSencab-tcambio").val("");
    }
  });

  // Evento cuando se abre el modal para cargar tipo de cambio si hay fecha
  $(document).on("shown.bs.modal", "#AJSmodalNuevaSalida", function () {
    console.log("📂 Modal Nueva Salida abierto");
    const fechaActual = $("#encab-fecha").val();
    if (fechaActual) {
      console.log("🔄 Cargando tipo de cambio para fecha existente:", fechaActual);
      AJSobtenerTipoCambioPorFecha(fechaActual);
    }
  });




  $("#AJSbtn-imprimir").on("click", function () {
    const id_salida = $(this).data("id");
    AJSCrearPdfSalidaInterna(id_salida);
  });

});
//================================================================================================================
// INICIALIZAR LA TABLA DE SALIDAS INTERNAS RESUMEN
//================================================================================================================

function AJSiniciarTablaSalInternos() {
  const tabla = new DataTable("#AJStablaSalidasInternas", {
    responsive: true,
    autoWidth: false,
    pageLength: 25,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },

    ajax: {
      url: "/almacen/salida-interna-ajs/",
      type: "GET",
      data: function (d) {
        // Agregar filtros a la petición
        d.idempresa = "001"; // O tomar de algún selector

        // Filtros de fecha
        const fechaDesde = $("#AJSdesde_salidas").val();
        const fechaHasta = $("#AJShasta_salidas").val();

        if (fechaDesde) {
          d.fecha_desde = fechaDesde;
        }
        if (fechaHasta) {
          d.fecha_hasta = fechaHasta;
        }

        // Filtro de estado
        const estado = $("#estado_salidas").val();
        if (estado && estado !== "todos") {
          // Mapear valores del select a códigos de estado
          const mapaEstados = {
            confirmado: "CO",
            pendiente: "PE",
            anulado: "AN",
            cerrado: "CE",
            aprobado: "AP",
          };
          d.idestado = mapaEstados[estado] || estado;
        }

        // Filtro de tipo de movimiento/motivo
        const tipoMovimiento = $("#AJStipo_movimiento").val();
        if (tipoMovimiento && tipoMovimiento !== "todos") {
          // Mapear valores del select a códigos de motivo
          const mapaMotivos = {
            salida_consumo: "CON",
            transferencia: "TRA",
            devolucion: "DEV",
            ajuste: "AJU",
            merma: "MER",
          };
          d.idmotivo = mapaMotivos[tipoMovimiento] || tipoMovimiento;
        }

        console.log("Filtros enviados:", d);
      },
      dataSrc: function (json) {
        console.log("Datos recibidos:", json);

        if (json.success) {
          //console.log(`Total de registros: ${json.total}`);
          console.log(`Total de registros: ${json.data.length}`);
          return json.data;
        } else {
          console.error("Error en la respuesta:", json.message);
          return [];
        }
      },
      error: function (xhr, error, thrown) {
        console.error("Error en la petición AJAX:", error);
        alert("Error al cargar los datos: " + error);
      },
    },
    columns: [
      {
        data: "idingresosalidaalm",
        title: "ID",
        visible: false,
      },
      {
        data: "fecha",
        title: "Fecha",
        render: function (data, type, row) {
          if (data && data !== null) {
            // Formatear fecha YYYY-MM-DD HH:MM:SS a DD/MM/YYYY
            const fecha = new Date(data);
            return fecha.toLocaleDateString("es-ES");
          }
          return "";
        },
        className: "text-center",
      },
      {
        data: null,
        title: "Documento",
        render: function (data, type, row) {
          // Combinar SERIE y NUMERO
          const serie = row.serie ? row.serie.trim() : "";
          const numero = row.numero ? row.numero.trim() : "";

          if (serie && numero) {
            return `${serie}-${numero}`;
          } else if (numero) {
            return numero;
          }
          return "";
        },
        className: "text-center",
      },
      {
        data: "idmotivo",
        title: "Motivo",
        render: function (data, type, row) {
          // Mapear códigos de motivo a descripciones
          const motivos = {
            CON: "Consumo",
            TRA: "Transferencia",
            DEV: "Devolución",
            AJU: "Ajuste",
            MER: "Merma",
          };
          return motivos[data] || data || "";
        },
      },
      {
        data: "idestado",
        title: "Estado",
        render: function (data, type, row) {
          // Mapear estados a descripciones y clases CSS
          const estados = {
            PE: { texto: "Pendiente", clase: "badge-warning" },
            CO: { texto: "Confirmado", clase: "badge-success" },
            AN: { texto: "Anulado", clase: "badge-danger" },
            CE: { texto: "Cerrado", clase: "badge-secondary" },
            AP: { texto: "Aprobado", clase: "badge-info" },
          };

          const estado = estados[data] || {
            texto: data || "",
            clase: "badge-light",
          };
          return `<span class="badge ${estado.clase}">${estado.texto}</span>`;
        },
        className: "text-center",
      },
      {
        data: "idresponsable",
        title: "Responsable",
        render: function (data, type, row) {
          return data ? data.trim() : "";
        },
      },
      {
        data: "idoperacion",
        title: "Tipo Movimiento",
        render: function (data, type, row) {
          // Mapear tipos de operación
          const operaciones = {
            SALM: "Salida Almacén",
            INGM: "Ingreso Almacén",
            TRAN: "Transferencia",
          };
          return operaciones[data] || data || "Salida Almacén";
        },
      },
      {
        data: "contabilizado",
        title: "Centralizado",
        render: function (data, type, row) {
          //if (data == 1 || data === true) {
          if (data == 1 || data === "1" || data === true){
            return '<span class="badge badge-success"><i class="fas fa-check"></i> Sí</span>';
          } else {
            return '<span class="badge badge-warning"><i class="fas fa-clock"></i> No</span>';
          }
        },
        className: "text-center",
      },
      {
        data: "glosa",
        title: "Observaciones",
        render: function (data, type, row) {
          if (data && data.length > 50) {
            return `<span title="${data}">${data.substring(0, 50)}...</span>`;
          }
          return data || "";
        },
      },
      {
        data: null,
        title: "Acciones",
        render: function (data, type, row) {
          // Solo mostrar botón de procesar si no está contabilizado
          if (row.contabilizado == 0 || row.contabilizado === false) {
            return `
              <button class="btn btn-sm btn-warning btn-procesar-salida" 
                      data-id="${row.idingresosalidaalm}"
                      data-serie="${row.serie || ""}"
                      data-numero="${row.numero || ""}"
                      title="Contabilizar y Centralizar">
                <i class="fas fa-cogs"></i> Procesar
              </button>
            `;
          } else {
            return `
              <span class="badge badge-success">
                <i class="fas fa-check"></i> Procesado
              </span>
            `;
          }
        },
        className: "text-center",
        orderable: false,
        width: "120px",
      },
    ],
    order: [[1, "desc"]], // Ordenar por fecha descendente
    rowCallback: function (row, data, index) {
      // Agregar clase CSS según el estado
      if (data.idestado === "AN") {
        $(row).addClass("table-danger");
      } else if (data.idestado === "CO") {
        $(row).addClass("table-success");
      }

      // Agregar cursor pointer para indicar que es clickeable
      $(row).addClass("cursor-pointer");

      // Agregar el evento de clic para abrir el modal de detalles
      $(row)
        .off("click")
        .on("click", function (e) {
          e.preventDefault();

          const idIngreso = data.idingresosalidaalm;
          console.log("IDINGRESOSALIDAALM obtenido:", idIngreso);
          console.log("Datos completos de la fila:", data);

          // Por ahora solo mostrar en consola y abrir el modal vacío
          AJSabrirModalDetallesSalida(idIngreso);
        });

      // Agregar tooltip con información básica
      $(row).attr(
        "title",
        `Click para ver detalles de: ${data.serie || ""}-${data.numero || ""}`
      );

      // Agregar efecto hover
      $(row).hover(
        function () {
          $(this).addClass("table-info");
        },
        function () {
          $(this).removeClass("table-info");
        }
      );
    },
    drawCallback: function (settings) {
      // Agregar información de filtros aplicados
      const api = this.api();
      const info = api.ajax.json();

      if (info && info.filtros_aplicados) {
        let filtrosTexto = "Filtros aplicados: ";
        const filtros = info.filtros_aplicados;

        if (filtros.fecha_desde)
          filtrosTexto += `Desde: ${filtros.fecha_desde} `;
        if (filtros.fecha_hasta)
          filtrosTexto += `Hasta: ${filtros.fecha_hasta} `;
        if (filtros.idestado) filtrosTexto += `Estado: ${filtros.idestado} `;
        if (filtros.idmotivo) filtrosTexto += `Motivo: ${filtros.idmotivo} `;

        console.log(filtrosTexto);
      }
    },
  });

  // Función para recargar la tabla
  window.recargarTablaSalidas = function () {
    tabla.ajax.reload();
  };

  return tabla;
}

// Función para manejar los botones de filtros
function AJSconfigurarFiltrosSalidas() {
  console.log("Configurando filtros de salidas internas...");

  // Botón actualizar salidas internas
  $("#AJSbtn-actualizar-salidas")
    .off("click")
    .on("click", function () {
      console.log("Actualizando tabla de salidas internas...");
      if (window.tablaSalidasInternas) {
        window.tablaSalidasInternas.ajax.reload();
        console.log("Tabla recargada exitosamente");
      } else {
        console.error("Tabla de salidas internas no encontrada");
      }
    });

  // Botón limpiar filtros salidas internas
  $("#AJSbtn-limpiar-salidas")
    .off("click")
    .on("click", function () {
      console.log("Limpiando filtros de salidas internas...");

      // Limpiar todos los filtros
      $("#estado_salidas").val("todos");
      $("#AJSarea_salidas").val("todos");
      $("#AJStipo_movimiento").val("todos");
      $("#AJSdesde_salidas").val("");
      $("#AJShasta_salidas").val("");

      // Recargar tabla después de limpiar
      if (window.tablaSalidasInternas) {
        window.tablaSalidasInternas.ajax.reload();
        console.log("Filtros limpiados y tabla recargada");
      } else {
        console.error("Tabla de salidas internas no encontrada");
      }
    });

  // Detectar cambios en los filtros y recargar automáticamente
  $("#estado_salidas, #AJStipo_movimiento")
    .off("change")
    .on("change", function () {
      console.log("Filtro cambiado:", $(this).attr("id"), "=", $(this).val());
      if (window.tablaSalidasInternas) {
        window.tablaSalidasInternas.ajax.reload();
      } else {
        console.error("Tabla de salidas internas no encontrada");
      }
    });

  // Para las fechas, recargar al cambiar
  $("#AJSdesde_salidas, #AJShasta_salidas")
    .off("change")
    .on("change", function () {
      console.log("Fecha cambiada:", $(this).attr("id"), "=", $(this).val());
      if (window.tablaSalidasInternas) {
        window.tablaSalidasInternas.ajax.reload();
      } else {
        console.error("Tabla de salidas internas no encontrada");
      }
    });

  // Verificar que los elementos existen
  const elementos = [
    "#AJSbtn-actualizar-salidas",
    "#AJSbtn-limpiar-salidas",
    "#estado_salidas",
    "#AJStipo_movimiento",
    "#AJSdesde_salidas",
    "#AJShasta_salidas",
  ];

  elementos.forEach((elemento) => {
    if ($(elemento).length === 0) {
      console.warn(`Elemento no encontrado: ${elemento}`);
    } else {
      console.log(`Elemento encontrado: ${elemento}`);
    }
  });
}

// =====================================================
// FUNCIÓN PARA ABRIR EL MODAL DE DETALLES DE SALIDA
// =====================================================
function AJSabrirModalDetallesSalida(idIngresosAlidaAlm) {
  console.log("Abriendo modal de detalles para:", idIngresosAlidaAlm);

  // Mostrar el modal
  $("#AJSmodalDetallesSalidaInterna").modal("show");

  // Mostrar el spinner de carga
  $("#AJSloading-salida-detalle").show();
  $("#AJScontenido-salida-detalle").hide();

  // Actualizar el subtítulo del modal
  $("#AJSmodal-subtitulo").text(
    `Cargando información para: ${idIngresosAlidaAlm}`
  );

  // Hacer llamada AJAX para obtener los detalles
  $.ajax({
    url: `/almacen/salida-interna-ajs/${idIngresosAlidaAlm}/`,
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log("Respuesta del servidor:", response);

      if (response.success) {
        // Llenar datos del encabezado
        AJSllenarEncabezadoSalida(response.encabezado);

        // Llenar tabla de productos
        AJSllenarTablaProductos(response.detalles);

        // Llenar totales
        AJSllenarTotales(response.totales, response.total_items);

        // Ocultar spinner y mostrar contenido
        $("#AJSloading-salida-detalle").hide();
        $("#AJScontenido-salida-detalle").show();

        // Actualizar subtítulo con información del documento
        const serie = response.encabezado.SERIE || "";
        const numero = response.encabezado.NUMERO || "";
        $("#AJSmodal-subtitulo").text(`Documento: ${serie}-${numero}`);

        console.log("Modal de detalles cargado correctamente");


        // Método 1: Verificar si jsPDF está disponible globalmente
        console.log('jsPDF disponible:', typeof jspdf !== 'undefined');
        console.log('jsPDF objeto:', jspdf);
        // enviar el idIngresosAlidaAlm al botón de imprimir
        $("#AJSbtn-imprimir").data("id", idIngresosAlidaAlm);
        $("#AJSbtn-imprimir").show();
        

      } else {
        AJSmostrarErrorEnModal(response.message || "Error al cargar los detalles");
      }
    },
    error: function (xhr, status, error) {
      console.error("Error en la petición AJAX:", error);
      console.error("Respuesta del servidor:", xhr.responseText);

      let errorMessage = "Error de conexión con el servidor";
      if (xhr.status === 404) {
        errorMessage = "Salida interna no encontrada";
      } else if (xhr.status === 500) {
        errorMessage = "Error interno del servidor";
      }

      AJSmostrarErrorEnModal(errorMessage);
    },
  });
}

// =====================================================
// FUNCIÓN PARA LLENAR EL ENCABEZADO
// =====================================================
function AJSllenarEncabezadoSalida(encabezado) {
  // ID del documento
  $("#AJSsalida-id-documento").text(encabezado.IDINGRESOSALIDAALM || "-");

  // Número de documento
  const serie = encabezado.SERIE ? encabezado.SERIE.trim() : "";
  const numero = encabezado.NUMERO ? encabezado.NUMERO.trim() : "";
  $("#AJSsalida-id-documento").text(
    serie && numero ? `${serie}-${numero}` : "-"
  );

  // Fecha del documento
  if (encabezado.FECHA) {
    const fecha = new Date(encabezado.FECHA);
    $("#AJSsalida-fecha-documento").text(fecha.toLocaleDateString("es-ES"));
  } else {
    $("#AJSsalida-fecha-documento").text("-");
  }

  // Estado del documento
  const estados = {
    PE: { texto: "Pendiente", clase: "estado-pendiente" },
    CO: { texto: "Confirmado", clase: "estado-confirmado" },
    AN: { texto: "Anulado", clase: "estado-anulado" },
    CE: { texto: "Cerrado", clase: "estado-confirmado" },
    AP: { texto: "Aprobado", clase: "estado-confirmado" },
  };

  const estado = estados[encabezado.IDESTADO] || {
    texto: encabezado.IDESTADO || "-",
    clase: "estado-pendiente",
  };
  $("#AJSsalida-estado-documento").text(estado.texto);

  // Aplicar clase de estado al badge
  const estadoBadge = $("#salida-estado-badge");
  estadoBadge.removeClass("estado-pendiente estado-confirmado estado-anulado");
  estadoBadge.addClass(estado.clase);

  // Empresa y sucursal
  $("#AJSsalida-empresa").val(encabezado.IDEMPRESA || "");
  $("#AJSsalida-sucursal").val(encabezado.IDSUCURSAL || "");

  // Almacenes
  $("#AJSsalida-almacen-origen").val(encabezado.IDALMACEN || "");
  $("#AJSsalida-almacen-destino").val(encabezado.IDALMACEND || "");

  // Responsable
  $("#AJSsalida-responsable").val(encabezado.IDRESPONSABLE || "");

  // Motivo
  const motivos = {
    CON: "Consumo",
    TRA: "Transferencia",
    DEV: "Devolución",
    AJU: "Ajuste",
    MER: "Merma",
  };
  const motivoTexto = motivos[encabezado.IDMOTIVO] || encabezado.IDMOTIVO || "";
  $("#AJSsalida-motivo").val(motivoTexto);

  // Proyecto
  $("#AJSsalida-proyecto").val(encabezado.IDPROYECTO || "");

  // Observaciones
  $("#AJSsalida-observaciones").val(encabezado.GLOSA || "");
}

// =====================================================
// FUNCIÓN PARA LLENAR LA TABLA DE PRODUCTOS
// =====================================================
function AJSllenarTablaProductos(detalles) {
  const tbody = $("#AJStbody-productos-salida");
  tbody.empty();

  if (!detalles || detalles.length === 0) {
    tbody.html(`
      <tr>
        <td colspan="10" class="text-center text-muted py-4">
          <i class="fas fa-box-open fa-2x mb-2 d-block"></i>
          No hay productos en esta salida
        </td>
      </tr>
    `);
    return;
  }

  detalles.forEach(function (detalle) {
    const fila = `
      <tr>
        <td class="text-center">${detalle.ITEM || "-"}</td>
        <td class="font-weight-bold">${detalle.IDPRODUCTO || "-"}</td>
        <td>
          <div class="text-truncate" style="max-width: 250px;" title="${
            detalle.DESCRIPCION || ""
          }">
            ${detalle.DESCRIPCION || "-"}
          </div>
        </td>
        <td class="text-center">${detalle.IDMEDIDA || "-"}</td>
        <td class="text-right font-weight-bold">${AJSformatearNumero(
          detalle.CANTIDAD
        )}</td>
        <td class="text-right">${AJSformatearNumero(detalle.PESO)}</td>
        <td class="text-right">${AJSformatearMoneda(detalle.PRECIO)}</td>
        <td class="text-right font-weight-bold">${AJSformatearMoneda(
          detalle.IMPORTE
        )}</td>
        <td>
          <small class="text-muted">${detalle.IDCONSUMIDOR || "-"}</small>
        </td>
        <td>
          <small class="text-muted text-truncate d-block" style="max-width: 150px;" title="${
            detalle.OBSERVACIONES || ""
          }">
            ${detalle.OBSERVACIONES || "-"}
          </small>
        </td>
      </tr>
    `;
    tbody.append(fila);
  });
}

// =====================================================
// FUNCIÓN PARA LLENAR TOTALES
// =====================================================
function AJSllenarTotales(totales, totalItems) {
  // Total de productos
  $("#AJStotal-productos").text(totalItems || 0);

  if (totales) {
    // Total peso
    const totalPeso = totales.TotalPeso || 0;
    $("#AJStotal-peso").text(`${AJSformatearNumero(totalPeso)} kg`);

    // Total importe
    const totalImporte = totales.TotalImporte || 0;
    $("#AJStotal-importe").text(AJSformatearMoneda(totalImporte));
  } else {
    $("#AJStotal-peso").text("0.00 kg");
    $("#AJStotal-importe").text("S/ 0.00");
  }
}

// =====================================================
// FUNCIÓN PARA MOSTRAR ERROR EN EL MODAL
// =====================================================
function AJSmostrarErrorEnModal(mensaje) {
  $("#AJSloading-salida-detalle").hide();
  $("#AJScontenido-salida-detalle").show();

  // Limpiar contenido y mostrar error
  $("#AJScontenido-salida-detalle").html(`
    <div class="text-center py-5">
      <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
      <h5 class="text-muted">Error al cargar los detalles</h5>
      <p class="text-muted">${mensaje}</p>
      <button type="button" class="btn btn-outline-primary" onclick="$('#AJSmodalDetallesSalidaInterna').modal('hide');">
        <i class="fas fa-times mr-1"></i>Cerrar
      </button>
    </div>
  `);

  $("#AJSmodal-subtitulo").text("Error en la carga");
}

// =====================================================
// FUNCIONES AUXILIARES DE FORMATO
// =====================================================
function AJSformatearNumero(numero) {
  if (numero === null || numero === undefined || numero === "") {
    return "0.000000";
  }
  return parseFloat(numero).toLocaleString("es-PE", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 6, // Permitir hasta 6 decimales para precisión crítica
  });
}

function AJSformatearMoneda(monto) {
  if (monto === null || monto === undefined || monto === "") {
    return "S/ 0.00";
  }
  return (
    "S/ " +
    parseFloat(monto).toLocaleString("es-PE", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
}

//================================================================================================================
// FUNCIONES DEL BUSCADOR DE REQUERIMIENTOS
//================================================================================================================

// Función principal para abrir el modal
function AJSabrirModalBuscarRequerimiento() {
  console.log("🔍 Abriendo modal de búsqueda de requerimientos...");

  // Limpiar datos anteriores
  AJSlimpiarModalDocumentosReferencia();

  // Mostrar el modal
  $("#AJSmodalBuscarRequerimiento").modal("show");

  // Cargar datos iniciales
  AJSmostrarRequerimientos();
}

// Función para limpiar el modal
function AJSlimpiarModalDocumentosReferencia() {
  // Limpiar filtros
  $("#AJSfiltro-numero-doc").val("");
  $("#AJSfiltro-estado-doc").val("");
  $("#AJSfiltro-fecha-desde").val("");
  $("#AJSfiltro-fecha-hasta").val("");

  // Limpiar tabla
  $("#AJStabla-documentos-referencia tbody").empty();

  // Desmarcar checkbox principal
  $("#AJSchk-seleccionar-todos").prop("checked", false);
}

// Función principal para mostrar requerimientos
function AJSmostrarRequerimientos() {
  console.log("📊 Cargando requerimientos desde la API...");

  // Mostrar indicador de carga
  AJSmostrarCargandoTablaDocumentos();

  // Obtener filtros actuales
  const filtros = AJSobtenerFiltrosActuales();

  // Construir URL con parámetros
  const url = AJSconstruirUrlConFiltros(
    "/almacen/api/buscar_requerimiento-ajs/",
    filtros
  );

  // Realizar petición AJAX
  $.ajax({
    url: url,
    method: "GET",
    success: function (response) {
      console.log("✅ Respuesta de la API:", response);

      if (response.status === "success") {
        AJSllenarTablaDocumentosReferencia(response.data);
      } else {
        AJSmostrarErrorTablaDocumentos(response.message);
      }
    },
    error: function (xhr, status, error) {
      console.error("❌ Error en petición AJAX:", error);
      AJSmostrarErrorTablaDocumentos("Error al cargar documentos de referencia");
    },
  });
}

// Función para obtener filtros actuales
function AJSobtenerFiltrosActuales() {
  return {
    numero: $("#AJSfiltro-numero-doc").val().trim(),
    estado: $("#AJSfiltro-estado-doc").val().trim(),
    fecha_desde: $("#AJSfiltro-fecha-desde").val().trim(),
    fecha_hasta: $("#AJSfiltro-fecha-hasta").val().trim(),
    limit: 50,
  };
}

// Función para construir URL con filtros
function AJSconstruirUrlConFiltros(baseUrl, filtros) {
  const params = new URLSearchParams();

  if (filtros.numero) {
    params.append("numero", filtros.numero);
  }

  if (filtros.estado && filtros.estado !== "") {
    params.append("estado", filtros.estado);
  }

  if (filtros.fecha_desde) {
    params.append("fecha_desde", filtros.fecha_desde);
  }

  if (filtros.fecha_hasta) {
    params.append("fecha_hasta", filtros.fecha_hasta);
  }

  if (filtros.limit) {
    params.append("limit", filtros.limit);
  }

  const urlFinal = params.toString()
    ? `${baseUrl}?${params.toString()}`
    : baseUrl;
  console.log("🔗 URL construida:", urlFinal);

  return urlFinal;
}

// Función para mostrar indicador de carga
function AJSmostrarCargandoTablaDocumentos() {
  const tbody = $("#AJStabla-documentos-referencia tbody");
  tbody.html(`
      <tr>
        <td colspan="8" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary mr-2" role="status">
            <span class="sr-only">Cargando...</span>
          </div>
          <span class="text-muted">Cargando documentos...</span>
        </td>
      </tr>
    `);
}

// Función para mostrar error en la tabla
function AJSmostrarErrorTablaDocumentos(mensaje) {
  const tbody = $("#AJStabla-documentos-referencia tbody");
  tbody.html(`
      <tr>
        <td colspan="8" class="text-center py-3 text-danger">
          <i class="fas fa-exclamation-triangle mr-2"></i>
          <span>${mensaje}</span>
          <br>
          <button class="btn btn-sm btn-outline-primary mt-2" onclick="AJSmostrarRequerimientos()">
            <i class="fas fa-redo mr-1"></i>Reintentar
          </button>
        </td>
      </tr>
    `);
}

// Función para llenar la tabla con los datos
function AJSllenarTablaDocumentosReferencia(documentos) {
  const tbody = $("#AJStabla-documentos-referencia tbody");
  tbody.empty();

  if (!documentos || documentos.length === 0) {
    tbody.html(`
        <tr>
          <td colspan="8" class="text-center py-3 text-muted">
            <i class="fas fa-inbox mr-2"></i>
            <span>No se encontraron documentos con los filtros aplicados</span>
          </td>
        </tr>
      `);
    return;
  }

  console.log(`📋 Llenando tabla con ${documentos.length} documentos`);

  documentos.forEach((doc, index) => {
    // Determinar color del estado
    let estadoBadge = "";
    if (doc.IDESTADO === "AP") {
      estadoBadge = '<span class="badge badge-success">AP</span>';
    } else if (doc.IDESTADO === "TP") {
      estadoBadge = '<span class="badge badge-warning">TP</span>';
    } else {
      estadoBadge = `<span class="badge badge-secondary">${doc.IDESTADO}</span>`;
    }

    const row = `
        <tr data-id="${doc.IDREQINTERNO}" style="font-size: 0.75rem;">
          <td style="padding: 0.15rem; text-align: center;">
            <input type="checkbox" 
                   class="chk-documento" 
                   data-id="${doc.IDREQINTERNO}" 
                   style="transform: scale(0.9);" />
          </td>
          <td style="padding: 0.15rem;">${doc.TD || "REQ"}</td>
          <td style="padding: 0.15rem;">${doc.SERIE || ""}</td>
          <td style="padding: 0.15rem;">${doc.NUMERO || ""}</td>
          <td style="padding: 0.15rem;">${doc.FECHA || ""}</td>
          <td style="padding: 0.15rem;" title="${
            doc.RAZON_SOCIAL || ""
          }">${AJStruncarTexto(doc.RAZON_SOCIAL || "", 30)}</td>
          <td style="padding: 0.15rem; text-align: center;">${estadoBadge}</td>
          <td style="padding: 0.15rem;">${doc.IDMOTIVO || ""}</td>
        </tr>
      `;
    tbody.append(row);
  });
}

// Función para truncar texto largo
function AJStruncarTexto(texto, maxLength) {
  if (!texto) return "";
  if (texto.length <= maxLength) return texto;
  return texto.substring(0, maxLength - 3) + "...";
}

//================================================================================================================
// FUNCIONES PARA MANEJAR SELECCIÓN DE DOCUMENTOS Y CARGAR DETALLES
//================================================================================================================

// Variable global para almacenar el documento actualmente seleccionado
let documentoSeleccionadoActual = null;

//================================================================================================================
// FUNCIONES PARA GUARDAR DATOS DEL REQUERIMIENTO SELECCIONADO
//================================================================================================================

// Función para guardar los datos del requerimiento desde la fila seleccionada
function AJSguardarDatosRequerimientoSeleccionado(checkbox) {
  const idReqInterno = $(checkbox).data("id");

  console.log("🔍 Obteniendo datos completos del requerimiento:", idReqInterno);

  // Hacer petición a la API para obtener datos completos
  AJSobtenerDatosCompletosRequerimiento(idReqInterno)
    .then((datosCompletos) => {
      // Guardar datos completos en la variable global
      datosRequerimientoSeleccionado = datosCompletos;
      console.log(
        "💾 Datos completos del requerimiento guardados:",
        datosRequerimientoSeleccionado
      );
    })
    .catch((error) => {
      console.error("❌ Error al obtener datos completos:", error);
      // Fallback: usar datos de la fila como antes
      AJSguardarDatosBasicosDesdeFilaTabla(checkbox);
    });
}

// Función para obtener datos completos del requerimiento desde la API
async function AJSobtenerDatosCompletosRequerimiento(idReqInterno) {
  try {
    console.log("🌐 Consultando API para requerimiento:", idReqInterno);

    // Hacer petición a la API de búsqueda usando el nuevo parámetro idreqinterno
    // Esto nos dará una búsqueda exacta por IDREQINTERNO
    const id_limpio = idReqInterno.trim();
    const url = `/almacen/api/buscar_requerimiento-ajs/?idreqinterno=${id_limpio}&limit=1`;
    console.log("🌐 URL de consulta:", url);

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("📦 Respuesta completa de la API:", data);

    // Validar la respuesta basada en la nueva estructura
    if (data.status !== "success" || !data.data || data.data.length === 0) {
      throw new Error("No se encontraron datos del requerimiento");
    }

    // Tomar el primer resultado (debería ser único por ID)
    const requerimiento = data.data[0];

    // Convertir fecha a formato ISO
    let fechaISO = "";
    if (requerimiento.FECHA) {
      try {
        const partesFecha = requerimiento.FECHA.split("/");
        if (partesFecha.length === 3) {
          const dia = partesFecha[0].padStart(2, "0");
          const mes = partesFecha[1].padStart(2, "0");
          let año = partesFecha[2];

          if (año.length === 2) {
            const añoActual = new Date().getFullYear();
            const sigloActual = Math.floor(añoActual / 100) * 100;
            año = sigloActual + parseInt(año);
          }

          fechaISO = `${año}-${mes}-${dia}`;
        }
      } catch (error) {
        console.warn("⚠️ Error al convertir fecha:", error);
      }
    }

    // Mapear datos completos de la API
    const datosCompletos = {
      // Datos básicos (compatibilidad)
      id: requerimiento.IDREQINTERNO,
      td: requerimiento.TD,
      serie: requerimiento.SERIE,
      numero: requerimiento.NUMERO,
      fecha: requerimiento.FECHA,
      fecha_iso: fechaISO,
      razon_social: requerimiento.RAZON_SOCIAL,
      estado: requerimiento.IDESTADO,
      motivo: requerimiento.IDMOTIVO,

      // Datos completos adicionales de la API - Estructura exacta de la respuesta
      IDREQINTERNO: requerimiento.IDREQINTERNO,
      TD: requerimiento.TD,
      SERIE: requerimiento.SERIE,
      NUMERO: requerimiento.NUMERO,
      FECHA: requerimiento.FECHA,
      RAZON_SOCIAL: requerimiento.RAZON_SOCIAL,
      IDESTADO: requerimiento.IDESTADO,
      IDMOTIVO: requerimiento.IDMOTIVO,
      DOC_ORIGEN: requerimiento.DOC_ORIGEN,
      DOC: requerimiento.DOC,
      IDEMPRESA: requerimiento.IDEMPRESA,
      OBSERVACION: requerimiento.OBSERVACION,
      TOTAL: requerimiento.TOTAL,
      IDRESPONSABLE: requerimiento.IDRESPONSABLE,
    };

    
    return datosCompletos;
  } catch (error) {
    console.error("❌ Error en AJSobtenerDatosCompletosRequerimiento:", error);
    throw error;
  }
}

// Función fallback para obtener datos básicos desde la fila de la tabla
function AJSguardarDatosBasicosDesdeFilaTabla(checkbox) {
  

  const fila = $(checkbox).closest("tr");
  const idReqInterno = $(checkbox).data("id");

  // Extraer datos de las celdas de la fila
  const td = fila.find("td:eq(1)").text().trim();
  const serie = fila.find("td:eq(2)").text().trim();
  const numero = fila.find("td:eq(3)").text().trim();
  const fecha = fila.find("td:eq(4)").text().trim();
  const razonSocial = fila.find("td:eq(5)").text().trim();
  const estadoBadge = fila.find("td:eq(6) .badge");
  const estado = estadoBadge.text().trim();
  const motivo = fila.find("td:eq(7)").text().trim();

  // Convertir fecha a formato ISO
  let fechaISO = "";
  if (fecha && fecha !== "") {
    try {
      const partesFecha = fecha.split("/");
      if (partesFecha.length === 3) {
        const dia = partesFecha[0].padStart(2, "0");
        const mes = partesFecha[1].padStart(2, "0");
        let año = partesFecha[2];

        if (año.length === 2) {
          const añoActual = new Date().getFullYear();
          const sigloActual = Math.floor(añoActual / 100) * 100;
          año = sigloActual + parseInt(año);
        }

        fechaISO = `${año}-${mes}-${dia}`;
      }
    } catch (error) {
      console.warn("⚠️ Error al convertir fecha:", error);
    }
  }

  // Guardar datos básicos en la variable global
  datosRequerimientoSeleccionado = {
    id: idReqInterno,
    td: td,
    serie: serie,
    numero: numero,
    fecha: fecha,
    fecha_iso: fechaISO,
    razon_social: razonSocial,
    estado: estado,
    motivo: motivo,

    // Campos adicionales vacíos para compatibilidad
    IDREQINTERNO: idReqInterno,
    TD: td,
    SERIE: serie,
    NUMERO: numero,
    FECHA: fecha,
    RAZON_SOCIAL: razonSocial,
    IDESTADO: estado,
    IDMOTIVO: motivo,
    DOC_ORIGEN: "",
    DOC: "",
    IDEMPRESA: "001",
    OBSERVACION: "",
    TOTAL: "0.00",
    IDRESPONSABLE: "",
  };

  console.log(
    "💾 Datos básicos guardados (fallback):",
    datosRequerimientoSeleccionado
  );
}

// Función para rellenar automáticamente el componente Doc.Referencia
function AJSrellenarDocumentoReferencia(datos) {
  

  // Guardar IDREQINTERNO en campo oculto (múltiples formatos para compatibilidad)
  $("#AJSdoc-ref-idreqinterno").val(datos.IDREQINTERNO || datos.id || "");

  // Rellenar campos visibles usando tanto el formato antiguo como nuevo
  $("#AJSdoc-ref-doc").val(datos.TD || datos.td || "REQ");
  $("#AJSdoc-ref-serie").val(datos.SERIE || datos.serie || "");
  $("#AJSdoc-ref-numero").val(datos.NUMERO || datos.numero || "");
  $("#AJSdoc-ref-fecha").val(datos.fecha_iso || "");
  $("#AJSdoc-ref-responsable").val(datos.RAZON_SOCIAL || datos.razon_social || "");

  // ✅ NUEVA FUNCIONALIDAD: Autocompletar responsable en el formulario principal
  if (datos.IDRESPONSABLE || datos.idresponsable) {
    const idResponsableDocRef = datos.IDRESPONSABLE || datos.idresponsable;
    const nombreResponsableDocRef = datos.RAZON_SOCIAL || datos.razon_social || "";
    
    
    
    // Autocompletar el select y input del responsable principal
    AJSautocompletarResponsablePrincipal(idResponsableDocRef, nombreResponsableDocRef);
  }

  // ✅ NUEVA FUNCIONALIDAD: Autocompletar observaciones en el formulario principal
  if (datos.OBSERVACION || datos.observacion) {
    const observacionDocRef = datos.OBSERVACION || datos.observacion || "";
    
    
    
    // Autocompletar el campo de observaciones/glosa
    $("#AJSencab-glosa").val(observacionDocRef);
    
  }

  // Actualizar badge de estado con colores
  const estadoBadge = $("#AJSdoc-ref-estado");
  estadoBadge.removeClass(
    "badge-secondary badge-success badge-warning badge-danger"
  );

  const estado = datos.IDESTADO || datos.estado || "";
  if (estado === "APROBADO" || estado === "AP") {
    estadoBadge.addClass("badge-success").text("APROBADO");
  } else if (estado === "PENDIENTE" || estado === "TP") {
    estadoBadge.addClass("badge-warning").text("PENDIENTE");
  } else if (estado === "RECHAZADO" || estado === "RE") {
    estadoBadge.addClass("badge-danger").text("RECHAZADO");
  } else {
    estadoBadge.addClass("badge-secondary").text(estado || "SIN ESTADO");
  }

  

  // Hacer disponibles todos los datos en una variable global para uso posterior
  window.datosRequerimientoCompletos = datos;
  
}

// ✅ NUEVA FUNCIÓN: Autocompletar responsable principal basado en el documento de referencia
function AJSautocompletarResponsablePrincipal(idResponsable, nombreResponsable) {
 

  const selectResponsable = $("#AJSencab-idresponsable");
  const inputDescripcion = $("#AJSencab-desc-responsable");

  // Habilitar el select de responsable si estaba deshabilitado
  selectResponsable.prop("disabled", false);

  // Verificar si el responsable ya existe en el select
  const opcionExistente = selectResponsable.find(`option[value="${idResponsable}"]`);
  
  if (opcionExistente.length > 0) {
    // Si la opción ya existe, seleccionarla
    
    selectResponsable.val(idResponsable);
    
    // Trigger change event para cualquier lógica adicional
    selectResponsable.trigger('change');
  } else {
    // Si la opción no existe, agregarla al select y luego seleccionarla
    
    const nuevaOpcion = new Option(idResponsable, idResponsable, true, true);
    selectResponsable.append(nuevaOpcion);
    
    // Seleccionar la nueva opción
    selectResponsable.val(idResponsable);
    
    // Trigger change event
    selectResponsable.trigger('change');
  }

  // Actualizar SIEMPRE el campo de descripción con el nombre del responsable
  inputDescripcion.val(nombreResponsable);

  
}

// Función de utilidad para verificar el estado actual de los datos guardados
function AJSverificarDatosRequerimientoGuardados() {
  

  return datosRequerimientoSeleccionado;
}

// Función para manejar la selección individual de documentos
function AJSmanejarSeleccionDocumento(checkbox) {
  const isChecked = $(checkbox).prop("checked");
  const idReqInterno = $(checkbox).data("id");

  

  if (isChecked) {
    // Desmarcar otros checkboxes (solo uno a la vez)
    $(".chk-documento").not(checkbox).prop("checked", false);

    // PASO 1: Guardar datos del requerimiento seleccionado desde la fila
    AJSguardarDatosRequerimientoSeleccionado(checkbox);

    // Cargar detalles del requerimiento seleccionado
    AJScargarDetallesRequerimiento(idReqInterno);

    // Guardar referencia del documento seleccionado
    documentoSeleccionadoActual = {
      id: idReqInterno,
      checkbox: checkbox,
    };
  } else {
    // Si se desmarca, limpiar la tabla de detalles y datos guardados
    AJSlimpiarTablaDetallesProducto();
    documentoSeleccionadoActual = null;
    datosRequerimientoSeleccionado = null; // Limpiar datos guardados
    
  }

  // Actualizar estado del checkbox principal
  AJSactualizarCheckboxPrincipal();
}

// Función para manejar la selección de todos (por ahora solo limpia)
function AJSmanejarSeleccionTodos(checkbox) {
  const isChecked = $(checkbox).prop("checked");

  if (!isChecked) {
    // Si se desmarca "seleccionar todos", desmarcar todos los individuales
    $(".chk-documento").prop("checked", false);
    AJSlimpiarTablaDetallesProducto();
    documentoSeleccionadoActual = null;
  } else {
    // Por ahora no permitimos selección múltiple, solo limpiamos
    $(checkbox).prop("checked", false);
    
  }
}

// Función para actualizar el estado del checkbox principal
function AJSactualizarCheckboxPrincipal() {
  const totalCheckboxes = $(".chk-documento").length;
  const checkboxesMarcados = $(".chk-documento:checked").length;

  const checkboxPrincipal = $("#AJSchk-seleccionar-todos");

  if (checkboxesMarcados === 0) {
    checkboxPrincipal.prop("checked", false);
    checkboxPrincipal.prop("indeterminate", false);
  } else if (checkboxesMarcados === totalCheckboxes) {
    checkboxPrincipal.prop("checked", true);
    checkboxPrincipal.prop("indeterminate", false);
  } else {
    checkboxPrincipal.prop("checked", false);
    checkboxPrincipal.prop("indeterminate", true);
  }
}

// Función principal para cargar detalles del requerimiento
function AJScargarDetallesRequerimiento(idReqInterno) {
 
  
  // Limpiar selección de productos anterior
  AJSlimpiarSeleccionProductos();

  // Mostrar indicador de carga en la tabla de detalles
  AJSmostrarCargandoDetallesProducto();

  // Construir URL de la API
  const url = `/almacen/api/detalle-requerimiento-ajs/${idReqInterno}/`;

  // Realizar petición AJAX
  $.ajax({
    url: url,
    method: "GET",
    success: function (response) {
      

      if (response.status === "success") {
        // Llenar tabla con los detalles
        AJSllenarTablaDetallesProducto(response.data, response.estadisticas);

        // Mostrar estadísticas si las hay
        if (response.estadisticas) {
          AJSmostrarEstadisticasRequerimiento(response.estadisticas);
        }
      } else {
        AJSmostrarErrorDetallesProducto(
          response.message || "Error al cargar detalles"
        );
      }
    },
    error: function (xhr, status, error) {
      console.error(`❌ Error al cargar detalles para ${idReqInterno}:`, error);

      let mensajeError = "Error de conexión con el servidor";
      if (xhr.status === 404) {
        mensajeError = "Requerimiento no encontrado";
      } else if (xhr.status === 500) {
        mensajeError = "Error interno del servidor";
      }

      AJSmostrarErrorDetallesProducto(mensajeError);
    },
  });
}

// Función para mostrar indicador de carga en detalles
function AJSmostrarCargandoDetallesProducto() {
  const tbody = $("#AJStabla-detalles-producto tbody");
  tbody.html(`
    <tr>
      <td colspan="13" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary mr-2" role="status">
          <span class="sr-only">Cargando...</span>
        </div>
        <span class="text-muted">Cargando detalles del requerimiento...</span>
      </td>
    </tr>
  `);
}

// Función para mostrar error en detalles
function AJSmostrarErrorDetallesProducto(mensaje) {
  const tbody = $("#AJStabla-detalles-producto tbody");
  tbody.html(`
    <tr>
      <td colspan="13" class="text-center py-4 text-danger">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        <span>${mensaje}</span>
        <br>
        <button class="btn btn-sm btn-outline-primary mt-2" onclick="AJSrecargarDetallesActual()">
          <i class="fas fa-redo mr-1"></i>Reintentar
        </button>
      </td>
    </tr>
  `);
}

// Función para recargar detalles del documento actual
function AJSrecargarDetallesActual() {
  if (documentoSeleccionadoActual && documentoSeleccionadoActual.id) {
    AJScargarDetallesRequerimiento(documentoSeleccionadoActual.id);
  }
}

// Función para limpiar la tabla de detalles
function AJSlimpiarTablaDetallesProducto() {
  const tbody = $("#AJStabla-detalles-producto tbody");
  tbody.html(`
    <tr>
      <td colspan="13" class="text-center py-3 text-muted">
        <i class="fas fa-info-circle mr-2"></i>
        <span>Seleccione un requerimiento para ver los detalles</span>
      </td>
    </tr>
  `);
}

// Función principal para llenar la tabla de detalles con productos
function AJSllenarTablaDetallesProducto(productos, estadisticas) {
  const tbody = $("#AJStabla-detalles-producto tbody");
  tbody.empty();

  if (!productos || productos.length === 0) {
    tbody.html(`
      <tr>
        <td colspan="13" class="text-center py-3 text-muted">
          <i class="fas fa-inbox mr-2"></i>
          <span>No hay productos en este requerimiento</span>
        </td>
      </tr>
    `);
    // Limpiar datos completos si no hay productos
    datosProductosCompletosAPI = [];
    return;
  }

  // ✅ GUARDAR TODOS LOS DATOS COMPLETOS DE LA API
  datosProductosCompletosAPI = [...productos]; // Copia completa de todos los datos

  
  

  productos.forEach((producto, index) => {
    // Determinar color del estado
    let estadoBadge = "";
    if (producto.ESTADO_ATENCION === "ATENDIDO") {
      estadoBadge = `<span class="badge badge-success">${producto.ESTADO_ATENCION}</span>`;
    } else if (producto.ESTADO_ATENCION === "EN_PROCESO") {
      estadoBadge = `<span class="badge badge-warning">${producto.ESTADO_ATENCION}</span>`;
    } else {
      estadoBadge = `<span class="badge badge-danger">${producto.ESTADO_ATENCION}</span>`;
    }

    // Formatear porcentaje
    const porcentaje = producto.PORCENTAJE_ATENCION || 0;
    let porcentajeBadge = "";
    if (porcentaje >= 100) {
      porcentajeBadge = `<span class="badge badge-success">${porcentaje}%</span>`;
    } else if (porcentaje >= 50) {
      porcentajeBadge = `<span class="badge badge-warning">${porcentaje}%</span>`;
    } else {
      porcentajeBadge = `<span class="badge badge-danger">${porcentaje}%</span>`;
    }

    const row = `
      <tr style="font-size: 0.75rem;" data-item="${producto.ITEM}">
        <td style="padding: 0.25rem; text-align: center;">
          <input type="checkbox" class="chk-producto" data-item="${
            producto.ITEM
          }">
        </td>
        <td style="padding: 0.25rem; text-align: center;">${
          producto.ITEM || ""
        }</td>
        <td style="padding: 0.25rem; font-weight: bold;">${
          producto.IDPRODUCTO || ""
        }</td>
        <td style="padding: 0.25rem;" title="${
          producto.DESCRIPCION || ""
        }">${AJStruncarTexto(producto.DESCRIPCION || "", 40)}</td>
        <td style="padding: 0.25rem; text-align: center;">${
          producto.IDMEDIDA || ""
        }</td>
        <td style="padding: 0.25rem; text-align: right; font-weight: bold;">${
          producto.CANTAPROBADA_DISPLAY || "0"
        }</td>
        <td style="padding: 0.25rem; text-align: right;">${
          producto.CANTIDAD_DISPLAY - producto.CANTIDAD_PENDIENTE_DISPLAY || "0"
        }</td>
        <td style="padding: 0.25rem; text-align: right; color: ${
          producto.CANTIDAD_PENDIENTE > 0 ? "#dc3545" : "#28a745"
        };">${producto.CANTIDAD_PENDIENTE_DISPLAY || "0"}</td>
        <td style="padding: 0.25rem; text-align: center;">${
          producto.IDCONSUMIDOR || ""
        }</td>
        <td style="padding: 0.25rem; text-align: center;">${
          producto.IDRESPONSABLE || ""
        }</td>
        <td style="padding: 0.25rem; text-align: center;">${estadoBadge}</td>
        <td style="padding: 0.25rem; text-align: center;">${porcentajeBadge}</td>
        <td style="padding: 0.25rem; text-align: center; font-size: 0.7rem;">${
          producto.PARAFECHA_FORMATTED || ""
        }</td>
      </tr>
    `;

    tbody.append(row);
  });

  
}

// Función para mostrar estadísticas del requerimiento (opcional)
function AJSmostrarEstadisticasRequerimiento(estadisticas) {
  

  // Aquí puedes agregar lógica para mostrar las estadísticas en algún lugar del modal
  // Por ejemplo, en un panel de resumen o en el footer del modal

  // Ejemplo de log para debug
  
}

// Función para obtener el documento actualmente seleccionado
function AJSobtenerDocumentoSeleccionado() {
  return documentoSeleccionadoActual;
}

//================================================================================================================
// FUNCIONES PARA MANEJO DE SELECCIÓN DE PRODUCTOS
//================================================================================================================

// Función para manejar la selección individual de productos
function AJSmanejarSeleccionProducto(checkbox) {
  const item = checkbox.getAttribute("data-item");
  const fila = checkbox.closest("tr");

  if (checkbox.checked) {
    // ✅ BUSCAR DATOS COMPLETOS EN LA API
    const productoCompleto = datosProductosCompletosAPI.find(
      (p) => p.ITEM === item
    );

    if (productoCompleto) {
      // Añadir datos completos a la lista de seleccionados
      productosSeleccionadosCompletos.push(productoCompleto);

      // También mantener la lista antigua para compatibilidad
      const producto = AJSobtenerDatosProductoDeFila(fila, item);
      productosSeleccionados.push(producto);

      
    } else {
      

      // Fallback: usar datos de la fila
      const producto = AJSobtenerDatosProductoDeFila(fila, item);
      productosSeleccionados.push(producto);
      
    }
  } else {
    // Remover de ambas listas de seleccionados
    productosSeleccionados = productosSeleccionados.filter(
      (p) => p.ITEM !== item
    );
    productosSeleccionadosCompletos = productosSeleccionadosCompletos.filter(
      (p) => p.ITEM !== item
    );

    
  }

  // Actualizar checkbox principal
  AJSactualizarCheckboxPrincipalProductos();

  
}

// Función para manejar selección/deselección de todos los productos
function AJSmanejarSeleccionTodosProductos(checkbox) {
  const checkboxesProductos = document.querySelectorAll(".chk-producto");

  if (checkbox.checked) {
    // Seleccionar todos los productos
    checkboxesProductos.forEach((chk) => {
      if (!chk.checked) {
        chk.checked = true;
        // Simular el evento change para cada checkbox
        AJSmanejarSeleccionProducto(chk);
      }
    });

    
  } else {
    // Deseleccionar todos los productos
    checkboxesProductos.forEach((chk) => {
      if (chk.checked) {
        chk.checked = false;
        // Simular el evento change para cada checkbox
        AJSmanejarSeleccionProducto(chk);
      }
    });

    
  }
}

// Función para actualizar el estado del checkbox principal
function AJSactualizarCheckboxPrincipalProductos() {
  const checkboxPrincipal = document.getElementById("AJSselectAllProductos");
  const checkboxesProductos = document.querySelectorAll(".chk-producto");
  const checkboxesSeleccionados = document.querySelectorAll(
    ".chk-producto:checked"
  );

  if (checkboxesProductos.length === 0) {
    // No hay productos disponibles
    checkboxPrincipal.checked = false;
    checkboxPrincipal.indeterminate = false;
  } else if (checkboxesSeleccionados.length === 0) {
    // Ningún producto seleccionado
    checkboxPrincipal.checked = false;
    checkboxPrincipal.indeterminate = false;
  } else if (checkboxesSeleccionados.length === checkboxesProductos.length) {
    // Todos los productos seleccionados
    checkboxPrincipal.checked = true;
    checkboxPrincipal.indeterminate = false;
  } else {
    // Algunos productos seleccionados
    checkboxPrincipal.checked = false;
    checkboxPrincipal.indeterminate = true;
  }
}

// Función para obtener los datos completos del producto desde la fila de la tabla
function AJSobtenerDatosProductoDeFila(fila, item) {
  const celdas = fila.querySelectorAll("td");

  return {
    ITEM: item,
    IDPRODUCTO: celdas[2].textContent.trim(), // Columna 2 (Código)
    DESCRIPCION: celdas[3].textContent.trim(), // Columna 3 (Producto)
    IDMEDIDA: celdas[4].textContent.trim(), // Columna 4 (U.M.)
    CANTAPROBADA: celdas[5].textContent.trim(), // Columna 5 (Cant. Aprobada)
    CANTIDAD_ATENDIDA: celdas[6].textContent.trim(), // Columna 6 (Cant. Atendida)
    CANTIDAD_PENDIENTE: celdas[7].textContent.trim(), // Columna 7 (Por Atender)
    IDCONSUMIDOR: celdas[8].textContent.trim(), // Columna 8 (Consumidor)
    IDRESPONSABLE: celdas[9].textContent.trim(), // Columna 9 (Responsable)
    ESTADO_ATENCION: celdas[10].textContent.trim(), // Columna 10 (Estado)
    PORCENTAJE_ATENCION: celdas[11].textContent.trim(), // Columna 11 (% Atención)
    PARA_FECHA: celdas[12].textContent.trim(), // Columna 12 (Para Fecha)
    SELECCIONADO_EN: new Date().toISOString(),
  };
}

// Función para limpiar la selección de productos
function AJSlimpiarSeleccionProductos() {
  productosSeleccionados = [];
  productosSeleccionadosCompletos = [];

  // Desmarcar todos los checkboxes
  const checkboxes = document.querySelectorAll(
    ".chk-producto, #AJSselectAllProductos"
  );
  checkboxes.forEach((chk) => {
    chk.checked = false;
    chk.indeterminate = false;
  });

  
}

// Función para obtener la lista actual de productos seleccionados
function AJSobtenerProductosSeleccionados() {
  return [...productosSeleccionados]; // Retornar copia para evitar modificaciones externas
}

//================================================================================================================
// FUNCIONES PARA TRANSFERIR PRODUCTOS AL MODAL DE NUEVA SALIDA
//================================================================================================================

// Función para transferir productos seleccionados al modal de nueva salida
function AJStransferirProductosAModalSalida(productos, requerimiento) {
  

  // Actualizar información del documento de referencia
  AJSactualizarDocumentoReferencia(requerimiento);

  // Llenar la tabla de productos seleccionados
  AJSllenarTablaProductosSeleccionados(productos);

  // Mostrar la card de productos seleccionados
  $("#card-productos-seleccionados").show();

  
}

// Función para actualizar la información del documento de referencia
function AJSactualizarDocumentoReferencia(requerimiento) {
  $("#AJSdoc-ref-doc").val(requerimiento.td || "REQ");
  $("#AJSdoc-ref-serie").val(requerimiento.serie || "");
  $("#AJSdoc-ref-numero").val(requerimiento.numero || "");
  $("#AJSdoc-ref-fecha").val(requerimiento.fecha_iso || "");
  $("#AJSdoc-ref-responsable").val(requerimiento.razon_social || "");

  // Actualizar badge de estado
  const estadoBadge = $("#AJSdoc-ref-estado");
  if (requerimiento.estado === "AP") {
    estadoBadge
      .removeClass("badge-secondary badge-warning")
      .addClass("badge-success")
      .text("APROBADO");
  } else if (requerimiento.estado === "TP") {
    estadoBadge
      .removeClass("badge-secondary badge-success")
      .addClass("badge-warning")
      .text("PENDIENTE");
  } else {
    estadoBadge
      .removeClass("badge-success badge-warning")
      .addClass("badge-secondary")
      .text(requerimiento.estado || "SIN ESTADO");
  }
}

// Función para llenar la tabla de productos seleccionados
function AJSllenarTablaProductosSeleccionados(productos) {
  const tbody = $("#tabla-productos-seleccionados tbody");
  tbody.empty();

  if (!productos || productos.length === 0) {
    tbody.html(`
      <tr>
        <td colspan="8" class="text-center py-3 text-muted">
          <i class="fas fa-info-circle mr-2"></i>
          <span>No hay productos seleccionados</span>
        </td>
      </tr>
    `);
    $("#AJStotal-productos-seleccionados").text("0");
    return;
  }

 
  

  productos.forEach((producto, index) => {
    
    // Limpiar y convertir cantidad pendiente a número
    const cantidadPendiente =
      parseFloat(
        (
          producto.CANTIDAD_PENDIENTE_DISPLAY ||
          producto.CANTIDAD_PENDIENTE ||
          "0"
        )
          .toString()
          .replace(/[^\d.-]/g, "")
      ) || 0;

    const row = `
      <tr style="font-size: 0.8rem;" data-item="${producto.ITEM}">
        <td style="padding: 0.4rem; text-align: center; font-weight: bold;">${
          producto.ITEM
        }</td>
        <td style="padding: 0.4rem; font-weight: bold;">${
          producto.IDPRODUCTO
        }</td>
        <td style="padding: 0.4rem;" title="${
          producto.DESCRIPCION
        }">${AJStruncarTexto(producto.DESCRIPCION, 50)}</td>
        <td style="padding: 0.4rem; text-align: center;">${
          producto.IDMEDIDA
        }</td>
        <td style="padding: 0.4rem; text-align: right; color: #dc3545; font-weight: bold;">${
          producto.CANTIDAD_PENDIENTE_DISPLAY ||
          producto.CANTIDAD_PENDIENTE ||
          "0"
        }</td>
        <td style="padding: 0.4rem;">
          <input 
            type="number" 
            class="form-control form-control-sm cantidad-salir" 
            value="${cantidadPendiente}" 
            min="0" 
            max="${cantidadPendiente}" 
            step="0.000001"
            data-item="${producto.ITEM}"
            style="width: 90px; text-align: right;"
          >
        </td>
        <td style="padding: 0.4rem;">${producto.IDCONSUMIDOR}</td>
        <td style="padding: 0.4rem; text-align: center;">
          <button 
            class="btn btn-danger btn-xs" 
            onclick="AJSeliminarProductoSeleccionado('${producto.ITEM}')"
            title="Eliminar producto"
          >
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>
    `;

    tbody.append(row);
  });

  // Actualizar contador
  $("#AJStotal-productos-seleccionados").text(productos.length);

  
}

// Función para eliminar un producto de la tabla de productos seleccionados
function AJSeliminarProductoSeleccionado(item) {
  

  // Remover fila de la tabla
  $(`#tabla-productos-seleccionados tbody tr[data-item="${item}"]`).remove();

  // Actualizar contador
  const filasRestantes = $("#tabla-productos-seleccionados tbody tr").length;
  $("#AJStotal-productos-seleccionados").text(filasRestantes);

  // Si no quedan productos, mostrar mensaje
  if (filasRestantes === 0) {
    $("#tabla-productos-seleccionados tbody").html(`
      <tr>
        <td colspan="8" class="text-center py-3 text-muted">
          <i class="fas fa-info-circle mr-2"></i>
          <span>No hay productos seleccionados</span>
        </td>
      </tr>
    `);
    $("#card-productos-seleccionados").hide();
  }

  
}

// Función para obtener los productos finales con las cantidades editadas
function oAJSbtenerProductosParaSalida() {
  const productos = [];

  $("#tabla-productos-seleccionados tbody tr").each(function () {
    const fila = $(this);
    const item = fila.data("item");

    if (item) {
      // Solo procesar filas con datos
      const cantidadInput = fila.find(".cantidad-salir");
      // Usar Number() para preservar precisión decimal completa
      const cantidad = Number(cantidadInput.val()) || 0;

      if (cantidad > 0) {
        productos.push({
          ITEM: item,
          IDPRODUCTO: fila.find("td:eq(1)").text().trim(),
          DESCRIPCION: fila.find("td:eq(2)").attr("title"),
          IDMEDIDA: fila.find("td:eq(3)").text().trim(),
          CANTIDAD_PENDIENTE: fila.find("td:eq(4)").text().trim(),
          CANTIDAD_SALIR: cantidad, // Mantener precisión completa
          IDCONSUMIDOR: fila.find("td:eq(6)").text().trim(),
        });
      }
    }
  });

  return productos;
}

// Función para limpiar la tabla de productos seleccionados
function AJSlimpiarTablaProductosSeleccionados() {
  $("#tabla-productos-seleccionados tbody").html(`
    <tr>
      <td colspan="8" class="text-center py-3 text-muted">
        <i class="fas fa-info-circle mr-2"></i>
        <span>No hay productos seleccionados</span>
      </td>
    </tr>
  `);

  $("#AJStotal-productos-seleccionados").text("0");
  $("#card-productos-seleccionados").hide();

  // Limpiar información del documento de referencia
  $("#AJSdoc-ref-idreqinterno").val("");
  $("#AJSdoc-ref-doc").val("");
  $("#AJSdoc-ref-serie").val("");
  $("#AJSdoc-ref-numero").val("");
  $("#AJSdoc-ref-fecha").val("");
  $("#AJSdoc-ref-responsable").val("");
  $("#AJSdoc-ref-estado")
    .removeClass("badge-success badge-warning badge-danger")
    .addClass("badge-secondary")
    .text("Sin seleccionar");

  // Limpiar datos del requerimiento guardados
  datosRequerimientoSeleccionado = null;

  
}

//================================================================================================================
// FUNCIONES PARA RECOPILAR DATOS DEL FORMULARIO
//================================================================================================================

// Función para recopilar todos los datos del encabezado del formulario
function AJSrecopilarDatosEncabezado() {
  

  // Obtener fecha actual para el periodo si no está establecido
  const fechaActual = new Date();
  const periodoActual = `${fechaActual.getFullYear()}${String(
    fechaActual.getMonth() + 1
  ).padStart(2, "0")}`;

  // Recopilar todos los datos según la estructura requerida
  const encabezado = {
    IDEMPRESA: "001", // Valor fijo
    IDEMISOR: $("#encab-idpunto").val() || "001", // Del campo punto de emisión
    PERIODO: $("#encab-periodo").val() || periodoActual,
    IDALMACEN: $("#encab-idalmacen").val() || "001",
    IDDOCUMENTO: $("#encab-iddocumento").val() || "SAL",
    FECHA: $("#encab-fecha").val() || "",
    IDRESPONSABLE: $("#AJSencab-idresponsable").val() || "",
    GLOSA: $("#AJSencab-glosa").val() || "",
    IDMONEDA: $("#encab-idmoneda").val() || "01",
    TCAMBIO: parseFloat($("#AJSencab-tcambio").val()) || 3.759,
    IDMOTIVO: $("#encab-motivo-salida").val() || "SCC",
    IDSUCURSAL: $("#encab-idsucursal").val() || "001",
    IDUSUARIO: "ADMINISTRADOR", // Valor fijo por ahora
  };

  return encabezado;
}

// Función para inicializar el formulario con valores por defecto
function AJSinicializarFormularioSalida() {
  // Obtener fecha actual
  const fechaActual = new Date();
  const fechaHoy = fechaActual.toISOString().split("T")[0]; // Formato YYYY-MM-DD
  const periodoActual = `${fechaActual.getFullYear()}${String(
    fechaActual.getMonth() + 1
  ).padStart(2, "0")}`;

  // Establecer valores por defecto
  $("#encab-fecha").val(fechaHoy);
  $("#encab-periodo").val(periodoActual);

  // Actualizar descripción del almacén según la selección inicial
  const almacenSeleccionado = $("#encab-idalmacen option:selected");
  if (almacenSeleccionado.length > 0) {
    const descripcionAlmacen = almacenSeleccionado.attr("data-descripcion");
    $("#encab-desc-almacen").val(descripcionAlmacen);
  }

  // Actualizar descripción de la moneda según la selección inicial
  const monedaSeleccionada = $("#encab-idmoneda").val();
  if (monedaSeleccionada === "01") {
    $("#encab-desc-moneda").val("SOLES");
  } else if (monedaSeleccionada === "02") {
    $("#encab-desc-moneda").val("DÓLARES");
  }

  

  
}

// Función para recopilar los datos COMPLETOS de los productos seleccionados
function AJSrecopilarDatosProductosCompletos() {
  

  const productos = [];

  // Verificar si hay productos seleccionados con datos completos
  if (productosSeleccionadosCompletos.length === 0) {
    
    return productos;
  }

  // Recorrer cada producto seleccionado con datos completos
  productosSeleccionadosCompletos.forEach((productoCompleto, index) => {
    // Buscar la cantidad editada por el usuario en la tabla de productos seleccionados
    const filaProducto = $(
      `#tabla-productos-seleccionados tbody tr[data-item="${productoCompleto.ITEM}"]`
    );
    let cantidadASalir = productoCompleto.CANTIDAD_PENDIENTE || 0;

    if (filaProducto.length > 0) {
      const inputCantidad = filaProducto.find(".cantidad-salir");
      if (inputCantidad.length > 0) {
        cantidadASalir = parseFloat(inputCantidad.val()) || 0;
      }
    }

    // Solo incluir productos con cantidad mayor a 0
    if (cantidadASalir > 0) {
      // Crear objeto producto con TODOS los datos de la API + cantidad editada
      const producto = {
        IDEMPRESA: productoCompleto.IDEMPRESA || "001",
        IDPRODUCTO: productoCompleto.IDPRODUCTO,
        DESCRIPCION: productoCompleto.DESCRIPCION,
        IDMEDIDA: productoCompleto.IDMEDIDA,
        IDCONSUMIDOR: productoCompleto.IDCONSUMIDOR,
        CANTIDAD: cantidadASalir, // Cantidad que el usuario quiere sacar
        IDREFERENCIA: productoCompleto.IDREQINTERNO,
        ITEMREF: productoCompleto.ITEM,
        TABLAREF: "REQINTERNO",
        idreqinterno: productoCompleto.IDREQINTERNO,
        itemreqinterno: productoCompleto.ITEM,

        // ✅ DATOS ADICIONALES COMPLETOS DE LA API
        CANTIDAD_ORIGINAL: productoCompleto.CANTIDAD,
        CANTAPROBADA: productoCompleto.CANTAPROBADA,
        CANTIDAD_PENDIENTE: productoCompleto.CANTIDAD_PENDIENTE,
        ATENDIDO: productoCompleto.ATENDIDO,
        ESTADOS: productoCompleto.ESTADOS,
        IDRESPONSABLE: productoCompleto.IDRESPONSABLE,
        IDCLIEPROV: productoCompleto.IDCLIEPROV,
        PARAFECHA: productoCompleto.PARAFECHA,
        PARAFECHA_FORMATTED: productoCompleto.PARAFECHA_FORMATTED,
        genero_salida: productoCompleto.genero_salida,
        ESTADO_ATENCION: productoCompleto.ESTADO_ATENCION,
        ESTADO_ATENCION_BADGE: productoCompleto.ESTADO_ATENCION_BADGE,
        PORCENTAJE_ATENCION: productoCompleto.PORCENTAJE_ATENCION,
        CANTIDAD_DISPLAY: productoCompleto.CANTIDAD_DISPLAY,
        CANTAPROBADA_DISPLAY: productoCompleto.CANTAPROBADA_DISPLAY,
        CANTIDAD_PENDIENTE_DISPLAY: productoCompleto.CANTIDAD_PENDIENTE_DISPLAY,
      };

      productos.push(producto);

      
    } else {
      
    }
  });

  
  return productos;
}

// Función para recopilar los datos del documento de referencia
function AJSrecopilarDatosDocumentoReferencia() {
  

  // Verificar si hay datos completos disponibles (de la nueva API)
  if (!window.datosRequerimientoCompletos && !datosRequerimientoSeleccionado) {
    
    return {};
  }

  // Priorizar datos completos de la API si están disponibles
  const datos =
    window.datosRequerimientoCompletos || datosRequerimientoSeleccionado;

  

  // Crear objeto documento de referencia con EXACTAMENTE los campos solicitados
  const documentoReferencia = {
    IDEMPRESA: datos.IDEMPRESA || "001",
    IDREFERENCIA: datos.IDREQINTERNO || datos.id || "",
    TABLAREFERENCIA: "REQINTERNO", // Valor por defecto como solicitaste
    IDDOCUMENTO: datos.TD || datos.td || "REQ",
    SERIE: datos.SERIE || datos.serie || "",
    NUMERO: datos.NUMERO || datos.numero || "",
    FECHA: datos.fecha_iso || datos.FECHA || datos.fecha || "",
    IDRESPONSABLE: datos.IDRESPONSABLE || "",
    GLOSA: datos.OBSERVACION || datos.observacion || "Documento de referencia",
    TOTAL: parseFloat(datos.TOTAL || datos.total || 0) || 0.0,
  };

  
  

  return documentoReferencia;
}

//================================================================================================================
// FUNCIÓN PARA RECOPILAR PRODUCTOS PARA GUARDADO CON ESTRUCTURA ESPECÍFICA
//================================================================================================================
function AJSrecopilarProductosParaGuardado() {
  

  const productosParaGuardado = [];
  const tablaProductos = document.querySelector(
    "#tabla-productos-seleccionados tbody"
  );

  if (!tablaProductos) {
    
    return productosParaGuardado;
  }

  const filas = tablaProductos.querySelectorAll("tr");
  

  filas.forEach((fila, index) => {
    try {
      // Obtener datos de la fila
      const celdas = fila.querySelectorAll("td");

      if (celdas.length < 8) {
        
        return;
      }

      // Extraer datos específicos según la estructura solicitada
      const item = celdas[0].textContent.trim();
      const idProducto = celdas[1].textContent.trim();
      const descripcion = celdas[2].textContent.trim();
      const idMedida = celdas[3].textContent.trim();
      const cantidadInput = celdas[5].querySelector("input[type='number']");
      const consumidor = celdas[6].textContent.trim();

      // Obtener la cantidad a salir del input
      const cantidad = cantidadInput ? parseFloat(cantidadInput.value) || 0 : 0;

      // Obtener IDREQINTERNO del documento de referencia
      const idReqInterno = $("#AJSdoc-ref-idreqinterno").val() || "";

      // Crear objeto con estructura específica solicitada
      const productoParaGuardado = {
        IDEMPRESA: "001", // Valor fijo como en el encabezado
        IDPRODUCTO: idProducto,
        DESCRIPCION: descripcion,
        IDMEDIDA: idMedida,
        IDCONSUMIDOR: consumidor,
        CANTIDAD: cantidad,
        IDREFERENCIA: idReqInterno, // IDREQINTERNO como solicitas
        ITEMREF: item, // Valor igual que el ITEM
        TABLAREF: "REQINTERNO", // Valor por defecto como solicitas
        ITEM: item, // itemreqinterno = ITEM como solicitas
      };

      productosParaGuardado.push(productoParaGuardado);

      
    } catch (error) {

      Swal.fire({
        title: "¡Error detectado!",
        text: `Error procesando fila ${index + 1}: ${error}`,
        icon: "error",
        confirmButtonColor: "#e74c3c"
      });   console.error(`❌ Error procesando fila ${index + 1}:`, error);
    }
  });

  
  return productosParaGuardado;
}

//================================================================================================================
// FUNCIÓN DE PRUEBA PARA VERIFICAR LA NUEVA IMPLEMENTACIÓN
//================================================================================================================
async function AJSprobarNuevaImplementacionAPI() {
  

  const idReqInternoEjemplo = "_76F0S2Y2D11109";

  try {
    
    const datosCompletos = await AJSobtenerDatosCompletosRequerimiento(
      idReqInternoEjemplo
    );

    
    AJSrellenarDocumentoReferencia(datosCompletos);

   

    // Verificar que window.datosRequerimientoCompletos se haya creado
    if (window.datosRequerimientoCompletos) {
      
      

      
      const documentoRef = AJSrecopilarDatosDocumentoReferencia();

      
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error en la prueba",
      text: error && error.message ? error.message : String(error),
      confirmButtonColor: "#dc3545"
    });
    console.error("❌ Error en la prueba:", error);
  }

  
}

// Para ejecutar la prueba desde la consola del navegador:
// AJSprobarNuevaImplementacionAPI()

//================================================================================================================
// FUNCIÓN DE PRUEBA COMPLETA DEL FLUJO DE GUARDADO
//================================================================================================================
async function AJSprobarFlujoCompletoGuardado() {
  

  try {
    // 1. Probar obtención de datos de la API
    const idReqInternoEjemplo = "_76F0S2Y2D11109";
    
    const datosCompletos = await AJSobtenerDatosCompletosRequerimiento(
      idReqInternoEjemplo
    );
    

    // 2. Rellenar documento de referencia
    
    AJSrellenarDocumentoReferencia(datosCompletos);
    

    // 3. Verificar que hay datos completos disponibles
    if (!window.datosRequerimientoCompletos) {
      
      return;
    }
    

    // 4. Probar generación de estructura final
   
    const estructura = AJSgenerarEstructuraFinalParaGuardar();
    

    // 5. Verificar documento_referencia específicamente
    
    const docRef = estructura.documento_referencia;

    const camposRequeridos = [
      "IDEMPRESA",
      "IDREFERENCIA",
      "TABLAREFERENCIA",
      "IDDOCUMENTO",
      "SERIE",
      "NUMERO",
      "FECHA",
      "IDRESPONSABLE",
      "GLOSA",
      "TOTAL",
    ];

    let todosCamposPresentes = true;
    camposRequeridos.forEach((campo) => {
      if (!(campo in docRef)) {
        console.error(`❌ Falta el campo: ${campo}`);
        Swal.fire({
          icon: "error",
          title: "Falta campo requerido",
          text: `Falta el campo: ${campo}`,
          confirmButtonColor: "#dc3545"
        });    todosCamposPresentes = false;
      } else {
       
        Swal.fire({
          icon: "success",
          title: `Campo ${campo} presente`,
          text: `${campo}: ${docRef[campo]}`,
          timer: 1200,
          showConfirmButton: false
        });    }
    });

   /*  if (todosCamposPresentes) {
      
    } else {
      console.error("❌ Faltan campos en documento_referencia");
    } */

    
  } catch (error) {
    console.error("❌ Error en la prueba completa:", error);
  }
}

// Para ejecutar ambas pruebas:
// 1. AJSprobarNuevaImplementacionAPI() - Solo API
// 2. AJSprobarFlujoCompletoGuardado() - Flujo completo
// 3. AJSprobarProcesamientoReqInterno() - Solo procesamiento REQINTERNO

//================================================================================================================
// FUNCIÓN DE PRUEBA PARA EL PROCESAMIENTO REQINTERNO
//================================================================================================================
async function AJSprobarProcesamientoReqInterno() {
 

  try {
    // Simular datos de documento después de centralización
    const datosDocumentoSimulado = {
      idingresosalidaalm: "_SAL123456789",
      serie: "SAL",
      numero: "001234",
    };

    const responseProceso = {
      success: true,
      data: {
        procesos_ejecutados: [
          "CONTAB_INGRESOSALIDAALM",
          "CENTRALIZA_ALMACENES",
        ],
      },
    };

   

    // Verificar que hay productos seleccionados
    if (
      !productosSeleccionadosCompletos ||
      productosSeleccionadosCompletos.length === 0
    ) {
      console.warn(
        "⚠️ No hay productos seleccionados completos para la prueba"
      );
      console.log(
        "💡 Para probar completamente, primero selecciona productos de un requerimiento"
      );
      return;
    }

    

    // Probar extracción de datos
    
    const productosExtraidos = extraerDatosProductosReqInterno(
      datosDocumentoSimulado
    );

    if (productosExtraidos.length > 0) {
      

      // Mostrar estructura para verificación
     
      const datosParaEnvio = {
        productos: productosExtraidos,
      };
      console.log(JSON.stringify(datosParaEnvio, null, 2));

      console.log("✅ PRUEBA EXITOSA - Datos preparados correctamente");
      console.log(
        "💡 Para ejecutar el procesamiento real, usa: AJSprocesarProductosReqInterno(datosDocumento, responseProceso)"
      );
    } else {
      console.error("❌ No se pudieron extraer productos");
      console.log("🔍 Verificando datos disponibles:");
      console.log(
        "   • productosSeleccionadosCompletos:",
        productosSeleccionadosCompletos
          ? productosSeleccionadosCompletos.length
          : "undefined"
      );
      console.log(
        "   • datosRequerimientoSeleccionado:",
        datosRequerimientoSeleccionado ? "disponible" : "undefined"
      );
      console.log(
        "   • window.datosRequerimientoCompletos:",
        window.datosRequerimientoCompletos ? "disponible" : "undefined"
      );
    }
  } catch (error) {
    console.error("❌ Error en la prueba:", error);
  }

  
}



// Función de utilidad para verificar el estado actual antes del procesamiento
function AJSverificarEstadoParaReqInterno() {
  

  

  if (
    productosSeleccionadosCompletos &&
    productosSeleccionadosCompletos.length > 0
  ) {
    console.log("   • Primer producto:", {
      IDPRODUCTO: productosSeleccionadosCompletos[0].IDPRODUCTO,
      ITEM: productosSeleccionadosCompletos[0].ITEM,
      IDREQINTERNO: productosSeleccionadosCompletos[0].IDREQINTERNO,
    });
  }

  
 
  if (datosRequerimientoSeleccionado) {
    console.log(
      "   • IDREQINTERNO:",
      datosRequerimientoSeleccionado.IDREQINTERNO ||
        datosRequerimientoSeleccionado.id
    );
  }

  const idFromForm = $("#AJSdoc-ref-idreqinterno").val();
  
}

// Para ejecutar las pruebas desde la consola:
// 1. AJSverificarEstadoParaReqInterno() - Verificar estado actual
// 2. AJSprobarProcesamientoReqInterno() - Probar extracción de datos
// 3. AJSprocesarProductosReqInterno(datosDocumento, responseProceso) - Ejecutar procesamiento real

//================================================================================================================
// FUNCIÓN DE DIAGNÓSTICO COMPLETO PARA PROBLEMAS DE GUARDADO
//================================================================================================================
function AJSdiagnosticarProblemaGuardado() {
 

  // 1. Verificar que las funciones existen
  
 

  // 2. Verificar elementos del DOM
  
  const modalSalida = document.getElementById("AJSmodalNuevaSalida");
  const tablaProductos = document.querySelector(
    "#tabla-productos-seleccionados tbody"
  );
  const btnGuardar = document.querySelector(
    'button[onclick="guardarEncabezado()"]'
  );

  

  if (tablaProductos) {
    const filas = tablaProductos.querySelectorAll("tr");
    
  }

  // 3. Verificar datos de requerimiento
  

  // 4. Verificar campos del formulario
  
  const campos = [
    "#id_idempresa",
    "#id_idemisor",
    "#id_periodo",
    "#id_idalmacen",
    "#id_iddocumento",
    "#id_fecha",
    "#id_idresponsable",
    "#id_glosa",
  ];

  campos.forEach((campo) => {
    const elemento = document.querySelector(campo);
    
  });

  // 5. Probar generación de estructura
  
  

  // 6. Verificar conectividad de red
  
  fetch("/almacen/salida-interna-ajs/", { method: "GET" })
    .then((response) => {
      console.log(
        "   • Conectividad API:",
        response.status,
        response.statusText
      );
    })
    .catch((error) => {
      console.error("   • Error de conectividad:", error);
      Swal.fire({
        icon: "error",
        title: "Error de conectividad",
        text: "No se pudo conectar con el servidor. Por favor, verifica tu conexión de red.",
        confirmButtonColor: "#dc3545"
      });
    });

  
}

//================================================================================================================
// FUNCIÓN PARA GENERAR LA ESTRUCTURA FINAL COMPLETA PARA GUARDAR
//================================================================================================================
function AJSgenerarEstructuraFinalParaGuardar() {
  

  try {
    // Recopilar todos los datos
    const encabezado = AJSrecopilarDatosEncabezado();
    const productos = AJSrecopilarProductosParaGuardado();
    const documentoReferencia = AJSrecopilarDatosDocumentoReferencia();

    // Crear la estructura final exacta como la imagen
    const estructuraFinal = {
      encabezado: encabezado,
      productos: productos,
      documento_referencia: documentoReferencia,
    };

    

    
    return estructuraFinal;
  } catch (error) {
    console.error("❌ Error al generar estructura final:", error);
    throw error;
  }
}

//================================================================================================================
// FUNCIÓN PARA GUARDAR SALIDA INTERNA CON AJAX
//================================================================================================================

function AJSguardarSalidaInterna() {
  

  try {
    // Validaciones básicas
    const productosSeleccionados = document.querySelectorAll(
      "#tabla-productos-seleccionados tbody tr"
    );
   

    if (productosSeleccionados.length === 0) {
      Swal.fire({
        icon: "error",
        title: "Error de validación",
        text: "Debe seleccionar al menos un producto",
        confirmButtonColor: "#dc3545",
      });
      return;
    }

    const tieneDocReferencia =
      window.datosRequerimientoCompletos || datosRequerimientoSeleccionado;
    if (!tieneDocReferencia) {
      Swal.fire({
        icon: "error",
        title: "Error de validación",
        text: "Debe seleccionar un documento de referencia",
        confirmButtonColor: "#dc3545",
      });
      return;
    }

    

    // Generar estructura completa con la estructura exacta solicitada
    const datosEnvio = {
      encabezado: AJSrecopilarDatosEncabezado(),
      productos: AJSrecopilarProductosParaGuardado(),
      documento_referencia: AJSrecopilarDatosDocumentoReferencia(),
    };

    

    // Mostrar loading con Swal
    Swal.fire({
      title: "Guardando...",
      text: "Procesando salida interna",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    // Enviar datos al servidor usando el mismo patrón
    $.ajax({
      url: "/almacen/salida-interna-ajs/",
      type: "POST",
      data: JSON.stringify(datosEnvio),
      contentType: "application/json",
      headers: {
        "X-CSRFToken": AJSgetCookie("csrftoken"),
      },
      success: function (response) {
        

        if (response.status === "success" || response.success) {
          // ✅ PASO 1: Salida interna creada exitosamente
         

          // ✅ PASO 2: Procesar contabilización y centralización automáticamente
          if (response.data && response.data.idingresosalidaalm) {
            const idIngresosAlidaAlm = response.data.idingresosalidaalm;
            

            // Mostrar loading para el proceso adicional
            Swal.fire({
              title: "Procesando...",
              html: `
                <div class="text-center">
                  <p>✅ Salida interna creada exitosamente</p>
                  <p>🔄 Contabilizando y centralizando...</p>
                  <div class="spinner-border text-primary mt-2" role="status">
                    <span class="sr-only">Procesando...</span>
                  </div>
                </div>
              `,
              allowOutsideClick: false,
              showConfirmButton: false,
            });

            // Llamar al endpoint de contabilización y centralización
            AJSprocesarContabilizacionYCentralizacion(
              idIngresosAlidaAlm,
              response.data
            );
          } else {
            // Si no hay ID, mostrar éxito básico
            AJSmostrarExitoBasico(response);
          }
        } else {
          Swal.fire({
            icon: "error",
            title: "Error",
            text:
              response.message ||
              "Ocurrió un error al guardar la salida interna",
            confirmButtonColor: "#dc3545",
          });
        }
      },
      error: function (xhr, status, error) {
        console.error("❌ ERROR AL GUARDAR SALIDA INTERNA:", xhr.responseText);
        let mensajeError = "Ocurrió un error al conectar con el servidor";

        try {
          if (xhr.responseText) {
            const respuesta = JSON.parse(xhr.responseText);
            mensajeError = respuesta.message || mensajeError;
          }
        } catch (e) {
          console.error("Error al parsear respuesta:", e);
          mensajeError = `Error ${xhr.status}: ${error}`;
        }

        Swal.fire({
          icon: "error",
          title: "Error de conexión",
          text: mensajeError,
          confirmButtonColor: "#dc3545",
        });
      },
    });
  } catch (error) {
    console.error("❌ ERROR GENERAL:", error);
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "Error al procesar el guardado: " + error.message,
      confirmButtonColor: "#dc3545",
    });
  }
}

//================================================================================================================
// FUNCIONES PARA PROCESAMIENTO DE PRODUCTOS REQINTERNO (VERSION SIMPLIFICADA)
//================================================================================================================

// ✅ FUNCIÓN SIMPLE PARA RECUPERAR DATOS ORIGINALES PARA REQINTERNO
function AJSrecuperarDatosOriginalesParaReqInterno(
  datosDocumento,
  responseProceso
) {
  

  try {
    // ✅ PASO 1: RECOPILAR DATOS BASE
    
    const encabezadoBase = AJSrecopilarDatosEncabezado();
    const productosBase = AJSrecopilarProductosParaGuardado();
    const documentoReferenciaBase = AJSrecopilarDatosDocumentoReferencia();

    

    // ✅ PASO 2: CONSTRUIR ESTRUCTURA COMPLETA PARA REQINTERNO
    

    // ENCABEZADO COMPLETO
    const encabezado = {
      IDEMPRESA: encabezadoBase.IDEMPRESA || "001",
      IDEMISOR: encabezadoBase.IDEMISOR || encabezadoBase.IDEMPRESA || "001",
      PERIODO: encabezadoBase.PERIODO,
      IDALMACEN: encabezadoBase.IDALMACEN || "001",
      IDDOCUMENTO: "SAL",
      FECHA: encabezadoBase.FECHA,
      IDRESPONSABLE: encabezadoBase.IDRESPONSABLE,
      GLOSA: encabezadoBase.GLOSA || "",
      IDMONEDA: encabezadoBase.IDMONEDA || "01",
      TCAMBIO: encabezadoBase.TCAMBIO || 3.759,
      IDMOTIVO: encabezadoBase.IDMOTIVO || "SCC",
      IDSUCURSAL: encabezadoBase.IDSUCURSAL || "001",
      IDUSUARIO: encabezadoBase.IDUSUARIO || "ADMINISTRADOR",
    };

    // PRODUCTOS COMPLETOS CON ESTRUCTURA PARA REQINTERNO
    const productos = productosBase.map((producto, index) => {
      return {
        IDEMPRESA: encabezado.IDEMPRESA,
        IDPRODUCTO: String(producto.IDPRODUCTO).trim(),
        DESCRIPCION: String(producto.DESCRIPCION || "").trim(),
        IDMEDIDA: String(producto.IDMEDIDA || "").trim(),
        IDCONSUMIDOR: String(producto.IDCONSUMIDOR || "").trim(),
        CANTIDAD: producto.CANTIDAD_PARA_SALIR || producto.CANTIDAD || 0,
        IDREFERENCIA: String(documentoReferenciaBase.IDREFERENCIA).trim(),
        ITEMREF: String(producto.ITEM).trim(),
        TABLAREF: "REQINTERNO",
        ITEM: String(producto.ITEM).trim(),
      };
    });

    // DOCUMENTO REFERENCIA COMPLETO
    const documento_referencia = {
      IDEMPRESA: encabezado.IDEMPRESA,
      IDREFERENCIA: String(documentoReferenciaBase.IDREFERENCIA).trim(),
      TABLAREFERENCIA: "REQINTERNO",
      IDDOCUMENTO: documentoReferenciaBase.IDDOCUMENTO || "REQ",
      SERIE: documentoReferenciaBase.SERIE || "",
      NUMERO: documentoReferenciaBase.NUMERO || "",
      FECHA: documentoReferenciaBase.FECHA || "",
      IDRESPONSABLE: documentoReferenciaBase.IDRESPONSABLE || "",
      GLOSA: documentoReferenciaBase.GLOSA || "",
      TOTAL: documentoReferenciaBase.TOTAL || 0,
    };

    // ✅ PASO 3: ESTRUCTURA FINAL COMPLETA CON IDINGRESOSALIDAALM
    const estructuraCompleta = {
      encabezado: encabezado,
      productos: productos,
      documento_referencia: documento_referencia,
      idingresosalidaalm: String(datosDocumento.idingresosalidaalm).trim(),
    };

    

   

    // ✅ VALIDAR QUE TENEMOS TODOS LOS DATOS NECESARIOS
    if (!estructuraCompleta.encabezado) {

      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo recuperar encabezado",
        confirmButtonColor: "#dc3545"
      });    return null;
    }

    if (
      !estructuraCompleta.productos ||
      estructuraCompleta.productos.length === 0
    ) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudieron recuperar productos",
        confirmButtonColor: "#dc3545"
      });
      return null;
    }

    if (!estructuraCompleta.documento_referencia) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo recuperar documento de referencia",
        confirmButtonColor: "#dc3545"
      });
      return null;
    }

    if (!estructuraCompleta.idingresosalidaalm) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se encontró IDINGRESOSALIDAALM",
        confirmButtonColor: "#dc3545"
      });
      return null;
    }

    
    AJSenviarEstructuraAApiReqInterno(
      estructuraCompleta,
      datosDocumento,
      responseProceso
    );

    return estructuraCompleta;
  } catch (error) {
    console.error("❌ Error al recuperar datos originales:", error);
    
    return null;
  }
}

// ✅ FUNCIÓN PARA ENVIAR ESTRUCTURA COMPLETA A LA API DE REQINTERNO
function AJSenviarEstructuraAApiReqInterno(
  estructuraCompleta,
  datosDocumento,
  responseProceso
) {
  console.log("📡 Enviando estructura completa a API REQINTERNO...");
  
  // Definir endpoint correcto
  const endpoint = "/almacen/api/procesar-requerimiento-ajs/";
  console.log(`🔗 Endpoint: ${endpoint}`);

  // Realizar petición AJAX al endpoint
  $.ajax({
    url: endpoint,
    type: "POST",
    data: JSON.stringify(estructuraCompleta),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": AJSgetCookie("csrftoken"),
    },
    beforeSend: function () {
      
    },
    success: function (response) {
      

      if (response.status === "success" || response.success) {
        

        

        // Mostrar modal de éxito
        Swal.fire({
          icon: "success",
          title: "¡Salida Procesada Exitosamente!",
          html: `
            <div class="text-center" style="padding: 10px;">
              <div class="success-container" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; padding: 20px; margin: 10px 0;">
                <div class="success-header" style="margin-bottom: 15px;">
                  <i class="fas fa-check-circle" style="color: #28a745; font-size: 2.5em; margin-bottom: 10px;"></i>
                  <h4 style="color: #2c3e50; margin: 0; font-weight: 600;">Operación Completada</h4>
                </div>
                
                <div class="success-details" style="text-align: left; background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                  <div class="detail-row" style="display: flex; align-items: center; margin-bottom: 8px; padding: 5px 0;">
                    <i class="fas fa-file-alt" style="color: #28a745; width: 20px; margin-right: 10px;"></i>
                    <span style="color: #495057; font-size: 14px;">Documento creado y centralizado</span>
                    <i class="fas fa-check" style="color: #28a745; margin-left: auto;"></i>
                  </div>
                  
                  <div class="detail-row" style="display: flex; align-items: center; margin-bottom: 12px; padding: 5px 0;">
                    <i class="fas fa-cogs" style="color: #28a745; width: 20px; margin-right: 10px;"></i>
                    <span style="color: #495057; font-size: 14px;">REQINTERNO procesado</span>
                    <i class="fas fa-check" style="color: #28a745; margin-left: auto;"></i>
                  </div>
                  
                  <div style="border-top: 1px solid #dee2e6; padding-top: 12px;">
                    <div class="info-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
                      <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; text-align: center;">
                        <div style="color: #6c757d; font-weight: 500;">ID Documento</div>
                        <div style="color: #2c3e50; font-weight: 600; font-family: monospace;">${datosDocumento.idingresosalidaalm}</div>
                      </div>
                      <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; text-align: center;">
                        <div style="color: #6c757d; font-weight: 500;">Productos</div>
                        <div style="color: #2c3e50; font-weight: 600;">${estructuraCompleta.productos.length}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          `,
          showConfirmButton: true,
          confirmButtonColor: "#28a745",
          confirmButtonText: '<i class="fas fa-check"></i> Entendido',
          buttonsStyling: true,
          customClass: {
            popup: 'swal-custom-success',
            confirmButton: 'btn btn-success'
          },
          width: '500px',
          padding: '20px'
        }).then((result) => {
          if (result.isConfirmed) {
            AJSfinalizarProceso();
          }
        });

        // cerrar modal de registro de salidas.
      } else {
        console.error("⚠️ API respondió pero con estado de error");
        console.log(
          "📋 Mensaje de error:",
          response.message || "Error desconocido"
        );

        Swal.fire({
          icon: "warning",
          title: "Respuesta con advertencias",
          text: response.message || "La API respondió pero reportó problemas",
          confirmButtonColor: "#ffc107",
        });
      }
    },
    error: function (xhr, status, error) {
     

      let mensajeError = "Error al procesar REQINTERNO";

      try {
        if (xhr.responseText) {
          const respuestaError = JSON.parse(xhr.responseText);
          mensajeError =
            respuestaError.message || respuestaError.error || mensajeError;
          console.error("📊 Error parseado:", respuestaError);
        }
      } catch (e) {
        console.error("📊 No se pudo parsear el error:", e);
        mensajeError = `Error ${xhr.status}: ${error}`;
      }

      // Mostrar modal de error
      Swal.fire({
        icon: "error",
        title: "Error en REQINTERNO",
        html: `
          <div class="text-center">
            <p>❌ Error al procesar requerimiento interno</p>
            <hr>
            <p><strong>Error:</strong> ${mensajeError}</p>
            <p><strong>Código:</strong> ${xhr.status}</p>
          </div>
        `,
        confirmButtonColor: "#dc3545",
        confirmButtonText: "Entendido",
      });
    },
    timeout: 60000, // 60 segundos timeout
  });
}

// Función principal para procesar productos REQINTERNO después de centralización
function AJSprocesarProductosReqInterno(datosDocumento, responseProceso) {
 
  try {
    // ✅ RECUPERAR DATOS Y ENVIAR AUTOMÁTICAMENTE A LA API
    console.log("🚀 ===== INICIANDO PROCESAMIENTO REQINTERNO =====");

    const datosRecuperados = AJSrecuperarDatosOriginalesParaReqInterno(
      datosDocumento,
      responseProceso
    );

    if (!datosRecuperados) {
      console.error("❌ No se pudieron recuperar los datos originales");
      AJSmostrarErrorReqInterno(
        datosDocumento,
        responseProceso,
        "No se pudieron recuperar los datos necesarios para procesar REQINTERNO"
      );
      return;
    }

    

    // La función AJSrecuperarDatosOriginalesParaReqInterno ya se encarga de enviar los datos
    // No necesitamos hacer nada más aquí, todo el flujo está automatizado
  } catch (error) {
    console.error("❌ Error en AJSprocesarProductosReqInterno:", error);
    AJSmostrarErrorReqInterno(
      datosDocumento,
      responseProceso,
      "Error en el procesamiento: " + error.message
    );
  }
}

// ✅ FUNCIÓN MEJORADA PARA OBTENER IDREFERENCIA CON MÁS FUENTES
function AJSobtenerIdReferenciaRequerimientoMejorado() {
  console.log("🔍 Intentando obtener IDREFERENCIA desde múltiples fuentes...");

  // Fuente 1: window.datosRequerimientoCompletos
  if (window.datosRequerimientoCompletos?.IDREQINTERNO) {
    console.log(
      "✅ IDREFERENCIA encontrado en window.datosRequerimientoCompletos"
    );
    return window.datosRequerimientoCompletos.IDREQINTERNO;
  }

  // Fuente 2: datosRequerimientoSeleccionado.IDREQINTERNO
  if (datosRequerimientoSeleccionado?.IDREQINTERNO) {
    
    return datosRequerimientoSeleccionado.IDREQINTERNO;
  }

  // Fuente 3: datosRequerimientoSeleccionado.id
  if (datosRequerimientoSeleccionado?.id) {
    
    return datosRequerimientoSeleccionado.id;
  }

  // Fuente 4: Campo del formulario
  const idFromForm = $("#AJSdoc-ref-idreqinterno").val();
  if (idFromForm && idFromForm.trim() !== "") {
    console.log("✅ IDREFERENCIA encontrado en campo del formulario");
    return idFromForm.trim();
  }

  // Fuente 5: Desde productos seleccionados (si tienen IDREQINTERNO)
  if (productosSeleccionadosCompletos?.length > 0) {
    const idDesdeProducto = productosSeleccionadosCompletos[0]?.IDREQINTERNO;
    if (idDesdeProducto) {
      console.log("✅ IDREFERENCIA encontrado en productos seleccionados");
      return idDesdeProducto;
    }
  }

  console.error(
    "❌ No se pudo obtener IDREFERENCIA de ninguna fuente disponible"
  );
  return null;
}

// ✅ NUEVA FUNCIÓN DE DIAGNÓSTICO COMPLETO
function AJSdiagnosticarEstadoParaReqInterno() {
  console.log("🔍 ===== EJECUTANDO DIAGNÓSTICO COMPLETO =====");

  const diagnostico = {
    todoListo: true,
    problemas: [],
    detalles: {},
  };

  // Verificar productos seleccionados
  diagnostico.detalles.productosSeleccionados = {
    disponible: !!productosSeleccionadosCompletos,
    cantidad: productosSeleccionadosCompletos?.length || 0,
    estructura: productosSeleccionadosCompletos?.[0] || null,
  };

  if (
    !productosSeleccionadosCompletos ||
    productosSeleccionadosCompletos.length === 0
  ) {
    diagnostico.problemas.push("No hay productos seleccionados");
    diagnostico.todoListo = false;
  }

  // Verificar datos del requerimiento
  diagnostico.detalles.datosRequerimiento = {
    windowDatos: !!window.datosRequerimientoCompletos,
    datosSeleccionado: !!datosRequerimientoSeleccionado,
    campoFormulario: $("#AJSdoc-ref-idreqinterno").val() || null,
  };

  const idreferencia = AJSobtenerIdReferenciaRequerimientoMejorado();
  if (!idreferencia) {
    diagnostico.problemas.push("No se puede obtener IDREFERENCIA");
    diagnostico.todoListo = false;
  }

  // Verificar datos de productos completos de API
  diagnostico.detalles.datosAPI = {
    disponible: !!datosProductosCompletosAPI,
    cantidad: datosProductosCompletosAPI?.length || 0,
  };

  console.log("📊 Resultado del diagnóstico:", diagnostico);
  return diagnostico;
}

// ✅ NUEVA FUNCIÓN DE VALIDACIÓN FINAL DE DATOS
function AJSvalidarDatosParaAPI(productos) {
  

  const validacion = {
    valido: true,
    errores: [],
  };

  if (!productos || productos.length === 0) {
    validacion.errores.push("Lista de productos vacía");
    validacion.valido = false;
    return validacion;
  }

  const camposRequeridos = [
    "IDPRODUCTO",
    "ITEMREF",
    "IDINGRESOSALIDAALM",
    "IDREFERENCIA",
  ];

  productos.forEach((producto, index) => {
    camposRequeridos.forEach((campo) => {
      if (!producto[campo] || String(producto[campo]).trim() === "") {
        validacion.errores.push(
          `Producto ${index + 1}: Campo ${campo} vacío o faltante`
        );
        validacion.valido = false;
      }
    });
  });

  
  return validacion;
}

// Función para obtener IDREFERENCIA del requerimiento seleccionado
function AJSobtenerIdReferenciaRequerimiento() {
  // Intentar obtener de varias fuentes en orden de prioridad
  if (
    window.datosRequerimientoCompletos &&
    window.datosRequerimientoCompletos.IDREQINTERNO
  ) {
    return window.datosRequerimientoCompletos.IDREQINTERNO;
  }

  if (
    datosRequerimientoSeleccionado &&
    datosRequerimientoSeleccionado.IDREQINTERNO
  ) {
    return datosRequerimientoSeleccionado.IDREQINTERNO;
  }

  if (datosRequerimientoSeleccionado && datosRequerimientoSeleccionado.id) {
    return datosRequerimientoSeleccionado.id;
  }

  // Como último recurso, intentar obtener del campo del formulario
  const idFromForm = $("#AJSdoc-ref-idreqinterno").val();
  if (idFromForm) {
    return idFromForm;
  }

  console.warn("⚠️ No se pudo obtener IDREFERENCIA de ninguna fuente");
  return null;
}

// ✅ FUNCIÓN MEJORADA PARA ENVIAR PRODUCTOS A LA API CON MEJOR MANEJO DE ERRORES
function AJSenviarProductosReqInternoAPI(
  productos,
  datosDocumento,
  responseProceso
) {
  

  const datosEnvio = {
    productos: productos,
  };

 
  // Agregar timeout para el proceso
  const timeoutId = setTimeout(() => {
    console.log("⏰ Timeout del procesamiento REQINTERNO (60 segundos)");
    AJSmostrarTimeoutReqInterno(datosDocumento, responseProceso);
  }, 60000); // 60 segundos timeout

  // ✅ VALIDACIÓN PREVIA AL ENVÍO
  if (!productos || productos.length === 0) {
    console.error("❌ No hay productos para enviar");
    clearTimeout(timeoutId);
    AJSmostrarErrorReqInterno(
      datosDocumento,
      responseProceso,
      "No hay productos para procesar"
    );
    return;
  }

  // ✅ INFORMACIÓN DEL ENDPOINT
  const endpoint = "/almacen/api/procesar-requerimiento-ajs/";
  

  // Realizar petición AJAX al endpoint
  $.ajax({
    url: endpoint,
    type: "POST",
    data: JSON.stringify(datosEnvio),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": AJSgetCookie("csrftoken"),
    },
    
    success: function (response, textStatus, xhr) {
      

      // Limpiar timeout
      clearTimeout(timeoutId);

      // ✅ VALIDAR ESTRUCTURA DE LA RESPUESTA
      if (!response) {
        
        AJSmostrarErrorReqInterno(
          datosDocumento,
          responseProceso,
          "Respuesta vacía del servidor"
        );
        return;
      }

      if (response.status === "success") {
        
        AJSmostrarExitoFinalCompleto(datosDocumento, responseProceso, response);
      } else if (response.status === "error") {
        console.error("❌ Error reportado por el backend:", response.message);
        console.error("📋 Errores adicionales:", response.errors);
        AJSmostrarErrorReqInterno(
          datosDocumento,
          responseProceso,
          response.message || "Error en procesamiento REQINTERNO"
        );
      } else {
        console.error("❌ Estado de respuesta no reconocido:", response.status);
        AJSmostrarErrorReqInterno(
          datosDocumento,
          responseProceso,
          `Estado no reconocido: ${response.status}`
        );
      }
    },
    error: function (xhr, textStatus, errorThrown) {
      

      // Limpiar timeout
      clearTimeout(timeoutId);

      let mensajeError = "Error de conexión en el procesamiento REQINTERNO";
      let detallesError = "";

      // ✅ ANÁLISIS DETALLADO DEL ERROR
      try {
        if (xhr.responseText) {
          const respuesta = JSON.parse(xhr.responseText);
         
          Swal.fire({
            icon: "error",
            title: "Error en el procesamiento",
            html: `
              <div class="text-left">
                <p><strong>❌ Error al procesar requerimiento interno</strong></p>
                <hr>
                <p><strong>Mensaje:</strong> ${mensajeError}</p>
                <p><strong>Detalles:</strong> ${detallesError}</p>
                <p><small class="text-muted">El documento fue creado y procesado correctamente, pero hubo un error al actualizar los estados del requerimiento interno.</small></p>
              </div>
            `,
            confirmButtonColor: "#dc3545",
            confirmButtonText: "Entendido",
            width: "600px",
          });
          mensajeError = respuesta.message || respuesta.error || mensajeError;

          if (respuesta.errors) {
            detallesError = ` Detalles: ${
              Array.isArray(respuesta.errors)
                ? respuesta.errors.join(", ")
                : respuesta.errors


            }`;
          }

          if (respuesta.code) {
            detallesError += ` (Código: ${respuesta.code})`;
          }
        }
      } catch (parseError) {
        console.error("❌ Error al parsear respuesta de error:", parseError);

        // Fallback basado en status HTTP
        switch (xhr.status) {
          case 400:
            mensajeError = "Datos inválidos enviados al servidor (HTTP 400)";
            break;
          case 401:
            mensajeError = "No autorizado - verifique su sesión (HTTP 401)";
            break;
          case 403:
            mensajeError = "Acceso prohibido (HTTP 403)";
            break;
          case 404:
            mensajeError = "Endpoint no encontrado (HTTP 404)";
            break;
          case 500:
            mensajeError = "Error interno del servidor (HTTP 500)";
            break;
          case 0:
            mensajeError = "Error de conexión - verifique su red";
            break;
          default:
            mensajeError = `Error HTTP ${xhr.status}: ${errorThrown}`;
        }
      }

      const mensajeFinal = mensajeError + detallesError;
      console.error("📋 Mensaje de error final:", mensajeFinal);

      AJSmostrarErrorReqInterno(datosDocumento, responseProceso, mensajeFinal);
    },
    
  });
}

// ✅ FUNCIÓN DE DEBUGGING MANUAL PARA LA CONSOLA
window.debugReqInterno = function () {
 

  const debug = {
    timestamp: new Date().toISOString(),
    variables_globales: {
      productosSeleccionadosCompletos: {
        definida: typeof productosSeleccionadosCompletos !== "undefined",
        cantidad: productosSeleccionadosCompletos?.length || 0,
        primer_producto: productosSeleccionadosCompletos?.[0] || null,
      },
      datosProductosCompletosAPI: {
        definida: typeof datosProductosCompletosAPI !== "undefined",
        cantidad: datosProductosCompletosAPI?.length || 0,
        primer_producto: datosProductosCompletosAPI?.[0] || null,
      },
      datosRequerimientoSeleccionado: {
        definida: typeof datosRequerimientoSeleccionado !== "undefined",
        tiene_datos: !!datosRequerimientoSeleccionado,
        contenido: datosRequerimientoSeleccionado,
      },
      window_datosRequerimientoCompletos: {
        definida: typeof window.datosRequerimientoCompletos !== "undefined",
        tiene_datos: !!window.datosRequerimientoCompletos,
        contenido: window.datosRequerimientoCompletos,
      },
    },
    elementos_dom: {
      campo_idreqinterno: {
        existe: $("#AJSdoc-ref-idreqinterno").length > 0,
        valor: $("#AJSdoc-ref-idreqinterno").val(),
        visible: $("#AJSdoc-ref-idreqinterno").is(":visible"),
      },
      checkboxes_productos: {
        total: $(".chk-producto").length,
        seleccionados: $(".chk-producto:checked").length,
      },
    },
    diagnostico_automatico: null,
    simulacion_extraccion: null,
  };

  // Ejecutar diagnóstico automático si está disponible
  if (typeof AJSdiagnosticarEstadoParaReqInterno === "function") {
    debug.diagnostico_automatico = AJSdiagnosticarEstadoParaReqInterno();
  }

  // Simular extracción de datos con datos de prueba
  if (
    productosSeleccionadosCompletos &&
    productosSeleccionadosCompletos.length > 0
  ) {
    const datosDocumentoPrueba = {
      idingresosalidaalm: "_TEST_IDINGRESOSALIDAALM_12345",
    };

    try {
      debug.simulacion_extraccion =
        extraerDatosProductosReqInterno(datosDocumentoPrueba);
    } catch (error) {
      debug.simulacion_extraccion = { error: error.message };
    }
  }

  

  // También retornar para uso programático
  return debug;
};

// ✅ FUNCIÓN PARA EJECUTAR PRUEBA COMPLETA DESDE LA CONSOLA
window.probarFlujoPocesaQueRrequirimiento = function () {
  

  // 1. Verificar estado inicial
  const debugInicial = window.debugReqInterno();
  

  // 2. Verificar si hay datos suficientes para la prueba
  if (
    !productosSeleccionadosCompletos ||
    productosSeleccionadosCompletos.length === 0
  ) {
    console.error("❌ No hay productos seleccionados para la prueba");
    return {
      exito: false,
      mensaje: "No hay productos seleccionados",
    };
  }

  // 3. Simular datos del documento
  const datosDocumentoPrueba = {
    idingresosalidaalm: "_PRUEBA_" + Date.now(),
    serie: "001",
    numero: "000001",
  };

  // 4. Simular response del proceso
  const responseProcesoPrueba = {
    status: "success",
    message: "Documento creado exitosamente para prueba",
  };

 

  try {
    // 5. Ejecutar el flujo completo
    AJSprocesarProductosReqInterno(datosDocumentoPrueba, responseProcesoPrueba);

    return {
      exito: true,
      mensaje:
        "Prueba iniciada correctamente - revise la consola y los modales",
    };
  } catch (error) {
    console.error("❌ Error en la prueba:", error);
    return {
      exito: false,
      mensaje: "Error en la prueba: " + error.message,
      error: error,
    };
  }
};



// Función para mostrar éxito final completo (documento + centralización + REQINTERNO)
function AJSmostrarExitoFinalCompleto(
  datosDocumento,
  responseProceso,
  responseReqInterno
) {
  

  const productosActualizados =
    responseReqInterno.data?.productos_procesados || 0;
  const tiempoProceso = responseReqInterno.data?.tiempo_proceso || 0;

  Swal.fire({
    icon: "success",
    title: "¡Proceso Completado Totalmente!",
    html: `
      <div class="text-left">
        <p><strong>📄 Documento creado:</strong></p>
        <ul>
          <li><strong>ID:</strong> ${datosDocumento.idingresosalidaalm}</li>
          <li><strong>Serie:</strong> ${datosDocumento.serie || "N/A"}</li>
          <li><strong>Número:</strong> ${datosDocumento.numero || "N/A"}</li>
        </ul>
        <hr>
        <p><strong>🔄 Procesos ejecutados:</strong></p>
        <ul>
          <li>✅ Contabilizado exitosamente</li>
          <li>✅ Centralizado exitosamente</li>
          <li>✅ Estados REQINTERNO actualizados</li>
        </ul>
        <hr>
        <p><strong>📊 Productos REQINTERNO:</strong></p>
        <ul>
          <li><strong>Productos procesados:</strong> ${productosActualizados}</li>
          <li><strong>Tiempo de proceso:</strong> ${tiempoProceso}s</li>
        </ul>
        <p class="text-success"><strong>🎉 Proceso completado exitosamente al 100%</strong></p>
      </div>
    `,
    confirmButtonColor: "#28a745",
    confirmButtonText: "¡Excelente!",
    width: "600px",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

// Función para mostrar éxito sin procesamiento REQINTERNO
function AJSmostrarExitoFinalSinReqInterno(datosDocumento, responseProceso) {
 

  Swal.fire({
    icon: "success",
    title: "¡Proceso Completo!",
    html: `
      <div class="text-left">
        <p><strong>📄 Documento creado:</strong></p>
        <ul>
          <li><strong>ID:</strong> ${datosDocumento.idingresosalidaalm}</li>
          <li><strong>Serie:</strong> ${datosDocumento.serie || "N/A"}</li>
          <li><strong>Número:</strong> ${datosDocumento.numero || "N/A"}</li>
        </ul>
        <hr>
        <p><strong>🔄 Procesos ejecutados:</strong></p>
        <ul>
          <li>✅ Contabilizado exitosamente</li>
          <li>✅ Centralizado exitosamente</li>
        </ul>
        <p class="text-info"><strong>ℹ️ No se requiere procesamiento REQINTERNO adicional</strong></p>
      </div>
    `,
    confirmButtonColor: "#28a745",
    confirmButtonText: "Entendido",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

// Función para mostrar error en procesamiento REQINTERNO
function AJSmostrarErrorReqInterno(datosDocumento, responseProceso, mensajeError) {
  

  Swal.fire({
    icon: "warning",
    title: "Documento Creado - Error REQINTERNO",
    html: `
      <div class="text-left">
        <p><strong>✅ Documento creado exitosamente:</strong></p>
        <ul>
          <li><strong>ID:</strong> ${datosDocumento.idingresosalidaalm}</li>
          <li><strong>Serie:</strong> ${datosDocumento.serie || "N/A"}</li>
          <li><strong>Número:</strong> ${datosDocumento.numero || "N/A"}</li>
        </ul>
        <hr>
        <p><strong>🔄 Procesos ejecutados:</strong></p>
        <ul>
          <li>✅ Contabilizado exitosamente</li>
          <li>✅ Centralizado exitosamente</li>
          <li>❌ Error en actualización REQINTERNO</li>
        </ul>
        <hr>
        <p><strong>⚠️ Error REQINTERNO:</strong></p>
        <p class="text-danger">${mensajeError}</p>
        <p><small class="text-muted">El documento fue creado y procesado correctamente, pero hubo un error al actualizar los estados del requerimiento interno. Puede procesarlo manualmente más tarde.</small></p>
      </div>
    `,
    confirmButtonColor: "#ffc107",
    confirmButtonText: "Entendido",
    width: "600px",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

// Función para manejar timeout del procesamiento REQINTERNO
function AJSmostrarTimeoutReqInterno(datosDocumento, responseProceso) {
 

  Swal.fire({
    icon: "warning",
    title: "Proceso REQINTERNO Demorado",
    html: `
      <div class="text-left">
        <p><strong>✅ Documento creado exitosamente:</strong></p>
        <ul>
          <li><strong>ID:</strong> ${datosDocumento.idingresosalidaalm}</li>
          <li><strong>Serie:</strong> ${datosDocumento.serie || "N/A"}</li>
          <li><strong>Número:</strong> ${datosDocumento.numero || "N/A"}</li>
        </ul>
        <hr>
        <p><strong>🔄 Procesos ejecutados:</strong></p>
        <ul>
          <li>✅ Contabilizado exitosamente</li>
          <li>✅ Centralizado exitosamente</li>
          <li>⏰ Actualización REQINTERNO en progreso...</li>
        </ul>
        <p><strong>⏰ La actualización de estados REQINTERNO está tomando más tiempo del esperado.</strong></p>
        <p><small class="text-muted">El documento fue creado y procesado correctamente. La actualización REQINTERNO puede continuar en segundo plano.</small></p>
      </div>
    `,
    confirmButtonColor: "#ffc107",
    confirmButtonText: "Entendido",
    width: "600px",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

//================================================================================================================
// FUNCIONES PARA CONTABILIZACIÓN Y CENTRALIZACIÓN AUTOMÁTICA
//================================================================================================================

// Función para procesar contabilización y centralización automáticamente
function AJSprocesarContabilizacionYCentralizacion(
  idIngresosAlidaAlm,
  datosDocumento
) {
  

  // Preparar datos para el endpoint
  const datosEnvio = {
    IDINGRESOSALIDAALM: idIngresosAlidaAlm,
    IDEMPRESA: "001",
    VENTANA: "EDT_SALIDAS",
    IDEMISOR: "001",
  };

  console.log("📤 Enviando datos al endpoint:", datosEnvio);

  // Agregar timeout para el proceso
  const timeoutId = setTimeout(() => {
    console.log("⏰ Timeout del proceso - tomando demasiado tiempo");
    AJSmostrarTimeoutProceso(datosDocumento);
  }, 30000); // 30 segundos timeout

  // Llamar al endpoint de contabilización y centralización
  $.ajax({
    url: "/almacen/salida-interna-procesar-ajs/",
    type: "POST",
    data: JSON.stringify(datosEnvio),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": AJSgetCookie("csrftoken"),
    },
    success: function (response) {
      console.log("✅ RESPUESTA DEL PROCESO:", response);

      // Limpiar timeout
      clearTimeout(timeoutId);

      if (response.success) {
        // Proceso exitoso
        AJSmostrarExitoCompleto(datosDocumento, response);
      } else {
        // Proceso falló
        AJSmostrarErrorProceso(datosDocumento, response);
      }
    },
    error: function (xhr, status, error) {
      console.error("❌ ERROR EN EL PROCESO:", xhr.responseText);

      // Limpiar timeout
      clearTimeout(timeoutId);

      let mensajeError = "Error de conexión en el proceso de contabilización";
      try {
        if (xhr.responseText) {
          const respuesta = JSON.parse(xhr.responseText);
          mensajeError = respuesta.error || mensajeError;
        }
      } catch (e) {
        console.error("Error al parsear respuesta:", e);
        mensajeError = `Error ${xhr.status}: ${error}`;
      }

      AJSmostrarErrorProceso(datosDocumento, { error: mensajeError });
    },
  });
}

// Función para mostrar éxito completo (documento creado + proceso exitoso)
function AJSmostrarExitoCompleto(datosDocumento, responseProceso) {
  console.log("🎉 PROCESO COMPLETO EXITOSO");

  // Determinar qué procesos se ejecutaron
  const procesosEjecutados = responseProceso.data?.procesos_ejecutados || [];
  let mensajeProcesos = "";

  if (
    procesosEjecutados.includes("CONTAB_INGRESOSALIDAALM") &&
    procesosEjecutados.includes("CENTRALIZA_ALMACENES")
  ) {
    mensajeProcesos = "✅ Contabilizado y centralizado exitosamente";

    // ✅ PASO ADICIONAL: Procesar productos REQINTERNO después de centralización exitosa
    console.log("🔄 Iniciando procesamiento de productos REQINTERNO...");
    AJSprocesarProductosReqInterno(datosDocumento, responseProceso);
    return; // Salir aquí para que el proceso continúe en la función de REQINTERNO
  } else if (procesosEjecutados.includes("CONTAB_INGRESOSALIDAALM")) {
    mensajeProcesos =
      "✅ Contabilizado exitosamente<br>⚠️ Centralización pendiente";
  } else {
    mensajeProcesos = "⚠️ Procesos adicionales pendientes";
  }

  // Mostrar resultado sin procesamiento REQINTERNO (solo cuando no hay centralización completa)
  Swal.fire({
    icon: "success",
    title: "¡Proceso Completo!",
    html: `
      <div class="text-left">
        <p><strong>📄 Documento creado:</strong></p>
        <ul>
          <li><strong>ID:</strong> ${datosDocumento.idingresosalidaalm}</li>
          <li><strong>Serie:</strong> ${datosDocumento.serie || "N/A"}</li>
          <li><strong>Número:</strong> ${datosDocumento.numero || "N/A"}</li>
        </ul>
        <hr>
        <p><strong>🔄 Procesos ejecutados:</strong></p>
        <p>${mensajeProcesos}</p>
      </div>
    `,
    confirmButtonColor: "#28a745",
    confirmButtonText: "Entendido",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

// Función para mostrar error en el proceso (documento creado pero proceso falló)
function AJSmostrarErrorProceso(datosDocumento, responseProceso) {
  console.log("⚠️ DOCUMENTO CREADO PERO PROCESO FALLÓ");

  Swal.fire({
    icon: "warning",
    title: "Documento Creado",
    html: `
      <div class="text-left">
        <p><strong>✅ Documento creado exitosamente:</strong></p>
        <ul>
          <li><strong>ID:</strong> ${datosDocumento.idingresosalidaalm}</li>
          <li><strong>Serie:</strong> ${datosDocumento.serie || "N/A"}</li>
          <li><strong>Número:</strong> ${datosDocumento.numero || "N/A"}</li>
        </ul>
        <hr>
        <p><strong>⚠️ Proceso adicional:</strong></p>
        <p class="text-danger">${
          responseProceso.error || "Error en contabilización/centralización"
        }</p>
        <p><small class="text-muted">El documento fue creado correctamente, pero deberá procesar manualmente la contabilización y centralización.</small></p>
      </div>
    `,
    confirmButtonColor: "#ffc107",
    confirmButtonText: "Entendido",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

// Función para mostrar éxito básico (cuando no hay ID del documento)
function AJSmostrarExitoBasico(response) {
  

  Swal.fire({
    icon: "success",
    title: "¡Éxito!",
    text: response.message || "La salida interna se ha guardado correctamente",
    confirmButtonColor: "#28a745",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

// Función para manejar timeout del proceso
function AJSmostrarTimeoutProceso(datosDocumento) {
  

  Swal.fire({
    icon: "warning",
    title: "Proceso Demorado",
    html: `
      <div class="text-left">
        <p><strong>✅ Documento creado exitosamente:</strong></p>
        <ul>
          <li><strong>ID:</strong> ${datosDocumento.idingresosalidaalm}</li>
          <li><strong>Serie:</strong> ${datosDocumento.serie || "N/A"}</li>
          <li><strong>Número:</strong> ${datosDocumento.numero || "N/A"}</li>
        </ul>
        <hr>
        <p><strong>⏰ El proceso de contabilización y centralización está tomando más tiempo del esperado.</strong></p>
        <p><small class="text-muted">El documento fue creado correctamente. El proceso puede continuar en segundo plano o puede procesarlo manualmente más tarde.</small></p>
      </div>
    `,
    confirmButtonColor: "#ffc107",
    confirmButtonText: "Entendido",
    showCancelButton: true,
    cancelButtonText: "Procesar Manualmente",
    cancelButtonColor: "#6c757d",
  }).then((result) => {
    if (result.isConfirmed) {
      AJSfinalizarProceso();
    } else if (result.dismiss === Swal.DismissReason.cancel) {
      // Abrir modal para proceso manual o redirigir a una página específica
      AJSmostrarOpcionesProcesamiento(datosDocumento);
    }
  });
}

// Función para mostrar opciones de procesamiento manual
function AJSmostrarOpcionesProcesamiento(datosDocumento) {
  Swal.fire({
    icon: "info",
    title: "Opciones de Procesamiento",
    html: `
      <div class="text-left">
        <p><strong>Documento:</strong> ${datosDocumento.idingresosalidaalm}</p>
        <p>Puede procesar la contabilización y centralización de las siguientes maneras:</p>
        <ul>
          <li>Buscar el documento en la tabla y hacer clic para procesarlo</li>
          <li>Usar el módulo de procesamiento manual</li>
          <li>Contactar al administrador del sistema</li>
        </ul>
      </div>
    `,
    confirmButtonColor: "#007bff",
    confirmButtonText: "Entendido",
  }).then(() => {
    AJSfinalizarProceso();
  });
}

// Función para finalizar el proceso y limpiar
function AJSfinalizarProceso() {
 

  // Limpiar formulario y cerrar modal
  AJSlimpiarFormularioCompleto();
  $("#AJSmodalNuevaSalida").modal("hide");

  // Recargar tabla si existe
  if (
    typeof window.tablaSalidasInternas !== "undefined" &&
    window.tablaSalidasInternas
  ) {
    console.log("🔄 Recargando tabla de salidas internas...");
    window.tablaSalidasInternas.ajax.reload();
  } else {
    console.log("⚠️ Tabla de salidas internas no encontrada para recargar");
  }

  // Actualizar cualquier botón de procesamiento que esté visible
  AJSactualizarBotonesProcesamientoEnTabla();

  console.log("✅ Proceso finalizado completamente");
}

// Función para actualizar botones de procesamiento en la tabla
function AJSactualizarBotonesProcesamientoEnTabla() {
  console.log("🔄 Actualizando botones de procesamiento en tabla...");

  // Esta función se ejecuta después de recargar la tabla
  // Los botones se actualizarán automáticamente con la nueva data
  setTimeout(() => {
    const botonesProcesar = $(".btn-procesar-salida");
    console.log(
      `📊 Botones de procesamiento encontrados: ${botonesProcesar.length}`
    );
  }, 1000);
}

//================================================================================================================
// FUNCIÓN AUXILIAR PARA OBTENER CSRF TOKEN
//================================================================================================================
function AJSgetCookie(name) {
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

//================================================================================================================
// FUNCIÓN PARA LIMPIAR FORMULARIO COMPLETO DESPUÉS DEL GUARDADO
//================================================================================================================
function AJSlimpiarFormularioCompleto() {
  

  // Limpiar tabla de productos seleccionados
  AJSlimpiarTablaProductosSeleccionados();

  // Limpiar selección de productos en modal de búsqueda
  AJSlimpiarSeleccionProductos();

  // Limpiar datos del requerimiento seleccionado
  datosRequerimientoSeleccionado = null;
  window.datosRequerimientoCompletos = null;

  // Limpiar documento de referencia
  $("#AJSdoc-ref-idreqinterno").val("");
  $("#AJSdoc-ref-doc").val("");
  $("#AJSdoc-ref-serie").val("");
  $("#AJSdoc-ref-numero").val("");
  $("#AJSdoc-ref-fecha").val("");
  $("#AJSdoc-ref-responsable").val("");
  $("#AJSdoc-ref-estado")
    .removeClass("badge-success badge-warning badge-danger")
    .addClass("badge-secondary")
    .text("SIN ESTADO");

  // Reinicializar formulario con valores por defecto
  AJSinicializarFormularioSalida();

 
}

//================================================================================================================
// FUNCIONES PARA BÚSQUEDA DINÁMICA DE RESPONSABLES
//================================================================================================================

// Variable global para almacenar todos los responsables cargados
let responsablesDisponibles = [];

// Función para inicializar la búsqueda de responsables
function AJSinicializarBusquedaResponsables() {
  

  // Cargar responsables inicialmente
  AJScargarResponsables();

  // Manejar cambio en el select de responsables
  $("#AJSencab-idresponsable").on("change", function () {
    const codigo = $(this).val();
    
    AJSactualizarDescripcionResponsable(codigo);

    // También actualizar el campo de descripción para mantener sincronización
    const responsable = responsablesDisponibles.find(
      (r) => r.idresponsable === codigo
    );
    if (responsable) {
      $("#AJSencab-desc-responsable").val(responsable.nombre);
    }
  });

  // Agregar opción de búsqueda al select
  AJSagregarFuncionalidadBusqueda();
}

// Función para cargar todos los responsables desde la API
function AJScargarResponsables() {
  

  $.ajax({
    url: "/almacen/api/responsables-ajs/",
    type: "GET",
    dataType: "json",
    success: function (response) {
      

      if (response.success && response.data) {
        responsablesDisponibles = response.data;
        AJSllenarSelectResponsables(response.data);
        console.log(`📊 Total responsables cargados: ${response.data.length}`);
      } else {
        console.error(
          "❌ Error en la respuesta de responsables:",
          response.message
        );
        AJSmostrarErrorCargaResponsables();
      }
    },
    error: function (xhr, status, error) {
      console.error("❌ Error al cargar responsables:", error);
      console.error("Respuesta del servidor:", xhr.responseText);
      AJSmostrarErrorCargaResponsables();
    },
  });
}

// Función para llenar el select con los responsables
function AJSllenarSelectResponsables(responsables) {
  const select = $("#AJSencab-idresponsable");

  // Limpiar opciones existentes excepto la primera
  select.find("option:not(:first)").remove();

  // Agregar responsables
  responsables.forEach((responsable) => {
    const option = new Option(
      responsable.idresponsable, // Solo mostrar el código en el select
      responsable.idresponsable
    );
    option.setAttribute("data-nombre", responsable.nombre);
    select.append(option);
  });

  console.log(`✅ Select llenado con ${responsables.length} responsables`);
}

// Función para actualizar la descripción del responsable seleccionado
function AJSactualizarDescripcionResponsable(idResponsable) {
  const descripcionInput = $("#AJSencab-desc-responsable");

  if (!idResponsable || idResponsable === "") {
    descripcionInput.val("");
    return;
  }

  // Buscar el responsable en los datos cargados
  const responsable = responsablesDisponibles.find(
    (r) => r.idresponsable === idResponsable
  );

  if (responsable) {
    descripcionInput.val(responsable.nombre);
    console.log(
      `✅ Responsable actualizado: ${idResponsable} - ${responsable.nombre}`
    );
  } else {
    // Si no se encuentra, buscar en la API
    AJSbuscarResponsablePorId(idResponsable);
  }
}

// Función para buscar un responsable específico por ID
function AJSbuscarResponsablePorId(idResponsable) {
  console.log(`🔍 Buscando responsable por ID: ${idResponsable}`);

  $.ajax({
    url: `/almacen/api/responsables-ajs/?idresponsable=${idResponsable}`,
    type: "GET",
    dataType: "json",
    success: function (response) {
      if (response.success && response.data && response.data.length > 0) {
        const responsable = response.data[0];
        $("#AJSencab-desc-responsable").val(responsable.nombre);
        console.log(`✅ Responsable encontrado: ${responsable.nombre}`);
      } else {
        $("#AJSencab-desc-responsable").val("Responsable no encontrado");
        console.warn(`⚠️ Responsable no encontrado: ${idResponsable}`);
      }
    },
    error: function (xhr, status, error) {
      console.error(`❌ Error al buscar responsable ${idResponsable}:`, error);
      $("#AJSencab-desc-responsable").val("Error al buscar");
    },
  });
}

// Función para agregar funcionalidad de búsqueda
function AJSagregarFuncionalidadBusqueda() {
  const selectResponsable = $("#AJSencab-idresponsable");
  const descripcionInput = $("#AJSencab-desc-responsable");

  // Convertir el input de descripción en un campo de búsqueda
  descripcionInput.prop("readonly", false);
  descripcionInput.attr("placeholder", "Buscar por código o nombre...");

  // Crear contenedor para sugerencias si no existe
  if (!$("#sugerencias-responsables").length) {
    const contenedorSugerencias = $(`
      <div id="sugerencias-responsables" class="dropdown-menu" style="
        position: absolute;
        z-index: 1050;
        width: 100%;
        max-height: 320px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 6px;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: none;
        margin-top: 2px;
        min-width: 300px;
      "></div>
    `);

    descripcionInput
      .closest(".input-group")
      .css("position", "relative")
      .append(contenedorSugerencias);
  }

  // Agregar evento de búsqueda en tiempo real
  descripcionInput.on("input", function () {
    const termino = $(this).val().trim();

    if (termino.length === 0) {
      // Si se borra todo, limpiar selección y ocultar sugerencias
      selectResponsable.val("");
      AJSocultarSugerencias();
      return;
    }

    // Detectar si es búsqueda por código (solo números) o por nombre
    const esCodigoBusqueda = /^\d+$/.test(termino);

    if (esCodigoBusqueda) {
      // Búsqueda por código - autocompletado o sugerencias
      console.log(`🔢 Buscando por código: ${termino}`);
      AJSbuscarYAutocompletarPorCodigo(termino);
    } else if (termino.length >= 2) {
      // Búsqueda por nombre - mostrar sugerencias
      console.log(`📝 Buscando por nombre: ${termino}`);
      AJSmostrarSugerenciasPorNombre(termino);
    } else {
      AJSocultarSugerencias();
    }
  });

  // Manejar teclas especiales (flechas, Enter, Escape)
  descripcionInput.on("keydown", function (e) {
    const sugerencias = $("#sugerencias-responsables");
    const itemsVisibles = sugerencias.find(".sugerencia-item:visible");

    if (sugerencias.is(":visible") && itemsVisibles.length > 0) {
      const itemActivo = itemsVisibles.filter(".active");

      switch (e.which) {
        case 38: // Flecha arriba
          e.preventDefault();
          if (itemActivo.length === 0) {
            itemsVisibles.last().addClass("active");
          } else {
            const anterior = itemActivo.prev(".sugerencia-item:visible");
            itemActivo.removeClass("active");
            if (anterior.length > 0) {
              anterior.addClass("active");
            } else {
              itemsVisibles.last().addClass("active");
            }
          }
          break;

        case 40: // Flecha abajo
          e.preventDefault();
          if (itemActivo.length === 0) {
            itemsVisibles.first().addClass("active");
          } else {
            const siguiente = itemActivo.next(".sugerencia-item:visible");
            itemActivo.removeClass("active");
            if (siguiente.length > 0) {
              siguiente.addClass("active");
            } else {
              itemsVisibles.first().addClass("active");
            }
          }
          break;

        case 13: // Enter
          e.preventDefault();
          if (itemActivo.length > 0) {
            itemActivo.click();
          }
          break;

        case 27: // Escape
          e.preventDefault();
          AJSocultarSugerencias();
          break;
      }
    }
  });

  // Ocultar sugerencias al hacer clic fuera
  $(document).on("click", function (e) {
    if (
      !$(e.target).closest("#AJSencab-desc-responsable, #sugerencias-responsables")
        .length
    ) {
      AJSocultarSugerencias();
    }
  });

  // Manejar focus para mostrar sugerencias si hay texto
  descripcionInput.on("focus", function () {
    const termino = $(this).val().trim();
    if (termino.length >= 2 && !/^\d+$/.test(termino)) {
      AJSmostrarSugerenciasPorNombre(termino);
    }
  });

  // IMPORTANTE: Agregar evento de cambio del select para autocompletar el nombre
  selectResponsable.on("change", function () {
    const idSeleccionado = $(this).val();
    console.log(`🔄 Select cambió a: ${idSeleccionado}`);

    if (idSeleccionado && idSeleccionado !== "") {
      AJSactualizarDescripcionResponsable(idSeleccionado);
    } else {
      descripcionInput.val("");
    }
  });
}

// Función para buscar y autocompletar por código de responsable
function AJSbuscarYAutocompletarPorCodigo(codigo) {
  console.log(`🔍 Autocompletando por código: "${codigo}"`);

  // Buscar coincidencias que empiecen con el código ingresado
  let coincidencias = responsablesDisponibles.filter((responsable) => {
    // Buscar tanto en el código original como en el código sin ceros a la izquierda
    const codigoSinCeros = responsable.idresponsable.replace(/^0+/, "") || "0";
    return (
      responsable.idresponsable.startsWith(codigo.padStart(6, "0")) ||
      codigoSinCeros.startsWith(codigo)
    );
  });

  if (coincidencias.length === 1) {
    // Si hay exactamente una coincidencia, autocompletar
    const responsable = coincidencias[0];
    $("#AJSencab-idresponsable").val(responsable.idresponsable);
    $("#AJSencab-desc-responsable").val(responsable.nombre);
    console.log(
      `✅ Autocompletado exacto: ${responsable.idresponsable} - ${responsable.nombre}`
    );
    return;
  } else if (coincidencias.length > 1 && codigo.length >= 3) {
    // Si hay múltiples coincidencias y suficiente texto, mostrar sugerencias de códigos
    AJSmostrarSugerenciasCodigos(coincidencias, codigo);
    return;
  }

  // Si no encuentra localmente y el código tiene suficientes dígitos, buscar en API
  if (codigo.length >= 3) {
    AJSbuscarCodigoEnAPI(codigo);
  }
}

// Función para buscar código en la API
function AJSbuscarCodigoEnAPI(codigo) {
  const codigoFormateado = codigo.padStart(6, "0");

  $.ajax({
    url: `/almacen/api/responsables-ajs/?idresponsable=${codigoFormateado}`,
    type: "GET",
    dataType: "json",
    success: function (response) {
      if (response.success && response.data && response.data.length > 0) {
        const responsable = response.data[0];
        $("#AJSencab-idresponsable").val(responsable.idresponsable);
        $("#AJSencab-desc-responsable").val(responsable.nombre);
        console.log(`✅ Responsable encontrado por API: ${responsable.nombre}`);

        // Agregar a la lista local para futuras búsquedas
        if (
          !responsablesDisponibles.find(
            (r) => r.idresponsable === responsable.idresponsable
          )
        ) {
          responsablesDisponibles.push(responsable);
        }
      } else {
        console.log(`⚠️ No se encontró responsable con código: ${codigo}`);
      }
    },
    error: function (xhr, status, error) {
      console.warn(`⚠️ Error al buscar código ${codigo}:`, error);
    },
  });
}

// Función para mostrar sugerencias de códigos cuando hay múltiples coincidencias
function AJSmostrarSugerenciasCodigos(responsables, codigoBuscado) {
  const contenedor = $("#sugerencias-responsables");
  contenedor.empty();

  responsables.slice(0, 6).forEach((responsable) => {
    // Resaltar el código buscado
    const codigoResaltado = AJSresaltarTexto(
      responsable.idresponsable,
      codigoBuscado
    );

    const item = $(`
      <div class="sugerencia-item dropdown-item" style="
        padding: 12px 16px;
        cursor: pointer;
        border-bottom: 1px solid #f1f3f4;
        transition: all 0.2s ease;
        border-radius: 4px;
        margin: 2px 4px;
        min-height: 60px;
      " data-id="${responsable.idresponsable}" data-nombre="${responsable.nombre}">
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <div style="flex-grow: 1; min-width: 0;">
            <div style="color: #2563eb; font-weight: bold; font-size: 0.9em; margin-bottom: 2px;">
              ${codigoResaltado}
            </div>
            <div style="font-size: 0.8em; color: #374151; line-height: 1.3; word-wrap: break-word;">
              ${responsable.nombre}
            </div>
          </div>
          <i class="fas fa-arrow-right" style="color: #9ca3af; font-size: 0.8em; margin-left: 8px; flex-shrink: 0;"></i>
        </div>
      </div>
    `);

    AJSconfigurarEventosSugerencia(item);
    contenedor.append(item);
  });

  contenedor.show();
}

// Función para mostrar sugerencias por nombre
function AJSmostrarSugerenciasPorNombre(termino) {
  console.log(`🔍 Mostrando sugerencias para: "${termino}"`);

  // Buscar coincidencias en los datos cargados
  const terminoLower = termino.toLowerCase();
  const coincidencias = responsablesDisponibles
    .filter((responsable) =>
      responsable.nombre.toLowerCase().includes(terminoLower)
    )
    .slice(0, 8); // Limitar a 8 resultados para no sobrecargar

  if (coincidencias.length > 0) {
    AJSmostrarDropdownSugerencias(coincidencias, termino);
  } else {
    // Si no hay coincidencias locales, buscar en la API
    AJSbuscarEnAPIPorNombre(termino);
  }
}

// Función para buscar en la API por nombre
function AJSbuscarEnAPIPorNombre(termino) {
  $.ajax({
    url: `/almacen/api/responsables-ajs/?nombre=${encodeURIComponent(termino)}`,
    type: "GET",
    dataType: "json",
    success: function (response) {
      if (response.success && response.data && response.data.length > 0) {
        AJSmostrarDropdownSugerencias(response.data.slice(0, 8), termino);
        console.log(
          `✅ Encontrados ${response.data.length} responsables por API`
        );
      } else {
        AJSmostrarSinSugerencias(termino);
      }
    },
    error: function (xhr, status, error) {
      console.error("❌ Error en búsqueda por nombre:", error);
      AJSmostrarSinSugerencias(termino);
    },
  });
}

// Función para mostrar el dropdown de sugerencias
function AJSmostrarDropdownSugerencias(responsables, terminoBuscado) {
  const contenedor = $("#sugerencias-responsables");
  contenedor.empty();

  responsables.forEach((responsable, index) => {
    // Resaltar el término buscado en el nombre
    const nombreResaltado = AJSresaltarTexto(responsable.nombre, terminoBuscado);

    const item = $(`
      <div class="sugerencia-item dropdown-item" style="
        padding: 12px 16px;
        cursor: pointer;
        border-bottom: 1px solid #f1f3f4;
        transition: all 0.2s ease;
        border-radius: 4px;
        margin: 2px 4px;
        min-height: 60px;
      " data-id="${responsable.idresponsable}" data-nombre="${responsable.nombre}">
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <div style="flex-grow: 1; min-width: 0;">
            <div style="color: #2563eb; font-weight: bold; font-size: 0.9em; margin-bottom: 2px;">
              ${responsable.idresponsable}
            </div>
            <div style="font-size: 0.8em; color: #374151; line-height: 1.3; word-wrap: break-word;">
              ${nombreResaltado}
            </div>
          </div>
          <i class="fas fa-arrow-right" style="color: #9ca3af; font-size: 0.8em; margin-left: 8px; flex-shrink: 0;"></i>
        </div>
      </div>
    `);

    AJSconfigurarEventosSugerencia(item);
    contenedor.append(item);
  });

  // Mostrar el contenedor
  contenedor.show();
}

// Función para configurar eventos de las sugerencias (reutilizable)
function AJSconfigurarEventosSugerencia(item) {
  // Agregar efectos hover mejorados
  item.on("mouseenter", function () {
    $(this).addClass("active").css({
      "background-color": "#3b82f6",
      color: "white",
      transform: "translateX(2px)",
      "box-shadow": "0 2px 8px rgba(59, 130, 246, 0.3)",
    });

    // Cambiar colores de los elementos internos
    $(this).find("strong").css("color", "#e5e7eb");
    $(this).find("span").css("color", "#f3f4f6");
    $(this).find("i").css("color", "#e5e7eb");

    $(this)
      .siblings()
      .removeClass("active")
      .css({
        "background-color": "",
        color: "",
        transform: "",
        "box-shadow": "",
      })
      .find("strong, span, i")
      .css("color", "");
  });

  item.on("mouseleave", function () {
    $(this).css({
      "background-color": "",
      color: "",
      transform: "",
      "box-shadow": "",
    });

    // Restaurar colores originales
    $(this).find("strong").css("color", "#2563eb");
    $(this).find("span").css("color", "#374151");
    $(this).find("i").css("color", "#9ca3af");
  });

  // Manejar clic en la sugerencia
  item.on("click", function () {
    const id = $(this).data("id");
    const nombre = $(this).data("nombre");

    // Actualizar tanto el select como el input de descripción
    const selectResponsable = $("#AJSencab-idresponsable");
    const descripcionInput = $("#AJSencab-desc-responsable");

    // Verificar si el responsable ya existe en el select
    if (selectResponsable.find(`option[value="${id}"]`).length === 0) {
      // Si no existe, agregarlo al select
      const nuevaOpcion = new Option(id, id);
      nuevaOpcion.setAttribute("data-nombre", nombre);
      selectResponsable.append(nuevaOpcion);

      // Agregarlo también a la lista local
      if (!responsablesDisponibles.find((r) => r.idresponsable === id)) {
        responsablesDisponibles.push({ idresponsable: id, nombre: nombre });
      }
    }

    // Seleccionar el responsable
    selectResponsable.val(id);
    descripcionInput.val(nombre);

    AJSocultarSugerencias();
    console.log(
      `✅ Responsable seleccionado desde sugerencias: ${id} - ${nombre}`
    );
  });
}

// Función para resaltar texto en las sugerencias
function AJSresaltarTexto(texto, termino) {
  if (!termino || termino.length < 2) return texto;

  const regex = new RegExp(`(${termino})`, "gi");
  return texto.replace(
    regex,
    '<strong style="background-color: #fff3cd;">$1</strong>'
  );
}

// Función para ocultar sugerencias
function AJSocultarSugerencias() {
  $("#sugerencias-responsables").hide().empty();
}

// Función para mostrar cuando no hay sugerencias
function AJSmostrarSinSugerencias(termino) {
  const contenedor = $("#sugerencias-responsables");
  contenedor
    .html(
      `
    <div class="dropdown-item" style="padding: 12px; text-align: center; color: #6c757d;">
      <i class="fas fa-search" style="margin-right: 8px;"></i>
      Sin resultados para "${termino}"
    </div>
  `
    )
    .show();

  // Ocultar después de 2 segundos
  setTimeout(() => {
    AJSocultarSugerencias();
  }, 2000);
}

function AJSmostrarErrorCargaResponsables() {
  console.error("❌ Error al cargar responsables, usando valores por defecto");

  // Mantener las opciones hardcodeadas como fallback
  const responsablesPorDefecto = [
    { idresponsable: "000065", nombre: "HUAMAN FLORES JOHAN ERICKSON" },
    { idresponsable: "000037", nombre: "RESPONSABLE 37" },
    { idresponsable: "000038", nombre: "RESPONSABLE 38" },
  ];

  responsablesDisponibles = responsablesPorDefecto;
  console.log("⚠️ Usando responsables por defecto");
}

//================================================================================================================
// FUNCIONES DE DEBUGGING Y DIAGNÓSTICO MANUAL
//================================================================================================================

// ✅ FUNCIÓN DE DEBUGGING MANUAL PARA LA CONSOLA
window.debugReqInterno = function () {
  console.log("🐛 ===== DEBUG MANUAL REQINTERNO =====");

  const debug = {
    timestamp: new Date().toISOString(),
    variables_globales: {
      productosSeleccionadosCompletos: {
        definida: typeof productosSeleccionadosCompletos !== "undefined",
        cantidad: productosSeleccionadosCompletos?.length || 0,
        primer_producto: productosSeleccionadosCompletos?.[0] || null,
      },
      datosProductosCompletosAPI: {
        definida: typeof datosProductosCompletosAPI !== "undefined",
        cantidad: datosProductosCompletosAPI?.length || 0,
        primer_producto: datosProductosCompletosAPI?.[0] || null,
      },
      datosRequerimientoSeleccionado: {
        definida: typeof datosRequerimientoSeleccionado !== "undefined",
        tiene_datos: !!datosRequerimientoSeleccionado,
        contenido: datosRequerimientoSeleccionado,
      },
      window_datosRequerimientoCompletos: {
        definida: typeof window.datosRequerimientoCompletos !== "undefined",
        tiene_datos: !!window.datosRequerimientoCompletos,
        contenido: window.datosRequerimientoCompletos,
      },
    },
    elementos_dom: {
      campo_idreqinterno: {
        existe: $("#AJSdoc-ref-idreqinterno").length > 0,
        valor: $("#AJSdoc-ref-idreqinterno").val(),
        visible: $("#AJSdoc-ref-idreqinterno").is(":visible"),
      },
      checkboxes_productos: {
        total: $(".chk-producto").length,
        seleccionados: $(".chk-producto:checked").length,
      },
    },
    diagnostico_automatico: null,
    simulacion_extraccion: null,
  };

  // Ejecutar diagnóstico automático si está disponible
  if (typeof AJSdiagnosticarEstadoParaReqInterno === "function") {
    debug.diagnostico_automatico = AJSdiagnosticarEstadoParaReqInterno();
  }

  // Simular extracción de datos con datos de prueba
  if (
    productosSeleccionadosCompletos &&
    productosSeleccionadosCompletos.length > 0
  ) {
    const datosDocumentoPrueba = {
      idingresosalidaalm: "_TEST_IDINGRESOSALIDAALM_12345",
    };

    try {
      debug.simulacion_extraccion =
        extraerDatosProductosReqInterno(datosDocumentoPrueba);
    } catch (error) {
      debug.simulacion_extraccion = { error: error.message };
    }
  }

  console.log("🐛 Resultado del debug:", debug);

  // También retornar para uso programático
  return debug;
};

// ✅ FUNCIÓN PARA EJECUTAR PRUEBA COMPLETA DESDE LA CONSOLA
window.probarFlujoProcesamiento = function () {
  console.log("🧪 ===== PRUEBA COMPLETA DEL FLUJO =====");

  // 1. Verificar estado inicial
  const debugInicial = window.debugReqInterno();
  console.log("📊 Estado inicial:", debugInicial);

  // 2. Verificar si hay datos suficientes para la prueba
  if (
    !productosSeleccionadosCompletos ||
    productosSeleccionadosCompletos.length === 0
  ) {
    console.error("❌ No hay productos seleccionados para la prueba");
    return {
      exito: false,
      mensaje: "No hay productos seleccionados",
    };
  }

  // 3. Simular datos del documento
  const datosDocumentoPrueba = {
    idingresosalidaalm: "_PRUEBA_" + Date.now(),
    serie: "001",
    numero: "000001",
  };

  // 4. Simular response del proceso
  const responseProcesoPrueba = {
    status: "success",
    message: "Documento creado exitosamente para prueba",
  };

  console.log("🔄 Iniciando procesamiento de prueba...");

  try {
    // 5. Ejecutar el flujo completo
    AJSprocesarProductosReqInterno(datosDocumentoPrueba, responseProcesoPrueba);

    return {
      exito: true,
      mensaje:
        "Prueba iniciada correctamente - revise la consola y los modales",
    };
  } catch (error) {
    console.error("❌ Error en la prueba:", error);
    return {
      exito: false,
      mensaje: "Error en la prueba: " + error.message,
      error: error,
    };
  }
};

// ✅ FUNCIÓN PARA VERIFICAR ENDPOINT Y BACKEND
window.verificarBackend = function () {
  console.log("🔍 ===== VERIFICANDO BACKEND =====");

  const datosTesteo = {
    productos: [
      {
        IDPRODUCTO: "TEST_PRODUCTO",
        ITEMREF: "001",
        IDINGRESOSALIDAALM: "TEST_SALIDA",
        IDREFERENCIA: "TEST_REF",
      },
    ],
  };

  console.log("📤 Enviando datos de prueba al backend...", datosTesteo);

  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/almacen/api/procesar-requerimiento/",
      type: "POST",
      data: JSON.stringify(datosTesteo),
      contentType: "application/json",
      headers: {
        "X-CSRFToken": AJSgetCookie("csrftoken"),
      },
      success: function (response) {
        console.log("✅ Backend responde correctamente:", response);
        resolve(response);
      },
      error: function (xhr, status, error) {
        console.error("❌ Error del backend:", {
          status: xhr.status,
          statusText: status,
          error: error,
          responseText: xhr.responseText,
        });
        reject({
          status: xhr.status,
          error: error,
          response: xhr.responseText,
        });
      },
    });
  });
};

//================================================================================================================
// FUNCIÓN DE PRUEBA SIMPLE PARA REQINTERNO
//================================================================================================================

// ✅ FUNCIÓN PARA PROBAR LA RECUPERACIÓN DE DATOS DESDE LA CONSOLA
window.probarRecuperacionDatos = function (enviarAApi = true) {
  console.log("🧪 ===== PROBANDO RECUPERACIÓN DE DATOS PARA REQINTERNO =====");
  console.log(
    `📤 Enviar a API: ${enviarAApi ? "SÍ" : "NO (solo mostrar datos)"}`
  );

  // Simular datos del documento (como si viniera de la contabilización)
  const datosDocumentoPrueba = {
    idingresosalidaalm: "_PRUEBA_" + Date.now(), // ID único para cada prueba
    serie: "0001",
    numero: "000001",
  };

  const responseProcesoPrueba = {
    status: "success",
    message: "Contabilización y centralización exitosa",
  };

  console.log("📋 Simulando llamada con datos de prueba:");
  console.log("   • datosDocumento:", datosDocumentoPrueba);
  console.log("   • responseProceso:", responseProcesoPrueba);

  try {
    if (enviarAApi) {
      // Usar la función completa que envía a la API
      const resultado = AJSrecuperarDatosOriginalesParaReqInterno(
        datosDocumentoPrueba,
        responseProcesoPrueba
      );

      console.log("🎯 ===== FLUJO COMPLETO EJECUTADO =====");
      console.log("✅ Datos recuperados y enviados a la API automáticamente");
      console.log(
        "📋 Revisa los logs anteriores para ver el resultado del envío"
      );

      return resultado;
    } else {
      // Solo recuperar datos sin enviar (versión original)
      console.log("📋 MODO SOLO RECUPERACIÓN - NO SE ENVIARÁ A LA API");

      // Temporalmente desactivar el envío
      const enviarOriginal = window.AJSenviarEstructuraAApiReqInterno;
      window.AJSenviarEstructuraAApiReqInterno = function () {
        console.log("⏳ Envío a API desactivado para esta prueba");
      };

      const resultado = AJSrecuperarDatosOriginalesParaReqInterno(
        datosDocumentoPrueba,
        responseProcesoPrueba
      );

      // Restaurar función original
      window.AJSenviarEstructuraAApiReqInterno = enviarOriginal;

      console.log("🎯 ===== RESULTADO DE LA PRUEBA (SOLO DATOS) =====");
      if (resultado) {
        console.log("✅ ÉXITO: Datos recuperados correctamente");
        console.log("📊 Resumen de datos recuperados:");
        console.log(`   • Productos: ${resultado.productos.length}`);
        console.log(`   • IDEMPRESA: ${resultado.encabezado.IDEMPRESA}`);
        console.log(
          `   • IDREFERENCIA: ${resultado.documento_referencia.IDREFERENCIA}`
        );
        console.log(`   • IDINGRESOSALIDAALM: ${resultado.idingresosalidaalm}`);
      } else {
        console.log("❌ ERROR: No se pudieron recuperar los datos");
      }

      return resultado;
    }
  } catch (error) {
    console.error("❌ Error en la prueba:", error);
    return null;
  }
};

// Función para consultar el tipo de cambio por fecha y actualizar el input
function AJSobtenerTipoCambioPorFecha(fecha) {
  console.log("🔄 Función AJSobtenerTipoCambioPorFecha ejecutándose con fecha:", fecha);
  
  // Mostrar loading en el campo
  $("#AJSencab-tcambio").val("...").prop("disabled", true);

  $.ajax({
    url: "/almacen/api/tcambio-ajs/?fecha=" + encodeURIComponent(fecha),
    method: "GET",
    dataType: "json",
    success: function (response) {
      console.log("✅ Respuesta del API de tipo de cambio:", response);
      
      if (response.success && response.data && response.data.length > 0) {
        // Tomar el primer resultado - cambio de T_COMPRA a T_VENTA según la vista
        const tc = response.data[0].T_VENTA || response.data[0].T_COMPRA;
        console.log("💰 Tipo de cambio encontrado:", tc);
        $("#AJSencab-tcambio").val(tc).prop("disabled", false);
        
        if (typeof toastr !== "undefined") {
          toastr.success(
            `Tipo de cambio actualizado: ${tc}`,
            "Tipo de Cambio"
          );
        }
      } else {
        console.log("⚠️ No se encontró tipo de cambio para la fecha:", fecha);
        $("#AJSencab-tcambio").val("").prop("disabled", false);
        if (typeof toastr !== "undefined") {
          toastr.warning(
            "El tipo de cambio no está actualizado en el sistema para la fecha seleccionada.",
            "Tipo de Cambio no encontrado"
          );
        } else {
          alert(
            "El tipo de cambio no está actualizado en el sistema para la fecha seleccionada."
          );
        }
      }
    },
    error: function (xhr, status, error) {
      console.error("❌ Error en la consulta del tipo de cambio:", { xhr, status, error });
      $("#AJSencab-tcambio").val("").prop("disabled", false);
      if (typeof toastr !== "undefined") {
        toastr.error("Error al consultar el tipo de cambio.", "Error API");
      } else {
        alert("Error al consultar el tipo de cambio.");
      }
    },
  });
}



//================================================================================================================
// FUNCION PARA IMPRIMIR DOCUMENTO DE SALIDA INTERNO
//=================================================================================================================



function AJSCrearPdfSalidaInterna(id_salida){
  console.log("📄 Crear PDF para salida interna con ID:", id_salida);
  
  // Mostrar loading
  console.log("🔄 Consultando API para obtener datos de la salida...");
  
  // Construir URL de la API
  const apiUrl = `/almacen/api/salida-interna-ajs/${id_salida}/`;
  console.log("🌐 URL de consulta:", apiUrl);
  
  // Realizar consulta AJAX
  $.ajax({
    url: apiUrl,
    method: 'GET',
    dataType: 'json',
    beforeSend: function() {
      console.log("⏳ Enviando petición a la API...");
    },
    success: function(response) {
      console.log("✅ Respuesta exitosa de la API:");
      console.log("📊 Datos completos recibidos:", response);
      
      // Mostrar estructura de datos detallada
      if (response && typeof response === 'object') {
        console.log("🔍 Análisis de la estructura de datos:");
        console.log("   • Tipo de respuesta:", typeof response);
        console.log("   • Propiedades principales:", Object.keys(response));
        
        // Si tiene encabezado
        if (response.encabezado) {
          console.log("📋 Datos del encabezado:");
          console.log(response.encabezado);
        }
        
        // Si tiene detalle
        if (response.detalle) {
          console.log("📦 Datos del detalle:");
          console.log("   • Cantidad de productos:", response.detalle.length);
          console.log("   • Primer producto:", response.detalle[0]);
          console.log("   • Todos los productos:", response.detalle);
        }
        
        // Si tiene otros campos
        Object.keys(response).forEach(key => {
          if (key !== 'encabezado' && key !== 'detalle') {
            console.log(`   • ${key}:`, response[key]);
          }
        });
        
      } else {
        console.log("⚠️ Respuesta no es un objeto válido");
      }
      
      console.log("🎯 Próximo paso: Crear plantilla PDF con estos datos");
      
      // ✅ CREAR PREVISUALIZACIÓN PDF
      AJScrearPrevisualizacionPDF(response.data);
    },
    error: function(xhr, status, error) {
      console.error("❌ Error al consultar la API:");
      console.error("   • Status:", status);
      console.error("   • Error:", error);
      console.error("   • Response Text:", xhr.responseText);
      console.error("   • Status Code:", xhr.status);
      
      // Intentar parsear el error si es JSON
      try {
        const errorData = JSON.parse(xhr.responseText);
        console.error("   • Error parseado:", errorData);
      } catch (e) {
        console.error("   • No se pudo parsear el error como JSON");
      }
    },
    complete: function() {
      console.log("🏁 Consulta completada");
    }
  });
}

/**
 * Crear previsualización del PDF con los datos obtenidos
 * @param {Object} datos - Datos de la salida interna (encabezado, detalle, resumen)
 */

/* 
function AJScrearPrevisualizacionPDF(datos) {
  console.log("🎨 Creando previsualización del PDF...");
  console.log("📊 Datos para el PDF:", datos);
  
  // Verificar que jsPDF esté disponible
  if (typeof jsPDF === 'undefined' && typeof window.jspdf === 'undefined') {
    console.error("❌ jsPDF no está disponible");
    alert("Error: La librería jsPDF no está cargada. Por favor, recarga la página.");
    return;
  }
  
  // Obtener la clase jsPDF
  const PDFClass = typeof jsPDF !== 'undefined' ? jsPDF : window.jspdf.jsPDF;
  
  try {
    // Crear nuevo documento PDF (formato A4)
    const doc = new PDFClass({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    // Configuración de página
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 5;
    let yPos = margin;
    
    console.log(`📏 Dimensiones página: ${pageWidth}mm x ${pageHeight}mm`);
    
    const encabezado = datos.encabezado;
    
    // ===== ENCABEZADO DE LA EMPRESA (Esquina superior izquierda) =====
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text('SOCIEDAD AGRICOLA DON LUIS S.A.', margin, yPos);
    yPos += 4;
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text('CAL. CONTRALMIRANTE MONTERO NRO. 411 INT.', margin, yPos);
    yPos += 4;
    doc.text('20325346435', margin, yPos);
    
    // ===== INFORMACIÓN SUPERIOR DERECHA =====
    const infoDerechaX = pageWidth - 15;
    doc.setFontSize(9);
    doc.text('Página 1 de 1', infoDerechaX, margin, { align: 'right' });
    doc.text('JUEVES, 31 DE JULIO DE 2025', infoDerechaX, margin + 4, { align: 'right' });
    doc.text('13:51:30', infoDerechaX, margin + 8, { align: 'right' });
    
    yPos += 15;
    
    // ===== TÍTULO PRINCIPAL CENTRADO =====
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    const numeroDocumento = encabezado.NUM_DOCUMENTO?.replace(/\s+/g, '-') || '0001-0061807';
    doc.text(`SALIDA INTERNA N° ${numeroDocumento}`, pageWidth/2, yPos, { align: 'center' });
    yPos += 12;
    
    // ===== INFORMACIÓN EN FORMATO DE ETIQUETAS (MEJORADO) =====
    doc.setFontSize(10);
    
    // Primera línea: Motivo y Almacen
    doc.setFont('helvetica', 'bold');
    doc.text('Motivo', margin, yPos);
    
    doc.setFont('helvetica', 'normal');
    const motivoTexto = `[${encabezado.IDMOTIVO || 'SAD'}] ${encabezado.NOMBRE_MOTIVO || 'SALIDA POR CONSUMO - ADMINISTRATIVO'}`;
    // Truncar motivo si es muy largo
    const motivoCorto = motivoTexto.length > 45 ? motivoTexto.substring(0, 42) + '...' : motivoTexto;
    doc.text(motivoCorto, margin + 20, yPos);
    
    doc.setFont('helvetica', 'bold');
    doc.text('Almacen', margin + 110, yPos);
    
    doc.setFont('helvetica', 'normal');
    const almacenTexto = `[${encabezado.IDALMACEN || '001'}] ${encabezado.ALMACEN_DESCRIPCION || 'ALMACEN CENTRAL'}`;
    // Truncar almacen si es muy largo
    const almacenCorto = almacenTexto.length > 35 ? almacenTexto.substring(0, 32) + '...' : almacenTexto;
    doc.text(almacenCorto, margin + 130, yPos);
    yPos += 7;
    
    // Segunda línea: Fecha Salida y Sucursal
    doc.setFont('helvetica', 'bold');
    doc.text('Fecha Salida', margin, yPos);
    
    doc.setFont('helvetica', 'normal');
    doc.text(encabezado.FECHA_SALIDA || '02/07/2025', margin + 30, yPos);
    
    doc.setFont('helvetica', 'bold');
    doc.text('Sucursal', margin + 110, yPos);
    
    doc.setFont('helvetica', 'normal');
    const sucursalTexto = `[${encabezado.IDEMPRESA || '001'}] ${encabezado.SUCURSAL || 'SOCIEDAD AGRICOLA DON LUIS'}`;
    // Truncar sucursal si es muy larga
    const sucursalCorto = sucursalTexto.length > 35 ? sucursalTexto.substring(0, 32) + '...' : sucursalTexto;
    doc.text(sucursalCorto, margin + 130, yPos);
    yPos += 15;
    
    // ===== CONFIGURACIÓN DE TABLA MEJORADA =====
    const tablaAncho = pageWidth - (margin * 2);
    const alturaFila = 7; // Altura más compacta como la original
    
    // Configuración de columnas exacta como la tabla original
    const columnas = [
      { header: 'Item', width: 10, align: 'center' },
      { header: 'Codigo', width: 20, align: 'left' },
      { header: 'Descripcion', width: 105, align: 'left' },
      { header: 'U.M', width: 15, align: 'center' },
      { header: 'Cantidad', width: 20, align: 'center' },
      { header: 'Consumidor', width: 30, align: 'left' }
    ];
    
    // Calcular altura estimada de la tabla (será ajustada dinámicamente)
    const numProductos = datos.detalle ? datos.detalle.length : 1;
    let alturaTablaProductos = (numProductos * alturaFila) + alturaFila; // +1 fila para el encabezado
    
    // Guardar posición inicial de la tabla
    const tablaInicio = yPos;
    
    // ===== DIBUJAR ENCABEZADO DE TABLA =====
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8);
    doc.setLineWidth(0.5);
    
    // Dibujar borde superior
    doc.line(margin, yPos, margin + tablaAncho, yPos);
    
    // Guardar posición del encabezado para después dibujar líneas verticales
    const yEncabezado = yPos;
    
    let xActual = margin;
    columnas.forEach((col, index) => {
      // Texto del encabezado
      const xTexto = col.align === 'center' ? xActual + (col.width / 2) : xActual + 2;
      doc.text(col.header, xTexto, yPos + 5, { align: col.align });
      xActual += col.width;
    });
    
    yPos += alturaFila;
    
    // Línea horizontal después del encabezado
    doc.line(margin, yPos, margin + tablaAncho, yPos);
    
    // ===== DATOS DE PRODUCTOS MEJORADO =====
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(6); // Fuente más pequeña para que quepa toda la información
    
    if (datos.detalle && datos.detalle.length > 0) {
      datos.detalle.forEach((producto, index) => {
        xActual = margin;
        let filaActual = yPos;
        
        // Item - centrado
        const item = producto.ITEM || (index + 1).toString().padStart(3, '0');
        doc.text(item, xActual + (columnas[0].width / 2), filaActual + 4, { align: 'center' });
        xActual += columnas[0].width;
        
        // Código - texto simple, truncado si es muy largo
        const codigo = (producto.CODIGO || 'no encontrado').trim();
        const codigoTruncado = codigo.length > 12 ? codigo.substring(0, 12) + '...' : codigo;
        doc.text(codigoTruncado, xActual + 1, filaActual + 4);
        xActual += columnas[1].width;
        
        // Descripción - texto simple, truncado si es muy largo
        const descripcion = producto.DESCRIPCION || 'no encontrado';
        const descripcionTruncada = descripcion.length > 50 ? descripcion.substring(0, 47) + '...' : descripcion;
        doc.text(descripcionTruncada, xActual + 1, filaActual + 4);
        xActual += columnas[2].width;
        
        // U.M - centrado
        const unidad = (producto.UNIDAD_MEDIDA || 'n/a').trim();
        doc.text(unidad, xActual + (columnas[3].width / 2), filaActual + 4, { align: 'center' });
        xActual += columnas[3].width;
        
        // Cantidad - centrado
        const cantidad = (producto.CANTIDAD || '0.011').toString();
        doc.text(cantidad, xActual + (columnas[4].width / 2), filaActual + 4, { align: 'center' });
        xActual += columnas[4].width;
        
        // Consumidor - texto simple, truncado
        let consumidor = producto.CONSUMIDOR || 'no encontrado';
        // Si el consumidor es muy largo, dividirlo en varias líneas (máx 30 caracteres por línea)
        const maxCharsConsumidor = 25;
        let lineasConsumidor = [];
        while (consumidor.length > 0) {
          if (consumidor.length <= maxCharsConsumidor) {
            lineasConsumidor.push(consumidor);
            break;
          }
          let corte = maxCharsConsumidor;
          const ultimoEspacio = consumidor.lastIndexOf(' ', corte);
          if (ultimoEspacio > corte * 0.7) {
            corte = ultimoEspacio;
          }
          lineasConsumidor.push(consumidor.substring(0, corte));
          consumidor = consumidor.substring(corte).trim();
        }
        // Mostrar cada línea de consumidor, una debajo de otra
        lineasConsumidor.forEach((linea, idx) => {
          doc.text(linea, xActual + 1, filaActual + 4 + (idx * 3.5));
        });
        // Actualizar yPos para la siguiente fila (si hay varias líneas, aumentar la altura)
        yPos += alturaFila + (lineasConsumidor.length - 1) * 3.5;    
        // Línea horizontal después de cada fila
        doc.line(margin, yPos, margin + tablaAncho, yPos);
      });
      
      // ===== DIBUJAR LÍNEAS VERTICALES DE LA TABLA =====
      // Dibujar las líneas verticales de las columnas
      let xLinea = margin;
      // Línea vertical izquierda
      doc.line(xLinea, yEncabezado, xLinea, yPos);
      
      // Líneas verticales entre columnas y la final
      columnas.forEach((col) => {
        xLinea += col.width;
        doc.line(xLinea, yEncabezado, xLinea, yPos);
      });
    } else {
      // Si no hay productos, agregar una fila vacía
      yPos += alturaFila;
      doc.line(margin, yPos, margin + tablaAncho, yPos);
    }
    
    // ===== SECCIÓN DE OBSERVACIONES Y REFERENCIAS DEBAJO DE LA TABLA =====
    yPos += 10; // Espacio después de la tabla

    const alturaSeccionObsRef = 20;
    // Cambiar la distribución: 85% para observaciones, 15% para referencias
    const anchoObservaciones = tablaAncho * 0.85; // 85% del ancho total
    const anchoReferencias = tablaAncho * 0.15;   // 15% del ancho total

    // NO DIBUJAR RECTÁNGULO NI LÍNEAS - Solo contenido

    // OBSERVACIONES (lado izquierdo - 85% del ancho)
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.text('Observaciones', margin + 2, yPos + 6);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    const observaciones = encabezado.OBSERVACIONES && encabezado.OBSERVACIONES.trim() ? 
                        encabezado.OBSERVACIONES : 'requerimiento para uso en oficina - rosa vera';

    // Aumentar caracteres por línea debido al mayor ancho disponible
    const maxCharsObsLinea = 55; // 55 caracteres por línea
    const lineasObs = [];
    let textoRestante = observaciones;

    while (textoRestante.length > 0 && lineasObs.length < 2) {
      if (textoRestante.length <= maxCharsObsLinea) {
        lineasObs.push(textoRestante);
        break;
      }
      
      let corte = maxCharsObsLinea;
      const ultimoEspacio = textoRestante.lastIndexOf(' ', corte);
      if (ultimoEspacio > corte * 0.7) {
        corte = ultimoEspacio;
      }
      
      lineasObs.push(textoRestante.substring(0, corte));
      textoRestante = textoRestante.substring(corte).trim();
    }

    lineasObs.forEach((linea, index) => {
      doc.text(linea, margin + 2, yPos + 12 + (index * 4));
    });

    // REFERENCIAS (lado derecho - 15% del ancho)
    const xReferencias = margin + anchoObservaciones + 10; // Añadir un poco de separación
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.text('Referencias', xReferencias, yPos + 6);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    const referencias = (datos.detalle && datos.detalle[0] && datos.detalle[0].REFERENCIA) ? 
                      datos.detalle[0].REFERENCIA : 'REQ 0001 0034309';
    doc.text(referencias, xReferencias, yPos + 12);
    
    // ===== SECCIÓN DE FIRMAS MEJORADA =====
    const yFirma = Math.max(yPos, pageHeight - 60); // Asegurar que esté cerca del final
    const anchoFirma = 70;
    const separacionFirmas = (pageWidth - (margin * 2) - (anchoFirma * 2)) / 3;
    
    const xFirma1 = margin + separacionFirmas;
    const xFirma2 = xFirma1 + anchoFirma + separacionFirmas;
    
    // Líneas para firmas
    doc.setLineWidth(0.3);
    doc.line(xFirma1, yFirma, xFirma1 + anchoFirma, yFirma);
    doc.line(xFirma2, yFirma, xFirma2 + anchoFirma, yFirma);
    
    // Etiquetas de firmas
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.text('Entregado por', xFirma1 + (anchoFirma / 2), yFirma + 6, { align: 'center' });
    doc.text('Recibido Por', xFirma2 + (anchoFirma / 2), yFirma + 6, { align: 'center' });
    
    // Nombres de responsables
    doc.setFontSize(8);
    

   
    // Obtener nombre del usuario logueado desde el DOM
    const nombreEntrega= $('#usuario-logueado').val().trim() || 'Usuario';

    doc.text(nombreEntrega, xFirma1 + (anchoFirma / 2), yFirma + 12, { align: 'center' });

    doc.text(nombreEntrega, xFirma1 + (anchoFirma / 2), yFirma + 12, { align: 'center' });
    doc.text(encabezado.RESPONSABLE_NOMBRE, xFirma2 + (anchoFirma / 2), yFirma + 12, { align: 'center' });
    
    // ===== MOSTRAR PREVISUALIZACIÓN =====
    
    
    // Abrir en nueva ventana
    const pdfBlob = doc.output('blob');
    const pdfUrl = URL.createObjectURL(pdfBlob);
    
    const ventanaPDF = window.open(pdfUrl, '_blank', 'width=800,height=900,scrollbars=yes,resizable=yes');
    
    if (ventanaPDF) {
      
      setTimeout(() => URL.revokeObjectURL(pdfUrl), 60000);
    } else {
      console.warn("⚠️ Descargando PDF...");
      const nombreArchivo = `Salida_Interna_${encabezado.ID_SALIDA?.trim() || 'documento'}.pdf`;
      doc.save(nombreArchivo);
    }
    
  } catch (error) {
    console.error("❌ Error al crear PDF:", error);
    alert("Error al generar el PDF: " + error.message);
  }
}
 */

function AJScrearPrevisualizacionPDF(datos) {
  
  
  // Verificar que jsPDF esté disponible
  if (typeof jsPDF === 'undefined' && typeof window.jspdf === 'undefined') {
    console.error("❌ jsPDF no está disponible");
    alert("Error: La librería jsPDF no está cargada. Por favor, recarga la página.");
    return;
  }
  
  // Obtener la clase jsPDF
  const PDFClass = typeof jsPDF !== 'undefined' ? jsPDF : window.jspdf.jsPDF;
  
  try {
    // Crear nuevo documento PDF (formato A4)
    const doc = new PDFClass({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    // Configuración de página
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 8; // Margen ligeramente mayor para impresoras matriciales
    let yPos = margin;
    
    console.log(`📏 Dimensiones página: ${pageWidth}mm x ${pageHeight}mm`);
    
    const encabezado = datos.encabezado;
    
    // ===== ENCABEZADO DE LA EMPRESA (Optimizado para impresora matricial) =====
    doc.setFontSize(12); // Tamaño mayor para mejor legibilidad
    doc.setFont('courier', 'bold'); // Courier es ideal para impresoras matriciales
    doc.text('SOCIEDAD AGRICOLA DON LUIS S.A.', margin, yPos);
    yPos += 5;
    
    doc.setFontSize(10);
    doc.setFont('courier', 'normal');
    doc.text('CAL. CONTRALMIRANTE MONTERO NRO. 411 INT.', margin, yPos);
    yPos += 4;
    doc.text('RUC: 20325346435', margin, yPos);
    
    // ===== INFORMACIÓN SUPERIOR DERECHA =====
    const infoDerechaX = pageWidth - margin;
    doc.setFontSize(9);
    doc.setFont('courier', 'normal');
    doc.text('Pagina 1 de 1', infoDerechaX, margin, { align: 'right' });
    doc.text(encabezado.FECHA_IMPRESION, infoDerechaX, margin + 4, { align: 'right' });
    doc.text(encabezado.HORA_IMPRESION , infoDerechaX, margin + 8, { align: 'right' });
    
    yPos += 15;
    
    // ===== TÍTULO PRINCIPAL CENTRADO =====
    doc.setFontSize(14);
    doc.setFont('courier', 'bold');
    const numeroDocumento = encabezado.NUM_DOCUMENTO?.replace(/\s+/g, '-') || 'no encontrado';
    doc.text(`SALIDA INTERNA N° ${numeroDocumento}`, pageWidth/2, yPos, { align: 'center' });
    yPos += 15;
    
  
    
    // ===== INFORMACIÓN EN FORMATO DE ETIQUETAS (Optimizado) =====
    doc.setFontSize(9);
    doc.setFont('courier', 'normal');
    
    // Primera línea: Motivo y Almacen
    doc.setFont('courier', 'bold');
    doc.text('Motivo', margin, yPos);
    
    doc.setFont('courier', 'normal');
    const motivoTexto = `[${encabezado.IDMOTIVO || 'XX'}] ${encabezado.NOMBRE_MOTIVO || 'no encontrado'}`;
    // Truncar motivo si es muy largo para impresora matricial
    const motivoCorto = motivoTexto.length > 50 ? motivoTexto.substring(0, 37) + '...' : motivoTexto;
    doc.text(motivoCorto, margin + 22, yPos);
    
    doc.setFont('courier', 'bold');
    doc.text('Almacen', margin + 105, yPos);
    
    doc.setFont('courier', 'normal');
    const almacenTexto = `[${encabezado.IDALMACEN || '001'}] ${encabezado.ALMACEN_DESCRIPCION || 'ALMACEN CENTRAL'}`;
    // Truncar almacen si es muy largo
    const almacenCorto = almacenTexto.length > 30 ? almacenTexto.substring(0, 27) + '...' : almacenTexto;
    doc.text(almacenCorto, margin + 125, yPos);
    yPos += 6;
    
    // Segunda línea: Fecha Salida y Sucursal
    doc.setFont('courier', 'bold');
    doc.text('Fecha Salida', margin, yPos);
    
    doc.setFont('courier', 'normal');
    doc.text(encabezado.FECHA_SALIDA || '02/07/2025', margin + 30, yPos);
    
    doc.setFont('courier', 'bold');
    doc.text('Sucursal', margin + 105, yPos);
    
    doc.setFont('courier', 'normal');
    const sucursalTexto = `[${encabezado.IDEMPRESA || '001'}] ${encabezado.SUCURSAL || 'no encontrado'}`;
    // Truncar sucursal si es muy larga
    const sucursalCorto = sucursalTexto.length > 39 ? sucursalTexto.substring(0, 32) + '...' : sucursalTexto;
    doc.text(sucursalCorto, margin + 125, yPos);
    yPos += 12;
    
    
    
    // ===== CONFIGURACIÓN DE TABLA OPTIMIZADA PARA MATRICIAL =====
    const tablaAncho = pageWidth + 5 - (margin * 2);
    const alturaFila = 5; // Altura reducida para menos espacio entre filas
    
    // Configuración de columnas optimizada para impresora matricial
    const columnas = [
      { header: 'Item', width: 11, align: 'center' },
      { header: 'Codigo', width: 20, align: 'left' },
      { header: 'Descripcion', width: 88, align: 'left' },
      { header: 'U.M', width: 10, align: 'center' },
      { header: 'Cant.', width: 15, align: 'right' },
      { header: 'Consumidor', width: 55, align: 'left' }
    ];
    
    // Guardar posición inicial de la tabla
    const tablaInicio = yPos;
    
    // ===== DIBUJAR ENCABEZADO DE TABLA =====
    doc.setFont('courier', 'bold');
    doc.setFontSize(8); // Tamaño optimizado para matricial
    doc.setLineWidth(0.3);
    
    // Dibujar borde superior de la tabla
    doc.line(margin, yPos, margin + tablaAncho, yPos);
    
    // Guardar posición del encabezado para líneas verticales
    const yEncabezado = yPos;
    
    let xActual = margin;
    columnas.forEach((col, index) => {
      // Texto del encabezado
      const xTexto = col.align === 'center' ? xActual + (col.width / 2) : 
                     col.align === 'right' ? xActual + col.width - 2 : xActual + 2;
      doc.text(col.header, xTexto, yPos + 4, { align: col.align });
      xActual += col.width;
    });
    
    yPos += alturaFila;
    
    // Línea horizontal después del encabezado
    doc.line(margin, yPos, margin + tablaAncho, yPos);
    
    // ===== DATOS DE PRODUCTOS OPTIMIZADO PARA MATRICIAL =====
    doc.setFont('courier', 'normal');
    doc.setFontSize(7); // Tamaño optimizado para que quepa más información en matricial
    
    if (datos.detalle && datos.detalle.length > 0) {
      datos.detalle.forEach((producto, index) => {
        // Verificar si necesitamos una nueva página
        if (yPos > pageHeight - 50) { // Dejar espacio para firmas
          doc.addPage();
          yPos = margin;
        }
        
        xActual = margin;
        let filaActual = yPos;
        let alturaFilaActual = alturaFila;
        
        // Item - centrado
        const item = producto.ITEM || (index + 1).toString().padStart(3, '0');
        doc.text(item, xActual + (columnas[0].width / 2), filaActual + 3, { align: 'center' });
        xActual += columnas[0].width;
        
        // Código - truncado optimizado
        const codigo = (producto.CODIGO || 'N/A').trim();
        const codigoTruncado = codigo.length > 15 ? codigo.substring(0, 12) + '...' : codigo;
        doc.text(codigoTruncado, xActual + 2, filaActual + 3);
        xActual += columnas[1].width;
        
        // Descripción - manejo inteligente de texto largo
        const descripcion = producto.DESCRIPCION || 'Sin descripcion';
        const maxCharsDescripcion = 45; // Caracteres por línea para matricial
        
        if (descripcion.length <= maxCharsDescripcion) {
          // Descripción corta - una sola línea
          doc.text(descripcion, xActual + 2, filaActual + 3);
        } else {
          // Descripción larga - dividir en líneas
          const palabras = descripcion.split(' ');
          let lineasDescripcion = [];
          let lineaActual = '';
          
          palabras.forEach(palabra => {
            if ((lineaActual + ' ' + palabra).length <= maxCharsDescripcion) {
              lineaActual += (lineaActual ? ' ' : '') + palabra;
            } else {
              if (lineaActual) lineasDescripcion.push(lineaActual);
              lineaActual = palabra;
            }
          });
          if (lineaActual) lineasDescripcion.push(lineaActual);
          
          // Limitar a máximo 2 líneas para matricial
          lineasDescripcion = lineasDescripcion.slice(0, 2);
          if (lineasDescripcion.length === 2 && descripcion.length > maxCharsDescripcion * 2) {
            lineasDescripcion[1] = lineasDescripcion[1].substring(0, maxCharsDescripcion - 3) + '...';
          }
          
          lineasDescripcion.forEach((linea, idx) => {
            doc.text(linea, xActual + 2, filaActual + 3 + (idx * 2.5));
          });
          
          // Ajustar altura de fila si hay múltiples líneas
          if (lineasDescripcion.length > 1) {
            alturaFilaActual = alturaFila + ((lineasDescripcion.length - 1) * 2.5);
          }
        }
        xActual += columnas[2].width;
        
        // U.M - centrado
        const unidad = (producto.UNIDAD_MEDIDA || 'UND').trim();
        doc.text(unidad, xActual + (columnas[3].width / 2), filaActual + 3, { align: 'center' });
        xActual += columnas[3].width;
        
        // Cantidad - alineada a la derecha con formato matricial
        const cantidad = parseFloat(producto.CANTIDAD || '0').toFixed(3);
        doc.text(cantidad, xActual + columnas[4].width - 2, filaActual + 3, { align: 'right' });
        xActual += columnas[4].width;
        
        // Consumidor - truncado para matricial
        // Obtener el valor original del consumidor
        let consumidorRaw = `[${producto.IDCONSUMIDOR.trim() || 'N/A'}] ${producto.CONSUMIDOR || 'N/A'}`;

        // Extraer solo la parte del consumidor (sin el ID entre corchetes)
        let consumidorTexto = producto.CONSUMIDOR || 'N/A';

        // Verificar si contiene "UVA" (case insensitive)
        if (consumidorTexto.toUpperCase().includes('UVA')) {
          
          
          // Buscar la posición de "UVA"
          const palabras = consumidorTexto.split(' ');
          const indiceUva = palabras.findIndex(palabra => palabra.toUpperCase() === 'UVA');
          
          if (indiceUva !== -1 && indiceUva + 2 < palabras.length) {
            // Tomar desde el inicio hasta UVA + las siguientes 2 palabras
            // Ejemplo: "LOTE C-1 UVA SWEET CELEBRATION CABILDO" -> "LOTE C-1 UVA SWEET CELEBRATION"
            const palabrasHastaUvaMasDos = palabras.slice(0, indiceUva + 3);
            consumidorTexto = palabrasHastaUvaMasDos.join(' ');
            
          } else if (indiceUva !== -1) {
            // Si no hay suficientes palabras después de UVA, tomar hasta UVA + lo que haya
            const palabrasHastaFin = palabras.slice(0, indiceUva + 2);
            consumidorTexto = palabrasHastaFin.join(' ');
            
          }
        }

        // Construir el texto final con ID + consumidor procesado
        let consumidorFinal = `[${producto.IDCONSUMIDOR.trim() || 'N/A'}] ${consumidorTexto}`;

        // Aplicar la lógica de truncamiento si es muy largo
        const consumidorTruncado = consumidorFinal.length > 35 ? 
                                  consumidorFinal.substring(0, 35) + '.' : consumidorFinal;

        doc.text(consumidorTruncado, xActual + 2, filaActual + 3);

        // Actualizar yPos según la altura de la fila actual
        yPos += alturaFilaActual;
        
        // NO dibujar líneas horizontales después de cada fila del cuerpo
      });
      
      // ===== NO DIBUJAR LÍNEAS VERTICALES DE LA TABLA =====
      // Comentamos esta sección para eliminar las líneas verticales
      /*
      let xLinea = margin;
      doc.line(xLinea, yEncabezado, xLinea, yPos);
      
      columnas.forEach((col) => {
        xLinea += col.width;
        doc.line(xLinea, yEncabezado, xLinea, yPos);
      });
      */

    } else {
      // Si no hay productos, agregar una fila vacía
      yPos += alturaFila;
    }
    
    // Dibujar línea de cierre de la tabla
    doc.line(margin, yPos, margin + tablaAncho, yPos);
    
    // ===== SECCIÓN DE OBSERVACIONES Y REFERENCIAS (PEGADA AL CONTENIDO) =====
    yPos += 8; // Espacio mínimo después de la tabla
    
    // Verificar si hay espacio suficiente para observaciones y firmas, si no, nueva página
    if (yPos > pageHeight - 60) {
      doc.addPage();
      yPos = margin;
    }
    
    // OBSERVACIONES (lado izquierdo)
    doc.setFont('courier', 'bold');
    doc.setFontSize(9);
    doc.text('Observaciones', margin, yPos);
    
    doc.setFont('courier', 'normal');
    doc.setFontSize(8);
    const observaciones = encabezado.OBSERVACIONES && encabezado.OBSERVACIONES.trim() ? 
                        encabezado.OBSERVACIONES : 'requerimiento para uso en oficina - rosa vera';
    
    // Procesar observaciones optimizado para matricial
    const maxCharsObsLinea = 50; // Optimizado para matricial
    const lineasObs = [];
    let textoRestante = observaciones;
    
    while (textoRestante.length > 0 && lineasObs.length < 3) { // Máximo 3 líneas
      if (textoRestante.length <= maxCharsObsLinea) {
        lineasObs.push(textoRestante);
        break;
      }
      
      let corte = maxCharsObsLinea;
      const ultimoEspacio = textoRestante.lastIndexOf(' ', corte);
      if (ultimoEspacio > corte * 0.7) {
        corte = ultimoEspacio;
      }
      
      lineasObs.push(textoRestante.substring(0, corte));
      textoRestante = textoRestante.substring(corte).trim();
    }
    
    yPos += 5;
    lineasObs.forEach((linea, index) => {
      doc.text(linea, margin, yPos + (index * 4));
    });
    
    // REFERENCIAS (lado derecho)
    const xReferencias = margin + 110;
    doc.setFont('courier', 'bold');
    doc.setFontSize(9);
    doc.text('Referencias', xReferencias, yPos - 5);
    
    doc.setFont('courier', 'normal');
    doc.setFontSize(8);
    const referencias = (datos.detalle && datos.detalle[0] && datos.detalle[0].REFERENCIA) ? 
                      datos.detalle[0].REFERENCIA : '0002 0028542';
    doc.text(referencias, xReferencias, yPos);
    
    // Actualizar yPos después de observaciones/referencias
    yPos += Math.max(lineasObs.length * 4, 8) + 10;
    
    // ===== SECCIÓN DE FIRMAS (PEGADA AL CONTENIDO Y DINÁMICA) =====
    // Verificar si hay espacio suficiente para las firmas, si no, nueva página
    if (yPos > pageHeight - 40) {
      doc.addPage();
      yPos = margin;
    }
    
    // Las firmas van inmediatamente después del contenido, no al final de la página
    const yFirma = yPos;
    const anchoFirma = 65; // Ancho optimizado para matricial
    const separacionFirmas = (pageWidth - (margin * 2) - (anchoFirma * 2)) / 3;
    
    const xFirma1 = margin + separacionFirmas;
    const xFirma2 = xFirma1 + anchoFirma + separacionFirmas;
    
    // Líneas para firmas más gruesas para matricial
    doc.setLineWidth(0.3);

    doc.line(xFirma1, yFirma, xFirma1 + anchoFirma, yFirma);
    doc.line(xFirma2, yFirma, xFirma2 + anchoFirma, yFirma);
    
    // Etiquetas de firmas optimizadas para matricial
    doc.setFont('courier', 'bold');
    doc.setFontSize(8);
    doc.text('Entregado por', xFirma1 + (anchoFirma / 2), yFirma + 6, { align: 'center' });
    doc.text('Recibido Por', xFirma2 + (anchoFirma / 2), yFirma + 6, { align: 'center' });
    
    // Nombres de responsables
    doc.setFont('courier', 'normal');
    doc.setFontSize(7);
    
    // Obtener nombre del responsable entregador
    const nombreEntrega = $('#usuario-logueado').val().trim() || 'Usuario';
    // Truncar nombres largos para matricial
    const nombreEntregaTruncado = nombreEntrega.length > 30 ? 
                                 nombreEntrega.substring(0, 17) + '...' : nombreEntrega;

    const nombreRecibe = encabezado.RESPONSABLE_NOMBRE|| 'Usuario';
    const nombreRecibeTruncado = nombreRecibe.length > 30 ?
                                nombreRecibe.substring(0, 17) + '...' : nombreRecibe;
    
    doc.text(nombreEntregaTruncado, xFirma1 + (anchoFirma / 2), yFirma + 12, { align: 'center' });
    doc.text(nombreRecibeTruncado, xFirma2 + (anchoFirma / 2), yFirma + 12, { align: 'center' });
    
    // ===== MOSTRAR PREVISUALIZACIÓN =====
    
    
    // Abrir en nueva ventana
    const pdfBlob = doc.output('blob');
    const pdfUrl = URL.createObjectURL(pdfBlob);
    
    const ventanaPDF = window.open(pdfUrl, '_blank', 'width=800,height=900,scrollbars=yes,resizable=yes');
    
    if (ventanaPDF) {
      console.log("✅ PDF abierto en nueva ventana para previsualización");
      // Limpiar URL después de 60 segundos
      setTimeout(() => URL.revokeObjectURL(pdfUrl), 60000);
    } else {
      console.warn("⚠️ No se pudo abrir ventana, descargando PDF...");
      const nombreArchivo = `Salida_Interna_${encabezado.ID_SALIDA?.trim() || 'documento'}.pdf`;
      doc.save(nombreArchivo);
    }
    
  } catch (error) {
    console.error("❌ Error al crear PDF:", error);
    alert("Error al generar el PDF: " + error.message);
  }
}

