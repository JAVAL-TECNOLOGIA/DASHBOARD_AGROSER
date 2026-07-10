function returnApproveOrders() {
  let allData = [];
  let table_show = $("#t_libro_mayor_ajs").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excelHtml5",
        title: "LIBRO MAYOR - CAMPO VERDE",
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
    serverSide: true, // Habilitar el procesamiento del lado del servidor
    ajax: {
      url: "/libro_mayor_conta_script_ajs/",
      type: "GET",
      dataSrc: function (json) {
        allData = json.data;
        return json.data;
      },
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
      { data: "IDCUENTA" },
      { data: "NOMBRE_CTA" },
      { data: "IDCCOSTO" },
      { data: "DESC_CCOSTO" },
      { data: "PERIODO" },
      { data: "ORIGEN" },
      { data: "VOUCHER" },
      { data: "FECHA" },
      { data: "DOCUMENTO" },
      { data: "GLOSA" },
      { data: "IDCABCONTA" },
      { data: "IDREF" },
      { data: "TABLAREF" },
      { data: "CARGO_MOF" },
      { data: "ABONO_MOF" },
      { data: "SALDO_MOF" },
      { data: "CARGO_MEX" },
      { data: "ABONO_MEX" },
      { data: "SALDO_MEX" },
      { data: "INI_CARGO_MOF" },
      { data: "INI_ABONO_MOF" },
      { data: "INI_CARGO_MEX" },
      { data: "INI_ABONO_MEX" },
      { data: "CARGO" },
      { data: "ABONO" },
      { data: "SALDO" },
      { data: "CARGO1" },
      { data: "ABONO1" },
      { data: "SALDO1" },
      { data: "IDOPERACION" },
      { data: "NOMBRE_OPERA" },
      { data: "NUMERO_OPERA" },
      { data: "IDCLIEPROV" },
      { data: "RAZONSOCIAL" },
      { data: "COD_MONEDA" },
      { data: "MONEDA" },
      { data: "REFERENCIA" },
      { data: "IDENTIFICADOR" },
      { data: "ORDEN" },
      { data: "FECHA_DOC" },
      { data: "IDACTIVO" },
      { data: "IDPRODUCTO" },
      { data: "RAZONSOCIAL2" },
      { data: "FECHA_REFERENCIA" },
      { data: "unidad_negocio" },
      { data: "observacion" },
      { data: "lote_ref" },
      { data: "cantidad" },
      { data: "item" },
      { data: "idconsumidor" },
      { data: "desc_consumidor" },
      { data: "idactividad" },
      { data: "desc_actividad" },
      { data: "idlabor" },
      { data: "desc_labor" },
      { data: "es_gasto_nodeducible" },
      { data: "PRODUCTO" },
      { data: "PRECIO_MOF" },
      { data: "PRECIO_MOEX" },
      { data: "IDCUENTA_EQUIVALENTE" },
      { data: "DESCRIPCION_EQUIVALENTE" },
    ],
    destroy: true,
  });

  // Cargar datos en segundo plano
  function loadAdditionalData() {
    $.ajax({
      url: "/libro_mayor_conta_script_ajs/",
      type: "GET",
      success: function (json) {
        allData = allData.concat(json.data);
      },
    });
  }

  // Llamar a la función para cargar datos adicionales
  loadAdditionalData();
}

returnApproveOrders();
