$(function(){
    showPassbook();
    getInventory();
    $('#btnRefresh').on('click', function() {showPassbook(); });
});

function getInventory(formData) {
    $.ajax({'type': 'GET', 'data': formData, 'url': '/stock/inventory_list',
        beforeSend: function(){ $('#processing').removeClass('d-none'); },
    })
    .done(function(data, textStatus, jqXHR) {
        var colors = [
            '#b91d1d', '#4169e1', '#c71585', '#008b8b', '#ff8c00',
            '#4682b4', '#ba55d3', '#ff1493', '#2e8b57', '#3b3b3b'
        ];
        var colorIndex = 0;
        var items = [];
        var aryChartData = [];
        var aryColData = [];
        var aryTableData = [];
        var aryColors = [];
        var row = '';
        var svalue = '';
        for(var stock in data.inventory) {
            row = data.inventory[stock];
            // 單位：萬元
            svalue = parseInt(parseFloat(row.sprice) * parseInt(row.inv_num)) / 10.0;
            aryChartData.push([row.name, svalue]);
            aryColData.push([row.name, parseFloat(row.roi.slice(0, -1)), row.roi]);
            aryTableData.push([row.name, svalue, row.roi]);
            // 設定顏色
            aryColors.push(colors[colorIndex]);
            colorIndex++;
            if (colorIndex == colors.length) {
                colorIndex -= 1;
            }
        }
        aryChartData.sort(function(a, b) { return b[1] - a[1]; });
        aryColData.sort(function(a, b) { return b[1] - a[1]; });
        aryTableData.sort(function(a, b) { return b[1] - a[1]; });

        aryTableData.forEach(function(row, index) {
            row.unshift(aryColors[index]);
            items.push(`
            <tr>
                <td><span style="color:${row[0]};">●</td>
                <td>${row[1]}</td>
                <td>${row[2]}萬</td>
                <td>${row[3]}</td>
            </tr>`);
        });
        $('#tableAssets tbody').html(items.join(''));
        drawPieChart(aryChartData, aryColors);
        drawColChart(aryColData)
        // 不要在 #assets-stat 設定 d-none 樣式
        // 而是設定 style="display: none;"
        // 圖表淡出效果才有作用
        $('#assets-stat').fadeIn(2000);
        if (aryTableData.length == 0) {
            toastr.info('目前沒有任何資產');
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
    .always(function(){ $('#processing').addClass('d-none'); });
}

function drawPieChart(aryChartData, aryColors) {
    // 圓餅圖
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawChart);

    function drawChart() {
        // 新增欄位
        aryChartData.unshift(['公司', '佔比']);
        var data = google.visualization.arrayToDataTable(aryChartData);
        var options = {
            // title: '資產總覽',
            colors: aryColors,
            legend: {position: 'top', textStyle: {color: 'black', fontSize: 14}},
            tooltip: {textStyle: {color: 'gray', fontSize: 16}, showColorCode: true},
            is3D: true
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
        chart.draw(data, options);
        // 移除欄位，否則影響長條圖
        aryChartData.shift();
    }
}

function drawColChart(aryChartData) {
    google.charts.load("current", {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
        aryChartData.unshift(['公司', '報酬率', { role: 'annotation' } ]);
        var data = google.visualization.arrayToDataTable(aryChartData);

        var view = new google.visualization.DataView(data);
        view.setColumns([0, 1, 2]);

        var options = {
            title: "各股票報酬率 (%)",
            legend: {position: 'top', textStyle: {color: 'black', fontSize: 14}},
            tooltip: {textStyle: {color: 'gray', fontSize: 16}, showColorCode: true},
            annotations: {textStyle: {fontSize: 14, color: '#871b47'}},
            hAxis: {textStyle: { fontSize: 16 }, titleTextStyle: { fontSize: 16 }},
            vAxis: {textStyle: { fontSize: 16 }, titleTextStyle: { fontSize: 16 }},
            titleTextStyle: { fontSize: 16 },
            bar: {groupWidth: "30%"},
        };
        var chart = new google.visualization.ColumnChart(document.getElementById("colchart"));
        chart.draw(view, options);
    }
}

function showPassbook(formData) {
    $.ajax({'type': 'GET', 'data': formData, 'url': '/stock/passbook',
        beforeSend: function(){ $('#btnRefresh > span').removeClass('d-none'); },
    })
    .done(function(data, textStatus, jqXHR) {
        var items = [];
        var row = '';
        for(var key in data.passbook) {
            row = data.passbook[key];
            items.push(`
            <tr>
                <td>${row.date}</td>
                <td>${row.memo}</td>
                <td>${row.withdrawal.currency()}</td>
                <td>${row.deposit.currency()}</td>
                <td>${row.balance.currency()}</td>
                <td>${row.remarks}</td>
            </tr>`);
        }
        $('#tablePassbook tbody').html(items.join(''));
    })
    .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
    .always(function(){ $('#btnRefresh > span').addClass('d-none'); });
}