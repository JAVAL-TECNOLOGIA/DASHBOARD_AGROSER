/**
 * RRHH - Reporte de Utilidades
 * Funcionalidad para mostrar, filtrar y exportar datos de utilidades
 */

$(document).ready(function () {
  // Inicializar tabla con DataTables
  const tabla = $("#tabla-utilidades").DataTable({
    responsive: true,
    language: {
      url: "//cdn.datatables.net/plug-ins/1.10.25/i18n/Spanish.json",
    },
    dom: 'rt<"bottom"ip>',
    ordering: true,
    order: [[0, "asc"]],
    pageLength: 10,
    lengthMenu: [10, 25, 50, 100],
    columns: [
      { data: "IDCODIGO" },
      { data: "A_PATERNO" },
      { data: "A_MATERNO" },
      { data: "NOMBRES" },
      { data: "DNI" },
      { data: "TELEFONO" },
      { data: "EMAIL" },
      { data: "BANCO" },
      { data: "N_CUENTA" },
      { data: "N_INTERBANCARIA" },
      { data: "PERIODO" },
      {
        data: "FECHA_CREACION",
        render: function (data) {
          if (!data) return "";
          // Formatear fecha a dd/mm/yyyy hh:mm:ss
          const fecha = new Date(data);
          return fecha.toLocaleString("es-ES");
        },
      },
    ],
  });

  // Función para verificar si una fecha está dentro de un rango
  function estaEnRango(fechaStr, fechaInicio, fechaFin) {
    // Si no hay fechas de filtro, retornar true (pasar el filtro)
    if (!fechaInicio && !fechaFin) return true;

    // Si no hay fecha en el registro, no cumple con el filtro
    if (!fechaStr) return false;

    // Convertir la fecha del registro a objeto Date
    const fecha = new Date(fechaStr);

    // Verificar si está dentro del rango
    if (fechaInicio && fechaFin) {
      // Ajustamos fechaFin para incluir todo el día
      const finAjustado = new Date(fechaFin);
      finAjustado.setHours(23, 59, 59, 999);
      return fecha >= new Date(fechaInicio) && fecha <= finAjustado;
    } else if (fechaInicio) {
      return fecha >= new Date(fechaInicio);
    } else if (fechaFin) {
      // Ajustamos fechaFin para incluir todo el día
      const finAjustado = new Date(fechaFin);
      finAjustado.setHours(23, 59, 59, 999);
      return fecha <= finAjustado;
    }

    return true;
  }

  // Función para cargar datos con filtros aplicados
  function cargarDatos() {
    // Mostrar indicador de carga
    $("#loading").removeClass("d-none");
    $("#no-data-message").addClass("d-none");

    // Obtener valores de filtros
    const periodo = $("#filtro-periodo").val();
    const dni = $("#filtro-dni").val().trim();
    const banco = $("#filtro-banco").val();
    const fechaInicio = $("#filtro-fecha-inicio").val();
    const fechaFin = $("#filtro-fecha-fin").val();

    // Construir URL con parámetros de filtro
    let url = `/rrhh/lista_utilidades_empleados_cv/?periodo=${periodo}`;

    // Realizar solicitud AJAX
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      success: function (response) {
        // Ocultar indicador de carga
        $("#loading").addClass("d-none");

        if (
          response.status === "success" &&
          response.data &&
          response.data.length > 0
        ) {
          // Filtrar datos según criterios adicionales en el cliente
          let datos = response.data;

          // Filtro por DNI
          if (dni) {
            datos = datos.filter((item) => item.DNI && item.DNI.includes(dni));
          }

          // Filtro por banco
          if (banco) {
            datos = datos.filter((item) => item.BANCO === banco);
          }

          // Filtro por rango de fechas
          if (fechaInicio || fechaFin) {
            datos = datos.filter((item) =>
              estaEnRango(item.FECHA_CREACION, fechaInicio, fechaFin)
            );
          }

          // Actualizar tabla con los datos filtrados
          tabla.clear().rows.add(datos).draw();

          // Mostrar mensaje si no hay resultados después del filtrado
          if (datos.length === 0) {
            $("#no-data-message").removeClass("d-none");
          }
        } else {
          // Mostrar mensaje de no hay datos
          tabla.clear().draw();
          $("#no-data-message").removeClass("d-none");
        }

        // Actualizar contadores o resúmenes si es necesario
        actualizarResumen(tabla.data().count());
      },
      error: function (xhr, status, error) {
        // Ocultar indicador de carga y mostrar error
        $("#loading").addClass("d-none");
        Swal.fire({
          icon: "error",
          title: "Error al cargar datos",
          text: "Ocurrió un error al intentar cargar los datos. Por favor, intente nuevamente.",
          confirmButtonText: "Aceptar",
        });
        console.error("Error en la solicitud AJAX:", error);
      },
    });
  }

  // Función para actualizar el resumen de registros
  function actualizarResumen(totalRegistros) {
    const mensaje = `Total de registros: ${totalRegistros}`;

    // Si existe un elemento para mostrar el resumen, actualizarlo
    if ($("#resumen-registros").length > 0) {
      $("#resumen-registros").text(mensaje);
    } else {
      // Si no existe, se puede crear dinámicamente
      $("<div>")
        .attr("id", "resumen-registros")
        .addClass("text-end text-muted small mt-2")
        .text(mensaje)
        .insertBefore(".table-responsive");
    }
  }

  // Función para limpiar todos los filtros
  function limpiarFiltros() {
    // Restablecer valores de filtros
    $("#filtro-periodo").val("2026");
    $("#filtro-dni").val("");
    $("#filtro-banco").val("");
    $("#filtro-fecha-inicio").val("");
    $("#filtro-fecha-fin").val("");

    // Recargar datos
    cargarDatos();
  }

  // Exportar a Excel
  function exportarExcel() {
    // Mostrar indicador de carga durante la exportación
    Swal.fire({
      title: "Generando Excel",
      text: "Por favor espere...",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    // Obtener datos actuales de la tabla
    const datos = tabla.data().toArray();

    if (datos.length === 0) {
      Swal.fire({
        icon: "info",
        title: "Sin datos",
        text: "No hay datos para exportar",
        confirmButtonText: "Aceptar",
      });
      return;
    }

    // Crear un nuevo libro de Excel
    const wb = XLSX.utils.book_new();

    // Preparar los datos para Excel (solo datos, sin formato)
    const datosProcesados = datos.map((item) => ({
      Código: item.IDCODIGO,
      "Apellido Paterno": item.A_PATERNO,
      "Apellido Materno": item.A_MATERNO,
      Nombres: item.NOMBRES,
      DNI: item.DNI,
      Teléfono: item.TELEFONO,
      Email: item.EMAIL,
      Banco: item.BANCO,
      "Número de Cuenta": item.N_CUENTA,
      "Cuenta Interbancaria": item.N_INTERBANCARIA,
      Período: item.PERIODO,
      "Fecha Registro": item.FECHA_CREACION
        ? new Date(item.FECHA_CREACION).toLocaleString("es-ES")
        : "",
    }));

    // Crear hoja de cálculo
    const ws = XLSX.utils.json_to_sheet(datosProcesados);

    // Ajustar anchos de columna
    const wscols = [
      { wch: 10 }, // Código
      { wch: 15 }, // Apellido Paterno
      { wch: 15 }, // Apellido Materno
      { wch: 20 }, // Nombres
      { wch: 12 }, // DNI
      { wch: 15 }, // Teléfono
      { wch: 30 }, // Email
      { wch: 12 }, // Banco
      { wch: 20 }, // Número de Cuenta
      { wch: 25 }, // Cuenta Interbancaria
      { wch: 10 }, // Período
      { wch: 20 }, // Fecha Registro
    ];
    ws["!cols"] = wscols;

    // Añadir la hoja al libro
    XLSX.utils.book_append_sheet(wb, ws, "Utilidades");

    // Generar nombre de archivo con fecha actual
    const fechaActual = new Date().toISOString().slice(0, 10);
    const nombreArchivo = `Reporte_Utilidades_${fechaActual}.xlsx`;

    // Guardar el archivo
    XLSX.writeFile(wb, nombreArchivo);

    // Cerrar el diálogo de carga
    Swal.close();
  }

  // Imprimir tabla
  function imprimirTabla() {
    // Crear una ventana de impresión
    const ventanaImpresion = window.open("", "_blank");
    const periodo = $("#filtro-periodo").val();
    const fechaInicio = $("#filtro-fecha-inicio").val();
    const fechaFin = $("#filtro-fecha-fin").val();

    // Estilos para la impresión
    const estilos = `
      <style>
        body { font-family: Arial, sans-serif; }
        h1 { text-align: center; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }
        th { background-color: #f2f2f2; }
        .fecha-impresion { text-align: right; font-size: 12px; margin-bottom: 20px; }
        .filtros { margin-bottom: 20px; font-size: 14px; }
      </style>
    `;

    // Obtener datos de la tabla
    const filas = tabla.rows({ search: "applied" }).data();
    let contenidoTabla = "";

    filas.each(function (item) {
      contenidoTabla += `
        <tr>
          <td>${item.IDCODIGO}</td>
          <td>${item.A_PATERNO}</td>
          <td>${item.A_MATERNO}</td>
          <td>${item.NOMBRES}</td>
          <td>${item.DNI}</td>
          <td>${item.TELEFONO}</td>
          <td>${item.EMAIL}</td>
          <td>${item.BANCO}</td>
          <td>${item.N_CUENTA}</td>
          <td>${item.N_INTERBANCARIA}</td>
          <td>${item.PERIODO}</td>
          <td>${
            item.FECHA_CREACION
              ? new Date(item.FECHA_CREACION).toLocaleString("es-ES")
              : ""
          }</td>
        </tr>
      `;
    });

    // Fecha y hora actual para el reporte
    const fechaHoraActual = new Date().toLocaleString("es-ES");

    // Filtros aplicados
    let filtrosHTML = `
      <div class="filtros">
        <strong>Filtros aplicados:</strong>
        <ul>
          <li>Período: ${periodo}</li>
          <li>DNI: ${$("#filtro-dni").val().trim() || "Todos"}</li>
          <li>Banco: ${$("#filtro-banco").val() || "Todos"}</li>
    `;

    // Añadir filtros de fecha si están presentes
    if (fechaInicio || fechaFin) {
      filtrosHTML += `<li>Rango de fechas: ${
        fechaInicio || "Sin fecha inicial"
      } hasta ${fechaFin || "Sin fecha final"}</li>`;
    }

    filtrosHTML += `</ul></div>`;

    // Contenido HTML para imprimir
    const contenidoHTML = `
      <!DOCTYPE html>
      <html lang="es">
      <head>
        <meta charset="UTF-8">
        <title>Reporte de Utilidades - Período ${periodo}</title>
        ${estilos}
      </head>
      <body>
        <h1>Reporte de Utilidades - Período ${periodo}</h1>
        <div class="fecha-impresion">Fecha de impresión: ${fechaHoraActual}</div>
        ${filtrosHTML}
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>Apellido Paterno</th>
              <th>Apellido Materno</th>
              <th>Nombres</th>
              <th>DNI</th>
              <th>Teléfono</th>
              <th>Email</th>
              <th>Banco</th>
              <th>N° Cuenta</th>
              <th>N° Interbancaria</th>
              <th>Período</th>
              <th>Fecha Registro</th>
            </tr>
          </thead>
          <tbody>
            ${contenidoTabla}
          </tbody>
        </table>
        <script>
          window.onload = function() {
            window.print();
            window.setTimeout(function() {
              window.close();
            }, 500);
          };
        </script>
      </body>
      </html>
    `;

    ventanaImpresion.document.write(contenidoHTML);
    ventanaImpresion.document.close();
  }

  // Eventos
  $("#btn-buscar").on("click", cargarDatos);
  $("#btn-exportar-excel").on("click", exportarExcel);
  $("#btn-imprimir").on("click", imprimirTabla);

  // Eventos para fechas
  $("#filtro-fecha-inicio, #filtro-fecha-fin").on("change", function () {
    // Validar que fecha inicio no sea mayor que fecha fin
    const fechaInicio = $("#filtro-fecha-inicio").val();
    const fechaFin = $("#filtro-fecha-fin").val();

    if (fechaInicio && fechaFin && fechaInicio > fechaFin) {
      Swal.fire({
        icon: "warning",
        title: "Error en fechas",
        text: "La fecha de inicio no puede ser posterior a la fecha final",
        confirmButtonText: "Entendido",
      });
      $(this).val(""); // Limpiar el campo que causó el error
    }
  });

  // También permitir búsqueda al presionar Enter en campos de filtro
  $("#filtro-dni, #filtro-fecha-inicio, #filtro-fecha-fin").on(
    "keypress",
    function (e) {
      if (e.which === 13) {
        cargarDatos();
      }
    }
  );

  // Botón para limpiar filtros (si existe en el HTML)
  $("#btn-limpiar").on("click", limpiarFiltros);

  // Cargar datos iniciales
  cargarDatos();
});
