$(document).ready(function () {
  iniciarTablaReqInternosDL();
  $("#modalDetallesRequerimiento").on("hidden.bs.modal", function () {
    limpiarTablaStock();
  });
});

//================================================================================================================
// INICIALIZAR LA TABLA DE REQUERIMIENTOS INTERNOS RESUMEN
//================================================================================================================
function iniciarTablaReqInternosDL() {
  const tabla = new DataTable("#tablaReqInternosDL", {
    responsive: true,
    autoWidth: false,
    pageLength: 10,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: "/almacen/api/req_interno_dl/",
      type: "GET",
      dataSrc: function (json) {
        // Convertir la fecha de formato ISO a DD/MM/YYYY
        json.data.forEach(function (item) {
          // Separar el string de la fecha
          const partes = item.fecha.split("/");
          // partes[0] = día, partes[1] = mes, partes[2] = año
          if (partes.length === 3) {
            // Crear la fecha correctamente (mes en JS es 0-indexado)
            const fecha = new Date(partes[2], partes[1] - 1, partes[0]);
            item.fecha = fecha.toLocaleDateString("es-ES");
          } else {
            item.fecha = "Fecha inválida";
          }
        });
        return json.data;
      },
    },
    columns: [
      { data: "fecha", title: "Fecha" },
      { data: "sucursal", title: "Sucursal" },
      { data: "almacen", title: "Almacén" },
      { data: "documento", title: "Documento" },
      { data: "responsable", title: "Responsable" },
      { data: "area", title: "Área" },
      { data: "motivo", title: "Motivo" },
      {
        data: "estado",
        title: "Estado",
        render: function (data, type, row) {
          // Usar el estado_clase que viene directamente de la API
          return `<span class="badge ${row.estado_clase}">${data}</span>`;
        },
      },
      { data: "nota_uso", title: "Nota/Uso" },
    ],
    order: [[1, "asc"]],
  });

  // Agregar evento de clic en la tabla para mostrar detalles
  $("#tablaReqInternosDL tbody").on("click", "tr", function () {
    const data = tabla.row(this).data();

    // Abrir el modal de detalles
    abrirModalDetalles(data);
  });
}

//================================================================================================================
// FUNCIONES PARA GESTIONAR EL MODAL DE DETALLES
//================================================================================================================

// Función para abrir el modal y cargar los datos del requerimiento

function abrirModalDetalles(Requerimiento) {
  if ($.fn.DataTable.isDataTable("#tablaDetalleProductos")) {
    $("#tablaDetalleProductos").DataTable().destroy();
  }

  // resetear el modal
  $("#modalDetallesRequerimiento").modal("hide");

  // mostrar el modal
  $("#modalDetallesRequerimiento").modal("show");

  //TITULO DEL MODAL
  $("#req-numero-documento").text(
    Requerimiento.documento || "no hay documento"
  );
  $("#req-fecha-documento").text(Requerimiento.fecha || "no hay fecha");
  $("#req-estado-documento").text(Requerimiento.estado || "no hay estado");

  // Cambiar color del contenedor del estado según el valor
  const estadoContainer = $("#req-estado-documento").parent();
  const estado = (Requerimiento.estado || "").toLowerCase();

  // Remover clases previas de color
  estadoContainer.removeClass(
    "bg-warning bg-danger bg-success bg-info bg-secondary"
  );

  // Asignar color según el estado
  if (estado.includes("pendiente") || estado === "pe") {
    estadoContainer.addClass("bg-warning text-dark"); // Anaranjado
  } else if (
    estado.includes("rechazado") ||
    estado.includes("cancelado") ||
    estado.includes("anulado")
  ) {
    estadoContainer.addClass("bg-danger text-white"); // Rojo
  } else if (estado.includes("aprobado") || estado === "ap") {
    estadoContainer.addClass("bg-success text-white"); // Verde
  } else if (estado.includes("atendido") || estado === "at") {
    estadoContainer.addClass("bg-info text-white"); // Azul
  } else {
    estadoContainer.addClass("bg-secondary text-white"); // Gris por defecto
  }

  // cargar los datos en el modal
  $("#req-periodo").val(Requerimiento.PERIODO || "no hay periodo");
  $("#req-punto-emision-codigo").val(
    Requerimiento.IDEMISOR || "no hay punto de emisión"
  );
  $("#req-punto-emision-nombre").val(
    Requerimiento.PUNTO_EMISION || "no hay punto de emisión"
  );
  $("#req-sucursal-nombre").val(Requerimiento.sucursal || "no hay sucursal");
  $("#req-almacen-nombre").val(Requerimiento.almacen || "no hay almacen");
  $("#req-documento").val(Requerimiento.documento || "no hay documento");
  $("#req-responsable-nombre").val(
    Requerimiento.responsable || "no hay responsable"
  );
  $("#req-area-nombre").val(Requerimiento.area || "no hay area");
  $("#req-observaciones").val(Requerimiento.nota_uso || "no hay observaciones");

  // #########################################################################################
  // TABLA DE DETALLES DE LOS ARTICULOS
  // #########################################################################################

  // CARGAR DATOS EN LA TABLA DE DETALLES DE LOS ARTICULOS
  const idReqInterno = Requerimiento.IDREQINTERNO;

  // CARGAR DATOS EN LA TABLA DE DETALLES DE LOS ARTICULOS
  // PASO 6: Inicializar nueva tabla con los datos de la API

  const tablaDetalles = new DataTable("#tablaDetalleProductos", {
    destroy: true,
    responsive: true,
    autoWidth: false,
    pageLength: 10,
    processing: true,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      zeroRecords: "No se encontraron detalles",
      emptyTable: "No hay datos disponibles en la tabla",
    },
    ajax: {
      url: `/almacen/api/req_internoDetalle_dl/${idReqInterno}/`,
      type: "GET",
      dataSrc: function (json) {
        loading = false;

        if (
          json.status === "success" &&
          Array.isArray(json.data) &&
          json.data.length > 0
        ) {
          // Modificar los datos para manejar valores nulos
          return json.data.map((item) => {
            return {
              ...item,
              // Garantizar que ningún valor sea null para evitar errores en DataTables
              DESTINO: item.DESTINO || "No especificado",
              IDACTIVIDAD: item.IDACTIVIDAD || "N/A",
              ACTIVIDAD: item.ACTIVIDAD || "No especificado",
            };
          });
        } else {
          // Mostrar mensaje después de que se complete la tabla
          setTimeout(() => {
            if (!$("#mensaje-sin-datos").length) {
              $("#tablaDetalleProductos_wrapper").append(
                '<div id="mensaje-sin-datos" class="alert alert-info mt-3">No hay detalles disponibles para este requerimiento</div>'
              );
            }
          }, 500);

          return [];
        }
      },
      error: function (xhr, error, thrown) {
        loading = false;

        return [];
      },
    },
    columns: [
      { data: "ITEM", defaultContent: "-" },
      { data: "IDPRODUCTO", defaultContent: "-" },
      { data: "PRODUCTO", defaultContent: "-" },
      { data: "IDMEDIDA", defaultContent: "-" },
      {
        data: "CANTIDAD",
        defaultContent: "0.00",
        render: function (data) {
          if (!data) return "0.00";
          return parseFloat(data).toFixed(2);
        },
      },
      //{ data: "IDDESTINO", defaultContent: "-" },
      //{ data: "DESTINO", defaultContent: "-" },
      { data: "IDCONSUMIDOR", defaultContent: "-" },
      { data: "CONSUMIDOR", defaultContent: "-" },
      { data: "OBSERVACIONES", defaultContent: "-" },
      {
        data: "ATENDIDO",
        defaultContent: "0",
        render: function (data) {
          return data === "0"
            ? '<span class="badge bg-danger">No</span>'
            : '<span class="badge bg-success">Sí</span>';
        },
      },
      //{ data: "IDACTIVIDAD", defaultContent: "-" },
      //{ data: "ACTIVIDAD", defaultContent: "-" },
      {
        data: "ESTADOS",
        defaultContent: "-",
        render: function (data) {
          if (!data)
            return '<span class="badge bg-secondary">Sin estado</span>';

          switch (data.trim()) {
            case "PE":
              return '<span class="badge bg-warning">Pendiente</span>';
            case "AP":
              return '<span class="badge bg-success">Aprobado</span>';
            case "AT":
              return '<span class="badge bg-info">Atendido</span>';
            default:
              return `<span class="badge bg-secondary">${data}</span>`;
          }
        },
      },
    ],

    // Agregar evento de clic en las filas
    rowCallback: function (row, data) {
      $(row).on("click", function () {
        //SACAR FUERA DE LA TABLA LA VARIEBLE CON EL IDPRODUCTO
        const idProducto = data.IDPRODUCTO;

        //MOSTRAR EL MODAL DE DETALLES DEL PRODUCTO
        cargarTablaStock(idProducto);
      });
    },
  });
}

//================================================================================================================
// FUNCIÓN PARA CARGAR LA TABLA DE STOCK DEL PRODUCTO
//================================================================================================================
function cargarTablaStock(idProducto) {
  // Limpiar tabla anterior si existe
  if ($.fn.DataTable.isDataTable("#tablaStockProductos")) {
    $("#tablaStockProductos").DataTable().destroy();
  }

  // Limpiar contenido pero mantener estructura
  $("#tablaStockProductos tbody").empty();

  console.log("Cargando stock para producto:", idProducto);

  const tablaStock = new DataTable("#tablaStockProductos", {
    destroy: true,
    responsive: true,
    autoWidth: false,
    pageLength: 1,
    searching: false,
    ordering: false,
    info: false,
    lengthChange: false,
    processing: true,
    paging: false,
    footerCallback: function (row, data, start, end, display) {
      console.log("Footer callback ejecutado");
      const api = this.api();

      // Calcular totales
      const totalStock = api
        .column(2, { page: "current" })
        .data()
        .reduce(function (a, b) {
          return parseFloat(a) + parseFloat(b || 0);
        }, 0);

      const totalDisponible = api
        .column(3, { page: "current" })
        .data()
        .reduce(function (a, b) {
          return parseFloat(a) + parseFloat(b || 0);
        }, 0);

      console.log(
        "Totales calculados - Stock:",
        totalStock,
        "Disponible:",
        totalDisponible
      );

      // Mostrar totales en el footer
      $(api.column(1).footer()).html("<strong>TOTAL:</strong>");
      $(api.column(2).footer()).html(
        `<strong style="background-color: #d4edda; color: #155724; display: block; padding: 2px 4px; border-radius: 3px;">${totalStock.toFixed(
          3
        )}</strong>`
      );
      $(api.column(3).footer()).html(
        `<strong>${totalDisponible.toFixed(3)}</strong>`
      );
    },
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
    },
    ajax: {
      url: `/almacen/api/stock_producto/${idProducto}/`,
      type: "GET",
      dataSrc: function (json) {
        console.log("Datos recibidos:", json);
        return json.data;
      },
    },
    initComplete: function (settings, json) {
      console.log("Tabla inicializada completamente");
      // Forzar la ejecución del footerCallback si hay datos
      if (json && json.data && json.data.length > 0) {
        console.log("Forzando recálculo del footer...");
        this.api().draw();
      }
    },
    columns: [
      { data: "IDEMPRESA", title: "Empresa" },
      {
        data: "IDLOTE",
        title: "Lote",
        render: function (data, type, row) {
          // Verificar si el valor está vacío, es null, undefined o solo espacios en blanco
          if (!data || data.toString().trim() === "") {
            return "SIN LOTE";
          }
          return data;
        },
      },
      //{ data: "ALMACEN", title: "Almacén" },
      {
        data: "STOCK_REAL",
        title: "Stock",
        render: function (data, type, row) {
          return `<span style="background-color: #d4edda; color: #155724; display: block; padding: 1px 2px; border-radius: 1px; font-weight: bold;">${data}</span>`;
        },
      },
      { data: "STOCK_SALDO", title: "Disponible" },
    ],
  });
}

//================================================================================================================
// FUNCIÓN PARA LIMPIAR LA TABLA DE STOCK
//================================================================================================================
function limpiarTablaStock() {
  if ($.fn.DataTable.isDataTable("#tablaStockProductos")) {
    $("#tablaStockProductos").DataTable().destroy();
  }
  // Solo limpiar tbody, mantener el tfoot para que se pueda regenerar
  $("#tablaStockProductos tbody").empty();
  // Agregar mensaje de placeholder
  $("#tablaStockProductos tbody").html(`
    <tr>
      <td colspan="4" class="text-center">
        <span class="text-muted">
          <i class="fa fa-info-circle me-1"></i>Seleccione un producto
        </span>
      </td>
    </tr>
  `);
}
