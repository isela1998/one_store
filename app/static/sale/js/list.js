var tableSale;
var sede = localStorage.getItem('sede');
var sede_id = 0;

function details_vents(d) {
  let html = '';
  html += `<span><b>Cliente:</b></span><br>`;
  html += `<span> ${escapeHtml(d.client.names)} ${escapeHtml(d.client.identity)}${escapeHtml(d.client.ci)} ${escapeHtml(d.client.contact)}</span><hr>`;
  html += `<span><b>Nº Factura:</b></span><br>`;
  html += `<span>${escapeHtml(d.invoice_number)}</span><br>`;
  html += `<span><b>Estado:</b></span><br>`;
  if (d.status == 0)
    html += `<span class="badge badge-success text-dark pointer-1">Pagada</span><hr>`;
  else if (d.status == 1)
    html += `<span class="badge badge-warning text-dark pointer-1">Crédito</span><hr>`;
  else if (d.status == 2)
    html += `<span class="badge badge-warning text-dark pointer-1">Anulada</span><br>`;
  if (d.status == 2 && d.cancel_reason) {
    let esc = (v) => $('<div>').text(v || '').html();
    html += `<span>Anulada por ${esc(d.cancelled_by)} el ${esc(d.cancelled_at)}: ${esc(d.cancel_reason)}</span><hr>`;
  } else if (d.status == 2) {
    html += `<hr>`;
  }
  html += '<span><b>PRODUCTOS:</b></span><hr>';
  $.each(d.det, function (key, value) {
    html += `<span> ${escapeHtml(value.prod.brand)} ${escapeHtml(value.prod.product)} (${escapeHtml(value.prod.type_product.name)})</span><br>`;
    html += `<span>Cantidad: ${value.quantity}</span><br>`;
    html += `<span>Precio: ${value.price}</span><br>`;
    html += `<span>Subtotal: ${value.total}</span><hr>`;
  });
  html += `<span><b>Subtotal:</b></span><br>`;
  html += `<span>${d.subtotal}</span><br>`;
  html += `<span><b>Descuento:</b></span><br>`;
  html += `<span>${d.discount}<br>`;
  html += `<span><b>Total ($):</b></span><br>`;
  html += `<span>${d.total}$</span><hr>`;
  html += `<span><b>Total (Bs):</b></span><br>`;
  html += `<span>${d.totalBs}</span><br><hr>`;
  html += `<span><b>Método de Pago Nº 1:</b></span><br>`;
  html += `<span>${escapeHtml(d.method_pay.name)}</span><br>`;
  html += `<span>${d.received} ${d.method_pay.type_symbol}</span><br><hr>`;
  html += '<span><b>Método de Pago Nº 2:</b></span><br>';
  html += `<span>${escapeHtml(d.method_pay1.name)}</span><br>`;
  html += `<span>${d.received1} ${d.method_pay1.type_symbol}</span><br><hr>`;
  html += '<span><b>Método de Pago Nº 3:</b></span><br>';
  html += `<span>${escapeHtml(d.method_pay2.name)}</span><br>`;
  html += `<span>${d.received2} ${d.method_pay2.type_symbol}</span><br><hr>`;
  html += '<span><b>Notas y/o Descripción:</b></span><br>';
  html += `<span>${escapeHtml(d.description)}</span>`;

  document.getElementById('detailsVent').innerHTML = html;
  $('#modalDetails').show();
}

function getData(start, end) {
  tableSale = $('#data').DataTable({
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
        start: start,
        end: end,
      },
      dataSrc: '',
    },
    columns: [
      { data: 'user', render: $.fn.dataTable.render.text() },
      { data: 'datehour' },
      { data: 'invoice_number' },
      { data: 'type_sale' },
      { data: 'status' },
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
        targets: [-6, -7],
        orderable: true,
        class: 'text-center',
      },
      {
        targets: [-5],
        orderable: true,
        render: function (data, type, row) {
          let typeSale = '';
          if (data == 'Al Contado') typeSale = 'Contado';
          else typeSale = 'Crédito';
          return typeSale;
        },
      },
      {
        targets: [-4],
        orderable: true,
        render: function (data, type, row) {
          let status = '';
          if (data == 0)
            status = `<span class="badge badge-success text-white pointer-1" style="width: 60px;">Pagada</span>`;
          else if (data == 1)
            status = `<span class="badge badge-warning text-dark pointer-1" style="width: 60px;">Crédito</span>`;
          else if (data == 2)
            status = `<span class="badge badge-secondary text-white pointer-1" style="width: 60px;">Anulada</span>`;
          return status;
        },
      },
      {
        targets: [-3],
        render: function (data, type, row) {
          let client = `<i>${escapeHtml(data.names)} (${escapeHtml(data.ci)}) ${escapeHtml(data.contact)}</i>`;
          return client;
        },
      },
      {
        targets: [-2],
        orderable: true,
        class: 'text-center',
        render: function (data, type, row) {
          if (row.status == 2)
            return `<span class="badge badge-secondary text-white pointer-1" style="width: 80px;">${data}</span>`;
          else
            return `<span class="badge badge-success text-white pointer-1" style="width: 80px;">${data}</span>`;
        },
      },
      {
        targets: [-1],
        class: 'text-center',
        orderable: false,
        render: function (data, type, row) {
          let buttons =
            '<a data-title="Detalles" rel="details" class="btn btn-success btn-smp btn-flat"><i class="fas text-dark fa-search"></i></a> ';
          buttons +=
            '<a data-title="Nota de Entrega" rel="pdfInvoice" class="btn btn-info btn-smp btn-flat"><i class="fas text-dark fa-file-alt"></i></a> ';
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
  $('.btn-report-sales').on('click', function () {
    let start = $('input[name="input-date"]').val();
    let end = $('input[name="input-date-2"]').val();
    window.open(`/panel/ventas/reporte/pdf/1/${start}/${end}/`);
  });

  $('.btn-report-product').on('click', function () {
    let start = $('input[name="input-date"]').val();
    let end = $('input[name="input-date-2"]').val();
    window.open(`/panel/ventas/reporte/pdf/2/${start}/${end}/`);
  });
});

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
    .on('click', 'a[rel="details"]', function () {
      let tr = tableSale.cell($(this).closest('td, li')).index();
      let data = tableSale.row(tr.row).data();
      details_vents(data);
      $('#modalDetails').modal('show');
    })
    .on('click', 'a[rel="pdfInvoice"]', function () {
      let tr = tableSale.cell($(this).closest('td, li')).index();
      let data = tableSale.row(tr.row).data();
      alertSweetSuccess('Nota de entrega con éxito');
      window.open(`/panel/ventas/factura/pdf/${data.id}/`, '_blank');
    })
    .on('click', 'a[rel="return"]', function () {
      let tr = tableSale.cell($(this).closest('td, li')).index();
      let data = tableSale.row(tr.row).data();
      let parameters = new FormData();
      parameters.append('sede', sede);
      parameters.append('action', 'return');
      parameters.append('id', data.id);
      $.confirm({
        theme: 'material',
        title: 'Notificación',
        icon: 'fa fa-info',
        content:
          '<p>Se ANULARÁ la factura. Indique el motivo:</p>' +
          '<input type="text" class="form-control cancel-reason" maxlength="255" autocomplete="off">',
        columnClass: 'small',
        typeAnimated: true,
        buttons: {
          info: {
            text: 'Si',
            btnClass: 'btn-outline-info',
            action: function () {
              let reason = this.$content.find('.cancel-reason').val().trim();
              if (!reason) {
                message_error('Debe indicar el motivo de la anulación');
                return false;
              }
              parameters.append('reason', reason);
              submit_with_ajax(window.location.pathname, parameters, function (response) {
                alertSweetSuccess('Factura anulada con éxito');
                setTimeout(tableSale.ajax.reload(), 5000);
              });
            },
          },
          danger: {
            text: 'No',
            btnClass: 'btn-red',
            action: function () {},
          },
        },
      });
    });
});

$(function () {
  $('.formOfficeGuide').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    // Validations in the form
    let parameters = new FormData(this);
    parameters.append('sede', sede);
    submit_with_ajax_msj(
      window.location.pathname,
      'Notificación',
      '¿Está seguro de generar la Orden de Entrega?',
      parameters,
      function (response) {
        window.open(
          '/panel/sale/invoice/pdf/' + response.sede + '/' + response.id + '/',
          '_blank'
        );
        alertSweetSuccess('Orden de Entrega generada');
        setTimeout(window.location.reload(), 5000);
      }
    );
  });

  $('.formInvoicePay').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    let parameters = new FormData(this);
    parameters.append('sede', sede);
    parameters.append('action', 'addPayment');
    submit_with_ajax(window.location.pathname, parameters, function (response) {
      $('#modalPayments').modal('hide');
      alertSweetSuccess('Abono registrado con exito');
      setTimeout(tableSale.ajax.reload(), 5000);
    });
  });
});
