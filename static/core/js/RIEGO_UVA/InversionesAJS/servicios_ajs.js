$(document).ready(function () {
  initServiciosTable();
  actualizarTotalWidget();
  $(".descripcion_servicios").select2();
  actualizarTotalesServicios();
});

function initServiciosTable() {
  // Obtener el año seleccionado del filtro o usar el año actual
  var yearVal = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();
  
  var table = $("#serviciosTable").DataTable({
    drawCallback: function (settings) {
      actualizarTotalesServicios();
    },
    // botón de exportar a excel
    dom: "Bfrtip",
    buttons: [
      {
        text: '<i class="fas fa-sync-alt"></i>',
        className: "btn-sm btn-secondary",
        action: function (e, dt, node, config) {
          // Añadir animación de giro
          $(node).find("i").addClass("fa-spin");
          
          // Obtener año actual del filtro
          var currentYear = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

          // Recargar la tabla con el año correcto
          dt.ajax.url("/riegouva/produccionpalta_servicios_ajs/?year=" + currentYear).load(function () {
            // Callback después de la recarga
            setTimeout(() => {
              $(node).find("i").removeClass("fa-spin");
            }, 1000);

            // Actualizar totales
            actualizarTotalWidget();
          });
        },
      },
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_SERVICIOS",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          {
            template: "green_medium",
          },
        ],
      },
      {
        extend: "pdfHtml5",
        title: "RPT_PRESUPUESTO_SERVICIOS",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 11;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = Array(colCount).fill("*");

          // Dar más espacio a la columna de observación
          widths[6] = "*"; // Ajusta el índice según la posición de la columna
          doc.content[1].table.widths = widths;

          // Reducir márgenes
          doc.pageMargins = [10, 10, 10, 10];

          // Ajustar el contenido para que quepa en una página
          doc.content[1].table.keepWithHeaderRows = 1;
          doc.content[1].table.body.forEach(function (row) {
            row.forEach(function (cell) {
              cell.alignment = "left";
            });
          });
        },
        exportOptions: {
          columns: ":visible",
          format: {
            body: function (data, row, column, node) {
              // Acortar texto largo si es necesario
              return data.length > 20 ? data.substr(0, 20) + "..." : data;
            },
          },
        },
      },
      {
        text: '<i class="fas fa-plus mr-1"></i>AGREGAR',
        className: "btn-sm btn-success btn-agregar",
        action: function (e, dt, node, config) {
          $("#Modal_Servicios").modal("show");
        },
      },
    ],

    scrollX: true,
    scrollY: 250,
    autoWidth: false,
    scrollCollapse: true,

    serverSide: false,
    searching: false,
    pageLength: 7,

    language: {
      url: dataTableEsUrl,
    },

    // ajax para obtener los datos de la tabla
    ajax: {
      url: "/riegouva/produccionpalta_servicios_ajs/?year=" + ($('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear()),
      dataSrc: "data",
    },

    fixedColumns: {
      right: 1, // Fija la última columna (acciones) a la derecha
      left: 3, // Fija las columnas de N°, idproducto, observación y acciones a la izquierda
    },

    columns: [
      { data: "id", title: "ID", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center sticky-col-left sticky-col-left-1",
        render: function (data, type, row, meta) {
          return meta.row + 1;
        },
      },

      /* { data: "grupo_servicio", title: "Grupo" },
      { data: "subgrupo_servicio", title: "Subgrupo" }, */

      {
        data: "idproducto",
        title: "ID Producto",
        className: "sticky-col-left sticky-col-left-2",
      },
      {
        data: "descripcion",
        title: "Descripción",
        className:
          "text-end descripcion-column sticky-col-left sticky-col-left-3",
      },
      {
        data: "observacion",
        title: "Observación",
        render: function (data, type, row) {
          if (type === "display") {
            // Si no hay observación, mostrar un guión
            if (!data) return "-";

            // Si la observación es muy larga, mostrar un tooltip
            if (data.length > 30) {
              return `<span title="${data}">${data.substring(0, 30)}...</span>`;
            }
            return data;
          }
          return data;
        },
      },
      {
        data: "precio_unitario",
        title: "Precio Unitario",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Enero
      {
        data: "enero_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "enero_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Febrero
      {
        data: "febrero_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "febrero_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Marzo
      {
        data: "marzo_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "marzo_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Abril
      {
        data: "abril_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "abril_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Mayo
      {
        data: "mayo_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "mayo_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Junio
      {
        data: "junio_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "junio_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Julio
      {
        data: "julio_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "julio_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Agosto
      {
        data: "agosto_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "agosto_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Septiembre
      {
        data: "septiembre_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "septiembre_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Octubre
      {
        data: "octubre_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "octubre_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Noviembre
      {
        data: "noviembre_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "noviembre_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      // Diciembre
      {
        data: "diciembre_cantidad",
        title: "Cant.",
        className: "text-center",
      },
      {
        data: "diciembre_precio",
        title: "Total",
        render: function (data) {
          return "S/. " + parseFloat(data).toFixed(2);
        },
      },
      {
        data: null,
        title: "Total",
        render: function (data, type, row) {
          let total = 0;
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];
          meses.forEach((mes) => {
            total += parseFloat(row[mes + "_precio"]) || 0;
          });
          return "S/. " + total.toFixed(2);
        },
      },
      {
        data: null,
        title: "Acciones",
        className: "sticky-col",
        render: function (data, type, row) {
          return `
                    <button class="btn btn-sm btn-primary editar-servicio" data-id="${row.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger eliminar-servicio" data-id="${row.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
        },
      },
    ],

    responsive: true,
    ordering: true,
    order: [[0, "desc"]],
    destroy: true,


    footerCallback: function (row, data, start, end, display) {
      var api = this.api();

      // Limpiar las columnas iniciales
      for (let i = 0; i <= 5; i++) {
        $(api.column(i).footer()).html(
          i === 5 ? "<strong>TOTALES</strong>" : ""
        );
      }

      // Calcular totales directamente de los datos de la tabla
      var tableData = api.rows().data().toArray();
      
      const meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
      ];
      
      const mesesCapitalized = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
      ];
      
      var totalGeneral = 0;
      
      meses.forEach((mes, index) => {
        var totalCantidad = 0;
        var totalPrecio = 0;
        
        // Sumar los valores de cada fila para este mes
        tableData.forEach(function(row) {
          totalCantidad += parseFloat(row[mes + "_cantidad"]) || 0;
          totalPrecio += parseFloat(row[mes + "_precio"]) || 0;
        });
        
        totalGeneral += totalPrecio;
        
        const cantidadIndex = 6 + index * 2;
        const precioIndex = cantidadIndex + 1;

        // Formatear cantidad
        $(api.column(cantidadIndex).footer()).html(`
          <div class="text-center">
            <strong>${formatNumber(totalCantidad)}</strong>
          </div>
        `);

        // Formatear precio
        $(api.column(precioIndex).footer()).html(`
          <div class="text-right">
            <strong>S/. ${formatNumber(totalPrecio, 2)}</strong>
          </div>
        `);
      });

      // Total general
      const totalGeneralIndex = api.columns().nodes().length - 2;
      $(api.column(totalGeneralIndex).footer()).html(`
        <div class="text-right">
          <strong>S/. ${formatNumber(totalGeneral, 2)}</strong>
        </div>
      `);

      // Actualizar widget con el total de la campaña seleccionada
      $("#stats_serviciosterceros").html(
        `S/. ${formatNumber(totalGeneral, 2)}`
      );
    },
  });
  function formatNumber(number, decimals = 0) {
    return Number(number).toLocaleString("es-PE", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }
}

function formatearMonedaPEN(monto) {
  return (
    "S/. " +
    parseFloat(monto)
      .toFixed(2)
      .replace(/\B(?=(\d{3})+(?!\d))/g, ",")
  );
}
//Actualizar el total cuando se realizan operaciones CRUD
function actualizarTotalWidget() {
  var yearVal = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();
  $.ajax({
    url: `/riegouva/produccionpalta_servicios_totals_ajs/?year=${yearVal}`,
    type: "GET",
    success: function (response) {
      const montoFormateado = formatearMonedaPEN(
        response.Total_General_Precio || 0
      );

      // Actualizar el widget principal
      $("#stats_serviciosterceros").html(montoFormateado);

      // Actualizar el widget consolidado
      $("#stats_serviciosterceros_consolidado").html(montoFormateado);
    },
    error: function (xhr, status, error) {
      console.error("Error al actualizar total widget:", error);
    },
  });
}

$("#grupo_servicio").change(function () {
  const grupoId = $(this).val();
  console.log("Grupo seleccionado:", grupoId); // Para debugging

  const subgrupoSelect = $("#subgrupo_servicio");
  const descripcionSelect = $("#descripcion_servicios");

  // Limpiar y deshabilitar selects
  subgrupoSelect
    .empty()
    .append('<option value="">Seleccione un subgrupo de servicios</option>');
  descripcionSelect
    .empty()
    .append('<option value="">Seleccione un servicio</option>');

  if (grupoId) {
    subgrupoSelect.prop("disabled", true); // Deshabilitar mientras carga

    $.ajax({
      url: `/api_subgrupos_servicios/${grupoId}/`, // URL actualizada
      type: "GET",
      beforeSend: function () {
        subgrupoSelect.append('<option value="">Cargando...</option>');
      },
      success: function (response) {
        subgrupoSelect
          .empty()
          .append(
            '<option value="">Seleccione un subgrupo de servicios</option>'
          );

        if (response.subgrupos && response.subgrupos.length > 0) {
          response.subgrupos.forEach(function (subgrupo) {
            subgrupoSelect.append(
              `<option value="${subgrupo.id}">${subgrupo.id} - ${subgrupo.descripcion}</option>`
            );
          });
          subgrupoSelect.prop("disabled", false);
        } else {
          subgrupoSelect.append(
            '<option value="">No hay subgrupos disponibles</option>'
          );
        }
      },
      error: function (error) {
        console.error("Error al cargar subgrupos:", error);
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudieron cargar los subgrupos",
        });
      },
      complete: function () {
        subgrupoSelect.find('option:contains("Cargando...")').remove();
      },
    });
  } else {
    subgrupoSelect.prop("disabled", true);
    descripcionSelect.prop("disabled", true);
  }
});

// Agregar después del evento change del grupo_servicio
$("#subgrupo_servicio").change(function () {
  const grupoId = $("#grupo_servicio").val();
  const subgrupoId = $(this).val();
  const descripcionSelect = $("#descripcion_servicio");
  const idProductoInput = $("#idproducto_servicios");
  const precioUnitarioInput = $("#precio_unitario_servicios");

  // Limpiar y deshabilitar select de descripción
  descripcionSelect
    .empty()
    .append('<option value="">Seleccione un servicio</option>');
  idProductoInput.val("");
  precioUnitarioInput.val("");

  if (grupoId && subgrupoId) {
    descripcionSelect.prop("disabled", true);

    $.ajax({
      url: "/api_descripciones_servicios/",
      type: "GET",
      data: {
        grupo: grupoId,
        subgrupo: subgrupoId,
      },
      beforeSend: function () {
        descripcionSelect.append('<option value="">Cargando...</option>');
      },
      success: function (response) {
        descripcionSelect
          .empty()
          .append('<option value="">Seleccione un servicio</option>');

        if (response.servicios && response.servicios.length > 0) {
          response.servicios.forEach(function (servicio) {
            descripcionSelect.append(
              `<option value="${servicio.id}" 
                                     data-precio="${servicio.precio}">
                                ${servicio.descripcion}
                            </option>`
            );
          });
          descripcionSelect.prop("disabled", false);
        } else {
          descripcionSelect.append(
            '<option value="">No hay servicios disponibles</option>'
          );
        }
      },
      error: function (error) {
        console.error("Error al cargar servicios:", error);
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudieron cargar los servicios",
        });
      },
      complete: function () {
        descripcionSelect.find('option:contains("Cargando...")').remove();
      },
    });
  } else {
    descripcionSelect.prop("disabled", true);
  }
});

// Manejar el cambio en la descripción para actualizar ID y precio
$("#descripcion_servicio").change(function () {
  const selectedOption = $(this).find("option:selected");
  const idProducto = selectedOption.val();
  const precio = selectedOption.data("precio");

  $("#idproducto_servicios").val(idProducto);
  $("#precio_unitario_servicios").val(precio ? precio.toFixed(2) : "");
});

// Agregar después del evento change de descripción_servicio
function actualizarTotalesServicios() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_servicios").val()) || 0;

  // Recorrer todos los meses
  $(".cantidad-mes-servicios").each(function () {
    var mes = this.id.replace("_cantidad_servicios", "");
    if ($("#" + mes + "_switch_servicios").is(":checked")) {
      var cantidad = parseInt($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  // Actualizar los totales en la interfaz
  $("#cantidad_total_servicios").text(cantidadTotal);
  $("#precio_total_servicios").text("S/. " + precioTotal.toFixed(2));
}

// Eventos para recalcular totales
$("#precio_unitario_servicios").on("input", actualizarTotalesServicios);
$(".cantidad-mes-servicios").on("input", actualizarTotalesServicios);

// Manejar cambios en los switches de meses
$('input[type="checkbox"][id$="_switch_servicios"]').on("change", function () {
  var mesId = this.id.replace("_switch_servicios", "");
  $("#" + mesId + "_cantidad_servicios")
    .prop("disabled", !this.checked)
    .val(this.checked ? "0" : ""); // Limpiar o inicializar en 0

  actualizarTotalesServicios();
});

function resetearFormularioServicios() {
  // Resetear el formulario base
  $("#cantidad_masiva_servicios").val("");
  $("#registerMaterialForm_servicios")[0].reset();
  $("#registerMaterialForm_servicios").removeData("id");

  // Resetear el título del botón submit
  $("#submitBtn_servicios").text("Guardar Presupuesto de Servicios");

  // Resetear el select de grupo y disparar el evento change
  $("#grupo_servicio").val("").trigger("change");

  // Resetear y deshabilitar el select de subgrupo
  $("#subgrupo_servicio")
    .empty()
    .append('<option value="">Seleccione un subgrupo de servicios</option>')
    .prop("disabled", true);

  // Resetear y deshabilitar el select de descripción
  $("#descripcion_servicio")
    .empty()
    .append('<option value="">Seleccione un servicio</option>')
    .prop("disabled", true);
  $("#observacion_servicios").val("");

  // Limpiar campos de ID y precio
  $("#idproducto_servicios").val("");
  $("#precio_unitario_servicios").val("");

  // Resetear todos los inputs de meses
  $(".cantidad-mes-servicios").val("").prop("disabled", true);

  // Desmarcar todos los checkboxes de meses
  $('input[type="checkbox"][id$="_switch_servicios"]').prop("checked", false);

  // Resetear los contadores totales
  $("#cantidad_total_servicios").text("0");
  $("#precio_total_servicios").text("S/. 0.00");

  // Limpiar cualquier mensaje de error que pudiera estar visible
  $(".is-invalid").removeClass("is-invalid");
  $(".invalid-feedback").remove();
}

// Calcular totales cuando se selecciona una descripción
$("#descripcion_servicio").change(function () {
  const selectedOption = $(this).find("option:selected");
  const idProducto = selectedOption.val();
  const precio = selectedOption.data("precio");

  $("#idproducto_servicios").val(idProducto);
  $("#precio_unitario_servicios").val(precio ? precio.toFixed(2) : "");

  // Recalcular totales cuando cambia el precio unitario
  actualizarTotalesServicios();
});

// Agregar después del submit del formulario
$(document).on("click", ".eliminar-servicio", function () {
  const id = $(this).data("id");

  Swal.fire({
    title: "¿Está seguro?",
    text: "Esta acción no se puede revertir",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: `/riegouva/produccionpalta_servicios_ajs/${id}/`,
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire({
              icon: "success",
              title: "Eliminado",
              text: "El servicio ha sido eliminado correctamente",
              showConfirmButton: false,
              timer: 1500,
            });

            // Recargar la tabla
            $("#serviciosTable").DataTable().ajax.reload();
          } else {
            Swal.fire({
              icon: "error",
              title: "Error",
              text: response.message || "Error al eliminar el servicio",
            });
          }
          actualizarTotalWidget();
        },
        error: function (xhr, status, error) {
          console.error("Error al eliminar servicio:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se pudo eliminar el servicio. Por favor, intente nuevamente.",
          });
        },
      });
    }
  });
});

//  Función de editar

$(document).on("click", ".editar-servicio", function () {
  resetearFormularioServicios();
  const id = $(this).data("id");

  $.ajax({
    url: `/riegouva/produccionpalta_servicios_ajs/${id}/`,
    type: "GET",
    success: function (response) {
      const servicio = response;

      // Abrir el modal
      $("#Modal_Servicios").modal("show");

      // Cargar el grupo y esperar que se carguen sus opciones
      $("#grupo_servicio").val(servicio.grupo_servicio).trigger("change");

      // Esperar a que se carguen las opciones del subgrupo
      setTimeout(() => {
        // Agregar la opción del subgrupo directamente y seleccionarla
        $("#subgrupo_servicio")
          .append(
            `<option value="${servicio.subgrupo_servicio}" selected>
                        ${servicio.subgrupo_servicio}
                    </option>`
          )
          .val(servicio.subgrupo_servicio)
          .trigger("change");

        // Esperar a que se procese el cambio del subgrupo
        setTimeout(() => {
          // Agregar la opción de descripción directamente y seleccionarla
          $("#descripcion_servicio")
            .append(
              `<option value="${servicio.idproducto}" 
                            data-precio="${servicio.precio_unitario}" selected>
                            ${servicio.descripcion}
                        </option>`
            )
            .val(servicio.idproducto);

          // Cargar el resto de los datos
          $("#idproducto_servicios").val(servicio.idproducto);
          $("#precio_unitario_servicios").val(servicio.precio_unitario);
          $("#observacion_servicios").val(servicio.observacion);

          // Manejar los meses
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];

          meses.forEach((mes) => {
            const cantidad = servicio[`${mes}_cantidad`];
            if (cantidad > 0) {
              $(`#${mes}_switch_servicios`)
                .prop("checked", true)
                .trigger("change");
              $(`#${mes}_cantidad_servicios`)
                .val(cantidad)
                .prop("disabled", false);
            }
          });

          // Actualizar totales
          actualizarTotalesServicios();

          // Guardar el ID para la edición
          $("#registerMaterialForm_servicios").data("id", id);
        }, 300);
      }, 300);
      actualizarTotalWidget();
    },
    error: function (xhr, status, error) {
      console.error("Error al obtener servicio:", error);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo obtener los datos del servicio",
      });
    },
  });
});

// Modificar el evento change del grupo para mantener la selección durante la edición
$("#grupo_servicio").change(function () {
  const grupoId = $(this).val();
  const subgrupoSelect = $("#subgrupo_servicio");

  if (grupoId) {
    $.ajax({
      url: "/api/subgrupos-servicios/",
      data: { grupo: grupoId },
      success: function (response) {
        subgrupoSelect
          .empty()
          .append(
            '<option value="">Seleccione un subgrupo de servicios</option>'
          );
        response.subgrupos.forEach(function (subgrupo) {
          subgrupoSelect.append(
            `<option value="${subgrupo.id}">${subgrupo.nombre}</option>`
          );
        });
        subgrupoSelect.prop("disabled", false);

        // Si hay un valor previo seleccionado (edición), lo mantenemos
        const valorPrevio = subgrupoSelect.data("valor-previo");
        if (valorPrevio) {
          subgrupoSelect.val(valorPrevio);
          subgrupoSelect.removeData("valor-previo");
        }
      },
    });
  } else {
    subgrupoSelect
      .empty()
      .append('<option value="">Seleccione un subgrupo de servicios</option>')
      .prop("disabled", true);
    $("#descripcion_servicio")
      .empty()
      .append('<option value="">Seleccione un servicio</option>')
      .prop("disabled", true);
  }
});

// Guardar el servicio
let isSubmitting = false;
$("#registerMaterialForm_servicios").submit(function (e) {
  e.preventDefault();

  // Verificar si ya se está procesando un envío
  if (isSubmitting) {
    return;
  }

  // Marcar como en proceso de envío
  isSubmitting = true;

  // Deshabilitar el botón de submit
  $("#submitBtn_servicios").prop("disabled", true);

  // Validar meses activados sin cantidad
  const meses = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
  ];

  let tieneCantidad = false;
  let mesesInvalidos = [];

  meses.forEach((mes) => {
    const switchChecked = $(`#${mes}_switch_servicios`).is(":checked");
    const cantidad = parseInt($(`#${mes}_cantidad_servicios`).val()) || 0;

    if (switchChecked && cantidad <= 0) {
      mesesInvalidos.push(mes.charAt(0).toUpperCase() + mes.slice(1));
    }

    if (switchChecked && cantidad > 0) {
      tieneCantidad = true;
    }
  });

  // Validar meses activados sin cantidad
  if (mesesInvalidos.length > 0) {
    Swal.fire({
      icon: "error",
      title: "Error de Validación",
      text: `Los siguientes meses están activados pero no tienen cantidad: ${mesesInvalidos.join(
        ", "
      )}`,
      confirmButtonText: "Entendido",
    });
    return;
  }

  // Validar que al menos un mes tenga cantidad
  if (!tieneCantidad) {
    Swal.fire({
      icon: "error",
      title: "Error de Validación",
      text: "Debe seleccionar al menos un mes y asignarle una cantidad",
      confirmButtonText: "Entendido",
    });
    return;
  }
  // Si pasa la validación, continuar con el envío del formulario
  const id = $(this).data("id");
  const isEdit = !!id;

  // Obtener los datos del formulario
  const formData = {
    idproducto: $("#idproducto_servicios").val(),
    grupo_servicio: $("#grupo_servicio").val(),
    subgrupo_servicio: $("#subgrupo_servicio").val(),
    descripcion: $("#descripcion_servicio option:selected").text(),
    precio_unitario: parseFloat($("#precio_unitario_servicios").val()) || 0,
    observacion: $("#observacion_servicios").val(),
    ID_CAMPANIA: $("#filtroAnioPresupuesto").val() || "CAMP" + new Date().getFullYear(),
  };

  // Agregar datos de cada mes
  meses.forEach((mes) => {
    const switchChecked = $(`#${mes}_switch_servicios`).is(":checked");
    formData[`${mes}_cantidad`] = switchChecked
      ? parseInt($(`#${mes}_cantidad_servicios`).val()) || 0
      : 0;
  });

  // Configurar la petición AJAX
  const ajaxConfig = {
    url: isEdit
      ? `/riegouva/produccionpalta_servicios_ajs/${id}/`
      : "/riegouva/produccionpalta_servicios_ajs/",
    type: isEdit ? "PUT" : "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      if (response.status === "success") {
        Swal.fire({
          icon: "success",
          title: "Éxito",
          text: response.message,
          showConfirmButton: false,
          timer: 1500,
        });

        // Recargar la tabla
        $("#serviciosTable").DataTable().ajax.reload();

        // Resetear el formulario
        resetearFormularioServicios();

        // Cerrar el modal solo si es edición
        if (isEdit) {
          $("#Modal_Servicios").modal("hide");
        }
        actualizarTotalWidget();
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al guardar servicio:", error);
      const response = xhr.responseJSON || {};
      Swal.fire({
        icon: "error",
        title: "Error",
        text:
          response.message ||
          "No se pudo guardar el servicio. Por favor, intente nuevamente.",
      });
    },
    complete: function () {
      // Restaurar el estado del formulario
      isSubmitting = false;
      $("#submitBtn_servicios").prop("disabled", false);
    },
  };

  $.ajax(ajaxConfig);
});

$(document).on("click", "#btnAgregarServicio", function () {
  resetearFormularioServicios();
  $("#Modal_Servicios").modal("show");
});

$("#Modal_Servicios").on("hidden.bs.modal", function () {
  resetearFormularioServicios();
});

$('[data-dismiss="modal"]').on("click", function () {
  resetearFormularioServicios();
});

$("#recargarServiciosTerceros_costos").on("click", function (e) {
  e.stopPropagation(); // Evitar que se abra el modal
  $(this).find("i").addClass("fa-spin"); // Añadir animación de giro

  actualizarTotalesServicios();

  // Quitar la animación después de 1 segundo
  setTimeout(() => {
    $(this).find("i").removeClass("fa-spin");
  }, 1000);
});

$("#aplicar_cantidad_masiva_servicios").click(function () {
  const cantidad = $("#cantidad_masiva_servicios").val();

  if (!cantidad || cantidad <= 0) {
    Swal.fire({
      icon: "error",
      title: "Cantidad inválida",
      text: "Por favor, ingrese una cantidad válida mayor a 0",
      confirmButtonText: "Entendido",
    });
    return;
  }

  Swal.fire({
    title: "¿Aplicar a todos los meses?",
    text: `Se aplicará la cantidad de ${cantidad} a todos los meses. ¿Desea continuar?`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, aplicar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      const meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ];

      meses.forEach((mes) => {
        // Activar el switch del mes
        $(`#${mes}_switch_servicios`).prop("checked", true);
        // Establecer la cantidad
        $(`#${mes}_cantidad_servicios`).val(cantidad);
      });

      // Actualizar totales
      actualizarTotalesServicios();

      // Limpiar el campo de cantidad masiva
      $("#cantidad_masiva_servicios").val("");

      // Mostrar mensaje de éxito
      Swal.fire({
        icon: "success",
        title: "Cantidades aplicadas",
        text: "Se han aplicado las cantidades a todos los meses correctamente",
        showConfirmButton: false,
        timer: 1500,
      });
    }
  });
});

// Manejador para el botón de recarga del panel
$('[data-click="panel-reload"]').click(function (e) {
  e.preventDefault();
  const modal = $(this).closest(".modal-content");
  const table = modal.find("#serviciosTable").DataTable();

  // Agregar el loader
  modal.append(
    '<div class="panel-loader"><span class="spinner-border spinner-border-sm"></span></div>'
  );

  // Recargar la tabla
  table.ajax.reload(function () {
    // Actualizar totales
    actualizarTotalesServicios();

    // Remover el loader después de la recarga
    setTimeout(function () {
      modal.find(".panel-loader").remove();
    }, 500);
  });
});
