$(document).ready(function () {
  // Inicializar DataTables
  function returnApproveOrders() {
    $("#lst_aplfitosanitarias_diario").DataTable({
      dom: "Bfrtip",
      buttons: [
        {
          extend: "excelHtml5",
          title: "Presupuesto - TIC",
          text: '<i class="far fa-file-excel"></i> Excel',
          className: "btn-sm btn-success",
          excelStyles: [
            {
              template: "green_medium",
            },
            {
              cells: "sh",
              style: {
                font: {
                  size: 12,
                  b: false,
                },
                fill: {
                  pattern: {
                    color: "74ac48",
                  },
                },
              },
            },
          ],
        },
      ],
      scrollX: false,
      scrollCollapse: true,
      fixedColumns: true,
      serverSide: false, // Ajusta según tu configuración
      ajax: {
        url: "/fitosanidad_apl_diario_data/",
        dataSrc: "",
      },
      searching: false,
      lengthChange: false,
      pageLength: 12,
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
        { data: "IDENTIFICADOR" },
        { data: "ALMACEN" },
        { data: "SUCURSAL" },
        { data: "FECHA" },
        { data: "DOCUMENTO" },
        { data: "CONSUMIDOR" },
        { data: "RESPONSABLE" },
        { data: "ESTADO_DESCRIPCION" },
        {
          data: null,
          render: function (data, type, row) {
            return (
              '<button class="btn btn-info btn-sm ver-detalles" data-id="' +
              row.IDENTIFICADOR +
              '" data-toggle="modal" data-target="#detallesModal">' +
              '<i class="fas fa-eye"></i> Ver detalles</button>'
            );
          },
        },
      ],
      destroy: true,
    });
  }

  returnApproveOrders();

  // Inicializar la tabla de detalles en el modal
  var detallesTable = $("#lst_det_aplfitosanitarias_diario").DataTable({
    columns: [
      { data: "ITEM" },
      { data: "DESCRIPCION" },
      { data: "MEDIDA" },
      { data: "Ing_Act" },
      { data: "DESCRIPCION_IAC" },
      { data: "UAC" },
      { data: "Dosis_x_Ha" },
      { data: "Total_Dosis" },
      { data: "DOSIS" },
      { data: "OBJETIVO" },
      { data: "DOSIS_FRACC" },
      { data: "SECTOR" },
      { data: "DOSIS_x_CILINDRO" },
      { data: "Dias_Carencia" },
      { data: "REINGRESO" },
      { data: "FRECUENCIA" },
      { data: "OBSERVACIONES" },
    ],
    paging: false,
    searching: false,
    info: false,
  });

  // Manejador de eventos para el botón "Ver detalles"
  $("#lst_aplfitosanitarias_diario").on("click", ".ver-detalles", function () {
    var identificador = $(this).data("id");
    cargarDetalles(identificador);
  });

  function cargarDetalles(identificador) {
    $.ajax({
      url: "/fitosanidad_apl_diario_data_detalle/" + identificador + "/",
      method: "GET",
      dataType: "json",
      success: function (data) {
        llenarModalConDetalles(data);
      },
      error: function (xhr, status, error) {
        console.error("Error al cargar los detalles:", error);
      },
    });
  }

  function llenarModalConDetalles(data) {
    if (data.length > 0) {
      var primerRegistro = data[0];

      // Llenar los campos del modal con la información del primer registro
      $("#detallesModal input").val(""); // Limpiar todos los campos primero

      // Sucursal
      $('#detallesModal input[name="sucursal_codigo"]').val(
        primerRegistro.IDSUCURSAL
      );
      $('#detallesModal input[name="sucursal_nombre"]').val(
        primerRegistro.SUCURSAL_NOMBRE
      );

      // Almacén
      $('#detallesModal input[name="almacen_codigo"]').val(
        primerRegistro.IDALMACEN
      );
      $('#detallesModal input[name="almacen_nombre"]').val(
        primerRegistro.ALMACEN_NOMBRE
      );

      // Documento, Serie y Número
      $('#detallesModal input[name="documento"]').val(primerRegistro.DOCUMENTO);
      $('#detallesModal input[name="serie"]').val(primerRegistro.SERIE);
      $('#detallesModal input[name="numero"]').val(primerRegistro.NUMERO);

      // Fechas
      $('#detallesModal input[name="fecha_doc"]').val(
        formatearFecha(primerRegistro.FECHA_DOC)
      );
      $('#detallesModal input[name="fecha_apl"]').val(
        formatearFecha(primerRegistro.FECHA_APL)
      );

      // Lote
      $('#detallesModal input[name="lote_codigo"]').val(primerRegistro.LOTE);
      $('#detallesModal input[name="lote_nombre"]').val(
        primerRegistro.LOTE_NOMBRE
      );

      // Área y Gasto
      $('#detallesModal input[name="area"]').val(primerRegistro.AREA);
      $('#detallesModal input[name="gasto"]').val(primerRegistro.GASTO);

      // Fecha de Cosecha
      $('#detallesModal input[name="fecha_cosecha"]').val(
        formatearFecha(primerRegistro.FECHACOSECHA)
      );

      // Tipo de Aplicación
      $('#detallesModal input[name="tipo_aplicacion_codigo"]').val(
        primerRegistro.IDTIPOAPLICACION
      );
      $('#detallesModal input[name="tipo_aplicacion_nombre"]').val(
        primerRegistro.TIPO_APL
      );

      // Tanque de Aplicación
      $('#detallesModal input[name="tanque_aplicacion_codigo"]').val(
        primerRegistro.IDTANQUE
      );
      $('#detallesModal input[name="tanque_aplicacion_nombre"]').val(
        primerRegistro.TANQUE_APL
      );

      // Litros, Cantidad y Total
      $('#detallesModal input[name="litros"]').val(primerRegistro.LITROS);
      $('#detallesModal input[name="cantidad"]').val(
        primerRegistro.CANTENVASES
      );
      $('#detallesModal input[name="total"]').val(primerRegistro.TOTAL);

      // Reingreso
      $('#detallesModal input[name="reingreso"]').val(primerRegistro.REINGRESO);

      // Responsable
      $('#detallesModal input[name="responsable_codigo"]').val(
        primerRegistro.IDRESPONSABLE
      );
      $('#detallesModal input[name="responsable_nombre"]').val(
        primerRegistro.RESPONSABLE
      );

      // Limpiar y llenar la tabla de detalles con todos los registros
      detallesTable.clear().rows.add(data).draw();

      // Mostrar el modal
      $("#detallesModal").modal("show");
    } else {
      console.error("No se recibieron datos del servidor");
    }
  }

  function formatearFecha(fechaString) {
    if (!fechaString) return "";
    var fecha = new Date(fechaString);
    return fecha.toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
});
