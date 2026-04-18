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
        action: 'searchdata',
      },
      dataSrc: '',
    },
    dom: '<"myCustomClass"f>rt<"bottom"lp><"clear">',
    fnDrawCallback: function () {
      $("input[type='search']").attr('id', 'searchBox');
      $("input[type='search']").attr('autocomplete', 'off');
      $("select[name='data_length'], #searchBox").removeClass('input-sm');
      $('#searchBox').css('width', '350px').focus();
      $('#data').removeClass('dataTables_filter');
    },
    columns: [
      { data: 'groups' },
      { data: 'date_joined' },
      { data: 'full_name' },
      { data: 'username' },
      { data: 'id' },
    ],
    columnDefs: [
      {
        targets: [-5],
        class: 'text-center',
        render: function (data, type, row) {
          let group = '';
          $.each(row.groups, function (key, value) {
            group += `<span class="badge color1 fill-available badge-info">${value.name}</span>`;
          });
          return group;
        },
      },
      {
        targets: [-4],
        class: 'text-center',
      },
      {
        targets: [-2],
        class: 'text-center',
        render: function (data, type, row) {
          let username = `<span class="badge color1 fill-available badge-info">${data}</span>`;
          return username;
        },
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons =
            '<a href="#" rel="edit" data-title="Editar" class="btn btn-warning btn-smp btn-flat"><i class="fas text-dark fa-edit"></i></a> ';
          buttons +=
            '<a href="#" rel="delete" data-title="Eliminar" type="button" class="btn btn-danger btn-smp btn-flat"><i class="fas text-dark fa-trash-alt"></i></a>';
          return buttons;
        },
      },
    ],
  });
}

$(function () {
  $('input[name="password"]').mouseover(function () {
    this.type = 'text';
  });

  $('input[name="password"]').mouseout(function () {
    this.type = 'password';
  });

  modal_title = $('.modal-title');
  $('#i_card_title').removeClass().addClass('text-dark fas fa-users-cog');

  getData();

  $('.btnAddUser').on('click', function () {
    $('form')[0].reset();
    $('input[name="action"]').val('add');
    $('#modalUsers').modal('show');
  });

  $('#data tbody')
    .on('click', 'a[rel="edit"]', function () {
      $('form')[0].reset();
      let tr = tbUser.cell($(this).closest('td, li')).index();
      let data = tbUser.row(tr.row).data();
      $('input[name="first_name"]').val(data.first_name);
      $('input[name="last_name"]').val(data.last_name);
      $('input[name="username"]').val(data.username);
      $('#modalUsers').modal('show');
    })
    .on('click', 'a[rel="delete"]', function () {
      let tr = tbUser.cell($(this).closest('td, li')).index();
      let data = tbUser.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('action', 'delete');
      parameters.append('id', data.id);
      submit_with_ajax_msj(
        window.location.pathname,
        'Notificación',
        '¿Estas seguro de eliminar el usuario?',
        parameters,
        function () {
          alertSweetSuccess('Listado de usuarios actualizado');
          setTimeout(tbUser.ajax.reload(), 5000);
        }
      );
    });

  $('form').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    let parameters = new FormData(this);
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalUsers').modal('hide');
      alertSweetSuccess('Datos de usuario actualizado con éxito');
      setTimeout(tbUser.ajax.reload(), 5000);
    });
  });
});
