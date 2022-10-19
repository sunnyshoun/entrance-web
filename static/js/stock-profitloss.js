$(function(){
    showProfitloss();
    $('#btnRefresh').on('click', function() {showProfitloss(); });
});

function showProfitloss() {
    $.ajax({'type': 'GET', 'data': {}, 'url': '/stock/profitloss_list',
        beforeSend: function(){ $('#btnRefresh > span').removeClass('d-none'); },
    })
    .done(function(data) {
        var items = [];
        var classProfitLoss = '';
        var row = '';

        for(var tdate in data.profitloss) {
            row = data.profitloss[tdate];
            entAction = row.ent_action;
            classProfitLoss = row.difference > 0 ? 'profit' : 'loss';
            items.unshift(`
            <tr>
                <td>${row.stockid}</td>
                <td>${row.stitle}</td>
                <td>${row.plnum}</td>
                <td>${row.plcost}</td>
                <td>${row.plprice}</td>
                <td>${row.total_cost.currency()}</td>
                <td>${row.total_revenue.currency()}</td>
                <td class="texti-${classProfitLoss}">${row.difference.currency()}</td>
                <td class="texti-${classProfitLoss}">${row.roi}%</td>
                <td>${tdate}</td>
            </tr>`);
        }
        $('#tableProfitloss tbody').html(items.join(''));
    })
    .fail(function(jqXHR) { alertError(jqXHR.status); })
    .always(function(){ $('#btnRefresh > span').addClass('d-none'); });
}