

function get_list(args) {

    var movimiento = {

        list: function () {
            $('#data').DataTable({
                responsive: true,
                autoWidth: false,
                destroy: true,
                deferRender: true,
                info:false,
                ordering:false,
                // processing: true,
                // serverSide: true,
                paging: false,
                // ordering: true,
                searching: false,
                // stateSave: true,      Salva la seleccion de longitud de pagina lengthMenu  
                // lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
                // pagingType: "full_numbers",
                // pageLength: 10,
                ajax: {
                    url: pathname,
                    type: 'POST',
                    data: {
                            'producto'  : args[7],
                            'sucursal'  : args[5],                            
                            'fecha'     : args[2],
                            'action'    : 'search'
                    },
                    dataSrc: "",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                },
                order: [[0, 'asc']],
                columns: [
                    { "data": "fecha" },
                    { "data": "vehiculo" },
                    { "data": "chofer" },
                    { "data": "producto" },
                    { "data": "peso_neto" },
                ],
                columnDefs: [
                    {
                        targets: [0,-1],
                        class: 'text-center',                        
                        render: function (data, type, row) {
                           return data;
                        }
                    },
                ],
                initComplete: function (settings, json) {

                }
            });
        }
    };

    $(function () {
        $(document).ready(function () {
            movimiento.list();
        });
    });
};