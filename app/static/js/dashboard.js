var input_fecha;
var v_anho;
var v_usu_denom_corta;
var v_fec_hora_actual;
var v_mes_actual;
var v_anho_actual;


function load() {
    args = []
    //INPUT NO VISIBLES 
    v_usu_suc_denom_corta = $('input[name="usu_suc_denom_corta"]').val();
    v_fec_hora_actual     = $('input[name="fecha_hora_actual"]').val();    
    v_mes_actual          = $('input[name="mes_actual"]').val();
    v_anho_actual         = $('input[name="anho_actual"]').val();

    // PRODUCTO
    v_producto        = $('select[name="producto"]').val();    
    v_producto_texto  = $('select[name="producto"] option:selected').text();    

    // SUCURSAL
    v_sucursal        = $('select[name="sucursal"]').val();    
    v_sucursal_texto  = $('select[name="sucursal"] option:selected').text();    

    //NOMBRE DEL MES
    v_fecha   = $('input[name="fecha"]').val();
    v_mes     = v_fecha.substring(3,5)
    v_mes     = obtenerNombreMes(v_mes);
    v_mes     = v_mes.charAt(0).toUpperCase() + v_mes.slice(1) 

    // ANHO
    v_anho = v_fecha.substring(6)       
    
    // console.log(fecha_seleccion)
    // console.log(v_mes)
    // console.log(sel_anho)

    args.push(v_sucursal_texto); //[0]
    args.push(v_fec_hora_actual);
    args.push(v_fecha);
    args.push(v_mes);
    args.push(v_anho); 
    args.push(v_sucursal);     
    args.push(v_producto_texto); 
    args.push(v_producto); 
    
    // console.log(anho_actual);

    get_graph_1_1(args);
    get_graph_1_2(args);
    get_graph_2_1(args);
    get_graph_2_2(args);
    get_graph_3(args);
    get_graph_4(args);
    get_graph_5(args);
    get_list(args);
    
};


$(function () {

    input_fecha = $('input[name="fecha"]');
    input_fecha
        .daterangepicker({
            language: 'auto',
            singleDatePicker: true,
            startDate: new Date(),
            locale: {
                format: 'DD/MM/YYYY',
            }
        })
        .on('apply.daterangepicker', function (ev, picker) {
            load();
        });


    /*ESTABLECER LA SUCURSAL ACTUAL EN EL DASHBOARD */
    // anho_actual = $('input[name="anho_actual"]').val(); 
    input_sucursal = $('input[name="usu_sucursal"]');
    select_sucursal = $('select[name="sucursal"]');
    select_producto = $('select[name="producto"]');

    /*AL CAMBIAR LA SUCURSAL*/
    select_sucursal.on('change', function () {
        load();
    });
    /*AL CAMBIAR EL PRODUCTO*/
    select_producto.on('change', function () {
        load();
    });

    /*AMBOS METODOS FUNCIONA */
    // sucursal.val(sucursal_actual).trigger("change"); //Cambia valor y dispara el evento
    select_sucursal.val(input_sucursal.val()).change(); //Cambia valor y dispara el evento

});