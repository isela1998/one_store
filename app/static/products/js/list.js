var tbProduct;
var modal_title;
var sede = localStorage.getItem('sede');
var sede_id = 0;

function getData() {
  $('#i_card_title').removeClass().addClass('text-dark fas fa-boxes');
  $('#i_card_title2').removeClass().addClass('text-dark fas fa-th-list');

  tbProduct = $('#data').DataTable({
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
        sede: sede,
        action: 'searchdata',
      },
      dataSrc: '',
    },
    columns: [
      { data: 'code' },
      { data: 'category.name' },
      { data: 'type_product.name' },
      { data: 'product' },
      { data: 'description' },
      { data: 'quantity' },
      { data: 'cost' },
      { data: 'price_dl' },
      { data: 'price_bs' },
      { data: 'id' },
    ],
    dom: '<"myCustomClass"f>rt<"bottom"lp><"clear">',
    fnDrawCallback: function () {
      $("input[type='search']").attr('id', 'searchBox');
      $("input[type='search']").attr('autocomplete', 'off');
      $("select[name='data_length'], #searchBox").removeClass('input-sm');
      $('#searchBox').css('width', '350px').focus();
      $('#data').removeClass('dataTables_filter');
    },
    columnDefs: [
      {
        targets: [-7],
        orderable: true,
        render: function (data, type, row) {
          let quantity = '<span>' + row.brand + ' ' + data + '</span>';
          return quantity;
        },
      },
      {
        targets: [-5],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let quantity = `<span class="${row.css}" style="width: 30px;">${parseInt(data)}</span`;
          return quantity;
        },
      },
      {
        targets: [-2, -3, -4],
        class: 'text-center',
        orderable: false,
        render: $.fn.dataTable.render.number('.', ',', 2),
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons =
            '<a href="#" rel="edit" data-title="Editar datos" type="button" class="btn btn-warning btn-smp btn-flat"><i class="fas text-dark fa-edit"></i></a> ';
          buttons +=
            '<a href="#" rel="increase" data-title="Incrementar" type="button" class="btn btn-info btn-smp btn-flat"><i class="fas text-dark fa-plus"></i></a> ';
          buttons +=
            '<a href="#" rel="delete" data-title="Eliminar" type="button" class="btn btn-danger btn-smp btn-flat"><i class="fas text-dark fa-trash-alt"></i></a> ';
          return buttons;
        },
      },
    ],
  });
}

$(function () {
  let btn =
    '<a href="/panel/productos/inventario/pdf/" target="_blank" class="btn btn-outline-info"><i class="fas fa-arrow-circle-down"></i> <i class="fas fa-file-pdf"></i> Descargar Reporte</a>';
  document.getElementById('btn-report').innerHTML = btn;

  modal_title = $('.modal-title');
  getData();

  if ($('input[name="group"]').val() == 1) {
    tbProduct.column(-1).visible(false);
    tbProduct.column(-4).visible(false);
  }

  $('.btnAdd').on('click', function () {
    $('form')[0].reset();
    modal_title.find('#span_modal_title').html('Agregar Producto');
    modal_title
      .find('#i_modal_title')
      .removeClass()
      .addClass('fas text-primary fa-plus');
    document.getElementById('btn_submit').innerHTML =
      '<i class="fas fa-save"></i> Guardar';
    $('input[name="action"]').val('add');
    $('input[name="sede"]').val(sede);
    $('#modalProduct').modal('show');
  });

  $('.btnAddCategory').on('click', function () {
    $('form')[1].reset();
    $('input[name="sede"]').val(sede);
    $('input[name="action"]').val('addCategory');
    $('#modalCategory').modal('show');
  });

  $('.btnAddType').on('click', function () {
    $('form')[2].reset();
    $('input[name="sede"]').val(sede);
    $('input[name="action"]').val('addType');
    $('#modalType').modal('show');
  });

  $('#data tbody')
    .on('click', 'a[rel="edit"]', function () {
      $('form')[0].reset();
      modal_title.find('#span_modal_title').html('Editar Producto');
      modal_title
        .find('#i_modal_title')
        .removeClass()
        .addClass('fas text-primary fa-edit');
      document.getElementById('btn_submit').innerHTML =
        '<i class="fas fa-sync"></i> Actualizar';
      let tr = tbProduct.cell($(this).closest('td, li')).index();
      let data = tbProduct.row(tr.row).data();
      $('input[name="sede"]').val(sede);
      $('input[name="action"]').val('edit');
      $('input[name="id"]').val(data.id);
      $('input[name="code"]').val(data.code);
      $('select[name="category"]').val(data.category.id);
      $('select[name="type_product"]').val(data.type_product.id);
      $('input[name="product"]').val(data.product);
      $('input[name="brand"]').val(data.brand);
      $('textarea[name="description"]').val(data.description);
      $('input[name="quantity"]').val(data.quantity);
      $('input[name="cost"]').val(data.cost);
      $('input[name="price_dl"]').val(data.price_dl);
      $('input[name="price_bs"]').val(data.price_bs);
      $('#modalProduct').modal('show');
    })
    .on('click', 'a[rel="increase"]', function () {
      $('form')[3].reset();
      let tr = tbProduct.cell($(this).closest('td, li')).index();
      let data = tbProduct.row(tr.row).data();
      $('input[name="sede"]').val(sede);
      $('input[name="id"]').val(data.id);
      $('input[name="action"]').val('IncreaseProduct');
      $('input[name="name_product"]').val(
        `${data.brand} ${data.product} (${data.type_product.name})`
      );
      $('input[name="dsp-inventary"]').val(data.quantity);
      $('#modalIncreaseProduct').modal('show');
    })
    .on('click', 'a[rel="delete"]', function () {
      let tr = tbProduct.cell($(this).closest('td, li')).index();
      let data = tbProduct.row(tr.row).data();
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
          alertSweetSuccess('Listado de Productos actualizado');
          setTimeout(tbProduct.ajax.reload(), 5000);
        }
      );
    });

  $('.formProduct').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    let parameters = new FormData(this);
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalProduct').modal('hide');
      alertSweetSuccess('Listado de Productos actualizado');
      setTimeout(tbProduct.ajax.reload(), 5000);
    });
  });

  $('.formCategory').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    let parameters = new FormData(this);
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalCategory').modal('hide');
      alertSweetSuccess('Nueva categoría registrada');
      setTimeout(window.location.reload(), 5000);
    });
  });

  $('.formType').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    let parameters = new FormData(this);
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalType').modal('hide');
      alertSweetSuccess('Nuevo tipo de producto registrado');
      setTimeout(window.location.reload(), 5000);
    });
  });

  $('.formIncreaseProduct').on('submit', function (e) {
    e.preventDefault();
    let parameters = new FormData(this);
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalIncreaseProduct').modal('hide');
      alertSweetSuccess('Actualizado con éxito');
      setTimeout(tbProduct.ajax.reload(), 5000);
    });
  });
});
