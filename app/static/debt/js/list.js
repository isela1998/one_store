var tableDebt;
var tbDebt;
var sede = localStorage.getItem('sede');
var sede_id = 0;

function getData(start, end) {
  tableDebt = $('#data').DataTable({
    ordering: true,
    order: [[1, 'desc']],
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
        sede: '',
        action: 'searchdata',
        start: start,
        end: end,
      },
      dataSrc: '',
    },
    columns: [
      { data: 'last_credit_date' },
      { data: 'name' },
      { data: 'totalDebt' },
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
        targets: [-4],
        orderable: true,
      },
      {
        targets: [-2],
        orderable: true,
        class: 'text-center',
        render: function (data, type, row) {
          return `<span class="badge color2 text-white pointer-1" style="width: 80px;">${data}</span>`;
        },
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons =
            '<a href="#" rel="increase" data-title="Incrementar" type="button" class="btn btn-info btn-smp btn-flat"><i class="fas text-dark fa-plus"></i></a> ';
          buttons +=
            '<a href="#" rel="payment" data-title="Abonar" type="button" class="btn btn-warning btn-smp btn-flat"><i class="fas text-dark fa-arrow-down"></i></a> ';
          buttons += `<a href="#" onclick="getData2(${data})" data-title="Historial" type="button" class="btn btn-secondary btn-smp btn-flat"><i class="fas text-dark fa-history"></i></a> `;
          buttons +=
            '<a href="#" rel="delete" data-title="Eliminar" type="button" class="btn btn-danger btn-smp btn-flat"><i class="fas text-dark fa-trash-alt"></i></a> ';
          return buttons;
        },
      },
    ],
    initComplete: function (settings, json) {},
  });
}

function getData2(id) {
  tbDebt = $('#data2').DataTable({
    ordering: true,
    order: [[1, 'asc']],
    searching: false,
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
        sede: '',
        action: 'searchdata2',
        id: id,
      },
      dataSrc: '',
    },
    dom: '<"myCustomClass"f>rt<"bottom"lp><"clear">',
    columns: [
      { data: 'operation' },
      { data: 'datehour' },
      { data: 'quantity' },
      { data: 'description' },
    ],
    columnDefs: [
      {
        targets: [-4],
        class: 'text-center',
        orderable: true,
        render: function (data, type, row) {
          let operation = 'nothing';
          if (data == '+')
            return `<span style="width: 25px; heigth: 25px; " class="badge badge-success text-white pointer-2">${data}</span>`;
          else if (data == '-')
            return `<span style="width: 25px; heigth: 25px; " class="badge badge-secondary text-white pointer-2">${data}</span>`;
        },
      },
      {
        targets: [-2],
        class: 'text-center',
        orderable: true,
        render: function (data, type, row) {
          return data + ' $';
        },
      },
    ],
  });
  $('#modalDetails').modal('show');
}

$(function () {
  $('#i_card_title').removeClass().addClass('text-dark fas fa-city');
  $('#i_card_title2').removeClass().addClass('text-dark fas fa-shopping-cart');

  $('#last_debt_date').datetimepicker({
    format: 'YYYY-MM-DD',
    date: moment().format('YYYY-MM-DD'),
    locale: 'es',
  });

  $('#last_credit_date').datetimepicker({
    format: 'YYYY-MM-DD',
    date: moment().format('YYYY-MM-DD'),
    locale: 'es',
  });

  $('#date_end').datetimepicker({
    format: 'YYYY-MM-DD',
    date: moment().format('YYYY-MM-DD'),
    locale: 'es',
  });

  $('#input-date').datetimepicker({
    format: 'YYYY-MM-DD',
    date: moment().format('YYYY-MM-DD'),
    locale: 'es',
  });

  $('#input-date-2').datetimepicker({
    format: 'YYYY-MM-DD',
    date: moment().format('YYYY-MM-DD'),
    locale: 'es',
  });

  $('#input-date, #input-date-2').on('change', function () {
    let start = $('input[name="input-date"]').val();
    let end = $('input[name="input-date-2"]').val();
    getData(start, end);
  });

  let start = $('input[name="input-date"]').val();
  let end = $('input[name="input-date-2"]').val();

  getData(start, end);
});

$(function () {
  $('.btn-report-debt').on('click', function () {
    let start = $('input[name="input-date"]').val();
    let end = $('input[name="input-date-2"]').val();
    window.open(`/panel/cuentas/pagar/reporte/pdf/${start}/${end}/`);
  });
});

$(function () {
  $('.btn-add-debt').on('click', function () {
    $('form')[0].reset();
    $('#modalDebt').modal('show');
  });

  $('#data tbody')
    .on('click', 'a[rel="details"]', function () {
      let tr = tableDebt.cell($(this).closest('td, li')).index();
      let data = tableDebt.row(tr.row).data();
      details_vents(data);
      $('#modalDetails').modal('show');
    })
    .on('click', 'a[rel="payment"]', function () {
      $('form')[1].reset();
      let tr = tableDebt.cell($(this).closest('td, li')).index();
      let data = tableDebt.row(tr.row).data();
      $('input[name="action"]').val('payment');
      $('input[name="idDebt"]').val(data.id);
      $('input[name="name"]').val(data.name);
      $('input[name="pending"]').val(data.totalDebt);
      $('#modalPayment').modal('show');
    })
    .on('click', 'a[rel="increase"]', function () {
      $('form')[2].reset();
      let tr = tableDebt.cell($(this).closest('td, li')).index();
      let data = tableDebt.row(tr.row).data();
      $('input[name="idIncreaseDebt"]').val(data.id);
      $('input[name="name"]').val(data.name);
      $('input[name="pending"]').val(data.totalDebt);
      $('#modalIncrease').modal('show');
    })
    .on('click', 'a[rel="delete"]', function () {
      let tr = tableDebt.cell($(this).closest('td, li')).index();
      let data = tableDebt.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('action', 'delete');
      parameters.append('id', data.id);
      submit_with_ajax_msj(
        window.location.pathname,
        'Notificación',
        '¿Estas seguro de realizar eliminar el siguiente registro?',
        parameters,
        function () {
          alertSweetSuccess('Listado de cuentas actualizado');
          setTimeout(tableDebt.ajax.reload(), 5000);
        }
      );
    });
});

$(function () {
  $('#formIncrease').on('submit', function (e) {
    e.preventDefault();
    let parameters = new FormData(this);
    parameters.append('action', 'increase');
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalIncrease').modal('hide');
      alertSweetSuccess('Cuenta actualizada con éxito');
      setTimeout(tableDebt.ajax.reload(), 5000);
    });
  });

  $('#formPayment').on('submit', function (e) {
    e.preventDefault();
    let parameters = new FormData(this);
    parameters.append('action', 'payment');
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalPayment').modal('hide');
      alertSweetSuccess('Abono registrado');
      setTimeout(tableDebt.ajax.reload(), 5000);
    });
  });

  $('#formDebt').on('submit', function (e) {
    e.preventDefault();
    let parameters = new FormData(this);
    parameters.append('action', 'addDebt');
    submit_with_ajax(window.location.pathname, parameters, function () {
      $('#modalDebt').modal('hide');
      alertSweetSuccess('Cuenta registrada con éxito');
      setTimeout(tableDebt.ajax.reload(), 5000);
    });
  });
});
