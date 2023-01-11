function get_graph_3(args) {
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'producto': args[7],
            'sucursal': args[5],
            'fecha': args[2],
            'action': 'get_graph_3'
        },
        dataType: 'json',
    }).done(function (request) {
        if (!request.hasOwnProperty('error')) {
            Highcharts.chart('graph_3', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: '</i><span style="font-size:20px; font-weight: bold;">Movimiento ' + args[6] + ' Mes de  ' + args[3] + ' de ' + args[4] + '</span>'
                },
                subtitle: {
                    text: args[0] + '<br> Fecha Hora Actualización: '+ args[1]
                },
                exporting: {
                    enabled: true,                
                  },
                xAxis: {
                    // categories: [
                    // 'DIA'                                 
                    // ],
                    max: request.categories.length - 1,
                    categories: request.categories,
                    crosshair: true
                },
                yAxis: {                           
                    min: request.series.min,
                    title: {
                        text: 'TOTALES'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">Día {point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                        '<td style="padding:0"><b>{point.y:.2f}</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true,

                },
                plotOptions: {
                    column: {
                        pointPadding: 0.1,
                        borderWidth: 0,
                        /**/
                        // stacking: 'normal',
                        dataLabels: {
                            enabled: true
                        }
                    },
                    // series: {
                    //     dataLabels: {
                    //         enabled: true,
                    //         format: '<b>{point.y:.2f}',
                    //         style: {
                    //             fontSize: 20 + 'px'
                    //         }
                    //     }
                    // }
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