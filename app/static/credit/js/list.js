var tableSale;
var tbCredit;
var sede = localStorage.getItem('sede');
var sede_id = 0;

function getData(start, end, all) {
  tableSale = $('#data').DataTable({
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
        all: all,
      },
      dataSrc: '',
    },
    columns: [
      { data: 'datehour' },
      { data: 'client' },
      { data: 'totalDebt' },
      { data: 'totalDebtBs' },
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
        targets: [-5],
        orderable: true,
      },
      {
        targets: [-4],
        render: function (data, type, row) {
          let client = `<i>${data.names} (${data.ci}) ${data.contact}</i>`;
          return client;
        },
      },
      {
        targets: [-3],
        orderable: true,
        class: 'text-center',
        render: function (data, type, row) {
          return `<span class="badge color2 text-white pointer-1" style="width: 80px;">${data}</span>`;
        },
      },
      {
        targets: [-2],
        orderable: true,
        class: 'text-center',
        render: function (data, type, row) {
          return `<span class="badge bg-secondary text-white pointer-1" style="width: 80px;">${data}</span>`;
        },
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons =
            '<a href="#" rel="payment" data-title="Abonar" type="button" class="btn btn-info btn-smp btn-flat"><i class="fas text-dark fa-arrow-down"></i></a> ';
          buttons += `<a href="#" onclick="getData2(${data})" data-title="Historial" type="button" class="btn btn-warning btn-smp btn-flat"><i class="fas text-dark fa-history"></i></a> `;
          return buttons;
        },
      },
    ],
    initComplete: function (settings, json) {},
  });
}

function getData2(id) {
  tbCredit = $('#data2').DataTable({
    ordering: true,
    order: [[0, 'desc']],
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
      { data: 'id' },
      { data: 'operation' },
      { data: 'datehour' },
      { data: 'quantity' },
      { data: 'quantitybs' },
      { data: 'description' },
      { data: 'sale.id' },
      { data: 'id' },
    ],
    columnDefs: [
      {
        targets: [-7],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let operation = 'nothing';
          if (data == '+')
            return `<span style="width: 25px; heigth: 25px; " class="badge badge-success text-white pointer-2">${data}</span>`;
          else if (data == '-')
            return `<span style="width: 25px; heigth: 25px; " class="badge badge-secondary text-white pointer-2">${data}</span>`;
        },
      },
      {
        targets: [-5],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          return data + ' $';
        },
      },
            {
        targets: [-4],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          return data + ' Bs';
        },
      },
      {
        targets: [-2],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          if (data == undefined)
            return `<span class="badge badge-info text-white pointer-1">NA</span>`;
          else
            return `<span class="badge badge-info text-white pointer-2" onclick="viewInvoice(${data})">${data}</span>`;
        },
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons = ''
          if(row.sale == undefined){
            buttons += '<a data-title="Eliminar" href="#" rel="delete" type="button" class="btn btn-secondary btn-smp"><i class="fas text-white fa-trash"></i></a> ';  
          }
          return buttons
        },
      },
    ],
  });
  $('#modalDetails').modal('show');
}

function viewInvoice(id) {
  window.open(`/panel/ventas/factura/pdf/${id}/`, '_blank');
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
    getData(start, end, gettAll());
  });

  $('#id_method_pay, #totalPayment').on('change keyup', function () {
    getDifference();
  });

  let start = $('input[name="input-date"]').val();
  let end = $('input[name="input-date-2"]').val();

  getData(start, end, gettAll());
});

$(function () {
  $('.btn-report-credit').on('click', function () {
    let start = $('input[name="input-date"]').val();
    let end = $('input[name="input-date-2"]').val();
    window.open(`/panel/ventas/creditos/reporte/pdf/${start}/${end}/`);
  });
});

$(function () {
   $('#data2 tbody')
    .on('click', 'a[rel="delete"]', function () {
      let tr = tbCredit.cell($(this).closest('td, li')).index();
      let data = tbCredit.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('action', 'deleteItem');
      parameters.append('id', data.id);
      submit_with_ajax_msj(
        window.location.pathname,
        'Notificación',
        '¿Estas seguro de realizar eliminar el siguiente registro?',
        parameters,
        function () {
          alertSweetSuccess('Listado de abonos actualizado');
          setTimeout(tableSale.ajax.reload(), 5000);
          setTimeout(tbCredit.ajax.reload(), 5000);
        }
      );
  });

  $('#data tbody')
    .on('click', 'a[rel="details"]', function () {
      let tr = tableSale.cell($(this).closest('td, li')).index();
      let data = tableSale.row(tr.row).data();
      details_vents(data);
      $('#modalDetails').modal('show');
    })
    .on('click', 'a[rel="payment"]', function () {
      $('form')[0].reset();
      let tr = tableSale.cell($(this).closest('td, li')).index();
      let data = tableSale.row(tr.row).data();
      $('input[name="action"]').val('payment');
      $('input[name="dl"]').val(data.dl);
      $('input[name="idCredit"]').val(data.id);
      $('input[name="client"]').val(data.client.names + ' ' +  data.client.identity + '-' + data.client.ci);
      $('input[name="pending"]').val(data.totalDebt);
      $('input[name="pending2"]').val(data.totalDebt);
      $('input[name="pendingBs"]').val(data.totalDebtBs);
      $('input[name="pending2Bs"]').val(data.totalDebtBs);
      $('#modalPayment').modal('show');
    })
    .on('click', 'a[rel="delete"]', function () {
      let tr = tableSale.cell($(this).closest('td, li')).index();
      let data = tableSale.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('action', 'delete');
      parameters.append('id', data.id);
      submit_with_ajax_msj(
        window.location.pathname,
        'Notificación',
        '¿Estas seguro de realizar eliminar el siguiente registro?',
        parameters,
        function () {
          alertSweetSuccess('Listado de créditos actualizado');
          setTimeout(tableSale.ajax.reload(), 5000);
        }
      );
    });
});

function searchAll(){
  let start = $('input[name="input-date"]').val();
  let end = $('input[name="input-date-2"]').val();
  getData(start, end, gettAll());
}

function gettAll() {
  let result = 0;
  const checkbox = document.getElementById('getAll');

  if (checkbox && checkbox.checked) { 
    result = 1;
  }
  
  return result;
}

function getDifference(){
  let option = $('select[name="method_pay"] option:selected').text();
  let amountDl = parseFloat($('input[name="pending"]').val());
  let amountBs = parseFloat($('input[name="pendingBs"]').val());
  let pay = parseFloat($('input[name="totalPayment"]').val()) || 0;
  let dl = parseFloat($('input[name="dl"]').val());

  console.log('dolar', dl)
  
  if (option.includes('$')) {
      let pendingDl = parseFloat(amountDl) - parseFloat(pay);
      let pendingBs = parseFloat(pendingDl) * parseFloat(dl);

      $('input[name="pending2"]').val(pendingDl.toFixed(2));
      $('input[name="pending2Bs"]').val(pendingBs.toFixed(2));

  } else if (option.includes('Bs')) {
      let pendingBs = parseFloat(amountBs) - parseFloat(pay);
      let pendingDl = parseFloat(pendingBs) / parseFloat(dl);

      $('input[name="pending2"]').val(pendingDl.toFixed(2));
      $('input[name="pending2Bs"]').val(pendingBs.toFixed(2));
  }
}

$(function () {
  $('#formPayment').on('submit', function (e) {
    e.preventDefault();
    let btnSubmit = $(this).find('button[type="submit"]');
    let option = $('select[name="method_pay"]').val();
    let pay = parseFloat($('input[name="totalPayment"]').val()) || 0;

    if (option == '' || option == 0){
      alertSweetErrorProducts('Debe seleccionar el método de pago');
      return false;
    } else if (pay <= 0){
      alertSweetErrorProducts('El monto a abonar debe ser mayor a 0');
      return false;
    } else {
      // Control de botón de envío
      btnSubmit.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Procesando...');
      // Send Data
      let parameters = new FormData(this);
      submit_with_ajax_with_error(window.location.pathname, parameters, function () {
        $('#modalPayment').modal('hide');
        alertSweetSuccess('Abono registrado');
        setTimeout(tableSale.ajax.reload(), 5000);
      },
      function (error) {
        btnSubmit.prop('disabled', false).text('Registrar Venta');
      });
    }
  });
});
