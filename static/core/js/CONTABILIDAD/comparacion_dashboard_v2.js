(function () {
    'use strict';
    var moneyChart, boxesChart;
    var colors = ['#0b6b45', '#278ba8', '#7c4dcc', '#e58a13'];
    var lightColors = ['#74b99c', '#82c5d6', '#b69ae2', '#f1bd70'];
    function payload() { return JSON.parse(document.getElementById('comparacion-data').textContent); }
    function metricMap(data) { return data.metrics.reduce(function (map, metric) { map[metric.key] = metric; return map; }, {}); }
    function selectedYears() {
        var years = Array.prototype.slice.call(document.querySelectorAll('#comparison-years input:checked')).map(function (input) { return input.value; }).sort();
        if (!years.length) { var options = document.querySelectorAll('#comparison-years input'), latest = options[options.length - 1]; latest.checked = true; years = [latest.value]; }
        return years;
    }
    function indexes() { var start = Number(document.getElementById('comparison-from').value), end = Number(document.getElementById('comparison-to').value); if (start > end) { var swap = start; start = end; end = swap; document.getElementById('comparison-from').value = start; document.getElementById('comparison-to').value = end; } var result = []; for (var i = start; i <= end; i += 1) result.push(i); return result; }
    function sum(values) { return values.reduce(function (total, value) { return total + Number(value || 0); }, 0); }
    function valuesFor(metrics, key, year, monthIndexes) { return monthIndexes.map(function (index) { return Number(metrics[key].values[year][index] || 0); }); }
    function format(value, type, compact) { value = Number(value || 0); var prefix = type === 'pen' ? 'S/ ' : type === 'usd' ? 'US$ ' : ''; if (compact && Math.abs(value) >= 1000000) return prefix + (value / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' M'; if (compact && Math.abs(value) >= 1000) return prefix + (value / 1000).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' mil'; var decimals = type === 'number' ? 0 : 2; return prefix + value.toLocaleString('es-PE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + (type === 'kilos' ? ' kg' : ''); }
    function tableValue(value, type) { return Number(value || 0) === 0 ? '—' : format(value, type, false); }
    function tick(value, currency) { var prefix = currency ? 'S/ ' : ''; if (Math.abs(value) >= 1000000) return prefix + (value / 1000000).toLocaleString('es-PE', { maximumFractionDigits: 1 }) + ' M'; if (Math.abs(value) >= 1000) return prefix + (value / 1000).toLocaleString('es-PE', { maximumFractionDigits: 0 }) + ' mil'; return prefix + value; }
    function chartOptions(currency) { return { maintainAspectRatio: false, responsive: true, legend: { position: 'bottom', labels: { boxWidth: 12, padding: 14, fontColor: '#52606d' } }, tooltips: { mode: 'index', intersect: false, callbacks: { label: function (item, data) { return data.datasets[item.datasetIndex].label + ': ' + (currency ? format(item.yLabel, 'pen', false) : format(item.yLabel, 'number', false)); } } }, scales: { xAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#71808d' } }], yAxes: [{ gridLines: { color: '#edf1f3', drawBorder: false }, ticks: { beginAtZero: true, fontColor: '#71808d', callback: function (value) { return tick(Number(value), currency); } } }] } }; }
    function totalsByMonth(metrics, keys, year, monthIndexes) { return monthIndexes.map(function (_, position) { return keys.reduce(function (total, key) { return total + valuesFor(metrics, key, year, monthIndexes)[position]; }, 0); }); }
    function renderCharts(data, metrics, years, monthIndexes) {
        var labels = monthIndexes.map(function (index) { return data.months[index]; });
        var moneySets = [], boxSets = [];
        years.forEach(function (year, index) {
            moneySets.push({ label: year + ' Ingresos', data: totalsByMonth(metrics, ['income_maquila', 'income_export', 'income_goods', 'other_income'], year, monthIndexes), borderColor: colors[index % colors.length], backgroundColor: colors[index % colors.length], borderWidth: 3, pointRadius: 2, fill: false, lineTension: .2 });
            moneySets.push({ label: year + ' Costos y gastos', data: totalsByMonth(metrics, ['cost_maquila', 'cost_export', 'cost_goods', 'other_expenses', 'profit_sharing', 'income_tax'], year, monthIndexes), borderColor: lightColors[index % lightColors.length], backgroundColor: lightColors[index % lightColors.length], borderDash: [6, 4], borderWidth: 2, pointRadius: 2, fill: false, lineTension: .2 });
            boxSets.push({ label: year + ' Maquila', data: valuesFor(metrics, 'boxes_maquila', year, monthIndexes), backgroundColor: colors[index % colors.length] });
            boxSets.push({ label: year + ' Exportación', data: valuesFor(metrics, 'boxes_export', year, monthIndexes), backgroundColor: lightColors[index % lightColors.length] });
        });
        if (moneyChart) moneyChart.destroy();
        moneyChart = new Chart(document.getElementById('comparison-money-chart'), { type: 'line', data: { labels: labels, datasets: moneySets }, options: chartOptions(true) });
        if (boxesChart) boxesChart.destroy();
        boxesChart = new Chart(document.getElementById('comparison-boxes-chart'), { type: 'bar', data: { labels: labels, datasets: boxSets }, options: chartOptions(false) });
    }
    function tableForYear(data, year, monthIndexes) {
        var head = '<thead><tr><th>Descripción</th>' + monthIndexes.map(function (index) { return '<th class="text-right">' + data.months[index].slice(0, 3) + '-' + String(year).slice(2) + '</th>'; }).join('') + '<th class="text-right">Total</th></tr></thead>';
        var body = '<tbody>' + data.metrics.map(function (metric) { var values = monthIndexes.map(function (index) { return Number(metric.values[year][index] || 0); }); var resultRow = metric.key === 'result_pen' || metric.key === 'result_usd'; return '<tr data-metric="' + metric.key + '" class="' + (resultRow ? 'result-row' : '') + '"><td>' + metric.label + '</td>' + values.map(function (value, position) { return '<td data-month="' + monthIndexes[position] + '" class="text-right comparison-month-value ' + (value < 0 ? 'negative' : '') + '">' + tableValue(value, metric.format) + '</td>'; }).join('') + '<td class="text-right ' + (sum(values) < 0 ? 'negative' : '') + '">' + tableValue(sum(values), metric.format) + '</td></tr>'; }).join('') + '</tbody>';
        return '<div class="table-responsive comparison-table-wrap"><table class="table comparison-table mb-0">' + head + body + '</table></div>';
    }
    function renderDetails(data, years, monthIndexes) {
        var tabs = document.getElementById('comparison-detail-tabs'), content = document.getElementById('comparison-detail-content');
        tabs.innerHTML = years.map(function (year, index) { return '<li class="nav-item"><button type="button" class="nav-link ' + (index === 0 ? 'active' : '') + '" data-year="' + year + '">Detalle ' + year + '</button></li>'; }).join('');
        content.innerHTML = years.map(function (year, index) { return '<div class="comparison-detail-pane ' + (index === 0 ? 'active' : '') + '" data-year="' + year + '">' + tableForYear(data, year, monthIndexes) + '</div>'; }).join('');
        tabs.querySelectorAll('button').forEach(function (button) { button.addEventListener('click', function () { tabs.querySelectorAll('button').forEach(function (item) { item.classList.toggle('active', item === button); }); content.querySelectorAll('.comparison-detail-pane').forEach(function (pane) { pane.classList.toggle('active', pane.getAttribute('data-year') === button.getAttribute('data-year')); }); }); });
        var tooltip = document.getElementById('comparison-row-tooltip'), metrics = metricMap(data);
        function positionTooltip(event) { tooltip.style.left = Math.min(event.clientX + 18, window.innerWidth - 350) + 'px'; tooltip.style.top = Math.min(Math.max(event.clientY - 35, 8), window.innerHeight - 190) + 'px'; }
        content.querySelectorAll('tr[data-metric] td:first-child').forEach(function (cell) {
            cell.addEventListener('mouseenter', function (event) {
                var metric = metrics[cell.parentNode.getAttribute('data-metric')], grandTotal = 0;
                var lines = [metric.label];
                years.forEach(function (year) { var yearlyTotal = sum(valuesFor(metrics, metric.key, year, monthIndexes)); grandTotal += yearlyTotal; lines.push('Año ' + year + ': ' + format(yearlyTotal, metric.format, false)); });
                lines.push('Total seleccionado: ' + format(grandTotal, metric.format, false));
                tooltip.textContent = lines.join('\n'); tooltip.classList.add('is-visible'); positionTooltip(event);
            });
            cell.addEventListener('mousemove', positionTooltip);
            cell.addEventListener('mouseleave', function () { tooltip.classList.remove('is-visible'); });
        });
        content.querySelectorAll('tr[data-metric] td[data-month]').forEach(function (cell) {
            cell.addEventListener('mouseenter', function (event) {
                var metric = metrics[cell.parentNode.getAttribute('data-metric')], monthIndex = Number(cell.getAttribute('data-month')), monthTotal = 0;
                var lines = [metric.label + ' · ' + data.months[monthIndex]];
                years.forEach(function (year) { var value = Number(metric.values[year][monthIndex] || 0); monthTotal += value; lines.push('Año ' + year + ': ' + format(value, metric.format, false)); });
                lines.push('Total del mes: ' + format(monthTotal, metric.format, false));
                tooltip.textContent = lines.join('\n'); tooltip.classList.add('is-visible'); positionTooltip(event);
            });
            cell.addEventListener('mousemove', positionTooltip);
            cell.addEventListener('mouseleave', function () { tooltip.classList.remove('is-visible'); });
        });
    }
    function refresh(data) {
        var metrics = metricMap(data), years = selectedYears(), monthIndexes = indexes();
        var resultPen = sum(years.map(function (year) { return sum(valuesFor(metrics, 'result_pen', year, monthIndexes)); }));
        var resultUsd = sum(years.map(function (year) { return sum(valuesFor(metrics, 'result_usd', year, monthIndexes)); }));
        var income = sum(years.map(function (year) { return ['income_maquila', 'income_export', 'income_goods', 'other_income'].reduce(function (total, key) { return total + sum(valuesFor(metrics, key, year, monthIndexes)); }, 0); }));
        var boxes = sum(years.map(function (year) { return sum(valuesFor(metrics, 'boxes_maquila', year, monthIndexes)) + sum(valuesFor(metrics, 'boxes_export', year, monthIndexes)); }));
        var pen = document.getElementById('comparison-result-pen'); pen.textContent = format(resultPen, 'pen', true); pen.className = 'kpi-value ' + (resultPen < 0 ? 'kpi-negative' : 'kpi-positive');
        var usd = document.getElementById('comparison-result-usd'); usd.textContent = format(resultUsd, 'usd', true); usd.className = 'kpi-value ' + (resultUsd < 0 ? 'kpi-negative' : 'kpi-positive');
        document.getElementById('comparison-income').textContent = format(income, 'pen', true);
        document.getElementById('comparison-boxes').textContent = format(boxes, 'number', false);
        document.getElementById('comparison-period').textContent = years.join(', ') + ' · ' + data.months[monthIndexes[0]] + ' a ' + data.months[monthIndexes[monthIndexes.length - 1]];
        renderCharts(data, metrics, years, monthIndexes);
        renderDetails(data, years, monthIndexes);
    }
    window.initComparacionDashboard = function () {
        var data = payload(), from = document.getElementById('comparison-from'), to = document.getElementById('comparison-to');
        data.months.forEach(function (month, index) { from.add(new Option(month, index)); to.add(new Option(month, index)); });
        var latest = String(data.years[data.years.length - 1]), last = 0;
        document.querySelector('#comparison-years input[value="' + latest + '"]').checked = true;
        data.metrics.forEach(function (metric) { metric.values[latest].forEach(function (value, index) { if (Number(value || 0) !== 0) last = Math.max(last, index); }); });
        from.value = 0; to.value = last;
        document.querySelectorAll('#comparison-years input, #comparison-from, #comparison-to').forEach(function (control) { control.addEventListener('change', function () { refresh(data); }); });
        document.getElementById('reset-comparison').addEventListener('click', function () { document.querySelectorAll('#comparison-years input').forEach(function (input) { input.checked = input.value === latest; }); from.value = 0; to.value = last; refresh(data); });
        refresh(data);
    };
}());
