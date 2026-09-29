(function () {
    'use strict';

    var colors = ['#0b6b45', '#2185a3', '#7a4bc2', '#e08a1e'];
    var trendChart;
    var annualChart;

    function parsePayload() {
        return JSON.parse(document.getElementById('comparacion-data').textContent);
    }

    function selectedYears() {
        return Array.prototype.slice.call(document.querySelectorAll('#year-options input:checked'))
            .map(function (item) { return item.value; })
            .sort();
    }

    function metricValue(payload, year, metric, index) {
        return payload.descriptions[metric][year][index];
    }

    function getMetricMeta(metric) {
        var upper = metric.toUpperCase();
        var isDollars = upper.indexOf('DOLARES') !== -1;
        var isMoney = isDollars || /SOLES|INGRESO|GASTO|COSTO|PARTICIPACION|IMPUESTO/.test(upper);
        return {
            label: metric.toLowerCase().replace(/(^|\s)\S/g, function (letter) { return letter.toUpperCase(); }),
            decimals: isMoney ? 2 : 0,
            currency: isDollars ? 'USD' : isMoney ? 'PEN' : null,
            suffix: upper.indexOf('KILOS') !== -1 ? ' kg' : ''
        };
    }

    function sum(values) {
        return values.reduce(function (total, value) { return total + (value === null ? 0 : value); }, 0);
    }

    function hasData(payload, year, metric, indexes) {
        return indexes.some(function (index) { return metricValue(payload, year, metric, index) !== null; });
    }

    function niceTickStep(maxValue) {
        if (!maxValue || maxValue <= 75000) return 15000;
        var rawStep = maxValue / 6;
        var magnitude = Math.pow(10, Math.floor(Math.log(rawStep) / Math.LN10));
        var normalized = rawStep / magnitude;
        var niceNormalized = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10;
        return niceNormalized * magnitude;
    }

    function formatNumber(value, metric, compact) {
        if (value === null || typeof value === 'undefined' || isNaN(value)) return '—';
        var meta = getMetricMeta(metric);
        var options = { minimumFractionDigits: meta.decimals, maximumFractionDigits: meta.decimals };
        if (compact && Math.abs(value) >= 1000000) {
            return (meta.currency === 'PEN' ? 'S/ ' : meta.currency === 'USD' ? 'US$ ' : '') +
                (value / 1000000).toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' M';
        }
        var formatted = value.toLocaleString('es-PE', options);
        if (meta.currency === 'PEN') return 'S/ ' + formatted;
        if (meta.currency === 'USD') return 'US$ ' + formatted;
        return formatted + meta.suffix;
    }

    function percentChange(current, previous) {
        if (previous === 0 || previous === null) return null;
        return ((current - previous) / Math.abs(previous)) * 100;
    }

    function rangeIndexes() {
        var start = Number(document.getElementById('month-from').value);
        var end = Number(document.getElementById('month-to').value);
        if (start > end) {
            var swap = start; start = end; end = swap;
            document.getElementById('month-from').value = start;
            document.getElementById('month-to').value = end;
        }
        var indexes = [];
        for (var index = start; index <= end; index += 1) indexes.push(index);
        return indexes;
    }

    function buildCharts(payload, years, metric, indexes) {
        var labels = indexes.map(function (index) { return payload.months[index]; });
        var datasets = years.map(function (year, index) {
            return {
                label: year,
                data: indexes.map(function (monthIndex) { return metricValue(payload, year, metric, monthIndex); }),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length],
                borderWidth: 3,
                pointRadius: 3,
                pointHoverRadius: 5,
                fill: false,
                lineTension: 0.25,
                spanGaps: false
            };
        });
        var trendMax = Math.max.apply(null, datasets.reduce(function (all, dataset) {
            return all.concat(dataset.data.filter(function (value) { return value !== null; }).map(Math.abs));
        }, [0]));
        if (trendChart) trendChart.destroy();
        trendChart = new Chart(document.getElementById('monthly-trend-chart'), {
            type: 'line',
            data: { labels: labels, datasets: datasets },
            options: chartOptions(metric, false, niceTickStep(trendMax))
        });

        var totals = years.map(function (year) {
            return sum(indexes.map(function (monthIndex) { return metricValue(payload, year, metric, monthIndex); }));
        });
        var annualMax = Math.max.apply(null, totals.map(Math.abs).concat([0]));
        if (annualChart) annualChart.destroy();
        annualChart = new Chart(document.getElementById('annual-total-chart'), {
            type: 'bar',
            data: { labels: years, datasets: [{ data: totals, backgroundColor: years.map(function (_, index) { return colors[index % colors.length]; }), borderWidth: 0 }] },
            options: chartOptions(metric, true, niceTickStep(annualMax))
        });
    }

    function chartOptions(metric, hideLegend, tickStep) {
        return {
            maintainAspectRatio: false,
            responsive: true,
            legend: { display: !hideLegend, position: 'bottom', labels: { boxWidth: 12, padding: 18, fontColor: '#52606d' } },
            tooltips: { callbacks: { label: function (item, data) {
                var label = data.datasets[item.datasetIndex].label || getMetricMeta(metric).label;
                return label + ': ' + formatNumber(Number(item.yLabel), metric, false);
            } } },
            scales: {
                xAxes: [{ gridLines: { display: false }, ticks: { fontColor: '#71808d' } }],
                yAxes: [{ gridLines: { color: '#edf1f3', drawBorder: false }, ticks: { beginAtZero: true, fontColor: '#71808d', stepSize: tickStep, callback: function (value) { return formatNumber(Number(value), metric, true); } } }]
            }
        };
    }

    function updateKpis(payload, years, metric, indexes) {
        var latestYear = years[years.length - 1];
        var previousYear = years.length > 1 ? years[years.length - 2] : null;
        var latestValues = indexes.map(function (index) { return metricValue(payload, latestYear, metric, index); });
        var latestTotal = sum(latestValues);
        var availableValues = latestValues.filter(function (value) { return value !== null; });
        var previousTotal = previousYear ? sum(indexes.map(function (index) { return metricValue(payload, previousYear, metric, index); })) : null;
        var yoy = previousYear ? percentChange(latestTotal, previousTotal) : null;
        var best = { value: null, index: null };
        indexes.forEach(function (index) {
            var value = metricValue(payload, latestYear, metric, index);
            if (value !== null && (best.value === null || value > best.value)) best = { value: value, index: index };
        });

        document.getElementById('kpi-total').textContent = formatNumber(latestTotal, metric, true);
        document.getElementById('kpi-total-detail').textContent = latestYear + ' · ' + payload.months[indexes[0]] + ' a ' + payload.months[indexes[indexes.length - 1]];
        var yoyElement = document.getElementById('kpi-yoy');
        yoyElement.textContent = yoy === null ? '—' : (yoy >= 0 ? '+' : '') + yoy.toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
        yoyElement.className = 'kpi-value ' + (yoy === null ? '' : yoy >= 0 ? 'kpi-positive' : 'kpi-negative');
        document.getElementById('kpi-yoy-detail').textContent = previousYear ? latestYear + ' vs. ' + previousYear : 'Selecciona al menos dos años';
        document.getElementById('kpi-best').textContent = best.index === null ? '—' : payload.months[best.index] + ' ' + latestYear;
        document.getElementById('kpi-best-detail').textContent = formatNumber(best.value, metric, false);
        document.getElementById('kpi-average').textContent = availableValues.length ? formatNumber(latestTotal / availableValues.length, metric, true) : '—';
        document.getElementById('kpi-average-detail').textContent = availableValues.length + ' meses con información';
    }

    function updateTable(payload, years, metric, indexes) {
        var head = document.getElementById('comparison-table-head');
        var body = document.getElementById('comparison-table-body');
        head.innerHTML = '<th>Descripción</th><th>Año</th>' + indexes.map(function (index) {
            return '<th class="text-right">' + payload.months[index] + '</th>';
        }).join('') + '<th class="text-right">Total</th>';
        body.innerHTML = years.map(function (year) {
            var values = indexes.map(function (index) { return metricValue(payload, year, metric, index); });
            var total = values.some(function (value) { return value !== null; }) ? sum(values) : null;
            return '<tr><td class="font-weight-bold">' + getMetricMeta(metric).label + '</td>' +
                '<td><span class="badge badge-light">' + year + '</span></td>' +
                values.map(function (value) { return '<td class="text-right">' + formatNumber(value, metric, false) + '</td>'; }).join('') +
                '<td class="text-right font-weight-bold">' + formatNumber(total, metric, false) + '</td></tr>';
        }).join('');
    }

    function updateInsights(payload, years, metric, indexes) {
        var latest = years[years.length - 1];
        var previous = years.length > 1 ? years[years.length - 2] : null;
        var totals = years.map(function (year) { return { year: year, value: sum(indexes.map(function (index) { return metricValue(payload, year, metric, index); })) }; });
        var leader = totals.reduce(function (best, current) { return current.value > best.value ? current : best; }, totals[0]);
        var latestTotal = totals[totals.length - 1].value;
        var previousTotal = previous ? totals[totals.length - 2].value : null;
        var yoy = previous ? percentChange(latestTotal, previousTotal) : null;
        var validMonths = indexes.filter(function (index) { return metricValue(payload, latest, metric, index) !== null; });
        var insights = [
            '<strong>' + leader.year + '</strong> registra el mayor acumulado: ' + formatNumber(leader.value, metric, false) + '.',
            yoy === null ? 'Selecciona dos o más años para calcular la variación interanual.' : 'El acumulado de <strong>' + latest + '</strong> ' + (yoy >= 0 ? 'aumenta' : 'disminuye') + ' <strong>' + Math.abs(yoy).toLocaleString('es-PE', { maximumFractionDigits: 1 }) + '%</strong> frente a ' + previous + '.',
            latest + ' tiene información disponible en <strong>' + validMonths.length + '</strong> de los ' + indexes.length + ' meses seleccionados.'
        ];
        document.getElementById('executive-insights').innerHTML = insights.map(function (text) { return '<li>' + text + '</li>'; }).join('');
    }

    function refresh(payload) {
        var years = selectedYears();
        if (!years.length) {
            var first = document.querySelector('#year-options input'); first.checked = true; years = [first.value];
        }
        var metric = document.getElementById('metric-filter').value;
        var indexes = rangeIndexes();
        var dataYears = years.filter(function (year) { return hasData(payload, year, metric, indexes); });
        document.getElementById('trend-subtitle').textContent = getMetricMeta(metric).label + ' · ' + payload.months[indexes[0]] + ' a ' + payload.months[indexes[indexes.length - 1]];
        updateKpis(payload, dataYears, metric, indexes);
        buildCharts(payload, dataYears, metric, indexes);
        updateTable(payload, years, metric, indexes);
        updateInsights(payload, dataYears, metric, indexes);
    }

    window.initComparacionDashboard = function () {
        var payload = parsePayload();
        var from = document.getElementById('month-from');
        var to = document.getElementById('month-to');
        payload.months.forEach(function (month, index) {
            from.add(new Option(month, index));
            to.add(new Option(month, index));
        });
        var firstDescription = Object.keys(payload.descriptions)[0];
        var latestData = payload.descriptions[firstDescription]['2026'];
        var latestMonth = latestData.reduce(function (last, value, index) { return value === null ? last : index; }, 0);
        from.value = 0;
        to.value = latestMonth;
        document.querySelectorAll('#year-options input, #metric-filter, #month-from, #month-to').forEach(function (control) {
            control.addEventListener('change', function () { refresh(payload); });
        });
        document.getElementById('reset-comparison').addEventListener('click', function () {
            document.querySelectorAll('#year-options input').forEach(function (item) { item.checked = true; });
            document.getElementById('metric-filter').value = firstDescription;
            from.value = 0; to.value = latestMonth;
            refresh(payload);
        });
        refresh(payload);
    };
}());
