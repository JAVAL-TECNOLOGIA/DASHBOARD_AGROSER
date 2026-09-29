(function () {
    'use strict';

    var colors = ['#0b6b45', '#278ba8', '#7c4dcc', '#e58a13', '#b7442b', '#4e6f8a', '#5f9e63'];
    var monthChart, yearChart, topChart, areaChart;

    function payload() { return JSON.parse(document.getElementById('costos-gastos-data').textContent); }
    function money(value, compact) {
        if (value === null || typeof value === 'undefined' || isNaN(value)) return '—';
        if (compact && Math.abs(value) >= 1000000) return 'S/ ' + (value / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' M';
        if (compact && Math.abs(value) >= 1000) return 'S/ ' + (value / 1000).toLocaleString('es-PE', { minimumFractionDigits: 0, maximumFractionDigits: 1 }) + ' mil';
        return 'S/ ' + value.toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    function percent(current, previous) { return previous ? ((current - previous) / Math.abs(previous)) * 100 : null; }
    function selectedMonths() {
        var values = Array.prototype.slice.call(document.querySelectorAll('#cost-months input:checked')).map(function (input) { return Number(input.value); });
        if (!values.length) { var first = document.querySelector('#cost-months input'); first.checked = true; values = [Number(first.value)]; }
        return values.sort();
    }
    function indexData(data) {
        data.periodMap = {};
        data.periods.forEach(function (period) {
            period.rowMap = {};
            period.rows.forEach(function (row) { period.rowMap[row.key] = row; });
            data.periodMap[period.key] = period;
        });
    }
    function rowValue(period, key, area) {
        var row = period && period.rowMap[key];
        if (!row) return 0;
        return area === '__total__' ? row.total : (row.areas[area] || 0);
    }
    function keysForFilter(data, indicator) {
        if (indicator !== '__all__') return [indicator];
        return data.accounts.map(function (item) { return item.account + ' | ' + item.description; });
    }
    function periodValue(data, year, month, area, keys) {
        var period = data.periodMap[year + '-' + String(month).padStart(2, '0')];
        return keys.reduce(function (total, key) { return total + rowValue(period, key, area); }, 0);
    }
    function yearlyValue(data, year, months, area, keys) {
        return months.reduce(function (total, month) { return total + periodValue(data, year, month, area, keys); }, 0);
    }
    function niceStep(maxValue) {
        if (!maxValue) return 10000;
        var raw = maxValue / 6;
        var magnitude = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10));
        var normalized = raw / magnitude;
        return (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude;
    }
    function axisOptions(step) {
        return { gridLines: { color: '#edf1f3', drawBorder: false }, ticks: { beginAtZero: true, fontColor: '#71808d', stepSize: step, callback: function (value) { return money(Number(value), true); } } };
    }
    function baseOptions(step, legend) {
        return {
            maintainAspectRatio: false, responsive: true,
            legend: { display: legend, position: 'bottom', labels: { boxWidth: 12, padding: 18, fontColor: '#52606d' } },
            tooltips: { callbacks: { label: function (item, chart) { var label = chart.datasets[item.datasetIndex].label || ''; return label + ': ' + money(Number(item.yLabel), false); } } },
            scales: { xAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#71808d' } }], yAxes: [axisOptions(step)] }
        };
    }
    function updateKpis(data, months, area, keys) {
        var total25 = yearlyValue(data, 2025, months, area, keys);
        var total26 = yearlyValue(data, 2026, months, area, keys);
        var change = percent(total26, total25);
        var ranking = keys.map(function (key) { return { key: key, value: yearlyValue(data, 2026, months, area, [key]) }; }).sort(function (a, b) { return Math.abs(b.value) - Math.abs(a.value); });
        var top = ranking[0] || { key: '—', value: 0 };
        document.getElementById('cost-total-latest').textContent = money(total26, true);
        document.getElementById('cost-total-detail').textContent = months.map(function (m) { return m === 6 ? 'Junio' : 'Julio'; }).join(' + ') + ' 2026';
        var yoy = document.getElementById('cost-yoy');
        yoy.textContent = change === null ? '—' : (change >= 0 ? '+' : '') + change.toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
        yoy.className = 'cost-kpi-value ' + (change === null ? '' : change >= 0 ? 'cost-negative' : 'cost-positive');
        document.getElementById('cost-top-name').textContent = top.key.replace(' | ', ' · ');
        document.getElementById('cost-top-value').textContent = money(top.value, false);
        document.getElementById('cost-active-count').textContent = ranking.filter(function (item) { return item.value !== 0; }).length.toLocaleString('es-PE');
    }
    function updatePeriodSummary(data, months, area, keys) {
        [2025, 2026].forEach(function (year) {
            [6, 7].forEach(function (month) {
                var element = document.getElementById('cost-period-' + year + '-' + month);
                var enabled = months.indexOf(month) !== -1;
                element.textContent = enabled ? money(periodValue(data, year, month, area, keys), false) : 'No seleccionado';
                element.parentElement.parentElement.style.opacity = enabled ? '1' : '.5';
            });
        });
    }
    function updateMainCharts(data, months, area, keys) {
        var labels = months.map(function (month) { return month === 6 ? 'Junio' : 'Julio'; });
        var monthDatasets = [2025, 2026].map(function (year, index) {
            return { label: String(year), data: months.map(function (month) { return periodValue(data, year, month, area, keys); }), backgroundColor: colors[index], borderRadius: 4 };
        });
        var monthMax = Math.max.apply(null, monthDatasets.reduce(function (all, set) { return all.concat(set.data.map(Math.abs)); }, [0]));
        if (monthChart) monthChart.destroy();
        monthChart = new Chart(document.getElementById('cost-month-chart'), { type: 'bar', data: { labels: labels, datasets: monthDatasets }, options: baseOptions(niceStep(monthMax), true) });

        var totals = [2025, 2026].map(function (year) { return yearlyValue(data, year, months, area, keys); });
        var annualMax = Math.max.apply(null, totals.map(Math.abs).concat([0]));
        if (yearChart) yearChart.destroy();
        yearChart = new Chart(document.getElementById('cost-year-chart'), { type: 'bar', data: { labels: ['2025', '2026'], datasets: [{ data: totals, backgroundColor: [colors[0], colors[1]] }] }, options: baseOptions(niceStep(annualMax), false) });
    }
    function updateTopChart(data, months, area, allKeys) {
        var ranking = allKeys.map(function (key) { return { key: key, value: yearlyValue(data, 2026, months, area, [key]) }; })
            .filter(function (item) { return item.value !== 0; }).sort(function (a, b) { return Math.abs(b.value) - Math.abs(a.value); }).slice(0, 10).reverse();
        var labels = ranking.map(function (item) { var label = item.key.replace(' | ', ' · '); return label.length > 42 ? label.slice(0, 41) + '…' : label; });
        var values25 = ranking.map(function (item) { return yearlyValue(data, 2025, months, area, [item.key]); });
        var values26 = ranking.map(function (item) { return item.value; });
        var max = Math.max.apply(null, values25.concat(values26).map(Math.abs).concat([0]));
        if (topChart) topChart.destroy();
        topChart = new Chart(document.getElementById('cost-top-chart'), {
            type: 'horizontalBar', data: { labels: labels, datasets: [{ label: '2025', data: values25, backgroundColor: colors[0] }, { label: '2026', data: values26, backgroundColor: colors[1] }] },
            options: { maintainAspectRatio: false, responsive: true, legend: { position: 'bottom', labels: { boxWidth: 12, padding: 16 } }, tooltips: { callbacks: { label: function (item, chart) { return chart.datasets[item.datasetIndex].label + ': ' + money(Number(item.xLabel), false); } } }, scales: { xAxes: [axisOptions(niceStep(max))], yAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#52606d' } }] } }
        });
    }
    function updateAreaChart(data, months, keys) {
        var values = data.areas.map(function (area) { return yearlyValue(data, 2026, months, area, keys); });
        var filtered = data.areas.map(function (area, index) { return { area: area, value: values[index] }; }).filter(function (item) { return item.value !== 0; });
        if (areaChart) areaChart.destroy();
        areaChart = new Chart(document.getElementById('cost-area-chart'), {
            type: 'doughnut', data: { labels: filtered.map(function (item) { return item.area; }), datasets: [{ data: filtered.map(function (item) { return item.value; }), backgroundColor: colors }] },
            options: { maintainAspectRatio: false, responsive: true, cutoutPercentage: 62, legend: { position: 'bottom', labels: { boxWidth: 11, padding: 12, fontSize: 10 } }, tooltips: { callbacks: { label: function (item, chart) { return chart.labels[item.index] + ': ' + money(Number(chart.datasets[0].data[item.index]), false); } } } }
        });
    }
    function updateTable(data, months, area, keys) {
        var rows = keys.map(function (key) {
            var parts = key.split(' | '); var values = {};
            [2025, 2026].forEach(function (year) { [6, 7].forEach(function (month) { values[year + '-' + month] = periodValue(data, year, month, area, [key]); }); });
            values.total25 = months.reduce(function (total, month) { return total + values['2025-' + month]; }, 0);
            values.total26 = months.reduce(function (total, month) { return total + values['2026-' + month]; }, 0);
            values.change = percent(values.total26, values.total25);
            return { account: parts[0], description: parts.slice(1).join(' | '), values: values };
        }).filter(function (row) { return row.values.total25 !== 0 || row.values.total26 !== 0; }).sort(function (a, b) { return Math.abs(b.values.total26) - Math.abs(a.values.total26); });
        document.getElementById('cost-detail-body').innerHTML = rows.map(function (row) {
            var v = row.values; var cls = v.change === null ? '' : v.change > 0 ? 'cost-row-negative' : 'cost-row-positive';
            return '<tr><td class="font-weight-bold">' + row.account + '</td><td>' + row.description + '</td>' +
                '<td class="text-right">' + money(v['2025-6'], false) + '</td><td class="text-right">' + money(v['2025-7'], false) + '</td><td class="text-right font-weight-bold">' + money(v.total25, false) + '</td>' +
                '<td class="text-right">' + money(v['2026-6'], false) + '</td><td class="text-right">' + money(v['2026-7'], false) + '</td><td class="text-right font-weight-bold">' + money(v.total26, false) + '</td>' +
                '<td class="text-right ' + cls + '">' + (v.change === null ? '—' : (v.change >= 0 ? '+' : '') + v.change.toLocaleString('es-PE', { maximumFractionDigits: 1 }) + '%') + '</td></tr>';
        }).join('');
    }
    function refresh(data) {
        var months = selectedMonths(); var area = document.getElementById('cost-area').value; var indicator = document.getElementById('cost-indicator').value;
        var keys = keysForFilter(data, indicator); var allKeys = data.accounts.map(function (item) { return item.account + ' | ' + item.description; });
        document.getElementById('cost-month-chart-subtitle').textContent = months.map(function (m) { return m === 6 ? 'Junio' : 'Julio'; }).join(' y ') + ' · 2025 vs. 2026';
        updatePeriodSummary(data, months, area, keys); updateKpis(data, months, area, keys); updateMainCharts(data, months, area, keys); updateTopChart(data, months, area, indicator === '__all__' ? allKeys : keys); updateAreaChart(data, months, keys); updateTable(data, months, area, keys);
    }
    window.initCostosGastosDashboard = function () {
        var data = payload(); indexData(data);
        document.querySelectorAll('#cost-months input, #cost-area, #cost-indicator').forEach(function (control) { control.addEventListener('change', function () { refresh(data); }); });
        document.getElementById('reset-costs').addEventListener('click', function () {
            document.querySelectorAll('#cost-months input').forEach(function (input) { input.checked = true; });
            document.getElementById('cost-area').value = '__total__'; document.getElementById('cost-indicator').value = '__all__'; refresh(data);
        });
        refresh(data);
    };
}());
