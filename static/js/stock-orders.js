$(function(){
    showOrders();
    $('#btnRefresh').on('click', function() {showOrders(); });
});

function showOrders(formData) {
    $.ajax({'type': 'GET', 'data': formData, 'url': '/stock/orders_list',
        beforeSend: function(){ $('#btnRefresh > span').removeClass('d-none'); },
    })
    .done(function(data, textStatus, jqXHR) {
        var items = [];
        var actName = '';
        var entAction = '';
        var row = '';

        for(var tdate in data.orders) {
            row = data.orders[tdate];
            entAction = row.ent_action;
            actName = row.ent_action == 'buy' ? '現股買進' : '現股賣出';
            items.unshift(`
            <tr>
                <td>${row.stockid}</td>
                <td>${row.stitle}</td>
                <td class="texti-bold texti-${entAction}">${actName}</td>
                <td>${row.sprice}</td>
                <td>${row.ent_num}</td>
                <td class="texti-money-${entAction}">${row.amount.currency()}</td>
                <td>${tdate}</td>
            </tr>`);
        }
        $('#tableOrders tbody').html(items.join(''));
    })
    .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
    .always(function(){ $('#btnRefresh > span').addClass('d-none'); });
}