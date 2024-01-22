$(document).ready(function () {
    console.log('trx504.js!');
    // FORM
    var form = $("#frmTransaccion")
    // BUTTON
    var procesar = $("#procesar");
    // INPUTS
    var fec_ult_desembolso = $('input[name="fec_ult_desembolso"]');
    var fec_1er_vencimiento = $('input[name="fec_1er_vencimiento"]');
    var select_solicitud = $('select[name="solicitud"]');


    select_solicitud.on('change', function () {
        console.log($(this).val())
        $.ajax({
            url: '/prestamo/trx504/',
            type: 'POST',
            dataType: 'json',
            data: {
                'action': 'search',
                'solicitud_prestamo': $(this).val()
            },

            beforeSend: function () {

            },
            success: function (response) {
                $('#fec_ult_desembolso').val('');
                $('#fec_1er_vencimiento').val('');

                if (!response.hasOwnProperty('error')) {
                    console.log(response)
                    console.log(response['fec_desembolso'])
                    $('#fec_ult_desembolso').val(response['fec_desembolso'])
                    $('#fec_1er_vencimiento').val(response['fec_1er_vencimiento'])
                    return false;
                }
                message_error(response.error);
            }
        });


    });

    // VALIDATORS
    var validator = form.validate({
        lang: 'es'//
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



    fec_ult_desembolso.datetimepicker({
        format: 'DD/MM/YYYY',
        locale: 'es',
        // keepOpen: false,
        // date: $('input[name="fecha"]').val(),
    });
    fec_1er_vencimiento.datetimepicker({
        format: 'DD/MM/YYYY',
        locale: 'es',
        // keepOpen: false,
        // date: $('input[name="fecha"]').val(),
    });



    /*PROCESAR TRANSACCION */

    var saveFormAjax = function () {
        // var form = $('#frmTransaccion');
        console.log('TRANSACCION TRX503')
        if (validator.form()) {
            var parameters = new FormData($(form)[0]);
            submit_formdata_with_ajax('Notificación',
                '¿Procesar Transaccion?',
                $('#transaccion').val(), //URL
                parameters,
                function (data) {
                    if (!data.hasOwnProperty('error')) {
                        console.log(data.val)
                        if (data.rtn != 0) {
                            message_warning(data.msg);
                            return false;
                        }
                        else {
                            message_success_to_url(data.msg, '.')
                        };
                        return false;
                    };

                });
        }
        return false;
    }

    procesar.on('click', saveFormAjax)

});
