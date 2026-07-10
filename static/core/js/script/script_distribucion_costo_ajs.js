function returnApproveOrders() {
  table_show = $("#table_dic_costo_ajs").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "REPORTES_DISTRIBUCION_COSTOS_DETALLADO- AJS",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        excelStyles: [
          // Add an excelStyles definition
          {
            template: "green_medium", // Apply the 'green_medium' template
          },
          {
            cells: "sh", // Use Smart References (s) to target the header row (h)
            style: {
              // The style definition
              font: {
                // Style the font
                size: 14, // Size 14
                b: false, // Turn off the default bolding of the header row
              },
              fill: {
                // Style the cell fill
                pattern: {
                  // Add a pattern (default is solid)
                  color: "74ac48", // Define the fill color
                },
              },
            },
          },
        ],
      },
    ],
    sScrollX: "200%",
    sScrollXInner: "250%",
    autoWidth: true,
    scrollX: true,
    scrollCollapse: true,

    fixedColumns: true,
    processing: true, // Habilitar el mensaje de procesamiento

    ajax: {
      url: "/distribucion_costos_detallado_AJS_script/",
      dataSrc: "",
    },
    searching: false,
    lengthChange: false,
    pageLength: 15,
    ordering: true,
    order: [[1, "desc"]],
    language: {
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
    },
    columns: [
      { data: "idempresa" },
      { data: "idcabconta" },
      { data: "idemisor" },
      { data: "periodo" },
      { data: "idsubdiario" },
      { data: "voucher" },
      { data: "fecha" },
      { data: "glosa" },
      { data: "tablaorigen" },
      { data: "idorigen" },
      { data: "idmoneda" },
      { data: "tcambio" },
      { data: "cargo" },
      { data: "abono" },
      { data: "fechacreacion" },
      { data: "sincroniza" },
      { data: "idestado" },
      { data: "centralizado" },
      { data: "ventana" },
      { data: "contabilizado" },
      { data: "es_apertura" },
      { data: "es_cierre" },
      { data: "idclieprov" },
      { data: "iddocumento" },
      { data: "idctareclasific" },
      { data: "idctacobranza" },
      { data: "idctaprovision" },
      { data: "idccosto" },
      { data: "TCMONEDA" },
      { data: "CORRELATIVO_PLE" },
      { data: "IDINGRESOSALIDAACTIVO" },
      { data: "viene_cierre" },
      { data: "tipo_cierre" },
      { data: "idcierre" },
      { data: "IDTIPOMEDIOPAGO" },
      { data: "idtransf_23" },
      { data: "idprocesogenaplicacion" },
      { data: "observaciones" },
      { data: "idreferencia" },
      { data: "tablaref" },
      { data: "docreferencia" },
      { data: "ventana_ref" },
      { data: "idcontrato" },
      { data: "numversion" },
      { data: "idclaseccosto_distribucion" },
      { data: "origen_distribucion" },
      { data: "idorigen2" },
      { data: "idplantillacierre" },
    ],
    destroy: true,
  });
}

returnApproveOrders();
