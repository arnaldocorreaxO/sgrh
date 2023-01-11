function search_select2(){
    //MOVIMIENTO ASOCIADO
    var select_movimiento_padre = $('select[name="movimiento_padre"]');
    select_movimiento_padre.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/bascula/movimiento/add/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: function (params) {
                return {
                    term: params.term,
                    action: 'search_movi_asociado'
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
    //VEHICULO
    var select_vehiculo = $('select[name="vehiculo"]');
    select_vehiculo.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/bascula/movimiento/add/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: function (params) {
                return {
                    term: params.term,
                    action: 'search_vehiculo'
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
    //CHOFER
    var select_chofer = $('select[name="chofer"]');
    select_chofer.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/bascula/movimiento/add/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: function (params) {
                return {
                    term: params.term,
                    action: 'search_chofer'
                };
            },
            processResults: function (data) {
                return {
                    results: data
                };

            },
        },
        // placeholder: 'Filtrar por CI o Chofer ',
        minimumInputLength: 1,
    });
    //CLIENTE
    var select_cliente = $('select[name="cliente"]');
    select_cliente.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/bascula/movimiento/add/',
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
        // placeholder: 'Filtrar por Cliente ',
        minimumInputLength: 1,
    });
    //PRODUCTO
    var select_producto = $('select[name="producto"]');
    select_producto.select2({
        theme: "bootstrap4",
        language: 'es',
        // allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: '/bascula/movimiento/add/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: function (params) {
                return {
                    term: params.term,
                    action: 'search_producto',
                    cliente: select_cliente.val()
                };
            },
            processResults: function (data) {
                return {
                    results: data
                };

            },
        },
        // placeholder: 'Filtrar por Nombre Cliente ',
        minimumInputLength: 1,
    });

};

$(function () {
    search_select2();
});