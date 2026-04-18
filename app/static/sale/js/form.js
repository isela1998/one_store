var tableProducts;
var tablePendingChanges;
var sede = localStorage.getItem('sede');
var sede_id = 0;
var client;

// Process for calculating invoice totals
var sales = {
  items: {
    subtotal: 0.0,
    discount: 0.0,
    iva: 0.0,
    total: 0.0,
    dolar1: 0.0,
    products: [],
  },
  calculate_invoice: function () {
    let subtotal = 0.0;
    let subtotalBs = 0.0;
    $.each(this.items.products, function (pos, dict) {
      dict.subtotal = dict.quantity * parseFloat(dict.price_dl);
      subtotal += dict.subtotal;
    });

    this.items.total = subtotal;
    subtotalBs = this.items.total * this.items.dolar1;

    $('input[name="quantity_dolars"]').val(this.items.total.toFixed(2));
    $('input[name="total"]').val(subtotalBs.toFixed(2));

    $('input[name="totalDlR"]').val(this.items.total.toFixed(2));
    $('input[name="totalBsR"]').val(subtotalBs.toFixed(2));
  },
  add: function (item) {
    this.items.products.push(item);
    this.list();
  },
  list: function () {
    this.calculate_invoice();
    tableProducts = $('#tableProducts').DataTable({
      responsive: false,
      autoWidth: false,
      destroy: true,
      data: this.items.products,
      columns: [
        { data: 'brand' },
        { data: 'product' },
        { data: 'price_dl' },
        { data: 'quantity' },
        { data: 'subtotal' },
      ],
      searching: false,
      columnDefs: [
        {
          targets: [0],
          class: 'text-center tdLarger',
          orderable: false,
          render: function (data, type, row) {
            return '<a rel="remove" class="btn color2 btn-sm"><i class="fas fa-trash-alt"></i></a>';
          },
        },
        {
          targets: [-4],
          class: 'text-left tdLarger',
          orderable: false,
          render: function (data, type, row, meta) {
            let product = `<span class="pointer-1" data-title="${row.price_dl}$"> ${row.category.name} - ${row.brand} ${row.product} (${row.type_product.name})</span>`;
            return product;
          },
        },
        {
          targets: [-3],
          class: 'text-center tdLarger',
          orderable: false,
          render: $.fn.dataTable.render.number(',', '.', 2),
        },
        {
          targets: [-2],
          class: 'text-center tdLarger',
          orderable: false,
          render: function (data, type, row) {
            return `<input type="text" onclick="selectThis(this)" name="quantity" style="width: 60px;" class="form-control form-control-sm input-sm text-center" autocomplete="off" value="${row.quantity}">`;
          },
        },
        {
          targets: [-1],
          class: 'text-right tdLarger',
          orderable: false,
          render: $.fn.dataTable.render.number(',', '.', 2),
        },
      ],
      rowCallback(row, data, displayNum, displayIndex, dataIndex) {
        $(row).find('input[name="quantity"]').TouchSpin({
          min: 1,
          max: data.qinitial,
          step: 1,
          decimals: 0,
          boostat: 5,
          maxboostedstep: 10,
        });
      },
      initComplete: function (settings, json) {},
    });
  },
};

$(function () {
  optionsTypeSale();
  

  // Delete or increase a product on the invoice
  $(function () {
    $('#tableProducts tbody')
      .on('click', 'a[rel="remove"]', function () {
        let tr = tableProducts.cell($(this).closest('td, li')).index();
        sales.items.products.splice(tr.row, 1);
        sales.list();
      })
      .on('change keyup', 'input[name="quantity"]', function (e) {
        let quantity = parseFloat($(this).val());
        let tr = tableProducts.cell($(this).closest('td, li')).index();

        sales.items.products[tr.row].quantity = quantity;
        sales.calculate_invoice();
        $('td:eq(4)', tableProducts.row(tr.row).node()).html(
          sales.items.products[tr.row].subtotal
            .toFixed(2)
            .replace(/\d(?=(\d{3})+\.)/g, '$&,')
        )

        getDifference();
      })
      .on('keydown', 'input[name="quantity"]', function (e) {
        var keyCode= e.which;
        if (keyCode == 13){
          e.preventDefault();
          return false;
        }
      });
  });

  // Default values
  $(function () {
    document.getElementById('id_received').disabled = true;
    document.getElementById('id_received1').disabled = true;
    document.getElementById('id_received2').disabled = true;

    $('.btnAddClient').on('click', function () {
      $('#formClient')[0].reset();
      $('#modalClient').modal('show');
    });

    $('select[name="method_pay"]').on('change', function () {
      let methodName = $('select[name="method_pay"] option:selected').text();
      if (this.value == 1) {
        document.getElementById('id_received').disabled = true;
        document.getElementById('id_received').value = 0.0;
      } else if(methodName.includes("($)")){
        document.getElementById('id_received').disabled = false;
        document.getElementById('id_received').value = $('input[name="totalDlR"]').val();
      } else if(methodName.includes("(Bs)")){
        document.getElementById('id_received').disabled = false;
        document.getElementById('id_received').value = $('input[name="totalBsR"]').val();
      } else document.getElementById('id_received').disabled = false;

      getDifference();
    });

    $('select[name="method_pay1"]').on('change', function () {
      let methodName = $('select[name="method_pay1"] option:selected').text();
      if (this.value == 1) {
        document.getElementById('id_received1').disabled = true;
        document.getElementById('id_received1').value = 0.0;
      } else if(methodName.includes("($)")){
        document.getElementById('id_received1').disabled = false;
        document.getElementById('id_received1').value = $('input[name="totalDlR"]').val();
      } else if(methodName.includes("(Bs)")){
        document.getElementById('id_received1').disabled = false;
        document.getElementById('id_received1').value = $('input[name="totalBsR"]').val();
      } else document.getElementById('id_received1').disabled = false;


      getDifference();
    });

    $('select[name="method_pay2"]').on('change', function () {
      let methodName = $('select[name="method_pay2"] option:selected').text();
      if (this.value == 1) {
        document.getElementById('id_received2').disabled = true;
        document.getElementById('id_received2').value = 0.0;
      } else if(methodName.includes("($)")){
        document.getElementById('id_received2').disabled = false;
        document.getElementById('id_received2').value = $('input[name="totalDlR"]').val();
      } else if(methodName.includes("(Bs)")){
        document.getElementById('id_received2').disabled = false;
        document.getElementById('id_received2').value = $('input[name="totalBsR"]').val();
      } else document.getElementById('id_received2').disabled = false;


      getDifference();
    });

    $('input[name="received"]').on('change keyup', function () {
      getDifference();
    }).on('keydown', function (e) {
      var keyCode= e.which;
      if (keyCode == 13){
        e.preventDefault();
        return false;
      }
    });

    $('input[name="received1"]').on('change keyup', function () {
      getDifference();
    }).on('keydown', function (e) {
      var keyCode= e.which;
      if (keyCode == 13){
        e.preventDefault();
        return false;
      }
    });

    $('input[name="received2"]').on('change keyup', function () {
      getDifference();
    }).on('keydown', function (e) {
      var keyCode= e.which;
      if (keyCode == 13){
        e.preventDefault();
        return false;
      }
    });

    $('input[name="discount"]')
      .on('change keyup', function () {
        sales.items.discount = parseFloat(this.value);
        sales.calculate_invoice();
        getDifference();
      })
      .on('blur', function () {
        if (this.value == '') this.value = 0;
        sales.items.discount = parseFloat(this.value);
        sales.calculate_invoice();
        getDifference();
      }).on('keydown', function (e) {
        var keyCode= e.which;
        if (keyCode == 13){
          e.preventDefault();
          return false;
        }
      });

    document.getElementById('searchClient').style.fontSize = 'large';

    $('.select2').select2({
      theme: 'bootstrap4',
      language: 'es',
    });

    $('#datejoined').datetimepicker({
      format: 'YYYY-MM-DD',
      date: moment().format('YYYY-MM-DD'),
      locale: 'es',
      maxDate: moment().format('YYYY-MM-DD'),
    });

    $('select[name="search"]')
      .select2({
        theme: 'bootstrap4',
        language: 'es',
        ajax: {
          delay: 150,
          type: 'POST',
          url: window.location.pathname,
          data: function (params) {
            let queryParameters = {
              term: params.term,
              sede: sede,
              action: 'search_products',
            };
            return queryParameters;
          },
          processResults: function (data) {
            return {
              results: data,
            };
          },
        },
        placeholder: 'Búsqueda...',
        minimunInputLength: 1,
      })
      .on('select2:select', function (e) {
        let result;
        let data = e.params.data;

        data.quantity = 1;
        data.subtotal = 0.0;

        sales.items.products.forEach((element) => {
          if (element.text == data.text) {
            result = true;
          }
        });

        if (result != true) {
          sales.add(data);
          $(this).val('').trigger('change.select2');
          return false;
        } else {
          alertSweetErrorProducts('El producto ya existe en la factura');
          $(this).val('').trigger('change.select2');
          return false;
        }
      });

    $('select[name="searchClient"]')
      .select2({
        theme: 'bootstrap4',
        language: 'es',
        ajax: {
          delay: 10,
          type: 'POST',
          url: window.location.pathname,
          data: function (params) {
            let queryParameters = {
              term: params.term,
              sede: sede,
              action: 'search_client',
            };
            return queryParameters;
          },
          processResults: function (data) {
            return {
              results: data,
            };
          },
        },
        placeholder: 'Búsqueda por Nombre/Cédula/RIF',
        minimunInputLength: 2,
      })
      .on('select2:select', function (e) {
        let data = e.params.data;
        $('select[name="searchClient"]').val(data.id);
      });
  });

  // Validate totals
  function validatePay() {
    let pay1 = 0;
    let pay2 = 0;
    let pay3 = 0;
    let received1 = parseFloat($('input[name="received"]').val());
    let received2 = parseFloat($('input[name="received1"]').val());
    let received3 = parseFloat($('input[name="received2"]').val());
    let totalReceived = 0;

    let option1 = $('select[name="method_pay"] option:selected').text();
    let option2 = $('select[name="method_pay1"] option:selected').text();
    let option3 = $('select[name="method_pay2"] option:selected').text();

    if (option1.includes('$')) {
      pay1 = received1;
    } else if (option1.includes('Bs')) {
      pay1 = received1 / sales.items.dolar1;
    }

    if (option2.includes('$')) {
      pay2 = received2;
    } else if (option2.includes('Bs')) {
      pay2 = received2 / sales.items.dolar1;
    }

    if (option3.includes('$')) {
      pay3 = received3;
    } else if (option3.includes('Bs')) {
      pay3 = received3 / sales.items.dolar1;
    }

    totalReceived = pay1 + pay2 + pay3;
    return totalReceived;
  }

  function getDifference() {
    let differenceDl = 0;
    let differenceBs = 0;
    let totalInvoice = sales.items.total;
    let discount = sales.items.discount;
    let totalReceived = validatePay();
    let totalRWDiscount = totalReceived + discount;

    differenceDl = totalInvoice - totalRWDiscount;
    differenceBs = differenceDl * sales.items.dolar1;

    $('input[name="totalDlR"]').val(differenceDl.toFixed(2));
    $('input[name="totalBsR"]').val(differenceBs.toFixed(2));

    if (differenceDl.toFixed(2) == 0 || differenceDl < 0) return true;
    else return false;
  }

  //Send data
  $('#formSale').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    // Validations in the form
    let difference = $('input[name="totalDlR"]').val();
    let check1 = document.getElementById('cash_payment').checked;
    let check2 = document.getElementById('credit_payment').checked;
    let select_cli = $('select[name="searchClient"]').val();

    if (check1 == true) {
      if (!getDifference()) {
        alertSweetErrorProducts(`Faltan ${difference}$ por pagar`);
        return false;
      }
    }
    if (sales.items.products.length == 0) {
      alertSweetErrorProducts('Debe agregar un producto');
      return false;
    } else if (select_cli == '') {
      alertSweetErrorProducts('Faltan los datos del Cliente');
      return false;
    } else if (
      check1 == true &&
      $('input[name="method_pay"]').val() == 1 &&
      $('input[name="method_pay1"]').val() == 1 &&
      $('input[name="method_pay2"]').val() == 1
    ) {
      alertSweetErrorProducts('Verifique los métodos de pago');
      return false;
    } else if (
      check1 == true &&
      $('input[name="received"]').val() == 0 &&
      $('input[name="received1"]').val() == 0 &&
      $('input[name="received2"]').val() == 0
    ) {
      alertSweetErrorProducts('Verifique los métodos de pago');
      return false;
    } else if (check1 != true && check2 != true) {
      alertSweetErrorProducts('Seleccione el Método de Pago');
      return false;
    } else if ($('input[name="request"]').val() == 1) {
      alertSweetErrorProducts('Ya se recibió su petición, porfavor espere...');
      return false;
    } else {
      // Send Data
      $('input[name="request"]').val(1);
      document.getElementById('id_received').disabled = false;
      document.getElementById('id_received1').disabled = false;
      document.getElementById('id_received2').disabled = false;
      // document.getElementById('id_discount').disabled = false;
      let parameters = new FormData(this);
      parameters.append('sales', JSON.stringify(sales.items));
      parameters.append('action', 'add');
      parameters.append('sede', sede);
      submit_with_ajax(
        window.location.pathname,
        parameters,
        function (response) {
          alertSweetSuccess('Venta registrada con Éxito');
          window.location.reload();
          location.href = '#top';
        }
      );
    }
  });

  $('#budget').on('click', function (e) {
    e.preventDefault();
    // Validations in the form
    $('input[name="type_request"]').val(1);
    let check1 = document.getElementById('cash_payment').checked;
    let check2 = document.getElementById('credit_payment').checked;
    let select_cli = $('select[name="searchClient"]').val();
    if (sales.items.products.length == 0) {
      alertSweetErrorProducts('Debe agregar un producto');
      return false;
    } else if (select_cli == '') {
      alertSweetErrorProducts('Faltan los datos del Cliente');
      return false;
    } else if (check1 != true && check2 != true) {
      alertSweetErrorProducts('Seleccione el Método de Pago');
      return false;
    } else if ($('select[name="method_pay1"]').val() == '') {
      $('select[name="method_pay1"]').val(1);
    } else if ($('select[name="method_pay2"]').val() == '') {
      $('select[name="method_pay2"]').val(1);
    } else {
      // Send Data
      let form = document.getElementById('formSale');
      let parameters = new FormData(form);
      parameters.append('sales', JSON.stringify(sales.items));
      parameters.append('action', 'addBudget');
      parameters.append('sede', sede);
      submit_with_ajax(
        window.location.pathname,
        parameters,
        function (response) {
          window.open(`/panel/presupuesto/pdf/${response.id}/`, '_blank');
          window.location.reload();
          location.href = '#top';
        }
      );
    }
  });

  $('#formClient').on('submit', function (e) {
    e.preventDefault();
    convertToUpperCase();
    let parameters = new FormData(this);
    parameters.append('action', 'addClient');
    parameters.append('sede', sede);
    submit_with_ajax(window.location.pathname, parameters, function (response) {
      console.log(response);
      let option =
        '<option value="' +
        response.id +
        '">' +
        response.names +
        ' ' +
        response.ci +
        ' </option>';
      document
        .getElementById('searchClient')
        .insertAdjacentHTML('beforeend', option);

      $('select[name="searchClient"]').val(response.id);
      document.getElementById('select2-searchClient-container').innerHTML =
        response.names + ' ' + response.ci;
      $('#modalClient').modal('hide');
      alertSweetSuccess('Cliente registrado con éxito');
    });
  });
});

// Auxiliary functions
function optionsTypeSale() {
  if (document.getElementById('cash_payment').checked == true) {
    cash_payment();
    $('#description')
      .val('Sin observaciones')
      .attr('placeholder', 'Agregue un comentario o nota de la venta...');
    $('select[name="method_pay"]').val(1);
  } else if (document.getElementById('credit_payment').checked == true) {
    credit_payment();
    sales.calculate_invoice();
    $('#description')
      .val('Sin observaciones')
      .attr('placeholder', 'Indique detalles del crédito ó presupuesto...');
  }
}

function cash_payment() {
  document.querySelectorAll('#box1,#box2,#box4').forEach(function (box) {
    box.style.display = 'block';
  });
}

function credit_payment() {
  $('select[name="method_pay"]').val(1);
  $('select[name="method_pay1"]').val(1);
  $('select[name="method_pay2"]').val(1);
  $('input[name="received"]').val(0);
  $('input[name="received1"]').val(0);
  $('input[name="received2"]').val(0);
  document.getElementById('id_received').disabled = true;
  document.getElementById('id_received1').disabled = true;
  document.getElementById('id_received2').disabled = true;

  document.querySelectorAll('#box1,#box2').forEach(function (box) {
    box.style.display = 'none';
  });
  document.querySelectorAll('#box4').forEach(function (box) {
    box.style.display = 'block';
  });
}

function selectThis(input) {
  input.select();
}
