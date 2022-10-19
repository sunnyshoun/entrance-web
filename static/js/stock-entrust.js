$(function(){
    showInventory();
    $('#btnRefresh').on('click', function() { showInventory(); });
    $('#selStock').change(function() { fetchPrice(); });
    $('#btnFetch').on('click', function() { fetchPrice(); });
    $('#btnEntrust').on('click', function() { entrustOrder(); });
    $('input[name="radOption"]').on('change', function() {
        clearEstimation();
        estimateMoney();
        if (this.value == 'sell') {
            showInventory();
        }
    });
    $('#txtLots').on('input', function (e) {
        estimateMoney();
    });
});

function fetchPrice() {
    var stockID = $('#selStock').val();
    $('#stitle').text('');
    $('#sprice').text('');
    $('#spercent').text('');
    clearEstimation();

    if (stockID != null) {
        $.ajax({'type': 'GET', 'url': '/stock/price/'+stockID,
            beforeSend: function(){ $('#btnFetch > span').removeClass('d-none'); },
        })
        .done(function(data, textStatus, jqXHR) {
            if (data.result[0] == true) {
                var row = data.result[1]
                $('#stitle').html(row.stitle);
                $('#sprice').html(row.sprice);
                $('#spercent').removeClass();
                if (row.spercent > 0) {
                    $('#spercent').html('&#9650;'+row.spercent+'%').addClass("text-danger");
                }
                else if (row.spercent < 0) {
                    $('#spercent').html('&#9660;'+row.spercent.slice(1)+'%').addClass("text-success");
                }
                else {
                    $('#spercent').html(row.spercent+'%').addClass("text-dark");
                }
                
                $('#balance').html(data.balance.currency());
                estimateMoney();
            }
            else {
                toastr.error(data.result[1]);
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
        .always(function(){ $('#btnFetch > span').addClass('d-none'); });
    }
    else {
        toastr.warning('請選取股票代碼', '查詢錯誤');
    }
}

function estimateMoney() {
    var estOption = '';
    var estMoney = 0;
    var entNum = parseInt($('#txtLots').val());
    var entAction = $('input[name="radOption"]:checked').val();

    if (isNaN(entNum)) {
        entNum = 1;
        $('#txtLots').val(entNum);
    }

    estMoney = 1000 * entNum * Number($('#sprice').text().replaceAll(',', '').slice(1));
    if (entAction == 'buy') {
        estOption = "買入預計付款 -";
    }
    else if (entAction == 'sell') {
        estOption = "賣出預計收款 +";
    }
    $('#estOption').text(estOption);
    $('#estMoney').text(estMoney.currency());
}

function clearEstimation() {
    $('#estOption').text('');
    $('#estMoney').text('');
}

function entrustOrder() {
    var stockID = $('#selStock').val();
    var entNum = parseInt($('#txtLots').val());
    var entAction = $('input[name="radOption"]:checked').val();

    if (isNaN(entNum)) {
        entNum = 1;
        $('#txtLots').val(entNum);
    }

    var formData = {
        'stockID': stockID,
        'entNum': entNum,
        'entAction': entAction,
    };

    $.ajax({'type': 'POST', 'data': formData, 'url': '/stock/entrust_order',
        beforeSend: function(){ $('#btnEntrust > span').removeClass('d-none'); },
    })
    .done(function(data, textStatus, jqXHR) {
        if(data.result == true) {
            toastr.success(data.msg);
            fetchPrice();
            showInventory();
        }
        else if (data.result == false) {
            toastr.error(data.msg);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
    .always(function(){ $('#btnEntrust > span').addClass('d-none'); });
}

function showInventory(formData) {
    $.ajax({'type': 'GET', 'data': formData, 'url': '/stock/inventory_list',
        beforeSend: function(){ $('#btnRefresh > span').removeClass('d-none'); },
    })
    .done(function(data, textStatus, jqXHR) {
        var items = [];
        var row;
        for(var stockid in data.inventory) {
            row = data.inventory[stockid];
            items.push(`
            <tr>
                <td>${stockid}</td>
                <td><a href="https://www.google.com/finance/quote/${row.stockex}" target="_blank">${row.name}</a></td>
                <td>${row.inv_num}</td>
                <td>${row.mcost}</td>
                <td>${row.sprice}</td>
                <td>${row.profitloss}</td>
                <td>${row.roi}</td>
            </tr>`);
        }
        $('#tableInventory tbody').html(items.join(''));
    })
    .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
    .always(function(){ $('#btnRefresh > span').addClass('d-none'); });
}