function get_graph_5(args) {
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'producto'  : args[7],
            'sucursal'  : args[5],
            'fecha'     : args[2],
            'action'    : 'get_graph_5'
        },
        dataType: 'json',
    }).done(function (request) {
        if (!request.hasOwnProperty('error')) {
            // console.log(request.series);
            Highcharts.chart('graph_5', {
                chart: {
                    type: 'bar'
                },
                title: {
                    text: '</i><span style="font-size:20px; font-weight: bold;">Cantidad de Vehículos por Productos '  + args[2] + '</span>'
                },
                subtitle: {
                    text: args[0] + '<br> Fecha Hora Actualización:: '+ args[1]
                },
                exporting: {
                    enabled: true
                },
                xAxis: request.xAxis,
                yAxis: {
                    min: 0,
                    title: {
                        text: 'CANTIDAD DE VEHICULOS'
                    }
                },
                tooltip: {
                    headerFormat:'<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                                 '<td style="padding:0"><b>{point.y}</b></td></tr>',
                    footerFormat:'</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: { 
                        pointPadding: 0.2,
                        borderWidth: 0,
                        /**/
                        // stacking: 'normal',
                        dataLabels: {
                            enabled: true
                        }
                    },
                    series: {
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.y}',
                            style: {
                                fontSize: 14 + 'px'
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
}