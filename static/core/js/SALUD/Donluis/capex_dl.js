$(document).ready(function () {
  calcularTotalPresupuesto_Capex();

  initCapexTable();
  inicializarAutocomplete_Capex("#descripcion_capex", "#idproducto_capex");
  $('[data-target="#PresupuestoModalCapex"]').on("click", function () {
    setTimeout(calcularTotalPresupuesto_Capex, 100);
  });

  $(".cantidad-mes-capex").prop("disabled", true);

  $('input[type="checkbox"]').change(function () {
    var mesId = this.id.replace("_switch_capex", "");
    $("#" + mesId + "_cantidad_capex").prop("disabled", !this.checked);
  });

  $("#precio_unitario_capex").on("input", calcularTotales_Capex);
  $(".cantidad-mes-capex").on("input", calcularTotales_Capex);
  $('input[type="checkbox"]').on("change", calcularTotales_Capex);
  $('input[type="checkbox"]').on("change", calcularTotales_Capex);

  restaurarPestaña();

  $(".nav-tabs a").on("shown.bs.tab", function (e) {
    var activeTab = $(e.target).attr("href");
    localStorage.setItem("activeTab", activeTab);
  });

  // Manejar el checkbox de producto nuevo
  $("#nuevoProductoCheck").on("change", function () {
    const isChecked = $(this).is(":checked");

    if (isChecked) {
      // Modo producto nuevo
      $("#idproducto_capex").val("11111111111");

      // Destruir correctamente el autocomplete
      if ($("#descripcion_capex").data("ui-autocomplete")) {
        $("#descripcion_capex").autocomplete("destroy");
      }

      $("#descripcion_capex")
        .prop("readonly", false)
        .val("")
        .off("focus") // Remover cualquier evento focus que pudiera reiniciar el autocomplete
        .off("keydown"); // Remover eventos de teclado asociados

      $("#precio_unitario_capex")
        .prop("readonly", false)
        .addClass("editable-campo")
        .val("");

      $("#observacion-container").fadeIn();
    } else {
      // Modo normal
      $("#idproducto_capex").val("");
      $("#descripcion_capex").val("");

      $("#precio_unitario_capex")
        .prop("readonly", true)
        .removeClass("editable-campo")
        .val("");

      $("#observacion-container").fadeOut();
      $("#observacion_capex").val("");

      // Reinicializar autocomplete
      inicializarAutocomplete_Capex("#descripcion_capex", "#idproducto_capex");
    }
  });
});

// funcion restaurar pestaña

function restaurarPestaña() {
  var activeTab = localStorage.getItem("activeTab");
  if (activeTab) {
    $('.nav-tabs a[href="' + activeTab + '"]').tab("show");
  }
}

//FUNCIONES DE AUTOCOMPLETE

function inicializarAutocomplete_Capex(
  descripcionSelector,
  idProductoSelector
) {
  $(descripcionSelector)
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_capex/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            var results = $.map(data, function (item) {
              return {
                label: item.value,
                value: item.value,
                id: item.id,
                ultimo_precio: parseFloat(item.ultimo_precio) || 0,
                sin_precio_historico: parseFloat(item.ultimo_precio) === 0,
              };
            });
            response(results);
          },
        });
      },
      minLength: 2,
      select: function (event, ui) {
        $(idProductoSelector).val(ui.item.id);

        // Establecer el precio y manejar la edición
        if (ui.item.sin_precio_historico) {
          $("#precio_unitario_capex")
            .val("0.00")
            .prop("readonly", false)
            .addClass("editable-precio")
            .attr("placeholder", "Ingrese el precio unitario");

          Swal.fire({
            title: "Producto sin precio histórico",
            text: "Por favor, ingrese manualmente el precio unitario para este producto.",
            icon: "info",
          });
        } else {
          $("#precio_unitario_capex")
            .val(ui.item.ultimo_precio.toFixed(2))
            .prop("readonly", true)
            .removeClass("editable-precio");
        }

        calcularTotales_Capex();
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    var precioText = item.sin_precio_historico
      ? "(Sin precio histórico)"
      : "(Último precio: S/. " + item.ultimo_precio.toFixed(2) + ")";

    return $("<li>")
      .append("<div>" + item.label + " " + precioText + "</div>")
      .appendTo(ul);
  };
}

function calcularTotales_Capex() {
  var cantidadTotal = 0;
  var precioTotal = 0;
  var precioUnitario = parseFloat($("#precio_unitario_capex").val()) || 0;

  $(".cantidad-mes-capex").each(function () {
    var mes = this.id.replace("_cantidad_capex", "");
    if ($("#" + mes + "_switch_capex").is(":checked")) {
      var cantidad = parseInt($(this).val()) || 0;
      cantidadTotal += cantidad;
      precioTotal += cantidad * precioUnitario;
    }
  });

  $("#cantidad_total_capex").text(cantidadTotal);
  $("#precio_total_capex").text("S/. " + precioTotal.toFixed(2));
}

function formatearMonedaPEN(monto) {
  return (
    "S/. " +
    parseFloat(monto)
      .toFixed(2)
      .replace(/\B(?=(\d{3})+(?!\d))/g, ",")
  );
}

// TABLA DATATABLE
function calcularTotalPresupuesto_Capex() {
  // Calcular el total directamente de los datos de la tabla (ya filtrados por campaña)
  if ($.fn.DataTable.isDataTable("#capexTable")) {
    var table = $("#capexTable").DataTable();
    var data = table.rows().data().toArray();
    
    // Inicializar totales por mes
    var totalesMes = {
      enero: {cantidad: 0, precio: 0},
      febrero: {cantidad: 0, precio: 0},
      marzo: {cantidad: 0, precio: 0},
      abril: {cantidad: 0, precio: 0},
      mayo: {cantidad: 0, precio: 0},
      junio: {cantidad: 0, precio: 0},
      julio: {cantidad: 0, precio: 0},
      agosto: {cantidad: 0, precio: 0},
      septiembre: {cantidad: 0, precio: 0},
      octubre: {cantidad: 0, precio: 0},
      noviembre: {cantidad: 0, precio: 0},
      diciembre: {cantidad: 0, precio: 0}
    };
    
    var totalGeneral = 0;
    
    data.forEach(function(row) {
      Object.keys(totalesMes).forEach(function(mes) {
        var cantidad = parseFloat(row[mes + '_cantidad']) || 0;
        var precio = parseFloat(row[mes + '_precio']) || 0;
        totalesMes[mes].cantidad += cantidad;
        totalesMes[mes].precio += precio;
        totalGeneral += precio;
      });
    });
    
    // Actualizar totales por mes
    const meses = [
      "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ];
    
    meses.forEach(function(mes) {
      var mesKey = mes.toLowerCase();
      var cantidad = totalesMes[mesKey].cantidad;
      var precio = totalesMes[mesKey].precio.toFixed(2);
      
      $(`#total_${mes}_cantidad`).text(cantidad);
      $(`#total_${mes}_precio`).text(`S/. ${precio}`);
    });
    
    // Actualizar total general con formato de moneda peruana
    var montoFormateado = formatearMonedaPEN(totalGeneral);
    
    // Actualizar todos los widgets que muestran el total
    $("#total_general").text(montoFormateado);
    $("#totalPresupuestoCapex").text(montoFormateado);
    $("#stats_capex").text(montoFormateado);
    
    // Actualizar el widget consolidado
    $("#stats_capex_consolidado").text(montoFormateado);
  }
}
function initCapexTable() {
  // Inicializar DataTable
  var table = $("#capexTable").DataTable({
    drawCallback: function (settings) {
      calcularTotalPresupuesto_Capex();
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

          // Recargar la tabla
          dt.ajax.reload(function () {
            // Callback después de la recarga
            setTimeout(() => {
              $(node).find("i").removeClass("fa-spin");
            }, 1000);

            // Actualizar totales
            calcularTotales_Capex();
          });
        },
      },
      {
        extend: "excelHtml5",
        title: "RPT_PRESUPUESTO_CAPEX",
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
        title: "RPT_PRESUPUESTO_CAPEX",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A2", // Cambiamos a un tamaño de página más grande
        customize: function (doc) {
          // Reducir el tamaño de la fuente
          doc.defaultStyle.fontSize = 6;
          doc.styles.tableHeader.fontSize = 7;
          doc.styles.title.fontSize = 12;

          // Ajustar el ancho de las columnas
          var table = doc.content[1].table.body;
          var colCount = table[0].length;
          var widths = [];
          for (var i = 0; i < colCount; i++) {
            widths.push("*");
          }
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
          $("#Modal_Capex").modal("show");
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
      url: "/salud/salud_capex/",
      dataSrc: "data",
    },

    fixedColumns: {
      right: 1, // Fija la última columna (acciones) a la derecha
    },

    columns: [
      { data: "id", title: "ID", visible: false },
      {
        data: null,
        title: "N°",
        className: "text-center",
        render: function (data, type, row, meta) {
          // Simplemente usar el índice de la fila + 1
          return meta.row + 1;
        },
      },
      { data: "idproducto", title: "ID Producto" }, // Cambiado de id_producto a idproducto
      {
        data: "descripcion",
        title: "Descripción",
        className: "text-end descripcion-column",
      },
      {
        data: "observacion",
        className: "text-left",
        title: "Observación",
        render: function (data, type, row) {
          return data ? data : "";
        },
      },
      { data: "precio_unitario", title: "Precio Unitario" },
      // Enero
      { data: "enero_cantidad", title: "Cantidad" },
      { data: "enero_precio", title: "Precio" }, // Cambiado de enero_total a enero_precio
      // Febrero
      { data: "febrero_cantidad", title: "Cantidad" },
      { data: "febrero_precio", title: "Precio" }, // Cambiado de febrero_total a febrero_precio
      // Marzo
      { data: "marzo_cantidad", title: "Cantidad" },
      { data: "marzo_precio", title: "Precio" }, // Cambiado de marzo_total a marzo_precio
      // Abril
      { data: "abril_cantidad", title: "Cantidad" },
      { data: "abril_precio", title: "Precio" }, // Cambiado de abril_total a abril_precio
      // Mayo
      { data: "mayo_cantidad", title: "Cantidad" },
      { data: "mayo_precio", title: "Precio" }, // Cambiado de mayo_total a mayo_precio
      // Junio
      { data: "junio_cantidad", title: "Cantidad" },
      { data: "junio_precio", title: "Precio" }, // Cambiado de junio_total a junio_precio
      // Julio
      { data: "julio_cantidad", title: "Cantidad" },
      { data: "julio_precio", title: "Precio" }, // Cambiado de julio_total a julio_precio
      // Agosto
      { data: "agosto_cantidad", title: "Cantidad" },
      { data: "agosto_precio", title: "Precio" }, // Cambiado de agosto_total a agosto_precio
      // Septiembre
      { data: "septiembre_cantidad", title: "Cantidad" },
      { data: "septiembre_precio", title: "Precio" }, // Cambiado de septiembre_total a septiembre_precio
      // Octubre
      { data: "octubre_cantidad", title: "Cantidad" },
      { data: "octubre_precio", title: "Precio" }, // Cambiado de octubre_total a octubre_precio
      // Noviembre
      { data: "noviembre_cantidad", title: "Cantidad" },
      { data: "noviembre_precio", title: "Precio" }, // Cambiado de noviembre_total a noviembre_precio
      // Diciembre
      { data: "diciembre_cantidad", title: "Cantidad" },
      { data: "diciembre_precio", title: "Precio" }, // Cambiado de diciembre_total a diciembre_precio
      // Columna de acciones
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
                          <button class="btn btn-sm btn-primary editar-capex" data-id="${row.id}">
                              <i class="fas fa-edit"></i>
                          </button>
                          <button class="btn btn-sm btn-danger eliminar-capex" data-id="${row.id}">
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
  });

  // Agregar evento de clic para el botón de eliminar
  $("#capexTable tbody").on("click", ".eliminar-capex", function () {
    var id = $(this).data("id");
    eliminarProducto_capex(id, "capex");
  });

  // Evento de clic para el botón de editar
  $("#capexTable tbody").on("click", ".editar-capex", function () {
    var id = $(this).data("id");
    editarProducto_capex(id);
  });

  /* registrar  */

  /*   
  $("#registerMaterialForm_capex").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_capex").val().trim(),
      descripcion: $("#descripcion_capex").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_capex").val()) || 0,
      //campo de observacion
      observacion: $("#observacion_capex").val().trim(),
    };

    // Si es un producto nuevo, validar la observación
    if (jsonData.idproducto === "11111111111" && !jsonData.observacion) {
      Swal.fire({
        title: "Error!",
        text: "La observación es obligatoria para productos nuevos.",
        icon: "warning",
      });
      return;
    }

    var cantidadTotal = parseFloat($("#cantidad_total_capex").text()) || 0;

    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }
    //===================================================
    // Obtener el precio unitario ingresado
    var precioUnitario = parseFloat($("#precio_unitario_capex").val());

    // Validar que se haya ingresado un precio cuando el campo es editable
    if (
      $("#precio_unitario_capex").hasClass("editable-precio") &&
      (!precioUnitario || precioUnitario <= 0)
    ) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar un precio unitario válido mayor a cero.",
        icon: "warning",
      });
      return;
    }
    //===================================================
    // Solo verificar producto existente si es una nueva adición, no una actualización
    if (!isUpdate) {
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    var meses = [
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

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_capex").is(":checked");
      var cantidad = switchChecked
        ? parseInt($("#" + mes + "_cantidad_capex").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    $.ajax({
      url: isUpdate ? "/salud/salud_capex/" + formId + "/" : "/salud/salud_capex/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#addCapexModal").modal("hide");
            $("#registerMaterialForm_capex")[0].reset();
            $("#registerMaterialForm_capex").removeAttr("data-id");
            $("#submitBtn_capex").text("Agregar");
            calcularTotales_Capex();
            calcularTotalPresupuesto_Capex();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

 */

  $("#registerMaterialForm_capex").submit(function (e) {
    e.preventDefault();

    var formId = $(this).attr("data-id");
    var isUpdate = formId !== undefined;

    var jsonData = {
      idproducto: $("#idproducto_capex").val().trim(),
      descripcion: $("#descripcion_capex").val().trim(),
      precio_unitario: parseFloat($("#precio_unitario_capex").val()) || 0,
      observacion: $("#observacion_capex").val().trim(),
    };

    // Validaciones según el modo (normal o producto nuevo)
    if (jsonData.idproducto === "11111111111") {
      // Modo producto nuevo
      if (!jsonData.observacion) {
        Swal.fire({
          title: "Error!",
          text: "La observación es obligatoria para productos nuevos.",
          icon: "warning",
        });
        return;
      }
    } else {
      // Modo normal
      if (!jsonData.idproducto || !jsonData.descripcion) {
        Swal.fire({
          title: "Error!",
          text: "Por favor seleccione un producto válido.",
          icon: "warning",
        });
        return;
      }
    }

    // Validación de cantidad total
    var cantidadTotal = parseFloat($("#cantidad_total_capex").text()) || 0;
    if (!cantidadTotal > 0) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar al menos una cantidad mayor a cero.",
        icon: "warning",
      });
      return;
    }

    // Validación de precio unitario
    var precioUnitario = parseFloat($("#precio_unitario_capex").val());
    if (
      (jsonData.idproducto === "11111111111" ||
        $("#precio_unitario_capex").hasClass("editable-precio")) &&
      (!precioUnitario || precioUnitario <= 0)
    ) {
      Swal.fire({
        title: "Error!",
        text: "Debe ingresar un precio unitario válido mayor a cero.",
        icon: "warning",
      });
      return;
    }

    // Verificar producto existente solo para nuevas adiciones
    if (!isUpdate) {
      var productoExistente = table
        .rows()
        .data()
        .toArray()
        .find(function (row) {
          // Permitir duplicados si es producto nuevo (11111111111)
          if (jsonData.idproducto === "11111111111") {
            return false;
          }
          return row.idproducto === jsonData.idproducto;
        });

      if (productoExistente) {
        Swal.fire({
          title: "Error!",
          text: "Este producto ya ha sido agregado al presupuesto. Por favor, seleccione un producto diferente.",
          icon: "error",
        });
        return;
      }
    }

    // Procesar cantidades mensuales
    var meses = [
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

    meses.forEach(function (mes) {
      var switchChecked = $("#" + mes + "_switch_capex").is(":checked");
      var cantidad = switchChecked
        ? parseInt($("#" + mes + "_cantidad_capex").val()) || 0
        : 0;
      jsonData[mes + "_cantidad"] = cantidad;
    });

    // Enviar datos al servidor
    $.ajax({
      url: isUpdate
        ? "/salud/salud_capex/" + formId + "/"
        : "/salud/salud_capex/",
      type: isUpdate ? "PUT" : "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
            text: response.message,
            icon: "success",
          }).then(() => {
            table.ajax.reload();
            $("#Modal_Capex").modal("hide"); // Cambiado de addCapexModal a Modal_Capex
            $("#registerMaterialForm_capex")[0].reset();
            $("#registerMaterialForm_capex").removeAttr("data-id");
            $("#submitBtn_capex").text("Agregar");
            calcularTotales_Capex();
            calcularTotalPresupuesto_Capex();
          });
        } else {
          Swal.fire({
            title: "Error!",
            text: "Hubo un problema al enviar los datos: " + response.message,
            icon: "error",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.fire({
          title: "Error!",
          text: "Hubo un problema al enviar los datos: " + error,
          icon: "error",
        });
      },
    });
  });

  // Agregar evento para resetear el formulario cuando se cierre el modal
  $("#registerMaterialForm_capex").on("hidden.bs.modal", function () {
    $("#registerMaterialForm_capex")[0].reset();
    $("#registerMaterialForm_capex").removeAttr("data-id");
    $("#submitBtn_capex").text("Agregar");
    $(".cantidad-mes-capex").prop("disabled", true);
    $('input[type="checkbox"][id$="_switch_capex"]').prop("checked", false);
  });

  // Calcular el total inicial
  calcularTotalPresupuesto_Capex();

  // Función para actualizar totales
  function actualizarTotales() {
    var cantidadTotal = 0;
    var precioTotal = 0;
    var precioUnitario = parseFloat($("#precio_unitario_capex").val()) || 0;

    $(".cantidad-mes-capex").each(function () {
      var mes = this.id.replace("_cantidad_capex", "");
      if ($("#" + mes + "_switch_capex").is(":checked")) {
        var cantidad = parseInt($(this).val()) || 0;
        cantidadTotal += cantidad;
        precioTotal += cantidad * precioUnitario;
      }
    });

    $("#cantidad_total_capex").text(cantidadTotal);
    $("#precio_total_capex").text("S/. " + precioTotal.toFixed(2));
  }

  // Eventos para recalcular totales
  $("#precio_unitario_capex").on("input", actualizarTotales);
  $(".cantidad-mes-capex").on("input", actualizarTotales);
  $('input[type="checkbox"][id$="_switch_capex"]').on("change", function () {
    var mesId = this.id.replace("_switch_capex", "");
    $("#" + mesId + "_cantidad_capex").prop("disabled", !this.checked);
    actualizarTotales();
  });

  // Calcular totales iniciales
  actualizarTotales();
}

function eliminarProducto_capex(id, tipo) {
  Swal.fire({
    title: "¿Estás seguro?",
    text: "No podrás revertir esta acción",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/" + tipo + "/" + id + "/",
        type: "DELETE",
        success: function (response) {
          if (response.status === "success") {
            Swal.fire(
              "¡Eliminado!",
              "El producto ha sido eliminado.",
              "success"
            ).then(() => {
              // Recargar la tabla
              $("#capexTable").DataTable().ajax.reload();
              // Recalcular totales
              calcularTotales_Capex();
              calcularTotalPresupuesto_Capex();
            });
          } else {
            Swal.fire(
              "Error",
              "Hubo un problema al eliminar el producto: " + response.message,
              "error"
            );
          }
        },
        error: function (xhr, status, error) {
          Swal.fire(
            "Error",
            "Hubo un problema al eliminar el producto: " + error,
            "error"
          );
        },
      });
    }
  });
}

/* 
function editarProducto_capex(id) {
  $.ajax({
    url: "/salud/salud_capex/" + id + "/",
    type: "GET",
    success: function (data) {
      // Verificar si es un producto nuevo
      const esProductoNuevo =
        data.observacion && data.observacion.trim() !== "";

      // Activar/desactivar modo producto nuevo
      manejarProductoNuevo(esProductoNuevo, data);
      // Llenar el formulario con los datos del producto
      $("#idproducto_capex").val(data.idproducto);
      $("#descripcion_capex").val(data.descripcion);
      $("#precio_unitario_capex").val(data.precio_unitario);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
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

      // Reiniciar todos los switches y cantidades
      meses.forEach(function (mes) {
        $("#" + mes + "_switch_capex").prop("checked", false);
        $("#" + mes + "_cantidad_capex").val(0);
        $("#" + mes + "_cantidad_capex").prop("disabled", true);
      });

      // Establecer los valores del producto
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"] || 0;
        if (cantidad > 0) {
          $("#" + mes + "_switch_capex").prop("checked", true);
          $("#" + mes + "_cantidad_capex").prop("disabled", false);
          $("#" + mes + "_cantidad_capex").val(cantidad);
        }
      });

      calcularTotales_Capex();

      // Cambiar el texto del botón de submit
      $("#submitBtn_capex").text("Actualizar");

      // Agregar un atributo data-id al formulario para identificar que es una edición
      $("#registerMaterialForm_capex").attr("data-id", id);

      // Abrir el modal
      $("#Modal_Capex").modal("show");

      // Calcular los totales después de cargar todos los datos
      setTimeout(function () {
        actualizarTotales();
      }, 100);
    },
    error: function (xhr, status, error) {
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

 */

function editarProducto_capex(id) {
  console.log("Iniciando editarProducto_capex con ID:", id);

  $.ajax({
    url: "/salud/salud_capex/" + id + "/",
    type: "GET",
    success: function (data) {
      // Verificar si es un producto nuevo por el ID
      const esProductoNuevo = data.idproducto === "11111111111";

      // Manejar visibilidad del checkbox y su contenedor completo
      const checkboxContainer = $(".custom-control.custom-switch").closest(
        ".form-group"
      );

      if (esProductoNuevo) {
        // Modo producto nuevo
        checkboxContainer.show();
        $("#nuevoProductoCheck").prop("checked", true);

        // Mostrar y llenar observación
        $("#observacion-container").show();

        $("#observacion_capex").val(data.observacion || "");

        // Configurar campos editables
        $("#descripcion_capex").prop("readonly", false);
        $("#precio_unitario_capex")
          .prop("readonly", false)
          .addClass("editable-campo");

        // Destruir autocomplete si existe
        if ($("#descripcion_capex").data("ui-autocomplete")) {
          $("#descripcion_capex").autocomplete("destroy");
        }
      } else {
        // Modo normal - Ocultar completamente el contenedor del checkbox
        checkboxContainer.hide();
        $("#nuevoProductoCheck").prop("checked", false);

        // Ocultar observación
        $("#observacion-container").hide();
        $("#observacion_capex").val("");

        // Configurar campos como readonly
        $("#descripcion_capex").prop("readonly", false);
        $("#precio_unitario_capex")
          .prop("readonly", true)
          .removeClass("editable-campo");

        // Reinicializar autocomplete
        inicializarAutocomplete_Capex(
          "#descripcion_capex",
          "#idproducto_capex"
        );
      }

      // Llenar el formulario con los datos del producto
      $("#idproducto_capex").val(data.idproducto);
      $("#descripcion_capex").val(data.descripcion);
      $("#precio_unitario_capex").val(data.precio_unitario);

      // Llenar las cantidades y activar los switches correspondientes
      var meses = [
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

      // Reiniciar todos los switches y cantidades
      meses.forEach(function (mes) {
        $("#" + mes + "_switch_capex").prop("checked", false);
        $("#" + mes + "_cantidad_capex").val(0);
        $("#" + mes + "_cantidad_capex").prop("disabled", true);
      });

      // Establecer los valores del producto
      meses.forEach(function (mes) {
        var cantidad = data[mes + "_cantidad"] || 0;
        if (cantidad > 0) {
          $("#" + mes + "_switch_capex").prop("checked", true);
          $("#" + mes + "_cantidad_capex").prop("disabled", false);
          $("#" + mes + "_cantidad_capex").val(cantidad);
        }
      });

      calcularTotales_Capex();
      $("#submitBtn_capex").text("Actualizar");
      $("#registerMaterialForm_capex").attr("data-id", id);

      // Asegurarse que el modal exista y sea visible
      if ($("#Modal_Capex").length) {
        $("#Modal_Capex").modal("show");
      } else {
        console.error("Modal no encontrado: #Modal_Capex");
      }

      // Asegurarse de que la observación esté visible y con valor después de mostrar el modal
      if (esProductoNuevo) {
        setTimeout(function () {
          $("#observacion-container").show();
          $("#observacion_capex").val(data.observacion || "");
          actualizarTotales();
        }, 200);
      } else {
        setTimeout(function () {
          actualizarTotales();
        }, 100);
      }
    },
    error: function (xhr, status, error) {
      console.error("Error en la petición:", error);
      Swal.fire({
        title: "Error!",
        text: "No se pudo cargar la información del producto.",
        icon: "error",
      });
    },
  });
}

// Modificar también el evento hidden.bs.modal
$("#Modal_Capex").on("hidden.bs.modal", function () {
  $("#registerMaterialForm_capex")[0].reset();
  $("#registerMaterialForm_capex").removeAttr("data-id");
  $("#submitBtn_capex").text("Agregar");
  $(".cantidad-mes-capex").prop("disabled", true);
  $('input[type="checkbox"][id$="_switch_capex"]').prop("checked", false);

  // Mostrar el contenedor del checkbox y desmarcarlo
  $(".custom-control.custom-switch").parent().show();
  $("#nuevoProductoCheck").prop("checked", false);

  // Resetear el campo de precio unitario
  $("#precio_unitario_capex")
    .prop("readonly", true)
    .removeClass("editable-precio")
    .attr("placeholder", "")
    .val("");

  // Ocultar y limpiar observación
  $("#observacion-container").fadeOut();
  $("#observacion_capex").val("");

  // Reinicializar autocomplete
  inicializarAutocomplete_Capex("#descripcion_capex", "#idproducto_capex");
});

$("#Modal_Capex").on("hidden.bs.modal", function () {
  $("#registerMaterialForm_capex")[0].reset();
  $("#registerMaterialForm_capex").removeAttr("data-id");
  $("#submitBtn_capex").text("Agregar");
  $(".cantidad-mes-capex").prop("disabled", true);
  $('input[type="checkbox"][id$="_switch_capex"]').prop("checked", false);

  // Resetear el campo de precio unitario
  $("#precio_unitario_capex")
    .prop("readonly", true)
    .removeClass("editable-precio")
    .attr("placeholder", "")
    .val("");
});

function manejarProductoNuevo(activar, data = null) {
  console.log("Ejecutando manejarProductoNuevo:", activar); // Debug

  if (activar) {
    // Activar modo producto nuevo
    $("#idproducto_capex").val("11111111111");

    // Desbloquear y marcar campos editables

    $("#precio_unitario_capex")
      .prop("readonly", false)
      .addClass("editable-campo")
      .val(data ? data.precio_unitario : "");

    // Mostrar campo de observación
    $("#observacion-container").fadeIn();

    if (data && data.observacion) {
      $("#observacion_capex").val(data.observacion);
    }

    // Desactivar autocompletado
    $("#descripcion_capex").off("autocomplete");
  } else {
    // Desactivar modo producto nuevo
    $("#idproducto_capex").val("");

    $("#precio_unitario_capex")
      .prop("readonly", true)
      .removeClass("editable-campo")
      .val("");

    // Ocultar y limpiar observación
    $("#observacion-container").fadeOut();
    $("#observacion_capex").val("");

    // Reactivar autocompletado
    inicializarAutocomplete_Capex("#descripcion_capex", "#idproducto_capex");
  }
}
