$(function () {   

    var action = $('input[name="action"]').val();

    if (action == 'add') {
        
        var select_vehiculo = $('select[name="vehiculo"]');
        var select_transporte = $('select[name="transporte"]');
        var sucursal_id = $('input[name="sucursal_id"]');

        // BUSCAMOS TRANSPORTE RELACIONADO AL VEHICULO
        select_vehiculo.on('change', function () {
            $.ajax({
                // csrftoken ver functions.js
                headers: { "X-CSRFToken": csrftoken },
                // url: window.location.pathname,
                url: '/bascula/movimiento/add/',
                type: 'POST',
                data: {
                    'action': 'search_data_vehiculo',
                    'id': $(this).val()
                },
                dataType: 'json',
            }).done(function (data) {
                if (!data.hasOwnProperty('error')) { 
                    transporte = data['transporte_id']
                    $('#id_transporte').val(transporte).change();
                    $('#id_peso_entrada').val(0);
                    // SOLO INTERNO 
                    if (transporte == 1) {
                        $('#id_peso_entrada').val(parseInt(data['peso']));
                        
                    };
                    return false;
                    
                };
                $('#id_vehiculo').val('').change();
                $('#id_transporte').val('').change();
                message_error(data.error);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ': ' + errorThrown);
            }).always(function (data) {
                //select_producto.html(options);
            });

        });

        select_vehiculo.on('change', function () {
            select_transporte.change();
        });

        // TRANSPORTE INTERNO REMITENTE Y DESTINO IGUALES 
        select_transporte.on('change', function () {
            // console.log($(this).val());
           if ($(this).val() == 1 ){   
               if (sucursal_id == 1){
                    $('#id_cliente').val(1).change();
                    $('#id_destino').val(1).change();
               }else{
                    $('#id_cliente').val(2).change();
                    $('#id_destino').val(2).change();
               };
               return false;
           }; 
            $('#id_cliente').val('').change();
            $('#id_destino').val('').change();          
        });
    };
});