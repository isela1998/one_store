var tableBudget;
var sede = localStorage.getItem('sede');
var sede_id = 0;

function getData() {
  tableBudget = $('#data').DataTable({
    ordering: true,
    order: [[2, 'desc']],
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
    columns: [
      { data: 'user' },
      { data: 'datejoined' },
      { data: 'budget_number' },
      { data: 'client' },
      { data: 'total' },
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
        targets: [-2, -4],
        class: 'text-center',
      },
      {
        targets: [-3],
        render: function (data, type, row) {
          let client = `<i>${data.names} (${data.ci}) ${data.contact}</i>`;
          return client;
        },
      },
      {
        targets: [-2],
        orderable: true,
        render: function (data, type, row) {
          return `<span class="badge color1 text-dark pointer-1" style="width: 80px;">${data}</span>`;
        },
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons =
            '<a data-title="Presupuesto" rel="pdfInvoice" class="btn btn-warning btn-smp btn-flat"><i class="fas text-dark fa-file-alt"></i></a> ';
          buttons +=
            '<a href="#" rel="delete" data-title="Eliminar" type="button" class="btn btn-danger btn-smp btn-flat"><i class="fas text-dark fa-trash-alt"></i></a>';
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

  getData();
});

$(function () {
  $('#data tbody')
    .on('click', 'a[rel="pdfInvoice"]', function () {
      let tr = tableBudget.cell($(this).closest('td, li')).index();
      let data = tableBudget.row(tr.row).data();
      window.open(`/panel/presupuesto/pdf/${data.id}/`, '_blank');
    })
    .on('click', 'a[rel="delete"]', function () {
      let tr = tableBudget.cell($(this).closest('td, li')).index();
      let data = tableBudget.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('sede', '');
      parameters.append('action', 'delete');
      parameters.append('id', data.id);
      submit_with_ajax_msj(
        window.location.pathname,
        'Notificación',
        'Se ELIMINARÁ el presupuesto ¿Desea continuar?',
        parameters,
        function (response) {
          alertSweetSuccess('Presupuesto eliminado con éxito');
          setTimeout(tableBudget.ajax.reload(), 5000);
        }
      );
    });
});
