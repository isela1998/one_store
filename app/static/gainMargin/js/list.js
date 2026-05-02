var tbGainMargin;
var modal_title;

function getData() {

    $('#i_card_title').removeClass().addClass('text-dark fas fa-boxes')
    $('#i_card_title2').removeClass().addClass('text-dark fas fa-th-list')

    tbGainMargin = $('#data').DataTable({
        ordering: true,
        searching: true,
        paging: true,
        info: false,
        pagingType: 'simple_numbers',
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: ""
        },
        columns: [
            { "data": "code" },
            { "data": "category.name" },
            { "data": "brand" },
            { "data": "product" },
            { "data": "cost" },
            { "data": "quantity" },
            { "data": "price_dl" },
            { "data": "gain" },
        ],
        dom: '<"myCustomClass"f>rt<"bottom"lp><"clear">',
        fnDrawCallback: function () {
            $("input[type='search']").attr("id", "searchBox");
            $("input[type='search']").attr("autocomplete", "off");
            $("select[name='data_length'], #searchBox").removeClass("input-sm");
            $('#searchBox').css("width", "350px").focus();
            $('#data').removeClass('dataTables_filter');

            // Calculo de ganancias totales
            var api = this.api();

            var totalInversion = api.rows({ search: 'applied' }).data().toArray().reduce(function (total, row) {
                let qty = parseFloat(row.quantity) || 0;
                let cost = parseFloat(row.cost) || 0;
                return total + (qty * cost);
            }, 0);

            var totalGain = api.column(7, { search: 'applied' }).data().reduce(function (a, b) {
                var x = parseFloat(a) || 0;
                var y = parseFloat(b) || 0;
                return x + y;
            }, 0);

            var totalVenta = api.rows({ search: 'applied' }).data().toArray().reduce(function (total, row) {
                let qty = parseFloat(row.quantity) || 0;
                let price_dl = parseFloat(row.price_dl) || 0;
                return total + (qty * price_dl);
            }, 0);

            $('#total-inversion').val(totalInversion.toLocaleString('de-DE', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
            }));

            $('#total-ganancia').val(totalGain.toLocaleString('de-DE', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
            }));

            $('#total-venta').val(totalVenta.toLocaleString('de-DE', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
            }));
        },
        columnDefs: [
            {
                targets: [-8],
                class: 'text-center',
                render: function (data, type, row) {
                    let code = '<span class="badge text-dark fill-available badge-info"><b>' + data + '</b></span>';
                    return code;
                }
            },
            {
                targets: [-5],
                class: 'text-left',
                render: function(data, type, row){
                    let product = data + ' (' + row.type_product.name + ') ' + row.description;
                    return product
                }
            },
            {
                targets: [-3],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let quantity = `<span class="${row.css}" style="width: 30px;">${data}</span`;
                    return quantity;
                },
            },
            {
                targets: [-1,-2,-4],
                class: 'text-center',
                render: $.fn.dataTable.render.number('.', ',', 2)
            },
        ]
    })
}

$(function (){
    getData();
});