
function get_graph_1_1(args) {
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'producto'  : args[7],
            'sucursal'  : args[5],
            'fecha'     : args[2],
            'action'    : 'get_graph_1_1'
        },
        dataType: 'json',
    }).done(function (request) {
        if (!request.hasOwnProperty('error')) {
            Highcharts.chart('graph_1_1', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: '</i><span style="font-size:20px; font-weight: bold;">Vehiculos en Tránsito ' + args[2] + '</span>'
                },
                subtitle: {
                    text: args[0] + '<br> Fecha Hora Actualización: ' + args[1]
                },
                exporting: {
                    enabled: true
                },
                xAxis: {
                    categories: request.categories,
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'TOTALES'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                        '<td style="padding:0"><b>{point.y:.0f}</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    },
                    series: {
                        dataLabels: {
                            enabled: true,
                            style: {
                                fontSize: 12 + 'px'
                            }
                        }
                    }
                },
                series: request.series
            });
            return false;
        }
        message_error(request.error);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (data) {

    });
};