$(function(){
    listStocks();

    $('#btnSave').on('click', function() {
        var formData = {
            'txtStockID': $('#txtStockID').val(),
            'txtName': $('#txtName').val(),
            'txtFullname': $('#txtFullname').val(),
            'txtStockEx': $('#txtStockEx').val(),
            'selCurrency': $('#selCurrency').val(),
            'act': 'Save'
        };
        saveStocks(formData);
    });

    $('#btnList').on('click', function() {
        listStocks();
    });

    $('#selAmount').change(function() {
        $('txtInitBalance').val(this.value);
    });

    $('#btnSetInitBalance').on('click', function() {
        setInitBalance();
    });
});

function listStocks() {
    var formData = {
        'act': 'List'
    };
    saveStocks(formData);
}

function saveStocks(formData) {
    $.ajax({'type': 'POST', 'data': formData, 'url': '/stock_stocks_save',
        beforeSend: function(){ $('#btnList > span').removeClass('d-none');},
    })
    .done(function(data, textStatus, jqXHR) {
        var stocks = data.main_stocks;
        var tblBody = '';
        var btnEdit = '';
        var btnDrop = '';
        var items = [];

        $.each(stocks, function(index, row) {
            btnEdit = `<span class="btn btn-sm btn-success" onclick="editStock('${index}')">編輯</span>`;
            btnDrop = `<span class="btn btn-sm btn-danger" onclick="dropStock('${index}')">刪除</span>`;
            items.push(`
            <tr id="rowid-${index}">
                <td>${row.stockid}</td>
                <td><a href="https:www.google.com/finance/quote/${row.stockex}" target="_blank">${row.stockex}</a></td>
                <td>${row.currency}</td>
                <td>${row.name}</td>
                <td>${row.fullname}</td>
                <td>${btnEdit}&nbsp;&nbsp;${btnDrop}</td>
            </tr>`);
        });
        $('#tableStocks tbody').html(items.join(''));
    })
    .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
    .always(function(){ $('#btnList > span').addClass('d-none'); });
}

function editStock(rowIndex) {
    var rowID = '#rowid-'+rowIndex;
    $('#txtStockID').val($(rowID+' td:first').text());
    $('#txtStockEx').val($(rowID+' td:nth-child(2)').text());
    $('#selCurrency').val($(rowID+' td:nth-child(3)').text());
    $('#txtName').val($(rowID+' td:nth-child(4)').text());
    $('#txtFullname').val($(rowID+' td:nth-child(5)').text());
}

function dropStock(rowIndex) {
    var rowID = '#rowid-'+rowIndex;
    var formData = {
        'txtStockID': $(rowID+' td:first').text(),
        'act': 'Drop'
    };
    saveStocks(formData);
}

function setInitBalance() {
    var formData = {
        'txtInitBalance': $('#txtInitBalance').val(),
    };

    $.ajax({'type': 'POST', 'data': formData, 'url':'/stock_set_init_balance',
        beforeSend: function(){ $('#btnList > span').removeClass('d-none'); },
    })
    .done(function(data, textStatus, jqXHR) {
        toastr.success('開戶金額設定成功');
    })
    .fail(function(jqXHR, textStatus, errorThrown) { alertError(jqXHR.status); })
    .always(function(){ $('#btnList > span').addClass('d-none'); });
}