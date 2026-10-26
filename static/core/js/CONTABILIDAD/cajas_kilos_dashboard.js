(function () {
    'use strict';
    var colors = ['#0b6b45', '#278ba8', '#7c4dcc', '#e58a13', '#b7442b', '#4e6f8a', '#5f9e63', '#9b7c3f'];
    var monthChart, yearChart, clientChart, shareChart;
    function payload() { return JSON.parse(document.getElementById('cajas-kilos-data').textContent); }
    function sum(values) { return values.reduce(function (total, value) { return total + (value === null ? 0 : value); }, 0); }
    function selectedYears() {
        var years = Array.prototype.slice.call(document.querySelectorAll('#ck-years input:checked')).map(function (input) { return input.value; }).sort();
        if (!years.length) { var first = document.querySelector('#ck-years input'); first.checked = true; years = [first.value]; }
        return years;
    }
    function monthIndexes() {
        var start = Number(document.getElementById('ck-from').value), end = Number(document.getElementById('ck-to').value);
        if (start > end) { var swap = start; start = end; end = swap; document.getElementById('ck-from').value = start; document.getElementById('ck-to').value = end; }
        var indexes = []; for (var index = start; index <= end; index += 1) indexes.push(index); return indexes;
    }
    function format(value, metric, compact) {
        if (value === null || typeof value === 'undefined' || isNaN(value)) return '—';
        var suffix = metric === 'cajas' ? ' cajas' : ' kg';
        if (compact && Math.abs(value) >= 1000000) return (value / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' M' + suffix;
        if (compact && Math.abs(value) >= 1000) return (value / 1000).toLocaleString('es-PE', { minimumFractionDigits: 0, maximumFractionDigits: 1 }) + ' mil' + suffix;
        return Number(value).toLocaleString('es-PE', { minimumFractionDigits: metric === 'cajas' ? 0 : 2, maximumFractionDigits: metric === 'cajas' ? 0 : 2 }) + suffix;
    }
    function filtered(data, client, producer) { return data.series.filter(function (item) { return (client === '__all__' || item.client === client) && (producer === '__all__' || item.producer === producer); }); }
    function hasMovement(item, year, indexes) { return indexes.some(function (month) { return Number(item.cajas[year][month] || 0) > 0; }); }
    function filterPeriod() { var years = selectedYears(); return { year: years[years.length - 1], indexes: monthIndexes() }; }
    function syncClientOptions(data) {
        var select = document.getElementById('ck-client'), previous = select.value, period = filterPeriod();
        var clients = data.series.filter(function (item) { return hasMovement(item, period.year, period.indexes); }).map(function (item) { return item.client; }).filter(function (name, index, items) { return items.indexOf(name) === index; }).sort();
        select.innerHTML = ''; select.add(new Option('TODOS LOS CLIENTES', '__all__'));
        clients.forEach(function (name) { select.add(new Option(name.toUpperCase(), name)); });
        select.value = clients.indexOf(previous) >= 0 ? previous : '__all__';
    }
    function syncProducerOptions(data) {
        var client = document.getElementById('ck-client').value, select = document.getElementById('ck-producer'), previous = select.value, period = filterPeriod();
        var producers = data.series.filter(function (item) { return (client === '__all__' || item.client === client) && hasMovement(item, period.year, period.indexes); }).map(function (item) { return item.producer; }).filter(function (name, index, items) { return items.indexOf(name) === index; }).sort();
        select.innerHTML = ''; select.add(new Option('TODOS LOS PRODUCTORES', '__all__'));
        producers.forEach(function (name) { select.add(new Option(name.toUpperCase(), name)); });
        select.value = producers.indexOf(previous) >= 0 ? previous : '__all__';
    }
    function seriesValues(data, metric, client, producer, year, indexes) {
        var items = filtered(data, client, producer);
        return indexes.map(function (month) { var values = items.map(function (item) { return item[metric][year][month]; }); return values.some(function (value) { return value !== null; }) ? sum(values) : null; });
    }
    function filterLabel(client, producer) { return (client === '__all__' ? 'Todos los clientes' : client) + ' · ' + (producer === '__all__' ? 'Todos los productores' : producer); }
    function niceStep(maxValue) { if (!maxValue) return 1000; var raw = maxValue / 6, magnitude = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)), normalized = raw / magnitude; return (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude; }
    function axis(step, metric) { return { gridLines: { color: '#edf1f3', drawBorder: false }, ticks: { beginAtZero: true, fontColor: '#71808d', stepSize: step, callback: function (value) { return format(Number(value), metric, true); } } }; }
    function options(step, metric, hideLegend) { return { maintainAspectRatio: false, responsive: true, legend: { display: !hideLegend, position: 'bottom', labels: { boxWidth: 12, padding: 18, fontColor: '#52606d' } }, tooltips: { callbacks: { label: function (item, chart) { var label = chart.datasets[item.datasetIndex].label || ''; return label + ': ' + format(Number(item.yLabel), metric, false); } } }, scales: { xAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#71808d' } }], yAxes: [axis(step, metric)] } }; }
    function ranking(data, metric, client, latest, indexes) { return data.producers.map(function (name) { return { name: name, value: sum(seriesValues(data, metric, client, name, latest, indexes)) }; }).filter(function (item) { return item.value !== 0; }).sort(function (a, b) { return b.value - a.value; }); }
    function updateKpis(data, metric, client, producer, years, indexes) {
        var latest = years[years.length - 1], prior = years.length > 1 ? years[years.length - 2] : null;
        var values = seriesValues(data, metric, client, producer, latest, indexes), available = values.filter(function (value) { return value !== null; }), total = sum(values);
        var priorTotal = prior ? sum(seriesValues(data, metric, client, producer, prior, indexes)) : null, change = prior && priorTotal ? ((total - priorTotal) / Math.abs(priorTotal)) * 100 : null;
        var leader = ranking(data, metric, client, latest, indexes)[0] || { name: '—', value: 0 };
        document.getElementById('ck-total').textContent = format(total, metric, true); document.getElementById('ck-total-detail').textContent = latest + ' · ' + filterLabel(client, producer);
        var yoy = document.getElementById('ck-yoy'); yoy.textContent = change === null ? '—' : (change >= 0 ? '+' : '') + change.toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; yoy.className = 'ck-kpi-value ' + (change === null ? '' : change >= 0 ? 'ck-positive' : 'ck-negative');
        document.getElementById('ck-yoy-detail').textContent = prior ? latest + ' vs. ' + prior + ' · mismo periodo' : 'Selecciona al menos dos años'; document.getElementById('ck-leader').textContent = leader.name; document.getElementById('ck-leader-detail').textContent = format(leader.value, metric, false) + ' · ' + latest;
        document.getElementById('ck-average').textContent = available.length ? format(total / available.length, metric, true) : '—'; document.getElementById('ck-average-detail').textContent = available.length + ' meses con información';
    }
    function updateMainCharts(data, metric, client, producer, years, indexes) {
        var labels = indexes.map(function (index) { return data.months[index]; });
        var sets = years.map(function (year, i) { return { label: year, data: seriesValues(data, metric, client, producer, year, indexes), borderColor: colors[i % colors.length], backgroundColor: colors[i % colors.length], borderWidth: 3, pointRadius: 3, fill: false, lineTension: .25, spanGaps: false }; });
        var maxMonth = Math.max.apply(null, sets.reduce(function (all, set) { return all.concat(set.data.filter(function (value) { return value !== null; }).map(Math.abs)); }, [0]));
        if (monthChart) monthChart.destroy(); monthChart = new Chart(document.getElementById('ck-month-chart'), { type: 'line', data: { labels: labels, datasets: sets }, options: options(niceStep(maxMonth), metric, false) });
        var totals = years.map(function (year) { return sum(seriesValues(data, metric, client, producer, year, indexes)); }), maxYear = Math.max.apply(null, totals.map(Math.abs).concat([0]));
        if (yearChart) yearChart.destroy(); yearChart = new Chart(document.getElementById('ck-year-chart'), { type: 'bar', data: { labels: years, datasets: [{ data: totals, backgroundColor: years.map(function (_, i) { return colors[i % colors.length]; }) }] }, options: options(niceStep(maxYear), metric, true) });
    }
    function updateProducerCharts(data, metric, client, latest, indexes) {
        var items = ranking(data, metric, client, latest, indexes), horizontal = items.slice().reverse(), max = Math.max.apply(null, items.map(function (item) { return item.value; }).concat([0]));
        if (clientChart) clientChart.destroy(); clientChart = new Chart(document.getElementById('ck-client-chart'), { type: 'horizontalBar', data: { labels: horizontal.map(function (item) { return item.name; }), datasets: [{ label: latest, data: horizontal.map(function (item) { return item.value; }), backgroundColor: '#278ba8' }] }, options: { maintainAspectRatio: false, responsive: true, legend: { display: false }, tooltips: { callbacks: { label: function (item) { return format(Number(item.xLabel), metric, false); } } }, scales: { xAxes: [axis(niceStep(max), metric)], yAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#52606d', fontSize: 10 } }] } } });
        var share = items.slice(0, 7); if (items.length > 7) share.push({ name: 'Otros', value: sum(items.slice(7).map(function (item) { return item.value; })) });
        if (shareChart) shareChart.destroy(); shareChart = new Chart(document.getElementById('ck-share-chart'), { type: 'doughnut', data: { labels: share.map(function (item) { return item.name; }), datasets: [{ data: share.map(function (item) { return item.value; }), backgroundColor: colors }] }, options: { maintainAspectRatio: false, responsive: true, cutoutPercentage: 62, legend: { position: 'bottom', labels: { boxWidth: 11, padding: 11, fontSize: 9 } }, tooltips: { callbacks: { label: function (item, chart) { return chart.labels[item.index] + ': ' + format(Number(chart.datasets[0].data[item.index]), metric, false); } } } } });
        document.getElementById('ck-ranking-subtitle').textContent = latest + ' · periodo seleccionado';
    }
    function updateTable(data, metric, client, producer, years, indexes) {
        document.getElementById('ck-table-head').innerHTML = '<th>Cliente</th><th>Productor</th><th>Año</th>' + indexes.map(function (index) { return '<th class="text-right">' + data.months[index] + '</th>'; }).join('') + '<th class="text-right">Total</th>';
        var rows = []; filtered(data, client, producer).forEach(function (item) { years.forEach(function (year) { var values = indexes.map(function (month) { return item[metric][year][month]; }), total = sum(values); if (total <= 0) return; rows.push('<tr><td class="font-weight-bold">' + item.client + '</td><td class="font-weight-bold">' + item.producer + '</td><td><span class="badge badge-light">' + year + '</span></td>' + values.map(function (value) { return '<td class="text-right">' + format(value, metric, false) + '</td>'; }).join('') + '<td class="text-right font-weight-bold">' + format(total, metric, false) + '</td></tr>'); }); });
        document.getElementById('ck-table-body').innerHTML = rows.length ? rows.join('') : '<tr><td class="text-center text-muted py-4" colspan="' + (indexes.length + 4) + '">No hay producción para los filtros seleccionados.</td></tr>';
    }
    function refresh(data) {
        var metric = document.getElementById('ck-metric').value, client = document.getElementById('ck-client').value, producer = document.getElementById('ck-producer').value, years = selectedYears(), indexes = monthIndexes();
        var active = years.filter(function (year) { return seriesValues(data, metric, client, producer, year, indexes).some(function (value) { return value !== null; }); }); if (!active.length) active = years;
        document.getElementById('ck-trend-subtitle').textContent = data.metrics[metric].label + ' · ' + filterLabel(client, producer) + ' · ' + data.months[indexes[0]] + ' a ' + data.months[indexes[indexes.length - 1]];
        updateKpis(data, metric, client, producer, active, indexes); updateMainCharts(data, metric, client, producer, active, indexes); updateProducerCharts(data, metric, client, active[active.length - 1], indexes); updateTable(data, metric, client, producer, years, indexes);
    }
    window.initCajasKilosDashboard = function () {
        var data = payload(), from = document.getElementById('ck-from'), to = document.getElementById('ck-to'); data.months.forEach(function (month, index) { from.add(new Option(month, index)); to.add(new Option(month, index)); });
        var latest = String(Math.max.apply(null, data.years)), latestMonth = 0; for (var index = 0; index < data.months.length; index += 1) if (data.series.some(function (item) { return item.cajas[latest][index] !== null; })) latestMonth = index;
        from.value = 0; to.value = latestMonth; syncClientOptions(data); syncProducerOptions(data);
        document.getElementById('ck-client').addEventListener('change', function () { syncProducerOptions(data); refresh(data); });
        document.querySelectorAll('#ck-years input, #ck-from, #ck-to').forEach(function (control) { control.addEventListener('change', function () { syncClientOptions(data); syncProducerOptions(data); refresh(data); }); });
        document.querySelectorAll('#ck-metric, #ck-producer').forEach(function (control) { control.addEventListener('change', function () { refresh(data); }); });
        document.getElementById('ck-reset').addEventListener('click', function () { document.getElementById('ck-metric').value = 'cajas'; document.querySelectorAll('#ck-years input').forEach(function (input) { input.checked = true; }); from.value = 0; to.value = latestMonth; document.getElementById('ck-client').value = '__all__'; syncClientOptions(data); syncProducerOptions(data); document.getElementById('ck-producer').value = '__all__'; refresh(data); }); refresh(data);
    };
}());
