var tableEvents;

function get_all_events() {
  tableEvents = $('#data').DataTable({
    ordering: false,
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
        action: 'get_all_events',
      },
      dataSrc: '',
    },
    columns: [{ data: 'name' }, { data: 'id' }],
    dom: '<"myCustomClass"f>rt<"bottom"lp><"clear">',
    fnDrawCallback: function () {
      $("input[type='search']").attr('id', 'searchBox');
      $("input[type='search']").attr('autocomplete', 'off');
      $("input[type='search']").attr(
        'placeholder',
        'Título/Descripción/Fecha...'
      );
      $("select[name='data_length'], #searchBox").removeClass('input-sm');
      $('#searchBox').css('width', '260px').focus();
      $('#data').removeClass('dataTables_filter');
    },
    columnDefs: [
      {
        targets: [-2],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let tr =
            '<td><b><i class="text-dark">' +
            row.name +
            '</i></b><br>' +
            row.description +
            '<br>' +
            row.day +
            '</td>';
          return tr;
        },
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons =
            '<a href="#" type="button" rel="delete" class="btn btn-danger btn-xs btn-flat btnDelete"><i class="fas fa-trash-alt"></i></a> ';
          return buttons;
        },
      },
    ],
  });
}

$(function () {
  get_all_events();

  $('#day').datetimepicker({
    format: 'YYYY-MM-DD',
    date: moment().format('YYYY-MM-DD'),
    locale: 'es',
  });

  $('#data tbody').on('click', 'a[rel="delete"]', function () {
    let tr = tableEvents.cell($(this).closest('td, li')).index();
    let data = tableEvents.row(tr.row).data();
    let parameters = new FormData();
    parameters.append('action', 'delete');
    parameters.append('id', data.id);
    submit_with_ajax_msj(
      window.location.pathname,
      'Notificación',
      '¿Está seguro de eliminar el siguiente Evento?',
      parameters,
      function () {
        alertSweetSuccess('Eventos Actualizados');
        setTimeout(tableEvents.ajax.reload(), 5000);
        calendar.destroy();
        get_events();
      }
    );
  });
});
