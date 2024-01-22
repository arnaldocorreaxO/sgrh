var monto_solicitado
var plazo_solicitado
var isBlur = false;
var isMontoSinPlazo = false; //Monto sin indicar el plazo recupera el plazo maximo
var isMontoConPlazo = false; //Monto con indicar el plazo recupera la tasa de interes

function fnMONTO_PLAZO_PRESTAMO() {
    if (!isBlur) {
        monto_solicitado = document.getElementById('id_monto_solicitado').value;
        plazo_solicitado = document.getElementById('id_plazo_meses').value;

        // console.log(monto_solicitado);
        // console.log(plazo_solicitado);

        if (monto_solicitado > 0) {
            isMontoSinPlazo = true;
            isMontoConPlazo = false;
            if (plazo_solicitado > 0) {
                isMontoSinPlazo = false
                isMontoConPlazo = true
            };
        };

        // IsBlur evitar el desenfoque múltiple 
        isBlur = true;
        $.ajax({
            // async: false,
            // csrftoken ver functions.js
            headers: { "X-CSRFToken": csrftoken },
            // url: window.location.pathname,
            url: '/prestamo/solicitud_prestamo/add/',
            type: 'POST',
            data: {
                'action': 'search_plazo_monto',
                'monto_solicitado': monto_solicitado,
                'plazo_solicitado': plazo_solicitado

            },
            dataType: 'json',
            success: function (data) {
                console.log(data.val);
                if (data.val != 0) {
                    if (isMontoSinPlazo) {
                        $('#id_plazo_meses').val(formatoNumero(data.val));
                    };
                    if (isMontoConPlazo) {
                        $('#id_tasa_interes').val(formatoNumero(data.val, 2));
                    };
                }
                else {
                    if (data.val == 0) {
                        message_warning('Plazo ó Monto NO válidos!');
                        $('#id_plazo_meses').val(0);
                        $('#id_tasa_interes').val(0);
                    };
                };
                // Limpiamos variables
                isMontoSinPlazo = false;
                isMontoConPlazo = false;
                isBlur = false;
            }
        });
    };

};


$(document).ready(function () {
    $('#id_monto_solicitado').blur(function () {
        fnMONTO_PLAZO_PRESTAMO();
    });
    $('#id_plazo_meses').blur(function () {
        fnMONTO_PLAZO_PRESTAMO();
    });
});