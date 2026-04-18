function message_error(obj) {
  contentStr = '';
  error = obj;
  alertSweetErrorProducts(error);
}

function submit_with_ajax_msj(url, title, content, parameters, callback) {
  $.confirm({
    theme: 'material',
    title: title,
    icon: 'fa fa-info',
    content: content,
    columnClass: 'small',
    typeAnimated: true,
    cancelButtonClass: 'btn-primary',
    draggable: true,
    dragWindowBorder: false,
    buttons: {
      info: {
        text: 'Si',
        btnClass: 'btn-outline-info',
        action: function () {
          $.ajax({
            url: url,
            type: 'POST',
            data: parameters,
            dataType: 'json',
            processData: false,
            contentType: false,
          })
            .done(function (data) {
              if (!data.hasOwnProperty('error')) {
                callback(data);
                return false;
              } else {
                message_error(data.error);
              }
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
              alert(textStatus + ': ' + errorThrown);
            })
            .always(function (data) {});
        },
      },
      danger: {
        text: 'No',
        btnClass: 'btn-red',
        action: function () {},
      },
    },
  });
}

function submit_with_ajax(url, parameters, callback) {
  $.ajax({
    url: url,
    type: 'POST',
    data: parameters,
    dataType: 'json',
    processData: false,
    contentType: false,
  })
    .done(function (data) {
      if (!data.hasOwnProperty('error')) {
        callback(data);
        return false;
      } else {
        message_error(data.error);
      }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      message_error(textStatus + ': ' + errorThrown);
      alert();
    });
}

function alert_action(title, content, callback, cancel) {
  $.confirm({
    theme: 'material',
    title: title,
    icon: 'fa fa-info',
    content: content,
    columnClass: 'small',
    typeAnimated: true,
    cancelButtonClass: 'btn-primary',
    draggable: true,
    dragWindowBorder: false,
    buttons: {
      info: {
        text: 'Si',
        btnClass: 'btn-primary',
        action: function () {
          callback();
        },
      },
      danger: {
        text: 'No',
        btnClass: 'btn-red',
        action: function () {
          cancel();
        },
      },
    },
  });
}

function alertSweetErrorProducts(title) {
  const Toast = Swal.mixin({
    toast: true,
    position: 'botoom-end',
    showConfirmButton: false,
    timer: 2000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer);
      toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
  });

  Toast.fire({
    icon: 'warning',
    title: title,
  });
}

function moduleInProcess() {
  const Toast = Swal.mixin({
    toast: true,
    position: 'botoom-end',
    showConfirmButton: false,
    timer: 2000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer);
      toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
  });

  Toast.fire({
    icon: 'warning',
    title: 'Falta por diseñar...',
  });
}

function alertSweetError(title) {
  const Toast = Swal.mixin({
    toast: true,
    position: 'botoom-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer);
      toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
  });

  Toast.fire({
    icon: 'warning',
    title: title,
  });
}

function alertSweetSuccess(title) {
  const Toast = Swal.fire({
    position: 'center',
    icon: 'success',
    title: title,
    showConfirmButton: false,
    timerProgressBar: true,
    timer: 2000,

    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer);
      toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
  });
}

function alertSuccess(title) {
  Swal.fire({
    position: 'center',
    icon: 'success',
    title: title,
    showConfirmButton: false,
    timer: 1000,
  });
}

$(function () {
  $('.inputNumberFormat').on('click', function () {
    $(this).select();
  });
});

$(function () {
  $('.inputNumbers').on('click', function () {
    $(this).select();
  });
});

function convertToUpperCase() {
  $('.UpperCase').each(function () {
    this.value = this.value.toUpperCase();
  });
}

function viewText() {
  $('.text-hide').removeClass('text-hide');
}

$(function () {
  if (document.body.classList.contains('sidebar-collapse')) {
  } else {
  }
});
