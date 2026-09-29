(function () {
    'use strict';

    var colors = ['#0b6b45', '#278ba8', '#7c4dcc', '#e58a13'];
    var monthlyChart;
    var annualChart;

    function payload() { return JSON.parse(document.getElementById('ventas-data').textContent); }
    function money(value, compact) {
        if (value === null || typeof value === 'undefined' || isNaN(value)) return '—';
        if (compact && Math.abs(value) >= 1000000) return 'S/ ' + (value / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' M';
        if (compact && Math.abs(value) >= 1000) return 'S/ ' + (value / 1000).toLocaleString('es-PE', { minimumFractionDigits: 0, maximumFractionDigits: 1 }) + ' mil';
        return 'S/ ' + Number(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    function sum(values) { return values.reduce(function (total, value) { return total + (value === null ? 0 : value); }, 0); }
    function percent(current, previous) { return previous ? ((current - previous) / Math.abs(previous)) * 100 : null; }
    function selectedYears() {
        var years = Array.prototype.slice.call(document.querySelectorAll('#sales-year-options input:checked')).map(function (input) { return input.value; }).sort();
        if (!years.length) { var first = document.querySelector('#sales-year-options input'); first.checked = true; years = [first.value]; }
        return years;
    }
    function monthIndexes() {
        var start = Number(document.getElementById('sales-month-from').value);
        var end = Number(document.getElementById('sales-month-to').value);
        if (start > end) { var swap = start; start = end; end = swap; document.getElementById('sales-month-from').value = start; document.getElementById('sales-month-to').value = end; }
        var indexes = [];
        for (var index = start; index <= end; index += 1) indexes.push(index);
        return indexes;
    }
    function yearValues(data, year, indexes) { return indexes.map(function (index) { return data.data[year][index]; }); }
    function niceStep(maxValue) {
        if (!maxValue) return 100000;
        var raw = maxValue / 6;
        var magnitude = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10));
        var normalized = raw / magnitude;
        return (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude;
    }
    function chartOptions(step, hideLegend) {
        return {
            maintainAspectRatio: false, responsive: true,
            legend: { display: !hideLegend, position: 'bottom', labels: { boxWidth: 12, padding: 18, fontColor: '#52606d' } },
            tooltips: { callbacks: { label: function (item, chart) { var label = chart.datasets[item.datasetIndex].label || 'Ventas'; return label + ': ' + money(Number(item.yLabel), false); } } },
            scales: {
                xAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#71808d' } }],
                yAxes: [{ gridLines: { color: '#edf1f3', drawBorder: false }, ticks: { beginAtZero: true, fontColor: '#71808d', stepSize: step, callback: function (value) { return money(Number(value), true); } } }]
            }
        };
    }
    function updateKpis(data, years, indexes) {
        var latest = years[years.length - 1];
        var prior = years.length > 1 ? years[years.length - 2] : null;
        var values = yearValues(data, latest, indexes);
        var available = values.filter(function (value) { return value !== null; });
        var total = sum(values);
        var priorTotal = prior ? sum(yearValues(data, prior, indexes)) : null;
        var change = prior ? percent(total, priorTotal) : null;
        var best = { value: null, index: null };
        indexes.forEach(function (index) {
            var value = data.data[latest][index];
            if (value !== null && (best.value === null || value > best.value)) best = { value: value, index: index };
        });
        document.getElementById('sales-total').textContent = money(total, true);
        document.getElementById('sales-total-detail').textContent = latest + ' · ' + data.months[indexes[0]] + ' a ' + data.months[indexes[indexes.length - 1]];
        var yoy = document.getElementById('sales-yoy');
        yoy.textContent = change === null ? '—' : (change >= 0 ? '+' : '') + change.toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
        yoy.className = 'sales-kpi-value ' + (change === null ? '' : change >= 0 ? 'sales-positive' : 'sales-negative');
        document.getElementById('sales-yoy-detail').textContent = prior ? latest + ' vs. ' + prior + ' · mismo periodo' : 'Selecciona al menos dos años';
        document.getElementById('sales-best').textContent = best.index === null ? '—' : data.months[best.index] + ' ' + latest;
        document.getElementById('sales-best-detail').textContent = money(best.value, false);
        document.getElementById('sales-average').textContent = available.length ? money(total / available.length, true) : '—';
        document.getElementById('sales-average-detail').textContent = available.length + ' meses con información';
    }
    function updateCharts(data, years, indexes) {
        var labels = indexes.map(function (index) { return data.months[index]; });
        var datasets = years.map(function (year, colorIndex) {
            return { label: year, data: yearValues(data, year, indexes), borderColor: colors[colorIndex % colors.length], backgroundColor: colors[colorIndex % colors.length], borderWidth: 3, pointRadius: 3, pointHoverRadius: 5, fill: false, lineTension: .25, spanGaps: false };
        });
        var maxMonthly = Math.max.apply(null, datasets.reduce(function (all, set) { return all.concat(set.data.filter(function (value) { return value !== null; }).map(Math.abs)); }, [0]));
        if (monthlyChart) monthlyChart.destroy();
        monthlyChart = new Chart(document.getElementById('sales-monthly-chart'), { type: 'line', data: { labels: labels, datasets: datasets }, options: chartOptions(niceStep(maxMonthly), false) });

        var totals = years.map(function (year) { return sum(yearValues(data, year, indexes)); });
        var maxAnnual = Math.max.apply(null, totals.map(Math.abs).concat([0]));
        if (annualChart) annualChart.destroy();
        annualChart = new Chart(document.getElementById('sales-annual-chart'), { type: 'bar', data: { labels: years, datasets: [{ data: totals, backgroundColor: years.map(function (_, index) { return colors[index % colors.length]; }) }] }, options: chartOptions(niceStep(maxAnnual), true) });
    }
    function updateTable(data, years, indexes) {
        document.getElementById('sales-table-head').innerHTML = '<th>Año</th>' + indexes.map(function (index) { return '<th class="text-right">' + data.months[index] + '</th>'; }).join('') + '<th class="text-right">Total</th>';
        document.getElementById('sales-table-body').innerHTML = years.map(function (year) {
            var values = yearValues(data, year, indexes);
            var total = values.some(function (value) { return value !== null; }) ? sum(values) : null;
            return '<tr><td><span class="badge badge-light">' + year + '</span></td>' + values.map(function (value) { return '<td class="text-right">' + money(value, false) + '</td>'; }).join('') + '<td class="text-right font-weight-bold">' + money(total, false) + '</td></tr>';
        }).join('');
    }
    function updateInsights(data, years, indexes) {
        var totals = years.map(function (year) { return { year: year, total: sum(yearValues(data, year, indexes)) }; });
        var leader = totals.reduce(function (best, current) { return current.total > best.total ? current : best; }, totals[0]);
        var latest = years[years.length - 1];
        var prior = years.length > 1 ? years[years.length - 2] : null;
        var latestTotal = totals[totals.length - 1].total;
        var priorTotal = prior ? totals[totals.length - 2].total : null;
        var change = prior ? percent(latestTotal, priorTotal) : null;
        var available = yearValues(data, latest, indexes).filter(function (value) { return value !== null; }).length;
        var insights = [
            '<strong>' + leader.year + '</strong> registra el mayor acumulado del periodo: ' + money(leader.total, false) + '.',
            change === null ? 'Selecciona dos o más años para calcular la variación interanual.' : 'Las ventas de <strong>' + latest + '</strong> ' + (change >= 0 ? 'aumentan' : 'disminuyen') + ' <strong>' + Math.abs(change).toLocaleString('es-PE', { maximumFractionDigits: 1 }) + '%</strong> frente a ' + prior + '.',
            latest + ' cuenta con información en <strong>' + available + '</strong> de los ' + indexes.length + ' meses seleccionados.'
        ];
        document.getElementById('sales-insights').innerHTML = insights.map(function (text) { return '<li>' + text + '</li>'; }).join('');
    }
    function refresh(data) {
        var years = selectedYears();
        var indexes = monthIndexes();
        var dataYears = years.filter(function (year) { return yearValues(data, year, indexes).some(function (value) { return value !== null; }); });
        var activeYears = dataYears.length ? dataYears : years;
        document.getElementById('sales-trend-subtitle').textContent = data.months[indexes[0]] + ' a ' + data.months[indexes[indexes.length - 1]] + ' · importes en soles';
        updateKpis(data, activeYears, indexes); updateCharts(data, activeYears, indexes); updateTable(data, years, indexes); updateInsights(data, activeYears, indexes);
    }
    window.initVentasDashboard = function () {
        var data = payload();
        var from = document.getElementById('sales-month-from');
        var to = document.getElementById('sales-month-to');
        data.months.forEach(function (month, index) { from.add(new Option(month, index)); to.add(new Option(month, index)); });
        var latestYear = String(Math.max.apply(null, data.years));
        var latestMonth = data.data[latestYear].reduce(function (last, value, index) { return value === null ? last : index; }, 0);
        from.value = 0; to.value = latestMonth;
        document.querySelectorAll('#sales-year-options input, #sales-month-from, #sales-month-to').forEach(function (control) { control.addEventListener('change', function () { refresh(data); }); });
        document.getElementById('reset-sales').addEventListener('click', function () { document.querySelectorAll('#sales-year-options input').forEach(function (input) { input.checked = true; }); from.value = 0; to.value = latestMonth; refresh(data); });
        refresh(data);
    };
}());
