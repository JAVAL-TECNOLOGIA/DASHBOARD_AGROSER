(function () {
    'use strict';

    var chart = null;

    function payload() {
        return JSON.parse(document.getElementById('ventas-exportacion-data').textContent);
    }

    function money(value, currency) {
        return new Intl.NumberFormat('es-PE', {
            style: 'currency', currency: currency || 'PEN', minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(Number(value || 0));
    }

    function number(value, digits) {
        return Number(value || 0).toLocaleString('es-PE', {
            minimumFractionDigits: digits || 0, maximumFractionDigits: digits || 0
        });
    }

    function dateLabel(value) {
        if (!value) return '';
        var parts = value.split('-');
        return parts[2] + '/' + parts[1] + '/' + parts[0];
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>'"]/g, function (character) {
            return {'&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'}[character];
        });
    }

    function selectedState(data) {
        return {
            year: Number(document.getElementById('export-year').value),
            from: Number(document.getElementById('export-from').value),
            to: Number(document.getElementById('export-to').value),
            customer: document.getElementById('export-customer').value
        };
    }

    function activeRows(items, state) {
        return items.filter(function (item) {
            return item.year === state.year && item.month >= state.from && item.month <= state.to;
        });
    }

    function refreshSummary(data, state) {
        var rows = activeRows(data.summary, state);
        var total = function (field) {
            return rows.reduce(function (sum, row) { return sum + Number(row[field] || 0); }, 0);
        };
        document.getElementById('export-with-sales').textContent = money(total('sales_with_export'));
        document.getElementById('export-without-sales').textContent = money(total('sales_without_export'));
        document.getElementById('export-sales-total').textContent = money(total('export_sales'));
        document.getElementById('export-cost-total').textContent = money(total('export_cost'));
        document.getElementById('export-tax-payable').textContent = money(total('igv_difference_with_export'));
        document.getElementById('export-income-tax').textContent = money(total('income_tax_with_export'));
        document.getElementById('export-drawback').textContent = money(total('drawback'));
        document.getElementById('export-scenario-difference').textContent = money(
            total('igv_scenario_difference') + total('income_tax_difference') + total('drawback_difference')
        );
        document.getElementById('export-period-label').textContent = state.year + ' · ' + data.months[state.from] + ' a ' + data.months[state.to];
        document.getElementById('export-chart-subtitle').textContent = state.year + ' · ' + data.months[state.from] + ' a ' + data.months[state.to];

        document.getElementById('export-with-body').innerHTML = rows.map(function (row) {
            var month = escapeHtml(data.months[row.month].slice(0, 3) + '-' + String(row.year).slice(-2));
            return '<tr><td>' + month + '</td><td><strong>VENTAS</strong></td>' +
                '<td class="amount">' + money(row.affected_sales) + '</td><td class="amount">' + money(row.sales_tax) + '</td>' +
                '<td class="amount">' + money(row.export_sales) + '</td><td class="amount">' + money(row.exempt_sales) + '</td><td class="amount">—</td>' +
                '<td class="amount"><strong>' + money(row.sales_total_with_export) + '</strong></td><td class="amount">' + money(row.sales_tax) + '</td>' +
                '<td class="amount">' + money(row.income_tax_with_export) + '</td><td class="amount">' + money(row.drawback) + '</td>' +
                '<td class="amount">—</td><td class="amount">—</td><td class="amount">—</td></tr>' +
                '<tr><td>' + month + '</td><td><strong>COMPRAS</strong></td>' +
                '<td class="amount">' + money(row.purchases_without_export) + '</td><td class="amount">' + money(row.purchase_tax_without_export) + '</td>' +
                '<td class="amount">—</td><td class="amount">' + money(row.purchases_non_taxed) + '</td><td class="amount">' + money(row.export_cost) + '</td>' +
                '<td class="amount"><strong>' + money(row.purchases_total_with_export) + '</strong></td><td class="amount">' + money(row.purchase_tax) + '</td>' +
                '<td class="amount">—</td><td class="amount">—</td><td class="amount">' + money(row.igv_difference_with_export) + '</td>' +
                '<td class="amount">' + money(row.income_tax_with_export) + '</td><td class="amount">' + money(row.drawback) + '</td></tr>';
        }).join('');
        document.getElementById('export-without-body').innerHTML = rows.map(function (row) {
            var month = escapeHtml(data.months[row.month].slice(0, 3) + '-' + String(row.year).slice(-2));
            return '<tr><td>' + month + '</td><td><strong>VENTAS</strong></td>' +
                '<td class="amount">' + money(row.affected_sales) + '</td><td class="amount">' + money(row.sales_tax) + '</td>' +
                '<td class="amount">—</td><td class="amount">' + money(row.exempt_sales) + '</td><td class="amount">—</td>' +
                '<td class="amount"><strong>' + money(row.sales_total_without_export) + '</strong></td><td class="amount">' + money(row.sales_tax) + '</td>' +
                '<td class="amount">' + money(row.income_tax_without_export) + '</td><td class="amount">—</td>' +
                '<td class="amount">—</td><td class="amount">—</td><td class="amount">—</td></tr>' +
                '<tr><td>' + month + '</td><td><strong>COMPRAS</strong></td>' +
                '<td class="amount">' + money(row.purchases_without_export) + '</td><td class="amount">' + money(row.purchase_tax_without_export) + '</td>' +
                '<td class="amount">—</td><td class="amount">' + money(row.purchases_non_taxed_without_export) + '</td><td class="amount">—</td>' +
                '<td class="amount"><strong>' + money(row.purchases_total_without_export) + '</strong></td><td class="amount">' + money(row.purchase_tax_without_export) + '</td>' +
                '<td class="amount">—</td><td class="amount">—</td><td class="amount">' + money(row.igv_difference_without_export) + '</td>' +
                '<td class="amount">' + money(row.income_tax_without_export) + '</td><td class="amount">—</td></tr>';
        }).join('');
        document.getElementById('export-with-foot').innerHTML = '<tr class="font-weight-bold"><td colspan="11" class="text-right">TOTAL DIFERENCIA</td><td class="amount">' + money(total('igv_difference_with_export')) + '</td><td class="amount">' + money(total('income_tax_with_export')) + '</td><td class="amount">' + money(total('drawback')) + '</td></tr>';
        document.getElementById('export-without-foot').innerHTML = '<tr class="font-weight-bold"><td colspan="11" class="text-right">TOTAL DIFERENCIA</td><td class="amount">' + money(total('igv_difference_without_export')) + '</td><td class="amount">' + money(total('income_tax_without_export')) + '</td><td class="amount">S/ 0.00</td></tr>' +
            '<tr class="font-weight-bold" style="background:#eef8f4"><td colspan="11" class="text-right">DIFERENCIA ENTRE ESCENARIOS</td><td class="amount">' + money(total('igv_scenario_difference')) + '</td><td class="amount">' + money(total('income_tax_difference')) + '</td><td class="amount">' + money(total('drawback_difference')) + '</td></tr>';

        if (chart) chart.destroy();
        chart = new Chart(document.getElementById('export-comparison-chart'), {
            type: 'bar',
            data: {
                labels: rows.map(function (row) { return data.months[row.month]; }),
                datasets: [
                    {label: 'Con exportación', data: rows.map(function (row) { return row.sales_with_export; }), backgroundColor: '#0f766e'},
                    {label: 'Sin exportación', data: rows.map(function (row) { return row.sales_without_export; }), backgroundColor: '#2f8faa'},
                    {label: 'Costo de exportación', data: rows.map(function (row) { return row.export_cost; }), backgroundColor: '#e78a0a'}
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                tooltips: {callbacks: {label: function (item, chartData) {
                    return chartData.datasets[item.datasetIndex].label + ': ' + money(item.yLabel);
                }}},
                scales: {yAxes: [{ticks: {beginAtZero: true, callback: function (value) { return money(value); }}}]}
            }
        });
    }

    function refreshInvoices(data, state) {
        var rows = activeRows(data.invoices, state).filter(function (item) {
            return state.customer === '__all__' || item.customer === state.customer;
        });
        document.getElementById('export-invoice-body').innerHTML = rows.length ? rows.map(function (item) {
            return '<tr><td>' + dateLabel(item.date) + '</td><td>' + escapeHtml(item.document_type) + '</td>' +
                '<td><strong>' + escapeHtml(item.document) + '</strong></td><td>' + escapeHtml(item.customer) + '</td>' +
                '<td class="amount">' + money(item.exported) + '</td><td>' + escapeHtml(item.currency) + '</td>' +
                '<td class="amount">' + number(item.exchange_rate, 4) + '</td><td class="amount">' + money(item.total_usd, 'USD') + '</td>' +
                '<td class="amount">' + money(item.total_pen) + '</td></tr>';
        }).join('') : '<tr><td colspan="9" class="text-center text-muted py-5">No hay facturas de exportación para los filtros seleccionados.</td></tr>';
    }

    function refreshPurchases(data, state) {
        var rows = activeRows(data.purchases, state);
        document.getElementById('export-purchase-body').innerHTML = rows.length ? rows.map(function (item) {
            return '<tr><td>' + dateLabel(item.date) + '</td><td>' + escapeHtml(item.document_type) + '</td>' +
                '<td><strong>' + escapeHtml(item.document) + '</strong></td><td>' + escapeHtml(item.tax_id) + '</td>' +
                '<td>' + escapeHtml(item.supplier) + '</td><td class="amount">' + money(item.base) + '</td>' +
                '<td class="amount">' + money(item.tax) + '</td><td class="amount">' + money(item.total) + '</td>' +
                '<td>' + escapeHtml(item.currency) + '</td><td style="min-width:280px">' + escapeHtml(item.detail) + '</td></tr>';
        }).join('') : '<tr><td colspan="10" class="text-center text-muted py-5">No hay compras vinculadas para los filtros seleccionados.</td></tr>';
    }

    function refresh(data) {
        var state = selectedState(data);
        if (state.from > state.to) {
            document.getElementById('export-to').value = state.from;
            state.to = state.from;
        }
        refreshSummary(data, state);
        refreshInvoices(data, state);
        refreshPurchases(data, state);
    }

    window.initVentasExportacionDashboard = function () {
        var data = payload();
        var year = document.getElementById('export-year');
        var from = document.getElementById('export-from');
        var to = document.getElementById('export-to');
        var customer = document.getElementById('export-customer');
        data.months.forEach(function (month, index) {
            from.add(new Option(month, index));
            to.add(new Option(month, index));
        });
        year.value = String(data.years[data.years.length - 1]);
        from.value = '0';
        var lastMonth = 0;
        data.summary.forEach(function (row) {
            if (row.year === Number(year.value) && (row.sales_with_export || row.purchases_with_export)) lastMonth = Math.max(lastMonth, row.month);
        });
        to.value = String(lastMonth);
        [year, from, to, customer].forEach(function (control) {
            control.addEventListener('change', function () { refresh(data); });
        });
        document.getElementById('export-reset').addEventListener('click', function () {
            year.value = String(data.years[data.years.length - 1]);
            from.value = '0';
            to.value = String(lastMonth);
            customer.value = '__all__';
            refresh(data);
        });
        refresh(data);
    };
}());
