var input_fec_resolucion;
$(function () {
    ///////////////////////////
    //    EVENTO SUBMIT     
    ////////////////////////

    $('#frmForm').on('submit', function (e) {
        e.preventDefault();

        var parameters = new FormData(this);
        // parameters.append('action', action);

        submit_formdata_with_ajax('Notificación',
            '¿Procesar Solicitud de Ingreso del Socio?',
            window.location.pathname,
            parameters,
            function (data) {
                if (!data.hasOwnProperty('error')) {
                    console.log(data.info)
                    if (data.return != 0) {
                        message_warning(data.info);
                        return false;
                    }
                    else {
                        message_info(data.info);
                    };
                    return false;
                };

            });
    });

    input_fec_resolucion = $('input[name="fec_resolucion"]');
    input_fec_resolucion.datetimepicker({
        format: 'DD/MM/YYYY',
        locale: 'es',
        keepOpen: false,
        date: new moment().format("YYYY-MM-DD")
    });

});