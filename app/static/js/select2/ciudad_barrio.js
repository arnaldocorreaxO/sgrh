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

    // SELECT2 CIUDAD
    var select2_ciudad = $('select[name="ciudad"]');
    select2_ciudad.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/base/persona/add/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: function (params) {
                return {
                    term: params.term,
                    action: 'search_ciudad'
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

    var select2_barrio = $('select[name="barrio"]');
    var token = $('input[name="csrfmiddlewaretoken"]');

    select2_ciudad.on('change', function () {
        var id = $(this).val();
        var options = '<option value="">(Todos)</option>';
        if (id === '') {
            select2_barrio.html(options);
            return false;
        }
        $.ajax({
            headers: { "X-CSRFToken": token.val() },
            // url: window.location.pathname,
            url: '/base/persona/add/',
            type: 'POST',
            data: {
                'action': 'search_barrio',
                'id': id
            },
            dataType: 'json',
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                select2_barrio.html('').select2({
                    theme: "bootstrap4",
                    language: 'es',
                    data: data
                });
                return false;
            }
            message_error(data.error);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ': ' + errorThrown);
        }).always(function (data) {
            //select2_barrio.html(options);
        });
    });

    select2_barrio.on('change', function () {
        var value = select2_barrio.select2('data')[0];
        // console.log(value);
    });
});