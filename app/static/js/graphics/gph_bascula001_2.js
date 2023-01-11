
function get_graph_1_2(args) {

    var graph_1 = Highcharts.chart('graph_1_2', {
        chart: {
            type: 'pie',
            options3d: {
                enabled: true,
                alpha: 45,
                beta: 0
            }
        },
        exporting: {
            enabled: true,
        },
        title: {
            text: '</i><span style="font-size:20px; font-weight: bold;">Movimiento del Día ' + args[2] + '</span>'
        },
        subtitle: {
            text: args[0] + '<br> Fecha Hora Actualización: '+ args[1]
        },
        accessibility: {
            point: {
                valueSuffix: '%'
            }
        },
        tooltip: {
            pointFormat: 'Stock: <b>{point.y:.2f} TON</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                depth: 35,
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
    });


    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'producto'  : args[7],
            'sucursal'  : args[5],
            'fecha'     : args[2],
            'action'    : 'get_graph_1_2'
        },
        dataType: 'json',
    }).done(function (request) {
        if (!request.hasOwnProperty('error')) {
            graph_1.addSeries(request);
            return false;
        }
        message_error(request.error);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (data) {

    });
}