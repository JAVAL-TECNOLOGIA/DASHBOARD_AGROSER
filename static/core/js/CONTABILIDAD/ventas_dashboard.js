(function () {
    'use strict';

    var colors = ['#0b6b45', '#278ba8', '#7c4dcc', '#e58a13'];
    var monthlyChart;
    var annualChart;
    var customerChart;
    var currentView;
    var currentYears = [];
    var currentIndexes = [];

    function payload() { return JSON.parse(document.getElementById('ventas-data').textContent); }
    function money(value, compact) {
        if (value === null || typeof value === 'undefined' || isNaN(value)) return '—';
        if (compact && Math.abs(value) >= 1000000) return 'S/ ' + (value / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' M';
        if (compact && Math.abs(value) >= 1000) return 'S/ ' + (value / 1000).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' mil';
        return 'S/ ' + Number(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    function dollars(value, compact) {
        if (value === null || typeof value === 'undefined' || isNaN(value)) return '—';
        if (compact && Math.abs(value) >= 1000000) return 'US$ ' + (value / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' M';
        if (compact && Math.abs(value) >= 1000) return 'US$ ' + (value / 1000).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' mil';
        return 'US$ ' + Number(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
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
    function updateCustomerOptions(data, years, indexes) {
        var select = document.getElementById('sales-customer');
        var current = select.value;
        var customers = Array.from(new Set(data.sales.filter(function (row) { return years.indexOf(String(row.year)) >= 0 && indexes.indexOf(row.month) >= 0 && row.total !== 0; }).map(function (row) { return row.customer; }))).sort();
        select.innerHTML = '';
        select.add(new Option('Todas las razones sociales', '__all__'));
        customers.forEach(function (customer) { select.add(new Option(customer, customer)); });
        select.value = customers.indexOf(current) >= 0 ? current : '__all__';
    }
    function filteredData(data) {
        var customer = document.getElementById('sales-customer').value;
        var filtered = data.sales.filter(function (row) { return customer === '__all__' || row.customer === customer; });
        var view = { months: data.months, years: data.years, sales: filtered, data: {}, data_usd: {} };
        data.years.forEach(function (year) { view.data[String(year)] = Array(12).fill(null); view.data_usd[String(year)] = Array(12).fill(null); });
        filtered.forEach(function (row) { var year = String(row.year); if (view.data[year][row.month] === null) { view.data[year][row.month] = 0; view.data_usd[year][row.month] = 0; } view.data[year][row.month] += row.total; view.data_usd[year][row.month] += row.total_usd; });
        return view;
    }
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
        var total = sum(years.reduce(function (all, year) { return all.concat(yearValues(data, year, indexes)); }, []));
        var totalUsd = sum(years.reduce(function (all, year) {
            return all.concat(indexes.map(function (index) { return data.data_usd[year][index]; }));
        }, []));
        var selectedPeriod = (years.length === 1 ? years[0] : years[0] + ' a ' + years[years.length - 1]) + ' · ' + data.months[indexes[0]] + ' a ' + data.months[indexes[indexes.length - 1]];
        var selectedSales = data.sales.filter(function (row) { return years.indexOf(String(row.year)) >= 0 && indexes.indexOf(row.month) >= 0; });
        var affected = selectedSales.reduce(function (value, row) { return value + row.affected; }, 0);
        var exported = selectedSales.reduce(function (value, row) { return value + row.exported; }, 0);
        var exempt = selectedSales.reduce(function (value, row) { return value + row.exempt; }, 0);
        document.getElementById('sales-total').textContent = money(total, true);
        document.getElementById('sales-total-detail').textContent = selectedPeriod;
        document.getElementById('sales-total-usd').textContent = dollars(totalUsd, true);
        document.getElementById('sales-total-usd-detail').textContent = selectedPeriod;
        document.getElementById('sales-affected').textContent = money(affected, true);
        document.getElementById('sales-affected-detail').textContent = selectedPeriod;
        document.getElementById('sales-exported').textContent = money(exported, true);
        document.getElementById('sales-exported-detail').textContent = selectedPeriod;
        document.getElementById('sales-exempt').textContent = money(exempt, true);
        document.getElementById('sales-exempt-detail').textContent = selectedPeriod;
    }
    function showBreakdown(kind) {
        var labels = { affected: 'Venta afectada', exported: 'Venta de exportación', exempt: 'Venta exonerada' };
        var totals = {};
        currentView.sales.forEach(function (row) {
            if (currentYears.indexOf(String(row.year)) < 0 || currentIndexes.indexOf(row.month) < 0 || !row[kind]) return;
            totals[row.customer] = (totals[row.customer] || 0) + row[kind];
        });
        var rows = Object.keys(totals).map(function (customer) { return { customer: customer, total: totals[customer] }; }).sort(function (a, b) { return b.total - a.total; });
        document.getElementById('sales-breakdown-title').textContent = 'Razones sociales · ' + labels[kind];
        document.getElementById('sales-breakdown-period').textContent = (currentYears.length === 1 ? currentYears[0] : currentYears[0] + ' a ' + currentYears[currentYears.length - 1]) + ' · ' + currentView.months[currentIndexes[0]] + ' a ' + currentView.months[currentIndexes[currentIndexes.length - 1]];
        document.getElementById('sales-breakdown-body').innerHTML = rows.length ? rows.map(function (row) { return '<tr><td>' + row.customer + '</td><td class="text-right">' + money(row.total, false) + '</td></tr>'; }).join('') : '<tr><td colspan="2" class="text-center text-muted py-4">No hay razones sociales para esta venta en el periodo seleccionado.</td></tr>';
        document.getElementById('sales-breakdown-total').textContent = money(rows.reduce(function (total, row) { return total + row.total; }, 0), false);
        $('#sales-breakdown-modal').modal('show');
    }
    function updateCustomerChart(data, years, indexes) {
        var totals = {};
        var totalsByYear = {};
        years.forEach(function (year) { totalsByYear[year] = {}; });
        data.sales.forEach(function (row) {
            var year = String(row.year);
            if (years.indexOf(year) < 0 || indexes.indexOf(row.month) < 0) return;
            totals[row.customer] = (totals[row.customer] || 0) + row.total;
            totalsByYear[year][row.customer] = (totalsByYear[year][row.customer] || 0) + row.total;
        });
        var customers = Object.keys(totals).sort(function (a, b) { return totals[b] - totals[a]; }).slice(0, 12);
        var datasets = years.map(function (year, index) {
            return {
                label: year,
                data: customers.map(function (customer) { return totalsByYear[year][customer] || 0; }),
                backgroundColor: colors[index % colors.length],
                borderWidth: 0
            };
        });
        var yearLabel = years.length === 1 ? years[0] : years.join(', ');
        var subtitle = document.getElementById('sales-customer-chart-subtitle');
        if (subtitle) subtitle.textContent = 'Acumulado ' + yearLabel + ' · ' + data.months[indexes[0]] + ' a ' + data.months[indexes[indexes.length - 1]];
        if (customerChart) customerChart.destroy();
        customerChart = new Chart(document.getElementById('sales-customer-chart'), { type: 'horizontalBar', data: { labels: customers, datasets: datasets }, options: { maintainAspectRatio: false, responsive: true, legend: { display: true, position: 'bottom', labels: { boxWidth: 12, padding: 18, fontColor: '#52606d' } }, tooltips: { mode: 'index', intersect: false, callbacks: { label: function (item, chart) { return chart.datasets[item.datasetIndex].label + ': ' + money(Number(item.xLabel), false); } } }, scales: { xAxes: [{ ticks: { beginAtZero: true, callback: function (value) { return money(Number(value), true); } }, gridLines: { color: '#edf1f3' } }], yAxes: [{ gridLines: { display: false } }] } } });
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
        updateCustomerOptions(data, years, indexes);
        data = filteredData(data);
        var dataYears = years.filter(function (year) { return yearValues(data, year, indexes).some(function (value) { return value !== null; }); });
        var activeYears = dataYears.length ? dataYears : years;
        currentView = data; currentYears = activeYears; currentIndexes = indexes;
        document.getElementById('sales-trend-subtitle').textContent = data.months[indexes[0]] + ' a ' + data.months[indexes[indexes.length - 1]] + ' · importes en soles';
        updateKpis(data, activeYears, indexes); updateCharts(data, activeYears, indexes); updateCustomerChart(data, activeYears, indexes); updateTable(data, years, indexes); updateInsights(data, activeYears, indexes);
    }
    window.initVentasDashboard = function () {
        var data = payload();
        var from = document.getElementById('sales-month-from');
        var to = document.getElementById('sales-month-to');
        data.months.forEach(function (month, index) { from.add(new Option(month, index)); to.add(new Option(month, index)); });
        var latestYear = String(Math.max.apply(null, data.years));
        var latestMonth = data.data[latestYear].reduce(function (last, value, index) { return value === null ? last : index; }, 0);
        from.value = 0; to.value = latestMonth;
        document.querySelectorAll('#sales-year-options input, #sales-customer, #sales-month-from, #sales-month-to').forEach(function (control) { control.addEventListener('change', function () { refresh(data); }); });
        document.getElementById('reset-sales').addEventListener('click', function () { document.querySelectorAll('#sales-year-options input').forEach(function (input) { input.checked = true; }); document.getElementById('sales-customer').value='__all__'; from.value = 0; to.value = latestMonth; refresh(data); });
        document.querySelectorAll('.sales-kpi-breakdown').forEach(function (card) {
            function openDetail() { showBreakdown(card.getAttribute('data-sales-kind')); }
            card.addEventListener('click', openDetail);
            card.addEventListener('keydown', function (event) { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openDetail(); } });
        });
        refresh(data);
    };
}());
