(function () {
    'use strict';

    function money(value, compact) {
        if (compact && Math.abs(value) >= 1000000) return (value < 0 ? '-S/ ' : 'S/ ') + (Math.abs(value) / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' M';
        if (compact && Math.abs(value) >= 1000) return (value < 0 ? '-S/ ' : 'S/ ') + (Math.abs(value) / 1000).toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mil';
        return (value < 0 ? '-S/ ' : 'S/ ') + Math.abs(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    function sum(items) { return items.reduce(function (total, item) { return total + item.amount; }, 0); }
    function niceStep(maxValue) { var raw = maxValue / 6; var magnitude = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)); var normalized = raw / magnitude; return (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude; }

    window.initBalanceGeneralDashboard = function () {
        var data = JSON.parse(document.getElementById('balance-data').textContent);
        var assets = data.items.filter(function (item) { return item.group === 'activo'; });
        var obligations = data.items.filter(function (item) { return item.group === 'obligacion'; });
        var assetTotal = sum(assets); var obligationTotal = sum(obligations); var net = assetTotal - obligationTotal; var coverage = obligationTotal ? assetTotal / obligationTotal : null;
        document.getElementById('balance-assets').textContent = money(assetTotal, true);
        document.getElementById('balance-obligations').textContent = money(obligationTotal, true);
        document.getElementById('balance-coverage').textContent = coverage === null ? '—' : (coverage * 100).toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
        var netElement = document.getElementById('balance-net'); netElement.textContent = money(net, true); netElement.className = 'balance-kpi-value ' + (net >= 0 ? 'balance-positive' : 'balance-negative');
        document.getElementById('balance-detail-net').textContent = money(net, false);

        var max = Math.max(assetTotal, obligationTotal);
        new Chart(document.getElementById('balance-position-chart'), {
            type: 'bar', data: { labels: ['Activos líquidos', 'Obligaciones'], datasets: [{ data: [assetTotal, obligationTotal], backgroundColor: ['#0b6b45', '#e58a13'] }] },
            options: { maintainAspectRatio: false, responsive: true, legend: { display: false }, tooltips: { callbacks: { label: function (item) { return money(Number(item.yLabel), false); } } }, scales: { xAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#61717e' } }], yAxes: [{ gridLines: { color: '#edf1f3', drawBorder: false }, ticks: { beginAtZero: true, stepSize: niceStep(max), fontColor: '#71808d', callback: function (value) { return money(Number(value), true); } } }] } }
        });
        new Chart(document.getElementById('balance-composition-chart'), {
            type: 'doughnut', data: { labels: data.items.map(function (item) { return item.label; }), datasets: [{ data: data.items.map(function (item) { return item.amount; }), backgroundColor: ['#0b6b45', '#278ba8', '#e58a13', '#b7442b'] }] },
            options: { maintainAspectRatio: false, responsive: true, cutoutPercentage: 62, legend: { position: 'bottom', labels: { boxWidth: 11, padding: 13, fontSize: 10 } }, tooltips: { callbacks: { label: function (item, chart) { return chart.labels[item.index] + ': ' + money(Number(chart.datasets[0].data[item.index]), false); } } } }
        });

        document.getElementById('balance-detail-body').innerHTML = data.items.map(function (item) {
            var groupTotal = item.group === 'activo' ? assetTotal : obligationTotal; var participation = groupTotal ? item.amount / groupTotal * 100 : 0;
            return '<tr><td class="font-weight-bold">' + item.label + '</td><td><span class="balance-badge balance-badge-' + (item.group === 'activo' ? 'asset' : 'obligation') + '">' + (item.group === 'activo' ? 'Activo líquido' : 'Obligación') + '</span></td><td class="text-right">' + money(item.amount, false) + '</td><td class="text-right">' + participation.toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%</td></tr>';
        }).join('');

        var gap = obligationTotal - assetTotal; var payables = data.items.filter(function (item) { return item.key === 'cuentas_por_pagar'; })[0]; var receivables = data.items.filter(function (item) { return item.key === 'cuentas_por_cobrar'; })[0];
        var insights = [
            coverage >= 1 ? 'Los activos líquidos cubren el <strong>' + (coverage * 100).toLocaleString('es-PE', { maximumFractionDigits: 1 }) + '%</strong> de las obligaciones.' : 'Los activos líquidos cubren el <strong>' + (coverage * 100).toLocaleString('es-PE', { maximumFractionDigits: 1 }) + '%</strong> de las obligaciones; existe una brecha de <strong>' + money(gap, false) + '</strong>.',
            'Las cuentas por pagar concentran el <strong>' + (payables.amount / obligationTotal * 100).toLocaleString('es-PE', { maximumFractionDigits: 1 }) + '%</strong> de las obligaciones.',
            'Las cuentas por cobrar representan el <strong>' + (receivables.amount / assetTotal * 100).toLocaleString('es-PE', { maximumFractionDigits: 1 }) + '%</strong> de los activos líquidos.',
            net < 0 ? 'La posición neta de agosto es negativa. Conviene priorizar cobranza y programación de pagos.' : 'La posición neta de agosto es positiva y cubre las obligaciones registradas.'
        ];
        document.getElementById('balance-insights').innerHTML = insights.map(function (text) { return '<li>' + text + '</li>'; }).join('');
    };
}());
