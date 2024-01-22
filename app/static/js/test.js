$(function () {
    console.log('TEST352')
    $('#id_fecha').blur(function () {
        console.log('TEST')
    })

    function isNULL(expression, replacement) {
        return (expression ? expression : replacement);
    }




    var saveForm = function (event) {
        console.log('holaaaaaaaaaaaaaaa')
        event.preventDefault()
        var form = $("#frmTransaccion");
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (request) {
                console.log(request);
                if (!request.hasOwnProperty('error')) {
                    if (request.rtn != 0) {
                        message_warning(isNULL(request.msg, request.error));
                        return false;
                    }
                    return false;
                }
                message_error(request.error);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                message_error(errorThrown + ' ' + textStatus);
            }
        });
        return false;
    };

    var saveFormAjax = function () {
        var form = $('#frmTransaccion');
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
                        message_success_to_url(data.msg, '/base/transaccion/add/')
                    };
                    return false;
                };

            });
    }
    // var saveForm = function () {
    //     alert('hoal')
    // }

    // $("#btnTEST2").click(function () {
    //     alert('hoal')
    // });
    // $("#btnTEST2").click(saveForm);
    $("#btnTEST2").click(saveFormAjax);
    // $("#frmTransaccion").on("submit", ".js-transaccion-form", saveForm);
    // btn = document.getElementById('btnTEST2');
    // // btn = $("#btnTEST2")
    // btn.click(function () {
    //     alert('hoal')
    // })// Works!
})

