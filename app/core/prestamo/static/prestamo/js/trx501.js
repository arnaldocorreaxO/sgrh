$(document).ready(function () {
  console.log("trx501.js!");
  // FORM
  var form = $("#frmTransaccion");
  // BUTTON
  var procesar = $("#procesar");
  // INPUTS
  var fecha = $('input[name="fecha"]');
  var fec_acta = $('input[name="fec_acta"]');

  // VALIDATORS
  var validator = form.validate({
    lang: "es", //
  });

  // var validator = form.validate({
  //     rules: {
  //         fecha: "required",
  //         comentario: "required",
  //         solicitud: "required",
  //         situacion_solicitud: "required",

  //     },
  //     messages: {
  //         fecha: "Este campo es requerido",
  //         comentario: "Este campo es requerido",
  //         solicitud: "Debe seleccionar una solicitud para la transaccion",
  //         situacion_solicitud: "Debe seleccionar una situacion de solicitud para la transaccion"
  //     }

  // });

  fecha.datetimepicker({
    format: "DD/MM/YYYY",
    locale: "es",
    // keepOpen: false,
    // date: $('input[name="fecha"]').val(),
  });
  fec_acta.datetimepicker({
    format: "DD/MM/YYYY",
    locale: "es",
    // keepOpen: false,
    // date: $('input[name="fecha"]').val(),
  });

  /*PROCESAR TRANSACCION */

  var saveFormAjax = function () {
    // var form = $('#frmTransaccion');
    console.log("TRANSACCION TRX501");
    if (validator.form()) {
      var parameters = new FormData($(form)[0]);
      submit_formdata_with_ajax(
        "Notificación",
        "¿Procesar Transaccion?",
        $("#transaccion").val(), //URL
        parameters,
        function (data) {
          if (!data.hasOwnProperty("error")) {
            console.log(data.val);
            if (data.rtn != 0) {
              message_warning(data.msg);
              return false;
            } else {
              message_success_to_url(data.msg, ".");
            }
            return false;
          }
        }
      );
    }
    return false;
  };

  procesar.on("click", saveFormAjax);
});
