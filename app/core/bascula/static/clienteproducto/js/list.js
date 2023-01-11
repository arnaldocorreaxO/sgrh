var tblData;
var input_daterange;
var columns = [];

function initTable() {
    
    tblData = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
    });

    $.each(tblData.settings()[0].aoColumns, function (key, value) {
        columns.push(value.sWidthOrig);
    });

    $('#data tbody tr').each(function (idx) {
        $(this).children("td:eq(0)").html(idx + 1);
        console.log(idx+1);
    });
}


function getData(all) {  

    var parameters = {
        'action': 'search',       
    };

    tblData = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,  
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            //Sin este da error de length
            dataSrc: ""
        },
        order: [[0, 'desc']],
        paging: true,
        ordering: true,
        searching: true,        
        columns: [
            {data: "id"},
            {data: "cliente"},
            {data: "producto"},
            {data: "id"},
        ],
        columnDefs: [
            {
            
                targets: [-2],
                class: 'text-left',
                orderable: false,
                render: function (data, type, row) {
                    var html = "";
                        $.each(row.producto, function (position,item) {
                 
                            html += '<div class="form-check form-check-inline">';
                            html += '<input class="form-check-input" type="checkbox" data-position="' + position + '" name="permit"' + 'checked' + '>';
                            html += '<label class="form-check-label">' + item.denominacion + '</label>';
                            html += '</div>';
                        });
                        return html;
                }
            },
            {
            
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = ''
                    buttons += '<a href="/bascula/clienteproducto/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat" data-toggle="tooltip" title="Editar Cliente Producto"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a href="/bascula/clienteproducto/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat" data-toggle="tooltip" title="Eliminar Cliente Producto"><i class="fas fa-trash"></i></a> ';                    
                    return buttons;
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });
}


$(function () {  
    
    
  
        initTable();
        getData(false);


});
