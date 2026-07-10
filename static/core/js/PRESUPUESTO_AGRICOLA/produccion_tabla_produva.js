$(document).ready(function () {
  initTablaProdUva();

  $('#btnReloadProduccion, #recargarTablaProdUva').on('click', function () {
    $('#tablaProdUva').DataTable().ajax.reload(null, false);
  });
});

function initTablaProdUva() {
  if ($.fn.DataTable.isDataTable('#tablaProdUva')) {
    $('#tablaProdUva').DataTable().destroy();
  }
  
  var table = $('#tablaProdUva').DataTable({
    ajax: {
      url: '/presupuesto-agricola/api/list_produva/',
      dataSrc: function (json) {
        if (Array.isArray(json)) return json;
        if (json && Array.isArray(json.data)) return json.data;
        console.error('Estructura de respuesta inesperada:', json);
        return [];
      },
      error: function (xhr) {
        console.error('Error al cargar datos:', xhr.responseText || xhr.statusText);
        alert('No se pudieron cargar los datos de producción.');
      }
    },
    columns: [
      { data: 'ID_PRODUVA' },
      { data: 'RENDIMIENTO' },
      { data: 'RAC_PLANTA' },
      { data: 'RAC_LOTE' },
      { data: 'RAC_PACKING' },
      { data: 'RAC_NACIONAL' },
      { data: 'PESO_RAC' },
      { data: 'KG_PROYEC_LOTE' },
      { data: 'KG_EXPOR_LOTE' },
      { data: 'KG_DESC_CAMP_LOTE' },
      { data: 'KG_DESC_PROC_LOTE' },
      { data: 'KG_PROYEC_HA' },
      { data: 'KG_EXPOR_HA' },
      { data: 'KG_DESC_CAMP_HA' },
      { data: 'KG_DESC_PROC_HA' },
      { data: 'CAJ_LOTE' },
      { data: 'CAJ_HA' },
      { data: 'CANT' },
      { data: 'PORC' },
      { data: 'ENV_FRU_PACK' },
      { data: 'TOTAL_KG_ENV' },
      { data: 'CAJAS' },
      { data: 'ID_DETALLE' }
    ],
    language: { url: window.dataTableEsUrl || "" },
    pageLength: 10,
    scrollX: true,
    processing: true,
    deferRender: true,
    drawCallback: function(settings) {
      $('#tablaProdUva tbody tr.fila-totales').remove();

      var api = this.api();
      var num = v => typeof v === 'string' ? (parseFloat(v.replace(/[^\d.-]/g, '')) || 0) : (typeof v === 'number' ? v : 0);
      var sumCols = [
        7,8,9,10,11,12,13,14,15,16,17,20,21
      ];
      var totals = [];
      for (let i = 0; i < 22; i++) {
        if (i === 0) {
          totals.push('<b class="text-end">Totales:</b>');
        } else if (sumCols.includes(i)) {
          const total = api.column(i, { page: 'current' }).data().reduce((a, b) => num(a) + num(b), 0);
          const decimals = (i >= 7 && i <= 14) || i === 20 ? 3 : 0;
          totals.push('<b>' + total.toFixed(decimals) + '</b>');
        } else if (i === 18) {
          // PORC promedio
          const porcData = api.column(i, { page: 'current' }).data();
          let porcAvg = 0;
          if (porcData.length) {
            const sumPorc = porcData.reduce((a, b) => num(a) + num(b), 0);
            porcAvg = sumPorc / porcData.length;
          }
          totals.push('<b>' + porcAvg.toFixed(2) + '%</b>');
        } else {
          totals.push('');
        }
      }
      $('#tablaProdUva tbody').append('<tr class="fila-totales">' + totals.map(td => `<td>${td}</td>`).join('') + '</tr>');
    }
  });
}
