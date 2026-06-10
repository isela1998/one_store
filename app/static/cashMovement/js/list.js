var tableCashMovement;
var tbCashMovement;
var sede_id = 0;

function getData(start, end) {
  tableCashMovement = $('#data').DataTable({
    ordering: true,
    order: [[0, 'desc']],
    searching: true,
    paging: true,
    info: false,
    pageLength: 20,
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
      { data: 'date_time' },
      { data: 'tipo' },
      { data: 'method_pay.name' },
      { data: 'amount_dl' },
      { data: 'amount_bs' },
      { data: 'description' },
      { data: 'status' },
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
        targets: [-2],
        orderable: true,
        class: 'text-center',
        render: function (data, type, row) {
          let status = '';
          if (data == 1)
            status = `<span class="badge badge-success text-white pointer-1" style="width: 100px;">Registrado</span>`;
          else status = `<span class="badge badge-secondary text-white pointer-1" style="width: 100px;">Anulado</span>`;
          return status;
        },
      },
      {
        targets: [-4,-5],
        orderable: true,
        class: 'text-center',
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons = ''
          buttons +=
            '<a data-title="Anular" href="#" rel="return" type="button" class="btn btn-danger btn-smp btn-flat"><i class="fas text-dark fa-undo"></i></a> ';
          return buttons;
        },
      },
    ],
    initComplete: function (settings, json) {},
  });
}

$(function () {
  $('#i_card_title').removeClass().addClass('text-dark fas fa-city');
  $('#i_card_title2').removeClass().addClass('text-dark fas fa-shopping-cart');

  $('#datejoined').datetimepicker({
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
  $('#data tbody')
    .on('click', 'a[rel="return"]', function () {
      let tr = tableCashMovement.cell($(this).closest('td, li')).index();
      let data = tableCashMovement.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('action', 'delete');
      parameters.append('id', data.id);
      submit_with_ajax_msj(
        window.location.pathname,
        'Notificación',
        '¿Estas seguro de realizar anular el registro seleccionado?',
        parameters,
        function () {
          alertSweetSuccess('Listado de movimientos de caja actualizado');
          setTimeout(tableCashMovement.ajax.reload(), 5000);
        }
      );
    });
});

function searchAll(){
  let start = $('input[name="input-date"]').val();
  let end = $('input[name="input-date-2"]').val();
  getData(start, end);
}
