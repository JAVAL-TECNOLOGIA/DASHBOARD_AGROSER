(function () {
    'use strict';

    var monthlyChart = null;
    var statusChart = null;

    function payload() { return JSON.parse(document.getElementById('drawback-data').textContent); }
    function money(value, currency) { return new Intl.NumberFormat('es-PE', {style: 'currency', currency: currency || 'PEN', minimumFractionDigits: 2, maximumFractionDigits: 2}).format(Number(value || 0)); }
    function number(value, digits) { return Number(value || 0).toLocaleString('es-PE', {minimumFractionDigits: digits || 0, maximumFractionDigits: digits || 0}); }
    function escapeHtml(value) { return String(value == null ? '' : value).replace(/[&<>'"]/g, function (character) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'}[character]; }); }
    function dateLabel(value) { var parts = String(value || '').split('-'); return parts.length === 3 ? parts[2] + '/' + parts[1] + '/' + parts[0] : ''; }
    function total(rows, field) { return rows.reduce(function (sum, row) { return sum + Number(row[field] || 0); }, 0); }

    function state() {
        return {
            year: Number(document.getElementById('drawback-year').value),
            from: Number(document.getElementById('drawback-from').value),
            to: Number(document.getElementById('drawback-to').value),
            customer: document.getElementById('drawback-customer').value,
            status: document.getElementById('drawback-status').value,
            transport: document.getElementById('drawback-transport').value
        };
    }

    function activeRows(data, selected) {
        return data.rows.filter(function (row) {
            return row.year === selected.year && row.month >= selected.from && row.month <= selected.to &&
                (selected.customer === '__all__' || row.customer === selected.customer) &&
                (selected.status === '__all__' || row.status === selected.status) &&
                (selected.transport === '__all__' || row.transport === selected.transport);
        });
    }

    function refresh(data) {
        var selected = state();
        if (selected.from > selected.to) {
            document.getElementById('drawback-to').value = selected.from;
            selected.to = selected.from;
        }
        var rows = activeRows(data, selected);
        var invoiced = total(rows, 'invoice_amount') + total(rows, 'adjustment');
        document.getElementById('drawback-invoices').textContent = number(rows.length);
        document.getElementById('drawback-invoiced').textContent = money(invoiced, 'USD');
        document.getElementById('drawback-usd').textContent = money(total(rows, 'drawback_usd'), 'USD');
        document.getElementById('drawback-pen').textContent = money(total(rows, 'drawback_pen'));
        document.getElementById('drawback-pending').textContent = number(rows.filter(function (row) { return row.status === 'POR SOLICITAR'; }).length);
        document.getElementById('drawback-monthly-subtitle').textContent = selected.year + ' · ' + data.months[selected.from] + ' a ' + data.months[selected.to];

        document.getElementById('drawback-body').innerHTML = rows.length ? rows.map(function (row) {
            var badgeClass = row.status === 'ABONADA' ? 'status-paid' : 'status-pending';
            return '<tr><td>' + dateLabel(row.date) + '</td><td>' + escapeHtml(row.crop) + '</td><td><strong>' + escapeHtml(row.document) + '</strong></td>' +
                '<td>' + escapeHtml(row.customer) + '</td><td>' + escapeHtml(row.transport) + '</td>' +
                '<td class="amount">' + money(row.invoice_amount, 'USD') + '</td><td class="amount">' + money(row.adjustment, 'USD') + '</td>' +
                '<td>' + (row.credit_note ? escapeHtml(row.credit_note) : '—') + '</td><td class="amount">' + money(row.drawback_usd, 'USD') + '</td>' +
                '<td class="amount">' + number(row.payment_exchange_rate, 4) + '</td><td class="amount">' + money(row.drawback_pen) + '</td>' +
                '<td><span class="status-badge ' + badgeClass + '">' + escapeHtml(row.status) + '</span></td></tr>';
        }).join('') : '<tr><td colspan="12" class="text-center text-muted py-5">No hay documentos para los filtros seleccionados.</td></tr>';
        document.getElementById('drawback-foot').innerHTML = rows.length ? '<tr class="font-weight-bold" style="background:#eef8f4"><td colspan="5" class="text-right">TOTALES</td>' +
            '<td class="amount">' + money(total(rows, 'invoice_amount'), 'USD') + '</td><td class="amount">' + money(total(rows, 'adjustment'), 'USD') + '</td><td></td>' +
            '<td class="amount">' + money(total(rows, 'drawback_usd'), 'USD') + '</td><td></td><td class="amount">' + money(total(rows, 'drawback_pen')) + '</td><td></td></tr>' : '';

        var monthly = [];
        for (var month = selected.from; month <= selected.to; month += 1) {
            var monthRows = rows.filter(function (row) { return row.month === month; });
            monthly.push({month: month, usd: total(monthRows, 'drawback_usd'), pen: total(monthRows, 'drawback_pen')});
        }
        if (monthlyChart) monthlyChart.destroy();
        monthlyChart = new Chart(document.getElementById('drawback-monthly-chart'), {type: 'bar', data: {labels: monthly.map(function (row) { return data.months[row.month]; }), datasets: [
            {label: 'Drawback US$', data: monthly.map(function (row) { return row.usd; }), backgroundColor: '#2f8faa', yAxisID: 'usd-axis'},
            {label: 'Drawback S/', data: monthly.map(function (row) { return row.pen; }), backgroundColor: '#0f766e', yAxisID: 'pen-axis'}
        ]}, options: {responsive: true, maintainAspectRatio: false, tooltips: {callbacks: {label: function (item, chartData) { var currency = item.datasetIndex === 0 ? 'USD' : 'PEN'; return chartData.datasets[item.datasetIndex].label + ': ' + money(item.yLabel, currency); }}}, scales: {yAxes: [
            {id: 'usd-axis', position: 'left', ticks: {beginAtZero: true, callback: function (value) { return money(value, 'USD'); }}},
            {id: 'pen-axis', position: 'right', gridLines: {drawOnChartArea: false}, ticks: {beginAtZero: true, callback: function (value) { return money(value); }}}
        ]}}});

        var paid = rows.filter(function (row) { return row.status === 'ABONADA'; }).length;
        var pending = rows.length - paid;
        if (statusChart) statusChart.destroy();
        statusChart = new Chart(document.getElementById('drawback-status-chart'), {type: 'doughnut', data: {labels: ['Abonada', 'Por solicitar'], datasets: [{data: [paid, pending], backgroundColor: ['#0f766e', '#e78a0a'], borderColor: '#fff', borderWidth: 3}]}, options: {responsive: true, maintainAspectRatio: false, cutoutPercentage: 68, legend: {position: 'bottom'}, tooltips: {callbacks: {label: function (item, chartData) { return chartData.labels[item.index] + ': ' + number(chartData.datasets[0].data[item.index]); }}}}});
    }

    window.initControlDrawbackDashboard = function () {
        var data = payload();
        var controls = ['drawback-year', 'drawback-from', 'drawback-to', 'drawback-customer', 'drawback-status', 'drawback-transport'].map(function (id) { return document.getElementById(id); });
        data.months.forEach(function (month, index) { controls[1].add(new Option(month, index)); controls[2].add(new Option(month, index)); });
        controls[0].value = String(data.years[data.years.length - 1]);
        controls[1].value = '0';
        var lastMonth = data.rows.reduce(function (last, row) { return row.year === Number(controls[0].value) ? Math.max(last, row.month) : last; }, 0);
        controls[2].value = String(lastMonth);
        controls.forEach(function (control) { control.addEventListener('change', function () { refresh(data); }); });
        document.getElementById('drawback-reset').addEventListener('click', function () {
            controls[0].value = String(data.years[data.years.length - 1]); controls[1].value = '0'; controls[2].value = String(lastMonth);
            controls[3].value = '__all__'; controls[4].value = '__all__'; controls[5].value = '__all__'; refresh(data);
        });
        refresh(data);
    };
}());
