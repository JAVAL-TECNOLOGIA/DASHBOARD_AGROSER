// Función que verifica la pestaña activa y muestra su nombre en la consola
function ORGANICAverificarPestañaActiva_SG() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#ORGANICAsweetGlobeTabs a.active").attr("id");
  let nombrePestaña = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "ORGANICAplantines-tab":
      nombrePestaña = "PLANTINES";

      ORGANICAOrganicainiciarTablaResumen_SG(nombrePestaña);
      break;
    case "ORGANICApostcosecha-tab":
      nombrePestaña = "POST COSECHA";

      ORGANICAOrganicainiciarTablaResumen_SG(nombrePestaña);
      break;
    case "ORGANICAcosecha-tab":
      nombrePestaña = "PRODUCCIÓN";

      ORGANICAOrganicainiciarTablaResumen_SG(nombrePestaña);
      break;
    default:
      nombrePestaña = "Pestaña desconocida";
  }

  return nombrePestaña;
}

function ORGANICAverificarPestañaActiva_AC() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#ORGANICAautumnCrispTabs a.active").attr("id");
  let nombrePestaña_AC = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "ORGANICAplantines-tab":
      nombrePestaña_AC = "PLANTINES";

      ORGANICAiniciarTablaResumen_AC(nombrePestaña_AC);
      break;
    case "ORGANICApostcosecha-tab":
      nombrePestaña_AC = "POST COSECHA";

      ORGANICAiniciarTablaResumen_AC(nombrePestaña_AC);
      break;
    case "ORGANICAcosecha-tab":
      nombrePestaña_AC = "PRODUCCIÓN";

      ORGANICAiniciarTablaResumen_AC(nombrePestaña_AC);
      break;
    default:
      nombrePestaña_AC = "Pestaña desconocida";
  }

  return nombrePestaña_AC;
}

function ORGANICAverificarPestañaActiva_MC() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#ORGANICAmoscatelTabs a.active").attr("id");
  let nombrePestaña_MC = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "ORGANICAplantines-tab":
      nombrePestaña_MC = "PLANTINES";

      ORGANICAiniciarTablaResumen_MC(nombrePestaña_MC);
      break;
    case "ORGANICApostcosecha-tab":
      nombrePestaña_MC = "POST COSECHA";

      ORGANICAiniciarTablaResumen_MC(nombrePestaña_MC);
      break;
    case "ORGANICAcosecha-tab":
      nombrePestaña_MC = "PRODUCCIÓN";

      ORGANICAiniciarTablaResumen_MC(nombrePestaña_MC);
      break;
    default:
      nombrePestaña_MC = "Pestaña desconocida";
  }

  return nombrePestaña_MC;
}

function ORGANICAverificarPestañaActiva_SUGRA() {
  // Obtener el ID de la pestaña activa
  const selectedTabId = $("#ORGANICAsugraTabs a.active").attr("id");
  let nombrePestaña_SUGRA = "";

  // Determinar el nombre de la pestaña según su ID
  switch (selectedTabId) {
    case "ORGANICAplantines-tab":
      nombrePestaña_SUGRA = "PLANTINES";

      ORGANICAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA);
      break;
    case "ORGANICApostcosecha-tab":
      nombrePestaña_SUGRA = "POST COSECHA";

      ORGANICAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA);
      break;
    case "ORGANICAcosecha-tab":
      nombrePestaña_SUGRA = "PRODUCCIÓN";

      ORGANICAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA);
      break;
    default:
      nombrePestaña_SUGRA = "Pestaña desconocida";
  }

  // Inicializar los eventos de búsqueda para todos los modales SUGRA cuando se seleccione esta variedad
  // Esto garantiza que buscarproducto_SUGRA se ejecute al cargar la interfaz para SUGRA
  $(document).ready(function () {
    // Si hay algún modal abierto para SUGRA, inicializar los eventos
    if ($("#ORGANICAmodalProducto_SUGRA").length > 0) {
      $("#ORGANICAmodalProducto_SUGRA")
        .off("shown.bs.modal")
        .on("shown.bs.modal", function () {
          initEventosFormularioProducto_SUGRA();
        });
    }

    // Asociar evento al botón de nuevo producto si existe
    $(".btn-nuevo-producto-sugra")
      .off("click")
      .on("click", function () {
        const programaId = $(this).data("programa-id");
        if (programaId) {
          abrirModalNuevoProducto_SUGRA(programaId);
        }
      });
  });

  return nombrePestaña_SUGRA;
}

//INICIALIZAR LA TABLA DE RESUMEN VARIEDAD SWEET GLOBE
function ORGANICAOrganicainiciarTablaResumen_SG(nombrePestaña) {
  //PLANTINES
  if (nombrePestaña == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAOrganicatablaFertilizacionPlantines_SG")) {
      $("#ORGANICAOrganicatablaFertilizacionPlantines_SG").DataTable().destroy();
    }

    const tabla = $("#ORGANICAOrganicatablaFertilizacionPlantines_SG").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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

          $("#ORGANICAfacesRegistradosSG_PLANTINES").text(datos.length);

          // Actualizar estadisticas cuando se cargan los datos
          ORGANICAactualizarEstadisticasPlantines_SG(datos);

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
        ORGANICAconfigurarMenuContextual_SG(nombrePestaña);
      },
    });
  } else if (nombrePestaña == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionPostCosecha_SG")) {
      $("#ORGANICAtablaFertilizacionPostCosecha_SG").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionPostCosecha_SG").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          //actualizarEstadisticasPlantines_SG(datos);

          // Actualizar el número de faces registradas
          $("#ORGANICAfacesRegistradosSG_POSTCOSECHA").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_SG(nombrePestaña);
      },
    });
  } else if (nombrePestaña == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionProduccion_SG")) {
      $("#ORGANICAtablaFertilizacionProduccion_SG").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionProduccion_SG").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          //actualizarEstadisticasPlantines_SG(datos);

          // Actualizar el número de faces registradas
          $("#ORGANICAfacesRegistradosSG_PRODUCCION").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_SG(nombrePestaña);
      },
    });
  }
}

function ORGANICAiniciarTablaResumen_AC(nombrePestaña_AC) {
  //PLANTINES
  if (nombrePestaña_AC == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionPlantines_AC")) {
      $("#ORGANICAtablaFertilizacionPlantines_AC").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionPlantines_AC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          //actualizarEstadisticasPlantines_SG(datos);

          $("#ORGANICAfacesRegistradosAC_PLANTINES").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_AC(nombrePestaña_AC);
      },
    });
  } else if (nombrePestaña_AC == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionPostCosecha_AC")) {
      $("#ORGANICAtablaFertilizacionPostCosecha_AC").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionPostCosecha_AC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          //actualizarEstadisticasPlantines_SG(datos);
          $("#ORGANICAfacesRegistradosAC_POSTCOSECHA").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_AC(nombrePestaña_AC);
      },
    });
  } else if (nombrePestaña_AC == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionProduccion_AC")) {
      $("#ORGANICAtablaFertilizacionProduccion_AC").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionProduccion_AC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          //actualizarEstadisticasPlantines_SG(datos);
          $("#ORGANICAfacesRegistradosAC_PRODUCCION").text(datos.length);
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
        ORGANICAconfigurarMenuContextual_AC(nombrePestaña_AC);
      },
    });
  }
}

function ORGANICAiniciarTablaResumen_MC(nombrePestaña_MC) {
  //PLANTINES
  if (nombrePestaña_MC == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionPlantines_MC")) {
      $("#ORGANICAtablaFertilizacionPlantines_MC").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionPlantines_MC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          $("#ORGANICAfacesRegistradasMC_PLANTINES").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_MC(nombrePestaña_MC);
      },
    });
  } else if (nombrePestaña_MC == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionPostCosecha_MC")) {
      $("#ORGANICAtablaFertilizacionPostCosecha_MC").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionPostCosecha_MC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          $("#ORGANICAfacesRegistradasMC_POSTCOSECHA").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_MC(nombrePestaña_MC);
      },
    });
  } else if (nombrePestaña_MC == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionProduccion_MC")) {
      $("#ORGANICAtablaFertilizacionProduccion_MC").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionProduccion_MC").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          $("#ORGANICAfacesRegistradasMC_PRODUCCION").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_MC(nombrePestaña_MC);
      },
    });
  }
}

function ORGANICAiniciarTablaResumen_SUGRA(nombrePestaña_SUGRA) {
  //PLANTINES
  if (nombrePestaña_SUGRA == "PLANTINES") {
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionPlantines_SUGRA")) {
      $("#ORGANICAtablaFertilizacionPlantines_SUGRA").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionPlantines_SUGRA").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
        ORGANICAconfigurarMenuContextual_SUGRA(nombrePestaña_SUGRA);
      },
    });
  } else if (nombrePestaña_SUGRA == "POST COSECHA") {
    //POST COSECHA
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionPostCosecha_SUGRA")) {
      $("#ORGANICAtablaFertilizacionPostCosecha_SUGRA").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionPostCosecha_SUGRA").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
          $("#ORGANICAfacesRegistradasSUGRA_POSTCOSECHA").text(datos.length);

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
        ORGANICAconfigurarMenuContextual_SUGRA(nombrePestaña_SUGRA);
      },
    });
  } else if (nombrePestaña_SUGRA == "PRODUCCIÓN") {
    //PRODUCCIÓN
    // Destruir la tabla si ya existe
    if ($.fn.DataTable.isDataTable("#ORGANICAtablaFertilizacionProduccion_SUGRA")) {
      $("#ORGANICAtablaFertilizacionProduccion_SUGRA").DataTable().destroy();
    }

    const tabla = $("#ORGANICAtablaFertilizacionProduccion_SUGRA").DataTable({
      responsive: true,
      autoWidth: false,
      pageLength: 5, // Número máximo de filas por página

      language: {
        url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      },
      ajax: {
        url: "/riego/api/materia_organica_dl/",
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
        ORGANICAconfigurarMenuContextual_SUGRA(nombrePestaña_SUGRA);
      },
    });
  }
}
//============================================================================
// CONFIGURACIONES PARA EL MENU CONTEXTUAL DE LAS FASES
//============================================================================
// Esta función soluciona el problema con el menú contextual
function ORGANICAconfigurarMenuContextual_SG(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#ORGANICAOrganicatablaFertilizacionPlantines_SG";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#ORGANICAtablaFertilizacionPostCosecha_SG";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#ORGANICAtablaFertilizacionProduccion_SG";
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
    ORGANICAmostrarDetallesProductos(idRegistro);
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
    $("#ORGANICAmenuContextualFertilizacion_SG").remove();

    // Crear el menú contextual de nuevo
    $("body").append(`
      <div id="ORGANICAmenuContextualFertilizacion_SG" class="dropdown-menu shadow" 
           style="display: none; position: absolute; z-index: 9999;">
        <h6 class="dropdown-header">Opciones</h6>
        <a class="dropdown-item text-primary" href="#" id="ORGANICAbtnEditarFertilizacion_SG">
          <i class="fas fa-edit mr-2"></i> Editar
        </a>
        <div class="dropdown-divider"></div>
        <a class="dropdown-item text-danger" href="#" id="btnEliminarFertilizacion_SG">
          <i class="fas fa-trash-alt mr-2"></i> Eliminar
        </a>
      </div>
    `);

    // Configurar los eventos justo después de crear el menú
    $("#ORGANICAbtnEditarFertilizacion_SG")
      .off("click")
      .on("click", function () {
        ORGANICAeditarFertilizacion_SG(idRegistro);
        $("#ORGANICAmenuContextualFertilizacion_SG").hide();
      });

    $("#btnEliminarFertilizacion_SG")
      .off("click")
      .on("click", function () {
        ORGANICAeliminarFertilizacion(idRegistro);
        $("#ORGANICAmenuContextualFertilizacion_SG").hide();
      });

    // Guardar el ID en los botones del menú para usarlo después
    $("#ORGANICAbtnEditarFertilizacion_SG").attr("data-id", idRegistro);
    $("#btnEliminarFertilizacion_SG").attr("data-id", idRegistro);

    // Mostrar el menú contextual en la posición del clic
    const menuContextual = $("#ORGANICAmenuContextualFertilizacion_SG");
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
    $("#ORGANICAmenuContextualFertilizacion_SG").hide();
  });
}

function ORGANICAconfigurarMenuContextual_AC(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#ORGANICAtablaFertilizacionPlantines_AC";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#ORGANICAtablaFertilizacionPostCosecha_AC";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#ORGANICAtablaFertilizacionProduccion_AC";
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
    ORGANICAmostrarDetallesProductos_AC(idRegistro);
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
        ORGANICAeditarFertilizacion_AC(idRegistro);
        $("#menuContextualFertilizacion_AC").hide();
      });

    $("#btnEliminarFertilizacion_AC")
      .off("click")
      .on("click", function () {
        ORGANICAeliminarFertilizacion_AC(idRegistro);
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

function ORGANICAconfigurarMenuContextual_MC(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#ORGANICAtablaFertilizacionPlantines_MC";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#ORGANICAtablaFertilizacionPostCosecha_MC";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#ORGANICAtablaFertilizacionProduccion_MC";
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
        ORGANICAeditarFertilizacion_MC(idRegistro);
        $("#menuContextualFertilizacion_MC").hide();
      });

    $("#btnEliminarFertilizacion_MC")
      .off("click")
      .on("click", function () {
        ORGANICAeliminarFertilizacion_MC(idRegistro);
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
        ORGANICAmostrarDetallesProductos_MC(filaSeleccionada.ID);
      }
    });
}

//============================================================================
// CONFIGURACIÓN DEL MENÚ CONTEXTUAL PARA SUGRA
//============================================================================

function ORGANICAconfigurarMenuContextual_SUGRA(nombrePestaña) {
  let tablaSelector;

  // Determinar el selector de la tabla según la pestaña
  if (nombrePestaña === "PLANTINES") {
    tablaSelector = "#ORGANICAtablaFertilizacionPlantines_SUGRA";
  } else if (nombrePestaña === "POST COSECHA") {
    tablaSelector = "#ORGANICAtablaFertilizacionPostCosecha_SUGRA";
  } else if (nombrePestaña === "PRODUCCIÓN") {
    tablaSelector = "#ORGANICAtablaFertilizacionProduccion_SUGRA";
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
    ORGANICAmostrarDetallesProductos_SUGRA(idRegistro);
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
        ORGANICAeditarFertilizacion_SUGRA(idRegistro);
        $("#menuContextualFertilizacion_SUGRA").hide();
      });

    $("#btnEliminarFertilizacion_SUGRA")
      .off("click")
      .on("click", function () {
        ORGANICAeliminarFertilizacion_SUGRA(idRegistro);
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
        ORGANICAmostrarDetallesProductos_SUGRA(filaSeleccionada.ID);
      }
    });
}

//============================================================================
// FUNCIONES PARA GUARDAR EL NUEVO PROGRAMA
//============================================================================

function ORGANICAguardarNuevoPrograma_SG() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#ORGANICAnombrePrograma").val().trim();
  const fechaInicio = $("#ORGANICAfechaInicio").val();
  const fechaFin = $("#ORGANICAfechaFin").val();
  const descripcion = $("#ORGANICAdescripcion_riego").val() || "";
  const idfase = $("#ORGANICAidfase").val();
  const idvariedad = $("#ORGANICAidvariedad").val();
  const idusuario = $("#ORGANICAidusuario").val();
  const idlote = $("#ORGANICAselectLote").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#ORGANICAidregistro").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#ORGANICAselectLote").css("border", "1px solid red");
    $("#ORGANICAselectLote").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#ORGANICAnombrePrograma").css("border", "1px solid red");
    $("#ORGANICAnombrePrograma").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#ORGANICAfechaInicio").css("border", "1px solid red");
    $("#ORGANICAfechaInicio").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#ORGANICAfechaFin").css("border", "1px solid red");
    $("#ORGANICAfechaFin").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#ORGANICAfechaFin").css("border", "1px solid red");
      $("#ORGANICAfechaFin").after(
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
      ? `/riego/api/materia_organica_dl/${idregistro}/`
      : "/riego/api/materia_organica_dl/";
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
        $("#ORGANICAmodalCrearPrograma").modal("hide");

        // Limpiar el formulario
        $("#ORGANICAformCrearPrograma")[0].reset();

        // Limpiar el selector de lotes
        $("#ORGANICAselectLote").find("option:not(:first)").remove();

        // Eliminar el campo idregistro si existe
        $("#ORGANICAidregistro").remove();

        // Restaurar el texto del botón
        $("#ORGANICAbtnGuardarProgramaSG").text("Guardar");

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = ORGANICAverificarPestañaActiva_SG();
        ORGANICAOrganicainiciarTablaResumen_SG(nombrePestaña);
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

function ORGANICAguardarNuevoPrograma_AC() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#ORGANICAnombrePrograma_AC").val().trim();
  const fechaInicio = $("#ORGANICAfechaInicio_AC").val();
  const fechaFin = $("#ORGANICAfechaFin_AC").val();
  const descripcion = $("#ORGANICAdescripcion_riego_AC").val() || "";
  const idfase = $("#ORGANICAidfase_AC").val();
  const idvariedad = $("#ORGANICAidvariedad_AC").val();
  const idusuario = $("#ORGANICAidusuario").val();
  const idlote = $("#ORGANICAselectLote_AC").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#ORGANICAidregistro_AC").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#ORGANICAselectLote_AC").css("border", "1px solid red");
    $("#ORGANICAselectLote_AC").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#ORGANICAnombrePrograma_AC").css("border", "1px solid red");
    $("#ORGANICAnombrePrograma_AC").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#ORGANICAfechaInicio_AC").css("border", "1px solid red");
    $("#ORGANICAfechaInicio_AC").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#ORGANICAfechaFin_AC").css("border", "1px solid red");
    $("#ORGANICAfechaFin_AC").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#ORGANICAfechaFin_AC").css("border", "1px solid red");
      $("#ORGANICAfechaFin_AC").after(
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
      ? `/riego/api/materia_organica_dl/${idregistro}/`
      : "/riego/api/materia_organica_dl/";

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
        $("#ORGANICAmodalCrearPrograma_AC").modal("hide");

        // Limpiar el formulario
        $("#ORGANICAformCrearPrograma_AC")[0].reset();

        // Limpiar el selector de lotes
        $("#ORGANICAselectLote_AC").find("option:not(:first)").remove();

        // Si estábamos en modo edición, cambiar el botón de vuelta a "Guardar"
        if (esEdicion) {
          $("#ORGANICAbtnGuardarProgramaAC").html(
            '<i class="fas fa-save mr-1"></i> Guardar'
          );
          // Eliminar el campo oculto del ID
          $("#ORGANICAidregistro_AC").remove();
        }

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = ORGANICAverificarPestañaActiva_AC();
        ORGANICAiniciarTablaResumen_AC(nombrePestaña);
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

function ORGANICAguardarNuevoPrograma_MC() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#ORGANICAnombrePrograma_MC").val().trim();
  const fechaInicio = $("#ORGANICAfechaInicio_MC").val();
  const fechaFin = $("#ORGANICAfechaFin_MC").val();
  const descripcion = $("#ORGANICAdescripcion_riego_MC").val() || "";
  const idfase = $("#ORGANICAidfase_MC").val();
  const idvariedad = $("#ORGANICAidvariedad_MC").val();
  const idusuario = $("#ORGANICAidusuario").val();
  const idlote = $("#ORGANICAselectLote_MC").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#ORGANICAidregistro_MC").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#ORGANICAselectLote_MC").css("border", "1px solid red");
    $("#ORGANICAselectLote_MC").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#ORGANICAnombrePrograma_MC").css("border", "1px solid red");
    $("#ORGANICAnombrePrograma_MC").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#ORGANICAfechaInicio_MC").css("border", "1px solid red");
    $("#ORGANICAfechaInicio_MC").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#ORGANICAfechaFin_MC").css("border", "1px solid red");
    $("#ORGANICAfechaFin_MC").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#ORGANICAfechaFin_MC").css("border", "1px solid red");
      $("#ORGANICAfechaFin_MC").after(
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
      ? `/riego/api/materia_organica_dl/${idregistro}/`
      : "/riego/api/materia_organica_dl/";
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
        $("#ORGANICAmodalCrearPrograma_MC").modal("hide");

        // Limpiar el formulario
        $("#ORGANICAformCrearPrograma_MC")[0].reset();

        // Limpiar el selector de lotes
        $("#ORGANICAselectLote_MC").find("option:not(:first)").remove();

        // Eliminar el campo oculto de ID si existe
        if (esEdicion) {
          $("#ORGANICAidregistro_MC").remove();
        }

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = ORGANICAverificarPestañaActiva_MC();
        ORGANICAiniciarTablaResumen_MC(nombrePestaña);
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

function ORGANICAguardarNuevoPrograma_SUGRA() {
  // Limpiar mensajes de error previos
  $(".text-danger").remove();
  $("input").css("border", "");

  // Obtener los valores de los campos
  const nombrePrograma = $("#ORGANICAnombrePrograma_SUGRA").val().trim();
  const fechaInicio = $("#ORGANICAfechaInicio_SUGRA").val();
  const fechaFin = $("#ORGANICAfechaFin_SUGRA").val();
  const descripcion = $("#ORGANICAdescripcion_riego_SUGRA").val() || "";
  const idfase = $("#ORGANICAidfase_SUGRA").val();
  const idvariedad = $("#ORGANICAidvariedad_SUGRA").val();
  const idusuario = $("#ORGANICAidusuario").val();
  const idlote = $("#ORGANICAselectLote_SUGRA").val();

  // Obtener el ID del registro si estamos en modo edición
  const idregistro = $("#ORGANICAidregistro_SUGRA").val() || null;
  const esEdicion = idregistro !== null && idregistro !== "";

  // Variable para controlar si hay errores
  let hayErrores = false;

  // VALIDAR QUE LOS CAMPOS NO ESTEN VACIOS PINTANDO DE COLOR ROJO Y MOSTRANDO UN MENSAJE DE ERROR
  if (idlote === "" || idlote === null) {
    $("#ORGANICAselectLote_SUGRA").css("border", "1px solid red");
    $("#ORGANICAselectLote_SUGRA").after(
      "<span class='text-danger'>Debe seleccionar un lote</span>"
    );
    hayErrores = true;
  }

  if (nombrePrograma === "") {
    $("#ORGANICAnombrePrograma_SUGRA").css("border", "1px solid red");
    $("#ORGANICAnombrePrograma_SUGRA").after(
      "<span class='text-danger'>El nombre del programa es obligatorio</span>"
    );
    hayErrores = true;
  }

  if (fechaInicio === "") {
    $("#ORGANICAfechaInicio_SUGRA").css("border", "1px solid red");
    $("#ORGANICAfechaInicio_SUGRA").after(
      "<span class='text-danger'>La fecha de inicio es obligatoria</span>"
    );
    hayErrores = true;
  }

  if (fechaFin === "") {
    $("#ORGANICAfechaFin_SUGRA").css("border", "1px solid red");
    $("#ORGANICAfechaFin_SUGRA").after(
      "<span class='text-danger'>La fecha de fin es obligatoria</span>"
    );
    hayErrores = true;
  }

  // Validar que fecha fin sea mayor que fecha inicio
  if (fechaInicio !== "" && fechaFin !== "") {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);

    if (fin < inicio) {
      $("#ORGANICAfechaFin_SUGRA").css("border", "1px solid red");
      $("#ORGANICAfechaFin_SUGRA").after(
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
      ? `/riego/api/materia_organica_dl/${idregistro}/`
      : "/riego/api/materia_organica_dl/";
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
        $("#ORGANICAmodalCrearPrograma_SUGRA").modal("hide");

        // Limpiar el formulario
        $("#ORGANICAformCrearPrograma_SUGRA")[0].reset();

        // Limpiar el selector de lotes
        $("#ORGANICAselectLote_SUGRA").find("option:not(:first)").remove();

        // Eliminar el campo oculto de ID si existe
        if (esEdicion) {
          $("#ORGANICAidregistro_SUGRA").remove();

          // Restaurar el texto del botón
          $("#ORGANICAbtnGuardarProgramaSUGRA").html(
            '<i class="fas fa-save mr-1"></i> Guardar'
          );
        }

        // Recargar la tabla correspondiente según la pestaña activa
        const nombrePestaña = ORGANICAverificarPestañaActiva_SUGRA();
        ORGANICAiniciarTablaResumen_SUGRA(nombrePestaña);
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
function ORGANICAeditarFertilizacion_SG(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAmodalCrearPrograma").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#ORGANICAmodalCrearProgramaLabel").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#ORGANICAbtnGuardarProgramaSG").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#ORGANICAidregistro").length === 0) {
        $("#ORGANICAformCrearPrograma").append(
          `<input type="hidden" id="idregistro" value="${idRegistro}">`
        );
      } else {
        $("#ORGANICAidregistro").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#ORGANICAnombrePrograma").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = ORGANICAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#ORGANICAfechaInicio").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = ORGANICAformatearFechaParaInput(registro.FECHA_FIN);
        $("#ORGANICAfechaFin").val(fechaFin);
      }

      // Llenar la descripción
      $("#ORGANICAdescripcion_riego").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#ORGANICAidfase").val(registro.IDFASE);
      $("#ORGANICAidvariedad").val(registro.IDVARIEDAD);
      $("#ORGANICAidusuario").val(registro.IDUSUARIO);

      // Cargar los lotes y seleccionar el lote correcto
      ORGANICAcargarLotes(registro.IDVARIEDAD);

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

function ORGANICAeditarFertilizacion_AC(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAmodalCrearPrograma_AC").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#ORGANICAmodalCrearProgramaLabel_AC").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#ORGANICAbtnGuardarProgramaAC").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#ORGANICAidregistro_AC").length === 0) {
        $("#ORGANICAformCrearPrograma_AC").append(
          `<input type="hidden" id="idregistro_AC" value="${idRegistro}">`
        );
      } else {
        $("#ORGANICAidregistro_AC").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#ORGANICAnombrePrograma_AC").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = ORGANICAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#ORGANICAfechaInicio_AC").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = ORGANICAformatearFechaParaInput(registro.FECHA_FIN);
        $("#ORGANICAfechaFin_AC").val(fechaFin);
      }

      // Llenar la descripción
      $("#ORGANICAdescripcion_riego_AC").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#ORGANICAidfase_AC").val(registro.IDFASE);
      $("#ORGANICAidvariedad_AC").val(registro.IDVARIEDAD);
      $("#ORGANICAidusuario").val(registro.IDUSUARIO);

      // Cargar los lotes y seleccionar el lote correcto
      ORGANICAcargarLotes(registro.IDVARIEDAD);

      // Después de un breve delay para que se carguen los lotes, seleccionar el lote correcto
      setTimeout(() => {
        if (registro.IDLOTE) {
          $("#ORGANICAselectLote_AC").val(registro.IDLOTE);
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

function ORGANICAmostrarDetallesProductos_AC(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#ORGANICAprogramaId_AC").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAnombreProgramaDetalle_AC").text(programa.NOMBRE);
      $("#ORGANICAfechaInicioProgramaDetalle_AC").text(programa.FECHA_INICIO);
      $("#ORGANICAfechaFinProgramaDetalle_AC").text(programa.FECHA_FIN);
      $("#ORGANICAdescripcionProgramaDetalle_AC").text(
        programa.DESCRIPCION || "Sin descripción"
      );
      $("#ORGANICAsectorProgramaDetalle_AC").text(programa.SECTOR || "no definido");
      $("#ORGANICAloteProgramaDetalle_AC").text(programa.LOTE_NOMBRE || "no definido");

      // Mostrar el modal
      $("#ORGANICAmodalDetalleProductos_AC").modal("show");

      // Cargar los productos relacionados con este programa
      // Lo hacemos después de mostrar el modal para asegurar que la tabla se renderice correctamente
      ORGANICAcargarProductosPrograma_AC(idRegistro);
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

function ORGANICAcargarProductosPrograma_AC(idPrograma) {
  // Mostrar mensaje en la consola

  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#ORGANICAtablaDetalleProductos_AC")) {
    $("#ORGANICAtablaDetalleProductos_AC").DataTable().clear().destroy();
  }

  // Iniciar la tabla de productos con datos de la API
  const tabla = $("#ORGANICAtablaDetalleProductos_AC").DataTable({
    responsive: true,
    autoWidth: false,
    pageLength: 5, // Número máximo de filas por página
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url: `/riego/api/organica_materia/`,
      type: "GET",
      dataSrc: function (json) {
        // Comprobar si hay datos
        if (!json || !json.data || json.data.length === 0) {
          return [];
        }

        // Convertir idPrograma a número para comparación segura
        const idProgramaNum = parseInt(idPrograma, 10);

        // Filtrar los datos para mostrar solo los del programa seleccionado
        const datosFiltrados = json.data.filter(function (item) {
          // Convertir el IDMATERIA_ORGANICA a número también
          const idPreFert = parseInt(item.IDMATERIA_ORGANICA, 10);

          return idPreFert === idProgramaNum;
        });

        // Actualizar contador de productos
        $("#totalProductosProgramaDetalle_AC").text(datosFiltrados.length);

        // Calcular y actualizar costo total
        let costoTotal = 0;
        datosFiltrados.forEach((item) => {
          const precioHa = parseFloat(item.PRECIO_HA || 0);
          if (!isNaN(precioHa)) {
            costoTotal += precioHa;
          }
        });

        // Formatear y mostrar el costo total
        $("#ORGANICAcostoTotalProgramaDetalle_AC").text(`$ ${costoTotal.toFixed(2)}`);
        $("#ORGANICAtotalCostoProductos_AC").text(`${costoTotal.toFixed(2)}`);

        return datosFiltrados;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        // Mostrar error en la interfaz
        $("#ORGANICAtablaDetalleProductos_AC tbody").html(
          '<tr><td colspan="10" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
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
      { data: "SUBGRUPO" },
      { data: "IDPRODUCTO" },
      { data: "PRODUCTO" },
      { data: "MATERIA_ACTIVA" },
      {
        data: "NECESIDADXHA",
        className: "text-center",
        render: function (data) {
          return data ? parseFloat(data).toFixed(2) : "0.00";
        },
      },
      {
        data: "UND",
        className: "text-center",
      },
      {
        data: "PRECIO_LTKG",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      {
        data: "PRECIO_HA",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      { data: "OBSERVACIONES" },
      {
        data: null,
        className: "text-center",
        orderable: false,
        width: "120px",
        render: function (data, type, row) {
          return `
            <div class="btn-group">
              <button class="btn btn-sm btn-outline-primary btn-editar-producto-AC" data-id="${row.ID}" title="Editar producto">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger btn-eliminar-producto-AC" data-id="${row.ID}" title="Eliminar producto">
                <i class="fas fa-trash-alt"></i>
              </button>
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
    language: {
      processing: "Procesando...",
      lengthMenu: "Mostrar _MENU_ registros",
      zeroRecords: "No se encontraron resultados",
      emptyTable: "No hay productos disponibles para este programa",
      info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
      infoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
      infoFiltered: "(filtrado de un total de _MAX_ registros)",
      search: "Buscar:",
      infoThousands: ",",
      loadingRecords: "Cargando...",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
      aria: {
        sortAscending: ": Activar para ordenar la columna de manera ascendente",
        sortDescending:
          ": Activar para ordenar la columna de manera descendente",
      },
    },
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excel",
        text: '<i class="fas fa-file-excel"></i> Excel',
        className: "btn btn-success",
        title: `Productos del Programa ${$(
          "#ORGANICAnombreProgramaDetalle_AC"
        ).text()}`,
        exportOptions: {
          columns: [1, 2, 3, 4, 5],
        },
      },
      {
        extend: "csv",
        text: '<i class="fas fa-file-csv"></i> CSV',
        className: "btn btn-info",
        title: `Productos del Programa ${$(
          "#ORGANICAnombreProgramaDetalle_AC"
        ).text()}`,
        exportOptions: {
          columns: [1, 2, 3, 4, 5],
        },
      },
      {
        text: '<i class="fas fa-print"></i> Imprimir',
        className: "btn btn-primary",
        action: function (e, dt, node, config) {
          // Obtener el título del programa
          var titulo = $("#ORGANICAnombreProgramaDetalle_AC").text();

          // Clonar la tabla para imprimirla
          var printContent = $("#ORGANICAtablaDetalleProductos_AC").clone();

          // Eliminar columnas no deseadas para impresión (opcional)
          printContent.find("thead tr th:last-child").remove();
          printContent.find("tbody tr").each(function () {
            $(this).find("td:last-child").remove();
          });

          // Crear una ventana de impresión
          var printWindow = window.open("", "", "height=600,width=800");
          printWindow.document.write(
            "<html><head><title>" + titulo + "</title>"
          );
          printWindow.document.write(
            '<link rel="stylesheet" href="/static/assets/css/bootstrap.min.css" type="text/css" />'
          );
          printWindow.document.write("</head><body>");
          printWindow.document.write(
            '<h1 class="text-center mb-4">' + titulo + "</h1>"
          );
          printWindow.document.write('<div class="container">');
          printWindow.document.write('<div class="table-responsive">');
          printWindow.document.write(printContent.prop("outerHTML"));
          printWindow.document.write("</div>");
          printWindow.document.write("</div>");
          printWindow.document.write("</body></html>");

          printWindow.document.close();
          printWindow.focus();

          // Imprimir después de que se carguen los estilos
          setTimeout(function () {
            printWindow.print();
            printWindow.close();
          }, 1000);
        },
      },
    ],
    responsive: true,
    pageLength: 10,
    order: [[1, "asc"]],
  });

  // Agregar eventos para los botones de acción
  $("#ORGANICAtablaDetalleProductos_AC").on(
    "click",
    ".btn-editar-producto-AC",
    function () {
      const idProducto = $(this).data("id");

      ORGANICAeditarProductoAutumnCrisp(idProducto);
    }
  );

  $("#ORGANICAtablaDetalleProductos_AC").on(
    "click",
    ".btn-eliminar-producto-AC",
    function () {
      const idProducto = $(this).data("id");

      ORGANICAeliminarProductoAutumnCrisp(idProducto);
    }
  );

  // Configurar el botón para agregar nuevos productos
  $("#ORGANICAbtnAñadirProducto_AC")
    .off("click")
    .on("click", function () {
      // Obtener el ID del programa actual
      const programaId = $("#ORGANICAprogramaId_AC").val();

      if (!programaId) {
        Swal.fire("Error", "No se ha seleccionado un programa", "error");
        return;
      }

      // Llamar a la función de abrir modal con autocompletado
      ORGANICAabrirModalNuevoProducto_AC(programaId);
    });

  // Configurar el envío del formulario para guardar un nuevo producto
  $("#ORGANICAformProducto_AC")
    .off("submit")
    .on("submit", function (e) {
      e.preventDefault();
      ORGANICAguardarProductoAutumnCrisp();
    });
}

// Función auxiliar para formatear fechas (de DD/MM/YYYY a YYYY-MM-DD)
function ORGANICAformatearFechaParaInput(fechaStr) {
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
function ORGANICAeliminarFertilizacion(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/organica_materia/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDMATERIA_ORGANICA, 10) ===
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
          url: `/riego/api/materia_organica_dl/${idRegistro}/`,
          type: "DELETE",
          success: function (response) {
            // Mostrar mensaje de éxito
            Swal.fire(
              "¡Eliminado!",
              "El registro ha sido eliminado correctamente.",
              "success"
            );

            // Recargar la tabla correspondiente según la pestaña activa
            const nombrePestaña = ORGANICAverificarPestañaActiva_SG();
            ORGANICAOrganicainiciarTablaResumen_SG(nombrePestaña);
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

function ORGANICAeliminarFertilizacion_AC(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/organica_materia/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDMATERIA_ORGANICA, 10) ===
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
          url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
              ORGANICAverificarPestañaActiva_AC();
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

function ORGANICAguardarProductoAutumnCrisp() {
  // Obtener valores del formulario
  const idProducto = $("#ORGANICAproductoId_AC").val();
  const programaId = $("#ORGANICAprogramaId_AC").val();
  // Obtener los IDs de producto y subgrupo para la API
  const idProductoAPI = $("#ORGANICAidProductoAC").val() || "";
  const idSubgrupoAPI = $("#ORGANICAidSubgrupoAC").val() || "";
  const subGrupo = $("#ORGANICAsubGrupoProducto_AC").val();
  const producto = $("#ORGANICAnombreProducto_AC").val();
  const materiaActiva = $("#ORGANICAmateriaActivaProducto_AC").val();
  const necesidad = $("#ORGANICAnecesidadProducto_AC").val();
  const unidad = $("#ORGANICAunidadNecesidadProducto_AC").val();
  const precioLtKg = $("#ORGANICAprecioProducto_AC").val();
  const observaciones = $("#ORGANICAobservacionesProducto_AC").val();

  // Validar datos
  if (!subGrupo || !producto || !materiaActiva || !necesidad || !precioLtKg) {
    Swal.fire({
      title: "Error",
      text: "Todos los campos obligatorios deben ser completados",
      icon: "error",
      confirmButtonText: "Aceptar",
    });
    return;
  }

  // Calcular precio por hectárea
  const precioHa = parseFloat(necesidad) * parseFloat(precioLtKg);

  // Datos para enviar al servidor
  const datos = {
    IDMATERIA_ORGANICA: programaId,
    IDPRODUCTO: idProductoAPI,
    IDSUBGRUPO: idSubgrupoAPI,
    SUBGRUPO: subGrupo,
    PRODUCTO: producto,
    MATERIA_ACTIVA: materiaActiva,
    NECESIDADXHA: necesidad,
    UND: unidad,
    PRECIO_LTKG: precioLtKg,
    PRECIO_HA: precioHa.toFixed(2),
    OBSERVACIONES: observaciones || "",
  };

  // Determinar URL y método según si es edición o nuevo registro
  let url = "/riego/api/organica_materia/";
  let tipo = "POST";

  if (idProducto) {
    url = `/riego/api/organica_materia/${idProducto}/`;
    tipo = "PUT";
  }

  // Enviar datos mediante AJAX
  $.ajax({
    url: url,
    type: tipo,
    data: JSON.stringify(datos),
    contentType: "application/json",
    beforeSend: function () {
      // Mostrar indicador de carga
      Swal.fire({
        title: "Guardando...",
        text: "Por favor espere",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });
    },
    success: function (response) {
      // Cerrar el modal
      $("#ORGANICAmodalProducto_AC").modal("hide");

      // Mostrar mensaje de éxito
      Swal.fire({
        title: "Guardado",
        text: "El producto se ha guardado correctamente",
        icon: "success",
        confirmButtonText: "Aceptar",
      }).then(() => {
        // Refrescar la tabla de productos
        ORGANICAcargarProductosPrograma_AC(programaId);
      });
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al guardar el producto";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al guardar producto:", error);
    },
  });
}

function ORGANICAeditarProductoAutumnCrisp(idProducto) {
  // Realizar una petición AJAX para obtener los datos del producto
  $.ajax({
    url: `/riego/api/organica_materia/${idProducto}/`,
    type: "GET",
    success: function (response) {
      if (response && response.data) {
        // Obtener los datos del producto
        const producto = response.data;

        // Llenar el formulario con los datos
        $("#ORGANICAproductoId_AC").val(idProducto);
        $("#ORGANICAsubGrupoProducto_AC").val(producto.SUBGRUPO);
        $("#ORGANICAnombreProducto_AC").val(producto.PRODUCTO);
        $("#ORGANICAmateriaActivaProducto_AC").val(producto.MATERIA_ACTIVA);
        $("#ORGANICAnecesidadProducto_AC").val(producto.NECESIDADXHA);
        $("#ORGANICAunidadNecesidadProducto_AC").val(producto.UND);
        $("#ORGANICAprecioProducto_AC").val(producto.PRECIO_LTKG);
        $("#ORGANICAprecioHaProducto_AC").val(producto.PRECIO_HA);
        $("#ORGANICAobservacionesProducto_AC").val(producto.OBSERVACIONES);

        // Agregar valores a los campos ocultos
        $("#ORGANICAidProductoAC").val(producto.IDPRODUCTO || "");
        $("#ORGANICAidSubgrupoAC").val(producto.IDSUBGRUPO || "");

        // Cambiar el título del modal
        $("#ORGANICAmodalProductoLabel_AC").text("Editar Producto");

        // Mostrar el modal
        $("#ORGANICAmodalProducto_AC").modal("show");
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

function ORGANICAeliminarProductoAutumnCrisp(idProducto) {
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
      const programaId = $("#ORGANICAprogramaId_AC").val();

      // Realizar la eliminación mediante AJAX
      $.ajax({
        url: `/riego/api/organica_materia/${idProducto}/`,
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
            ORGANICAcargarProductosPrograma_AC(programaId);
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

function ORGANICAeditarFertilizacion_MC(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAmodalCrearPrograma_MC").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#ORGANICAmodalCrearProgramaLabel_MC").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#ORGANICAbtnGuardarProgramaMC").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#ORGANICAidregistro_MC").length === 0) {
        $("#ORGANICAformCrearPrograma_MC").append(
          `<input type="hidden" id="idregistro_MC" value="${idRegistro}">`
        );
      } else {
        $("#ORGANICAidregistro_MC").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#ORGANICAnombrePrograma_MC").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = ORGANICAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#ORGANICAfechaInicio_MC").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = ORGANICAformatearFechaParaInput(registro.FECHA_FIN);
        $("#ORGANICAfechaFin_MC").val(fechaFin);
      }

      // Llenar la descripción
      $("#ORGANICAdescripcion_riego_MC").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#ORGANICAidfase_MC").val(registro.IDFASE);
      $("#ORGANICAidvariedad_MC").val(registro.IDVARIEDAD);
      $("#ORGANICAidusuario").val(registro.IDUSUARIO);

      // Cargar lotes para Moscatel (idvariedad = 3) y seleccionar el lote correspondiente
      if (registro.IDLOTE) {
        ORGANICAcargarLotes(3).then(() => {
          $("#ORGANICAselectLote_MC").val(registro.IDLOTE);
        });
      } else {
        ORGANICAcargarLotes(3);
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

function ORGANICAeditarFertilizacion_SUGRA(idRegistro) {
  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAmodalCrearPrograma_SUGRA").modal("show");

      // Cambiar el título del modal para indicar que es una edición
      $("#ORGANICAmodalCrearProgramaLabel_SUGRA").html(
        '<i class="fas fa-edit mr-2"></i> Editar programa de fertilización'
      );

      // Cambiar el texto del botón de guardar
      $("#ORGANICAbtnGuardarProgramaSUGRA").html(
        '<i class="fas fa-save mr-1"></i> Actualizar'
      );

      // Agregar un campo oculto con el ID del registro si no existe
      if ($("#ORGANICAidregistro_SUGRA").length === 0) {
        $("#ORGANICAformCrearPrograma_SUGRA").append(
          `<input type="hidden" id="idregistro_SUGRA" value="${idRegistro}">`
        );
      } else {
        $("#ORGANICAidregistro_SUGRA").val(idRegistro);
      }

      // Llenar el formulario con los datos del registro
      $("#ORGANICAnombrePrograma_SUGRA").val(registro.NOMBRE);

      // Formatear las fechas para el formato yyyy-MM-dd que espera el input type="date"
      if (registro.FECHA_INICIO) {
        const fechaInicio = ORGANICAformatearFechaParaInput(registro.FECHA_INICIO);
        $("#ORGANICAfechaInicio_SUGRA").val(fechaInicio);
      }

      if (registro.FECHA_FIN) {
        const fechaFin = ORGANICAformatearFechaParaInput(registro.FECHA_FIN);
        $("#ORGANICAfechaFin_SUGRA").val(fechaFin);
      }

      // Llenar la descripción
      $("#ORGANICAdescripcion_riego_SUGRA").val(registro.DESCRIPCION || "");

      // Actualizar los campos ocultos
      $("#ORGANICAidfase_SUGRA").val(registro.IDFASE);
      $("#ORGANICAidvariedad_SUGRA").val(registro.IDVARIEDAD);
      $("#ORGANICAidusuario").val(registro.IDUSUARIO);

      // Cargar lotes para Sugra (idvariedad = 4) y seleccionar el lote correspondiente
      if (registro.IDLOTE) {
        ORGANICAcargarLotes(4).then(() => {
          $("#ORGANICAselectLote_SUGRA").val(registro.IDLOTE);
        });
      } else {
        ORGANICAcargarLotes(4);
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

function ORGANICAeliminarFertilizacion_MC(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/organica_materia/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDMATERIA_ORGANICA, 10) ===
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
          url: `/riego/api/materia_organica_dl/${idRegistro}/`,
          type: "DELETE",
          success: function (response) {
            // Mostrar mensaje de éxito
            Swal.fire(
              "¡Eliminado!",
              "El registro ha sido eliminado correctamente.",
              "success"
            );

            // Recargar la tabla correspondiente según la pestaña activa
            const nombrePestaña = ORGANICAverificarPestañaActiva_MC();
            ORGANICAiniciarTablaResumen_MC(nombrePestaña);
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

function ORGANICAeliminarFertilizacion_SUGRA(idRegistro) {
  // Primero verificar si hay productos asociados
  $.ajax({
    url: `/riego/api/organica_materia/`,
    type: "GET",
    success: function (response) {
      // Comprobar si hay datos
      if (response && response.data) {
        // Filtrar productos por el ID del programa
        const productosAsociados = response.data.filter(function (item) {
          return (
            parseInt(item.IDMATERIA_ORGANICA, 10) ===
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
          url: `/riego/api/materia_organica_dl/${idRegistro}/`,
          type: "DELETE",
          success: function (response) {
            // Mostrar mensaje de éxito
            Swal.fire(
              "¡Eliminado!",
              "El registro ha sido eliminado correctamente.",
              "success"
            );

            // Recargar la tabla correspondiente según la pestaña activa
            const nombrePestaña = ORGANICAverificarPestañaActiva_SUGRA();
            ORGANICAiniciarTablaResumen_SUGRA(nombrePestaña);
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
function ORGANICAmostrarDetallesProductos(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#ORGANICAprogramaId").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAnombreProgramaDetalle").text(programa.NOMBRE);
      $("#ORGANICAfechaInicioProgramaDetalle").text(programa.FECHA_INICIO);
      $("#ORGANICAfechaFinProgramaDetalle").text(programa.FECHA_FIN);
      $("#ORGANICAdescripcionProgramaDetalle").text(
        programa.DESCRIPCION || "Sin descripción"
      );
      $("#ORGANICAsectorProgramaDetalle").text(programa.SECTOR || "no definido");
      $("#ORGANICAloteProgramaDetalle").text(programa.LOTE_NOMBRE || "no definido");

      // Mostrar el modal
      $("#ORGANICAmodalDetalleProductos").modal("show");

      // Cargar los productos relacionados con este programa
      // Lo hacemos después de mostrar el modal para asegurar que la tabla se renderice correctamente
      ORGANICAcargarProductosPrograma(idRegistro);
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
function ORGANICAcargarProductosPrograma(idPrograma) {
  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#ORGANICAtablaDetalleProductos")) {
    $("#ORGANICAtablaDetalleProductos").DataTable().clear().destroy();
  }

  // Iniciar la tabla de productos con datos de la API
  const tabla = $("#ORGANICAtablaDetalleProductos").DataTable({
    responsive: true,
    autoWidth: false,
    pageLength: 5, // Número máximo de filas por página
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url: `/riego/api/organica_materia/`,
      type: "GET",
      dataSrc: function (json) {
        // Comprobar si hay datos
        if (!json || !json.data || json.data.length === 0) {
          return [];
        }

        // Convertir idPrograma a número para comparación segura
        const idProgramaNum = parseInt(idPrograma, 10);

        // Filtrar los datos para mostrar solo los del programa seleccionado
        const datosFiltrados = json.data.filter(function (item) {
          // Convertir el IDMATERIA_ORGANICA a número también
          const idPreFert = parseInt(item.IDMATERIA_ORGANICA, 10);

          return idPreFert === idProgramaNum;
        });

        // Actualizar contador de productos

        $("#ORGANICAtotalProductosProgramaDetalle_plantines").text(
          datosFiltrados.length
        );

        // Calcular y actualizar costo total
        let costoTotal = 0;
        datosFiltrados.forEach((item) => {
          const precioHa = parseFloat(item.PRECIO_HA || 0);
          if (!isNaN(precioHa)) {
            costoTotal += precioHa;
          }
        });

        // Formatear y mostrar el costo total
        $("#ORGANICAcostoTotalProgramaDetalle").text(`$ ${costoTotal.toFixed(2)}`);
        $("#ORGANICAtotalCostoProductos").text(`${costoTotal.toFixed(2)}`);

        return datosFiltrados;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        // Mostrar error en la interfaz
        $("#ORGANICAtablaDetalleProductos tbody").html(
          '<tr><td colspan="10" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
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
      { data: "SUBGRUPO" },
      { data: "IDPRODUCTO" },
      { data: "PRODUCTO" },
      { data: "MATERIA_ACTIVA" },
      {
        data: "NECESIDADXHA",
        className: "text-center",
        render: function (data) {
          return data ? parseFloat(data).toFixed(2) : "0.00";
        },
      },
      {
        data: "UND",
        className: "text-center",
      },
      {
        data: "PRECIO_LTKG",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      {
        data: "PRECIO_HA",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      { data: "OBSERVACIONES" },
      {
        data: null,
        className: "text-center",
        orderable: false,
        width: "120px",
        render: function (data, type, row) {
          return `
            <div class="btn-group">
              <button class="btn btn-sm btn-outline-primary btn-editar-producto" data-id="${row.ID}" title="Editar producto">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger btn-eliminar-producto" data-id="${row.ID}" title="Eliminar producto">
                <i class="fas fa-trash-alt"></i>
              </button>
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
  });

  // Agregar eventos para los botones de acción
  $("#ORGANICAtablaDetalleProductos").on("click", ".btn-editar-producto", function () {
    const idProducto = $(this).data("id");

    ORGANICAeditarProductoSweetGlobe(idProducto);
  });

  $("#ORGANICAtablaDetalleProductos").on(
    "click",
    ".btn-eliminar-producto",
    function () {
      const idProducto = $(this).data("id");

      ORGANICAeliminarProductoSweetGlobe(idProducto);
    }
  );
}

//============================================================================
// EVENTOS
//============================================================================
// Modificar la función para abrir el modal de nuevo producto
function ORGANICAabrirModalNuevoProducto_SG(idPrograma) {
  resetearFormularioProducto();
  $("#ORGANICAprogramaId").val(idPrograma);
  $("#ORGANICAmodalProducto").modal("show");
  ORGANICAinitEventosFormularioProducto_SG();
}

// Agregamos los eventos necesarios
$(document).ready(function () {
  // Verificar al abrir el modal SWEET GLOBE
  $("#ORGANICAmodalSweetGlobe").on("shown.bs.modal", function () {
    ORGANICAverificarPestañaActiva_SG();
  });

  // Verificar al abrir el modal AUTUMN CRISP
  $("#ORGANICAmodalAutumnCrisp").on("shown.bs.modal", function () {
    ORGANICAverificarPestañaActiva_AC();
  });

  $("#ORGANICAmodalMoscatel").on("shown.bs.modal", function () {
    ORGANICAverificarPestañaActiva_MC();
  });

  $("#ORGANICAmodalSugra").on("shown.bs.modal", function () {
    ORGANICAverificarPestañaActiva_SUGRA();
  });

  // Evento para el botón añadir producto
  $("#ORGANICAbtnAñadirProducto").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#ORGANICAprogramaId").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    ORGANICAabrirModalNuevoProducto_SG(programaId);
  });

  // El evento para guardar producto ahora se maneja en initEventosFormularioProducto_SG

  // Evento para calcular el precio por hectárea automáticamente
  $("#ORGANICAnecesidadProducto, #ORGANICAprecioProducto").on("input", function () {
    const necesidad = parseFloat($("#ORGANICAnecesidadProducto").val()) || 0;
    const precioLtKg = parseFloat($("#ORGANICAprecioProducto").val()) || 0;

    // Calcular el precio por hectárea
    const precioHa = necesidad * precioLtKg;

    // Actualizar el campo
    $("#ORGANICAprecioHaProducto").val(precioHa.toFixed(2));
  });

  //============================================================

  // Verificar al cambiar de pestaña SWEET GLOBE
  $('#ORGANICAsweetGlobeTabs a[data-toggle="tab"]').on("shown.bs.tab", function () {
    ORGANICAverificarPestañaActiva_SG();
  });

  // Verificar al cambiar de pestaña AUTUMN CRISP
  $("#ORGANICAautumnCrispTabs a[data-toggle='tab']").on("shown.bs.tab", function () {
    ORGANICAverificarPestañaActiva_AC();
  });

  // Verificar al cambiar de pestaña MOSCATEL
  $("#ORGANICAmoscatelTabs a[data-toggle='tab']").on("shown.bs.tab", function () {
    ORGANICAverificarPestañaActiva_MC();
  });

  // Verificar al cambiar de pestaña MOSCATEL
  $("#ORGANICAsugraTabs a[data-toggle='tab']").on("shown.bs.tab", function () {
    ORGANICAverificarPestañaActiva_SUGRA();
  });

  //============================================================

  //SWEET GLOBE - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION
  $(".ORGANICAbtnAñadirFaseSG").on("click", function () {
    // Abrir el modal de creación de programa
    $("#ORGANICAmodalCrearPrograma").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = ORGANICAverificarPestañaActiva_SG();

    // cambiar el titulo del modal
    $("#ORGANICAmodalCrearProgramaLabel").text("CREAR NUEVA FASE - " + nombrePestaña);

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    let idVariedad;
    if (nombrePestaña == "PLANTINES") {
      $("#ORGANICAidfase").val(1);
      $("#ORGANICAidvariedad").val(1);
      idVariedad = 1;
    } else if (nombrePestaña == "POST COSECHA") {
      $("#ORGANICAidfase").val(2);
      $("#ORGANICAidvariedad").val(1);
      idVariedad = 1;
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#ORGANICAidfase").val(3);
      $("#ORGANICAidvariedad").val(1);
      idVariedad = 1;
    }

    // Cargar los lotes para la variedad Sweet Globe
    ORGANICAcargarLotes(idVariedad);
  });

  // AUTUMN CRISP - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION
  $(".ORGANICAbtnAñadirFaseAC").on("click", function () {
    // Abrir el modal de creación de programa
    $("#ORGANICAmodalCrearPrograma_AC").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = ORGANICAverificarPestañaActiva_AC();

    // cambiar el titulo del modal
    $("#ORGANICAmodalCrearProgramaLabel_AC").text(
      "CREAR NUEVA FASE - " + nombrePestaña
    );

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    if (nombrePestaña == "PLANTINES") {
      $("#ORGANICAidfase_AC").val(1);
      $("#ORGANICAidvariedad_AC").val(2);
      // Cargar lotes para Autumn Crisp (idvariedad = 2)
      ORGANICAcargarLotes(2);
    } else if (nombrePestaña == "POST COSECHA") {
      $("#ORGANICAidfase_AC").val(2);
      $("#ORGANICAidvariedad_AC").val(2);
      // Cargar lotes para Autumn Crisp (idvariedad = 2)
      ORGANICAcargarLotes(2);
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#ORGANICAidfase_AC").val(3);
      $("#ORGANICAidvariedad_AC").val(2);
      // Cargar lotes para Autumn Crisp (idvariedad = 2)
      ORGANICAcargarLotes(2);
    }

    // Si estamos en modo creación, limpiar el formulario
    if (!$("#ORGANICAidregistro_AC").length) {
      // Limpiar el formulario
      $("#ORGANICAformCrearPrograma_AC")[0].reset();

      // Limpiar el selector de lotes
      $("#ORGANICAselectLote_AC").find("option:not(:first)").remove();

      // Restaurar el texto del botón
      $("#ORGANICAbtnGuardarProgramaAC").text("Guardar");
    }
  });

  //MOSCATEL - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION
  $(".ORGANICAbtnAñadirFaseMC").on("click", function () {
    // Abrir el modal de creación de programa
    $("#ORGANICAmodalCrearPrograma_MC").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = ORGANICAverificarPestañaActiva_MC();

    // cambiar el titulo del modal
    $("#ORGANICAmodalCrearProgramaLabel_MC").text(
      "CREAR NUEVA FASE - " + nombrePestaña
    );

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    if (nombrePestaña == "PLANTINES") {
      $("#ORGANICAidfase_MC").val(1);
      $("#ORGANICAidvariedad_MC").val(3);
      // Cargar lotes para Moscatel (idvariedad = 3)
      ORGANICAcargarLotes(3);
    } else if (nombrePestaña == "POST COSECHA") {
      $("#ORGANICAidfase_MC").val(2);
      $("#ORGANICAidvariedad_MC").val(3);
      // Cargar lotes para Moscatel (idvariedad = 3)
      ORGANICAcargarLotes(3);
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#ORGANICAidfase_MC").val(3);
      $("#ORGANICAidvariedad_MC").val(3);
      // Cargar lotes para Moscatel (idvariedad = 3)
      ORGANICAcargarLotes(3);
    }

    // Si estamos en modo creación, limpiar el formulario
    if (!$("#ORGANICAidregistro_MC").length) {
      // Limpiar el formulario
      $("#ORGANICAformCrearPrograma_MC")[0].reset();

      // Limpiar el selector de lotes
      $("#ORGANICAselectLote_MC").find("option:not(:first)").remove();

      // Restaurar el texto del botón
      $("#ORGANICAbtnGuardarProgramaMC").text("Guardar");
    }
  });

  //SUGRA - EVENTO PARA ABRIR EL MODAL DE CREACION DE DE LAS FASES DE FERTILIZACION

  $(".ORGANICAbtnAñadirFaseSUGRA").on("click", function () {
    // Abrir el modal de creación de programa
    $("#ORGANICAmodalCrearPrograma_SUGRA").modal("show");

    // Obtener el nombre de la pestaña actual
    const nombrePestaña = ORGANICAverificarPestañaActiva_SUGRA();

    // cambiar el titulo del modal
    $("#ORGANICAmodalCrearProgramaLabel_SUGRA").text(
      "CREAR NUEVA FASE - " + nombrePestaña
    );

    // PASAR A CAMPOS OCULTOS LA FASE Y LA VARIEDAD SEGUN LA DASE
    if (nombrePestaña == "PLANTINES") {
      $("#ORGANICAidfase_SUGRA").val(1);
      $("#ORGANICAidvariedad_SUGRA").val(4);
      // Cargar lotes para Sugra (idvariedad = 4)
      ORGANICAcargarLotes(4);
    } else if (nombrePestaña == "POST COSECHA") {
      $("#ORGANICAidfase_SUGRA").val(2);
      $("#ORGANICAidvariedad_SUGRA").val(4);
      // Cargar lotes para Sugra (idvariedad = 4)
      ORGANICAcargarLotes(4);
    } else if (nombrePestaña == "PRODUCCIÓN") {
      $("#ORGANICAidfase_SUGRA").val(3);
      $("#ORGANICAidvariedad_SUGRA").val(4);
      // Cargar lotes para Sugra (idvariedad = 4)
      ORGANICAcargarLotes(4);
    }

    // Si estamos en modo creación, limpiar el formulario
    if (!$("#ORGANICAidregistro_SUGRA").length) {
      // Limpiar el formulario
      $("#ORGANICAformCrearPrograma_SUGRA")[0].reset();

      // Limpiar el selector de lotes
      $("#ORGANICAselectLote_SUGRA").find("option:not(:first)").remove();

      // Restaurar el texto del botón
      $("#ORGANICAbtnGuardarProgramaSUGRA").text("Guardar");
    }
  });

  //============================================================

  // SWEET GLOBE - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#ORGANICAbtnGuardarProgramaSG").on("click", function () {
    ORGANICAguardarNuevoPrograma_SG();
  });

  //============================================================================
  // EVENTOS PARA GUARDAR EL NUEVO FASE
  //============================================================================

  // AUTUMN CRISP - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#ORGANICAbtnGuardarProgramaAC").on("click", function () {
    ORGANICAguardarNuevoPrograma_AC();
  });

  // MOSCATEL - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#ORGANICAbtnGuardarProgramaMC").on("click", function () {
    ORGANICAguardarNuevoPrograma_MC();
  });

  // SUGRA - EVENTO PARA GUARDAR EL NUEVO FASE DE FERTILIZACION
  $("#ORGANICAbtnGuardarProgramaSUGRA").on("click", function () {
    ORGANICAguardarNuevoPrograma_SUGRA();
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
  $("#ORGANICAselectLote_AC").on("change", function () {
    // Limpiar errores de validación
    $(this).css("border", "");
    $(this).next(".text-danger").remove();
  });

  // Evento para limpiar errores cuando se selecciona un lote en Moscatel
  $("#ORGANICAselectLote_MC").on("change", function () {
    // Limpiar errores de validación
    $(this).css("border", "");
    $(this).next(".text-danger").remove();
  });

  // Evento para limpiar errores cuando se selecciona un lote en Sugra
  $("#ORGANICAselectLote_SUGRA").on("change", function () {
    // Limpiar errores de validación
    $(this).css("border", "");
    $(this).next(".text-danger").remove();
  });

  //============================================================================
  // EVENTOS PARA EDITAR LA FASE
  //============================================================================

  $("#ORGANICAbtnEditarFertilizacion_SG").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    ORGANICAeditarFertilizacion_SG(idRegistro);
  });

  $("#btnEditarFertilizacion_AC").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    ORGANICAeditarFertilizacion_AC(idRegistro);
  });

  $("#btnEditarFertilizacion_MC").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    ORGANICAeditarFertilizacion_MC(idRegistro);
  });

  $("#btnEditarFertilizacion_SUGRA").on("click", function () {
    const idRegistro = $(this).attr("data-id");
    ORGANICAeditarFertilizacion_SUGRA(idRegistro);
  });

  //============================================================================
  // EVENTOS PARA ELIMINAR LA FASE
  //============================================================================

  // Corregir el evento del botón eliminar para que use el data-id correctamente
  $("#btnEliminarFertilizacion_SG").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    ORGANICAeliminarFertilizacion(idRegistro);
  });

  $("#btnEliminarFertilizacion_AC").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    ORGANICAeliminarFertilizacion_AC(idRegistro);
  });

  $("#btnEliminarFertilizacion_MC").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    ORGANICAeliminarFertilizacion_MC(idRegistro);
  });

  $("#btnEliminarFertilizacion_SUGRA").on("click", function () {
    const idRegistro = $(this).attr("data-id");

    ORGANICAeliminarFertilizacion_SUGRA(idRegistro);
  });

  $("#ORGANICAbtnGuardarProducto").on("click", function () {
    ORGANICAguardarProductoSweetGlobe();
  });

  // Evento para guardar producto de Autumn Crisp
  $("#ORGANICAbtnGuardarProducto_AC").on("click", function () {
    ORGANICAguardarProductoAutumnCrisp();
  });

  // Calcular precio por hectárea automáticamente para productos de Autumn Crisp
  $("#ORGANICAnecesidadProducto_AC, #ORGANICAprecioProducto_AC").on("input", function () {
    const necesidad = parseFloat($("#ORGANICAnecesidadProducto_AC").val()) || 0;
    const precioLtKg = parseFloat($("#ORGANICAprecioProducto_AC").val()) || 0;
    const precioHa = necesidad * precioLtKg;
    $("#ORGANICAprecioHaProducto_AC").val(precioHa.toFixed(2));
  });

  // Eventos para botones de editar y eliminar productos (delegación de eventos)
  $("#ORGANICAtablaDetalleProductos_AC").on(
    "click",
    ".btn-editar-producto-AC",
    function () {
      const idProducto = $(this).data("id");
      ORGANICAeditarProductoAutumnCrisp(idProducto);
    }
  );

  $("#ORGANICAtablaDetalleProductos_AC").on(
    "click",
    ".btn-eliminar-producto-AC",
    function () {
      const idProducto = $(this).data("id");
      ORGANICAeliminarProductoAutumnCrisp(idProducto);
    }
  );

  // ============================================================================
  // EVENT LISTENERS PARA PRODUCTOS MOSCATEL
  // ============================================================================

  // Evento para guardar producto de Moscatel
  $("#ORGANICAbtnGuardarProducto_MC").on("click", function () {
    ORGANICAguardarProductoMoscatel();
  });

  // Calcular precio por hectárea automáticamente para productos de Moscatel
  $("#ORGANICAnecesidadProducto_MC, #ORGANICAprecioProducto_MC").on("input", function () {
    const necesidad = parseFloat($("#ORGANICAnecesidadProducto_MC").val()) || 0;
    const precioLtKg = parseFloat($("#ORGANICAprecioProducto_MC").val()) || 0;
    const precioHa = necesidad * precioLtKg;
    $("#ORGANICAprecioHaProducto_MC").val(precioHa.toFixed(2));
  });

  // Eventos para botones de editar y eliminar productos (delegación de eventos)
  $("#ORGANICAtablaDetalleProductos_MC").on(
    "click",
    ".btn-editar-producto-MC",
    function () {
      const idProducto = $(this).data("id");
      ORGANICAeditarProductoMoscatel(idProducto);
    }
  );

  $("#ORGANICAtablaDetalleProductos_MC").on(
    "click",
    ".btn-eliminar-producto-MC",
    function () {
      const idProducto = $(this).data("id");
      ORGANICAeliminarProductoMoscatel(idProducto);
    }
  );

  // Evento para el botón Añadir Producto en el modal de detalless
  $("#ORGANICAbtnAñadirProducto_MC").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#ORGANICAprogramaId_MC").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    ORGANICAabrirModalNuevoProducto_MC(programaId);
  });

  // Evento para el botón Añadir Producto en el modal de detalles de Autumn Crisp
  $("#ORGANICAbtnAñadirProducto_AC").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#ORGANICAprogramaId_AC").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    ORGANICAabrirModalNuevoProducto_AC(programaId);
  });

  // ============================================================================
  // EVENT LISTENERS PARA PRODUCTOS SUGRA
  // ============================================================================

  // Evento para guardar producto de Sugra
  $("#ORGANICAbtnGuardarProducto_SUGRA").on("click", function () {
    ORGANICAguardarProductoSugra();
  });

  // Calcular precio por hectárea automáticamente para productos de Sugra
  $("#ORGANICAnecesidadProducto_SUGRA, #ORGANICAprecioProducto_SUGRA").on("input", function () {
    const necesidad = parseFloat($("#ORGANICAnecesidadProducto_SUGRA").val()) || 0;
    const precioLtKg = parseFloat($("#ORGANICAprecioProducto_SUGRA").val()) || 0;
    const precioHa = necesidad * precioLtKg;
    $("#ORGANICAprecioHaProducto_SUGRA").val(precioHa.toFixed(2));
  });

  // Eventos para botones de editar y eliminar productos (delegación de eventos)
  $("#ORGANICAtablaDetalleProductos_SUGRA").on(
    "click",
    ".btn-editar-producto-SUGRA",
    function () {
      const idProducto = $(this).data("id");
      ORGANICAeditarProductoSugra(idProducto);
    }
  );

  $("#ORGANICAtablaDetalleProductos_SUGRA").on(
    "click",
    ".btn-eliminar-producto-SUGRA",
    function () {
      const idProducto = $(this).data("id");
      ORGANICAeliminarProductoSugra(idProducto);
    }
  );

  // Evento para el botón Añadir Producto en el modal de detalles
  $("#ORGANICAbtnAñadirProducto_SUGRA").on("click", function () {
    // Obtener el ID del programa actual
    const programaId = $("#ORGANICAprogramaId_SUGRA").val();

    if (!programaId) {
      Swal.fire("Error", "No se ha seleccionado un programa", "error");
      return;
    }

    // Llamar a la función de abrir modal con autocompletado
    abrirModalNuevoProducto_SUGRA(programaId);
  });
});

//============================================================================
// FUNCIONES PARA GUARDAR PRODUCTOS POR VARIEDAD
//============================================================================

// Función específica para guardar productos de Sweet Globe
function ORGANICAguardarProductoSweetGlobe() {
  // Obtener el ID del programa seleccionado
  const programaId = $("#ORGANICAprogramaId").val();
  // Obtener el ID del producto si estamos editando
  const productoId = $("#ORGANICAproductoId").val();
  // Obtener los IDs de producto y subgrupo para la API
  const idProductoAPI = $("#ORGANICAidProductoSG").val() || "";
  const idSubgrupoAPI = $("#ORGANICAidSubgrupoSG").val() || "";

  // Determinar si es una edición o una creación
  const esEdicion = productoId && productoId.trim() !== "";

  if (!programaId) {
    Swal.fire("Error", "No se ha seleccionado un programa", "error");
    return false;
  }

  // Validar el formulario
  const formProducto = $("#ORGANICAformProducto")[0];
  if (!formProducto.checkValidity()) {
    formProducto.reportValidity();
    return false;
  }

  // Obtener los valores del formulario
  const subGrupo = $("#ORGANICAsubGrupoProducto").val();
  const producto = $("#ORGANICAnombreProducto").val();
  const materiaActiva = $("#ORGANICAmateriaActivaProducto").val();
  const necesidadPorHa = $("#ORGANICAnecesidadProducto").val();
  const unidad = $("#ORGANICAunidadNecesidadProducto").val();
  const precioLtKg = $("#ORGANICAprecioProducto").val();
  const precioHa = $("#ORGANICAprecioHaProducto").val();
  const observaciones = $("#ORGANICAobservacionesProducto").val() || "";

  // Crear el objeto con los datos
  const datosProducto = {
    IDMATERIA_ORGANICA: programaId,
    IDPRODUCTO: idProductoAPI,
    IDSUBGRUPO: idSubgrupoAPI,
    SUBGRUPO: subGrupo,
    PRODUCTO: producto,
    MATERIA_ACTIVA: materiaActiva,
    NECESIDADXHA: necesidadPorHa,
    UND: unidad,
    PRECIO_LTKG: precioLtKg,
    PRECIO_HA: precioHa,
    OBSERVACIONES: observaciones,
  };

  // Determinar la URL y el método según si es edición o creación
  let url = "/riego/api/organica_materia/";
  let metodo = "POST";

  if (esEdicion) {
    url = `/riego/api/organica_materia/${productoId}/`;
    metodo = "PUT";
  } else {
  }

  // Mostrar indicador de carga
  Swal.fire({
    title: esEdicion ? "Actualizando..." : "Guardando...",
    text: `Por favor espere mientras se ${
      esEdicion ? "actualiza" : "guarda"
    } el producto`,
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Enviar la petición AJAX para guardar o actualizar el producto
  $.ajax({
    url: url,
    type: metodo,
    contentType: "application/json",
    data: JSON.stringify(datosProducto),
    success: function (response) {
      // Cerrar indicador de carga
      Swal.close();

      // Mostrar mensaje de éxito
      Swal.fire({
        title: "¡Éxito!",
        text: `El producto ha sido ${
          esEdicion ? "actualizado" : "guardado"
        } correctamente`,
        icon: "success",
        confirmButtonText: "Aceptar",
      });

      // Cerrar el modal
      $("#ORGANICAmodalProducto").modal("hide");

      // Recargar la tabla de productos
      ORGANICAcargarProductosPrograma(programaId);

      return true;
    },
    error: function (xhr, status, error) {
      console.error(
        `Error al ${
          esEdicion ? "actualizar" : "guardar"
        } el producto Sweet Globe:`,
        error
      );

      // Cerrar indicador de carga
      Swal.close();

      // Mostrar mensaje de error
      let errorMsg = `Ha ocurrido un error al ${
        esEdicion ? "actualizar" : "guardar"
      } el producto`;
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

// Función para editar un producto de Sweet Globe
function ORGANICAeditarProductoSweetGlobe(idProducto) {
  // Obtener los datos del producto mediante AJAX
  $.ajax({
    url: `/riego/api/organica_materia/${idProducto}/`,
    type: "GET",
    success: function (response) {
      // Verificar si se obtuvo el producto correctamente
      if (!response || !response.data) {
        Swal.fire(
          "Error",
          "No se pudo obtener la información del producto",
          "error"
        );
        return;
      }

      // Obtener los datos del producto
      const producto = response.data;

      // Establecer el ID del producto en el formulario
      $("#ORGANICAproductoId").val(producto.ID);
      $("#ORGANICAprogramaId").val(producto.IDMATERIA_ORGANICA);

      // Establecer los IDs ocultos
      $("#ORGANICAidProductoSG").val(producto.IDPRODUCTO || "");
      $("#ORGANICAidSubgrupoSG").val(producto.IDSUBGRUPO || "");

      // Poblar los campos del formulario con los datos del producto
      $("#ORGANICAsubGrupoProducto").val(producto.SUBGRUPO || "");
      $("#ORGANICAnombreProducto").val(producto.PRODUCTO || "");
      $("#ORGANICAmateriaActivaProducto").val(producto.MATERIA_ACTIVA || "");
      $("#ORGANICAnecesidadProducto").val(producto.NECESIDADXHA || "");
      $("#ORGANICAunidadNecesidadProducto").val(producto.UND || "");
      $("#ORGANICAprecioProducto").val(producto.PRECIO_LTKG || "");
      $("#ORGANICAprecioHaProducto").val(producto.PRECIO_HA || "");
      $("#ORGANICAobservacionesProducto").val(producto.OBSERVACIONES || "");

      // Cambiar el título del modal
      $("#ORGANICAmodalProductoLabel").html(
        '<i class="fas fa-edit mr-2"></i> Editar Producto'
      );

      // Abrir el modal
      $("#ORGANICAmodalProducto").modal("show");

      // Inicializar el autocompletado y otros eventos
      ORGANICAinitEventosFormularioProducto_SG();
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al obtener los datos del producto";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al obtener datos del producto:", error);
    },
  });
}

// Función para eliminar un producto de Sweet Globe
function ORGANICAeliminarProductoSweetGlobe(idProducto) {
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

      // Enviar la petición AJAX para eliminar el producto
      $.ajax({
        url: `/riego/api/organica_materia/${idProducto}/`,
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
          const programaId = $("#ORGANICAprogramaId").val();

          // Recargar la tabla de productos
          if (programaId) {
            ORGANICAcargarProductosPrograma(programaId);
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
function ORGANICAmostrarDetallesProductos_MC(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#ORGANICAprogramaId_MC").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAnombreProgramaDetalle_MC").text(programa.NOMBRE);
      $("#ORGANICAfechaInicioProgramaDetalle_MC").text(programa.FECHA_INICIO);
      $("#ORGANICAfechaFinProgramaDetalle_MC").text(programa.FECHA_FIN);
      $("#ORGANICAdescripcionProgramaDetalle_MC").text(
        programa.DESCRIPCION || "Sin descripción"
      );

      $("#ORGANICAsectorProgramaDetalle_MC").text(programa.SECTOR || "no definido");
      $("#ORGANICAloteProgramaDetalle_MC").text(programa.LOTE_NOMBRE || "no definido");

      // Mostrar el modal

      $("#ORGANICAmodalDetalleProductos_MC").modal("show");

      // Cargar los productos relacionados con este programa
      ORGANICAcargarProductosPrograma_MC(idRegistro);
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
function ORGANICAcargarProductosPrograma_MC(idPrograma) {
  // Mostrar mensaje en la consola

  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#ORGANICAtablaDetalleProductos_MC")) {
    $("#ORGANICAtablaDetalleProductos_MC").DataTable().clear().destroy();
  }

  // Iniciar la tabla de productos con datos de la API
  const tabla = $("#ORGANICAtablaDetalleProductos_MC").DataTable({
    responsive: true,
    autoWidth: false,
    pageLength: 5, // Número máximo de filas por página
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url: `/riego/api/organica_materia/`,
      type: "GET",
      dataSrc: function (json) {
        // Comprobar si hay datos
        if (!json || !json.data || json.data.length === 0) {
          return [];
        }

        // Convertir idPrograma a número para comparación segura
        const idProgramaNum = parseInt(idPrograma, 10);

        // Filtrar los datos para mostrar solo los del programa seleccionado
        const datosFiltrados = json.data.filter(function (item) {
          // Convertir el IDMATERIA_ORGANICA a número también
          const idPreFert = parseInt(item.IDMATERIA_ORGANICA, 10);
          return idPreFert === idProgramaNum;
        });

        // Actualizar contador de productos
        $("#totalProductosProgramaDetalle_MC").text(datosFiltrados.length);

        // Calcular y actualizar costo total
        let costoTotal = 0;
        datosFiltrados.forEach((item) => {
          const precioHa = parseFloat(item.PRECIO_HA || 0);
          if (!isNaN(precioHa)) {
            costoTotal += precioHa;
          }
        });

        // Formatear y mostrar el costo total
        $("#ORGANICAcostoTotalProgramaDetalle_MC").text(`$ ${costoTotal.toFixed(2)}`);
        $("#ORGANICAtotalCostoProductos_MC").text(`${costoTotal.toFixed(2)}`);

        return datosFiltrados;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        // Mostrar error en la interfaz
        $("#ORGANICAtablaDetalleProductos_MC tbody").html(
          '<tr><td colspan="10" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
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
      { data: "SUBGRUPO" },
      { data: "IDPRODUCTO" },
      { data: "PRODUCTO" },
      { data: "MATERIA_ACTIVA" },
      {
        data: "NECESIDADXHA",
        className: "text-center",
        render: function (data) {
          return data ? parseFloat(data).toFixed(2) : "0.00";
        },
      },
      {
        data: "UND",
        className: "text-center",
      },
      {
        data: "PRECIO_LTKG",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      {
        data: "PRECIO_HA",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      { data: "OBSERVACIONES" },
      {
        data: null,
        className: "text-center",
        orderable: false,
        width: "120px",
        render: function (data, type, row) {
          return `
            <div class="btn-group">
              <button class="btn btn-sm btn-outline-primary btn-editar-producto-MC" data-id="${row.ID}" title="Editar producto">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger btn-eliminar-producto-MC" data-id="${row.ID}" title="Eliminar producto">
                <i class="fas fa-trash-alt"></i>
              </button>
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
    language: {
      processing: "Procesando...",
      lengthMenu: "Mostrar _MENU_ registros",
      zeroRecords: "No se encontraron resultados",
      emptyTable: "No hay productos disponibles para este programa",
      info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
      infoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
      infoFiltered: "(filtrado de un total de _MAX_ registros)",
      search: "Buscar:",
      infoThousands: ",",
      loadingRecords: "Cargando...",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
      aria: {
        sortAscending: ": Activar para ordenar la columna de manera ascendente",
        sortDescending:
          ": Activar para ordenar la columna de manera descendente",
      },
    },
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excel",
        text: '<i class="fas fa-file-excel"></i> Excel',
        className: "btn btn-success",
        title: `Productos del Programa ${$(
          "#ORGANICAnombreProgramaDetalle_MC"
        ).text()}`,
        exportOptions: {
          columns: [1, 2, 3, 4, 5],
        },
      },
      {
        extend: "csv",
        text: '<i class="fas fa-file-csv"></i> CSV',
        className: "btn btn-info",
        title: `Productos del Programa ${$(
          "#ORGANICAnombreProgramaDetalle_MC"
        ).text()}`,
        exportOptions: {
          columns: [1, 2, 3, 4, 5],
        },
      },
    ],
  });

  // Evento para el botón de añadir producto
  $("#ORGANICAbtnAñadirProducto_MC")
    .off("click")
    .on("click", function () {
      // Obtener el ID del programa actual
      const programaId = $("#ORGANICAprogramaId_MC").val();

      if (!programaId) {
        Swal.fire(
          "Error",
          "No se pudo identificar el programa actual",
          "error"
        );
        return;
      }

      // Inicializar los eventos del formulario
      initEventosFormularioProducto_MC();

      // Resetear formulario y campos ocultos
      resetearFormularioProducto_MC();

      // Almacenar el ID del programa
      $("#ORGANICAprogramaId_MC").val(programaId);

      // Cambiar el título del modal
      $("#ORGANICAmodalProductoLabel_MC").html(
        '<i class="fas fa-plus-circle mr-2"></i> Agregar Producto al Programa'
      );

      // Mostrar el modal
      $("#ORGANICAmodalProducto_MC").modal("show");
    });

  // Retornar la instancia de la tabla por si se necesita trabajar con ella más adelante
  return tabla;
}

//============================================================================
// FUNCIONES PARA GUARDAR, EDITAR Y ELIMINAR PRODUCTOS - MOSCATEL
//============================================================================

// Función para guardar o editar un producto de Moscatel
function ORGANICAguardarProductoMoscatel() {
  // Obtener valores del formulario
  const idProducto = $("#ORGANICAproductoId_MC").val();
  const programaId = $("#ORGANICAprogramaId_MC").val();
  // Usar valores de los campos ocultos si están disponibles
  const idProductoReal = $("#ORGANICAidProductoMC").val() || "";
  const idSubgrupo = $("#ORGANICAidSubgrupoMC").val() || "";
  // Usar campos visibles
  const subGrupo = $("#ORGANICAsubGrupoProducto_MC").val();
  const producto = $("#ORGANICAnombreProducto_MC").val();
  const materiaActiva = $("#ORGANICAmateriaActivaProducto_MC").val();
  const necesidad = $("#ORGANICAnecesidadProducto_MC").val();
  const unidad = $("#ORGANICAunidadNecesidadProducto_MC").val();
  const precioLtKg = $("#ORGANICAprecioProducto_MC").val();
  const observaciones = $("#ORGANICAobservacionesProducto_MC").val();

  // Validar datos
  if (!subGrupo || !producto || !materiaActiva || !necesidad || !precioLtKg) {
    Swal.fire({
      title: "Error",
      text: "Todos los campos obligatorios deben ser completados",
      icon: "error",
      confirmButtonText: "Aceptar",
    });
    return;
  }

  // Calcular precio por hectárea
  const precioHa = parseFloat(necesidad) * parseFloat(precioLtKg);

  // Datos para enviar al servidor
  const datos = {
    IDMATERIA_ORGANICA: programaId,
    SUBGRUPO: subGrupo,
    PRODUCTO: producto,
    MATERIA_ACTIVA: materiaActiva,
    NECESIDADXHA: necesidad,
    UND: unidad,
    PRECIO_LTKG: precioLtKg,
    PRECIO_HA: precioHa.toFixed(2),
    OBSERVACIONES: observaciones || "",
    // Agregar IDs de campos ocultos si están disponibles
    IDPRODUCTO: idProductoReal,
    IDSUBGRUPO: idSubgrupo,
  };

  // Determinar URL y método según si es edición o nuevo registro
  let url = "/riego/api/organica_materia/";
  let tipo = "POST";

  if (idProducto) {
    url = `/riego/api/organica_materia/${idProducto}/`;
    tipo = "PUT";
  }

  // Enviar datos mediante AJAX
  $.ajax({
    url: url,
    type: tipo,
    data: JSON.stringify(datos),
    contentType: "application/json",
    beforeSend: function () {
      // Mostrar indicador de carga
      Swal.fire({
        title: "Guardando...",
        text: "Por favor espere",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });
    },
    success: function (response) {
      // Cerrar el modal
      $("#ORGANICAmodalProducto_MC").modal("hide");

      // Mostrar mensaje de éxito
      Swal.fire({
        title: "Guardado",
        text: "El producto se ha guardado correctamente",
        icon: "success",
        confirmButtonText: "Aceptar",
      }).then(() => {
        // Refrescar la tabla de productos
        ORGANICAcargarProductosPrograma_MC(programaId);
      });
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al guardar el producto";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al guardar producto Moscatel:", error);
    },
  });
}

// Función para editar un producto de Moscatel
function ORGANICAeditarProductoMoscatel(idProducto) {
  // Realizar una petición AJAX para obtener los datos del producto
  $.ajax({
    url: `/riego/api/organica_materia/${idProducto}/`,
    type: "GET",
    success: function (response) {
      if (response && response.data) {
        // Obtener los datos del producto
        const producto = response.data;

        // Llenar el formulario con los datos
        $("#ORGANICAproductoId_MC").val(idProducto);
        $("#ORGANICAsubGrupoProducto_MC").val(producto.SUBGRUPO);
        $("#ORGANICAnombreProducto_MC").val(producto.PRODUCTO);
        $("#ORGANICAmateriaActivaProducto_MC").val(producto.MATERIA_ACTIVA);
        $("#ORGANICAnecesidadProducto_MC").val(producto.NECESIDADXHA);
        $("#ORGANICAunidadNecesidadProducto_MC").val(producto.UND);
        $("#ORGANICAprecioProducto_MC").val(producto.PRECIO_LTKG);
        $("#ORGANICAprecioHaProducto_MC").val(producto.PRECIO_HA);
        $("#ORGANICAobservacionesProducto_MC").val(producto.OBSERVACIONES);

        // Guardar valores en los campos ocultos
        $("#ORGANICAidProductoMC").val(producto.IDPRODUCTO || "");
        $("#ORGANICAidSubgrupoMC").val(producto.IDSUBGRUPO || "");

        // Cambiar el título del modal
        $("#ORGANICAmodalProductoLabel_MC").html(
          '<i class="fas fa-edit mr-2"></i> Editar Producto'
        );

        // Mostrar el modal
        $("#ORGANICAmodalProducto_MC").modal("show");
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
function ORGANICAeliminarProductoMoscatel(idProducto) {
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
      const programaId = $("#ORGANICAprogramaId_MC").val();

      // Realizar la eliminación mediante AJAX
      $.ajax({
        url: `/riego/api/organica_materia/${idProducto}/`,
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
            ORGANICAcargarProductosPrograma_MC(programaId);
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
function ORGANICAmostrarDetallesProductos_SUGRA(idRegistro) {
  // Guardar el ID del programa para usarlo al cargar los productos
  $("#ORGANICAprogramaId_SUGRA").val(idRegistro);

  // Obtener los datos del registro mediante AJAX
  $.ajax({
    url: `/riego/api/materia_organica_dl/${idRegistro}/`,
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
      $("#ORGANICAnombreProgramaDetalle_SUGRA").text(programa.NOMBRE);
      $("#ORGANICAfechaInicioProgramaDetalle_SUGRA").text(programa.FECHA_INICIO);
      $("#ORGANICAfechaFinProgramaDetalle_SUGRA").text(programa.FECHA_FIN);
      $("#ORGANICAdescripcionProgramaDetalle_SUGRA").text(
        programa.DESCRIPCION || "Sin descripción"
      );
      $("#ORGANICAsectorProgramaDetalle_SUGRA").text(programa.SECTOR || "no definido");
      $("#ORGANICAloteProgramaDetalle_SUGRA").text(
        programa.LOTE_NOMBRE || "no definido"
      );

      // Mostrar el modal

      $("#ORGANICAmodalDetalleProductos_SUGRA").modal("show");

      // Cargar los productos relacionados con este programa
      ORGANICAcargarProductosPrograma_SUGRA(idRegistro);
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
function ORGANICAcargarProductosPrograma_SUGRA(idPrograma) {
  // Mostrar mensaje en la consola

  // Inicializar o limpiar la tabla de productos
  if ($.fn.DataTable.isDataTable("#ORGANICAtablaDetalleProductos_SUGRA")) {
    $("#ORGANICAtablaDetalleProductos_SUGRA").DataTable().clear().destroy();
  }

  // Iniciar la tabla de productos con datos de la API
  const tabla = $("#ORGANICAtablaDetalleProductos_SUGRA").DataTable({
    responsive: true,
    autoWidth: false,
    pageLength: 5, // Número máximo de filas por página
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json",
      emptyTable: "No hay productos disponibles para este programa",
      zeroRecords: "No se encontraron productos que coincidan con la búsqueda",
    },
    ajax: {
      url: `/riego/api/organica_materia/`,
      type: "GET",
      dataSrc: function (json) {
        // Comprobar si hay datos
        if (!json || !json.data || json.data.length === 0) {
          return [];
        }

        // Convertir idPrograma a número para comparación segura
        const idProgramaNum = parseInt(idPrograma, 10);

        // Filtrar los datos para mostrar solo los del programa seleccionado
        const datosFiltrados = json.data.filter(function (item) {
          // Convertir el IDMATERIA_ORGANICA a número también
          const idPreFert = parseInt(item.IDMATERIA_ORGANICA, 10);
          return idPreFert === idProgramaNum;
        });

        // Actualizar contador de productos
        $("#totalProductosProgramaDetalle_SUGRA").text(datosFiltrados.length);

        // Calcular y actualizar costo total
        let costoTotal = 0;
        datosFiltrados.forEach((item) => {
          const precioHa = parseFloat(item.PRECIO_HA || 0);
          if (!isNaN(precioHa)) {
            costoTotal += precioHa;
          }
        });

        // Formatear y mostrar el costo total
        $("#ORGANICAcostoTotalProgramaDetalle_SUGRA").text(
          `$ ${costoTotal.toFixed(2)}`
        );
        $("#ORGANICAtotalCostoProductos_SUGRA").text(`${costoTotal.toFixed(2)}`);

        return datosFiltrados;
      },
      error: function (xhr, error, thrown) {
        console.error(
          "Error en la solicitud AJAX de productos:",
          error,
          thrown
        );
        // Mostrar error en la interfaz
        $("#ORGANICAtablaDetalleProductos_SUGRA tbody").html(
          '<tr><td colspan="10" class="text-center text-danger">Error al cargar los datos. Por favor, intente nuevamente.</td></tr>'
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
      { data: "SUBGRUPO" },
      { data: "IDPRODUCTO" },
      { data: "PRODUCTO" },
      { data: "MATERIA_ACTIVA" },
      {
        data: "NECESIDADXHA",
        className: "text-center",
        render: function (data) {
          return data ? parseFloat(data).toFixed(2) : "0.00";
        },
      },
      {
        data: "UND",
        className: "text-center",
      },
      {
        data: "PRECIO_LTKG",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      {
        data: "PRECIO_HA",
        className: "text-center",
        render: function (data) {
          return data ? `$ ${parseFloat(data).toFixed(2)}` : "$ 0.00";
        },
      },
      { data: "OBSERVACIONES" },
      {
        data: null,
        className: "text-center",
        orderable: false,
        width: "120px",
        render: function (data, type, row) {
          return `
            <div class="btn-group">
              <button class="btn btn-sm btn-outline-primary btn-editar-producto-SUGRA" data-id="${row.ID}" title="Editar producto">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger btn-eliminar-producto-SUGRA" data-id="${row.ID}" title="Eliminar producto">
                <i class="fas fa-trash-alt"></i>
              </button>
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
    language: {
      processing: "Procesando...",
      lengthMenu: "Mostrar _MENU_ registros",
      zeroRecords: "No se encontraron resultados",
      emptyTable: "No hay productos disponibles para este programa",
      info: "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
      infoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
      infoFiltered: "(filtrado de un total de _MAX_ registros)",
      search: "Buscar:",
      infoThousands: ",",
      loadingRecords: "Cargando...",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
      aria: {
        sortAscending: ": Activar para ordenar la columna de manera ascendente",
        sortDescending:
          ": Activar para ordenar la columna de manera descendente",
      },
    },
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excel",
        text: '<i class="fas fa-file-excel"></i> Excel',
        className: "btn btn-success",
        title: `Productos del Programa ${$(
          "#ORGANICAnombreProgramaDetalle_SUGRA"
        ).text()}`,
        exportOptions: {
          columns: [1, 2, 3, 4, 5],
        },
      },
      {
        extend: "csv",
        text: '<i class="fas fa-file-csv"></i> CSV',
        className: "btn btn-info",
        title: `Productos del Programa ${$(
          "#ORGANICAnombreProgramaDetalle_SUGRA"
        ).text()}`,
        exportOptions: {
          columns: [1, 2, 3, 4, 5],
        },
      },
    ],
  });

  // Evento para el botón de añadir producto
  $("#ORGANICAbtnAñadirProducto_SUGRA")
    .off("click")
    .on("click", function () {
      // Obtener el ID del programa actual
      const programaId = $("#ORGANICAprogramaId_SUGRA").val();

      if (!programaId) {
        Swal.fire(
          "Error",
          "No se pudo identificar el programa actual",
          "error"
        );
        return;
      }

      // Inicializar los eventos del formulario
      initEventosFormularioProducto_SUGRA();

      // Resetear formulario y campos ocultos
      resetearFormularioProducto_SUGRA();

      // Almacenar el ID del programa
      $("#ORGANICAprogramaId_SUGRA").val(programaId);

      // Cambiar el título del modal
      $("#ORGANICAmodalProductoLabel_SUGRA").html(
        '<i class="fas fa-plus-circle mr-2"></i> Agregar Producto al Programa'
      );

      // Mostrar el modal
      $("#ORGANICAmodalProducto_SUGRA").modal("show");
    });

  // Retornar la instancia de la tabla por si se necesita trabajar con ella más adelante
  return tabla;
}

//============================================================================
// FUNCIONES PARA GUARDAR, EDITAR Y ELIMINAR PRODUCTOS - SUGRA
//============================================================================

// Función para guardar o editar un producto de SUGRA
function ORGANICAguardarProductoSugra() {
  // Obtener valores del formulario
  const idProducto = $("#ORGANICAproductoId_SUGRA").val();
  const programaId = $("#ORGANICAprogramaId_SUGRA").val();
  // Usar valores de los campos ocultos si están disponibles
  const idProductoReal = $("#ORGANICAidProductoSUGRA").val() || "";
  const idSubgrupo = $("#ORGANICAidSubgrupoSUGRA").val() || "";
  // Usar campos visibles
  const subGrupo = $("#ORGANICAsubGrupoProducto_SUGRA").val();
  const producto = $("#ORGANICAnombreProducto_SUGRA").val();
  const materiaActiva = $("#ORGANICAmateriaActivaProducto_SUGRA").val();
  const necesidad = $("#ORGANICAnecesidadProducto_SUGRA").val();
  const unidad = $("#ORGANICAunidadNecesidadProducto_SUGRA").val();
  const precioLtKg = $("#ORGANICAprecioProducto_SUGRA").val();
  const observaciones = $("#ORGANICAobservacionesProducto_SUGRA").val();

  // Validar datos
  if (!subGrupo || !producto || !materiaActiva || !necesidad || !precioLtKg) {
    Swal.fire({
      title: "Error",
      text: "Todos los campos obligatorios deben ser completados",
      icon: "error",
      confirmButtonText: "Aceptar",
    });
    return;
  }

  // Calcular precio por hectárea
  const precioHa = parseFloat(necesidad) * parseFloat(precioLtKg);

  // Datos para enviar al servidor
  const datos = {
    IDMATERIA_ORGANICA: programaId,
    SUBGRUPO: subGrupo,
    PRODUCTO: producto,
    MATERIA_ACTIVA: materiaActiva,
    NECESIDADXHA: necesidad,
    UND: unidad,
    PRECIO_LTKG: precioLtKg,
    PRECIO_HA: precioHa.toFixed(2),
    OBSERVACIONES: observaciones || "",
    // Agregar IDs de campos ocultos si están disponibles
    IDPRODUCTO: idProductoReal,
    IDSUBGRUPO: idSubgrupo,
  };

  // Determinar URL y método según si es edición o nuevo registro
  let url = "/riego/api/organica_materia/";
  let tipo = "POST";

  if (idProducto) {
    url = `/riego/api/organica_materia/${idProducto}/`;
    tipo = "PUT";
  }

  // Enviar datos mediante AJAX
  $.ajax({
    url: url,
    type: tipo,
    data: JSON.stringify(datos),
    contentType: "application/json",
    beforeSend: function () {
      // Mostrar indicador de carga
      Swal.fire({
        title: "Guardando...",
        text: "Por favor espere",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });
    },
    success: function (response) {
      // Cerrar el modal
      $("#ORGANICAmodalProducto_SUGRA").modal("hide");

      // Mostrar mensaje de éxito
      Swal.fire({
        title: "Guardado",
        text: "El producto se ha guardado correctamente",
        icon: "success",
        confirmButtonText: "Aceptar",
      }).then(() => {
        // Refrescar la tabla de productos
        ORGANICAcargarProductosPrograma_SUGRA(programaId);
      });
    },
    error: function (xhr, status, error) {
      // Mostrar mensaje de error
      let errorMsg = "Ha ocurrido un error al guardar el producto";

      if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMsg = xhr.responseJSON.message;
      }

      Swal.fire({
        title: "Error",
        text: errorMsg,
        icon: "error",
        confirmButtonText: "Aceptar",
      });

      console.error("Error al guardar producto SUGRA:", error);
    },
  });
}

// Función para editar un producto de SUGRA
function ORGANICAeditarProductoSugra(idProducto) {
  // Realizar una petición AJAX para obtener los datos del producto
  $.ajax({
    url: `/riego/api/organica_materia/${idProducto}/`,
    type: "GET",
    success: function (response) {
      if (response && response.data) {
        // Obtener los datos del producto
        const producto = response.data;

        // Llenar el formulario con los datos
        $("#ORGANICAproductoId_SUGRA").val(idProducto);
        $("#ORGANICAsubGrupoProducto_SUGRA").val(producto.SUBGRUPO);
        $("#ORGANICAnombreProducto_SUGRA").val(producto.PRODUCTO);
        $("#ORGANICAmateriaActivaProducto_SUGRA").val(producto.MATERIA_ACTIVA);
        $("#ORGANICAnecesidadProducto_SUGRA").val(producto.NECESIDADXHA);
        $("#ORGANICAunidadNecesidadProducto_SUGRA").val(producto.UND);
        $("#ORGANICAprecioProducto_SUGRA").val(producto.PRECIO_LTKG);
        $("#ORGANICAprecioHaProducto_SUGRA").val(producto.PRECIO_HA);
        $("#ORGANICAobservacionesProducto_SUGRA").val(producto.OBSERVACIONES);

        // Guardar valores en los campos ocultos
        $("#ORGANICAidProductoSUGRA").val(producto.IDPRODUCTO || "");
        $("#ORGANICAidSubgrupoSUGRA").val(producto.IDSUBGRUPO || "");

        // Cambiar el título del modal
        $("#ORGANICAmodalProductoLabel_SUGRA").html(
          '<i class="fas fa-edit mr-2"></i> Editar Producto'
        );

        // Mostrar el modal
        $("#ORGANICAmodalProducto_SUGRA").modal("show");

        // Inicializar eventos del formulario (autocompletado)
        initEventosFormularioProducto_SUGRA();
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

// Función para eliminar un producto de SUGRA
function ORGANICAeliminarProductoSugra(idProducto) {
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
      const programaId = $("#ORGANICAprogramaId_SUGRA").val();

      // Realizar la eliminación mediante AJAX
      $.ajax({
        url: `/riego/api/organica_materia/${idProducto}/`,
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
            ORGANICAcargarProductosPrograma_SUGRA(programaId);
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

          console.error("Error al eliminar producto SUGRA:", error);
        },
      });
    }
  });
}

// Función para buscar productos para Sweet Globe
function ORGANICAbuscarproducto_SG() {
  let timeoutId;
  let sugerenciasContainer;

  // Desactivar eventos previos para evitar duplicados
  $("#ORGANICAnombreProducto").off("input");

  // Crear el contenedor de sugerencias si no existe
  if (!$("#sugerencias-producto-container").length) {
    $("body").append(
      '<div id="sugerencias-producto-container" class="sugerencias-container"></div>'
    );
    sugerenciasContainer = $("#sugerencias-producto-container");

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
        !$(e.target).closest("#sugerencias-producto-container, #ORGANICAnombreProducto")
          .length
      ) {
        sugerenciasContainer.hide();
      }
    });
  } else {
    sugerenciasContainer = $("#sugerencias-producto-container");
  }

  // Función para posicionar el contenedor de sugerencias
  function posicionarSugerencias() {
    const input = $("#ORGANICAnombreProducto");
    const inputPos = input.offset();
    sugerenciasContainer.css({
      top: inputPos.top + input.outerHeight() + "px",
      left: inputPos.left + "px",
      width: input.outerWidth() + "px",
    });
  }

  // Asociar evento de entrada al campo de producto
  $("#ORGANICAnombreProducto").on("input", function () {
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
      posicionarSugerencias();
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
            ORGANICAmostrarSugerenciasProductos_SG(response.data);
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
          console.error("Error al buscar productos:", error);
        },
      });
    }, 300); // 300ms de debounce
  });

  // Función para mostrar las sugerencias de productos
  function ORGANICAmostrarSugerenciasProductos_SG(productos) {
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
        ORGANICAseleccionarProducto_SG(producto);
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
    posicionarSugerencias();
  }

  // Función para seleccionar un producto
  function ORGANICAseleccionarProducto_SG(producto) {
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
    $("#ORGANICAnombreProducto").val(nombreProducto);
    $("#ORGANICAsubGrupoProducto").val(subgrupo);
    $("#ORGANICAmateriaActivaProducto").val(materiaActiva);
    $("#ORGANICAprecioProducto").val(
      typeof precio === "number" ? precio.toFixed(2) : precio
    );

    // Establecer valores en los campos ocultos
    $("#ORGANICAidProductoSG").val(idProducto);
    $("#ORGANICAidSubgrupoSG").val(idSubgrupo);

    // Configurar la unidad de medida según el producto
    if (idMedida) {
      const unidadFormateada = idMedida.trim().toUpperCase();
      if (unidadFormateada.includes("LT") || unidadFormateada.includes("L")) {
        $("#ORGANICAunidadNecesidadProducto").val("LT");
      } else if (unidadFormateada.includes("KG")) {
        $("#ORGANICAunidadNecesidadProducto").val("kg");
      }
    }

    // Calcular el precio por hectárea si ya hay un valor en necesidad
    calcularPrecioHa();

    // Feedback visual
    $("#ORGANICAnombreProducto")
      .addClass("is-valid")
      .parent()
      .append(
        '<small class="text-success product-selected-message">Producto seleccionado correctamente</small>'
      );

    // Eliminar mensaje después de 2 segundos
    setTimeout(function () {
      $(".product-selected-message").fadeOut(500, function () {
        $(this).remove();
        $("#ORGANICAnombreProducto").removeClass("is-valid");
      });
    }, 2000);
  }

  // Inicializar la posición del contenedor de sugerencias al cargar
  $(window).on("resize", posicionarSugerencias);
}

// Función eliminada para evitar duplicación

// Modificar la función para inicializar los eventos
function ORGANICAinitEventosFormularioProducto_SG() {
  // Inicializar la búsqueda de productos
  ORGANICAbuscarproducto_SG();

  // Calcular precio por hectárea cuando cambie la necesidad o el precio
  $("#ORGANICAnecesidadProducto, #ORGANICAprecioProducto").on("input", calcularPrecioHa);

  // Evento para guardar el producto
  $("#ORGANICAbtnGuardarProducto")
    .off("click")
    .on("click", function () {
      ORGANICAguardarProductoSweetGlobe();
    });
}

// Función para resetear el formulario de productos
function ORGANICAresetearFormularioProducto() {
  // Resetear todos los campos del formulario
  $("#ORGANICAformProducto")[0].reset();

  // Limpiar campos ocultos
  $("#ORGANICAproductoId").val("");
  $("#ORGANICAidProductoSG").val("");
  $("#ORGANICAidSubgrupoSG").val("");

  // Restaurar el título del modal para añadir (no editar)
  $("#ORGANICAmodalProductoLabel").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar Producto al Programa'
  );
}

// Función eliminada para evitar duplicación - Se usa la implementación dentro de ORGANICAbuscarproducto_SG()

// Referencia a la función seleccionarProducto_SG definida dentro de ORGANICAbuscarproducto_SG()

// Función para buscar productos para Autumn Crisp
function ORGANICAbuscarproducto_AC() {
  let timeoutId;
  let sugerenciasContainer;

  // Desactivar eventos previos para evitar duplicados
  $("#ORGANICAnombreProducto_AC").off("input");

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
          "#sugerencias-producto-container-AC, #ORGANICAnombreProducto_AC"
        ).length
      ) {
        sugerenciasContainer.hide();
      }
    });
  } else {
    sugerenciasContainer = $("#sugerencias-producto-container-AC");
  }

  // Función para posicionar el contenedor de sugerencias
  function posicionarSugerencias() {
    const input = $("#ORGANICAnombreProducto_AC");
    const inputPos = input.offset();
    sugerenciasContainer.css({
      top: inputPos.top + input.outerHeight() + "px",
      left: inputPos.left + "px",
      width: input.outerWidth() + "px",
    });
  }

  // Asociar evento de entrada al campo de producto
  $("#ORGANICAnombreProducto_AC").on("input", function () {
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
      posicionarSugerencias();
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
            mostrarSugerenciasProductos_AC(response.data);
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
  function mostrarSugerenciasProductos_AC(productos) {
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
        seleccionarProducto_AC(producto);
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
    posicionarSugerencias();
  }

  // Función para seleccionar un producto
  function seleccionarProducto_AC(producto) {
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
    $("#ORGANICAnombreProducto_AC").val(nombreProducto);
    $("#ORGANICAsubGrupoProducto_AC").val(subgrupo);
    $("#ORGANICAmateriaActivaProducto_AC").val(materiaActiva);
    $("#ORGANICAprecioProducto_AC").val(
      typeof precio === "number" ? precio.toFixed(2) : precio
    );

    // Establecer valores en los campos ocultos
    $("#ORGANICAidProductoAC").val(idProducto);
    $("#ORGANICAidSubgrupoAC").val(idSubgrupo);

    // Configurar la unidad de medida según el producto
    if (idMedida) {
      const unidadFormateada = idMedida.trim().toUpperCase();
      if (unidadFormateada.includes("LT") || unidadFormateada.includes("L")) {
        $("#ORGANICAunidadNecesidadProducto_AC").val("LT");
      } else if (unidadFormateada.includes("KG")) {
        $("#ORGANICAunidadNecesidadProducto_AC").val("kg");
      }
    }

    // Calcular el precio por hectárea si ya hay un valor en necesidad
    calcularPrecioHa_AC();

    // Feedback visual
    $("#ORGANICAnombreProducto_AC")
      .addClass("is-valid")
      .parent()
      .append(
        '<small class="text-success product-selected-message">Producto seleccionado correctamente</small>'
      );

    // Eliminar mensaje después de 2 segundos
    setTimeout(function () {
      $(".product-selected-message").fadeOut(500, function () {
        $(this).remove();
        $("#ORGANICAnombreProducto_AC").removeClass("is-valid");
      });
    }, 2000);
  }

  // Inicializar la posición del contenedor de sugerencias al cargar
  $(window).on("resize", posicionarSugerencias);
}

// Función para calcular el precio por hectárea para Autumn Crisp
function ORGANICAcalcularPrecioHa_AC() {
  const necesidad = parseFloat($("#ORGANICAnecesidadProducto_AC").val()) || 0;
  const precioLtKg = parseFloat($("#ORGANICAprecioProducto_AC").val()) || 0;
  const precioHa = necesidad * precioLtKg;
  $("#ORGANICAprecioHaProducto_AC").val(precioHa.toFixed(2));
}

// Función para inicializar los eventos del formulario de producto para Autumn Crisp
function ORGANICAinitEventosFormularioProducto_AC() {
  // Inicializar la búsqueda de productos
  ORGANICAbuscarproducto_AC();

  // Calcular precio por hectárea cuando cambie la necesidad o el precio
  $("#ORGANICAnecesidadProducto_AC, #ORGANICAprecioProducto_AC").on(
    "input",
    ORGANICAcalcularPrecioHa_AC
  );

  // El evento para guardar el producto ya está configurado en el document.ready
}

// Función para abrir el modal de nuevo producto para Autumn Crisp
function ORGANICAabrirModalNuevoProducto_AC(idPrograma) {
  ORGANICAresetearFormularioProducto_AC();
  $("#ORGANICAprogramaId_AC").val(idPrograma);
  $("#ORGANICAmodalProducto_AC").modal("show");
  ORGANICAinitEventosFormularioProducto_AC();
}

// Función para resetear el formulario de productos para Autumn Crisp
function ORGANICAresetearFormularioProducto_AC() {
  // Resetear todos los campos del formulario
  $("#ORGANICAformProducto_AC")[0].reset();

  // Limpiar campos ocultos
  $("#ORGANICAproductoId_AC").val("");
  $("#ORGANICAidProductoAC").val("");
  $("#ORGANICAidSubgrupoAC").val("");

  // Restaurar el título del modal para añadir (no editar)
  $("#ORGANICAmodalProductoLabel_AC").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar Producto al Programa'
  );
}

// Función para buscar productos para Moscatel
function ORGANICAbuscarproducto_MC() {
  let timeoutId;
  let sugerenciasContainer;

  // Desactivar eventos previos para evitar duplicados
  $("#ORGANICAnombreProducto_MC").off("input");

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
          "#sugerencias-producto-container-MC, #ORGANICAnombreProducto_MC"
        ).length
      ) {
        sugerenciasContainer.hide();
      }
    });
  } else {
    sugerenciasContainer = $("#sugerencias-producto-container-MC");
  }

  // Función para posicionar el contenedor de sugerencias
  function posicionarSugerencias() {
    const input = $("#ORGANICAnombreProducto_MC");
    const inputPos = input.offset();
    sugerenciasContainer.css({
      top: inputPos.top + input.outerHeight() + "px",
      left: inputPos.left + "px",
      width: input.outerWidth() + "px",
    });
  }

  // Asociar evento de entrada al campo de producto
  $("#ORGANICAnombreProducto_MC").on("input", function () {
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
      posicionarSugerencias();
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
            mostrarSugerenciasProductos_MC(response.data);
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
  function mostrarSugerenciasProductos_MC(productos) {
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
        seleccionarProducto_MC(producto);
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
    posicionarSugerencias();
  }

  // Función para seleccionar un producto
  function seleccionarProducto_MC(producto) {
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
    $("#ORGANICAnombreProducto_MC").val(nombreProducto);
    $("#ORGANICAsubGrupoProducto_MC").val(subgrupo);
    $("#ORGANICAmateriaActivaProducto_MC").val(materiaActiva);
    $("#ORGANICAprecioProducto_MC").val(
      typeof precio === "number" ? precio.toFixed(2) : precio
    );

    // Establecer valores en los campos ocultos
    $("#ORGANICAidProductoMC").val(idProducto);
    $("#ORGANICAidSubgrupoMC").val(idSubgrupo);

    // Configurar la unidad de medida según el producto
    if (idMedida) {
      const unidadFormateada = idMedida.trim().toUpperCase();
      if (unidadFormateada.includes("LT") || unidadFormateada.includes("L")) {
        $("#ORGANICAunidadNecesidadProducto_MC").val("LT");
      } else if (unidadFormateada.includes("KG")) {
        $("#ORGANICAunidadNecesidadProducto_MC").val("kg");
      }
    }

    // Calcular el precio por hectárea si ya hay un valor en necesidad
    calcularPrecioHa_MC();

    // Feedback visual
    $("#ORGANICAnombreProducto_MC")
      .addClass("is-valid")
      .parent()
      .append(
        '<small class="text-success product-selected-message">Producto seleccionado correctamente</small>'
      );

    // Eliminar mensaje después de 2 segundos
    setTimeout(function () {
      $(".product-selected-message").fadeOut(500, function () {
        $(this).remove();
        $("#ORGANICAnombreProducto_MC").removeClass("is-valid");
      });
    }, 2000);
  }

  // Inicializar la posición del contenedor de sugerencias al cargar
  $(window).on("resize", posicionarSugerencias);
}

// Función para calcular el precio por hectárea para Moscatel
function ORGANICAcalcularPrecioHa_MC() {
  const necesidad = parseFloat($("#ORGANICAnecesidadProducto_MC").val()) || 0;
  const precioLtKg = parseFloat($("#ORGANICAprecioProducto_MC").val()) || 0;
  const precioHa = necesidad * precioLtKg;
  $("#ORGANICAprecioHaProducto_MC").val(precioHa.toFixed(2));
}

// Función para inicializar los eventos del formulario de producto para Moscatel
function ORGANICAinitEventosFormularioProducto_MC() {
  // Inicializar la búsqueda de productos
  ORGANICAbuscarproducto_MC();

  // Calcular precio por hectárea cuando cambie la necesidad o el precio
  $("#ORGANICAnecesidadProducto_MC, #ORGANICAprecioProducto_MC").on(
    "input",
    ORGANICAcalcularPrecioHa_MC
  );

  // El evento para guardar el producto ya está configurado en el document.ready
}

// Función para abrir el modal de nuevo producto para Moscatel
function ORGANICAabrirModalNuevoProducto_MC(idPrograma) {
  ORGANICAresetearFormularioProducto_MC();
  $("#ORGANICAprogramaId_MC").val(idPrograma);
  $("#ORGANICAmodalProducto_MC").modal("show");
  ORGANICAinitEventosFormularioProducto_MC();
}

// Función para resetear el formulario de productos para Moscatel
function ORGANICAresetearFormularioProducto_MC() {
  // Resetear todos los campos del formulario
  $("#ORGANICAformProducto_MC")[0].reset();

  // Limpiar campos ocultos
  $("#ORGANICAproductoId_MC").val("");
  $("#ORGANICAidProductoMC").val("");
  $("#ORGANICAidSubgrupoMC").val("");

  // Restaurar el título del modal para añadir (no editar)
  $("#ORGANICAmodalProductoLabel_MC").html(
    '<i class="fas fa-plus-circle mr-2"></i> Agregar Producto al Programa'
  );
}

// Función para posicionar el contenedor de sugerencias (separada para mayor claridad)
function ORGANICAposicionarSugerencias_SUGRA() {
  const input = $("#ORGANICAnombreProducto_SUGRA");
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
function ORGANICAbuscarproducto_SUGRA() {
  let timeoutId;
  let sugerenciasContainer;

  // Desactivar eventos previos para evitar duplicados
  $("#ORGANICAnombreProducto_SUGRA").off("input");

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
          "#sugerencias-producto-container-SUGRA, #ORGANICAnombreProducto_SUGRA"
        ).length
      ) {
        sugerenciasContainer.hide();
      }
    });

  // Asociar evento de entrada al campo de producto
  $("#ORGANICAnombreProducto_SUGRA").on("input", function () {
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
      posicionarSugerencias_SUGRA();
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
    posicionarSugerencias_SUGRA();
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
    $("#ORGANICAnombreProducto_SUGRA").val(nombreProducto);
    $("#ORGANICAsubGrupoProducto_SUGRA").val(subgrupo);
    $("#ORGANICAmateriaActivaProducto_SUGRA").val(materiaActiva);
    $("#ORGANICAprecioProducto_SUGRA").val(
      typeof precio === "number" ? precio.toFixed(2) : precio
    );

    // Si la necesidad está vacía, establecerla a 1 por defecto
    if (!$("#ORGANICAnecesidadProducto_SUGRA").val()) {
      $("#ORGANICAnecesidadProducto_SUGRA").val("1");
    }

    // Establecer valores en los campos ocultos
    $("#ORGANICAidProducto_SUGRA").val(idProducto);
    $("#idSubGrupo_SUGRA").val(idSubgrupo);

    // Calcular el precio por hectárea
    calcularPrecioHa_SUGRA();

    // Feedback visual
    $("#ORGANICAnombreProducto_SUGRA")
      .addClass("is-valid")
      .parent()
      .append(
        '<small class="text-success product-selected-message">Producto seleccionado correctamente</small>'
      );

    // Eliminar mensaje después de 2 segundos
    setTimeout(function () {
      $(".product-selected-message").fadeOut(500, function () {
        $(this).remove();
        $("#ORGANICAnombreProducto_SUGRA").removeClass("is-valid");
      });
    }, 2000);
  }

  // Inicializar la posición del contenedor de sugerencias al cargar
  $(window).on("resize", posicionarSugerencias_SUGRA);
}

// Función para calcular el precio por hectárea para SUGRA
function ORGANICAcalcularPrecioHa_SUGRA() {
  const necesidad = parseFloat($("#ORGANICAnecesidadProducto_SUGRA").val()) || 0;
  const precioUnidad = parseFloat($("#ORGANICAprecioProducto_SUGRA").val()) || 0;
  const precioHa = necesidad * precioUnidad;

  // Formatear con 2 decimales y actualizar el campo correcto
  $("#precioHa_SUGRA").val(precioHa.toFixed(2));
  $("#ORGANICAprecioHaProducto_SUGRA").val(precioHa.toFixed(2));
}

// Función para resetear el formulario producto SUGRA
function ORGANICAresetearFormularioProducto_SUGRA() {
  $("#ORGANICAformProducto_SUGRA")[0].reset();
  $("#ORGANICAidProducto_SUGRA").val("");
  $("#idSubGrupo_SUGRA").val("");
  $("#ORGANICAprogramaId_SUGRA").val("");
}

// Función para abrir el modal de nuevo producto para SUGRA
function ORGANICAabrirModalNuevoProducto_SUGRA(idPrograma) {
  // Resetear formulario y establecer ID del programa
  ORGANICAresetearFormularioProducto_SUGRA();
  $("#ORGANICAprogramaId_SUGRA").val(idPrograma);

  // Eliminar eventos anteriores para evitar duplicados
  $("#ORGANICAmodalProducto_SUGRA").off("shown.bs.modal");

  // Prevenir inicialización múltiple
  $(document).off("input", "#ORGANICAnombreProducto_SUGRA");

  // Limpiar sugerencias anteriores
  $("#sugerencias-producto-container-SUGRA").remove();

  // Mostrar el modal directamente (sin usar eventos)
  $("#ORGANICAmodalProducto_SUGRA").modal({
    backdrop: "static",
    keyboard: false,
    show: true,
  });

  // Esperar a que el modal esté visible y luego inicializar los eventos
  $("#ORGANICAmodalProducto_SUGRA").on("shown.bs.modal", function () {
    // Inicializar todos los eventos del formulario
    ORGANICAinitEventosFormularioProducto_SUGRA();
  });
}

// Nueva función para inicializar todos los eventos del formulario de productos SUGRA
function ORGANICAinitEventosFormularioProducto_SUGRA() {
  // Inicializar la búsqueda de productos
  ORGANICAbuscarproducto_SUGRA();

  // Calcular precio por hectárea cuando cambie la necesidad o el precio
  $("#ORGANICAnecesidadProducto_SUGRA, #ORGANICAprecioProducto_SUGRA")
    .off("input")
    .on("input", ORGANICAcalcularPrecioHa_SUGRA);

  // Forzar foco en el campo de búsqueda
  $("#ORGANICAnombreProducto_SUGRA").focus();
}

// Al cargar el documento, inicializar las funciones principales
$(document).ready(function () {
  // Inicializar pestañas SUGRA si existen
  if ($("#ORGANICAsugraTabs").length > 0) {
    ORGANICAverificarPestañaActiva_SUGRA();

    // Asociar evento a los cambios de pestaña
    $("#ORGANICAsugraTabs a[data-toggle='tab']").on("shown.bs.tab", function (e) {
      ORGANICAverificarPestañaActiva_SUGRA();
    });
  }

  // Inicializar también las otras variedades si existen
  if ($("#ORGANICAsweetGlobeTabs").length > 0) {
    ORGANICAverificarPestañaActiva_SG();
  }

  if ($("#ORGANICAautumnCrispTabs").length > 0) {
    ORGANICAverificarPestañaActiva_AC();
  }

  if ($("#ORGANICAmoscatelTabs").length > 0) {
    ORGANICAverificarPestañaActiva_MC();
  }
});

//============================================================

// BOTON CERRAR MODAL FACE  SUGRA
$('[data-click="panel-remove-face-sugra"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalSugra").modal("hide");
});

// BOTON CERRAR MODAL CREAR FACE SUGRA
$('[data-click="panel-remove-crear-programa-sugra"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalCrearPrograma_SUGRA").modal("hide");
});

// BOTON CERRAR MODAL  DETALLE PRODUCTOS SUGRA
$('[data-click="panel-remove-detalle-productos-sugra"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalDetalleProductos_SUGRA").modal("hide");
});

//============================================================

// BOTON CERRAR MODAL FACE  SWEET GLOBE
$('[data-click="panel-remove-face-sweet-globe"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalSweetGlobe").modal("hide");
});

// BOTON CERRAR MODAL CREAR PROGRAMA SWEET GLOBE
$('[data-click="panel-remove-crear-programa-sweet-globe"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalCrearPrograma").modal("hide");
});

// BOTON CERRAR MODAL  DETALLE PRODUCTOS SWEET GLOBE
$('[data-click="panel-remove-detalle-productos-sweet-globe"]').click(function (
  e
) {
  e.stopPropagation();
  $("#ORGANICAmodalDetalleProductos").modal("hide");
});

//============================================================

// BOTON CERRAR MODAL FACE  AUTUMN CRISP
$('[data-click="panel-remove-face-autumn-crisp"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalAutumnCrisp").modal("hide");
});

$('[data-click="panel-remove-crear-programa-autumn-crisp"]').click(function (
  e
) {
  e.stopPropagation();
  $("#ORGANICAmodalCrearPrograma_AC").modal("hide");
});

// BOTON CERRAR MODAL  DETALLE PRODUCTOS AUTUMN CRISP
$('[data-click="panel-remove-detalle-productos-autumn-crisp"]').click(function (
  e
) {
  e.stopPropagation();
  $("#ORGANICAmodalDetalleProductos_AC").modal("hide");
});

//============================================================

// BOTON CERRAR MODAL FACE  MOSCATEL
$('[data-click="panel-remove-face-moscatel"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalMoscatel").modal("hide");
});

$('[data-click="panel-remove-crear-programa-moscatel"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalCrearPrograma_MC").modal("hide");
});

// BOTON CERRAR MODAL  DETALLE PRODUCTOS MOSCATEL
$('[data-click="panel-remove-detalle-productos-moscatel"]').click(function (e) {
  e.stopPropagation();
  $("#ORGANICAmodalDetalleProductos_MC").modal("hide");
});

//============================================================
// FUNCIONES PARA SELECCIÓN DE LOTES
//============================================================

/**
 * Cargar lotes desde el backend para el selector
 * @param {number} idVariedad - ID de la variedad para filtrar lotes
 * @param {string} selectorId - ID del selector donde cargar los lotes (opcional)
 */

function ORGANICAcargarLotes(idVariedad, selectorId = null, idCampania = null, idEmpresa = null) {
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
        idempresa: 1,
      },

      success: function (response) {

        let selectLote;

        if (selectorId) {
          selectLote = $(selectorId);
        } else {

          if (idVariedad === 1) {
            selectLote = $("#ORGANICAselectLote");

          } else if (idVariedad === 2) {
            selectLote = $("#ORGANICAselectLote_AC");

          } else if (idVariedad === 3) {
            selectLote = $("#ORGANICAselectLote_MC");

          } else if (idVariedad === 4) {
            selectLote = $("#ORGANICAselectLote_SUGRA");

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
function formatearMoneda(valor) {
  if (isNaN(valor) || valor === null || valor === undefined) {
    return "$ 0.00";
  }
  return `$ ${parseFloat(valor).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

// Función para actualizar estadísticas de plantines Sweet Globe
function ORGANICAactualizarEstadisticasPlantines_SG(datos) {
  // Calcular número de registros
  const numRegistros = datos.length;

  $("#ORGANICAfacesRegistradosSG_PLANTINES").text(numRegistros);

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
            url: `/riego/api/organica_materia/`,
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
    $("#ORGANICAprecioTotalSG_PLANTINES").text(formatearMoneda(precioTotalPorLtKg));
    $("#ORGANICAcostoTotalSG_PLANTINES").text(formatearMoneda(precioTotalPorHa));
  };

  // Iniciar el procesamiento de programas
  if (numRegistros > 0) {
    procesarProgramas().catch((error) => {
      console.error("Error al procesar programas:", error);
      // En caso de error, mostrar valores en cero
      $("#ORGANICAprecioTotalSG_PLANTINES").text("$ 0.00");
      $("#ORGANICAcostoTotalSG_PLANTINES").text("$ 0.00");
    });
  } else {
    // Si no hay registros, mostrar valores en cero
    $("#ORGANICAprecioTotalSG_PLANTINES").text("$ 0.00");
    $("#ORGANICAcostoTotalSG_PLANTINES").text("$ 0.00");
  }
}
