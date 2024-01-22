

$(document).ready(function () {
    var url;

    var transaccion = document.querySelector("#transaccion");
    var procesar = document.querySelector("#procesar");

    var loadForm = function () {

        console.log('GET URL')
        url = transaccion.value
        console.log(url)
        // console.log(data_parameters);
        $.ajax({
            url: url,
            // url: btn.attr("data-url"),
            type: 'POST',
            dataType: 'json',
            // data: '',//data_parameters,
            data: {
                action: 'load_form',
                // cod_cliente: 63
            },
            beforeSend: function () {
                $("#div_transaccion").html("");
                // div_transaccion.innerHTML = ""
                // $("#modal-transaccion").modal("show");
            },
            success: function (response) {
                // if (!response.hasOwnProperty('error')) {
                //     $("#modal-transaccion .modal-content").html(response.html_form);
                //     return false;
                // }
                // message_error(response.error);

                if (!response.hasOwnProperty('error')) {
                    $("#div_transaccion").html(response.html_form);
                    //de esta manera ejecuta Javascript inserto en el html 
                    // div_transaccion.innerHTML = response.html_form;
                    //de esta manera NO ejecuta javascript inserto en el html 
                    // div_transaccion.html = response.html_form;
                    // $("#frmTransaccion").attr("action", url)
                    // $("#frmTransaccion").attr("data-url", '/prestamo/solicitud_prestamo')
                    // form.setAttribute('action', url)

                    // setear_valores_form_modales(response.data)
                    return false;
                }
                message_error(response.error);
            }
        });
    };

    // LAS LLAMADAS DE saveFormAjax SE HACEN EN CADA UNA DE LAS TRX INDEPENDIENTES

    // var saveFormAjax = function () {
    //     var form = $('#frmTransaccion');
    //     form.validate();
    //     console.log('TRANSACCION BASE')
    //     var parameters = new FormData($(form)[0]);
    //     submit_formdata_with_ajax('Notificación',
    //         '¿Procesar Transaccion?',
    //         $('#transaccion').val(), //URL
    //         parameters,
    //         function (data) {
    //             if (!data.hasOwnProperty('error')) {
    //                 console.log(data.val)
    //                 if (data.rtn != 0) {
    //                     message_warning(data.msg);
    //                     return false;
    //                 }
    //                 else {
    //                     message_success_to_url(data.msg, '.')
    //                 };
    //                 return false;
    //             };

    //         });
    // }

    // $("#btnPROCESAR").click(saveFormAjax);


    // Con DOM Javascript
    transaccion.onchange = function () {
        loadForm();
    };
    // procesar.onclick = function () {
    //     saveFormAjax();
    // };
    // window.location.href = window.location.href
    // Con JQuery
    // $("#transaccion").on('change', loadForm)
    // $("#procesar").on('click', saveFormAjax);

});


