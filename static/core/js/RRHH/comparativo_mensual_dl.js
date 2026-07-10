/*$(document).ready(function () {
  $.ajax({
    url: '/rrhh/api/rpt-remuneracion/?area=12&tipo=1', // cambia tipo según necesites
    method: 'GET',
    success: function (resp) {
      const rows = (resp.data || []).map(x => ({
        mes: x.mes,
        presupuesto: Number(x.presupuesto || 0)
      }));

      $('#dtTest').DataTable({
        data: rows,
        columns: [
          { data: 'mes', title: 'Mes' },
          { data: 'presupuesto', title: 'Presupuesto', className: 'dt-right',
            render: function (v) {
              return 'S/ ' + Number(v).toLocaleString('es-PE', {minimumFractionDigits:2});
            }
          }
        ],
        paging: true,
        searching: true,
        ordering: true,
        info: true,
        dom: 'Bfrtip', // B: Buttons, f: filter, r: processing, t: table, i: info, p: paging
        buttons: [
          { extend: 'excelHtml5', className: 'btn btn-success', title: 'Presupuesto_Mensual' }
        ],
        language: { url: 'https://cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json' }
      });
    },
    error: function (err) {
      console.error('API error', err);
    }
  });
});*/




(function () {
  const TAB_ID   = '#default-tab-6';
  const TABLE_ID = '#dtConsolidado';
  const API_URL  = '/rrhh/api/rpt-remuneracion/'; // GET ?area=12&tipo=1|2



  // Utiles
  const MESES = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SETIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'];
  const normMes = s => String(s||'').trim().toUpperCase().replace('SEPTIEMBRE','SETIEMBRE');
  const money   = n => (n==null || isNaN(n)) ? '-' : 'S/ ' + Number(n).toLocaleString('es-PE', { minimumFractionDigits:2 });
  const badge   = v => v==null ? '-' : `<span class="badge ${v<=0?'badge-success':'badge-danger'}">${money(v)}</span>`;


  // === API: ahora el backend devuelve { mes, presupuesto } (Consolidado_Mes = presupuesto)

  async function fetchSP(params) {
      const { area, fuente, tipo, id_tipo, id } = params;

      const qs = new URLSearchParams({
        area: String(area),
        fuente: fuente
      });

      if (typeof tipo === 'number') qs.append('tipo', tipo);
      if (typeof id_tipo === 'number') qs.append('id_tipo', id_tipo);
      if (typeof id === 'number') qs.append('id', id);

      const r = await fetch(`/rrhh/api/consolidado-mensual/?${qs.toString()}`);
      const j = await r.json();

      if (j.status !== 'ok') {
        throw new Error(j.message || 'Error API');
      }

      return (j.data || []).map(x => ({
        mes: normMes(x.mes),
        ppto: Number(x.presupuesto || 0)
      }));
    }
  /*async function fetchSP_bk2({ area, fuente, tipo, id_tipo, id }: {
    area: number;
    fuente: string;
    tipo?: number;
    id_tipo?: number;
    id?: number;
  }) {
      console.log('llegó a fetchSP');
      const params = new URLSearchParams({ area, fuente });
      if (tipo != null) params.set('tipo', tipo);          // remuneracion
      if (id_tipo != null) params.set('id_tipo', id_tipo); // suministros
      if (id != null) params.set('id', id);                // item específico

      const r = await fetch(`/rrhh/api/consolidado-mensual/?${params.toString()}`);
      const j = await r.json();
      if (j.status !== 'ok') throw new Error(j.message || 'Error API');

      return (j.data||[]).map(x => ({ mes: normMes(x.mes), ppto: Number(x.presupuesto||0) }));
  }
  async function fetchSP_bk(area, tipo) {
    const r = await fetch(`${API_URL}?area=${area}&tipo=${tipo}`);
    const j = await r.json();
    if (j.status !== 'ok') throw new Error(j.message || 'Error API');
    return (j.data || []).map(x => ({
      mes:  normMes(x.mes),
      ppto: Number(x.presupuesto || 0)   // <- este es el único valor que llega hoy
    }));
  }*/

  function baseRows(){
    return MESES.map(m => ({
      mes: m,
      // Salarios
      sal_ppto: null, sal_ejec: null, sal_bal: null,
      // Sueldos
      sue_ppto: null, sue_ejec: null, sue_bal: null,

      sum_ppto:null, sum_ejec:null, sum_bal:null,

    }));
  }

  // Une salarios (tipo=2) y sueldos (tipo=1) SOLO con presupuesto por ahora
  function mergeRows(salarios, sueldos, servicios, combustible, materiales, oficina, eproteccion, otros, repuestos, matAgricultura, computo, equit){
    const rows = baseRows();
    const byMes = m => rows.find(r => r.mes === m);

    salarios.forEach(x => {
      const r = byMes(x.mes); if (!r) return;
      r.sal_ppto = x.ppto;    // presupuestado
      r.sal_ejec = null;      // aún no tenemos ejecutado
      r.sal_bal  = null;      // sin ejecutado no se calcula balance
    });

    sueldos.forEach(x => {
      const r = byMes(x.mes); if (!r) return;
      r.sue_ppto = x.ppto;
      r.sue_ejec = null;
      r.sue_bal  = null;
    });

    servicios.forEach(x => {
        const r = byMes(x.mes); if(!r) return;
        r.ser_ppto = x.ppto;
        r.ser_ejec = null;
        r.ser_bal  = null;
    });

    combustible.forEach(x => {
        const r = byMes(x.mes); if(!r) return;
        r.sum_comb_ppto = x.ppto;
        r.sum_comb_ejec = null;
        r.sum_comb_bal  = null;
    });

    // Materiales de construcción
    materiales.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_mat_ppto = x.ppto;
      r.sum_mat_ejec = null;
      r.sum_mat_bal  = null;
    });

    oficina.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_ofi_ppto = x.ppto;
      r.sum_ofi_ejec = null;
      r.sum_ofi_bal  = null;
    });

    eproteccion.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_ep_ppto = x.ppto;
      r.sum_ep_ejec = null;
      r.sum_ep_bal  = null;
    });

     otros.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_otr_ppto = x.ppto;
      r.sum_otr_ejec = null;
      r.sum_otr_bal  = null;
    });

     repuestos.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_rep_ppto = x.ppto;
      r.sum_rep_ejec = null;
      r.sum_rep_bal  = null;
    });


     matAgricultura.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_mag_ppto = x.ppto;
      r.sum_mag_ejec = null;
      r.sum_mag_bal  = null;
    });

    computo.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_ecom_ppto = x.ppto;
      r.sum_ecom_ejec = null;
      r.sum_ecom_bal  = null;
    });

    equit.forEach(x => {
      const r = byMes(x.mes);
      if (!r) return;
      r.sum_euit_ppto = x.ppto;
      r.sum_euit_ejec = null;
      r.sum_euit_bal  = null;
    });


    return rows;
  }

  // === IMPORTANTE: inicializar SIN data y luego usar rows.add() ===
  function initDataTable() {
    $(TABLE_ID).DataTable({
      paging:false, searching:true, ordering:false, info:false,
      dom:"<'d-flex justify-content-between align-items-center mb-2'fB>t",
      buttons:[
        { extend:'excelHtml5', className:'btn btn-success btn-sm', title:'Comparativo_Mensual' }
      ],
      // No tocamos headers; solo mapeamos columnas a datos
      columns:[
        { data:'mes' },
        { data:'sal_ppto', className:'text-right',  render: money },
        { data:'sal_ejec', className:'text-right',  render: money },
        { data:'sal_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sue_ppto', className:'text-right',  render: money },
        { data:'sue_ejec', className:'text-right',  render: money },
        { data:'sue_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'ser_ppto', className:'text-right',  render: money },
        { data:'ser_ejec', className:'text-right',  render: money },
        { data:'ser_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_comb_ppto', className:'text-right',  render: money },
        { data:'sum_comb_ejec', className:'text-right',  render: money },
        { data:'sum_comb_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_mat_ppto', className:'text-right',  render: money },
        { data:'sum_mat_ejec', className:'text-right',  render: money },
        { data:'sum_mat_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_ofi_ppto', className:'text-right',  render: money },
        { data:'sum_ofi_ejec', className:'text-right',  render: money },
        { data:'sum_ofi_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_ep_ppto', className:'text-right',  render: money },
        { data:'sum_ep_ejec', className:'text-right',  render: money },
        { data:'sum_ep_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_otr_ppto', className:'text-right',  render: money },
        { data:'sum_otr_ejec', className:'text-right',  render: money },
        { data:'sum_otr_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_rep_ppto', className:'text-right',  render: money },
        { data:'sum_rep_ejec', className:'text-right',  render: money },
        { data:'sum_rep_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_mag_ppto', className:'text-right',  render: money },
        { data:'sum_mag_ejec', className:'text-right',  render: money },
        { data:'sum_mag_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_ecom_ppto', className:'text-right',  render: money },
        { data:'sum_ecom_ejec', className:'text-right',  render: money },
        { data:'sum_ecom_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

        { data:'sum_euit_ppto', className:'text-right',  render: money },
        { data:'sum_euit_ejec', className:'text-right',  render: money },
        { data:'sum_euit_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },

      ],
      footerCallback: function(row, data){
        const sum = k => data.reduce((a,x)=>a+(Number(x[k])||0),0);
        const sal_p=sum('sal_ppto'), sal_e=sum('sal_ejec'), sal_b=sum('sal_bal');
        const sue_p=sum('sue_ppto'), sue_e=sum('sue_ejec'), sue_b=sum('sue_bal');
        const ser_p = sum('ser_ppto'), ser_e = sum('ser_ejec'), ser_b = sum('ser_bal');
        const sum_comb = sum('sum_comb_ppto'), sum_comb_e = sum('sum_comb_ejec'), sum_comb_b = sum('sum_comb_bal');
        const sum_mat = sum('sum_mat_ppto'), sum_mat_e = sum('sum_mat_ejec'), sum_mat_b = sum('sum_mat_bal');
        const sum_ofi = sum('sum_ofi_ppto'), sum_ofi_e = sum('sum_ofi_ejec'), sum_ofi_b = sum('sum_ofi_bal');
        const sum_ep = sum('sum_ep_ppto'), sum_ep_e = sum('sum_ep_ejec'), sum_ep_b = sum('sum_ep_bal');
        const sum_otr = sum('sum_otr_ppto'), sum_otr_e = sum('sum_otr_ejec'), sum_otr_b = sum('sum_otr_bal');
        const sum_rep = sum('sum_rep_ppto'), sum_rep_e = sum('sum_rep_ejec'), sum_rep_b = sum('sum_rep_bal');
        const sum_mag = sum('sum_mag_ppto'), sum_mag_e = sum('sum_mag_ejec'), sum_mag_b = sum('sum_mag_bal');
        const sum_ecom = sum('sum_ecom_ppto'), sum_ecom_e = sum('sum_ecom_ejec'), sum_ecom_b = sum('sum_ecom_bal');
        const sum_euit = sum('sum_euit_ppto'), sum_euit_e = sum('sum_euit_ejec'), sum_euit_b = sum('sum_euit_bal');

        $('#f_sal_ppto').text(money(sal_p));
        $('#f_sal_ejec').text(sal_e ? money(sal_e) : '-');
        $('#f_sal_bal').html((sal_b||sal_b===0) ? badge(sal_b) : '-');

        $('#f_sue_ppto').text(money(sue_p));
        $('#f_sue_ejec').text(sue_e ? money(sue_e) : '-');
        $('#f_sue_bal').html((sue_b||sue_b===0) ? badge(sue_b) : '-');

        // ✅ Servicios (nuevo)
        $('#f_ser_ppto').text(money(ser_p));
        $('#f_ser_ejec').text(ser_e ? money(ser_e) : '-');
        $('#f_ser_bal').html((ser_e && (ser_b || ser_b===0)) ? badge(ser_b) : '-');

        $('#f_sumc_ppto').text(money(sum_comb));
        $('#f_sumc_ejec').text(sum_comb_e ? money(sum_comb_e) : '-');
        $('#f_sumc_bal').html((sum_comb_e && (sum_comb_b || sum_comb_b===0)) ? badge(sum_comb_b) : '-');

        $('#f_summ_ppto').text(money(sum_mat));
        $('#f_summ_ejec').text(sum_mat_e ? money(sum_mat_e) : '-');
        $('#f_summ_bal').html((sum_mat_e && (sum_mat_b || sum_mat_b===0)) ? badge(sum_mat_b) : '-');

        $('#f_sumo_ppto').text(money(sum_ofi));
        $('#f_sumo_ejec').text(sum_ofi_e ? money(sum_ofi_e) : '-');
        $('#f_sumo_bal').html((sum_ofi_e && (sum_ofi_b || sum_ofi_b===0)) ? badge(sum_ofi_b) : '-');

        $('#f_sumep_ppto').text(money(sum_ep));
        $('#f_sumep_ejec').text(sum_ep_e ? money(sum_ep_e) : '-');
        $('#f_sumep_bal').html((sum_ep_e && (sum_ep_b || sum_ep_b===0)) ? badge(sum_ep_b) : '-');

        $('#f_sumotr_ppto').text(money(sum_otr));
        $('#f_sumotr_ejec').text(sum_otr_e ? money(sum_otr_e) : '-');
        $('#f_sumotr_bal').html((sum_otr_e && (sum_otr_b || sum_otr_b===0)) ? badge(sum_otr_b) : '-');

        $('#f_sumrep_ppto').text(money(sum_rep));
        $('#f_sumrep_ejec').text(sum_rep_e ? money(sum_rep_e) : '-');
        $('#f_sumrep_bal').html((sum_rep_e && (sum_rep_b || sum_rep_b===0)) ? badge(sum_rep_b) : '-');

        $('#f_summag_ppto').text(money(sum_mag));
        $('#f_summag_ejec').text(sum_mag_e ? money(sum_mag_e) : '-');
        $('#f_summag_bal').html((sum_mag_e && (sum_mag_b || sum_mag_b===0)) ? badge(sum_mag_b) : '-');

        $('#f_sumecom_ppto').text(money(sum_ecom));
        $('#f_sumecom_ejec').text(sum_ecom_e ? money(sum_ecom_e) : '-');
        $('#f_sumecom_bal').html((sum_ecom_e && (sum_ecom_b || sum_ecom_b===0)) ? badge(sum_ecom_b) : '-');

        $('#f_sumeuit_ppto').text(money(sum_euit));
        $('#f_sumeuit_ejec').text(sum_euit_e ? money(sum_euit_e) : '-');
        $('#f_sumeuit_bal').html((sum_euit_e && (sum_euit_b || sum_euit_b===0)) ? badge(sum_euit_b) : '-');
      }
    });
  }

  // Carga datos del SP y puebla/recarga la tabla
  async function loadTable(){
    const area = $(TAB_ID).data('area');
    if (!area) { console.warn('data-area no definido en el tab'); return; }

    // Secuencial para evitar HY010 con ODBC
    const salarios = await fetchSP({area:12, fuente:'remuneracion', tipo:2}); // 2 = Salarios
    const sueldos  = await fetchSP({area:12, fuente:'remuneracion', tipo:1}); // 1 = Sueldos
    const servicios = await fetchSP({area:12, fuente:'servicios'});
    const combustible = await fetchSP({area:12, fuente:'suministros', id_tipo:1}); // NUEVO
    const materiales = await fetchSP({area:12, fuente:'suministros', id_tipo:4}); // NUEVO
    const oficina = await fetchSP({area:12, fuente:'suministros', id_tipo:5}); // NUEVO
    const eproteccion = await fetchSP({area:12, fuente:'suministros', id_tipo:6}); // NUEVO
    const otros_sum = await fetchSP({area:12, fuente:'suministros', id_tipo:8}); // NUEVO
    const repuestos = await fetchSP({area:12, fuente:'suministros', id_tipo:2}); // NUEVO
    const matAgricultura = await fetchSP({area:12, fuente:'suministros', id_tipo:3}); // NUEVO
    const computo = await fetchSP({area:12, fuente:'suministros', id_tipo:7}); // NUEVO
    const equit = await fetchSP({area:12, fuente:'suministros', id_tipo:9}); // NUEVO


    const rows = mergeRows(salarios, sueldos, servicios, combustible, materiales, oficina, eproteccion, otros_sum, repuestos, matAgricultura, computo, equit);

    if (!$.fn.dataTable.isDataTable(TABLE_ID)) {
      initDataTable();
    }

    const dt = $(TABLE_ID).DataTable();
    dt.clear();
    dt.rows.add(rows);
    dt.draw(false);
  }

  // Eventos
  $(document).ready(function () {
    // Si el tab ya está activo al cargar
    if ($(TAB_ID).hasClass('active') || $(TAB_ID).hasClass('show')) {
      loadTable().catch(console.error);
    }
    // O inicialízalo la primera vez que se muestre
    $('a[data-toggle="tab"], a[data-bs-toggle="tab"]').one('shown.bs.tab', function (e) {
      if ($(e.target).attr('href') === TAB_ID) loadTable().catch(console.error);
    });
  });

})();



/*
(function () {

  const TAB_ID   = '#default-tab-6';
  const TABLE_ID = '#dtConsolidado';
  const API_URL  = '/rrhh/api/rpt-remuneracion/';

  // Normaliza meses (“Setiembre” / “Septiembre”, mayúsculas)
  const MESES = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SETIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'];
  const normMes = s => String(s||'').trim().toUpperCase().replace('SEPTIEMBRE','SETIEMBRE');


  const money = n => (n==null || isNaN(n)) ? '-' : 'S/ ' + Number(n).toLocaleString('es-PE',{minimumFractionDigits:2});
  const badge = v => v==null ? '-' : `<span class="badge ${v<=0?'badge-success':'badge-danger'}">${money(v)}</span>`;

  async function fetchSP(area, tipo) {
  const r = await fetch(`/rrhh/api/rpt-remuneracion/?area=${area}&tipo=${tipo}`);
  const j = await r.json();
  if (j.status !== 'ok') throw new Error(j.message || 'Error API');
  // ← Solo Mes y Presupuesto
  return (j.data || []).map(x => ({
    mes  : normMes(x.mes),
    ppto : Number(x.presupuesto || 0)
  }));
}

  async function fetchSP2(area, tipo) {
    const r = await fetch(`${API_URL}?area=${area}&tipo=${tipo}`);
    const j = await r.json();
    if (j.status !== 'ok') throw new Error(j.message || 'Error API');
    // Esperamos: [{ mes, presupuesto, real }]
    return (j.data||[]).map(x => ({
      mes  : normMes(x.mes),
      ppto : Number(x.presupuesto || 0),
      real : (x.real!=null) ? Number(x.real) : null
    }));
  }

  function baseRows(){
  return ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO","SETIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
    .map(m => ({ mes:m,
      sal_ppto:null, sal_ejec:null, sal_bal:null,
      sue_ppto:null, sue_ejec:null, sue_bal:null
    }));
}

  function baseRows2(){
    return MESES.map(m => ({
      mes:m,
      sal_ppto:null, sal_ejec:null, sal_bal:null,
      sue_ppto:null, sue_ejec:null, sue_bal:null
    }));
  }

  function mergeRows(salarios, sueldos){
      const rows = baseRows();
      const byMes = m => rows.find(r => r.mes === m);

      salarios.forEach(x => { const r = byMes(x.mes); if(!r) return;
        r.sal_ppto = x.ppto;                 // presupuestado
        r.sal_ejec = null;                   // ejecutado vendrá luego
        r.sal_bal  = null;                   // balance se calculará cuando haya ejecutado
      });

      sueldos.forEach(x => { const r = byMes(x.mes); if(!r) return;
        r.sue_ppto = x.ppto;
        r.sue_ejec = null;
        r.sue_bal  = null;
      });

      return rows;
    }

  function mergeRows2(salarios, sueldos){
    const rows = baseRows();
    const byMes = m => rows.find(r => r.mes===m);

    salarios.forEach(x => {
      const r = byMes(x.mes); if(!r) return;
      r.sal_ppto = x.ppto;
      r.sal_ejec = x.real;
      r.sal_bal  = (x.real!=null) ? (x.real - x.ppto) : null;
    });

    sueldos.forEach(x => {
      const r = byMes(x.mes); if(!r) return;
      r.sue_ppto = x.ppto;
      r.sue_ejec = x.real;
      r.sue_bal  = (x.real!=null) ? (x.real - x.ppto) : null;
    });

    return rows;
  }

  function initDataTable4() {
  console.log('initDataTable (sin data)');
  $('#dtConsolidado').DataTable({
    paging:false, searching:true, ordering:false, info:false,
    dom:"<'d-flex justify-content-between align-items-center mb-2'fB>t",
    buttons:[
      { extend:'excelHtml5', className:'btn btn-success btn-sm', title:'Comparativo_Mensual' },
      { extend:'pdfHtml5',   className:'btn btn-danger btn-sm',  title:'Comparativo_Mensual', orientation:'landscape', pageSize:'A4' },
      { extend:'print',      className:'btn btn-primary btn-sm', title:'Comparativo Mensual' }
    ],
    columns:[
      { data:'mes' },
      { data:'sal_ppto', className:'text-right',  render: money },
      { data:'sal_ejec', className:'text-right',  render: money },
      { data:'sal_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },
      { data:'sue_ppto', className:'text-right',  render: money },
      { data:'sue_ejec', className:'text-right',  render: money },
      { data:'sue_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d }
    ]
  });
  _logDT('initDataTable');
}


  function initDataTable6() {
      console.log('initDataTable (sin data)');

      $(TABLE_ID).DataTable({
        paging: false,
        searching: true,
        ordering: false,
        info: false,
        dom: "<'d-flex justify-content-between align-items-center mb-2'fB>t",
        buttons: [
          { extend: 'excelHtml5', className: 'btn btn-success btn-sm', title: 'Comparativo_Mensual' },
          { extend: 'pdfHtml5',   className: 'btn btn-danger btn-sm',  title: 'Comparativo_Mensual', orientation:'landscape', pageSize:'A4' },
          { extend: 'print',      className: 'btn btn-primary btn-sm', title: 'Comparativo Mensual' }
        ],
        columns: [
          { data:'mes' },
          { data:'sal_ppto', className:'text-right',  render: money },
          { data:'sal_ejec', className:'text-right',  render: money },
          { data:'sal_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },
          { data:'sue_ppto', className:'text-right',  render: money },
          { data:'sue_ejec', className:'text-right',  render: money },
          { data:'sue_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d }
        ]
      });
    }


  function initDataTable(data){
    console.log('initDataTable -> filas:', data.length);
    $(TABLE_ID).DataTable({
      data,
      paging:false, searching:true, ordering:false, info:false,
      dom:"<'d-flex justify-content-between align-items-center mb-2'fB>t",
      buttons:[
        { extend:'excelHtml5', className:'btn btn-success btn-sm', title:'Comparativo_Mensual' },
        { extend:'pdfHtml5',   className:'btn btn-danger btn-sm',  title:'Comparativo_Mensual', orientation:'landscape', pageSize:'A4' },
        { extend:'print',      className:'btn btn-primary btn-sm', title:'Comparativo Mensual' }
      ],
      // ¡NO tocamos headers! Solo mapeamos datos -> columnas existentes
      columns:[
        { data:'mes' },
        { data:'sal_ppto', className:'text-right',  render: money },
        { data:'sal_ejec', className:'text-right',  render: money },
        { data:'sal_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d },
        { data:'sue_ppto', className:'text-right',  render: money },
        { data:'sue_ejec', className:'text-right',  render: money },
        { data:'sue_bal',  className:'text-center', render:(d,t)=>t==='display'?badge(d):d }
      ],
      footerCallback: function(row, data){
        const sum = k => data.reduce((a,x)=>a+(Number(x[k])||0),0);
        const sal_p=sum('sal_ppto'), sal_e=sum('sal_ejec'), sal_b=sum('sal_bal');
        const sue_p=sum('sue_ppto'), sue_e=sum('sue_ejec'), sue_b=sum('sue_bal');
        $('#f_sal_ppto').text(money(sal_p));
        $('#f_sal_ejec').text(sal_e?money(sal_e):'-');
        $('#f_sal_bal').html((sal_b||sal_b===0)?badge(sal_b):'-');
        $('#f_sue_ppto').text(money(sue_p));
        $('#f_sue_ejec').text(sue_e?money(sue_e):'-');
        $('#f_sue_bal').html((sue_b||sue_b===0)?badge(sue_b):'-');
      }
    });
  }

  async function loadTable(){
  console.log('loadTable: start');
  const area = $('#default-tab-6').data('area');
  if (!area) { console.error('data-area vacío'); return; }

  // 1) fetch secuencial
  const salarios = await fetchSP(area, 2);
  const sueldos  = await fetchSP(area, 1);

  // 2) fusiona
  const rows = mergeRows(salarios, sueldos);
  console.log('rows length =', rows.length, ' sample ->', rows[0]);
  console.table(rows);

  // 3) init DT si hace falta
  if (!$.fn.dataTable.isDataTable('#dtConsolidado')) {
    initDataTable();
  }

  // 4) agregar filas SIEMPRE con API
  const dt = $('#dtConsolidado').DataTable();
  dt.clear();
  dt.rows.add(rows);
  dt.columns.adjust();
  dt.draw(false);
  _logDT('after rows.add');

  // 5) fallback plan — si por alguna razón sigue 0, destruye e inserta a mano
  if (dt.rows().count() === 0) {
    console.warn('Fallback: DataTable no pintó filas, construyendo tbody manual...');
    dt.clear().destroy();
    const tbody = $('#dtConsolidado tbody').empty();
    rows.forEach(r => {
      tbody.append(`
        <tr>
          <td>${r.mes}</td>
          <td class="text-right">${money(r.sal_ppto)}</td>
          <td class="text-right">${money(r.sal_ejec)}</td>
          <td class="text-center">${r.sal_bal==null?'-':badge(r.sal_bal)}</td>
          <td class="text-right">${money(r.sue_ppto)}</td>
          <td class="text-right">${money(r.sue_ejec)}</td>
          <td class="text-center">${r.sue_bal==null?'-':badge(r.sue_bal)}</td>
        </tr>
      `);
    });
    console.warn('Fallback tbody rows =', $('#dtConsolidado tbody tr').length);

    // re-inicializa DT encima del HTML ya pintado (opcional)
    initDataTable();
    _logDT('after fallback reinit');
  }
}

  async function loadTable3(){
      const area = $(TAB_ID).data('area');
      if (!area) return;

      const salarios = await fetchSP(area, 2);
      const sueldos  = await fetchSP(area, 1);

      const rows = mergeRows(salarios, sueldos);

      console.table(rows); // ✔ confirmación visual
/
      if (!$.fn.dataTable.isDataTable(TABLE_ID)) {
        initDataTable();
      }

      const dt = $(TABLE_ID).DataTable();

      dt.clear();
      dt.rows.add(rows);   // 🔴 ESTE ERA EL PASO CLAVE
      dt.draw();           // 🔴 SIN ESTO NO SE PINTA
    }


  async function loadTable2(){
    const area = $(TAB_ID).data('area');
    if(!area){ console.warn('data-area no definido en el tab'); return; }

    // Secuencial para evitar HY010
    const salarios = await fetchSP(area, 2); // salarios
    const sueldos  = await fetchSP(area, 1); // sueldos

    const rows = mergeRows(salarios, sueldos);
    console.table(rows); // <- verifica qué llega

    if ($.fn.dataTable.isDataTable(TABLE_ID)) {
      const dt = $(TABLE_ID).DataTable();
      dt.clear().rows.add(rows).draw(false);   // <-- aquí se pobla
    } else {
      initDataTable(rows);                     // <-- init + poblar
    }
  }

  $(document).ready(function () {
    // Si el tab ya está visible, carga de frente
    if ($(TAB_ID).hasClass('active') || $(TAB_ID).hasClass('show')) {
      loadTable().catch(console.error);
    }
    // Si no, carga en el primer shown
    $('a[data-toggle="tab"], a[data-bs-toggle="tab"]').one('shown.bs.tab', function (e) {
      if ($(e.target).attr('href') === TAB_ID) loadTable().catch(console.error);
    });
  });

  // === utilidades de depuración (temporal) ===
function _logDT(where) {
  if (!$.fn.dataTable.isDataTable('#dtConsolidado')) {
    console.warn(where, '-> DataTable NO inicializado');
    return;
  }
  const dt = $('#dtConsolidado').DataTable();
  console.warn(where, 'rows().count =', dt.rows().count(), ' | tbody TR =', $('#dtConsolidado tbody tr').length);
}


})();
*/
