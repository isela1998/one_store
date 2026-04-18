var tbUser;
var modal_title;

function getData() {
    tbUser = $('#data').DataTable({
        ordering: true,
        searching: true,
        paging: true,
        info: false,
        pagingType: 'simple_numbers',
        responsive: false,
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
        dom: '<"myCustomClass"f>rt<"bottom"lp><"clear">',
        fnDrawCallback: function () {
            $("input[type='search']").attr("id", "searchBox");
            $("input[type='search']").attr("autocomplete", "off");
            $("select[name='data_length'], #searchBox").removeClass("input-sm");
            $('#searchBox').css("width", "350px").focus();
            $('#data').removeClass('dataTables_filter');
        },
        columns: [
            { "data": "groups" },
            { "data": "date_joined" },
            { "data": "full_name" },
            { "data": "username" },
            { "data": "id" },
        ],
        columnDefs: [
            {
                targets: [-5],
                class: 'text-center',
                render: function (data, type, row) {
                    let group = ''
                    $.each(row.groups, function(key, value) {
                        group += '<span class="badge text-dark fill-available badge-info">'+value.name+'</span>';
                    });
                    return group;
                }
            },
            {
                targets: [-4],
                class: 'text-center',
            },
            {
                targets: [-2],
                class: 'text-center',
                render: function(data, type, row) {
                    let username = '<span class="badge text-dark fill-available badge-info">'+data+'</span>';
                    return username;
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let buttons = '<a href="#" rel="edit" data-title="Editar" class="btn btn-warning btn-smp btn-flat"><i class="fas text-dark fa-edit"></i></a> ';
                    return buttons;
                }
            },
        ]
    })
}

$(function () {

    $('input[name="password"]').mouseover(function () {
        this.type = 'text';
    });

    $('input[name="password"]').mouseout(function () {
        this.type = 'password';
    });

    modal_title = $('.modal-title')
    $('#i_card_title').removeClass().addClass('text-dark fas fa-users-cog')

    getData();

    $('#data tbody').on('click', 'a[rel="edit"]', function () {
        $('form')[0].reset();
        modal_title.find('span').html('Editar Usuario');
        modal_title.find('#i_modal_title').removeClass().addClass('fas text-primary fa-edit');
        document.getElementById('label_password').innerHTML = 'Nueva contraseña'
        document.getElementById('btn_submit').innerHTML = '<i class="fas fa-sync"></i> Actualizar'
        let tr = tbUser.cell($(this).closest('td, li')).index();
        let data = tbUser.row(tr.row).data();
        $('input[name="action"]').val('edit');
        $('input[name="id"]').val(data.id);
        $('input[name="first_name"]').val(data.first_name);
        $('input[name="last_name"]').val(data.last_name);
        $('input[name="username"]').val(data.username);
        $('input[name="date_joined"]').val(data.date_joined);
        $('#modalUsers').modal('show');
    });

    $('form').on('submit', function (e) {
        e.preventDefault();
        let parameters = new FormData(this);
        submit_with_ajax(window.location.pathname, 'Notificación', '¿Estas seguro de realizar la siguiente acción?', parameters, function () {
            $('#modalUsers').modal('hide');
            alertSweetSuccess('Listado de Usuarios Actualizadas');
            setTimeout(tbUser.ajax.reload(), 5000);
        });
    });
});

