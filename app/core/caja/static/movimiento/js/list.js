var tblPurchase;
var input_daterange;

function getData(all) {
    var parameters = {
        'action': 'search',
        'start_date': input_daterange.data('daterangepicker').startDate.format('YYYY-MM-DD'),
        'end_date': input_daterange.data('daterangepicker').endDate.format('YYYY-MM-DD'),
    };

    if (all) {
        parameters['start_date'] = '';
        parameters['end_date'] = '';
    }

    tblPurchase = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        columns: [
            { data: "fec_movimiento" },
            { data: "cod_movimiento" },
            { data: "cliente__cod_cliente" },
            { data: "cliente__persona__nombre" },
            { data: "cliente__persona__apellido" },
            { data: "usu_insercion__cod_usuario" },
            { data: "importe" },
            { data: "usu_insercion__cod_usuario" },
        ],
        columnDefs: [
            {
                targets: [0],
                class: 'text-left',
                render: function (data, type, row) {
                    return formatoFecha(data, "/")
                }
            },
            {
                targets: [-2],
                class: 'text-right',
                render: function (data, type, row) {
                    return 'G. ' + formatoNumero(data)
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    var btnClass = "btn btn-secondary btn-flat"
                    var buttons = '';
                    buttons += '<a href="/caja/movimiento/print/'
                        + formatoFecha(row.fec_movimiento, "-") + '/' + row.cod_movimiento + '/'
                        + row.cliente__cod_cliente + '/' + row.usu_insercion__cod_usuario + '/'
                        + '" id="btnPrint" target="_blank"  class="' + btnClass + '" data-toggle="tooltip" title="Imprimir Comprobante"><i class="fas fa-print"></i></a>';

                    return buttons;
                }
            },
        ],
        rowCallback: function (row, data, index) {

        },
        initComplete: function (settings, json) {
            $('[data-toggle="tooltip"]').tooltip();
        }
    });
}

$(function () {

    input_daterange = $('input[name="date_range"]');

    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        });

    $('.drp-buttons').hide();

    getData(false);

    $('.btnSearch').on('click', function () {
        getData(false);
    });

    $('.btnSearchAll').on('click', function () {
        getData(true);
    });

});