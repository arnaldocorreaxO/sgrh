/*Select2 de Transacciones*/

$(function () {
    // SELECT2 TRANSACCION
    var transaccion = $('select[name="transaccion"]');
    var modulo = $('input[name="modulo"]');
    var tipo_acceso = $('input[name="tipo_acceso"]');
    transaccion.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/base/transaccion/add/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: function (params) {
                // EL CODIGO DEL MODULO TOMA DEL INPUT HIDDEN DEL FORMULARIO CABECERA LLAMADO 
                // CADA VIEWS ENVIA EL CODIGO DEPENDIENDO DEL MODULO 
                params['modulo'] = modulo.val();
                params['tipo_acceso'] = tipo_acceso.val();
                return {
                    term: isNULL(params.term, ''),
                    action: 'search_trx_url',
                    modulo: isNULL(params.modulo, ''),
                    tipo_acceso: isNULL(params.tipo_acceso, '')
                };
            },
            processResults: function (data) {
                return {
                    results: data
                };

            },

        },
        // placeholder: 'Filtrar por Transacción',
        // minimumInputLength: 1,
    });
});