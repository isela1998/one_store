var tbBrand;
var modal_title;
var sede = localStorage.getItem('sede');

function getData() {
  tbBrand = $('#data').DataTable({
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
        sede: sede,
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
    columns: [{ data: 'name' }, { data: 'name' }],
    columnDefs: [
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
  modal_title = $('.modal-title');
  $('#i_card_title').removeClass().addClass('text-dark fas fa-braille');

  getData();

  $('.btnAddBrand').on('click', function () {
    $('input[name="sede"]').val(sede);
    $('input[name="action"]').val('add');
    modal_title.find('span').html('Nueva Marca');
    document.getElementById('btn_submit').innerHTML =
      '<i class="fas fa-save"></i> Guardar';
    modal_title
      .find('#i_modal_title')
      .removeClass()
      .addClass('fas text-primary fa-plus');
    $('form')[0].reset();
    $('#modalBrand').modal('show');
  });

  $('#data tbody')
    .on('click', 'a[rel="edit"]', function () {
      modal_title.find('span').html('Editar marca');
      modal_title
        .find('#i_modal_title')
        .removeClass()
        .addClass('fas text-primary fa-edit');
      document.getElementById('btn_submit').innerHTML =
        '<i class="fas fa-sync"></i> Actualizar';
      let tr = tbBrand.cell($(this).closest('td, li')).index();
      let data = tbBrand.row(tr.row).data();
      $('input[name="sede"]').val(sede);
      $('input[name="action"]').val('edit');
      $('input[name="id"]').val(data.id);
      $('input[name="name"]').val(data.name);
      $('#modalBrand').modal('show');
    })
    .on('click', 'a[rel="delete"]', function () {
      let tr = tbBrand.cell($(this).closest('td, li')).index();
      let data = tbBrand.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('sede', sede);
      parameters.append('action', 'delete');
      parameters.append('id', data.id);
      submit_with_ajax_msj(
        window.location.pathname,
        'Notificación',
        '¿Estas seguro de realizar eliminar el siguiente registro?',
        parameters,
        function () {
          alertSweetSuccess('Categorías de Producto Actualizadas');
          setTimeout(tbBrand.ajax.reload(), 5000);
        }
      );
    });

  $('form').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    let parameters = new FormData(this);
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalBrand').modal('hide');
      alertSweetSuccess('Categorías de Producto Actualizadas');
      setTimeout(tbBrand.ajax.reload(), 5000);
    });
  });
});
