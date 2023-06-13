var solicitud_ingreso = {
    list: function () {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            processing: true,
            serverSide: true,
            paging: true,
            ordering: true,
            searching: true,
            // stateSave: true,      Salva la seleccion de longitud de pagina lengthMenu  
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
            pagingType: "full_numbers",
            pageLength: 10,
            ajax: {
                url: pathname,
                type: 'POST',
                data: {
                    'action': 'search'
                },
                // dataSrc: "",
                headers: {
                    'X-CSRFToken': csrftoken
                },
            },
            order: [[0, 'asc']],
            columns: [
                {"data": "nro_solicitud"},
                {"data": "fec_solicitud"},                
                {"data": "persona"},
                {"data": "telefono"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var btnClass = "btn btn-secondary btn btn-flat disabled_aprobar";
                        if(!row.aprobado){
                            btnClass +='btn btn-success btn btn-flat';
                        };
                        console.log(btnClass)
                        var buttons = '<a href="' + pathname + '/update/' + row.id + '/" class= "btn btn-warning btn btn-flat" data-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a> ';
                        buttons += '<a href="' + pathname + '/aprobar/' + row.id + '/" class="'+ btnClass+ '" data-toggle="tooltip" title="Aprobar"><i class="fas fa-user-check"></i></a> ';
                        buttons += '<a href="' + pathname + '/delete/' + row.id + '/" type="button" class="btn btn-danger btn btn-flat" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash-alt"></i></a>';
                        return buttons;
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
        solicitud_ingreso.list(false);
    });
});
