/**
 * Reporte de Campaña de Poda y Amarre
 * Script para gestionar la visualización y filtrado de registros
 * Autor: Jhon Gutierrez
 */

$(document).ready(function () {
  // Variables globales
  let dataTable;
  let registros = [];

  // Inicializar la tabla con DataTables
  function inicializarTabla() {
    dataTable = $("#tabla-poda-amarre").DataTable({
      language: {
        url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
      },
      pageLength: 10,
      lengthMenu: [
        [5, 10, 25, 50, -1],
        [5, 10, 25, 50, "Todos"],
      ],
      ordering: true,
      responsive: true,
      processing: true,
      dom: "Bfrtip",
      buttons: [
        {
          extend: "copy",
          text: '<i class="fas fa-copy"></i> Copiar',
          className: "btn btn-sm btn-outline-secondary",
        },
        {
          extend: "excel",
          text: '<i class="fas fa-file-excel"></i> Excel',
          className: "btn btn-sm btn-outline-success",
        },
        {
          extend: "pdf",
          text: '<i class="fas fa-file-pdf"></i> PDF',
          className: "btn btn-sm btn-outline-danger",
        },
        {
          extend: "print",
          text: '<i class="fas fa-print"></i> Imprimir',
          className: "btn btn-sm btn-outline-primary",
        },
      ],
      columnDefs: [{ className: "text-center align-middle", targets: "_all" }],
      order: [[8, "desc"]], // Ordenar por fecha de registro descendente por defecto
    });
  }

  // Cargar datos de la API
  function cargarDatos() {
    // Mostrar indicador de carga
    $("#loading").removeClass("d-none");
    $("#no-data-message").addClass("d-none");
    $("#tabla-poda-amarre").addClass("d-none");

    // Llamada a la API para obtener los registros
    $.ajax({
      url: "/rrhh/api/registro_campana_poda_amarre/",
      type: "GET",
      dataType: "json",
      success: function (response) {
        if (response.success) {
          registros = response.data;
          actualizarTabla(registros);
          $("#resumen-registros").html(
            `Total: <strong>${registros.length}</strong> registros encontrados`
          );
        } else {
          mostrarError("Error al cargar los datos: " + response.message);
        }
      },
      error: function (xhr, status, error) {
        mostrarError("Error en la solicitud: " + error);
      },
      complete: function () {
        $("#loading").addClass("d-none");
      },
    });
  }

  // Actualizar la tabla con los datos filtrados
  function actualizarTabla(datos) {
    // Limpiar la tabla
    dataTable.clear();

    if (datos.length === 0) {
      $("#tabla-poda-amarre").addClass("d-none");
      $("#no-data-message").removeClass("d-none");
      return;
    }

    // Agregar los datos a la tabla
    datos.forEach(function (registro) {
      dataTable.row.add([
        registro.id,
        registro.nombreCompleto ? registro.nombreCompleto.toUpperCase() : "",
        registro.dni,
        registro.nacionalidad ? registro.nacionalidad.toUpperCase() : "",
        registro.celular,
        registro.correo || "-",
        registro.labor ? registro.labor.toUpperCase() : "",
        registro.lugarResidencia ? registro.lugarResidencia.toUpperCase() : "",
        registro.fechaRegistro,
      ]);
    });

    // Actualizar la tabla
    dataTable.draw();
    $("#tabla-poda-amarre").removeClass("d-none");
    $("#no-data-message").addClass("d-none");
  }

  // Función para filtrar los datos
  function filtrarDatos() {
    const dni = $("#filtro-dni").val().trim().toLowerCase();
    const labor = $("#filtro-labor").val();
    const fechaInicio = $("#filtro-fecha-inicio").val();
    const fechaFin = $("#filtro-fecha-fin").val();

    // Aplicar filtros
    let datosFiltrados = registros.filter(function (registro) {
      // Filtro por DNI
      if (dni && !registro.dni.toLowerCase().includes(dni)) {
        return false;
      }

      // Filtro por labor
      if (labor && registro.labor !== labor) {
        return false;
      }

      // Filtro por fecha de inicio
      if (fechaInicio) {
        const fechaRegistro = new Date(registro.fechaRegistro);
        const fechaInicioObj = new Date(fechaInicio);
        if (fechaRegistro < fechaInicioObj) {
          return false;
        }
      }

      // Filtro por fecha de fin
      if (fechaFin) {
        const fechaRegistro = new Date(registro.fechaRegistro);
        const fechaFinObj = new Date(fechaFin);
        fechaFinObj.setHours(23, 59, 59); // Establecer al final del día
        if (fechaRegistro > fechaFinObj) {
          return false;
        }
      }

      return true;
    });

    // Actualizar la tabla con los datos filtrados
    actualizarTabla(datosFiltrados);
    $("#resumen-registros").html(
      `Total: <strong>${datosFiltrados.length}</strong> registros encontrados`
    );
  }

  // Función para limpiar los filtros
  function limpiarFiltros() {
    $("#filtro-dni").val("");
    $("#filtro-labor").val("");
    $("#filtro-fecha-inicio").val("");
    $("#filtro-fecha-fin").val("");

    // Recargar todos los datos
    actualizarTabla(registros);
    $("#resumen-registros").html(
      `Total: <strong>${registros.length}</strong> registros encontrados`
    );
  }

  // Función para exportar a Excel
  function exportarExcel() {
    // Obtener los datos visibles en la tabla
    const filas = dataTable.rows({ search: "applied" }).data();

    // Crear el libro de Excel
    const libro = XLSX.utils.book_new();

    // Preparar los datos para Excel
    const datos = [];

    // Agregar título y fecha en filas superiores
    const fechaActual = new Date().toLocaleDateString("es-PE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

    datos.push(["REPORTE DE CAMPAÑA DE PODA Y AMARRE - DON LUIS"]);
    datos.push(["Fecha de generación: " + fechaActual]);
    datos.push([]); // Fila vacía como separador

    // Agregar encabezados con formato específico
    datos.push([
      "ID",
      "NOMBRE COMPLETO",
      "DNI",
      "NACIONALIDAD",
      "CELULAR",
      "CORREO",
      "LABOR",
      "LUGAR DE RESIDENCIA",
      "FECHA REGISTRO",
    ]);

    // Agregar filas
    for (let i = 0; i < filas.length; i++) {
      // Obtener la fila actual
      const filaOriginal = Array.from(filas[i]);

      // Crear una copia de la fila para Excel asegurando que los nombres estén en mayúsculas
      const fila = [
        filaOriginal[0], // ID
        String(filaOriginal[1]).toUpperCase(), // Nombre Completo
        filaOriginal[2], // DNI
        String(filaOriginal[3]).toUpperCase(), // Nacionalidad
        filaOriginal[4], // Celular
        filaOriginal[5], // Correo
        String(filaOriginal[6]).toUpperCase(), // Labor
        String(filaOriginal[7]).toUpperCase(), // Lugar de Residencia
        filaOriginal[8], // Fecha Registro
      ];

      datos.push(fila);
    }

    // Crear la hoja de Excel
    const hoja = XLSX.utils.aoa_to_sheet(datos);

    // Establecer anchos de columna
    const anchos = [
      { wch: 8 }, // ID
      { wch: 30 }, // Nombre Completo
      { wch: 12 }, // DNI
      { wch: 15 }, // Nacionalidad
      { wch: 15 }, // Celular
      { wch: 30 }, // Correo
      { wch: 15 }, // Labor
      { wch: 25 }, // Lugar de Residencia
      { wch: 20 }, // Fecha Registro
    ];
    hoja["!cols"] = anchos;

    // Definir estilos (solo si la versión de XLSX lo soporta)
    try {
      // Aplicar estilos a celdas del título
      hoja["A1"] = {
        v: "REPORTE DE CAMPAÑA DE PODA Y AMARRE - DON LUIS",
        s: {
          font: { bold: true, color: { rgb: "FFFFFF" }, sz: 14 },
          fill: { fgColor: { rgb: "4F81BD" } },
          alignment: { horizontal: "center" },
        },
      };

      // Aplicar estilos a los encabezados (fila 4)
      for (let i = 0; i < 9; i++) {
        const letra = String.fromCharCode(65 + i); // A, B, C, etc.
        hoja[letra + "4"] = {
          v: datos[3][i],
          s: {
            font: { bold: true, color: { rgb: "FFFFFF" } },
            fill: { fgColor: { rgb: "365F91" } },
            alignment: { horizontal: "center" },
            border: { top: { style: "thin" }, bottom: { style: "thin" } },
          },
        };
      }

      // Combinar celdas del título
      if (!hoja["!merges"]) hoja["!merges"] = [];
      hoja["!merges"].push({ s: { r: 0, c: 0 }, e: { r: 0, c: 8 } }); // A1:I1
      hoja["!merges"].push({ s: { r: 1, c: 0 }, e: { r: 1, c: 8 } }); // A2:I2
    } catch (e) {
      console.log("La versión de XLSX no soporta estilos completos");
    }

    // Agregar la hoja al libro
    XLSX.utils.book_append_sheet(libro, hoja, "Registros de Poda y Amarre");

    // Descargar el archivo
    XLSX.writeFile(
      libro,
      `Reporte_Poda_Amarre_${formatoFechaArchivo(new Date())}.xlsx`
    );

    // Mostrar mensaje de éxito
    Swal.fire({
      icon: "success",
      title: "Excel Generado",
      text: "El reporte se ha exportado correctamente",
      confirmButtonText: "Aceptar",
      timer: 2000,
      timerProgressBar: true,
    });
  }

  // Función para imprimir
  function imprimir() {
    window.print();
  }

  // Función para formatear fecha para nombre de archivo
  function formatoFechaArchivo(fecha) {
    const dia = fecha.getDate().toString().padStart(2, "0");
    const mes = (fecha.getMonth() + 1).toString().padStart(2, "0");
    const anio = fecha.getFullYear();
    const hora = fecha.getHours().toString().padStart(2, "0");
    const minuto = fecha.getMinutes().toString().padStart(2, "0");

    return `${dia}${mes}${anio}_${hora}${minuto}`;
  }

  // Función para mostrar mensajes de error
  function mostrarError(mensaje) {
    Swal.fire({
      icon: "error",
      title: "¡Error!",
      text: mensaje,
      confirmButtonText: "Aceptar",
    });
  }

  // Inicialización
  inicializarTabla();
  cargarDatos();

  // Eventos
  $("#btn-buscar").on("click", filtrarDatos);
  $("#btn-limpiar").on("click", limpiarFiltros);
  $("#btn-exportar-excel").on("click", exportarExcel);
  $("#btn-imprimir").on("click", imprimir);

  // Permitir filtrar al presionar Enter en los campos de texto
  $("#filtro-dni").on("keydown", function (e) {
    if (e.keyCode === 13) {
      filtrarDatos();
    }
  });
});
