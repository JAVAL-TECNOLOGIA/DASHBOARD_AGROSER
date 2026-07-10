$(document).ready(function () {
  App.init();

  let dataTable;

  // Configuración de fechas por defecto
  function setDefaultDates() {
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    $("#fecha_inicio").val(firstDay.toISOString().split("T")[0]);
    $("#fecha_fin").val(new Date().toISOString().split("T")[0]);
  }

  // Función principal para obtener y renderizar el reporte
  function fetchAndRenderReport() {
    const fechaInicio = $("#fecha_inicio").val();
    const fechaFin = $("#fecha_fin").val();
    const regimen = $("#regimen").val();

    // Validación de fechas
    if (!fechaInicio || !fechaFin) {
      alert("Las fechas son obligatorias.");
      return;
    }

    // Validación de rango de fechas
    if (new Date(fechaInicio) > new Date(fechaFin)) {
      alert("La fecha de inicio no puede ser mayor a la fecha de fin.");
      return;
    }

    // Parámetros exactos según la especificación
    const params = {
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      regimen: regimen,
      detallado_fechas: 1,
      tipo_filtro: "A",
      dato: "",
      dato2: "",
      detallado: 1,
      resumen: 0,
      subplanilla: "XX",
    };

    const apiUrl = `/costos/costos_rpt_horas_personal_api/?${$.param(params)}`;

    console.log("URL de la API:", apiUrl);
    console.log("Parámetros enviados:", params);

    // Destruir la tabla anterior antes de hacer una nueva llamada
    if (dataTable) {
      dataTable.destroy();
      $("#reporte-table thead").empty();
      $("#reporte-table tbody").empty();
    }

    // Mostrar indicador de carga
    $("#reporte-table tbody").html(
      '<tr><td colspan="100%" class="text-center"><i class="fas fa-spinner fa-spin"></i> Cargando datos...</td></tr>'
    );

    // Realizar la petición AJAX
    $.ajax({
      url: apiUrl,
      method: "GET",
      dataType: "json",
      timeout: 30000, // 30 segundos de timeout
      success: function (response) {
        console.log("Respuesta de la API:", response);
        handleSuccessResponse(response);
      },
      error: function (xhr, status, error) {
        console.error("Error en la petición AJAX:", {
          status: status,
          error: error,
          responseText: xhr.responseText,
          statusCode: xhr.status,
        });

        handleErrorResponse(xhr, status, error);
      },
    });
  }

  // Manejar respuesta exitosa
  function handleSuccessResponse(response) {
    if (response.status !== "success") {
      alert(
        `Error al cargar el reporte: ${response.message || "Error desconocido"}`
      );
      $("#reporte-table tbody").html(
        '<tr><td colspan="100%" class="text-center text-danger">Error al cargar datos</td></tr>'
      );
      return;
    }

    if (!response.data || response.data.length === 0) {
      alert("No se encontraron datos para los filtros seleccionados.");
      $("#reporte-table tbody").html(
        '<tr><td colspan="100%" class="text-center text-warning">No hay datos disponibles</td></tr>'
      );
      return;
    }

    const data = response.data;
    console.log("Datos recibidos:", data);
    console.log("Número de registros:", data.length);

    // Obtener las columnas del primer registro
    const firstRecord = data[0];
    const columnNames = Object.keys(firstRecord);

    console.log("Columnas detectadas:", columnNames);

    // Crear las columnas para DataTables
    const columns = columnNames.map((key) => ({
      title: key.toUpperCase(),
      data: key,
      defaultContent: "-",
      className: "text-center",
      render: function (data, type, row) {
        if (data === null || data === undefined || data === "") {
          return "-";
        }
        // Si es un número, formatearlo
        if (typeof data === "number") {
          return parseFloat(data).toLocaleString("es-ES", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          });
        }
        // Si es una cadena que representa un número
        if (typeof data === "string" && !isNaN(data) && data.trim() !== "") {
          return parseFloat(data).toLocaleString("es-ES", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          });
        }
        return data;
      },
    }));

    // Crear la cabecera de la tabla
    let headerHtml = "<tr>";
    columnNames.forEach((col) => {
      headerHtml += `<th class="text-center" style="color: white !important; background-color: #343a40 !important; font-weight: bold;">${col.toUpperCase()}</th>`;
    });
    headerHtml += "</tr>";

    $("#reporte-table thead").html(headerHtml);
    $("#reporte-table tbody").empty();

    // Inicializar DataTable
    try {
      dataTable = $("#reporte-table").DataTable({
        data: data,
        columns: columns,
        responsive: true,
        pageLength: 25,
        lengthMenu: [
          [10, 25, 50, 100, -1],
          [10, 25, 50, 100, "Todos"],
        ],
        language: {
          url: "/static/datatables/i18n/es-ES.json",
          loadingRecords: "Cargando...",
          processing: "Procesando...",
          emptyTable: "No hay datos disponibles",
          info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
          infoEmpty: "Mostrando 0 a 0 de 0 registros",
          infoFiltered: "(filtrado de _MAX_ registros totales)",
          search: "Buscar:",
          paginate: {
            first: "Primero",
            last: "Último",
            next: "Siguiente",
            previous: "Anterior",
          },
        },
        dom: "Bfrtip",
        buttons: [
          {
            extend: "copy",
            text: "Copiar",
          },
          {
            extend: "csv",
            text: "CSV",
          },
          {
            extend: "excel",
            text: "Excel",
          },
          {
            extend: "pdf",
            text: "PDF",
          },
          {
            extend: "print",
            text: "Imprimir",
          },
        ],
        order: [[0, "asc"]],
        scrollX: true,
        processing: true,
        autoWidth: false,
        drawCallback: function (settings) {
          console.log(
            "DataTable dibujado con",
            settings.fnRecordsTotal(),
            "registros"
          );
        },
        initComplete: function () {
          console.log("DataTable inicializado correctamente");
        },
      });

      console.log(
        "DataTable creado exitosamente con",
        data.length,
        "registros"
      );
    } catch (error) {
      console.error("Error al inicializar DataTable:", error);
      alert("Error al mostrar los datos en la tabla: " + error.message);

      // Fallback: mostrar datos en tabla simple
      let tableHtml = "<tr>";
      columnNames.forEach((col) => {
        tableHtml += `<th class="text-center" style="color: white !important; background-color: #343a40 !important; font-weight: bold;">${col.toUpperCase()}</th>`;
      });
      tableHtml += "</tr>";
      $("#reporte-table thead").html(tableHtml);

      let bodyHtml = "";
      data.forEach((row) => {
        bodyHtml += "<tr>";
        columnNames.forEach((col) => {
          let value = row[col];
          if (value === null || value === undefined || value === "") {
            value = "-";
          }
          bodyHtml += `<td class="text-center">${value}</td>`;
        });
        bodyHtml += "</tr>";
      });
      $("#reporte-table tbody").html(bodyHtml);
    }
  }

  // Manejar respuesta de error
  function handleErrorResponse(xhr, status, error) {
    let errorMessage = "Error al conectar con el servidor.";

    if (xhr.status === 0) {
      errorMessage =
        "No se pudo conectar al servidor. Verifique su conexión a internet.";
    } else if (xhr.status === 404) {
      errorMessage = "La API no fue encontrada (Error 404).";
    } else if (xhr.status === 500) {
      errorMessage = "Error interno del servidor (Error 500).";
    } else if (status === "timeout") {
      errorMessage = "La petición tardó demasiado tiempo en responder.";
    } else if (xhr.responseText) {
      try {
        const errorResponse = JSON.parse(xhr.responseText);
        errorMessage = errorResponse.message || errorMessage;
      } catch (e) {
        errorMessage = `Error del servidor: ${xhr.responseText}`;
      }
    }

    alert(`Error: ${errorMessage}`);
    $("#reporte-table tbody").html(
      `<tr><td colspan="100%" class="text-center text-danger">Error: ${errorMessage}</td></tr>`
    );
  }

  // Inicialización
  setDefaultDates();

  // Evento del botón actualizar
  $("#btn-actualizar").on("click", function () {
    console.log("Botón actualizar clickeado");
    fetchAndRenderReport();
  });

  // Evento para actualizar al cambiar las fechas (opcional)
  $("#fecha_inicio, #fecha_fin").on("change", function () {
    // Opcional: actualizar automáticamente al cambiar fechas
    // fetchAndRenderReport();
  });

  // Carga inicial de datos
  fetchAndRenderReport();
});
