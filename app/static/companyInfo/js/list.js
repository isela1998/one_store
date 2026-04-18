var tbCompany;
var modal_title;

function getData() {
  $.ajax({
    url: window.location.pathname,
    type: 'POST',
    data: {
      action: 'searchdata',
    },
    dataType: 'json',
  }).done(function (data) {
    if (data.error) {
      alertSweetError(data.error);
    } else {
      $('input[name="name"]').val(data.name);
      $('input[name="comercialName"]').val(data.comercialName);
      $('input[name="nit"]').val(data.nit);
      $('input[name="address"]').val(data.address);
      $('input[name="city"]').val(data.city);
      $('input[name="phone"]').val(data.phone);
      $('input[name="email"]').val(data.email);
      $('textarea[name="services"]').val(data.services);
    }
  });
}

$(function () {
  getData();

  $('#btn-edit-data').on('click', function () {
    disabledInput();
  });

  $('form').on('submit', function (e) {
    e.preventDefault();
    if (document.getElementById('id_nit').hasAttribute('disabled')) {
      alertSweetError('Primero, debes usar el botón de editar datos');
      return false;
    } else {
      convertToUpperCase();
      let parameters = new FormData(this);
      submit_with_ajax(window.location.pathname, parameters, function () {
        $('#modalCompany').modal('hide');
        alertSweetSuccess('Se actualizaron los datos de la empresa');
        setTimeout(window.location.reload(), 5000);
      });
    }
  });
});

function disabledInput() {
  document.getElementById('logo').removeAttribute('disabled');
  document.getElementById('id_name').removeAttribute('disabled');
  document.getElementById('id_comercialName').removeAttribute('disabled');
  document.getElementById('id_nit').removeAttribute('disabled');
  document.getElementById('id_address').removeAttribute('disabled');
  document.getElementById('id_city').removeAttribute('disabled');
  document.getElementById('id_phone').removeAttribute('disabled');
  document.getElementById('id_email').removeAttribute('disabled');
  document.getElementById('id_services').removeAttribute('disabled');
  document.getElementById('id_logo').removeAttribute('disabled');
}
