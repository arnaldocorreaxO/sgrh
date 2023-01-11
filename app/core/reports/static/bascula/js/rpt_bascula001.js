
var input_daterange;
var input_timerange_in;
var input_timerange_out;
// INIT LOAD
$(function () {  
    current_date = new moment().format('YYYY-MM-DD');
    input_daterange = $('input[name="date_range"]');
    input_timerange_in =  $('input[name="time_range_in"]');
    input_timerange_out =  $('input[name="time_range_out"]');
    
    // RANGO DE FECHAS
    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        })
        .on('apply.daterangepicker', function (ev, picker) {

        });

    // RANGO DE HORAS ENTRADAS
    input_timerange_in
        .daterangepicker({
            timePicker: true,
            timePicker24Hour: true,
            timePickerIncrement: 1,
            timePickerSeconds: true,
            locale: {
                format: 'HH:mm:ss'
            }
        }).on('show.daterangepicker', function (ev, picker) {
            picker.container.find(".calendar-table").hide();
        });
    // RANGO DE HORAS SALIDAS
    input_timerange_out
        .daterangepicker({
            timePicker: true,
            timePicker24Hour: true,
            timePickerIncrement: 1,
            timePickerSeconds: true,
            locale: {
                format: 'HH:mm:ss'
            }
        }).on('show.daterangepicker', function (ev, picker) {
            picker.container.find(".calendar-table").hide();
        });


         // #SUCURSAL POR DEFECTO 
    var sucursal_id = $('input[name="suc_usuario"]').val();   
    var select_sucursal = $('select[name="sucursal"]'); 
    select_sucursal.val(sucursal_id).change();
    // getData('all');
});