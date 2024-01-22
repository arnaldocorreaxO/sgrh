/*
===================================================================
Author: xO
====================================================================
*/
$(function () {

    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });

    // SELECT2 CLIENTE
    var select2_cliente = $('select[name="cliente"]');
    select2_cliente.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/general/cliente/add/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: function (params) {
                return {
                    term: params.term,
                    action: 'search_cliente'
                };
            },
            processResults: function (data) {
                return {
                    results: data
                };

            },

        },
        // placeholder: 'Filtrar por N°. Chapa',
        minimumInputLength: 1,
    });
});