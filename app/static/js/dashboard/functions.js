function get_graph_sales() {
  $.ajax({
    url: window.location.pathname,
    type: 'POST',
    data: {
      action: 'get_graph_sales',
    },
    dataType: 'json',
  })
    .done(function (data) {
      if (!data.hasOwnProperty('error')) {
        graphcolumn.addSeries(data);
        return false;
      }
      message_error(data.error);
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      alert(textStatus + ': ' + errorThrown);
    })
    .always(function (data) {
      console.log(data);
    });
}

function get_graph_products() {
  $.ajax({
    url: window.location.pathname,
    type: 'POST',
    data: {
      action: 'get_graph_products',
    },
    dataType: 'json',
  })
    .done(function (data) {
      if (!data.hasOwnProperty('error')) {
        graphpie.addSeries(data);
        return false;
      }
      message_error(data.error);
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      alert(textStatus + ': ' + errorThrown);
    })
    .always(function (data) {});
}

$(function () {
  get_graph_sales();
  get_graph_products();
});

function alertSweet() {
  const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 1000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer);
      toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
  });

  Toast.fire({
    icon: 'success',
    title: 'Precios actualizados!',
  });
}

function up_dolar() {
  var dolar = document.getElementById('dolar').value;
  var parameters = new FormData();
  parameters.append('dolar', dolar);
  parameters.append('sede', '');
  parameters.append('action', 'upDolar');
  $.ajax({
    url: window.location.pathname,
    type: 'POST',
    data: parameters,
    dataType: 'json',
    processData: false,
    contentType: false,
  })
    .done(function (data) {
      if (!data.hasOwnProperty('error')) {
        alertSweet();
        window.setTimeout(function () {
          window.location.reload();
        }, 1500);
      } else {
        console.log('data');
        alert('Ocurrió un error');
      }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      alert(textStatus + ': ' + errorThrown);
    })
    .always(function (data) {});
}
