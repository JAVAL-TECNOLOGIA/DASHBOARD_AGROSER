// Función que verifica la pestaña activa y muestra su nombre en la consola
function AGRICOLAverificarPestañaActiva_SG() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#AGRICOLAsweetGlobeTabs a.active").attr("id");
  let nombrePestaña = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "AGRICOLAplantines-tab":
      nombrePestaña = "PLANTINES";

      AGRICOLAAGRICOLAiniciarTablaResumen_SG(nombrePestaña);
      break;
    case "AGRICOLApostcosecha-tab":
      nombrePestaña = "POST COSECHA";

      AGRICOLAAGRICOLAiniciarTablaResumen_SG(nombrePestaña);
      break;
    case "AGRICOLAcosecha-tab":
      nombrePestaña = "PRODUCCIÓN";

      AGRICOLAAGRICOLAiniciarTablaResumen_SG(nombrePestaña);
      break;
    default:
      nombrePestaña = "Pestaña desconocida";
  }

  return nombrePestaña;
}

function AGRICOLAverificarPestañaActiva_AC() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#AGRICOLAautumnCrispTabs a.active").attr("id");
  let nombrePestaña_AC = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "AGRICOLAplantines-tab":
      nombrePestaña_AC = "PLANTINES";

      AGRICOLAiniciarTablaResumen_AC(nombrePestaña_AC);
      break;
    case "AGRICOLApostcosecha-tab":
      nombrePestaña_AC = "POST COSECHA";

      AGRICOLAiniciarTablaResumen_AC(nombrePestaña_AC);
      break;
    case "AGRICOLAcosecha-tab":
      nombrePestaña_AC = "PRODUCCIÓN";

      AGRICOLAiniciarTablaResumen_AC(nombrePestaña_AC);
      break;
    default:
      nombrePestaña_AC = "Pestaña desconocida";
  }

  return nombrePestaña_AC;
}

function AGRICOLAverificarPestañaActiva_MC() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#AGRICOLAmoscatelTabs a.active").attr("id");
  let nombrePestaña_MC = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "AGRICOLAplantines-tab":
      nombrePestaña_MC = "PLANTINES";

      AGRICOLAiniciarTablaResumen_MC(nombrePestaña_MC);
      break;
    case "AGRICOLApostcosecha-tab":
      nombrePestaña_MC = "POST COSECHA";

      AGRICOLAiniciarTablaResumen_MC(nombrePestaña_MC);
      break;
    case "AGRICOLAcosecha-tab":
      nombrePestaña_MC = "PRODUCCIÓN";

      AGRICOLAiniciarTablaResumen_MC(nombrePestaña_MC);
      break;
    default:
      nombrePestaña_MC = "Pestaña desconocida";
  }

  return nombrePestaña_MC;
}

function AGRICOLAverificarPestañaActiva_SUGRA() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#AGRICOLAsugraTabs a.active").attr("id");
  let nombrePestaña_SUGRA = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "AGRICOLAplantines-tab":
      nombrePestaña_SUGRA = "PLANTINES";

      AGRICOLAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA);
      break;
    case "AGRICOLApostcosecha-tab":
      nombrePestaña_SUGRA = "POST COSECHA";

      AGRICOLAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA);
      break;
    case "AGRICOLAcosecha-tab":
      nombrePestaña_SUGRA = "PRODUCCIÓN";

      AGRICOLAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA);
      break;
    default:
      nombrePestaña_SUGRA = "Pestaña desconocida";
  }

  // Inicializar los eventos de búsqueda para todos los modales SUGRA cuando se seleccione esta variedad
  // Esto garantiza que buscarproducto_SUGRA se ejecute al cargar la interfaz para SUGRA
  $(document).ready(function () {
    // Si hay algún modal abierto para SUGRA, inicializar los eventos
    if ($("#AGRICOLAmodalProducto_SUGRA").length > 0) {
      $("#AGRICOLAmodalProducto_SUGRA")
        .off("shown.bs.modal")
        .on("shown.bs.modal", function () {
          AGRICOLAinitEventosFormularioProducto_SUGRA();
        });
    }

    // Asociar evento al botón de nuevo producto si existe
    $(".btn-nuevo-producto-sugra")
      .off("click")
      .on("click", function () {
        const programaId = $(this).data("programa-id");
        if (programaId) {
          AGRICOLAabrirModalNuevoProducto_SUGRA(programaId);
        }
      });
  });

  return nombrePestaña_SUGRA;
}

//INICIALIZAR LA TABLA DE RESUMEN VARIEDAD SWEET GLOBE
function AGRICOLAAGRICOLAiniciarTablaResumen_SG(nombrePestaña) {
  //PLANTINES
  if (nombrePestaña == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAAGRICOLAtablaFertilizacionPlantines_SG")) {
      $("#AGRICOLAAGRICOLAtablaFertilizacionPlantines_SG").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAAGRICOLAtablaFertilizacionPlantines_SG").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
        type: "GET",
        data: function (d) {
          d.idfase = 1;
          d.idvariedad = 1;
          d.idcampania = $("#filtroAnioPresupuesto").val();
          return d;
        },
        dataSrc: function (json) {
          const datos = json.data || [];

          // Actualizar el número de faces registradas

          $("#AGRICOLAfacesRegistradosSG_PLANTINES").text(datos.length);

          // Actualizar estadisticas cuando se cargan los datos
          AGRICOLAactualizarEstadisticasPlantines_SG(datos);

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
        {
          data: null,

          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_SG(nombrePestaña);
      },
    });
  } else if (nombrePestaña == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionPostCosecha_SG")) {
      $("#AGRICOLAtablaFertilizacionPostCosecha_SG").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionPostCosecha_SG").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
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
          //AGRICOLAactualizarEstadisticasPlantines_SG(datos);

          // Actualizar el número de faces registradas
          $("#AGRICOLAfacesRegistradosSG_POSTCOSECHA").text(datos.length);

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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_SG(nombrePestaña);
      },
    });
  } else if (nombrePestaña == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionProduccion_SG")) {
      $("#AGRICOLAtablaFertilizacionProduccion_SG").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionProduccion_SG").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
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
          //AGRICOLAactualizarEstadisticasPlantines_SG(datos);

          // Actualizar el número de faces registradas
          $("#AGRICOLAfacesRegistradosSG_PRODUCCION").text(datos.length);

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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_SG(nombrePestaña);
      },
    });
  }
}

function AGRICOLAiniciarTablaResumen_AC(nombrePestaña_AC) {
  //PLANTINES
  if (nombrePestaña_AC == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionPlantines_AC")) {
      $("#AGRICOLAtablaFertilizacionPlantines_AC").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionPlantines_AC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
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
          //AGRICOLAactualizarEstadisticasPlantines_SG(datos);

          $("#AGRICOLAfacesRegistradosAC_PLANTINES").text(datos.length);

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
        {
          data: null,

          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_AC(nombrePestaña_AC);
      },
    });
  } else if (nombrePestaña_AC == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionPostCosecha_AC")) {
      $("#AGRICOLAtablaFertilizacionPostCosecha_AC").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionPostCosecha_AC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
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
          //AGRICOLAactualizarEstadisticasPlantines_SG(datos);
          $("#AGRICOLAfacesRegistradosAC_POSTCOSECHA").text(datos.length);

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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_AC(nombrePestaña_AC);
      },
    });
  } else if (nombrePestaña_AC == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionProduccion_AC")) {
      $("#AGRICOLAtablaFertilizacionProduccion_AC").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionProduccion_AC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
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
          //AGRICOLAactualizarEstadisticasPlantines_SG(datos);
          $("#AGRICOLAfacesRegistradosAC_PRODUCCION").text(datos.length);
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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_AC(nombrePestaña_AC);
      },
    });
  }
}

function AGRICOLAiniciarTablaResumen_MC(nombrePestaña_MC) {
  //PLANTINES
  if (nombrePestaña_MC == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionPlantines_MC")) {
      $("#AGRICOLAtablaFertilizacionPlantines_MC").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionPlantines_MC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
        type: "GET",
        data: function (d) {
          d.idfase = 1;
          d.idvariedad = 3;
          d.idcampania = $("#filtroAnioPresupuesto").val();
          return d;
        },
        dataSrc: function (json) {
          const datos = json.data || [];

          // Actualizar el número de faces registradas
          $("#AGRICOLAfacesRegistradasMC_PLANTINES").text(datos.length);

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
        {
          data: null,

          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_MC(nombrePestaña_MC);
      },
    });
  } else if (nombrePestaña_MC == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionPostCosecha_MC")) {
      $("#AGRICOLAtablaFertilizacionPostCosecha_MC").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionPostCosecha_MC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
        type: "GET",
        data: function (d) {
          d.idfase = 2;
          d.idvariedad = 3;
          d.idcampania = $("#filtroAnioPresupuesto").val();
          return d;
        },
        dataSrc: function (json) {
          const datos = json.data || [];

          // Actualizar el número de faces registradas
          $("#AGRICOLAfacesRegistradasMC_POSTCOSECHA").text(datos.length);

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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_MC(nombrePestaña_MC);
      },
    });
  } else if (nombrePestaña_MC == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionProduccion_MC")) {
      $("#AGRICOLAtablaFertilizacionProduccion_MC").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionProduccion_MC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
        type: "GET",
        data: function (d) {
          d.idfase = 3;
          d.idvariedad = 3;
          d.idcampania = $("#filtroAnioPresupuesto").val();
          return d;
        },
        dataSrc: function (json) {
          const datos = json.data || [];

          // Actualizar el número de faces registradas
          $("#AGRICOLAfacesRegistradasMC_PRODUCCION").text(datos.length);

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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_MC(nombrePestaña_MC);
      },
    });
  }
}

function AGRICOLAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA) {
  //PLANTINES
  if (nombrePestaña_SUGRA == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionPlantines_SUGRA")) {
      $("#AGRICOLAtablaFertilizacionPlantines_SUGRA").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionPlantines_SUGRA").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
        type: "GET",
        data: function (d) {
          d.idfase = 1;
          d.idvariedad = 4;
          d.idcampania = $("#filtroAnioPresupuesto").val();
          return d;
        },
        dataSrc: function (json) {
          const datos = json.data || [];

          // Actualizar el número de faces registradas
          $("#facesRegistradasSUGRA_PLANTINES").text(datos.length);

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
        {
          data: null,

          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_SUGRA(nombrePestaña_SUGRA);
      },
    });
  } else if (nombrePestaña_SUGRA == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionPostCosecha_SUGRA")) {
      $("#AGRICOLAtablaFertilizacionPostCosecha_SUGRA").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionPostCosecha_SUGRA").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
        type: "GET",
        data: function (d) {
          d.idfase = 2;
          d.idvariedad = 4;
          d.idcampania = $("#filtroAnioPresupuesto").val();
          return d;
        },
        dataSrc: function (json) {
          const datos = json.data || [];

          // Actualizar el número de faces registradas
          $("#AGRICOLAfacesRegistradasSUGRA_POSTCOSECHA").text(datos.length);

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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_SUGRA(nombrePestaña_SUGRA);
      },
    });
  } else if (nombrePestaña_SUGRA == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#AGRICOLAtablaFertilizacionProduccion_SUGRA")) {
      $("#AGRICOLAtablaFertilizacionProduccion_SUGRA").DataTable().destroy();
    }

    const tabla = $("#AGRICOLAtablaFertilizacionProduccion_SUGRA").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_agricola_ajs/",
        type: "GET",
        data: function (d) {
          d.idfase = 3;
          d.idvariedad = 4;
          d.idcampania = $("#filtroAnioPresupuesto").val();
          return d;
        },
        dataSrc: function (json) {
          const datos = json.data || [];

          // Actualizar el número de faces registradas
          $("#facesRegistradasSUGRA_PRODUCCION").text(datos.length);

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
        {
          data: null,
          className: "text-center",
          render: function (data, type, row, meta) {
            return meta.row + 1;
          },
        },
        { data: "NOMBRE" },
        { data: "FECHA_INICIO" },
        { data: "FECHA_FIN" },
        {
          data: null,

          className: "text-center",
          render: function (data, type, row) {
            // Verificar si hay datos de sector y lote
            const sector = row.SECTOR || "No definido";
            const lote = row.LOTE_NOMBRE || "No definido";

            return `
              <div class="d-flex justify-content-center align-items-center flex-wrap">
                <!-- Sector -->
                <span class="badge badge-secondary px-2 py-1 rounded-pill shadow-sm mr-2 mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #6c757d, #5a6268);">
                  <i class="fas fa-layer-group mr-1"></i>
                  <strong>Sector:</strong> ${sector}
                </span>
                
                <!-- Lote -->
                <span class="badge badge-info px-2 py-1 rounded-pill shadow-sm mb-1" 
                      style="font-size: 0.75rem; background: linear-gradient(135deg, #17a2b8, #138496);">
                  <i class="fas fa-map-marker-alt mr-1"></i>
                  <strong>Lote:</strong> ${lote}
                </span>
              </div>
            `;
          },
        },
      ],
      // Agregar clase a las filas para mejor estilo con hover
      createdRow: function (row, data, dataIndex) {
        $(row).addClass("programa-row");
        // Agregar el ID como atributo data para identificar la fila
        $(row).attr("data-id", data.ID);
      },
      // Cuando la tabla termina de inicializarse, configurar el menú contextual
      initComplete: function () {
        AGRICOLAconfigurarMenuContextual_SUGRA(nombrePestaña_SUGRA);
      },
    });
  }
}
//============================================================================
// CONFIGURACIONES PARA EL MENU CONTEXTUAL DE LAS FASES
//============================================================================
// Esta función soluciona el problema con el menú contextual
function AGRICOLAconfigurarMenuContextual_SG(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#AGRICOLAAGRICOLAtablaFertilizacionPlantines_SG";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#AGRICOLAtablaFertilizacionPostCosecha_SG";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#AGRICOLAtablaFertilizacionProduccion_SG";
  } else {
    return; // Si no es una pestaña válida, no hacer nada
  }

  // Eliminar eventos previos para evitar duplicados
  $(`${tablaSelector} tbody`).off("contextmenu");

  // Eliminar evento de doble clic previo para evitar duplicados
  $(`${tablaSelector} tbody`).off("dblclick");

  // Configurar evento de doble clic en las filas para abrir el modal de detalles
  $(`${tablaSelector} tbody`).on("dblclick", "tr", function () {
    // Obtener el objeto DataTable
    const tabla = $(`${tablaSelector}`).DataTable();

    // Obtener los datos de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) {
      return; // Si no hay datos, no hacer nada
    }

    const idRegistro = filaSeleccionada.ID;

    // Llamar a la función que mostrará el modal con los detalles
    AGRICOLAmostrarDetallesProductos(idRegistro);
  });

  // Configurar evento de clic derecho en las filas
  $(`${tablaSelector} tbody`).on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el objeto DataTable
    const tabla = $(`${tablaSelector}`).DataTable();

    // Obtener los datos de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) {
      return; // Si no hay datos, no hacer nada
    }

    const idRegistro = filaSeleccionada.ID;

    // Eliminar el menú contextual existente, para recrearlo completo
    $("#menuContextualFertilizacion_SG").remove();

    // Crear el menú contextual de nuevo
    $("body").append(`
      <div id="menuContextualFertilizacion_SG" class="dropdown-menu shadow" 
           style="display: none; position: absolute; z-index: 9999;">
        <h6 class="dropdown-header">Opciones</h6>
        <a class="dropdown-item text-primary" href="#" id="btnEditarFertilizacion_SG">
          <i class="fas fa-edit mr-2"></i> Editar
        </a>
        <div class="dropdown-divider"></div>
        <a class="dropdown-item text-danger" href="#" id="btnEliminarFertilizacion_SG">
          <i class="fas fa-trash-alt mr-2"></i> Eliminar
        </a>
      </div>
    `);

    // Configurar los eventos justo después de crear el menú
    $("#btnEditarFertilizacion_SG")
      .off("click")
      .on("click", function () {
        AGRICOLAeditarFertilizacion_SG(idRegistro);
        $("#menuContextualFertilizacion_SG").hide();
      });

    $("#btnEliminarFertilizacion_SG")
      .off("click")
      .on("click", function () {
        AGRICOLAeliminarFertilizacion(idRegistro);
        $("#menuContextualFertilizacion_SG").hide();
      });

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarFertilizacion_SG").attr("data-id", idRegistro);
    $("#btnEliminarFertilizacion_SG").attr("data-id", idRegistro);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualFertilizacion_SG");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
      zIndex: 9999, // Asegurar que está por encima de otros elementos
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");

    // Evitar que el evento click del document se active inmediatamente
    e.stopPropagation();

    return false;
  });

  // Quitar el manejador de eventos anterior para evitar múltiples bindings
  $(document).off("click.menuContextual");

  // Ocultar el menú al hacer clic en cualquier parte
  $(document).on("click.menuContextual", function () {
    $("#menuContextualFertilizacion_SG").hide();
  });
}

function AGRICOLAconfigurarMenuContextual_AC(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#AGRICOLAtablaFertilizacionPlantines_AC";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#AGRICOLAtablaFertilizacionPostCosecha_AC";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#AGRICOLAtablaFertilizacionProduccion_AC";
  } else {
    return; // Si no es una pestaña válida, no hacer nada
  }

  // Eliminar eventos previos para evitar duplicados
  $(`${tablaSelector} tbody`).off("contextmenu");

  // Eliminar evento de doble clic previo para evitar duplicados
  $(`${tablaSelector} tbody`).off("dblclick");

  // Configurar evento de doble clic en las filas para abrir el modal de detalles
  $(`${tablaSelector} tbody`).on("dblclick", "tr", function () {
    // Obtener el objeto DataTable
    const tabla = $(`${tablaSelector}`).DataTable();

    // Obtener los datos de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) {
      return; // Si no hay datos, no hacer nada
    }

    const idRegistro = filaSeleccionada.ID;

    // Llamar a la función que mostrará el modal con los detalles
    AGRICOLAmostrarDetallesProductos_AC(idRegistro);
  });

  // Configurar evento de clic derecho en las filas
  $(`${tablaSelector} tbody`).on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el objeto DataTable
    const tabla = $(`${tablaSelector}`).DataTable();

    // Obtener los datos de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) {
      return; // Si no hay datos, no hacer nada
    }

    const idRegistro = filaSeleccionada.ID;

    // Eliminar el menú contextual existente, para recrearlo completo
    $("#menuContextualFertilizacion_AC").remove();

    // Crear el menú contextual de nuevo
    $("body").append(`
      <div id="menuContextualFertilizacion_AC" class="dropdown-menu shadow" 
           style="display: none; position: absolute; z-index: 9999;">
        <h6 class="dropdown-header">Opciones</h6>
        <a class="dropdown-item text-primary" href="#" id="btnEditarFertilizacion_AC">
          <i class="fas fa-edit mr-2"></i> Editar
        </a>
        <div class="dropdown-divider"></div>
        <a class="dropdown-item text-danger" href="#" id="btnEliminarFertilizacion_AC">
          <i class="fas fa-trash-alt mr-2"></i> Eliminar
        </a>
      </div>
    `);

    // Configurar los eventos justo después de crear el menú
    $("#btnEditarFertilizacion_AC")
      .off("click")
      .on("click", function () {
        AGRICOLAeditarFertilizacion_AC(idRegistro);
        $("#menuContextualFertilizacion_AC").hide();
      });

    $("#btnEliminarFertilizacion_AC")
      .off("click")
      .on("click", function () {
        AGRICOLAeliminarFertilizacion_AC(idRegistro);
        $("#menuContextualFertilizacion_AC").hide();
      });

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarFertilizacion_AC").attr("data-id", idRegistro);
    $("#btnEliminarFertilizacion_AC").attr("data-id", idRegistro);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualFertilizacion_AC");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
      zIndex: 9999, // Asegurar que está por encima de otros elementos
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");

    // Evitar que el evento click del document se active inmediatamente
    e.stopPropagation();

    return false;
  });

  // Quitar el manejador de eventos anterior para evitar múltiples bindings
  $(document).off("click.menuContextualAC");

  // Ocultar el menú al hacer clic en cualquier parte
  $(document).on("click.menuContextualAC", function () {
    $("#menuContextualFertilizacion_AC").hide();
  });
}

//============================================================================
// CONFIGURACIÓN DEL MENÚ CONTEXTUAL PARA MOSCATEL
//============================================================================

function AGRICOLAconfigurarMenuContextual_MC(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#AGRICOLAtablaFertilizacionPlantines_MC";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#AGRICOLAtablaFertilizacionPostCosecha_MC";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#AGRICOLAtablaFertilizacionProduccion_MC";
  } else {
    return; // Si no es una pestaña válida, no hacer nada
  }

  // Eliminar eventos previos para evitar duplicados
  $(`${tablaSelector} tbody`).off("contextmenu");

  // Configurar evento de clic derecho en las filas
  $(`${tablaSelector} tbody`).on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el objeto DataTable
    const tabla = $(`${tablaSelector}`).DataTable();

    // Obtener los datos de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) {
      return; // Si no hay datos, no hacer nada
    }

    const idRegistro = filaSeleccionada.ID;

    // Eliminar el menú contextual existente, para recrearlo completo
    $("#menuContextualFertilizacion_MC").remove();

    // Crear el menú contextual de nuevo
    $("body").append(`
      <div id="menuContextualFertilizacion_MC" class="dropdown-menu shadow" 
           style="display: none; position: absolute; z-index: 9999;">
        <h6 class="dropdown-header">Opciones</h6>
        <a class="dropdown-item text-primary" href="#" id="btnEditarFertilizacion_MC">
          <i class="fas fa-edit mr-2"></i> Editar
        </a>
        <div class="dropdown-divider"></div>
        <a class="dropdown-item text-danger" href="#" id="btnEliminarFertilizacion_MC">
          <i class="fas fa-trash-alt mr-2"></i> Eliminar
        </a>
      </div>
    `);

    // Configurar los eventos justo después de crear el menú
    $("#btnEditarFertilizacion_MC")
      .off("click")
      .on("click", function () {
        AGRICOLAeditarFertilizacion_MC(idRegistro);
        $("#menuContextualFertilizacion_MC").hide();
      });

    $("#btnEliminarFertilizacion_MC")
      .off("click")
      .on("click", function () {
        AGRICOLAeliminarFertilizacion_MC(idRegistro);
        $("#menuContextualFertilizacion_MC").hide();
      });

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarFertilizacion_MC").attr("data-id", idRegistro);
    $("#btnEliminarFertilizacion_MC").attr("data-id", idRegistro);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualFertilizacion_MC");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
      zIndex: 9999, // Asegurar que está por encima de otros elementos
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");

    // Evitar que el evento click del document se active inmediatamente
    e.stopPropagation();

    return false;
  });

  // Quitar el manejador de eventos anterior para evitar múltiples bindings
  $(document).off("click.menuContextualMC");

  // Ocultar el menú al hacer clic en cualquier parte
  $(document).on("click.menuContextualMC", function () {
    $("#menuContextualFertilizacion_MC").hide();
  });

  // Configurar evento para mostrar detalles al hacer clic en una fila
  // Usar el selector correcto y desactivar eventos anteriores
  $(`${tablaSelector} tbody`)
    .off("click", "tr")
    .on("click", "tr", function () {
      const tabla = $(`${tablaSelector}`).DataTable();
      const filaSeleccionada = tabla.row(this).data();

      if (filaSeleccionada && filaSeleccionada.ID) {
        AGRICOLAmostrarDetallesProductos_MC(filaSeleccionada.ID);
      }
    });
}

//============================================================================
// CONFIGURACIÓN DEL MENÚ CONTEXTUAL PARA SUGRA
//============================================================================

function AGRICOLAconfigurarMenuContextual_SUGRA(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#AGRICOLAtablaFertilizacionPlantines_SUGRA";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#AGRICOLAtablaFertilizacionPostCosecha_SUGRA";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#AGRICOLAtablaFertilizacionProduccion_SUGRA";
  } else {
    return; // Si no es una pestaña válida, no hacer nada
  }

  // Eliminar eventos previos para evitar duplicados
  $(`${tablaSelector} tbody`).off("contextmenu");

  // Eliminar evento de doble clic previo para evitar duplicados
  $(`${tablaSelector} tbody`).off("dblclick");

  // Configurar evento de doble clic en las filas para abrir el modal de detalles
  $(`${tablaSelector} tbody`).on("dblclick", "tr", function () {
    // Obtener el objeto DataTable
    const tabla = $(`${tablaSelector}`).DataTable();

    // Obtener los datos de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) {
      return; // Si no hay datos, no hacer nada
    }

    const idRegistro = filaSeleccionada.ID;

    // Llamar a la función que mostrará el modal con los detalles
    AGRICOLAmostrarDetallesProductos_SUGRA(idRegistro);
  });

  // Configurar evento de clic derecho en las filas
  $(`${tablaSelector} tbody`).on("contextmenu", "tr", function (e) {
    e.preventDefault(); // Prevenir el menú contextual del navegador

    // Obtener el objeto DataTable
    const tabla = $(`${tablaSelector}`).DataTable();

    // Obtener los datos de la fila seleccionada
    const filaSeleccionada = tabla.row(this).data();
    if (!filaSeleccionada) {
      return; // Si no hay datos, no hacer nada
    }

    const idRegistro = filaSeleccionada.ID;

    // Eliminar el menú contextual existente, para recrearlo completo
    $("#menuContextualFertilizacion_SUGRA").remove();

    // Crear el menú contextual de nuevo
    $("body").append(`
      <div id="menuContextualFertilizacion_SUGRA" class="dropdown-menu shadow" 
           style="display: none; position: absolute; z-index: 9999;">
        <h6 class="dropdown-header">Opciones</h6>
        <a class="dropdown-item text-primary" href="#" id="btnEditarFertilizacion_SUGRA">
          <i class="fas fa-edit mr-2"></i> Editar
        </a>
        <div class="dropdown-divider"></div>
        <a class="dropdown-item text-danger" href="#" id="btnEliminarFertilizacion_SUGRA">
          <i class="fas fa-trash-alt mr-2"></i> Eliminar
        </a>
      </div>
    `);

    // Configurar los eventos justo después de crear el menú
    $("#btnEditarFertilizacion_SUGRA")
      .off("click")
      .on("click", function () {
        AGRICOLAeditarFertilizacion_SUGRA(idRegistro);
        $("#menuContextualFertilizacion_SUGRA").hide();
      });

    $("#btnEliminarFertilizacion_SUGRA")
      .off("click")
      .on("click", function () {
        AGRICOLAeliminarFertilizacion_SUGRA(idRegistro);
        $("#menuContextualFertilizacion_SUGRA").hide();
      });

    // Guardar el ID en los botones del menú para usarlo después
    $("#btnEditarFertilizacion_SUGRA").attr("data-id", idRegistro);
    $("#btnEliminarFertilizacion_SUGRA").attr("data-id", idRegistro);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#menuContextualFertilizacion_SUGRA");
    menuContextual.css({
      display: "block",
      left: e.pageX,
      top: e.pageY,
      zIndex: 9999, // Asegurar que está por encima de otros elementos
    });

    // Resaltar la fila seleccionada
    $(this).addClass("table-primary").siblings().removeClass("table-primary");

    // Evitar que el evento click del document se active inmediatamente
    e.stopPropagation();

    return false;
  });

  // Quitar el manejador de eventos anterior para evitar múltiples bindings
  $(document).off("click.menuContextualSUGRA");

  // Ocultar el menú al hacer clic en cualquier parte
  $(document).on("click.menuContextualSUGRA", function () {
    $("#menuContextualFertilizacion_SUGRA").hide();
  });

  // Configurar evento para mostrar detalles al hacer clic en una fila
  // Usar el selector correcto y desactivar eventos anteriores
  $(`${tablaSelector} tbody`)
    .off("click", "tr")
    .on("click", "tr", function () {
      const tabla = $(`${tablaSelector}`).DataTable();
      const filaSeleccionada = tabla.row(this).data();

      if (filaSeleccionada && filaSeleccionada.ID) {
        AGRICOLAmostrarDetallesProductos_SUGRA(filaSeleccionada.ID);
      }
    });
}

//============================================================================
// FUNCIONES PARA GUARDAR EL NUEVO PROGRAMA
//============================================================================

function AGRICOLAguardarNuevoPrograma_SG() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#AGRICOLAnombrePrograma").val().trim();
  const fechaInicio = $("#AGRICOLAfechaInicio").val();
  const fechaFin = $("#AGRICOLAfechaFin").val();
  const descripcion = $("#AGRICOLAdescripcion_riego").val() || "";
  const idfase = $("#AGRICOLAidfase").val();
  const idvariedad = $("#AGRICOLAidvariedad").val();
  const idusuario = $("#AGRICOLAidusuario").val();
  const idlote = $("#AGRICOLAselectLote").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#AGRICOLAidregistro").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#AGRICOLAselectLote").css("border", "1px solid red");
    $("#AGRICOLAselectLote").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#AGRICOLAnombrePrograma").css("border", "1px solid red");
    $("#AGRICOLAnombrePrograma").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#AGRICOLAfechaInicio").css("border", "1px solid red");
    $("#AGRICOLAfechaInicio").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#AGRICOLAfechaFin").css("border", "1px solid red");
    $("#AGRICOLAfechaFin").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#AGRICOLAfechaFin").css("border", "1px solid red");
      $("#AGRICOLAfechaFin").after(
        "<span class='text-danger'>La fecha de fin debe ser posterior a la fecha de inicio</span>"
      );
      hayErrores = true;
    }
  }

  // SI TODOS LOS CAMPOS ESTAN CORRECTOS, ENVIAR LOS DATOS AL BACKEND
  if (!hayErrores) {
    // Crear el objeto con los datos
    const datosPrograma = {
      IDUSUARIO: idusuario,
      IDVARIEDAD: idvariedad,
      IDFASE: idfase,
      IDLOTE: idlote,
      NOMBRE: nombrePrograma,
      FECHA_INICIO: fechaInicio,
      FECHA_FIN: fechaFin,
      DESCRIPCION: descripcion,
    };

    // Añadir el ID solo si estamos en modo edición
    if (esEdicion) {
      datosPrograma.ID = idregistro;
    }

    // Determinar URL y método según si es creación o edición
    const url = esEdicion
      ? `/riego/api/materia_agricola_ajs/${idregistro}/`
      : "/riego/api/materia_agricola_ajs/";
    const metodo = esEdicion ? "PUT" : "POST";

    // Enviar datos al servidor
    $.ajax({
      url: url,
      type: metodo,
      contentType: "application/json",
      data: JSON.stringify(datosPrograma),
      success: function (response) {
        // Mostrar mensaje de éxito
        Swal.fire({
          title: "¡Éxito!",
          text: esEdicion
            ? "El programa de fertilización ha sido actualizado correctamente"
            : "El programa de fertilización ha sido creado correctamente",
          icon: "success",
          confirmButtonText: "Aceptar",
        });

        // Cerrar el modal
        $("#AGRICOLAmodalCrearPrograma").modal("hide");

        // Limpiar el formulario
        $("#AGRICOLAformCrearPrograma")[0].reset();

        // Limpiar el selector de lotes
        $("#AGRICOLAselectLote").find("option:not(:first)").remove();

        // Eliminar el campo idregistro si existe
        $("#AGRICOLAidregistro").remove();

        // Restaurar el texto del botón
        $("#AGRICOLAbtnGuardarProgramaSG").text("Guardar");

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = AGRICOLAverificarPestañaActiva_SG();
        AGRICOLAAGRICOLAiniciarTablaResumen_SG(nombrePestaña);
      },
      error: function (xhr, status, error) {
        // Mostrar mensaje de error
        let errorMsg = esEdicion
          ? "Ha ocurrido un error al actualizar el programa"
          : "Ha ocurrido un error al guardar el programa";

        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        }

        Swal.fire({
          title: "Error",
          text: errorMsg,
          icon: "error",
          confirmButtonText: "Aceptar",
        });
      },
    });
  }
}

function AGRICOLAguardarNuevoPrograma_AC() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#AGRICOLAnombrePrograma_AC").val().trim();
  const fechaInicio = $("#AGRICOLAfechaInicio_AC").val();
  const fechaFin = $("#AGRICOLAfechaFin_AC").val();
  const descripcion = $("#AGRICOLAdescripcion_riego_AC").val() || "";
  const idfase = $("#AGRICOLAidfase_AC").val();
  const idvariedad = $("#AGRICOLAidvariedad_AC").val();
  const idusuario = $("#AGRICOLAidusuario").val();
  const idlote = $("#AGRICOLAselectLote_AC").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#AGRICOLAidregistro_AC").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#AGRICOLAselectLote_AC").css("border", "1px solid red");
    $("#AGRICOLAselectLote_AC").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#AGRICOLAnombrePrograma_AC").css("border", "1px solid red");
    $("#AGRICOLAnombrePrograma_AC").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#AGRICOLAfechaInicio_AC").css("border", "1px solid red");
    $("#AGRICOLAfechaInicio_AC").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#AGRICOLAfechaFin_AC").css("border", "1px solid red");
    $("#AGRICOLAfechaFin_AC").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#AGRICOLAfechaFin_AC").css("border", "1px solid red");
      $("#AGRICOLAfechaFin_AC").after(
        "<span class='text-danger'>La fecha de fin debe ser posterior a la fecha de inicio</span>"
      );
      hayErrores = true;
    }
  }

  // SI TODOS LOS CAMPOS ESTAN CORRECTOS, ENVIAR LOS DATOS AL BACKEND
  if (!hayErrores) {
    // Crear el objeto con los datos
    const datosPrograma = {
      IDUSUARIO: idusuario,
      IDVARIEDAD: idvariedad,
      IDFASE: idfase,
      IDLOTE: idlote,
      NOMBRE: nombrePrograma,
      FECHA_INICIO: fechaInicio,
      FECHA_FIN: fechaFin,
      DESCRIPCION: descripcion,
    };

    // Añadir el ID solo si estamos en modo edición
    if (esEdicion) {
      datosPrograma.ID = idregistro;
    }

    // Determinar la URL y el método según si es edición o creación
    const url = esEdicion
      ? `/riego/api/materia_agricola_ajs/${idregistro}/`
      : "/riego/api/materia_agricola_ajs/";

    const metodo = esEdicion ? "PUT" : "POST";
    const mensajeExito = esEdicion
      ? "El programa de fertilización ha sido actualizado correctamente"
      : "El programa de fertilización ha sido creado correctamente";

    // Enviar datos al servidor
    $.ajax({
      url: url,
      type: metodo,
      contentType: "application/json",
      data: JSON.stringify(datosPrograma),
      success: function (response) {
        // Mostrar mensaje de éxito
        Swal.fire({
          title: "¡Éxito!",
          text: mensajeExito,
          icon: "success",
          confirmButtonText: "Aceptar",
        });

        // Cerrar el modal
        $("#AGRICOLAmodalCrearPrograma_AC").modal("hide");

        // Limpiar el formulario
        $("#AGRICOLAformCrearPrograma_AC")[0].reset();

        // Limpiar el selector de lotes
        $("#AGRICOLAselectLote_AC").find("option:not(:first)").remove();

        // Si estábamos en modo edición, cambiar el botón de vuelta a "Guardar"
        if (esEdicion) {
          $("#AGRICOLAbtnGuardarProgramaAC").html(
            '<i class="fas fa-save mr-1"></i> Guardar'
          );
          // Eliminar el campo oculto del ID
          $("#AGRICOLAidregistro_AC").remove();
        }

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = AGRICOLAverificarPestañaActiva_AC();
        AGRICOLAiniciarTablaResumen_AC(nombrePestaña);
      },
      error: function (xhr, status, error) {
        // Mostrar mensaje de error
        let errorMsg = esEdicion
          ? "Ha ocurrido un error al actualizar el programa"
          : "Ha ocurrido un error al guardar el programa";

        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        }

        Swal.fire({
          title: "Error",
          text: errorMsg,
          icon: "error",
          confirmButtonText: "Aceptar",
        });
      },
    });
  }
}

function AGRICOLAguardarNuevoPrograma_MC() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#AGRICOLAnombrePrograma_MC").val().trim();
  const fechaInicio = $("#AGRICOLAfechaInicio_MC").val();
  const fechaFin = $("#AGRICOLAfechaFin_MC").val();
  const descripcion = $("#AGRICOLAdescripcion_riego_MC").val() || "";
  const idfase = $("#AGRICOLAidfase_MC").val();
  const idvariedad = $("#AGRICOLAidvariedad_MC").val();
  const idusuario = $("#AGRICOLAidusuario").val();
  const idlote = $("#AGRICOLAselectLote_MC").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#AGRICOLAidregistro_MC").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#AGRICOLAselectLote_MC").css("border", "1px solid red");
    $("#AGRICOLAselectLote_MC").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#AGRICOLAnombrePrograma_MC").css("border", "1px solid red");
    $("#AGRICOLAnombrePrograma_MC").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#AGRICOLAfechaInicio_MC").css("border", "1px solid red");
    $("#AGRICOLAfechaInicio_MC").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#AGRICOLAfechaFin_MC").css("border", "1px solid red");
    $("#AGRICOLAfechaFin_MC").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#AGRICOLAfechaFin_MC").css("border", "1px solid red");
      $("#AGRICOLAfechaFin_MC").after(
        "<span class='text-danger'>La fecha de fin debe ser posterior a la fecha de inicio</span>"
      );
      hayErrores = true;
    }
  }

  // SI TODOS LOS CAMPOS ESTAN CORRECTOS, ENVIAR LOS DATOS AL BACKEND
  if (!hayErrores) {
    // Crear el objeto con los datos
    const datosPrograma = {
      IDUSUARIO: idusuario,
      IDVARIEDAD: idvariedad,
      IDFASE: idfase,
      IDLOTE: idlote,
      NOMBRE: nombrePrograma,
      FECHA_INICIO: fechaInicio,
      FECHA_FIN: fechaFin,
      DESCRIPCION: descripcion,
    };

    // Añadir el ID solo si estamos en modo edición
    if (esEdicion) {
      datosPrograma.ID = idregistro;
    }

    // Determinar URL y método según si es creación o edición
    const url = esEdicion
      ? `/riego/api/materia_agricola_ajs/${idregistro}/`
      : "/riego/api/materia_agricola_ajs/";
    const metodo = esEdicion ? "PUT" : "POST";

    // Enviar datos al servidor
    $.ajax({
      url: url,
      type: metodo,
      contentType: "application/json",
      data: JSON.stringify(datosPrograma),
      success: function (response) {
        // Mostrar mensaje de éxito
        Swal.fire({
          title: "¡Éxito!",
          text: esEdicion
            ? "El programa de fertilización ha sido actualizado correctamente"
            : "El programa de fertilización ha sido creado correctamente",
          icon: "success",
          confirmButtonText: "Aceptar",
        });

        // Cerrar el modal
        $("#AGRICOLAmodalCrearPrograma_MC").modal("hide");

        // Limpiar el formulario
        $("#AGRICOLAformCrearPrograma_MC")[0].reset();

        // Limpiar el selector de lotes
        $("#AGRICOLAselectLote_MC").find("option:not(:first)").remove();

        // Eliminar el campo oculto de ID si existe
        if (esEdicion) {
          $("#AGRICOLAidregistro_MC").remove();
        }

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = AGRICOLAverificarPestañaActiva_MC();
        AGRICOLAiniciarTablaResumen_MC(nombrePestaña);
      },
      error: function (xhr, status, error) {
        // Mostrar mensaje de error
        let errorMsg = "Ha ocurrido un error al guardar el programa";
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        }

        Swal.fire({
          title: "Error",
          text: errorMsg,
          icon: "error",
          confirmButtonText: "Aceptar",
        });
      },
    });
  }
}

function AGRICOLAguardarNuevoPrograma_SUGRA() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#AGRICOLAnombrePrograma_SUGRA").val().trim();
  const fechaInicio = $("#AGRICOLAfechaInicio_SUGRA").val();
  const fechaFin = $("#AGRICOLAfechaFin_SUGRA").val();
  const descripcion = $("#AGRICOLAdescripcion_riego_SUGRA").val() || "";
  const idfase = $("#AGRICOLAidfase_SUGRA").val();
  const idvariedad = $("#AGRICOLAidvariedad_SUGRA").val();
  const idusuario = $("#AGRICOLAidusuario").val();
  const idlote = $("#AGRICOLAselectLote_SUGRA").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#AGRICOLAidregistro_SUGRA").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#AGRICOLAselectLote_SUGRA").css("border", "1px solid red");
    $("#AGRICOLAselectLote_SUGRA").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#AGRICOLAnombrePrograma_SUGRA").css("border", "1px solid red");
    $("#AGRICOLAnombrePrograma_SUGRA").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#AGRICOLAfechaInicio_SUGRA").css("border", "1px solid red");
    $("#AGRICOLAfechaInicio_SUGRA").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#AGRICOLAfechaFin_SUGRA").css("border", "1px solid red");
    $("#AGRICOLAfechaFin_SUGRA").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#AGRICOLAfechaFin_SUGRA").css("border", "1px solid red");
      $("#AGRICOLAfechaFin_SUGRA").after(
        "<span class='text-danger'>La fecha de fin debe ser posterior a la fecha de inicio</span>"
      );
      hayErrores = true;
    }
  }

  // SI TODOS LOS CAMPOS ESTAN CORRECTOS, ENVIAR LOS DATOS AL BACKEND
  if (!hayErrores) {
    // Crear el objeto con los datos
    const datosPrograma = {
      IDUSUARIO: idusuario,
      IDVARIEDAD: idvariedad,
      IDFASE: idfase,
      IDLOTE: idlote,
      NOMBRE: nombrePrograma,
      FECHA_INICIO: fechaInicio,
      FECHA_FIN: fechaFin,
      DESCRIPCION: descripcion,
    };

    // Añadir el ID solo si estamos en modo edición
    if (esEdicion) {
      datosPrograma.ID = idregistro;
    }

    // Determinar URL y método según si es creación o edición
    const url = esEdicion
      ? `/riego/api/materia_agricola_ajs/${idregistro}/`
      : "/riego/api/materia_agricola_ajs/";
    const metodo = esEdicion ? "PUT" : "POST";

    // Enviar datos al servidor
    $.ajax({
      url: url,
      type: metodo,
      contentType: "application/json",
      data: JSON.stringify(datosPrograma),
      success: function (response) {
        // Mostrar mensaje de éxito
        Swal.fire({
          title: "¡Éxito!",
          text: esEdicion
            ? "El programa de fertilización ha sido actualizado correctamente"
            : "El programa de fertilización ha sido creado correctamente",
          icon: "success",
          confirmButtonText: "Aceptar",
        });

        // Cerrar el modal
        $("#AGRICOLAmodalCrearPrograma_SUGRA").modal("hide");

        // Limpiar el formulario
        $("#AGRICOLAformCrearPrograma_SUGRA")[0].reset();

        // Limpiar el selector de lotes
        $("#AGRICOLAselectLote_SUGRA").find("option:not(:first)").remove();

        // Eliminar el campo oculto de ID si existe
        if (esEdicion) {
          $("#AGRICOLAidregistro_SUGRA").remove();

          // Restaurar el texto del botón
          $("#AGRICOLAbtnGuardarProgramaSUGRA").html(
            '<i class="fas fa-save mr-1"></i> Guardar'
          );
        }

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = AGRICOLAverificarPestañaActiva_SUGRA();
        AGRICOLAiniciarTablaResumen_SUGRA(nombrePestaña);
      },
      error: function (xhr, status, error) {
        // Mostrar mensaje de error
        let errorMsg = "Ha ocurrido un error al guardar el programa";
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        }

        Swal.fire({
          title: "Error",
          text: errorMsg,
          icon: "error",
          confirmButtonText: "Aceptar",
        });
      },
    });
  }
}

//============================================================================
// FUNCIONES PARA EDITAR LA FASE
//============================================================================

// Función para editar un registro
function AGRICOLAeditarFertilizacion_SG(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del registro",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const registro = response.data;

      // Abrir el modal de creación (que usaremos también para edición)
      $("#AGRICOLAmodalCrearPrograma").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#AGRICOLAmodalCrearProgramaLabel").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#AGRICOLAbtnGuardarProgramaSG").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#AGRICOLAidregistro").length === 0) {
        $("#AGRICOLAformCrearPrograma").append(
          `<input type="hidden" id="idregistro" value="${idRegistro}">`
        );
      } else {
        $("#AGRICOLAidregistro").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#AGRICOLAnombrePrograma").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = AGRICOLAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#AGRICOLAfechaInicio").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = AGRICOLAformatearFechaParaInput(registro.FECHA_FIN);
        $("#AGRICOLAfechaFin").val(fechaFin);
      }

      // Llenar la descripción
      $("#AGRICOLAdescripcion_riego").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#AGRICOLAidfase").val(registro.IDFASE);
      $("#AGRICOLAidvariedad").val(registro.IDVARIEDAD);
      $("#AGRICOLAidusuario").val(registro.IDUSUARIO);

      // Cargar los lotes y seleccionar el lote correcto
      AGRICOLAcargarLotes(registro.IDVARIEDAD);

      // Después de un breve delay para que se carguen los lotes, seleccionar el lote correcto
      setTimeout(() => {
        if (registro.IDLOTE) {
          $("#selectLote").val(registro.IDLOTE);
        }
      }, 500);
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del registro";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos para edición:", error);
    },
  });
}

function AGRICOLAeditarFertilizacion_AC(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del registro",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const registro = response.data;

      // Abrir el modal de creación (que usaremos también para edición)
      $("#AGRICOLAmodalCrearPrograma_AC").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#AGRICOLAmodalCrearProgramaLabel_AC").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#AGRICOLAbtnGuardarProgramaAC").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#AGRICOLAidregistro_AC").length === 0) {
        $("#AGRICOLAformCrearPrograma_AC").append(
          `<input type="hidden" id="idregistro_AC" value="${idRegistro}">`
        );
      } else {
        $("#AGRICOLAidregistro_AC").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#AGRICOLAnombrePrograma_AC").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = AGRICOLAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#AGRICOLAfechaInicio_AC").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = AGRICOLAformatearFechaParaInput(registro.FECHA_FIN);
        $("#AGRICOLAfechaFin_AC").val(fechaFin);
      }

      // Llenar la descripción
      $("#AGRICOLAdescripcion_riego_AC").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#AGRICOLAidfase_AC").val(registro.IDFASE);
      $("#AGRICOLAidvariedad_AC").val(registro.IDVARIEDAD);
      $("#AGRICOLAidusuario").val(registro.IDUSUARIO);

      // Cargar los lotes y seleccionar el lote correcto
      AGRICOLAcargarLotes(registro.IDVARIEDAD);

      // Después de un breve delay para que se carguen los lotes, seleccionar el lote correcto
      setTimeout(() => {
        if (registro.IDLOTE) {
          $("#AGRICOLAselectLote_AC").val(registro.IDLOTE);
        }
      }, 500);
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del registro";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos para edición:", error);
    },
  });
}

function AGRICOLAmostrarDetallesProductos_AC(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#AGRICOLAprogramaId_AC").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del programa",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const programa = response.data;

      // Actualizar los datos en el modal
      $("#AGRICOLAnombreProgramaDetalle_AC").text(programa.NOMBRE);
      $("#AGRICOLAfechaInicioProgramaDetalle_AC").text(programa.FECHA_INICIO);
      $("#AGRICOLAfechaFinProgramaDetalle_AC").text(programa.FECHA_FIN);
      $("#AGRICOLAdescripcionProgramaDetalle_AC").text(
        programa.DESCRIPCION || "Sin descripción"
      );
      $("#AGRICOLAsectorProgramaDetalle_AC").text(programa.SECTOR || "no definido");
      $("#AGRICOLAloteProgramaDetalle_AC").text(programa.LOTE_NOMBRE || "no definido");

      // Mostrar el modal
      $("#AGRICOLAmodalDetalleProductos_AC").modal("show");

      // Cargar los productos relacionados con este programa
      // Lo hacemos después de mostrar el modal para asegurar que la tabla se renderice correctamente
      AGRICOLAcargarProductosPrograma_AC(idRegistro);
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del programa";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos del programa AC:", error);
    },
  });
}

function AGRICOLAcargarProductosPrograma_AC(idPrograma) {
  var mesesDetalle = [
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

  function AGRICOLAvalorMesCantidad_AC(row, mes) {
    var k = mes + "_cantidad";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAvalorMesPrecio_AC(row, mes) {
    var k = mes + "_precio";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAtotalFilaProducto_AC(row) {
    var suma = 0;
    mesesDetalle.forEach(function (m) {
      var k = m + "_precio";
      if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
        suma += parseFloat(row[k]);
      }
    });
    if (suma > 0) {
      return "S/ " + suma.toFixed(2);
    }
    return "S/ 0.00";
  }

  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#AGRICOLAtablaDetalleProductos_AC")) {
    $("#AGRICOLAtablaDetalleProductos_AC").DataTable().clear().destroy();
  }

  var columnasDetalle = [
    {
      data: null,
      className: "text-center",
      orderable: false,
      render: function (data, type, row, meta) {
        return meta.row + 1;
      },
    },
    { data: "idproducto", className: "text-center" },
    { data: "descripcion", className: "text-left" },
  ];

  mesesDetalle.forEach(function (mes) {
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesCantidad_AC(row, mes);
      },
    });
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesPrecio_AC(row, mes);
      },
    });
  });

  columnasDetalle.push({
    data: null,
    className: "text-center",
    orderable: false,
    render: function (data, type, row) {
      return AGRICOLAtotalFilaProducto_AC(row);
    },
  });

  columnasDetalle.push({
    data: null,
    className: "text-center text-nowrap",
    orderable: false,
    render: function (data, type, row) {
      var id = row.id;
      return (
        '<button type="button" class="btn btn-sm btn-info mr-1" title="Editar" onclick="AGRICOLAeditarProductoAutumnCrisp(' +
        id +
        ')"><i class="fas fa-edit"></i></button>' +
        '<button type="button" class="btn btn-sm btn-danger" title="Eliminar" onclick="AGRICOLAeliminarProductoAutumnCrisp(' +
        id +
        ')"><i class="fas fa-trash"></i></button>'
      );
    },
  });

  // Iniciar la tabla de productos con datos de la API
  $("#AGRICOLAtablaDetalleProductos_AC").DataTable({
    responsive: false,
    scrollX: true,
    autoWidth: false,
    pageLength: 7,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url:
        "/riego/api/suministro_agricola_ajs/?id_producto_agricola=" +
        encodeURIComponent(idPrograma),
      type: "GET",
      dataSrc: function (json) {
        if (!json) {
          return [];
        }
        if (json.error) {
          return [];
        }
        var rows = Array.isArray(json) ? json : json.data || [];
        $("#AGRICOLAtotalProductosProgramaDetalle_plantines_AC").text(rows.length);
        var costoTotal = 0;
        rows.forEach(function (item) {
          var sumaMeses = 0;
          mesesDetalle.forEach(function (m) {
            var pk = m + "_precio";
            if (
              item[pk] != null &&
              item[pk] !== "" &&
              !isNaN(parseFloat(item[pk]))
            ) {
              sumaMeses += parseFloat(item[pk]);
            }
          });
          costoTotal += sumaMeses;
        });
        $("#AGRICOLAcostoTotalProgramaDetalle_AC").text(
          "$ " + costoTotal.toFixed(2)
        );
        return rows;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        $("#AGRICOLAtablaDetalleProductos_AC tbody").html(
          '<tr><td colspan="29" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
        );
      },
    },
    columns: columnasDetalle,
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      $(row).attr("data-id", data.id);
    },
  });

}

//============================================================================
// FUNCIONES PARA EDITAR Y ELIMINAR PRODUCTOS - SWEET GLOBE
//============================================================================

// Función para editar una fila de SUMINISTRO_AGRICOLA (Sweet Globe)
function AGRICOLAeditarProductoAutumnCrisp(idSuministro) {
  $.ajax({
    url: "/riego/api/suministro_agricola_ajs/" + encodeURIComponent(idSuministro) + "/",
    type: "GET",
    success: function (response) {
      if (!response || !response.data) {
        Swal.fire("Error", "No se pudo obtener la información del suministro", "error");
        return;
      }

      var p = response.data;
      var mesesEd = [
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

      $("#AGRICOLAproductoId_AC").val(p.id);
      if (p.idproducto_agricola != null && p.idproducto_agricola !== "") {
        $("#AGRICOLAprogramaId_AC").val(p.idproducto_agricola);
      }

      $("#AGRICOLA_idproducto_sum_AC").val(p.idproducto != null ? String(p.idproducto) : "");
      $("#AGRICOLA_descripcion_sum_AC").val(p.descripcion || "");
      var pu = parseFloat(p.precio_unitario);
      if (isNaN(pu)) {
        pu = 0;
      }
      $("#AGRICOLA_precio_unitario_sum_AC").val(pu.toFixed(2)).prop("readonly", false);

      if ($("#AGRICOLA_id_area_sum_AC").length) {
        $("#AGRICOLA_id_area_sum_AC").val(
          p.id_area != null && p.id_area !== "" ? p.id_area : "11"
        );
      }
      if ($("#AGRICOLA_id_tipo_suministro_sum_AC").length) {
        $("#AGRICOLA_id_tipo_suministro_sum_AC").val(
          p.id_tipo_suministro != null && p.id_tipo_suministro !== ""
            ? p.id_tipo_suministro
            : "1"
        );
      }

      mesesEd.forEach(function (mes) {
        var cantKey = mes + "_cantidad";
        var cant = parseFloat(p[cantKey]);
        if (!isNaN(cant) && cant > 0) {
          $("#AGRICOLA_sum_AC" + mes + "_switch").prop("checked", true);
          $("#AGRICOLA_sum_AC" + mes + "_cantidad").prop("disabled", false).val(cant);
        } else {
          $("#AGRICOLA_sum_AC" + mes + "_switch").prop("checked", false);
          $("#AGRICOLA_sum_AC" + mes + "_cantidad").prop("disabled", true).val("");
        }
      });

      $("#AGRICOLA_cantidad_masiva_sum_AC").val("");
      $("#AGRICOLAmodalProductoLabel_AC").html(
        '<i class="fas fa-edit mr-2"></i> Editar suministro'
      );
      $("#AGRICOLAmodalProducto_AC").modal("show");
      AGRICOLAinitEventosFormularioProducto_SG();
      AGRICOLA_calcularTotalesSuministroSG();
    },
    error: function (xhr, status, error) {
      var errorMsg = "Ha ocurrido un error al obtener los datos del suministro";
      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }
      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      console.error("Error al obtener datos del suministro:", error);
    },
  });
}

// Función para eliminar un producto de Sweet Globe
function AGRICOLAeliminarProductoAutumnCrisp(idProducto) {
  // Mostrar confirmación mediante SweetAlert2
  Swal.fire({
    title: "¿Estás seguro?",
    text: "¡No podrás revertir esta acción!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Mostrar indicador de carga
      Swal.fire({
        title: "Eliminando...",
        text: "Por favor espere mientras se elimina el producto",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Enviar la petición AJAX para eliminar el suministro
      $.ajax({
        url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
        type: "DELETE",
        success: function (response) {
          // Cerrar indicador de carga
          Swal.close();

          // Mostrar mensaje de éxito
          Swal.fire({
            title: "¡Eliminado!",
            text: "El producto ha sido eliminado correctamente",
            icon: "success",
            confirmButtonText: "Aceptar",
          });

          // Obtener el ID del programa actual para recargar la tabla
          const programaId = $("#AGRICOLAprogramaId_AC").val();

          // Recargar la tabla de productos
          if (programaId) {
            AGRICOLAcargarProductosPrograma_AC(programaId);
          }
        },
        error: function (xhr, status, error) {
          // Cerrar indicador de carga
          Swal.close();

          // Mostrar mensaje de error
          let errorMsg = "Ha ocurrido un error al eliminar el producto";

          if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          }

          Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error",
            confirmButtonText: "Aceptar",
          });

          console.error("Error al eliminar el producto:", error);
        },
      });
    }
  });
}

// Función auxiliar para formatear fechas (de DD/MM/YYYY a YYYY-MM-DD)
function AGRICOLAformatearFechaParaInput(fechaStr) {
  // Verificar formato DD/MM/YYYY
  const formatoDD_MM_YYYY = /^(\d{2})\/(\d{2})\/(\d{4})$/;
  if (formatoDD_MM_YYYY.test(fechaStr)) {
    const partes = fechaStr.match(formatoDD_MM_YYYY);
    return `${partes[3]}-${partes[2]}-${partes[1]}`;
  }

  // Intentar con formato ISO (por si viene en otro formato del backend)
  try {
    const fecha = new Date(fechaStr);
    return fecha.toISOString().split("T")[0];
  } catch (e) {
    console.error("Error al formatear fecha:", e);
    return fechaStr; // Devolver la original si hay error
  }
}

//============================================================================
// FUNCIONES PARA ELIMINAR LA FASE
//============================================================================

// Función para eliminar un registro con confirmación
function AGRICOLAeliminarFertilizacion(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/suministro_agricola_ajs/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDPRODUCTO_AGRICOLA, 10) ===
            parseInt(idRegistro, 10)
          );
        });

        if (productosAsociados.length > 0) {
          // Si hay productos asociados, mostrar mensaje y no permitir eliminar
          Swal.fire({
            title: "No se puede eliminar",
            text: `No es posible eliminar esta fase porque tiene ${productosAsociados.length} producto(s) asociado(s). Elimine primero los productos.`,
            icon: "warning",
            confirmButtonText: "Entendido",
          });
          return;
        } else {
          // No hay productos, proceder con la eliminación
          confirmarEliminacion();
        }
      } else {
        // Si no hay respuesta válida, asumir que no hay productos y proceder
        confirmarEliminacion();
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al verificar productos asociados:", error);
      // En caso de error, mostrar mensaje y no permitir eliminar por precaución
      Swal.fire({
        title: "Error",
        text: "No se pudo verificar si hay productos asociados. Por favor, inténtelo de nuevo.",
        icon: "error",
        confirmButtonText: "Aceptar",
      });
    },
  });

  // Función para mostrar confirmación y eliminar
  function confirmarEliminacion() {
    // Mostrar confirmación mediante SweetAlert2
    Swal.fire({
      title: "¿Estás seguro?",
      text: "¡No podrás revertir esta acción!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        // El usuario confirmó la eliminación
        $.ajax({
          url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
          type: "DELETE",
          success: function (response) {
            // Mostrar mensaje de éxito
            Swal.fire(
              "¡Eliminado!",
              "El registro ha sido eliminado correctamente.",
              "success"
            );

            // Recargar la tabla correspondiente según la pestaña activa
            const nombrePestaña = AGRICOLAverificarPestañaActiva_SG();
            AGRICOLAAGRICOLAiniciarTablaResumen_SG(nombrePestaña);
          },
          error: function (xhr, status, error) {
            // Mostrar mensaje de error
            let mensajeError = "Ha ocurrido un error al eliminar el registro.";
            if (xhr.responseJSON && xhr.responseJSON.message) {
              mensajeError = xhr.responseJSON.message;
            }

            Swal.fire("Error", mensajeError, "error");

            console.error("Error al eliminar:", error);
          },
        });
      }
    });
  }
}

function AGRICOLAeliminarFertilizacion_AC(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/suministro_agricola_ajs/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDPRODUCTO_AGRICOLA, 10) ===
            parseInt(idRegistro, 10)
          );
        });

        if (productosAsociados.length > 0) {
          // Si hay productos asociados, mostrar mensaje y no permitir eliminar
          Swal.fire({
            title: "No se puede eliminar",
            text: `No es posible eliminar esta fase porque tiene ${productosAsociados.length} producto(s) asociado(s). Elimine primero los productos.`,
            icon: "warning",
            confirmButtonText: "Entendido",
          });
          return;
        } else {
          // No hay productos, proceder con la eliminación
          confirmarEliminacion();
        }
      } else {
        // Si no hay respuesta válida, asumir que no hay productos y proceder
        confirmarEliminacion();
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al verificar productos asociados:", error);
      // En caso de error, mostrar mensaje y no permitir eliminar por precaución
      Swal.fire({
        title: "Error",
        text: "No se pudo verificar si hay productos asociados. Por favor, inténtelo de nuevo.",
        icon: "error",
        confirmButtonText: "Aceptar",
      });
    },
  });

  // Función para mostrar confirmación y eliminar
  function confirmarEliminacion() {
    // Mostrar confirmación
    Swal.fire({
      title: "¿Está seguro?",
      text: "Esta acción eliminará el programa y todos sus productos asociados. Esta acción no se puede deshacer.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        // Realizar la eliminación mediante AJAX
        $.ajax({
          url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
          type: "DELETE",
          beforeSend: function () {
            // Mostrar indicador de carga
            Swal.fire({
              title: "Eliminando...",
              text: "Por favor espere",
              allowOutsideClick: false,
              didOpen: () => {
                Swal.showLoading();
              },
            });
          },
          success: function (response) {
            // Mostrar mensaje de éxito
            Swal.fire({
              title: "Eliminado",
              text: "El programa ha sido eliminado correctamente",
              icon: "success",
              confirmButtonText: "Aceptar",
            }).then(() => {
              // Refrescar la tabla de programas según la pestaña activa
              AGRICOLAverificarPestañaActiva_AC();
            });
          },
          error: function (xhr, status, error) {
            // Mostrar mensaje de error
            let errorMsg = "Ha ocurrido un error al eliminar el programa";

            if (xhr.responseJSON && xhr.responseJSON.message) {
              errorMsg = xhr.responseJSON.message;
            }

            Swal.fire({
              title: "Error",
              text: errorMsg,
              icon: "error",
              confirmButtonText: "Aceptar",
            });

            console.error(
              "Error al eliminar programa de fertilización:",
              error
            );
          },
        });
      }
    });
  }
}

function AGRICOLAguardarProductoAutumnCrisp() {
  var programaId = $("#AGRICOLAprogramaId_AC").val();
  var suministroPk = ($("#AGRICOLAproductoId_AC").val() || "").trim();
  var esEdicion = suministroPk !== "";
  var idproducto = ($("#AGRICOLA_idproducto_sum_AC").val() || "").trim();
  var descripcion = ($("#AGRICOLA_descripcion_sum_AC").val() || "").trim();
  var precioUnitario = parseFloat($("#AGRICOLA_precio_unitario_sum_AC").val());
  var idArea = parseInt($("#AGRICOLA_id_area_sum_AC").val(), 10);
  var idTipo = parseInt($("#AGRICOLA_id_tipo_suministro_sum_AC").val(), 10);

  if (!programaId) {
    Swal.fire("Error", "No se ha seleccionado el programa (cabecera).", "error");
    return false;
  }

  var formProducto = $("#AGRICOLAformProducto_AC")[0];
  if (formProducto && !formProducto.checkValidity()) {
    formProducto.reportValidity();
    return false;
  }

  if (!idproducto || !descripcion) {
    Swal.fire("Error", "Seleccione un producto de la lista (descripción e ID).", "error");
    return false;
  }

  if (isNaN(precioUnitario) || precioUnitario <= 0) {
    Swal.fire("Error", "Indique un precio unitario válido mayor a 0.", "error");
    return false;
  }

  var mesesPayload = [
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

  var datosProducto = {
    idproducto: idproducto,
    descripcion: descripcion,
    precio_unitario: precioUnitario,
    id_area: isNaN(idArea) ? 11 : idArea,
    id_tipo_suministro: isNaN(idTipo) ? 1 : idTipo,
  };

  mesesPayload.forEach(function (mes) {
    var activo = $("#AGRICOLA_sum_AC" + mes + "_switch").is(":checked");
    var c = activo ? parseFloat($("#AGRICOLA_sum_AC" + mes + "_cantidad").val()) || 0 : 0;
    datosProducto[mes + "_cantidad"] = c;
  });

  if (!esEdicion) {
    datosProducto.IDPRODUCTO_AGRICOLA = parseInt(programaId, 10);
    if (isNaN(datosProducto.IDPRODUCTO_AGRICOLA)) {
      Swal.fire("Error", "ID de programa agrícola inválido.", "error");
      return false;
    }
  }

  var url = "/riego/api/suministro_agricola_ajs/";
  var metodo = "POST";
  if (esEdicion) {
    url = "/riego/api/suministro_agricola_ajs/" + encodeURIComponent(suministroPk) + "/";
    metodo = "PUT";
  }

  Swal.fire({
    title: esEdicion ? "Actualizando..." : "Guardando...",
    text: esEdicion
      ? "Por favor espere mientras se actualiza el suministro"
      : "Por favor espere mientras se guarda el suministro",
    allowOutsideClick: false,
    didOpen: function () {
      Swal.showLoading();
    },
  });

  $.ajax({
    url: url,
    type: metodo,
    contentType: "application/json",
    data: JSON.stringify(datosProducto),
    success: function () {
      Swal.close();
      Swal.fire({
        title: "¡Éxito!",
        text: esEdicion
          ? "El suministro ha sido actualizado correctamente"
          : "El suministro ha sido guardado correctamente",
        icon: "success",
        confirmButtonText: "Aceptar",
      });
      $("#AGRICOLAmodalProducto_AC").modal("hide");
      AGRICOLAcargarProductosPrograma_AC(programaId);
      return true;
    },
    error: function (xhr, status, error) {
      console.error(
        "Error al " + (esEdicion ? "actualizar" : "guardar") + " suministro Sweet Globe:",
        error
      );
      Swal.close();
      var errorMsg =
        "Ha ocurrido un error al " + (esEdicion ? "actualizar" : "guardar") + " el suministro";
      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }
      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      return false;
    },
  });
}

function AGRICOLAeditarProductoAutumnCrisp(idProducto) {
  // Realizar una petición AJAX para obtener los datos del producto
  $.ajax({
    url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
    type: "GET",
    success: function (response) {
      if (response && response.data) {
        // Obtener los datos del producto
        const producto = response.data;

        // Llenar el formulario con los datos
        $("#AGRICOLAproductoId_AC").val(idProducto);
        $("#AGRICOLAsubGrupoProducto_AC").val(producto.SUBGRUPO);
        $("#AGRICOLAnombreProducto_AC").val(producto.PRODUCTO);
        $("#AGRICOLAmateriaActivaProducto_AC").val(producto.MATERIA_ACTIVA);
        $("#AGRICOLAnecesidadProducto_AC").val(producto.NECESIDADXHA);
        $("#AGRICOLAunidadNecesidadProducto_AC").val(producto.UND);
        $("#AGRICOLAprecioProducto_AC").val(producto.PRECIO_LTKG);
        $("#AGRICOLAprecioHaProducto_AC").val(producto.PRECIO_HA);
        $("#AGRICOLAobservacionesProducto_AC").val(producto.OBSERVACIONES);

        // Agregar valores a los campos ocultos
        $("#AGRICOLAidProductoAC").val(producto.IDPRODUCTO || "");
        $("#AGRICOLAidSubgrupoAC").val(producto.IDSUBGRUPO || "");

        // Cambiar el título del modal
        $("#AGRICOLAmodalProductoLabel_AC").text("Editar Producto");

        // Mostrar el modal
        $("#AGRICOLAmodalProducto_AC").modal("show");
      } else {
        Swal.fire(
          "Error",
          "No se pudieron cargar los datos del producto",
          "error"
        );
      }
    },
    error: function (xhr, status, error) {
      Swal.fire(
        "Error",
        "Ocurrió un error al intentar cargar los datos: " + error,
        "error"
      );
    },
  });
}

function AGRICOLAeliminarProductoAutumnCrisp(idProducto) {
  // Mostrar confirmación
  Swal.fire({
    title: "¿Está seguro?",
    text: "Esta acción eliminará el producto seleccionado. Esta acción no se puede deshacer.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Obtener el ID del programa actual
      const programaId = $("#AGRICOLAprogramaId_AC").val();

      // Realizar la eliminación mediante AJAX
      $.ajax({
        url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
        type: "DELETE",
        beforeSend: function () {
          // Mostrar indicador de carga
          Swal.fire({
            title: "Eliminando...",
            text: "Por favor espere",
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading();
            },
          });
        },
        success: function (response) {
          // Mostrar mensaje de éxito
          Swal.fire({
            title: "Eliminado",
            text: "El producto ha sido eliminado correctamente",
            icon: "success",
            confirmButtonText: "Aceptar",
          }).then(() => {
            // Refrescar la tabla de productos
            AGRICOLAcargarProductosPrograma_AC(programaId);
          });
        },
        error: function (xhr, status, error) {
          // Mostrar mensaje de error
          let errorMsg = "Ha ocurrido un error al eliminar el producto";

          if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          }

          Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error",
            confirmButtonText: "Aceptar",
          });

          console.error("Error al eliminar producto:", error);
        },
      });
    }
  });
}

//============================================================================
// FUNCIÓN PARA EDITAR FERTILIZACIÓN - MOSCATEL
//============================================================================

function AGRICOLAeditarFertilizacion_MC(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del registro",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const registro = response.data;

      // Abrir el modal de creación (que usaremos también para edición)
      $("#AGRICOLAmodalCrearPrograma_MC").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#AGRICOLAmodalCrearProgramaLabel_MC").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#AGRICOLAbtnGuardarProgramaMC").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#AGRICOLAidregistro_MC").length === 0) {
        $("#AGRICOLAformCrearPrograma_MC").append(
          `<input type="hidden" id="idregistro_MC" value="${idRegistro}">`
        );
      } else {
        $("#AGRICOLAidregistro_MC").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#AGRICOLAnombrePrograma_MC").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = AGRICOLAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#AGRICOLAfechaInicio_MC").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = AGRICOLAformatearFechaParaInput(registro.FECHA_FIN);
        $("#AGRICOLAfechaFin_MC").val(fechaFin);
      }

      // Llenar la descripción
      $("#AGRICOLAdescripcion_riego_MC").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#AGRICOLAidfase_MC").val(registro.IDFASE);
      $("#AGRICOLAidvariedad_MC").val(registro.IDVARIEDAD);
      $("#AGRICOLAidusuario").val(registro.IDUSUARIO);

      // Cargar lotes para Moscatel (idvariedad = 3) y seleccionar el lote correspondiente
      if (registro.IDLOTE) {
        AGRICOLAcargarLotes(3).then(() => {
          $("#AGRICOLAselectLote_MC").val(registro.IDLOTE);
        });
      } else {
        AGRICOLAcargarLotes(3);
      }
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del registro";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos para edición MC:", error);
    },
  });
}

//============================================================================
// FUNCIONES PARA EDITAR FERTILIZACIÓN - SUGRA
//============================================================================

function AGRICOLAeditarFertilizacion_SUGRA(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del registro",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const registro = response.data;

      // Abrir el modal de creación (que usaremos también para edición)
      $("#AGRICOLAmodalCrearPrograma_SUGRA").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#AGRICOLAmodalCrearProgramaLabel_SUGRA").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#AGRICOLAbtnGuardarProgramaSUGRA").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#AGRICOLAidregistro_SUGRA").length === 0) {
        $("#AGRICOLAformCrearPrograma_SUGRA").append(
          `<input type="hidden" id="idregistro_SUGRA" value="${idRegistro}">`
        );
      } else {
        $("#AGRICOLAidregistro_SUGRA").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#AGRICOLAnombrePrograma_SUGRA").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = AGRICOLAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#AGRICOLAfechaInicio_SUGRA").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = AGRICOLAformatearFechaParaInput(registro.FECHA_FIN);
        $("#AGRICOLAfechaFin_SUGRA").val(fechaFin);
      }

      // Llenar la descripción
      $("#AGRICOLAdescripcion_riego_SUGRA").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#AGRICOLAidfase_SUGRA").val(registro.IDFASE);
      $("#AGRICOLAidvariedad_SUGRA").val(registro.IDVARIEDAD);
      $("#AGRICOLAidusuario").val(registro.IDUSUARIO);

      // Cargar lotes para Sugra (idvariedad = 4) y seleccionar el lote correspondiente
      if (registro.IDLOTE) {
        AGRICOLAcargarLotes(4).then(() => {
          $("#AGRICOLAselectLote_SUGRA").val(registro.IDLOTE);
        });
      } else {
        AGRICOLAcargarLotes(4);
      }
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del registro";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos para edición SUGRA:", error);
    },
  });
}

//============================================================================
// FUNCIONES PARA ELIMINAR FERTILIZACIÓN - MOSCATEL
//============================================================================

function AGRICOLAeliminarFertilizacion_MC(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/suministro_agricola_ajs/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDPRODUCTO_AGRICOLA, 10) ===
            parseInt(idRegistro, 10)
          );
        });

        if (productosAsociados.length > 0) {
          // Si hay productos asociados, mostrar mensaje y no permitir eliminar
          Swal.fire({
            title: "No se puede eliminar",
            text: `No es posible eliminar esta fase porque tiene ${productosAsociados.length} producto(s) asociado(s). Elimine primero los productos.`,
            icon: "warning",
            confirmButtonText: "Entendido",
          });
          return;
        } else {
          // No hay productos, proceder con la eliminación
          confirmarEliminacion();
        }
      } else {
        // Si no hay respuesta válida, asumir que no hay productos y proceder
        confirmarEliminacion();
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al verificar productos asociados:", error);
      // En caso de error, mostrar mensaje y no permitir eliminar por precaución
      Swal.fire({
        title: "Error",
        text: "No se pudo verificar si hay productos asociados. Por favor, inténtelo de nuevo.",
        icon: "error",
        confirmButtonText: "Aceptar",
      });
    },
  });

  // Función para mostrar confirmación y eliminar
  function confirmarEliminacion() {
    // Mostrar confirmación mediante SweetAlert2
    Swal.fire({
      title: "¿Estás seguro?",
      text: "¡No podrás revertir esta acción!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        // El usuario confirmó la eliminación
        $.ajax({
          url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
          type: "DELETE",
          success: function (response) {
            // Mostrar mensaje de éxito
            Swal.fire(
              "¡Eliminado!",
              "El registro ha sido eliminado correctamente.",
              "success"
            );

            // Recargar la tabla correspondiente según la pestaña activa
            const nombrePestaña = AGRICOLAverificarPestañaActiva_MC();
            AGRICOLAiniciarTablaResumen_MC(nombrePestaña);
          },
          error: function (xhr, status, error) {
            // Mostrar mensaje de error
            let mensajeError = "Ha ocurrido un error al eliminar el registro.";
            if (xhr.responseJSON && xhr.responseJSON.message) {
              mensajeError = xhr.responseJSON.message;
            }

            Swal.fire("Error", mensajeError, "error");

            console.error("Error al eliminar:", error);
          },
        });
      }
    });
  }
}

//============================================================================
// FUNCIONES PARA ELIMINAR FERTILIZACIÓN - SUGRA
//============================================================================

function AGRICOLAeliminarFertilizacion_SUGRA(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/suministro_agricola_ajs/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDPRODUCTO_AGRICOLA, 10) ===
            parseInt(idRegistro, 10)
          );
        });

        if (productosAsociados.length > 0) {
          // Si hay productos asociados, mostrar mensaje y no permitir eliminar
          Swal.fire({
            title: "No se puede eliminar",
            text: `No es posible eliminar esta fase porque tiene ${productosAsociados.length} producto(s) asociado(s). Elimine primero los productos.`,
            icon: "warning",
            confirmButtonText: "Entendido",
          });
          return;
        } else {
          // No hay productos, proceder con la eliminación
          confirmarEliminacion();
        }
      } else {
        // Si no hay respuesta válida, asumir que no hay productos y proceder
        confirmarEliminacion();
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al verificar productos asociados:", error);
      // En caso de error, mostrar mensaje y no permitir eliminar por precaución
      Swal.fire({
        title: "Error",
        text: "No se pudo verificar si hay productos asociados. Por favor, inténtelo de nuevo.",
        icon: "error",
        confirmButtonText: "Aceptar",
      });
    },
  });

  // Función para mostrar confirmación y eliminar
  function confirmarEliminacion() {
    // Mostrar confirmación mediante SweetAlert2
    Swal.fire({
      title: "¿Estás seguro?",
      text: "¡No podrás revertir esta acción!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        // El usuario confirmó la eliminación
        $.ajax({
          url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
          type: "DELETE",
          success: function (response) {
            // Mostrar mensaje de éxito
            Swal.fire(
              "¡Eliminado!",
              "El registro ha sido eliminado correctamente.",
              "success"
            );

            // Recargar la tabla correspondiente según la pestaña activa
            const nombrePestaña = AGRICOLAverificarPestañaActiva_SUGRA();
            AGRICOLAiniciarTablaResumen_SUGRA(nombrePestaña);
          },
          error: function (xhr, status, error) {
            // Mostrar mensaje de error
            let mensajeError = "Ha ocurrido un error al eliminar el registro.";
            if (xhr.responseJSON && xhr.responseJSON.message) {
              mensajeError = xhr.responseJSON.message;
            }

            Swal.fire("Error", mensajeError, "error");

            console.error("Error al eliminar:", error);
          },
        });
      }
    });
  }
}

//============================================================================
// FUNCIONES PARA MOSTRAR LOS DETALLES DE LOS PRODUCTOS PARA SWEET GLOBE
//============================================================================

// Función para mostrar el modal de detalle de productos para SWEET GLOBE
function AGRICOLAmostrarDetallesProductos(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#AGRICOLAprogramaId").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del programa",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const programa = response.data;
      console.log("estos son los datos del programa: ", programa);

      // Actualizar los datos en el modal
      $("#AGRICOLAnombreProgramaDetalle").text(programa.NOMBRE);
      $("#AGRICOLAfechaInicioProgramaDetalle").text(programa.FECHA_INICIO);
      $("#AGRICOLAfechaFinProgramaDetalle").text(programa.FECHA_FIN);
      $("#AGRICOLAdescripcionProgramaDetalle").text(
        programa.DESCRIPCION || "Sin descripción"
      );
      $("#AGRICOLAsectorProgramaDetalle").text(programa.SECTOR || "no definido");
      $("#AGRICOLAloteProgramaDetalle").text(programa.LOTE_NOMBRE || "no definido");

      // Mostrar el modal
      $("#AGRICOLAmodalDetalleProductos").modal("show");

      // Cargar los productos relacionados con este programa
      // Lo hacemos después de mostrar el modal para asegurar que la tabla se renderice correctamente
      AGRICOLAcargarProductosPrograma(idRegistro);
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del programa";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos del programa:", error);
    },
  });
}

// Función para cargar los productos relacionados con el programa para SWEET GLOBE
function AGRICOLAcargarProductosPrograma(idPrograma) {
  var mesesDetalle = [
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

  function AGRICOLAvalorMesCantidad(row, mes) {
    var k = mes + "_cantidad";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAvalorMesPrecio(row, mes) {
    var k = mes + "_precio";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAtotalFilaProducto(row) {
    var suma = 0;
    mesesDetalle.forEach(function (m) {
      var k = m + "_precio";
      if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
        suma += parseFloat(row[k]);
      }
    });
    if (suma > 0) {
      return "S/ " + suma.toFixed(2);
    }
    return "S/ 0.00";
  }

  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#AGRICOLAtablaDetalleProductos")) {
    $("#AGRICOLAtablaDetalleProductos").DataTable().clear().destroy();
  }

  var columnasDetalle = [
    {
      data: null,
      className: "text-center",
      orderable: false,
      render: function (data, type, row, meta) {
        return meta.row + 1;
      },
    },
    { data: "idproducto", className: "text-center" },
    { data: "descripcion", className: "text-left" },
  ];

  mesesDetalle.forEach(function (mes) {
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesCantidad(row, mes);
      },
    });
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesPrecio(row, mes);
      },
    });
  });

  columnasDetalle.push({
    data: null,
    className: "text-center",
    orderable: false,
    render: function (data, type, row) {
      return AGRICOLAtotalFilaProducto(row);
    },
  });

  columnasDetalle.push({
    data: null,
    className: "text-center text-nowrap",
    orderable: false,
    render: function (data, type, row) {
      var id = row.id;
      return (
        '<button type="button" class="btn btn-sm btn-info mr-1" title="Editar" onclick="AGRICOLAeditarProductoSweetGlobe(' +
        id +
        ')"><i class="fas fa-edit"></i></button>' +
        '<button type="button" class="btn btn-sm btn-danger" title="Eliminar" onclick="AGRICOLAeliminarProductoSweetGlobe(' +
        id +
        ')"><i class="fas fa-trash"></i></button>'
      );
    },
  });

  // Iniciar la tabla de productos con datos de la API
  $("#AGRICOLAtablaDetalleProductos").DataTable({
    responsive: false,
    scrollX: true,
    autoWidth: false,
    pageLength: 7,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url:
        "/riego/api/suministro_agricola_ajs/?id_producto_agricola=" +
        encodeURIComponent(idPrograma),
      type: "GET",
      dataSrc: function (json) {
        if (!json) {
          return [];
        }
        if (json.error) {
          return [];
        }
        var rows = Array.isArray(json) ? json : json.data || [];
        $("#AGRICOLAtotalProductosProgramaDetalle_plantines").text(rows.length);
        var costoTotal = 0;
        rows.forEach(function (item) {
          var sumaMeses = 0;
          mesesDetalle.forEach(function (m) {
            var pk = m + "_precio";
            if (
              item[pk] != null &&
              item[pk] !== "" &&
              !isNaN(parseFloat(item[pk]))
            ) {
              sumaMeses += parseFloat(item[pk]);
            }
          });
          costoTotal += sumaMeses;
        });
        $("#AGRICOLAcostoTotalProgramaDetalle").text(
          "$ " + costoTotal.toFixed(2)
        );
        return rows;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        $("#AGRICOLAtablaDetalleProductos tbody").html(
          '<tr><td colspan="29" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
        );
      },
    },
    columns: columnasDetalle,
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      $(row).attr("data-id", data.id);
    },
  });
}

function AGRICOLA_calcularTotalesSuministroSG() {
  var pu = parseFloat($("#AGRICOLA_precio_unitario_sum").val()) || 0;
  var cantTotal = 0;
  var precioTotal = 0;
  $(".AGRICOLA_sum_cantidad_mes").each(function () {
    var idEl = this.id;
    var mes = idEl.replace(/^AGRICOLA_sum_/, "").replace(/_cantidad$/, "");
    if ($("#AGRICOLA_sum_" + mes + "_switch").is(":checked")) {
      var c = parseFloat($(this).val()) || 0;
      cantTotal += c;
      precioTotal += c * pu;
    }
  });
  $("#AGRICOLA_cantidad_total_sum").text(cantTotal.toFixed(2));
  $("#AGRICOLA_precio_total_sum").text("S/ " + precioTotal.toFixed(2));
}

function AGRICOLAcalcularPrecioHa() {
  AGRICOLA_calcularTotalesSuministroSG();
}

function AGRICOLA_destruirAutocompleteSuministroSiExiste() {
  var $d = $("#AGRICOLA_descripcion_sum");
  if ($d.length && $d.data("ui-autocomplete")) {
    $d.autocomplete("destroy");
  }
}

function AGRICOLA_inicializarAutocompleteSuministroSG() {
  AGRICOLA_destruirAutocompleteSuministroSiExiste();
  $("#AGRICOLA_descripcion_sum").autocomplete({
    minLength: 2,
    source: function (request, response) {
      $.ajax({
        url: "/riego/api_productos_agricolas_uva1/",
        dataType: "json",
        data: { q: request.term },
        success: function (data) {
          if (!data || data.error) {
            response([]);
            return;
          }
          var arr = Array.isArray(data) ? data : [];
          var results = $.map(arr, function (item) {
            var up = parseFloat(item.ultimo_precio) || 0;
            return {
              label: item.value,
              value: item.value,
              id: item.id,
              ultimo_precio: up,
              sin_precio_historico: up === 0,
            };
          });
          response(results);
        },
        error: function () {
          response([]);
        },
      });
    },
    select: function (event, ui) {
      $("#AGRICOLA_idproducto_sum").val(ui.item.id);
      if (ui.item.sin_precio_historico) {
        $("#AGRICOLA_precio_unitario_sum")
          .val("")
          .prop("readonly", false)
          .attr("placeholder", "Ingrese precio unitario");
        Swal.fire({
          title: "Sin precio histórico",
          text: "Ingrese manualmente el precio unitario.",
          icon: "info",
        });
      } else {
        $("#AGRICOLA_precio_unitario_sum")
          .val(ui.item.ultimo_precio.toFixed(2))
          .prop("readonly", true)
          .attr("placeholder", "");
      }
      AGRICOLA_calcularTotalesSuministroSG();
    },
  });
}

function AGRICOLA_inicializarAutocompleteSuministro_AC() {
  AGRICOLA_destruirAutocompleteSuministroSiExiste();
  $("#AGRICOLA_descripcion_sum_AC").autocomplete({
    minLength: 2,
    source: function (request, response) {
      $.ajax({
        url: "/riego/api_productos_agricolas_uva1/",
        dataType: "json",
        data: { q: request.term },
        success: function (data) {
          if (!data || data.error) {
            response([]);
            return;
          }
          var arr = Array.isArray(data) ? data : [];
          var results = $.map(arr, function (item) {
            var up = parseFloat(item.ultimo_precio) || 0;
            return {
              label: item.value,
              value: item.value,
              id: item.id,
              ultimo_precio: up,
              sin_precio_historico: up === 0,
            };
          });
          response(results);
        },
        error: function () {
          response([]);
        },
      });
    },
    select: function (event, ui) {
      $("#AGRICOLA_idproducto_sum_AC").val(ui.item.id);
      if (ui.item.sin_precio_historico) {
        $("#AGRICOLA_precio_unitario_sum_AC")
          .val("")
          .prop("readonly", false)
          .attr("placeholder", "Ingrese precio unitario");
        Swal.fire({
          title: "Sin precio histórico",
          text: "Ingrese manualmente el precio unitario.",
          icon: "info",
        });
      } else {
        $("#AGRICOLA_precio_unitario_sum_AC")
          .val(ui.item.ultimo_precio.toFixed(2))
          .prop("readonly", true)
          .attr("placeholder", "");
      }
      AGRICOLA_calcularTotalesSuministroSG();
    },
  });
}




//============================================================================
// EVENTOS
//============================================================================
// Modificar la función para abrir el modal de nuevo producto
function AGRICOLAabrirModalNuevoProducto_SG(idPrograma) {
  AGRICOLAresetearFormularioProducto();
  $("#AGRICOLAprogramaId").val(idPrograma);
  $("#AGRICOLAmodalProducto").modal("show");
  AGRICOLAinitEventosFormularioProducto_SG();
}

// Agregamos los eventos necesarios
$(document).ready(function () {
  // Verificar al abrir el modal SWEET GLOBE
  $("#AGRICOLAmodalSweetGlobe").on("shown.bs.modal", function () {
    AGRICOLAverificarPestañaActiva_SG();
  });

  // Verificar al abrir el modal AUTUMN CRISP
  $("#AGRICOLAmodalAutumnCrisp").on("shown.bs.modal", function () {
    AGRICOLAverificarPestañaActiva_AC();
  });

  $("#AGRICOLAmodalMoscatel").on("shown.bs.modal", function () {
    AGRICOLAverificarPestañaActiva_MC();
  });

  $("#AGRICOLAmodalSugra").on("shown.bs.modal", function () {
    AGRICOLAverificarPestañaActiva_SUGRA();
  });

  // Evento para el botón añadir producto
  $("#AGRICOLAbtnAñadirProducto").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#AGRICOLAprogramaId").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    AGRICOLAabrirModalNuevoProducto_SG(programaId);
  });

  // El evento para guardar producto ahora se maneja en initEventosFormularioProducto_SG

  $("#AGRICOLAmodalProducto").on("hidden.bs.modal", function () {
    AGRICOLA_destruirAutocompleteSuministroSiExiste();
  });

  //============================================================

  // Verificar al cambiar de pestaña SWEET GLOBE
  $('#AGRICOLAsweetGlobeTabs a[data-toggle="tab"]').on("shown.bs.tab", function () {
    AGRICOLAverificarPestañaActiva_SG();
  });

  // Verificar al cambiar de pestaña AUTUMN CRISP
  $("#AGRICOLAautumnCrispTabs a[data-toggle='tab']").on("shown.bs.tab", function () {
    AGRICOLAverificarPestañaActiva_AC();
  });

  // Verificar al cambiar de pestaña MOSCATEL
  $("#AGRICOLAmoscatelTabs a[data-toggle='tab']").on("shown.bs.tab", function () {
    AGRICOLAverificarPestañaActiva_MC();
  });

  // Verificar al cambiar de pestaña MOSCATEL
  $("#AGRICOLAsugraTabs a[data-toggle='tab']").on("shown.bs.tab", function () {
    AGRICOLAverificarPestañaActiva_SUGRA();
  });

  //============================================================

  //SWEET GLOBE - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION
  $(".AGRICOLAbtnAñadirFaseSG").on("click", function () {
    // Abrir el modal de creación de programa
    $("#AGRICOLAmodalCrearPrograma").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = AGRICOLAverificarPestañaActiva_SG();

    // cambiar el titulo del modal
    $("#AGRICOLAmodalCrearProgramaLabel").text("CREAR NUEVA FASE - " + nombrePestaña);

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    let idVariedad;
    if (nombrePestaña == "PLANTINES") {
      $("#AGRICOLAidfase").val(1);
      $("#AGRICOLAidvariedad").val(1);
      idVariedad = 1;
    } else if (nombrePestaña == "POST COSECHA") {
      $("#AGRICOLAidfase").val(2);
      $("#AGRICOLAidvariedad").val(1);
      idVariedad = 1;
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#AGRICOLAidfase").val(3);
      $("#AGRICOLAidvariedad").val(1);
      idVariedad = 1;
    }

    // Cargar los lotes para la variedad Sweet Globe
    AGRICOLAcargarLotes(idVariedad);
  });

  // AUTUMN CRISP - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION
  $(".AGRICOLAbtnAñadirFaseAC").on("click", function () {
    // Abrir el modal de creación de programa
    $("#AGRICOLAmodalCrearPrograma_AC").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = AGRICOLAverificarPestañaActiva_AC();

    // cambiar el titulo del modal
    $("#AGRICOLAmodalCrearProgramaLabel_AC").text(
      "CREAR NUEVA FASE - " + nombrePestaña
    );

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    if (nombrePestaña == "PLANTINES") {
      $("#AGRICOLAidfase_AC").val(1);
      $("#AGRICOLAidvariedad_AC").val(2);
      // Cargar lotes para Autumn Crisp (idvariedad = 2)
      AGRICOLAcargarLotes(2);
    } else if (nombrePestaña == "POST COSECHA") {
      $("#AGRICOLAidfase_AC").val(2);
      $("#AGRICOLAidvariedad_AC").val(2);
      // Cargar lotes para Autumn Crisp (idvariedad = 2)
      AGRICOLAcargarLotes(2);
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#AGRICOLAidfase_AC").val(3);
      $("#AGRICOLAidvariedad_AC").val(2);
      // Cargar lotes para Autumn Crisp (idvariedad = 2)
      AGRICOLAcargarLotes(2);
    }

    // Si estamos en modo creación, limpiar el formulario
    if (!$("#AGRICOLAidregistro_AC").length) {
      // Limpiar el formulario
      $("#AGRICOLAformCrearPrograma_AC")[0].reset();

      // Limpiar el selector de lotes
      $("#AGRICOLAselectLote_AC").find("option:not(:first)").remove();

      // Restaurar el texto del botón
      $("#AGRICOLAbtnGuardarProgramaAC").text("Guardar");
    }
  });

  //MOSCATEL - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION
  $(".AGRICOLAbtnAñadirFaseMC").on("click", function () {
    // Abrir el modal de creación de programa
    $("#AGRICOLAmodalCrearPrograma_MC").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = AGRICOLAverificarPestañaActiva_MC();

    // cambiar el titulo del modal
    $("#AGRICOLAmodalCrearProgramaLabel_MC").text(
      "CREAR NUEVA FASE - " + nombrePestaña
    );

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    if (nombrePestaña == "PLANTINES") {
      $("#AGRICOLAidfase_MC").val(1);
      $("#AGRICOLAidvariedad_MC").val(3);
      // Cargar lotes para Moscatel (idvariedad = 3)
      AGRICOLAcargarLotes(3);
    } else if (nombrePestaña == "POST COSECHA") {
      $("#AGRICOLAidfase_MC").val(2);
      $("#AGRICOLAidvariedad_MC").val(3);
      // Cargar lotes para Moscatel (idvariedad = 3)
      AGRICOLAcargarLotes(3);
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#AGRICOLAidfase_MC").val(3);
      $("#AGRICOLAidvariedad_MC").val(3);
      // Cargar lotes para Moscatel (idvariedad = 3)
      AGRICOLAcargarLotes(3);
    }

    // Si estamos en modo creación, limpiar el formulario
    if (!$("#AGRICOLAidregistro_MC").length) {
      // Limpiar el formulario
      $("#AGRICOLAformCrearPrograma_MC")[0].reset();

      // Limpiar el selector de lotes
      $("#AGRICOLAselectLote_MC").find("option:not(:first)").remove();

      // Restaurar el texto del botón
      $("#AGRICOLAbtnGuardarProgramaMC").text("Guardar");
    }
  });

  //SUGRA - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION

  $(".AGRICOLAbtnAñadirFaseSUGRA").on("click", function () {
    // Abrir el modal de creación de programa
    $("#AGRICOLAmodalCrearPrograma_SUGRA").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = AGRICOLAverificarPestañaActiva_SUGRA();

    // cambiar el titulo del modal
    $("#AGRICOLAmodalCrearProgramaLabel_SUGRA").text(
      "CREAR NUEVA FASE - " + nombrePestaña
    );

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    if (nombrePestaña == "PLANTINES") {
      $("#AGRICOLAidfase_SUGRA").val(1);
      $("#AGRICOLAidvariedad_SUGRA").val(4);
      // Cargar lotes para Sugra (idvariedad = 4)
      AGRICOLAcargarLotes(4);
    } else if (nombrePestaña == "POST COSECHA") {
      $("#AGRICOLAidfase_SUGRA").val(2);
      $("#AGRICOLAidvariedad_SUGRA").val(4);
      // Cargar lotes para Sugra (idvariedad = 4)
      AGRICOLAcargarLotes(4);
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#AGRICOLAidfase_SUGRA").val(3);
      $("#AGRICOLAidvariedad_SUGRA").val(4);
      // Cargar lotes para Sugra (idvariedad = 4)
      AGRICOLAcargarLotes(4);
    }

    // Si estamos en modo creación, limpiar el formulario
    if (!$("#AGRICOLAidregistro_SUGRA").length) {
      // Limpiar el formulario
      $("#AGRICOLAformCrearPrograma_SUGRA")[0].reset();

      // Limpiar el selector de lotes
      $("#AGRICOLAselectLote_SUGRA").find("option:not(:first)").remove();

      // Restaurar el texto del botón
      $("#AGRICOLAbtnGuardarProgramaSUGRA").text("Guardar");
    }
  });

  //============================================================

  // SWEET GLOBE - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#AGRICOLAbtnGuardarProgramaSG").on("click", function () {
    AGRICOLAguardarNuevoPrograma_SG();
  });

  //============================================================================
  // EVENTOS PARA GUARDAR EL NUEVO FASE
  //============================================================================

  // AUTUMN CRISP - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#AGRICOLAbtnGuardarProgramaAC").on("click", function () {
    AGRICOLAguardarNuevoPrograma_AC();
  });

  // MOSCATEL - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#AGRICOLAbtnGuardarProgramaMC").on("click", function () {
    AGRICOLAguardarNuevoPrograma_MC();
  });

  // SUGRA - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#AGRICOLAbtnGuardarProgramaSUGRA").on("click", function () {
    AGRICOLAguardarNuevoPrograma_SUGRA();
  });

  //============================================================================
  // EVENTOS PARA MANEJO DE LOTES
  //============================================================================

  // Evento para limpiar errores cuando se selecciona un lote
  $("#selectLote").on("change", function () {
    // Limpiar errores de validación
    $(this).css("border", "");
    $(this).next(".text-danger").remove();
  });

  // Evento para limpiar errores cuando se selecciona un lote en Autumn Crisp
  $("#AGRICOLAselectLote_AC").on("change", function () {
    // Limpiar errores de validación
    $(this).css("border", "");
    $(this).next(".text-danger").remove();
  });

  // Evento para limpiar errores cuando se selecciona un lote en Moscatel
  $("#AGRICOLAselectLote_MC").on("change", function () {
    // Limpiar errores de validación
    $(this).css("border", "");
    $(this).next(".text-danger").remove();
  });

  // Evento para limpiar errores cuando se selecciona un lote en Sugra
  $("#AGRICOLAselectLote_SUGRA").on("change", function () {
    // Limpiar errores de validación
    $(this).css("border", "");
    $(this).next(".text-danger").remove();
  });

  //============================================================================
  // EVENTOS PARA EDITAR LA FASE
  //============================================================================

  $("#btnEditarFertilizacion_SG").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    AGRICOLAeditarFertilizacion_SG(idRegistro);
  });

  $("#btnEditarFertilizacion_AC").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    AGRICOLAeditarFertilizacion_AC(idRegistro);
  });

  $("#btnEditarFertilizacion_MC").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    AGRICOLAeditarFertilizacion_MC(idRegistro);
  });

  $("#btnEditarFertilizacion_SUGRA").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    AGRICOLAeditarFertilizacion_SUGRA(idRegistro);
  });

  //============================================================================
  // EVENTOS PARA ELIMINAR LA FASE
  //============================================================================

  // Corregir el evento del botón eliminar para que use el data-id correctamente
  $("#btnEliminarFertilizacion_SG").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    AGRICOLAeliminarFertilizacion(idRegistro);
  });

  $("#btnEliminarFertilizacion_AC").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    AGRICOLAeliminarFertilizacion_AC(idRegistro);
  });

  $("#btnEliminarFertilizacion_MC").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    AGRICOLAeliminarFertilizacion_MC(idRegistro);
  });

  $("#btnEliminarFertilizacion_SUGRA").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    AGRICOLAeliminarFertilizacion_SUGRA(idRegistro);
  });

  // $("#AGRICOLAbtnGuardarProducto").on("click", function () {
  //   guardarProductoSweetGlobe();
  // });

  // Evento para guardar producto de Autumn Crisp
  // $("#AGRICOLAbtnGuardarProducto_AC").on("click", function () {
  //   AGRICOLAguardarProductoAutumnCrisp();
  // });

  // Calcular precio por hectárea automáticamente para productos de Autumn Crisp
  $("#AGRICOLAnecesidadProducto_AC, #AGRICOLAprecioProducto_AC").on("input", function () {
    const necesidad = parseFloat($("#AGRICOLAnecesidadProducto_AC").val()) || 0;
    const precioLtKg = parseFloat($("#AGRICOLAprecioProducto_AC").val()) || 0;
    const precioHa = necesidad * precioLtKg;
    $("#AGRICOLAprecioHaProducto_AC").val(precioHa.toFixed(2));
  });

  // Eventos para botones de editar y eliminar productos (delegación de eventos)
  $("#AGRICOLAtablaDetalleProductos_AC").on(
    "click",
    ".btn-editar-producto-AC",
    function () {
      const idProducto = $(this).data("id");
      AGRICOLAeditarProductoAutumnCrisp(idProducto);
    }
  );

  $("#AGRICOLAtablaDetalleProductos_AC").on(
    "click",
    ".btn-eliminar-producto-AC",
    function () {
      const idProducto = $(this).data("id");
      AGRICOLAeliminarProductoAutumnCrisp(idProducto);
    }
  );

  // ============================================================================
  // EVENT LISTENERS PARA PRODUCTOS MOSCATEL
  // ============================================================================

  // // Evento para guardar producto de Moscatel
  // $("#AGRICOLAbtnGuardarProducto_MC").on("click", function () {
  //   AGRICOLAguardarProductoMoscatel();
  // });

  // Calcular precio por hectárea automáticamente para productos de Moscatel
  $("#AGRICOLAnecesidadProducto_MC, #AGRICOLAprecioProducto_MC").on("input", function () {
    const necesidad = parseFloat($("#AGRICOLAnecesidadProducto_MC").val()) || 0;
    const precioLtKg = parseFloat($("#AGRICOLAprecioProducto_MC").val()) || 0;
    const precioHa = necesidad * precioLtKg;
    $("#AGRICOLAprecioHaProducto_MC").val(precioHa.toFixed(2));
  });

  // Eventos para botones de editar y eliminar productos (delegación de eventos)
  $("#AGRICOLAtablaDetalleProductos_MC").on(
    "click",
    ".btn-editar-producto-MC",
    function () {
      const idProducto = $(this).data("id");
      AGRICOLAeditarProductoMoscatel(idProducto);
    }
  );

  $("#AGRICOLAtablaDetalleProductos_MC").on(
    "click",
    ".btn-eliminar-producto-MC",
    function () {
      const idProducto = $(this).data("id");
      AGRICOLAeliminarProductoMoscatel(idProducto);
    }
  );

  // Evento para el botón Añadir Producto en el modal de detalless
  $("#AGRICOLAbtnAñadirProducto_MC").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#AGRICOLAprogramaId_MC").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    AGRICOLAabrirModalNuevoProducto_MC(programaId);
  });

  // Evento para el botón Añadir Producto en el modal de detalles de Autumn Crisp
  $("#AGRICOLAbtnAñadirProducto_AC").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#AGRICOLAprogramaId_AC").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    AGRICOLAabrirModalNuevoProducto_AC(programaId);
  });

  // ============================================================================
  // EVENT LISTENERS PARA PRODUCTOS SUGRA
  // ============================================================================

  // Evento para guardar producto de Sugra
  // $("#AGRICOLAbtnGuardarProducto_SUGRA").on("click", function () {
  //   AGRICOLAguardarProductoSugra();
  // });

  // BOTON CERRAR MODAL FACE  SUGRA
  $('[data-click="panel-remove-face-sugra"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalSugra").modal("hide");
  });

  // BOTON CERRAR MODAL CREAR FACE SUGRA
  $('[data-click="panel-remove-crear-programa-sugra"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalCrearPrograma_SUGRA").modal("hide");
  });

  // BOTON CERRAR MODAL  DETALLE PRODUCTOS SUGRA
  $('[data-click="panel-remove-detalle-productos-sugra"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalDetalleProductos_SUGRA").modal("hide");
  });

  //============================================================

  // BOTON CERRAR MODAL FACE  SWEET GLOBE
  $('[data-click="panel-remove-face-sweet-globe"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalSweetGlobe").modal("hide");
  });

  // BOTON CERRAR MODAL CREAR PROGRAMA SWEET GLOBE
  $('[data-click="panel-remove-crear-programa-sweet-globe"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalCrearPrograma").modal("hide");
  });

  // BOTON CERRAR MODAL  DETALLE PRODUCTOS SWEET GLOBE
  $('[data-click="panel-remove-detalle-productos-sweet-globe"]').click(function (
    e
  ) {
    e.stopPropagation();
    $("#AGRICOLAmodalDetalleProductos").modal("hide");
  });

  //============================================================

  // BOTON CERRAR MODAL FACE  AUTUMN CRISP
  $('[data-click="panel-remove-face-autumn-crisp"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalAutumnCrisp").modal("hide");
  });

  $('[data-click="panel-remove-crear-programa-autumn-crisp"]').click(function (
    e
  ) {
    e.stopPropagation();
    $("#AGRICOLAmodalCrearPrograma_AC").modal("hide");
  });

  // BOTON CERRAR MODAL  DETALLE PRODUCTOS AUTUMN CRISP
  $('[data-click="panel-remove-detalle-productos-autumn-crisp"]').click(function (
    e
  ) {
    e.stopPropagation();
    $("#AGRICOLAmodalDetalleProductos_AC").modal("hide");
  });

  //============================================================

  // BOTON CERRAR MODAL FACE  MOSCATEL
  $('[data-click="panel-remove-face-moscatel"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalMoscatel").modal("hide");
  });

  $('[data-click="panel-remove-crear-programa-moscatel"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalCrearPrograma_MC").modal("hide");
  });

  // BOTON CERRAR MODAL  DETALLE PRODUCTOS MOSCATEL
  $('[data-click="panel-remove-detalle-productos-moscatel"]').click(function (e) {
    e.stopPropagation();
    $("#AGRICOLAmodalDetalleProductos_MC").modal("hide");
  });


  // Calcular precio por hectárea automáticamente para productos de Sugra
  $("#AGRICOLAnecesidadProducto_SUGRA, #AGRICOLAprecioProducto_SUGRA").on("input", function () {
    const necesidad = parseFloat($("#AGRICOLAnecesidadProducto_SUGRA").val()) || 0;
    const precioLtKg = parseFloat($("#AGRICOLAprecioProducto_SUGRA").val()) || 0;
    const precioHa = necesidad * precioLtKg;
    $("#AGRICOLAprecioHaProducto_SUGRA").val(precioHa.toFixed(2));
  });

  // Eventos para botones de editar y eliminar productos (delegación de eventos)
  $("#AGRICOLAtablaDetalleProductos_SUGRA").on(
    "click",
    ".btn-editar-producto-SUGRA",
    function () {
      const idProducto = $(this).data("id");
      AGRICOLAeditarProductoSugra(idProducto);
    }
  );

  $("#AGRICOLAtablaDetalleProductos_SUGRA").on(
    "click",
    ".btn-eliminar-producto-SUGRA",
    function () {
      const idProducto = $(this).data("id");
      AGRICOLAeliminarProductoSugra(idProducto);
    }
  );

  // Evento para el botón Añadir Producto en el modal de detalles
  $("#AGRICOLAbtnAñadirProducto_SUGRA").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#AGRICOLAprogramaId_SUGRA").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    AGRICOLAabrirModalNuevoProducto_SUGRA(programaId);
  });
});

//============================================================================
// FUNCIONES PARA GUARDAR PRODUCTOS POR VARIEDAD
//============================================================================

// Función específica para guardar suministros (SUMINISTRO_AGRICOLA) de Sweet Globe
function AGRICOLAguardarProductoSweetGlobe() {
  var programaId = $("#AGRICOLAprogramaId").val();
  var suministroPk = ($("#AGRICOLAproductoId").val() || "").trim();
  var esEdicion = suministroPk !== "";
  var idproducto = ($("#AGRICOLA_idproducto_sum").val() || "").trim();
  var descripcion = ($("#AGRICOLA_descripcion_sum").val() || "").trim();
  var precioUnitario = parseFloat($("#AGRICOLA_precio_unitario_sum").val());
  var idArea = parseInt($("#AGRICOLA_id_area_sum").val(), 10);
  var idTipo = parseInt($("#AGRICOLA_id_tipo_suministro_sum").val(), 10);

  if (!programaId) {
    Swal.fire("Error", "No se ha seleccionado el programa (cabecera).", "error");
    return false;
  }

  var formProducto = $("#AGRICOLAformProducto")[0];
  if (formProducto && !formProducto.checkValidity()) {
    formProducto.reportValidity();
    return false;
  }

  if (!idproducto || !descripcion) {
    Swal.fire("Error", "Seleccione un producto de la lista (descripción e ID).", "error");
    return false;
  }

  if (isNaN(precioUnitario) || precioUnitario <= 0) {
    Swal.fire("Error", "Indique un precio unitario válido mayor a 0.", "error");
    return false;
  }

  var mesesPayload = [
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

  var datosProducto = {
    idproducto: idproducto,
    descripcion: descripcion,
    precio_unitario: precioUnitario,
    id_area: isNaN(idArea) ? 11 : idArea,
    id_tipo_suministro: isNaN(idTipo) ? 1 : idTipo,
  };

  mesesPayload.forEach(function (mes) {
    var activo = $("#AGRICOLA_sum_" + mes + "_switch").is(":checked");
    var c = activo ? parseFloat($("#AGRICOLA_sum_" + mes + "_cantidad").val()) || 0 : 0;
    datosProducto[mes + "_cantidad"] = c;
  });

  if (!esEdicion) {
    datosProducto.IDPRODUCTO_AGRICOLA = parseInt(programaId, 10);
    if (isNaN(datosProducto.IDPRODUCTO_AGRICOLA)) {
      Swal.fire("Error", "ID de programa agrícola inválido.", "error");
      return false;
    }
  }

  var url = "/riego/api/suministro_agricola_ajs/";
  var metodo = "POST";
  if (esEdicion) {
    url = "/riego/api/suministro_agricola_ajs/" + encodeURIComponent(suministroPk) + "/";
    metodo = "PUT";
  }

  Swal.fire({
    title: esEdicion ? "Actualizando..." : "Guardando...",
    text: esEdicion
      ? "Por favor espere mientras se actualiza el suministro"
      : "Por favor espere mientras se guarda el suministro",
    allowOutsideClick: false,
    didOpen: function () {
      Swal.showLoading();
    },
  });

  $.ajax({
    url: url,
    type: metodo,
    contentType: "application/json",
    data: JSON.stringify(datosProducto),
    success: function () {
      Swal.close();
      Swal.fire({
        title: "¡Éxito!",
        text: esEdicion
          ? "El suministro ha sido actualizado correctamente"
          : "El suministro ha sido guardado correctamente",
        icon: "success",
        confirmButtonText: "Aceptar",
      });
      $("#AGRICOLAmodalProducto").modal("hide");
      AGRICOLAcargarProductosPrograma(programaId);
      return true;
    },
    error: function (xhr, status, error) {
      console.error(
        "Error al " + (esEdicion ? "actualizar" : "guardar") + " suministro Sweet Globe:",
        error
      );
      Swal.close();
      var errorMsg =
        "Ha ocurrido un error al " + (esEdicion ? "actualizar" : "guardar") + " el suministro";
      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }
      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      return false;
    },
  });
}

//============================================================================
// FUNCIONES PARA EDITAR Y ELIMINAR PRODUCTOS - SWEET GLOBE
//============================================================================

// Función para editar una fila de SUMINISTRO_AGRICOLA (Sweet Globe)
function AGRICOLAeditarProductoSweetGlobe(idSuministro) {
  $.ajax({
    url: "/riego/api/suministro_agricola_ajs/" + encodeURIComponent(idSuministro) + "/",
    type: "GET",
    success: function (response) {
      if (!response || !response.data) {
        Swal.fire("Error", "No se pudo obtener la información del suministro", "error");
        return;
      }

      var p = response.data;
      var mesesEd = [
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

      $("#AGRICOLAproductoId").val(p.id);
      if (p.idproducto_agricola != null && p.idproducto_agricola !== "") {
        $("#AGRICOLAprogramaId").val(p.idproducto_agricola);
      }

      $("#AGRICOLA_idproducto_sum").val(p.idproducto != null ? String(p.idproducto) : "");
      $("#AGRICOLA_descripcion_sum").val(p.descripcion || "");
      var pu = parseFloat(p.precio_unitario);
      if (isNaN(pu)) {
        pu = 0;
      }
      $("#AGRICOLA_precio_unitario_sum").val(pu.toFixed(2)).prop("readonly", false);

      if ($("#AGRICOLA_id_area_sum").length) {
        $("#AGRICOLA_id_area_sum").val(
          p.id_area != null && p.id_area !== "" ? p.id_area : "11"
        );
      }
      if ($("#AGRICOLA_id_tipo_suministro_sum").length) {
        $("#AGRICOLA_id_tipo_suministro_sum").val(
          p.id_tipo_suministro != null && p.id_tipo_suministro !== ""
            ? p.id_tipo_suministro
            : "1"
        );
      }

      mesesEd.forEach(function (mes) {
        var cantKey = mes + "_cantidad";
        var cant = parseFloat(p[cantKey]);
        if (!isNaN(cant) && cant > 0) {
          $("#AGRICOLA_sum_" + mes + "_switch").prop("checked", true);
          $("#AGRICOLA_sum_" + mes + "_cantidad").prop("disabled", false).val(cant);
        } else {
          $("#AGRICOLA_sum_" + mes + "_switch").prop("checked", false);
          $("#AGRICOLA_sum_" + mes + "_cantidad").prop("disabled", true).val("");
        }
      });

      $("#AGRICOLA_cantidad_masiva_sum").val("");
      $("#AGRICOLAmodalProductoLabel").html(
        '<i class="fas fa-edit mr-2"></i> Editar suministro'
      );
      $("#AGRICOLAmodalProducto").modal("show");
      AGRICOLAinitEventosFormularioProducto_SG();
      AGRICOLA_calcularTotalesSuministroSG();
    },
    error: function (xhr, status, error) {
      var errorMsg = "Ha ocurrido un error al obtener los datos del suministro";
      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }
      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      console.error("Error al obtener datos del suministro:", error);
    },
  });
}

// Función para eliminar un producto de Sweet Globe
function AGRICOLAeliminarProductoSweetGlobe(idProducto) {
  // Mostrar confirmación mediante SweetAlert2
  Swal.fire({
    title: "¿Estás seguro?",
    text: "¡No podrás revertir esta acción!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Mostrar indicador de carga
      Swal.fire({
        title: "Eliminando...",
        text: "Por favor espere mientras se elimina el producto",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Enviar la petición AJAX para eliminar el suministro
      $.ajax({
        url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
        type: "DELETE",
        success: function (response) {
          // Cerrar indicador de carga
          Swal.close();

          // Mostrar mensaje de éxito
          Swal.fire({
            title: "¡Eliminado!",
            text: "El producto ha sido eliminado correctamente",
            icon: "success",
            confirmButtonText: "Aceptar",
          });

          // Obtener el ID del programa actual para recargar la tabla
          const programaId = $("#AGRICOLAprogramaId").val();

          // Recargar la tabla de productos
          if (programaId) {
            AGRICOLAcargarProductosPrograma(programaId);
          }
        },
        error: function (xhr, status, error) {
          // Cerrar indicador de carga
          Swal.close();

          // Mostrar mensaje de error
          let errorMsg = "Ha ocurrido un error al eliminar el producto";

          if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          }

          Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error",
            confirmButtonText: "Aceptar",
          });

          console.error("Error al eliminar el producto:", error);
        },
      });
    }
  });
}

//============================================================================
// FUNCIONES PARA MOSTRAR LOS DETALLES DE LOS PRODUCTOS PARA MOSCATEL
//============================================================================

// Función para mostrar el modal de detalle de productos para MOSCATEL
function AGRICOLAmostrarDetallesProductos_MC(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#AGRICOLAprogramaId_MC").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del programa",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const programa = response.data;

      // Actualizar los datos en el modal
      $("#AGRICOLAnombreProgramaDetalle_MC").text(programa.NOMBRE);
      $("#AGRICOLAfechaInicioProgramaDetalle_MC").text(programa.FECHA_INICIO);
      $("#AGRICOLAfechaFinProgramaDetalle_MC").text(programa.FECHA_FIN);
      $("#AGRICOLAdescripcionProgramaDetalle_MC").text(
        programa.DESCRIPCION || "Sin descripción"
      );

      $("#AGRICOLAsectorProgramaDetalle_MC").text(programa.SECTOR || "no definido");
      $("#AGRICOLAloteProgramaDetalle_MC").text(programa.LOTE_NOMBRE || "no definido");

      // Mostrar el modal

      $("#AGRICOLAmodalDetalleProductos_MC").modal("show");

      // Cargar los productos relacionados con este programa
      AGRICOLAcargarProductosPrograma_MC(idRegistro);
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del programa";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos del programa Moscatel:", error);
    },
  });
}

// Función para cargar los productos relacionados con el programa para MOSCATEL
function AGRICOLAcargarProductosPrograma_MC(idPrograma) {
  var mesesDetalle = [
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

  function AGRICOLAvalorMesCantidad_MC(row, mes) {
    var k = mes + "_cantidad";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAvalorMesPrecio_MC(row, mes) {
    var k = mes + "_precio";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAtotalFilaProducto_MC(row) {
    var suma = 0;
    mesesDetalle.forEach(function (m) {
      var k = m + "_precio";
      if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
        suma += parseFloat(row[k]);
      }
    });
    if (suma > 0) {
      return "S/ " + suma.toFixed(2);
    }
    return "S/ 0.00";
  }

  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#AGRICOLAtablaDetalleProductos_MC")) {
    $("#AGRICOLAtablaDetalleProductos_MC").DataTable().clear().destroy();
  }

  var columnasDetalle = [
    {
      data: null,
      className: "text-center",
      orderable: false,
      render: function (data, type, row, meta) {
        return meta.row + 1;
      },
    },
    { data: "idproducto", className: "text-center" },
    { data: "descripcion", className: "text-left" },
  ];

  mesesDetalle.forEach(function (mes) {
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesCantidad_MC(row, mes);
      },
    });
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesPrecio_MC(row, mes);
      },
    });
  });

  columnasDetalle.push({
    data: null,
    className: "text-center",
    orderable: false,
    render: function (data, type, row) {
      return AGRICOLAtotalFilaProducto_MC(row);
    },
  });

  columnasDetalle.push({
    data: null,
    className: "text-center text-nowrap",
    orderable: false,
    render: function (data, type, row) {
      var id = row.id;
      return (
        '<button type="button" class="btn btn-sm btn-info mr-1" title="Editar" onclick="AGRICOLAeditarProductoMoscatel(' +
        id +
        ')"><i class="fas fa-edit"></i></button>' +
        '<button type="button" class="btn btn-sm btn-danger" title="Eliminar" onclick="AGRICOLAeliminarProductoMoscatel(' +
        id +
        ')"><i class="fas fa-trash"></i></button>'
      );
    },
  });

  // Iniciar la tabla de productos con datos de la API
  $("#AGRICOLAtablaDetalleProductos_MC").DataTable({
    responsive: false,
    scrollX: true,
    autoWidth: false,
    pageLength: 7,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url:
        "/riego/api/suministro_agricola_ajs/?id_producto_agricola=" +
        encodeURIComponent(idPrograma),
      type: "GET",
      dataSrc: function (json) {
        if (!json) {
          return [];
        }
        if (json.error) {
          return [];
        }
        var rows = Array.isArray(json) ? json : json.data || [];
        $("#AGRICOLAtotalProductosProgramaDetalle_plantines_MC").text(rows.length);
        var costoTotal = 0;
        rows.forEach(function (item) {
          var sumaMeses = 0;
          mesesDetalle.forEach(function (m) {
            var pk = m + "_precio";
            if (
              item[pk] != null &&
              item[pk] !== "" &&
              !isNaN(parseFloat(item[pk]))
            ) {
              sumaMeses += parseFloat(item[pk]);
            }
          });
          costoTotal += sumaMeses;
        });
        $("#AGRICOLAcostoTotalProgramaDetalle_MC").text(
          "$ " + costoTotal.toFixed(2)
        );
        return rows;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        $("#AGRICOLAtablaDetalleProductos_MC tbody").html(
          '<tr><td colspan="29" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
        );
      },
    },
    columns: columnasDetalle,
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      $(row).attr("data-id", data.id);
    },
  });
}

//============================================================================
// FUNCIONES PARA EDITAR Y ELIMINAR PRODUCTOS - SWEET GLOBE
//============================================================================

// Función para editar una fila de SUMINISTRO_AGRICOLA (Sweet Globe)
function AGRICOLAeditarProductoMoscatel(idSuministro) {
  $.ajax({
    url: "/riego/api/suministro_agricola_ajs/" + encodeURIComponent(idSuministro) + "/",
    type: "GET",
    success: function (response) {
      if (!response || !response.data) {
        Swal.fire("Error", "No se pudo obtener la información del suministro", "error");
        return;
      }

      var p = response.data;
      var mesesEd = [
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

      $("#AGRICOLAproductoId_MC").val(p.id);
      if (p.idproducto_agricola != null && p.idproducto_agricola !== "") {
        $("#AGRICOLAprogramaId_MC").val(p.idproducto_agricola);
      }

      $("#AGRICOLA_idproducto_sum_MC").val(p.idproducto != null ? String(p.idproducto) : "");
      $("#AGRICOLA_descripcion_sum_MC").val(p.descripcion || "");
      var pu = parseFloat(p.precio_unitario);
      if (isNaN(pu)) {
        pu = 0;
      }
      $("#AGRICOLA_precio_unitario_sum_MC").val(pu.toFixed(2)).prop("readonly", false);

      if ($("#AGRICOLA_id_area_sum_MC").length) {
        $("#AGRICOLA_id_area_sum_MC").val(
          p.id_area != null && p.id_area !== "" ? p.id_area : "11"
        );
      }
      if ($("#AGRICOLA_id_tipo_suministro_sum_MC").length) {
        $("#AGRICOLA_id_tipo_suministro_sum_MC").val(
          p.id_tipo_suministro != null && p.id_tipo_suministro !== ""
            ? p.id_tipo_suministro
            : "1"
        );
      }

      mesesEd.forEach(function (mes) {
        var cantKey = mes + "_cantidad";
        var cant = parseFloat(p[cantKey]);
        if (!isNaN(cant) && cant > 0) {
          $("#AGRICOLA_sum_MC" + mes + "_switch").prop("checked", true);
          $("#AGRICOLA_sum_MC" + mes + "_cantidad").prop("disabled", false).val(cant);
        } else {
          $("#AGRICOLA_sum_MC" + mes + "_switch").prop("checked", false);
          $("#AGRICOLA_sum_MC" + mes + "_cantidad").prop("disabled", true).val("");
        }
      });

      $("#AGRICOLA_cantidad_masiva_sum_MC").val("");
      $("#AGRICOLAmodalProductoLabel_MC").html(
        '<i class="fas fa-edit mr-2"></i> Editar suministro'
      );
      $("#AGRICOLAmodalProducto_MC").modal("show");
      AGRICOLAinitEventosFormularioProducto_SG();
      AGRICOLA_calcularTotalesSuministroSG();
    },
    error: function (xhr, status, error) {
      var errorMsg = "Ha ocurrido un error al obtener los datos del suministro";
      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }
      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      console.error("Error al obtener datos del suministro:", error);
    },
  });
}

// Función para eliminar un producto de Sweet Globe
function AGRICOLAeliminarProductoMoscatel(idProducto) {
  // Mostrar confirmación mediante SweetAlert2
  Swal.fire({
    title: "¿Estás seguro?",
    text: "¡No podrás revertir esta acción!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Mostrar indicador de carga
      Swal.fire({
        title: "Eliminando...",
        text: "Por favor espere mientras se elimina el producto",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Enviar la petición AJAX para eliminar el suministro
      $.ajax({
        url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
        type: "DELETE",
        success: function (response) {
          // Cerrar indicador de carga
          Swal.close();

          // Mostrar mensaje de éxito
          Swal.fire({
            title: "¡Eliminado!",
            text: "El producto ha sido eliminado correctamente",
            icon: "success",
            confirmButtonText: "Aceptar",
          });

          // Obtener el ID del programa actual para recargar la tabla
          const programaId = $("#AGRICOLAprogramaId_MC").val();

          // Recargar la tabla de productos
          if (programaId) {
            AGRICOLAcargarProductosPrograma_MC(programaId);
          }
        },
        error: function (xhr, status, error) {
          // Cerrar indicador de carga
          Swal.close();

          // Mostrar mensaje de error
          let errorMsg = "Ha ocurrido un error al eliminar el producto";

          if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          }

          Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error",
            confirmButtonText: "Aceptar",
          });

          console.error("Error al eliminar el producto:", error);
        },
      });
    }
  });
}

//============================================================================
// FUNCIONES PARA GUARDAR, EDITAR Y ELIMINAR PRODUCTOS - MOSCATEL
//============================================================================

// Función para guardar o editar un producto de Moscatel
function AGRICOLAguardarProductoMoscatel() {
  var programaId = $("#AGRICOLAprogramaId_MC").val();
  var suministroPk = ($("#AGRICOLAproductoId_MC").val() || "").trim();
  var esEdicion = suministroPk !== "";
  var idproducto = ($("#AGRICOLA_idproducto_sum_MC").val() || "").trim();
  var descripcion = ($("#AGRICOLA_descripcion_sum_MC").val() || "").trim();
  var precioUnitario = parseFloat($("#AGRICOLA_precio_unitario_sum_MC").val());
  var idArea = parseInt($("#AGRICOLA_id_area_sum_MC").val(), 10);
  var idTipo = parseInt($("#AGRICOLA_id_tipo_suministro_sum_MC").val(), 10);

  if (!programaId) {
    Swal.fire("Error", "No se ha seleccionado el programa (cabecera).", "error");
    return false;
  }

  var formProducto = $("#AGRICOLAformProducto_MC")[0];
  if (formProducto && !formProducto.checkValidity()) {
    formProducto.reportValidity();
    return false;
  }

  if (!idproducto || !descripcion) {
    Swal.fire("Error", "Seleccione un producto de la lista (descripción e ID).", "error");
    return false;
  }

  if (isNaN(precioUnitario) || precioUnitario <= 0) {
    Swal.fire("Error", "Indique un precio unitario válido mayor a 0.", "error");
    return false;
  }

  var mesesPayload = [
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

  var datosProducto = {
    idproducto: idproducto,
    descripcion: descripcion,
    precio_unitario: precioUnitario,
    id_area: isNaN(idArea) ? 11 : idArea,
    id_tipo_suministro: isNaN(idTipo) ? 1 : idTipo,
  };

  mesesPayload.forEach(function (mes) {
    var activo = $("#AGRICOLA_sum_MC" + mes + "_switch").is(":checked");
    var c = activo ? parseFloat($("#AGRICOLA_sum_MC" + mes + "_cantidad").val()) || 0 : 0;
    datosProducto[mes + "_cantidad"] = c;
  });

  if (!esEdicion) {
    datosProducto.IDPRODUCTO_AGRICOLA = parseInt(programaId, 10);
    if (isNaN(datosProducto.IDPRODUCTO_AGRICOLA)) {
      Swal.fire("Error", "ID de programa agrícola inválido.", "error");
      return false;
    }
  }

  var url = "/riego/api/suministro_agricola_ajs/";
  var metodo = "POST";
  if (esEdicion) {
    url = "/riego/api/suministro_agricola_ajs/" + encodeURIComponent(suministroPk) + "/";
    metodo = "PUT";
  }

  Swal.fire({
    title: esEdicion ? "Actualizando..." : "Guardando...",
    text: esEdicion
      ? "Por favor espere mientras se actualiza el suministro"
      : "Por favor espere mientras se guarda el suministro",
    allowOutsideClick: false,
    didOpen: function () {
      Swal.showLoading();
    },
  });

  $.ajax({
    url: url,
    type: metodo,
    contentType: "application/json",
    data: JSON.stringify(datosProducto),
    success: function () {
      Swal.close();
      Swal.fire({
        title: "¡Éxito!",
        text: esEdicion
          ? "El suministro ha sido actualizado correctamente"
          : "El suministro ha sido guardado correctamente",
        icon: "success",
        confirmButtonText: "Aceptar",
      });
      $("#AGRICOLAmodalProducto_MC").modal("hide");
      AGRICOLAcargarProductosPrograma_MC(programaId);
      return true;
    },
    error: function (xhr, status, error) {
      console.error(
        "Error al " + (esEdicion ? "actualizar" : "guardar") + " suministro Sweet Globe:",
        error
      );
      Swal.close();
      var errorMsg =
        "Ha ocurrido un error al " + (esEdicion ? "actualizar" : "guardar") + " el suministro";
      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }
      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      return false;
    },
  });
}

// Función para editar un producto de Moscatel
function AGRICOLAeditarProductoMoscatel(idProducto) {
  // Realizar una petición AJAX para obtener los datos del producto
  $.ajax({
    url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
    type: "GET",
    success: function (response) {
      if (response && response.data) {
        // Obtener los datos del producto
        const producto = response.data;

        // Llenar el formulario con los datos
        $("#AGRICOLAproductoId_MC").val(idProducto);
        $("#AGRICOLAsubGrupoProducto_MC").val(producto.SUBGRUPO);
        $("#AGRICOLAnombreProducto_MC").val(producto.PRODUCTO);
        $("#AGRICOLAmateriaActivaProducto_MC").val(producto.MATERIA_ACTIVA);
        $("#AGRICOLAnecesidadProducto_MC").val(producto.NECESIDADXHA);
        $("#AGRICOLAunidadNecesidadProducto_MC").val(producto.UND);
        $("#AGRICOLAprecioProducto_MC").val(producto.PRECIO_LTKG);
        $("#AGRICOLAprecioHaProducto_MC").val(producto.PRECIO_HA);
        $("#AGRICOLAobservacionesProducto_MC").val(producto.OBSERVACIONES);

        // Guardar valores en los campos ocultos
        $("#AGRICOLAidProductoMC").val(producto.IDPRODUCTO || "");
        $("#AGRICOLAidSubgrupoMC").val(producto.IDSUBGRUPO || "");

        // Cambiar el título del modal
        $("#AGRICOLAmodalProductoLabel_MC").html(
          '<i class="fas fa-edit mr-2"></i> Editar Producto'
        );

        // Mostrar el modal
        $("#AGRICOLAmodalProducto_MC").modal("show");
      } else {
        Swal.fire(
          "Error",
          "No se pudieron cargar los datos del producto",
          "error"
        );
      }
    },
    error: function (xhr, status, error) {
      Swal.fire(
        "Error",
        "Ocurrió un error al intentar cargar los datos: " + error,
        "error"
      );
    },
  });
}

// Función para eliminar un producto de Moscatel
function AGRICOLAeliminarProductoMoscatel(idProducto) {
  // Mostrar confirmación
  Swal.fire({
    title: "¿Está seguro?",
    text: "Esta acción eliminará el producto seleccionado. Esta acción no se puede deshacer.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Obtener el ID del programa actual
      const programaId = $("#AGRICOLAprogramaId_MC").val();

      // Realizar la eliminación mediante AJAX
      $.ajax({
        url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
        type: "DELETE",
        beforeSend: function () {
          // Mostrar indicador de carga
          Swal.fire({
            title: "Eliminando...",
            text: "Por favor espere",
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading();
            },
          });
        },
        success: function (response) {
          // Mostrar mensaje de éxito
          Swal.fire({
            title: "Eliminado",
            text: "El producto ha sido eliminado correctamente",
            icon: "success",
            confirmButtonText: "Aceptar",
          }).then(() => {
            // Refrescar la tabla de productos
            AGRICOLAcargarProductosPrograma_MC(programaId);
          });
        },
        error: function (xhr, status, error) {
          // Mostrar mensaje de error
          let errorMsg = "Ha ocurrido un error al eliminar el producto";

          if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          }

          Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error",
            confirmButtonText: "Aceptar",
          });

          console.error("Error al eliminar producto Moscatel:", error);
        },
      });
    }
  });
}

//============================================================================
// FUNCIONES PARA MOSTRAR LOS DETALLES DE LOS PRODUCTOS PARA SUGRA
//============================================================================

// Función para mostrar el modal de detalle de productos para SUGRA
function AGRICOLAmostrarDetallesProductos_SUGRA(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#AGRICOLAprogramaId_SUGRA").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_agricola_ajs/${idRegistro}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el registro correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del programa",
          "error"
        );
        return;
      }

      // Obtener los datos del registro
      const programa = response.data;

      // Actualizar los datos en el modal
      $("#AGRICOLAnombreProgramaDetalle_SUGRA").text(programa.NOMBRE);
      $("#AGRICOLAfechaInicioProgramaDetalle_SUGRA").text(programa.FECHA_INICIO);
      $("#AGRICOLAfechaFinProgramaDetalle_SUGRA").text(programa.FECHA_FIN);
      $("#AGRICOLAdescripcionProgramaDetalle_SUGRA").text(
        programa.DESCRIPCION || "Sin descripción"
      );
      $("#AGRICOLAsectorProgramaDetalle_SUGRA").text(programa.SECTOR || "no definido");
      $("#AGRICOLAloteProgramaDetalle_SUGRA").text(
        programa.LOTE_NOMBRE || "no definido"
      );

      // Mostrar el modal

      $("#AGRICOLAmodalDetalleProductos_SUGRA").modal("show");

      // Cargar los productos relacionados con este programa
      AGRICOLAcargarProductosPrograma_SUGRA(idRegistro);
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del programa";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos del programa SUGRA:", error);
    },
  });
}

// Función para cargar los productos relacionados con el programa para SUGRA
function AGRICOLAcargarProductosPrograma_SUGRA(idPrograma) {
  var mesesDetalle = [
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

  function AGRICOLAvalorMesCantidad_SUGRA(row, mes) {
    var k = mes + "_cantidad";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAvalorMesPrecio_SUGRA(row, mes) {
    var k = mes + "_precio";
    if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
      return parseFloat(row[k]).toFixed(2);
    }
    return "0.00";
  }

  function AGRICOLAtotalFilaProducto_SUGRA(row) {
    var suma = 0;
    mesesDetalle.forEach(function (m) {
      var k = m + "_precio";
      if (row[k] != null && row[k] !== "" && !isNaN(parseFloat(row[k]))) {
        suma += parseFloat(row[k]);
      }
    });
    if (suma > 0) {
      return "S/ " + suma.toFixed(2);
    }
    return "S/ 0.00";
  }

  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#AGRICOLAtablaDetalleProductos_SUGRA")) {
    $("#AGRICOLAtablaDetalleProductos_SUGRA").DataTable().clear().destroy();
  }

  var columnasDetalle = [
    {
      data: null,
      className: "text-center",
      orderable: false,
      render: function (data, type, row, meta) {
        return meta.row + 1;
      },
    },
    { data: "idproducto", className: "text-center" },
    { data: "descripcion", className: "text-left" },
  ];

  mesesDetalle.forEach(function (mes) {
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesCantidad_SUGRA(row, mes);
      },
    });
    columnasDetalle.push({
      data: null,
      className: "text-center",
      render: function (data, type, row) {
        return AGRICOLAvalorMesPrecio_SUGRA(row, mes);
      },
    });
  });

  columnasDetalle.push({
    data: null,
    className: "text-center",
    orderable: false,
    render: function (data, type, row) {
      return AGRICOLAtotalFilaProducto_SUGRA(row);
    },
  });

  columnasDetalle.push({
    data: null,
    className: "text-center text-nowrap",
    orderable: false,
    render: function (data, type, row) {
      var id = row.id;
      return (
        '<button type="button" class="btn btn-sm btn-info mr-1" title="Editar" onclick="AGRICOLAeditarProductoSugra(' +
        id +
        ')"><i class="fas fa-edit"></i></button>' +
        '<button type="button" class="btn btn-sm btn-danger" title="Eliminar" onclick="AGRICOLAeliminarProductoSugra(' +
        id +
        ')"><i class="fas fa-trash"></i></button>'
      );
    },
  });

  // Iniciar la tabla de productos con datos de la API
  $("#AGRICOLAtablaDetalleProductos_SUGRA").DataTable({
    responsive: false,
    scrollX: true,
    autoWidth: false,
    pageLength: 7,
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url:
        "/riego/api/suministro_agricola_ajs/?id_producto_agricola=" +
        encodeURIComponent(idPrograma),
      type: "GET",
      dataSrc: function (json) {
        if (!json) {
          return [];
        }
        if (json.error) {
          return [];
        }
        var rows = Array.isArray(json) ? json : json.data || [];
        $("#AGRICOLAtotalProductosProgramaDetalle_plantines_SUGRA").text(rows.length);
        var costoTotal = 0;
        rows.forEach(function (item) {
          var sumaMeses = 0;
          mesesDetalle.forEach(function (m) {
            var pk = m + "_precio";
            if (
              item[pk] != null &&
              item[pk] !== "" &&
              !isNaN(parseFloat(item[pk]))
            ) {
              sumaMeses += parseFloat(item[pk]);
            }
          });
          costoTotal += sumaMeses;
        });
        $("#AGRICOLAcostoTotalProgramaDetalle_SUGRA").text(
          "$ " + costoTotal.toFixed(2)
        );
        return rows;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        $("#AGRICOLAtablaDetalleProductos_SUGRA tbody").html(
          '<tr><td colspan="29" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
        );
      },
    },
    columns: columnasDetalle,
    createdRow: function (row, data, dataIndex) {
      $(row).addClass("programa-row");
      $(row).attr("data-id", data.id);
    },
  });
}

//============================================================================
// FUNCIONES PARA GUARDAR, EDITAR Y ELIMINAR PRODUCTOS - SUGRA
//============================================================================

// Función para guardar o editar un producto de SUGRA
function AGRICOLAguardarProductoSugra() {
  var programaId = $("#AGRICOLAprogramaId_SUGRA").val();
  var suministroPk = ($("#AGRICOLAproductoId_SUGRA").val() || "").trim();
  var esEdicion = suministroPk !== "";
  var idproducto = ($("#AGRICOLA_idproducto_sum_SUGRA").val() || "").trim();
  var descripcion = ($("#AGRICOLA_descripcion_sum_SUGRA").val() || "").trim();
  var precioUnitario = parseFloat($("#AGRICOLA_precio_unitario_sum_SUGRA").val());
  var idArea = parseInt($("#AGRICOLA_id_area_sum_SUGRA").val(), 10);
  var idTipo = parseInt($("#AGRICOLA_id_tipo_suministro_sum_SUGRA").val(), 10);

  if (!programaId) {
    Swal.fire("Error", "No se ha seleccionado el programa (cabecera).", "error");
    return false;
  }

  var formProducto = $("#AGRICOLAformProducto_SUGRA")[0];
  if (formProducto && !formProducto.checkValidity()) {
    formProducto.reportValidity();
    return false;
  }

  if (!idproducto || !descripcion) {
    Swal.fire("Error", "Seleccione un producto de la lista (descripción e ID).", "error");
    return false;
  }

  if (isNaN(precioUnitario) || precioUnitario <= 0) {
    Swal.fire("Error", "Indique un precio unitario válido mayor a 0.", "error");
    return false;
  }

  var mesesPayload = [
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

  var datosProducto = {
    idproducto: idproducto,
    descripcion: descripcion,
    precio_unitario: precioUnitario,
    id_area: isNaN(idArea) ? 11 : idArea,
    id_tipo_suministro: isNaN(idTipo) ? 1 : idTipo,
  };

  mesesPayload.forEach(function (mes) {
    var activo = $("#AGRICOLA_sum_SUGRA" + mes + "_switch").is(":checked");
    var c = activo ? parseFloat($("#AGRICOLA_sum_SUGRA" + mes + "_cantidad").val()) || 0 : 0;
    datosProducto[mes + "_cantidad"] = c;
  });

  if (!esEdicion) {
    datosProducto.IDPRODUCTO_AGRICOLA = parseInt(programaId, 10);
    if (isNaN(datosProducto.IDPRODUCTO_AGRICOLA)) {
      Swal.fire("Error", "ID de programa agrícola inválido.", "error");
      return false;
    }
  }

  var url = "/riego/api/suministro_agricola_ajs/";
  var metodo = "POST";
  if (esEdicion) {
    url = "/riego/api/suministro_agricola_ajs/" + encodeURIComponent(suministroPk) + "/";
    metodo = "PUT";
  }

  Swal.fire({
    title: esEdicion ? "Actualizando..." : "Guardando...",
    text: esEdicion
      ? "Por favor espere mientras se actualiza el suministro"
      : "Por favor espere mientras se guarda el suministro",
    allowOutsideClick: false,
    didOpen: function () {
      Swal.showLoading();
    },
  });

  $.ajax({
    url: url,
    type: metodo,
    contentType: "application/json",
    data: JSON.stringify(datosProducto),
    success: function () {
      Swal.close();
      Swal.fire({
        title: "¡Éxito!",
        text: esEdicion
          ? "El suministro ha sido actualizado correctamente"
          : "El suministro ha sido guardado correctamente",
        icon: "success",
        confirmButtonText: "Aceptar",
      });
      $("#AGRICOLAmodalProducto_SUGRA").modal("hide");
      AGRICOLAcargarProductosPrograma_SUGRA(programaId);
      return true;
    },
    error: function (xhr, status, error) {
      console.error(
        "Error al " + (esEdicion ? "actualizar" : "guardar") + " suministro Sweet Globe:",
        error
      );
      Swal.close();
      var errorMsg =
        "Ha ocurrido un error al " + (esEdicion ? "actualizar" : "guardar") + " el suministro";
      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }
      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      return false;
    },
  });
}

function AGRICOLAeditarProductoSugra(idProducto) {
  // Realizar una petición AJAX para obtener los datos del producto
  $.ajax({
    url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
    type: "GET",
    success: function (response) {
      if (response && response.data) {
        // Obtener los datos del producto
        const producto = response.data;

        // Llenar el formulario con los datos
        $("#AGRICOLAproductoId_SUGRA").val(idProducto);
        $("#AGRICOLAsubGrupoProducto_SUGRA").val(producto.SUBGRUPO);
        $("#AGRICOLAnombreProducto_SUGRA").val(producto.PRODUCTO);
        $("#AGRICOLAmateriaActivaProducto_SUGRA").val(producto.MATERIA_SUGRATIVA);
        $("#AGRICOLAnecesidadProducto_SUGRA").val(producto.NECESIDADXHA);
        $("#AGRICOLAunidadNecesidadProducto_SUGRA").val(producto.UND);
        $("#AGRICOLAprecioProducto_SUGRA").val(producto.PRECIO_LTKG);
        $("#AGRICOLAprecioHaProducto_SUGRA").val(producto.PRECIO_HA);
        $("#AGRICOLAobservacionesProducto_SUGRA").val(producto.OBSERVACIONES);

        // Agregar valores a los campos ocultos
        $("#AGRICOLAidProductoSUGRA").val(producto.IDPRODUCTO || "");
        $("#AGRICOLAidSubgrupoSUGRA").val(producto.IDSUBGRUPO || "");

        // Cambiar el título del modal
        $("#AGRICOLAmodalProductoLabel_SUGRA").text("Editar Producto");

        // Mostrar el modal
        $("#AGRICOLAmodalProducto_SUGRA").modal("show");
      } else {
        Swal.fire(
          "Error",
          "No se pudieron cargar los datos del producto",
          "error"
        );
      }
    },
    error: function (xhr, status, error) {
      Swal.fire(
        "Error",
        "Ocurrió un error al intentar cargar los datos: " + error,
        "error"
      );
    },
  });
}

function AGRICOLAeliminarProductoSugra(idProducto) {
  // Mostrar confirmación
  Swal.fire({
    title: "¿Está seguro?",
    text: "Esta acción eliminará el producto seleccionado. Esta acción no se puede deshacer.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      // Obtener el ID del programa actual
      const programaId = $("#AGRICOLAprogramaId_SUGRA").val();

      // Realizar la eliminación mediante AJAX
      $.ajax({
        url: `/riego/api/suministro_agricola_ajs/${idProducto}/`,
        type: "DELETE",
        beforeSend: function () {
          // Mostrar indicador de carga
          Swal.fire({
            title: "Eliminando...",
            text: "Por favor espere",
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading();
            },
          });
        },
        success: function (response) {
          // Mostrar mensaje de éxito
          Swal.fire({
            title: "Eliminado",
            text: "El producto ha sido eliminado correctamente",
            icon: "success",
            confirmButtonText: "Aceptar",
          }).then(() => {
            // Refrescar la tabla de productos
            AGRICOLAcargarProductosPrograma_SUGRA(programaId);
          });
        },
        error: function (xhr, status, error) {
          // Mostrar mensaje de error
          let errorMsg = "Ha ocurrido un error al eliminar el producto";

          if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          }

          Swal.fire({
            title: "Error",
            text: errorMsg,
            icon: "error",
            confirmButtonText: "Aceptar",
          });

          console.error("Error al eliminar producto:", error);
        },
      });
    }
  });
}

// Sweet Globe — autocompletado de producto (API agrícolas)
function AGRICOLAbuscarproducto_SG() {
  AGRICOLA_inicializarAutocompleteSuministroSG();
}

function AGRICOLAinitEventosFormularioProducto_SG() {
  AGRICOLA_inicializarAutocompleteSuministroSG();

  $("#AGRICOLA_precio_unitario_sum")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministroSG();
    });

  $("input[id^='AGRICOLA_sum_'][id$='_switch']")
    .off("change.sgSum")
    .on("change.sgSum", function () {
      var mes = this.id.replace(/^AGRICOLA_sum_/, "").replace(/_switch$/, "");
      var $cant = $("#AGRICOLA_sum_" + mes + "_cantidad");
      if ($(this).is(":checked")) {
        $cant.prop("disabled", false);
      } else {
        $cant.prop("disabled", true).val("");
      }
      AGRICOLA_calcularTotalesSuministroSG();
    });

  $(".AGRICOLA_sum_cantidad_mes")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministroSG();
    });

  $("#AGRICOLA_aplicar_cantidad_masiva_sum")
    .off("click.sgSum")
    .on("click.sgSum", function () {
      var cantidad = $("#AGRICOLA_cantidad_masiva_sum").val();
      if (!cantidad || parseFloat(cantidad) <= 0) {
        Swal.fire({
          icon: "error",
          title: "Cantidad inválida",
          text: "Por favor, ingrese una cantidad válida mayor a 0",
        });
        return;
      }
      Swal.fire({
        title: "¿Aplicar a todos los meses?",
        text:
          "Se aplicará la cantidad de " +
          cantidad +
          " a todos los meses. ¿Desea continuar?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, aplicar",
        cancelButtonText: "Cancelar",
      }).then(function (result) {
        if (!result.isConfirmed) {
          return;
        }
        var mesesMas = [
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
        mesesMas.forEach(function (mes) {
          $("#AGRICOLA_sum_" + mes + "_switch").prop("checked", true);
          $("#AGRICOLA_sum_" + mes + "_cantidad")
            .prop("disabled", false)
            .val(cantidad);
        });
        AGRICOLA_calcularTotalesSuministroSG();
      });
    });

  $("#AGRICOLAbtnGuardarProducto")
    .off("click.sgSumGuardar")
    .on("click.sgSumGuardar", function () {
      AGRICOLAguardarProductoSweetGlobe();
    });
}

function AGRICOLAresetearFormularioProducto() {
  var form = $("#AGRICOLAformProducto");
  if (form.length && form[0]) {
    form[0].reset();
  }
  $("#AGRICOLAproductoId").val("");
  $("#AGRICOLA_idproducto_sum").val("");
  $("#AGRICOLA_descripcion_sum").val("");
  $("#AGRICOLA_precio_unitario_sum")
    .val("0.00")
    .prop("readonly", false)
    .attr("placeholder", "");
  $("#AGRICOLA_cantidad_masiva_sum").val("");
  var mesesReset = [
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
  mesesReset.forEach(function (mes) {
    $("#AGRICOLA_sum_" + mes + "_switch").prop("checked", false);
    $("#AGRICOLA_sum_" + mes + "_cantidad").prop("disabled", true).val("");
  });
  AGRICOLA_destruirAutocompleteSuministroSiExiste();
  $("#AGRICOLAmodalProductoLabel").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar suministro al programa'
  );
  AGRICOLA_calcularTotalesSuministroSG();
}

// Función para buscar productos para Autumn Crisp
function AGRICOLAbuscarproducto_AC() {
  let timeoutId;
  let sugerenciasContainer;

  // Desactivar eventos previos para evitar duplicados
  $("#AGRICOLAnombreProducto_AC").off("input");

  // Crear el contenedor de sugerencias si no existe
  if (!$("#sugerencias-producto-container-AC").length) {
    $("body").append(
      '<div id="sugerencias-producto-container-AC" class="sugerencias-container"></div>'
    );
    sugerenciasContainer = $("#sugerencias-producto-container-AC");

    // Aplicar estilos al contenedor
    sugerenciasContainer.css({
      position: "absolute",
      width: "auto",
      "max-height": "250px",
      "overflow-y": "auto",
      "background-color": "#fff",
      border: "1px solid #ddd",
      "border-radius": "4px",
      "box-shadow": "0 2px 5px rgba(0,0,0,0.2)",
      "z-index": "99999", // Valor muy alto para asegurar que esté por encima de todo
      display: "none",
    });

    // Cerrar sugerencias al hacer clic fuera de ellas
    $(document).on("click", function (e) {
      if (
        !$(e.target).closest(
          "#sugerencias-producto-container-AC, #AGRICOLAnombreProducto_AC"
        ).length
      ) {
        sugerenciasContainer.hide();
      }
    });
  } else {
    sugerenciasContainer = $("#sugerencias-producto-container-AC");
  }

  // Función para posicionar el contenedor de sugerencias
  function AGRICOLAposicionarSugerencias() {
    const input = $("#AGRICOLAnombreProducto_AC");
    const inputPos = input.offset();
    sugerenciasContainer.css({
      top: inputPos.top + input.outerHeight() + "px",
      left: inputPos.left + "px",
      width: input.outerWidth() + "px",
    });
  }

  // Asociar evento de entrada al campo de producto
  $("#AGRICOLAnombreProducto_AC").on("input", function () {
    const query = $(this).val();

    // Limpiar el timeout anterior
    clearTimeout(timeoutId);

    // Si el input está vacío, ocultar sugerencias
    if (query.trim() === "") {
      sugerenciasContainer.hide();
      return;
    }

    // Establecer un nuevo timeout para evitar demasiadas peticiones
    timeoutId = setTimeout(function () {
      // Mostrar indicador de carga
      sugerenciasContainer.html(
        '<div class="p-2 text-center"><i class="fas fa-spinner fa-spin mr-2"></i>Buscando...</div>'
      );
      AGRICOLAposicionarSugerencias();
      sugerenciasContainer.show();

      // Preparar los parámetros de búsqueda
      const params = {
        idgrupo: 2400, // Valor fijo según requerimiento
      };

      // Determinar si la consulta es un ID o descripción
      if (/^\d+$/.test(query)) {
        // Es un número, buscar por ID de producto
        params.idproducto = query;
      } else {
        // Es texto, buscar por descripción
        params.descripcion = query;
      }

      // Asegurarnos de que el parámetro se envíe correctamente
      if (params.descripcion === "") {
        delete params.descripcion;
      }
      if (params.idproducto === "") {
        delete params.idproducto;
      }

      // Realizar la petición AJAX
      $.ajax({
        url: "/aplicaciones/productos/",
        type: "GET",
        data: params,
        success: function (response) {
          if (response.data && response.data.length > 0) {
            AGRICOLAmostrarSugerenciasProductos_AC(response.data);
          } else {
            sugerenciasContainer.html(
              '<div class="p-2 text-center text-muted">No se encontraron productos</div>'
            );
          }
        },
        error: function (xhr, status, error) {
          sugerenciasContainer.html(
            '<div class="p-2 text-center text-danger">Error al buscar productos</div>'
          );
          console.error("Error al buscar productos para AC:", error);
        },
      });
    }, 300); // 300ms de debounce
  });

  // Función para mostrar las sugerencias de productos
  function AGRICOLAmostrarSugerenciasProductos_AC(productos) {
    sugerenciasContainer.empty();

    if (productos.length === 0) {
      sugerenciasContainer.html(
        '<div class="p-2 text-center text-muted">No se encontraron productos</div>'
      );
      return;
    }

    const ul = $("<ul>").addClass("list-unstyled mb-0");

    // Crear elementos de lista para cada producto
    productos.forEach(function (producto) {
      // Usar las propiedades correctas según la respuesta de la API
      const idProducto = producto.IDPRODUCTO || "";
      const nombreProducto = producto.DESCRIPCION || producto.PRODUCTO || "";
      const materiaActiva =
        producto.MATERIA_ACTIVA || producto.MATERIAACTIVA || "Sin información";
      const subgrupo =
        producto.DESCRIPCION_SUBGRUPO ||
        producto.SUBGRUPO ||
        producto.SUBGRUPOPROGRAMA ||
        "-";
      const precio = producto.PRECIO || producto.ultimo_precio || "0.00";
      const idMedida = producto.IDMEDIDA ? producto.IDMEDIDA.trim() : "-";

      const li = $("<li>").addClass("sugerencia-item p-2 border-bottom");

      li.html(`
        <div class="d-flex align-items-center">
          <div>
            <strong>${nombreProducto}</strong>
            <br>
            <small class="text-muted">${materiaActiva} - ${subgrupo}</small>
            <br>
            <small class="text-info">Unidad: ${idMedida}</small>
          </div>
          <span class="badge badge-primary ml-auto">$${
            typeof precio === "number" ? precio.toFixed(2) : precio
          }</span>
        </div>
      `);

      // Agregar evento click para seleccionar el producto
      li.on("click", function () {
        AGRICOLAseleccionarProducto_AC(producto);
        sugerenciasContainer.hide();
      });

      // Agregar efecto hover
      li.hover(
        function () {
          $(this).addClass("bg-light");
        },
        function () {
          $(this).removeClass("bg-light");
        }
      );

      ul.append(li);
    });

    sugerenciasContainer.append(ul);
    AGRICOLAposicionarSugerencias();
  }

  // Función para seleccionar un producto
  function AGRICOLAseleccionarProducto_AC(producto) {
    // Usar las propiedades correctas según la respuesta de la API
    const idProducto = producto.IDPRODUCTO || "";
    const nombreProducto = producto.DESCRIPCION || producto.PRODUCTO || "";
    const materiaActiva =
      producto.MATERIA_ACTIVA || producto.MATERIAACTIVA || "";
    const subgrupo =
      producto.DESCRIPCION_SUBGRUPO ||
      producto.SUBGRUPO ||
      producto.SUBGRUPOPROGRAMA ||
      "";
    const idSubgrupo =
      producto.IDSUBGRUPO || producto.IDSUBGRUPOPROGRAMA || subgrupo;
    const precio = producto.PRECIO || producto.ultimo_precio || 0;
    const idMedida = producto.IDMEDIDA ? producto.IDMEDIDA.trim() : "";

    // Establecer valores en los campos
    $("#AGRICOLAnombreProducto_AC").val(nombreProducto);
    $("#AGRICOLAsubGrupoProducto_AC").val(subgrupo);
    $("#AGRICOLAmateriaActivaProducto_AC").val(materiaActiva);
    $("#AGRICOLAprecioProducto_AC").val(
      typeof precio === "number" ? precio.toFixed(2) : precio
    );

    // Establecer valores en los campos ocultos
    $("#AGRICOLAidProductoAC").val(idProducto);
    $("#AGRICOLAidSubgrupoAC").val(idSubgrupo);

    // Configurar la unidad de medida según el producto
    if (idMedida) {
      const unidadFormateada = idMedida.trim().toUpperCase();
      if (unidadFormateada.includes("LT") || unidadFormateada.includes("L")) {
        $("#AGRICOLAunidadNecesidadProducto_AC").val("LT");
      } else if (unidadFormateada.includes("KG")) {
        $("#AGRICOLAunidadNecesidadProducto_AC").val("kg");
      }
    }

    // Calcular el precio por hectárea si ya hay un valor en necesidad
    AGRICOLAcalcularPrecioHa_AC();

    // Feedback visual
    $("#AGRICOLAnombreProducto_AC")
      .addClass("is-valid")
      .parent()
      .append(
        '<small class="text-success product-selected-message">Producto seleccionado correctamente</small>'
      );

    // Eliminar mensaje después de 2 segundos
    setTimeout(function () {
      $(".product-selected-message").fadeOut(500, function () {
        $(this).remove();
        $("#AGRICOLAnombreProducto_AC").removeClass("is-valid");
      });
    }, 2000);
  }

  // Inicializar la posición del contenedor de sugerencias al cargar
  $(window).on("resize", AGRICOLAposicionarSugerencias);
}

// Función para calcular el precio por hectárea para Autumn Crisp
function AGRICOLAcalcularPrecioHa_AC() {
  const necesidad = parseFloat($("#AGRICOLAnecesidadProducto_AC").val()) || 0;
  const precioLtKg = parseFloat($("#AGRICOLAprecioProducto_AC").val()) || 0;
  const precioHa = necesidad * precioLtKg;
  $("#AGRICOLAprecioHaProducto_AC").val(precioHa.toFixed(2));
}

// Función para inicializar los eventos del formulario de producto para Autumn Crisp
function AGRICOLAinitEventosFormularioProducto_AC() {
  AGRICOLA_inicializarAutocompleteSuministro_AC();

  $("#AGRICOLA_precio_unitario_sum_AC")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministro_AC();
    });

  $("input[id^='AGRICOLA_sum_AC'][id$='_switch']")
    .off("change.sgSum")
    .on("change.sgSum", function () {
      var mes = this.id.replace(/^AGRICOLA_sum_AC/, "").replace(/_switch$/, "");
      var $cant = $("#AGRICOLA_sum_AC" + mes + "_cantidad");
      if ($(this).is(":checked")) {
        $cant.prop("disabled", false);
      } else {
        $cant.prop("disabled", true).val("");
      }
      AGRICOLA_calcularTotalesSuministro_AC();
    });

  $(".AGRICOLA_sum_cantidad_mes_AC")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministro_AC();
    });

  $("#AGRICOLA_aplicar_cantidad_masiva_sum_AC")
    .off("click.sgSum")
    .on("click.sgSum", function () {
      var cantidad = $("#AGRICOLA_cantidad_masiva_sum_AC").val();
      if (!cantidad || parseFloat(cantidad) <= 0) {
        Swal.fire({
          icon: "error",
          title: "Cantidad inválida",
          text: "Por favor, ingrese una cantidad válida mayor a 0",
        });
        return;
      }
      Swal.fire({
        title: "¿Aplicar a todos los meses?",
        text:
          "Se aplicará la cantidad de " +
          cantidad +
          " a todos los meses. ¿Desea continuar?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, aplicar",
        cancelButtonText: "Cancelar",
      }).then(function (result) {
        if (!result.isConfirmed) {
          return;
        }
        var mesesMas = [
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
        mesesMas.forEach(function (mes) {
          $("#AGRICOLA_sum_AC" + mes + "_switch").prop("checked", true);
          $("#AGRICOLA_sum_AC" + mes + "_cantidad")
            .prop("disabled", false)
            .val(cantidad);
        });
        AGRICOLA_calcularTotalesSuministro_AC();
      });
    });

  $("#AGRICOLAbtnGuardarProducto_AC")
    .off("click.sgSumGuardar")
    .on("click.sgSumGuardar", function () {
      AGRICOLAguardarProductoAutumnCrisp();
    });
}


function AGRICOLA_calcularTotalesSuministro_AC() {
  var pu = parseFloat($("#AGRICOLA_precio_unitario_sum_AC").val()) || 0;
  var cantTotal = 0;
  var precioTotal = 0;
  $(".AGRICOLA_sum_cantidad_mes_AC").each(function () {
    var idEl = this.id;
    var mes = idEl.replace(/^AGRICOLA_sum_AC/, "").replace(/_cantidad$/, "");
    if ($("#AGRICOLA_sum_AC" + mes + "_switch").is(":checked")) {
      var c = parseFloat($(this).val()) || 0;
      cantTotal += c;
      precioTotal += c * pu;
    }
  });
  $("#AGRICOLA_cantidad_total_sum_AC").text(cantTotal.toFixed(2));
  $("#AGRICOLA_precio_total_sum_AC").text("S/ " + precioTotal.toFixed(2));
}

// Función para abrir el modal de nuevo producto para Autumn Crisp
function AGRICOLAabrirModalNuevoProducto_AC(idPrograma) {
  AGRICOLAresetearFormularioProducto_AC();
  $("#AGRICOLAprogramaId_AC").val(idPrograma);
  $("#AGRICOLAmodalProducto_AC").modal("show");
  AGRICOLAinitEventosFormularioProducto_AC();
}

// Función para resetear el formulario de productos para Autumn Crisp
function AGRICOLAresetearFormularioProducto_AC() {
  var form = $("#AGRICOLAformProducto_AC");
  if (form.length && form[0]) {
    form[0].reset();
  }
  $("#AGRICOLAproductoId_AC").val("");
  $("#AGRICOLA_idproducto_sum_AC").val("");
  $("#AGRICOLA_descripcion_sum_AC").val("");
  $("#AGRICOLA_precio_unitario_sum_AC")
    .val("0.00")
    .prop("readonly", false)
    .attr("placeholder", "");
  $("#AGRICOLA_cantidad_masiva_sum_AC").val("");
  var mesesReset = [
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
  mesesReset.forEach(function (mes) {
    $("#AGRICOLA_sum_AC" + mes + "_switch").prop("checked", false);
    $("#AGRICOLA_sum_AC" + mes + "_cantidad").prop("disabled", true).val("");
  });
  AGRICOLA_destruirAutocompleteSuministroSiExiste_AC();
  $("#AGRICOLAmodalProductoLabel_AC").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar suministro al programa'
  );
  AGRICOLA_calcularTotalesSuministro_AC();
}

function AGRICOLA_destruirAutocompleteSuministroSiExiste_AC() {
  var $d = $("#AGRICOLA_descripcion_sum_AC");
  if ($d.length && $d.data("ui-autocomplete")) {
    $d.autocomplete("destroy");
  }
}

// Función para buscar productos para Moscatel
function AGRICOLAbuscarproducto_MC() {
  let timeoutId;
  let sugerenciasContainer;

  // Desactivar eventos previos para evitar duplicados
  $("#AGRICOLAnombreProducto_MC").off("input");

  // Crear el contenedor de sugerencias si no existe
  if (!$("#sugerencias-producto-container-MC").length) {
    $("body").append(
      '<div id="sugerencias-producto-container-MC" class="sugerencias-container"></div>'
    );
    sugerenciasContainer = $("#sugerencias-producto-container-MC");

    // Aplicar estilos al contenedor
    sugerenciasContainer.css({
      position: "absolute",
      width: "auto",
      "max-height": "250px",
      "overflow-y": "auto",
      "background-color": "#fff",
      border: "1px solid #ddd",
      "border-radius": "4px",
      "box-shadow": "0 2px 5px rgba(0,0,0,0.2)",
      "z-index": "99999", // Valor muy alto para asegurar que esté por encima de todo
      display: "none",
    });

    // Cerrar sugerencias al hacer clic fuera de ellas
    $(document).on("click", function (e) {
      if (
        !$(e.target).closest(
          "#sugerencias-producto-container-MC, #AGRICOLAnombreProducto_MC"
        ).length
      ) {
        sugerenciasContainer.hide();
      }
    });
  } else {
    sugerenciasContainer = $("#sugerencias-producto-container-MC");
  }

  // Función para posicionar el contenedor de sugerencias
  function AGRICOLAposicionarSugerencias() {
    const input = $("#AGRICOLAnombreProducto_MC");
    const inputPos = input.offset();
    sugerenciasContainer.css({
      top: inputPos.top + input.outerHeight() + "px",
      left: inputPos.left + "px",
      width: input.outerWidth() + "px",
    });
  }

  // Asociar evento de entrada al campo de producto
  $("#AGRICOLAnombreProducto_MC").on("input", function () {
    const query = $(this).val();

    // Limpiar el timeout anterior
    clearTimeout(timeoutId);

    // Si el input está vacío, ocultar sugerencias
    if (query.trim() === "") {
      sugerenciasContainer.hide();
      return;
    }

    // Establecer un nuevo timeout para evitar demasiadas peticiones
    timeoutId = setTimeout(function () {
      // Mostrar indicador de carga
      sugerenciasContainer.html(
        '<div class="p-2 text-center"><i class="fas fa-spinner fa-spin mr-2"></i>Buscando...</div>'
      );
      AGRICOLAposicionarSugerencias();
      sugerenciasContainer.show();

      // Preparar los parámetros de búsqueda
      const params = {
        idgrupo: 2400, // Valor fijo según requerimiento
      };

      // Determinar si la consulta es un ID o descripción
      if (/^\d+$/.test(query)) {
        // Es un número, buscar por ID de producto
        params.idproducto = query;
      } else {
        // Es texto, buscar por descripción
        params.descripcion = query;
      }

      // Asegurarnos de que el parámetro se envíe correctamente
      if (params.descripcion === "") {
        delete params.descripcion;
      }
      if (params.idproducto === "") {
        delete params.idproducto;
      }

      // Realizar la petición AJAX
      $.ajax({
        url: "/aplicaciones/productos/",
        type: "GET",
        data: params,
        success: function (response) {
          if (response.data && response.data.length > 0) {
            AGRICOLAmostrarSugerenciasProductos_MC(response.data);
          } else {
            sugerenciasContainer.html(
              '<div class="p-2 text-center text-muted">No se encontraron productos</div>'
            );
          }
        },
        error: function (xhr, status, error) {
          sugerenciasContainer.html(
            '<div class="p-2 text-center text-danger">Error al buscar productos</div>'
          );
          console.error("Error al buscar productos para MC:", error);
        },
      });
    }, 300); // 300ms de debounce
  });

  // Función para mostrar las sugerencias de productos
  function AGRICOLAmostrarSugerenciasProductos_MC(productos) {
    sugerenciasContainer.empty();

    if (productos.length === 0) {
      sugerenciasContainer.html(
        '<div class="p-2 text-center text-muted">No se encontraron productos</div>'
      );
      return;
    }

    const ul = $("<ul>").addClass("list-unstyled mb-0");

    // Crear elementos de lista para cada producto
    productos.forEach(function (producto) {
      // Usar las propiedades correctas según la respuesta de la API
      const idProducto = producto.IDPRODUCTO || "";
      const nombreProducto = producto.DESCRIPCION || producto.PRODUCTO || "";
      const materiaActiva =
        producto.MATERIA_ACTIVA || producto.MATERIAACTIVA || "Sin información";
      const subgrupo =
        producto.DESCRIPCION_SUBGRUPO ||
        producto.SUBGRUPO ||
        producto.SUBGRUPOPROGRAMA ||
        "-";
      const precio = producto.PRECIO || producto.ultimo_precio || "0.00";
      const idMedida = producto.IDMEDIDA ? producto.IDMEDIDA.trim() : "-";

      const li = $("<li>").addClass("sugerencia-item p-2 border-bottom");

      li.html(`
        <div class="d-flex align-items-center">
          <div>
            <strong>${nombreProducto}</strong>
            <br>
            <small class="text-muted">${materiaActiva} - ${subgrupo}</small>
            <br>
            <small class="text-info">Unidad: ${idMedida}</small>
          </div>
          <span class="badge badge-primary ml-auto">$${
            typeof precio === "number" ? precio.toFixed(2) : precio
          }</span>
        </div>
      `);

      // Agregar evento click para seleccionar el producto
      li.on("click", function () {
        AGRICOLAseleccionarProducto_MC(producto);
        sugerenciasContainer.hide();
      });

      // Agregar efecto hover
      li.hover(
        function () {
          $(this).addClass("bg-light");
        },
        function () {
          $(this).removeClass("bg-light");
        }
      );

      ul.append(li);
    });

    sugerenciasContainer.append(ul);
    AGRICOLAposicionarSugerencias();
  }

  // Función para seleccionar un producto
  function AGRICOLAseleccionarProducto_MC(producto) {
    // Usar las propiedades correctas según la respuesta de la API
    const idProducto = producto.IDPRODUCTO || "";
    const nombreProducto = producto.DESCRIPCION || producto.PRODUCTO || "";
    const materiaActiva =
      producto.MATERIA_ACTIVA || producto.MATERIAACTIVA || "";
    const subgrupo =
      producto.DESCRIPCION_SUBGRUPO ||
      producto.SUBGRUPO ||
      producto.SUBGRUPOPROGRAMA ||
      "";
    const idSubgrupo =
      producto.IDSUBGRUPO || producto.IDSUBGRUPOPROGRAMA || subgrupo;
    const precio = producto.PRECIO || producto.ultimo_precio || 0;
    const idMedida = producto.IDMEDIDA ? producto.IDMEDIDA.trim() : "";

    // Establecer valores en los campos
    $("#AGRICOLAnombreProducto_MC").val(nombreProducto);
    $("#AGRICOLAsubGrupoProducto_MC").val(subgrupo);
    $("#AGRICOLAmateriaActivaProducto_MC").val(materiaActiva);
    $("#AGRICOLAprecioProducto_MC").val(
      typeof precio === "number" ? precio.toFixed(2) : precio
    );

    // Establecer valores en los campos ocultos
    $("#AGRICOLAidProductoMC").val(idProducto);
    $("#AGRICOLAidSubgrupoMC").val(idSubgrupo);

    // Configurar la unidad de medida según el producto
    if (idMedida) {
      const unidadFormateada = idMedida.trim().toUpperCase();
      if (unidadFormateada.includes("LT") || unidadFormateada.includes("L")) {
        $("#AGRICOLAunidadNecesidadProducto_MC").val("LT");
      } else if (unidadFormateada.includes("KG")) {
        $("#AGRICOLAunidadNecesidadProducto_MC").val("kg");
      }
    }

    // Calcular el precio por hectárea si ya hay un valor en necesidad
    AGRICOLAcalcularPrecioHa_MC();

    // Feedback visual
    $("#AGRICOLAnombreProducto_MC")
      .addClass("is-valid")
      .parent()
      .append(
        '<small class="text-success product-selected-message">Producto seleccionado correctamente</small>'
      );

    // Eliminar mensaje después de 2 segundos
    setTimeout(function () {
      $(".product-selected-message").fadeOut(500, function () {
        $(this).remove();
        $("#AGRICOLAnombreProducto_MC").removeClass("is-valid");
      });
    }, 2000);
  }

  // Inicializar la posición del contenedor de sugerencias al cargar
  $(window).on("resize", AGRICOLAposicionarSugerencias);
}

// Función para calcular el precio por hectárea para Moscatel
function AGRICOLAcalcularPrecioHa_MC() {
  const necesidad = parseFloat($("#AGRICOLAnecesidadProducto_MC").val()) || 0;
  const precioLtKg = parseFloat($("#AGRICOLAprecioProducto_MC").val()) || 0;
  const precioHa = necesidad * precioLtKg;
  $("#AGRICOLAprecioHaProducto_MC").val(precioHa.toFixed(2));
}

// Función para inicializar los eventos del formulario de producto para Moscatel
function AGRICOLAinitEventosFormularioProducto_MC() {
  AGRICOLA_inicializarAutocompleteSuministro_MC();

  $("#AGRICOLA_precio_unitario_sum_MC")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministro_MC();
    });

  $("input[id^='AGRICOLA_sum_MC'][id$='_switch']")
    .off("change.sgSum")
    .on("change.sgSum", function () {
      var mes = this.id.replace(/^AGRICOLA_sum_MC/, "").replace(/_switch$/, "");
      var $cant = $("#AGRICOLA_sum_MC" + mes + "_cantidad");
      if ($(this).is(":checked")) {
        $cant.prop("disabled", false);
      } else {
        $cant.prop("disabled", true).val("");
      }
      AGRICOLA_calcularTotalesSuministro_MC();
    });

  $(".AGRICOLA_sum_cantidad_mes_MC")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministro_MC();
    });

  $("#AGRICOLA_aplicar_cantidad_masiva_sum_MC")
    .off("click.sgSum")
    .on("click.sgSum", function () {
      var cantidad = $("#AGRICOLA_cantidad_masiva_sum_MC").val();
      if (!cantidad || parseFloat(cantidad) <= 0) {
        Swal.fire({
          icon: "error",
          title: "Cantidad inválida",
          text: "Por favor, ingrese una cantidad válida mayor a 0",
        });
        return;
      }
      Swal.fire({
        title: "¿Aplicar a todos los meses?",
        text:
          "Se aplicará la cantidad de " +
          cantidad +
          " a todos los meses. ¿Desea continuar?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, aplicar",
        cancelButtonText: "Cancelar",
      }).then(function (result) {
        if (!result.isConfirmed) {
          return;
        }
        var mesesMas = [
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
        mesesMas.forEach(function (mes) {
          $("#AGRICOLA_sum_MC" + mes + "_switch").prop("checked", true);
          $("#AGRICOLA_sum_MC" + mes + "_cantidad")
            .prop("disabled", false)
            .val(cantidad);
        });
        AGRICOLA_calcularTotalesSuministro_MC();
      });
    });

  $("#AGRICOLAbtnGuardarProducto_MC")
    .off("click.sgSumGuardar")
    .on("click.sgSumGuardar", function () {
      AGRICOLAguardarProductoMoscatel();
    });
}

// Función para abrir el modal de nuevo producto para Moscatel
function AGRICOLAabrirModalNuevoProducto_MC(idPrograma) {
  AGRICOLAresetearFormularioProducto_MC();
  $("#AGRICOLAprogramaId_MC").val(idPrograma);
  $("#AGRICOLAmodalProducto_MC").modal("show");
  AGRICOLAinitEventosFormularioProducto_MC();
}

// Función para resetear el formulario de productos para Moscatel
function AGRICOLAresetearFormularioProducto_MC() {
  var form = $("#AGRICOLAformProducto_MC");
  if (form.length && form[0]) {
    form[0].reset();
  }
  $("#AGRICOLAproductoId_MC").val("");
  $("#AGRICOLA_idproducto_sum_MC").val("");
  $("#AGRICOLA_descripcion_sum_MC").val("");
  $("#AGRICOLA_precio_unitario_sum_MC")
    .val("0.00")
    .prop("readonly", false)
    .attr("placeholder", "");
  $("#AGRICOLA_cantidad_masiva_sum_MC").val("");
  var mesesReset = [
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
  mesesReset.forEach(function (mes) {
    $("#AGRICOLA_sum_MC" + mes + "_switch").prop("checked", false);
    $("#AGRICOLA_sum_MC" + mes + "_cantidad").prop("disabled", true).val("");
  });
  AGRICOLA_destruirAutocompleteSuministroSiExiste_MC();
  $("#AGRICOLAmodalProductoLabel_MC").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar suministro al programa'
  );
  AGRICOLA_calcularTotalesSuministro_MC();
}

function AGRICOLA_destruirAutocompleteSuministroSiExiste_MC() {
  var $d = $("#AGRICOLA_descripcion_sum_MC");
  if ($d.length && $d.data("ui-autocomplete")) {
    $d.autocomplete("destroy");
  }
}

function AGRICOLA_calcularTotalesSuministro_MC() {
  var pu = parseFloat($("#AGRICOLA_precio_unitario_sum_MC").val()) || 0;
  var cantTotal = 0;
  var precioTotal = 0;
  $(".AGRICOLA_sum_cantidad_mes_MC").each(function () {
    var idEl = this.id;
    var mes = idEl.replace(/^AGRICOLA_sum_MC/, "").replace(/_cantidad$/, "");
    if ($("#AGRICOLA_sum_MC" + mes + "_switch").is(":checked")) {
      var c = parseFloat($(this).val()) || 0;
      cantTotal += c;
      precioTotal += c * pu;
    }
  });
  $("#AGRICOLA_cantidad_total_sum_MC").text(cantTotal.toFixed(2));
  $("#AGRICOLA_precio_total_sum_MC").text("S/ " + precioTotal.toFixed(2));
}

function AGRICOLA_inicializarAutocompleteSuministro_MC() {
  AGRICOLA_destruirAutocompleteSuministroSiExiste();
  $("#AGRICOLA_descripcion_sum_MC").autocomplete({
    minLength: 2,
    source: function (request, response) {
      $.ajax({
        url: "/riego/api_productos_agricolas_uva1/",
        dataType: "json",
        data: { q: request.term },
        success: function (data) {
          if (!data || data.error) {
            response([]);
            return;
          }
          var arr = Array.isArray(data) ? data : [];
          var results = $.map(arr, function (item) {
            var up = parseFloat(item.ultimo_precio) || 0;
            return {
              label: item.value,
              value: item.value,
              id: item.id,
              ultimo_precio: up,
              sin_precio_historico: up === 0,
            };
          });
          response(results);
        },
        error: function () {
          response([]);
        },
      });
    },
    select: function (event, ui) {
      $("#AGRICOLA_idproducto_sum_MC").val(ui.item.id);
      if (ui.item.sin_precio_historico) {
        $("#AGRICOLA_precio_unitario_sum_MC")
          .val("")
          .prop("readonly", false)
          .attr("placeholder", "Ingrese precio unitario");
        Swal.fire({
          title: "Sin precio histórico",
          text: "Ingrese manualmente el precio unitario.",
          icon: "info",
        });
      } else {
        $("#AGRICOLA_precio_unitario_sum_MC")
          .val(ui.item.ultimo_precio.toFixed(2))
          .prop("readonly", true)
          .attr("placeholder", "");
      }
      AGRICOLA_calcularTotalesSuministroSG();
    },
  });
}


// Función para posicionar el contenedor de sugerencias (separada para mayor claridad)
function AGRICOLAposicionarSugerencias_SUGRA() {
  const input = $("#AGRICOLAnombreProducto_SUGRA");
  const sugerenciasContainer = $("#sugerencias-producto-container-SUGRA");

  if (input.length === 0 || sugerenciasContainer.length === 0) {
    console.error(
      "Error al posicionar sugerencias SUGRA: elementos no encontrados"
    );
    return;
  }

  const inputPos = input.offset();

  sugerenciasContainer.css({
    top: inputPos.top + input.outerHeight() + "px",
    left: inputPos.left + "px",
    width: input.outerWidth() + "px",
    display: "block", // Asegurar que sea visible
  });
}

// Función para inicializar la búsqueda de productos SUGRA
function AGRICOLAbuscarproducto_SUGRA() {
  let timeoutId;
  let sugerenciasContainer;

  // Desactivar eventos previos para evitar duplicados
  $("#AGRICOLAnombreProducto_SUGRA").off("input");

  // Eliminar contenedor de sugerencias anterior si existe
  $("#sugerencias-producto-container-SUGRA").remove();

  // Crear el contenedor de sugerencias
  $("body").append(
    '<div id="sugerencias-producto-container-SUGRA" class="sugerencias-container"></div>'
  );
  sugerenciasContainer = $("#sugerencias-producto-container-SUGRA");

  // Aplicar estilos al contenedor
  sugerenciasContainer.css({
    position: "absolute",
    width: "auto",
    "max-height": "250px",
    "overflow-y": "auto",
    "background-color": "#fff",
    border: "1px solid #ddd",
    "border-radius": "4px",
    "box-shadow": "0 2px 5px rgba(0,0,0,0.2)",
    "z-index": "99999", // Valor muy alto para asegurar que esté por encima de todo
    display: "none",
  });

  // Cerrar sugerencias al hacer clic fuera de ellas
  $(document)
    .off("click.sugerenciasSUGRA")
    .on("click.sugerenciasSUGRA", function (e) {
      if (
        !$(e.target).closest(
          "#sugerencias-producto-container-SUGRA, #AGRICOLAnombreProducto_SUGRA"
        ).length
      ) {
        sugerenciasContainer.hide();
      }
    });

  // Asociar evento de entrada al campo de producto
  $("#AGRICOLAnombreProducto_SUGRA").on("input", function () {
    const query = $(this).val();

    // Limpiar el timeout anterior
    clearTimeout(timeoutId);

    // Si el input está vacío, ocultar sugerencias
    if (query.trim() === "") {
      sugerenciasContainer.hide();
      return;
    }

    // Establecer un nuevo timeout para evitar demasiadas peticiones
    timeoutId = setTimeout(function () {
      // Mostrar indicador de carga
      sugerenciasContainer.html(
        '<div class="p-2 text-center"><i class="fas fa-spinner fa-spin mr-2"></i>Buscando...</div>'
      );
      AGRICOLAposicionarSugerencias_SUGRA();
      sugerenciasContainer.show();

      // Preparar los parámetros de búsqueda
      const params = {
        idgrupo: 2400, // Valor fijo según requerimiento
      };

      // Determinar si la consulta es un ID o descripción
      if (/^\d+$/.test(query)) {
        // Es un número, buscar por ID de producto
        params.idproducto = query;
      } else {
        // Es texto, buscar por descripción
        params.descripcion = query;
      }

      // Asegurarnos de que el parámetro se envíe correctamente
      if (params.descripcion === "") {
        delete params.descripcion;
      }
      if (params.idproducto === "") {
        delete params.idproducto;
      }

      // Realizar la petición AJAX
      $.ajax({
        url: "/aplicaciones/productos/",
        type: "GET",
        data: params,
        success: function (response) {
          if (response.data && response.data.length > 0) {
            mostrarSugerenciasProductos_SUGRA(response.data);
          } else {
            sugerenciasContainer.html(
              '<div class="p-2 text-center text-muted">No se encontraron productos</div>'
            );
          }
        },
        error: function (xhr, status, error) {
          sugerenciasContainer.html(
            '<div class="p-2 text-center text-danger">Error al buscar productos</div>'
          );
          console.error("Error al buscar productos para SUGRA:", error);
        },
      });
    }, 300); // 300ms de debounce
  });

  // Función para mostrar las sugerencias de productos
  function mostrarSugerenciasProductos_SUGRA(productos) {
    sugerenciasContainer.empty();

    if (productos.length === 0) {
      sugerenciasContainer.html(
        '<div class="p-2 text-center text-muted">No se encontraron productos</div>'
      );
      return;
    }

    const ul = $("<ul>").addClass("list-unstyled mb-0");

    // Crear elementos de lista para cada producto
    productos.forEach(function (producto) {
      // Usar las propiedades correctas según la respuesta de la API
      const idProducto = producto.IDPRODUCTO || "";
      const nombreProducto = producto.DESCRIPCION || producto.PRODUCTO || "";
      const materiaActiva =
        producto.MATERIA_ACTIVA || producto.MATERIAACTIVA || "Sin información";
      const subgrupo =
        producto.DESCRIPCION_SUBGRUPO ||
        producto.SUBGRUPO ||
        producto.SUBGRUPOPROGRAMA ||
        "-";
      const precio = producto.PRECIO || producto.ultimo_precio || "0.00";

      const li = $("<li>").addClass("sugerencia-item p-2 border-bottom");

      li.html(`
        <div class="d-flex align-items-center">
          <div>
            <strong>${nombreProducto}</strong>
            <br>
            <small class="text-muted">${materiaActiva} - ${subgrupo}</small>
          </div>
          <span class="badge badge-primary ml-auto">$${
            typeof precio === "number" ? precio.toFixed(2) : precio
          }</span>
        </div>
      `);

      // Agregar evento click para seleccionar el producto
      li.on("click", function () {
        seleccionarProducto_SUGRA(producto);
        sugerenciasContainer.hide();
      });

      // Agregar efecto hover
      li.hover(
        function () {
          $(this).addClass("bg-light");
        },
        function () {
          $(this).removeClass("bg-light");
        }
      );

      ul.append(li);
    });

    sugerenciasContainer.append(ul);
    AGRICOLAposicionarSugerencias_SUGRA();
    sugerenciasContainer.show();
  }

  // Función para seleccionar un producto SUGRA
  function seleccionarProducto_SUGRA(producto) {
    // Usar las propiedades correctas según la respuesta de la API
    const idProducto = producto.IDPRODUCTO || "";
    const nombreProducto = producto.DESCRIPCION || producto.PRODUCTO || "";
    const materiaActiva =
      producto.MATERIA_ACTIVA || producto.MATERIAACTIVA || "";
    const subgrupo =
      producto.DESCRIPCION_SUBGRUPO ||
      producto.SUBGRUPO ||
      producto.SUBGRUPOPROGRAMA ||
      "";
    const idSubgrupo =
      producto.IDSUBGRUPO || producto.IDSUBGRUPOPROGRAMA || subgrupo;
    const precio = producto.PRECIO || producto.ultimo_precio || 0;

    // Establecer valores en los campos
    $("#AGRICOLAnombreProducto_SUGRA").val(nombreProducto);
    $("#AGRICOLAsubGrupoProducto_SUGRA").val(subgrupo);
    $("#AGRICOLAmateriaActivaProducto_SUGRA").val(materiaActiva);
    $("#AGRICOLAprecioProducto_SUGRA").val(
      typeof precio === "number" ? precio.toFixed(2) : precio
    );

    // Si la necesidad está vacía, establecerla a 1 por defecto
    if (!$("#AGRICOLAnecesidadProducto_SUGRA").val()) {
      $("#AGRICOLAnecesidadProducto_SUGRA").val("1");
    }

    // Establecer valores en los campos ocultos
    $("#AGRICOLAidProducto_SUGRA").val(idProducto);
    $("#idSubGrupo_SUGRA").val(idSubgrupo);

    // Calcular el precio por hectárea
    AGRICOLAcalcularPrecioHa_SUGRA();

    // Feedback visual
    $("#AGRICOLAnombreProducto_SUGRA")
      .addClass("is-valid")
      .parent()
      .append(
        '<small class="text-success product-selected-message">Producto seleccionado correctamente</small>'
      );

    // Eliminar mensaje después de 2 segundos
    setTimeout(function () {
      $(".product-selected-message").fadeOut(500, function () {
        $(this).remove();
        $("#AGRICOLAnombreProducto_SUGRA").removeClass("is-valid");
      });
    }, 2000);
  }

  // Inicializar la posición del contenedor de sugerencias al cargar
  $(window).on("resize", AGRICOLAposicionarSugerencias_SUGRA);
}

// Función para calcular el precio por hectárea para SUGRA
function AGRICOLAcalcularPrecioHa_SUGRA() {
  const necesidad = parseFloat($("#AGRICOLAnecesidadProducto_SUGRA").val()) || 0;
  const precioUnidad = parseFloat($("#AGRICOLAprecioProducto_SUGRA").val()) || 0;
  const precioHa = necesidad * precioUnidad;

  // Formatear con 2 decimales y actualizar el campo correcto
  $("#precioHa_SUGRA").val(precioHa.toFixed(2));
  $("#AGRICOLAprecioHaProducto_SUGRA").val(precioHa.toFixed(2));
}

// Función para resetear el formulario producto SUGRA
function AGRICOLAresetearFormularioProducto_SUGRA() {
  var form = $("#AGRICOLAformProducto_SUGRA");
  if (form.length && form[0]) {
    form[0].reset();
  }
  $("#AGRICOLAproductoId_SUGRA").val("");
  $("#AGRICOLA_idproducto_sum_SUGRA").val("");
  $("#AGRICOLA_descripcion_sum_SUGRA").val("");
  $("#AGRICOLA_precio_unitario_sum_SUGRA")
    .val("0.00")
    .prop("readonly", false)
    .attr("placeholder", "");
  $("#AGRICOLA_cantidad_masiva_sum_SUGRA").val("");
  var mesesReset = [
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
  mesesReset.forEach(function (mes) {
    $("#AGRICOLA_sum_SUGRA" + mes + "_switch").prop("checked", false);
    $("#AGRICOLA_sum_SUGRA" + mes + "_cantidad").prop("disabled", true).val("");
  });
  AGRICOLA_destruirAutocompleteSuministroSiExiste_SUGRA();
  $("#AGRICOLAmodalProductoLabel_SUGRA").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar suministro al programa'
  );
  AGRICOLA_calcularTotalesSuministro_SUGRA();
}

function AGRICOLA_destruirAutocompleteSuministroSiExiste_SUGRA() {
  var $d = $("#AGRICOLA_descripcion_sum_SUGRA");
  if ($d.length && $d.data("ui-autocomplete")) {
    $d.autocomplete("destroy");
  }
}


function AGRICOLA_calcularTotalesSuministro_SUGRA() {
  var pu = parseFloat($("#AGRICOLA_precio_unitario_sum_SUGRA").val()) || 0;
  var cantTotal = 0;
  var precioTotal = 0;
  $(".AGRICOLA_sum_cantidad_mes_SUGRA").each(function () {
    var idEl = this.id;
    var mes = idEl.replace(/^AGRICOLA_sum_SUGRA/, "").replace(/_cantidad$/, "");
    if ($("#AGRICOLA_sum_SUGRA" + mes + "_switch").is(":checked")) {
      var c = parseFloat($(this).val()) || 0;
      cantTotal += c;
      precioTotal += c * pu;
    }
  });
  $("#AGRICOLA_cantidad_total_sum_SUGRA").text(cantTotal.toFixed(2));
  $("#AGRICOLA_precio_total_sum_SUGRA").text("S/ " + precioTotal.toFixed(2));
}

// Función para abrir el modal de nuevo producto para SUGRA
function AGRICOLAabrirModalNuevoProducto_SUGRA(idPrograma) {
  AGRICOLAresetearFormularioProducto_SUGRA();
  $("#AGRICOLAprogramaId_SUGRA").val(idPrograma);
  $("#AGRICOLAmodalProducto_SUGRA").modal("show");
  AGRICOLAinitEventosFormularioProducto_SUGRA();
}

// Nueva función para inicializar todos los eventos del formulario de productos SUGRA
function AGRICOLAinitEventosFormularioProducto_SUGRA() {
  AGRICOLA_inicializarAutocompleteSuministro_SUGRA();

  $("#AGRICOLA_precio_unitario_sum_SUGRA")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministro_SUGRA();
    });

  $("input[id^='AGRICOLA_sum_SUGRA'][id$='_switch']")
    .off("change.sgSum")
    .on("change.sgSum", function () {
      var mes = this.id.replace(/^AGRICOLA_sum_SUGRA/, "").replace(/_switch$/, "");
      var $cant = $("#AGRICOLA_sum_SUGRA" + mes + "_cantidad");
      if ($(this).is(":checked")) {
        $cant.prop("disabled", false);
      } else {
        $cant.prop("disabled", true).val("");
      }
      AGRICOLA_calcularTotalesSuministro_SUGRA();
    });

  $(".AGRICOLA_sum_cantidad_mes_SUGRA")
    .off("input.sgSum")
    .on("input.sgSum", function () {
      AGRICOLA_calcularTotalesSuministro_SUGRA();
    });

  $("#AGRICOLA_aplicar_cantidad_masiva_sum_SUGRA")
    .off("click.sgSum")
    .on("click.sgSum", function () {
      var cantidad = $("#AGRICOLA_cantidad_masiva_sum_SUGRA").val();
      if (!cantidad || parseFloat(cantidad) <= 0) {
        Swal.fire({
          icon: "error",
          title: "Cantidad inválida",
          text: "Por favor, ingrese una cantidad válida mayor a 0",
        });
        return;
      }
      Swal.fire({
        title: "¿Aplicar a todos los meses?",
        text:
          "Se aplicará la cantidad de " +
          cantidad +
          " a todos los meses. ¿Desea continuar?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, aplicar",
        cancelButtonText: "Cancelar",
      }).then(function (result) {
        if (!result.isConfirmed) {
          return;
        }
        var mesesMas = [
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
        mesesMas.forEach(function (mes) {
          $("#AGRICOLA_sum_SUGRA" + mes + "_switch").prop("checked", true);
          $("#AGRICOLA_sum_SUGRA" + mes + "_cantidad")
            .prop("disabled", false)
            .val(cantidad);
        });
        AGRICOLA_calcularTotalesSuministro_SUGRA();
      });
    });

  $("#AGRICOLAbtnGuardarProducto_SUGRA")
    .off("click.sgSumGuardar")
    .on("click.sgSumGuardar", function () {
      AGRICOLAguardarProductoSugra();
    });
}

function AGRICOLA_inicializarAutocompleteSuministro_SUGRA() {
  AGRICOLA_destruirAutocompleteSuministroSiExiste();
  $("#AGRICOLA_descripcion_sum_SUGRA").autocomplete({
    minLength: 2,
    source: function (request, response) {
      $.ajax({
        url: "/riego/api_productos_agricolas_uva1/",
        dataType: "json",
        data: { q: request.term },
        success: function (data) {
          if (!data || data.error) {
            response([]);
            return;
          }
          var arr = Array.isArray(data) ? data : [];
          var results = $.map(arr, function (item) {
            var up = parseFloat(item.ultimo_precio) || 0;
            return {
              label: item.value,
              value: item.value,
              id: item.id,
              ultimo_precio: up,
              sin_precio_historico: up === 0,
            };
          });
          response(results);
        },
        error: function () {
          response([]);
        },
      });
    },
    select: function (event, ui) {
      $("#AGRICOLA_idproducto_sum_SUGRA").val(ui.item.id);
      if (ui.item.sin_precio_historico) {
        $("#AGRICOLA_precio_unitario_sum_SUGRA")
          .val("")
          .prop("readonly", false)
          .attr("placeholder", "Ingrese precio unitario");
        Swal.fire({
          title: "Sin precio histórico",
          text: "Ingrese manualmente el precio unitario.",
          icon: "info",
        });
      } else {
        $("#AGRICOLA_precio_unitario_sum_SUGRA")
          .val(ui.item.ultimo_precio.toFixed(2))
          .prop("readonly", true)
          .attr("placeholder", "");
      }
      AGRICOLA_calcularTotalesSuministroSG();
    },
  });
}

//============================================================
// FUNCIONES PARA SELECCIÓN DE LOTES
//============================================================

/**
 * Cargar lotes desde el backend para el selector
 * @param {number} idVariedad - ID de la variedad para filtrar lotes
 * @param {string} selectorId - ID del selector donde cargar los lotes (opcional)
 */

function AGRICOLAcargarLotes(idVariedad, selectorId = null, idCampania = null, idEmpresa = null) {
  if (!idCampania) {
    idCampania = document.getElementById("filtroAnioPresupuesto").value;
  }
  
  return new Promise((resolve, reject) => {

    $.ajax({
      url: "/riego/api/lotes_variedad/",
      type: "GET",
      data: {
        idvariedad: idVariedad,
        idcampania: idCampania,
        idempresa: 3,
      },

      success: function (response) {

        let selectLote;

        if (selectorId) {
          selectLote = $(selectorId);
        } else {

          if (idVariedad === 1) {
            selectLote = $("#AGRICOLAselectLote");

          } else if (idVariedad === 2) {
            selectLote = $("#AGRICOLAselectLote_AC");

          } else if (idVariedad === 3) {
            selectLote = $("#AGRICOLAselectLote_MC");

          } else if (idVariedad === 4) {
            selectLote = $("#AGRICOLAselectLote_SUGRA");

          } else {
            console.error("Variedad no reconocida:", idVariedad);
            reject("Variedad no reconocida");
            return;
          }

        }

        selectLote.find("option:not(:first)").remove();

        if (response.status === "success" && response.data.length > 0) {

          response.data.forEach(function (lote) {

            const option = `
              <option value="${lote.ID}">
                ${lote.SECTOR} - ${lote.LOTE} - ${lote.CONDICION} (${lote.AREA_TOTAL} ha)
              </option>
            `;

            selectLote.append(option);

          });

        } else {

          selectLote.append(`
            <option value="" disabled>
              No hay lotes disponibles
            </option>
          `);

        }

        resolve(response);

      },

      error: function (xhr, status, error) {

        console.error("Error al cargar lotes:", error);

        Swal.fire({
          title: "Error",
          text: "No se pudieron cargar los lotes disponibles",
          icon: "error"
        });

        reject(error);

      }

    });

  });

}

// Función para formatear moneda
function AGRICOLAformatearMoneda(valor) {
  if (isNaN(valor) || valor === null || valor === undefined) {
    return "$ 0.00";
  }
  return `$ ${parseFloat(valor).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

// Función para actualizar estadísticas de plantines Sweet Globe
function AGRICOLAactualizarEstadisticasPlantines_SG(datos) {
  // Calcular número de registros
  const numRegistros = datos.length;

  $("#AGRICOLAfacesRegistradosSG_PLANTINES").text(numRegistros);

  // Variables para almacenar totales
  let precioTotalPorLtKg = 0;
  let precioTotalPorHa = 0;
  let contadorProgramasConDetalles = 0;

  // Función para procesar todos los programas secuencialmente
  const procesarProgramas = async () => {
    for (const programa of datos) {
      if (programa.ID) {
        console.log("programa", programa);
        try {
          // Obtener detalles del programa
          const response = await $.ajax({
            url: `/riego/api/suministro_agricola_ajs/`,
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
              if (producto.PRECIO_HA && producto.PRECIO) {
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
    console.log("precioTotalPorLtKg", precioTotalPorLtKg);
    console.log("precioTotalPorHa", precioTotalPorHa);
    // Actualizar la interfaz con los totales calculados
    $("#AGRICOLAprecioTotalSG_PLANTINES").text(AGRICOLAformatearMoneda(precioTotalPorLtKg));
    $("#AGRICOLAcostoTotalSG_PLANTINES").text(AGRICOLAformatearMoneda(precioTotalPorHa));
  };

  // Iniciar el procesamiento de programas
  if (numRegistros > 0) {
    procesarProgramas().catch((error) => {
      console.error("Error al procesar programas:", error);
      // En caso de error, mostrar valores en cero
      $("#AGRICOLAprecioTotalSG_PLANTINES").text("$ 0.00");
      $("#AGRICOLAcostoTotalSG_PLANTINES").text("$ 0.00");
    });
  } else {
    // Si no hay registros, mostrar valores en cero
    $("#AGRICOLAprecioTotalSG_PLANTINES").text("$ 0.00");
    $("#AGRICOLAcostoTotalSG_PLANTINES").text("$ 0.00");
  }
}

// NUEVAS FUNCION MATERIAL AGRICOLA

