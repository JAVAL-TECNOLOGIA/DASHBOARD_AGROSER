(function () {
    'use strict';
    function money(value, compact) {
        value = Number(value || 0);
        if (compact && Math.abs(value) >= 1000000) return (value < 0 ? '-S/ ' : 'S/ ') + (Math.abs(value) / 1000000).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' M';
        if (compact && Math.abs(value) >= 1000) return (value < 0 ? '-S/ ' : 'S/ ') + (Math.abs(value) / 1000).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' mil';
        return (value < 0 ? '-S/ ' : 'S/ ') + Math.abs(value).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
    function rows(items) {
        return items.map(function (item) { return '<tr><td><span class="cash-account">' + item.account + '</span></td><td>' + item.label + '</td><td class="text-right font-weight-bold">' + money(item.amount, false) + '</td></tr>'; }).join('');
    }
    window.initLiquidacionCajaDashboard = function () {
        var data = JSON.parse(document.getElementById('liquidacion-caja-data').textContent);
        document.getElementById('cash-cash-total').textContent = money(data.cash_total, true);
        document.getElementById('cash-receivable-total').textContent = money(data.receivable_total, true);
        document.getElementById('cash-payable-total').textContent = money(data.payable_total, true);
        var net = document.getElementById('cash-net-total'); net.textContent = money(data.net_position, true); net.className = 'cash-kpi-value ' + (data.net_position >= 0 ? 'cash-positive' : 'cash-negative');
        document.getElementById('cash-coverage').textContent = Number(data.coverage).toLocaleString('es-PE', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
        document.getElementById('cash-receivable-body').innerHTML = rows([{account:'10', label:'Efectivo y Equivalente de Efectivo', amount:data.cash_total}].concat(data.receivables));
        document.getElementById('cash-payable-body').innerHTML = rows(data.payables);
        document.getElementById('cash-receivable-footer').textContent = money(data.available_total, false);
        document.getElementById('cash-payable-footer').textContent = money(data.payable_total, false);
        new Chart(document.getElementById('cash-position-chart'), {type:'bar',data:{labels:['Efectivo','Por cobrar','Por pagar'],datasets:[{data:[data.cash_total,data.receivable_total,data.payable_total],backgroundColor:['#0d6b45','#126e82','#d98212'],barPercentage:.55}]},options:{maintainAspectRatio:false,responsive:true,legend:{display:false},tooltips:{callbacks:{label:function(item){return money(item.yLabel,false);}}},scales:{xAxes:[{gridLines:{display:false}}],yAxes:[{ticks:{beginAtZero:true,callback:function(value){return money(value,true);}},gridLines:{color:'#edf1f3'}}]}}});
        var payableItems = data.payables.filter(function(item){return Number(item.amount)>0;});
        new Chart(document.getElementById('cash-payables-chart'), {type:'doughnut',data:{labels:payableItems.map(function(item){return item.label;}),datasets:[{data:payableItems.map(function(item){return item.amount;}),backgroundColor:['#0d6b45','#278ba8','#7654c6','#d98212','#b7442b','#476c8c','#9b7b4f']}]},options:{maintainAspectRatio:false,responsive:true,cutoutPercentage:60,legend:{position:'bottom',labels:{boxWidth:10,fontSize:9,padding:10}},tooltips:{callbacks:{label:function(item,chart){return chart.labels[item.index]+': '+money(chart.datasets[0].data[item.index],false);}}}}});
    };
}());
