(function () {
    'use strict';

    var colors = ['#0b6b45', '#278ba8', '#7c4dcc', '#e58a13', '#b7442b', '#4e6f8a', '#5f9e63', '#9b7c3f'];
    var monthChart, yearChart, clientChart, shareChart;

    function payload() { return JSON.parse(document.getElementById('cajas-kilos-data').textContent); }
    function selectedYears() {
        var years = Array.prototype.slice.call(document.querySelectorAll('#ck-years input:checked')).map(function (input) { return input.value; }).sort();
        if (!years.length) { var first = document.querySelector('#ck-years input'); first.checked = true; years = [first.value]; }
        return years;
    }
    function monthIndexes() {
        var start = Number(document.getElementById('ck-from').value); var end = Number(document.getElementById('ck-to').value);
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
    function sum(values) { return values.reduce(function (total, value) { return total + (value === null ? 0 : value); }, 0); }
    function percent(current, previous) { return previous ? ((current - previous) / Math.abs(previous)) * 100 : null; }
    function clientMonthValue(data, metric, client, year, month) { return data.metrics[metric].clients[client][year][month]; }
    function seriesValues(data, metric, client, year, indexes) {
        return indexes.map(function (month) {
            if (client !== '__all__') return clientMonthValue(data, metric, client, year, month);
            var values = data.clients.map(function (name) { return clientMonthValue(data, metric, name, year, month); });
            return values.some(function (value) { return value !== null; }) ? sum(values) : null;
        });
    }
    function niceStep(maxValue) {
        if (!maxValue) return 1000; var raw = maxValue / 6; var magnitude = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)); var normalized = raw / magnitude;
        return (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude;
    }
    function axis(step, metric) { return { gridLines: { color: '#edf1f3', drawBorder: false }, ticks: { beginAtZero: true, fontColor: '#71808d', stepSize: step, callback: function (value) { return format(Number(value), metric, true); } } }; }
    function options(step, metric, hideLegend) {
        return { maintainAspectRatio: false, responsive: true, legend: { display: !hideLegend, position: 'bottom', labels: { boxWidth: 12, padding: 18, fontColor: '#52606d' } }, tooltips: { callbacks: { label: function (item, chart) { var label = chart.datasets[item.datasetIndex].label || ''; return label + ': ' + format(Number(item.yLabel), metric, false); } } }, scales: { xAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#71808d' } }], yAxes: [axis(step, metric)] } };
    }
    function updateKpis(data, metric, client, years, indexes) {
        var latest = years[years.length - 1]; var prior = years.length > 1 ? years[years.length - 2] : null;
        var values = seriesValues(data, metric, client, latest, indexes); var available = values.filter(function (value) { return value !== null; }); var total = sum(values);
        var priorTotal = prior ? sum(seriesValues(data, metric, client, prior, indexes)) : null; var change = prior ? percent(total, priorTotal) : null;
        var leaders = data.clients.map(function (name) { return { name: name, value: sum(seriesValues(data, metric, name, latest, indexes)) }; }).sort(function (a, b) { return b.value - a.value; });
        var leader = leaders[0] || { name: '—', value: 0 };
        document.getElementById('ck-total').textContent = format(total, metric, true);
        document.getElementById('ck-total-detail').textContent = latest + ' · ' + (client === '__all__' ? 'Todos los clientes' : client);
        var yoy = document.getElementById('ck-yoy'); yoy.textContent = change === null ? '—' : (change >= 0 ? '+' : '') + change.toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; yoy.className = 'ck-kpi-value ' + (change === null ? '' : change >= 0 ? 'ck-positive' : 'ck-negative');
        document.getElementById('ck-yoy-detail').textContent = prior ? latest + ' vs. ' + prior + ' · mismo periodo' : 'Selecciona al menos dos años';
        document.getElementById('ck-leader').textContent = leader.name; document.getElementById('ck-leader-detail').textContent = format(leader.value, metric, false) + ' · ' + latest;
        document.getElementById('ck-average').textContent = available.length ? format(total / available.length, metric, true) : '—'; document.getElementById('ck-average-detail').textContent = available.length + ' meses con información';
    }
    function updateMainCharts(data, metric, client, years, indexes) {
        var labels = indexes.map(function (index) { return data.months[index]; });
        var sets = years.map(function (year, colorIndex) { return { label: year, data: seriesValues(data, metric, client, year, indexes), borderColor: colors[colorIndex % colors.length], backgroundColor: colors[colorIndex % colors.length], borderWidth: 3, pointRadius: 3, fill: false, lineTension: .25, spanGaps: false }; });
        var maxMonth = Math.max.apply(null, sets.reduce(function (all, set) { return all.concat(set.data.filter(function (value) { return value !== null; }).map(Math.abs)); }, [0]));
        if (monthChart) monthChart.destroy(); monthChart = new Chart(document.getElementById('ck-month-chart'), { type: 'line', data: { labels: labels, datasets: sets }, options: options(niceStep(maxMonth), metric, false) });
        var totals = years.map(function (year) { return sum(seriesValues(data, metric, client, year, indexes)); }); var maxYear = Math.max.apply(null, totals.map(Math.abs).concat([0]));
        if (yearChart) yearChart.destroy(); yearChart = new Chart(document.getElementById('ck-year-chart'), { type: 'bar', data: { labels: years, datasets: [{ data: totals, backgroundColor: years.map(function (_, index) { return colors[index % colors.length]; }) }] }, options: options(niceStep(maxYear), metric, true) });
    }
    function updateClientCharts(data, metric, latest, indexes) {
        var ranking = data.clients.map(function (name) { return { name: name, value: sum(seriesValues(data, metric, name, latest, indexes)) }; }).filter(function (item) { return item.value !== 0; }).sort(function (a, b) { return b.value - a.value; });
        var horizontal = ranking.slice().reverse(); var max = Math.max.apply(null, ranking.map(function (item) { return item.value; }).concat([0]));
        if (clientChart) clientChart.destroy(); clientChart = new Chart(document.getElementById('ck-client-chart'), { type: 'horizontalBar', data: { labels: horizontal.map(function (item) { return item.name; }), datasets: [{ label: latest, data: horizontal.map(function (item) { return item.value; }), backgroundColor: '#278ba8' }] }, options: { maintainAspectRatio: false, responsive: true, legend: { display: false }, tooltips: { callbacks: { label: function (item) { return format(Number(item.xLabel), metric, false); } } }, scales: { xAxes: [axis(niceStep(max), metric)], yAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#52606d', fontSize: 10 } }] } } });
        var share = ranking.slice(0, 7); if (ranking.length > 7) share.push({ name: 'Otros', value: sum(ranking.slice(7).map(function (item) { return item.value; })) });
        if (shareChart) shareChart.destroy(); shareChart = new Chart(document.getElementById('ck-share-chart'), { type: 'doughnut', data: { labels: share.map(function (item) { return item.name; }), datasets: [{ data: share.map(function (item) { return item.value; }), backgroundColor: colors }] }, options: { maintainAspectRatio: false, responsive: true, cutoutPercentage: 62, legend: { position: 'bottom', labels: { boxWidth: 11, padding: 11, fontSize: 9 } }, tooltips: { callbacks: { label: function (item, chart) { return chart.labels[item.index] + ': ' + format(Number(chart.datasets[0].data[item.index]), metric, false); } } } } });
        document.getElementById('ck-ranking-subtitle').textContent = latest + ' · periodo seleccionado';
    }
    function updateTable(data, metric, client, years, indexes) {
        var clients = client === '__all__' ? data.clients : [client];
        document.getElementById('ck-table-head').innerHTML = '<th>Cliente</th><th>Año</th>' + indexes.map(function (index) { return '<th class="text-right">' + data.months[index] + '</th>'; }).join('') + '<th class="text-right">Total</th>';
        document.getElementById('ck-table-body').innerHTML = clients.map(function (name) { return years.map(function (year) { var values = seriesValues(data, metric, name, year, indexes); var total = values.some(function (value) { return value !== null; }) ? sum(values) : null; return '<tr><td class="font-weight-bold">' + name + '</td><td><span class="badge badge-light">' + year + '</span></td>' + values.map(function (value) { return '<td class="text-right">' + format(value, metric, false) + '</td>'; }).join('') + '<td class="text-right font-weight-bold">' + format(total, metric, false) + '</td></tr>'; }).join(''); }).join('');
    }
    function refresh(data) {
        var metric = document.getElementById('ck-metric').value; var client = document.getElementById('ck-client').value; var years = selectedYears(); var indexes = monthIndexes();
        var active = years.filter(function (year) { return seriesValues(data, metric, client, year, indexes).some(function (value) { return value !== null; }); }); if (!active.length) active = years;
        document.getElementById('ck-trend-subtitle').textContent = data.metrics[metric].label + ' · ' + (client === '__all__' ? 'Todos los clientes' : client) + ' · ' + data.months[indexes[0]] + ' a ' + data.months[indexes[indexes.length - 1]];
        updateKpis(data, metric, client, active, indexes); updateMainCharts(data, metric, client, active, indexes); updateClientCharts(data, metric, active[active.length - 1], indexes); updateTable(data, metric, client, years, indexes);
    }
    window.initCajasKilosDashboard = function () {
        var data = payload(); var from = document.getElementById('ck-from'); var to = document.getElementById('ck-to');
        data.months.forEach(function (month, index) { from.add(new Option(month, index)); to.add(new Option(month, index)); });
        var latest = String(Math.max.apply(null, data.years)); var allLatest = data.clients.map(function (client) { return data.metrics.cajas.clients[client][latest]; }); var latestMonth = 0;
        for (var index = 0; index < data.months.length; index += 1) if (allLatest.some(function (values) { return values[index] !== null; })) latestMonth = index;
        from.value = 0; to.value = latestMonth;
        document.querySelectorAll('#ck-metric, #ck-client, #ck-years input, #ck-from, #ck-to').forEach(function (control) { control.addEventListener('change', function () { refresh(data); }); });
        document.getElementById('ck-reset').addEventListener('click', function () { document.getElementById('ck-metric').value = 'cajas'; document.getElementById('ck-client').value = '__all__'; document.querySelectorAll('#ck-years input').forEach(function (input) { input.checked = true; }); from.value = 0; to.value = latestMonth; refresh(data); }); refresh(data);
    };
}());
