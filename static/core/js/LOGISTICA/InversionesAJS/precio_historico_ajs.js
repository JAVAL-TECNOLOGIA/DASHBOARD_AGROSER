$(document).ready(function () {
  // Variables globales
  let selectedProductCode = null;
  let priceChart = null;

  // Función para buscar productos
  $("#btnSearch").click(function () {
    const searchTerm = $("#searchProduct").val().trim();

    if (searchTerm.length < 3) {
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "Por favor ingrese al menos 3 caracteres para buscar",
      });
      return;
    }

    // Mostrar indicador de carga
    $("#resultTable").html(
      '<tr><td class="text-center py-3"><i class="fa fa-spinner fa-spin"></i> Buscando productos...</td></tr>'
    );

    // Realizar la petición AJAX
    $.ajax({
      url: "/logistica/logistica_buscar-productos_ajs/",
      type: "GET",
      data: { search: searchTerm },
      dataType: "json",
      success: function (response) {
        console.log("Datos recuperados:", response);
        displaySearchResults(response.data || []);
      },
      error: function (xhr, status, error) {
        console.error("Error en la búsqueda:", error);
        $("#resultTable").html(
          '<tr><td class="text-center py-3 text-danger"><i class="fa fa-exclamation-circle"></i> Error al buscar productos</td></tr>'
        );
      },
    });
  });

  // También buscar al presionar Enter
  $("#searchProduct").keypress(function (e) {
    if (e.which == 13) {
      $("#btnSearch").click();
    }
  });

  // Mostrar resultados de búsqueda
  function displaySearchResults(results) {
    const $resultTable = $("#resultTable");
    $resultTable.empty();

    if (results.length === 0) {
      $resultTable.html(
        '<tr><td class="text-center py-3">No se encontraron productos</td></tr>'
      );
      return;
    }

    results.forEach((product) => {
      const row = `
                    <tr class="product-row" data-code="${
                      product.IDPRODUCTO || product.codigo
                    }">
                        <td>
                            <div class="d-flex flex-column">
                                <strong>${
                                  product.DESCRIPCION || product.descripcion
                                }</strong>
                                <small class="text-muted">Código: ${
                                  product.IDPRODUCTO || product.codigo
                                }</small>
                                <small class="text-muted">
                                    ${product.grupo} > ${product.subgrupo} | 
                                    Unidad: ${product.unidad_medida}
                                </small>
                            </div>
                        </td>
                        <td class="text-right">
                            <strong>S/ ${parseFloat(
                              product.ultimo_precio
                            ).toFixed(2)}</strong>
                        </td>
                    </tr>
                `;
      $resultTable.append(row);
    });

    // Evento para mostrar historial al hacer clic en un producto
    $(".product-row").click(function () {
      const productCode = $(this).data("code");
      selectedProductCode = productCode;

      // Resaltar la fila seleccionada
      $(".product-row").removeClass("bg-light");
      $(this).addClass("bg-light");

      console.log("Producto seleccionado:", productCode);

      // Cargar historial de precios
      loadPriceHistory(productCode);
    });
  }

  // Cargar historial de precios
  function loadPriceHistory(productCode) {
    // Mostrar secciones relevantes
    $("#noProductSelected").hide();
    $("#productInfo").show();
    $("#priceHistory").show();
    $("#priceChart").show();

    // Mostrar mensaje de carga
    $("#productName").html(
      '<i class="fa fa-spinner fa-spin"></i> Cargando información...'
    );
    $("#priceHistoryTable tbody").html(
      '<tr><td colspan="3" class="text-center"><i class="fa fa-spinner fa-spin"></i> Cargando historial...</td></tr>'
    );

    // Realizar la petición AJAX para obtener el historial
    $.ajax({
      url: "/logistica/logistica_historial-precios_ajs/",
      type: "GET",
      data: { codigo: productCode },
      dataType: "json",
      success: function (response) {
        console.log("Historial recuperado:", response);
        displayProductHistory(response);
      },
      error: function (xhr, status, error) {
        console.error("Error al cargar historial:", error);
        $("#productName").text("Error al cargar información");
        $("#priceHistoryTable tbody").html(
          '<tr><td colspan="3" class="text-center text-danger"><i class="fa fa-exclamation-circle"></i> Error al cargar el historial de precios</td></tr>'
        );
      },
    });
  }

  // Mostrar historial de precios
  function displayProductHistory(data) {
    const producto = data.producto;
    const historial = data.historial || [];
    const evolucionMensual = data.evolucion_mensual || [];

    // Mostrar información del producto
    $("#productName").text(producto.descripcion);
    $("#productCode").text(producto.codigo);

    // Mostrar precio actual (el más reciente)
    if (historial.length > 0) {
      $("#currentPrice").text(
        `S/ ${parseFloat(historial[0].precio).toFixed(2)}`
      );
    } else {
      $("#currentPrice").text("No disponible");
    }

    // Mostrar historial de precios
    const $historyTable = $("#priceHistoryTable tbody");
    $historyTable.empty();

    if (historial.length === 0) {
      $historyTable.html(
        '<tr><td colspan="3" class="text-center">No hay historial de precios disponible</td></tr>'
      );
    } else {
      historial.forEach((item) => {
        const variacionClass =
          item.variacion > 0
            ? "text-danger"
            : item.variacion < 0
            ? "text-success"
            : "";

        const variacionTexto =
          item.variacion === 0
            ? "0.00"
            : item.variacion > 0
            ? `+${item.variacion.toFixed(2)}`
            : item.variacion.toFixed(2);

        const porcentajeTexto =
          item.porcentaje === 0
            ? "0.00%"
            : item.porcentaje > 0
            ? `+${item.porcentaje.toFixed(2)}%`
            : `${item.porcentaje.toFixed(2)}%`;

        const row = `
              <tr>
                <td>${item.fecha_formato} <small class="text-muted">${
          item.proveedor || ""
        }</small></td>
                <td>S/ ${parseFloat(item.precio).toFixed(2)}</td>
                <td class="${variacionClass}">
                  ${variacionTexto} 
                  <small>(${porcentajeTexto})</small>
                </td>
              </tr>
            `;
        $historyTable.append(row);
      });
    }

    // Crear gráfico de evolución de precios
    createPriceChart(evolucionMensual);
  }

  // Crear gráfico de evolución de precios
  function createPriceChart(data) {
    const ctx = document.getElementById("priceChart");

    // Destruir gráfico anterior si existe
    if (priceChart) {
      priceChart.destroy();
    }

    if (!data || data.length === 0) {
      $(ctx).hide();
      return;
    }

    $(ctx).show();

    const labels = data.map((item) => `${item.mes} ${item.anio}`);
    const prices = data.map((item) => item.precio);

    priceChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Precio (S/)",
            data: prices,
            borderColor: "#348fe2",
            backgroundColor: "rgba(52, 143, 226, 0.1)",
            borderWidth: 2,
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `S/ ${context.raw.toFixed(2)}`;
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: false,
            ticks: {
              callback: function (value) {
                return "S/ " + value;
              },
            },
          },
        },
      },
    });
  }
});
