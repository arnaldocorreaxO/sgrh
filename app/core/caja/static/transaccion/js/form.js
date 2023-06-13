var tblTransacciones;

var input_fec_movimiento;
var input_cod_movimiento;
var input_nro_recibo
var input_nro_factura;
var input_socio_id;
var data_url = '';
var data_parameters = {};
var select_transaccion;
var trx;


transaccion = {
    // parameters: {
    //     action: 'search_trx',
    //     cod_movimiento: input_cod_movimiento,
    // },
    details: {
        provider: '',
        date_joined: '',
        end_credit: '',
        subtotal: 0.00,
        iva: 0.00,
        dscto: 0.00,
        total: 0.00,
        payment_condition: 0,
        rows: [],
    },
    calculate_total: function () {
        var total = 0.00;
        $.each(this.details.rows, function (i, item) {
            item.pos = i;
            total += item.importe;
            // console.log(total)
        });
        $('input[name="total"]').val(formatoNumero(total));
    },
    list_transacciones: function () {
        /*Reseteamos detalle antes de cada llamada*/
        this.details.rows = []

        var parameters = {
            action: 'list_trx',
            fec_movimiento: data_parameters['fec_movimiento'],
            cod_movimiento: data_parameters['cod_movimiento']

        };
        console.log(parameters)
        tblTransacciones = $('#tblTransacciones').DataTable({
            //responsive: true,
            //autoWidth: false,
            destroy: true,
            // data: this.details.products,
            ordering: false,
            lengthChange: false,
            searching: false,
            paginate: false,
            scrollX: true,
            scrollCollapse: true,
            ajax: {
                url: pathname,
                type: 'POST',
                data: parameters,
                //Sin este da error de length
                dataSrc: ""
            },
            columns: [
                { data: "id" },
                { data: "cod_transaccion" },
                { data: "abr_transaccion" },
                { data: "iso_moneda" },
                { data: "importe" },
                // { data: "importe" },
            ],
            columnDefs: [
                // {
                //     targets: [-3],
                //     class: 'text-center',
                //     render: function (data, type, row) {
                //         return '<input type="text" class="form-control input-sm" style="width: 100px;" autocomplete="off" name="cant" value="' + row.cant + '">';
                //     }
                // },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {

                        return formatoNumero(data);
                    }
                },
                {
                    targets: [0],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-flat btn-xs"><i class="fa fa-trash fa-1x"></i></a>';
                    }
                },
            ],
            rowCallback: function (row, data, index) {
                transaccion.add_transaccion(data);
                return true;

            },
            initComplete: function (settings, json) {
                transaccion.calculate_total();
            },
        });
    },
    // get_products_ids: function () {
    //     var ids = [];
    //     $.each(this.details.products, function (i, item) {
    //         ids.push(item.id);
    //     });
    //     return ids;
    // },

    add_transaccion: function (item) {
        this.details.rows.push(item);
    },
    del_transaccion: function (row) {
        console.log(row)
        item = transaccion.details.rows[row]
        console.log(item)
        item.action = 'del_trx';

        // $.ajax({
        //     url: pathname,
        //     type: 'POST',
        //     data: item,
        // }).done(function (response) {
        //transaccion.details.rows.splice(row, 1);
        // });

        console.log(item);
    },
};



$(function () {
    // inputCredit = $('.inputCredit');
    // current_date = new moment().format("YYYY-MM-DD");
    // input_datejoined = $('input[name="date_joined"]');
    // input_endcredit = $('input[name="end_credit"]');
    // select_cliente = $('select[name="provider"]');
    // input_searchproducts = $('input[name="searchproducts"]');
    // select_paymentcondition = $('select[name="payment_condition"]');

    // PARAMETROS COMUNES PARA TODAS LAS TRANSACCIONES 
    input_fec_movimiento = $('#fec_movimiento');
    input_cod_movimiento = $('#id_cod_movimiento');
    input_nro_recibo = $('#id_nro_recibo');
    input_nro_factura = $('#id_nro_factura');
    input_socio_id = $('#id_socio');
    select_transaccion = $('#id_transaccion');

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    $('#tblTransacciones tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblTransacciones.cell($(this).closest('td, li')).index();
            transaccion.del_transaccion(tr.row);
        });


    $('#formModal').on('shown.bs.modal', function () {
        transaccion.list_transacciones();
    });



    /*VALORES COMUNES PARA TODAS LAS TRANSACCIONES */
    data_parameters['fec_movimiento'] = input_fec_movimiento.val();
    data_parameters['cod_movimiento'] = input_cod_movimiento.val();


    /*SELECCON DE TRANSACCIONES*/

    select_transaccion.on('change', function () {

        /*INICIALIZAMOS VALORES*/
        data_url = "#"
        data_parameters = {};
        /*Por ahora enviamos de nuevo todos los parametros */
        data_parameters['action'] = 'search'
        data_parameters['fec_movimiento'] = input_fec_movimiento.val();
        data_parameters['cod_movimiento'] = input_cod_movimiento.val();
        data_parameters['nro_recibo'] = input_nro_recibo.val();
        data_parameters['nro_factura'] = input_nro_factura.val();
        data_parameters['socio_id'] = input_socio_id.val();

        trx = $(this).val();
        switch (trx) {

            case '700':
                data_url = "/caja/trx700/add/"
                break;
            case '701':
                data_url = "/caja/trx701/add/"
                break;
            case '702':
                data_url = "/caja/trx702/add/"
                break;
        }

        if (data_parameters.length !== 0) {
            console.log(data_parameters.length);
            $(this).val('').focus();
            $('#btnTRX').attr("data-url", data_url)
            $('#btnTRX').attr("data-parameters", data_parameters)
            $('#btnTRX').trigger("click");
        };
    });
    /*FIN SELECCION DE TRANSACCIONES*/


    /*SECCION MODALES*/
    var loadForm = function () {
        var btn = $(this);
        // console.log(data_parameters);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'POST',
            dataType: 'json',
            data: data_parameters,
            // data: {
            //     action: 'search',
            //     socio_id: 63
            // },
            beforeSend: function () {
                $("#modal-transaccion").modal("show");
            },
            success: function (response) {
                if (!response.hasOwnProperty('error')) {
                    $("#modal-transaccion .modal-content").html(response.html_form);
                    setear_valores_form_modales(response.data)
                    return false;
                }
                message_error(response.error);
            }
        });
    };

    var saveForm = function () {
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (request) {
                if (!request.hasOwnProperty('error')) {
                    if (request.rtn != 0) {
                        message_warning(request.msg);
                        return false;
                    }
                    $("#modal-transaccion").modal("hide");
                    transaccion.list_transacciones();
                    return false;
                }
                message_error(request.error);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                message_error(errorThrown + ' ' + textStatus);
            }
        });
        return false;
    };

    /*LIMPIAR MODAL*/
    $(".modal").on("hidden.bs.modal", function () {
        $(".modal-content").html("");
    });

    $('#btnTRX').click(loadForm);
    $("#modal-transaccion").on("submit", ".js-transaccion-form", saveForm);
    /*FIN SECCION MODALES*/



    /**/
    function setear_valores_form_modales(data) {
        /******************************************************
         * Setea los valores tipo json retornados por ajax
         * para aplicar a campos del formulario modal segun trx
        ******************************************************/

        /*VARIABLES COMUNES PARA LOS MODALS */
        var m_input_fec_movimiento = $('#frmModal #id_fec_movimiento');
        var m_input_cod_movimiento = $('#frmModal #id_cod_movimiento');
        var m_input_nro_documento = $('#frmModal #id_nro_documento');
        var m_input_socio_id = $('#frmModal #id_socio');

        m_input_fec_movimiento.val(data_parameters['fec_movimiento']);
        m_input_cod_movimiento.val(data_parameters['cod_movimiento']);
        m_input_nro_documento.val(data_parameters['nro_recibo']);
        m_input_socio_id.val(data_parameters['socio_id']);
        /*FIN PARAMETROS COMUNES PARA LAS TRANSACCIONES*/
        console.log('**************')
        console.log(trx)
        switch (trx) {
            case '700':
                /*TRX 700 VARIABLES LOCALES*/
                var m_select_promocion = $('#frmModal #id_promocion');
                var m_input_aporte_ingreso = $('#frmModal #id_aporte_ingreso');
                var m_input_aporte_social = $('#frmModal #id_aporte');
                var m_input_aporte_solidaridad = $('#frmModal #id_solidaridad');
                var m_input_gastos_administrativos = $('#frmModal #id_gastos');
                var m_input_total = $('#frmModal #id_total');
                var m_total = 0

                console.log(data);

                m_select_promocion.val(data['id']).change();
                m_input_aporte_ingreso.val(data['mto_ini_aporte_ingreso']);
                m_input_aporte_social.val(data['mto_ini_aporte_social']);
                m_input_aporte_solidaridad.val(data['mto_ini_aporte_solidaridad']);
                m_input_gastos_administrativos.val(data['mto_ini_gastos_administrativos']);
                /* TOTAL */
                m_total = parseFloat(m_input_aporte_ingreso.val()) + parseFloat(m_input_aporte_social.val())
                    + parseFloat(m_input_aporte_solidaridad.val()) + parseFloat(m_input_gastos_administrativos.val())
                m_input_total.val(m_total)

                /*FIN TRX 700 */
                break;

            case '701':
                /*TRX 701 VARIABLES LOCALES*/
                var m_input_aporte_efectivo = $('#frmModal #id_aporte_efectivo');
                m_input_aporte_efectivo.val(data['val']);
                /*FIN TRX 701 */
                break;

            case '702':
                /*TRX 702 VARIABLES LOCALES*/
                var m_input_solidaridad_efectivo = $('#frmModal #id_solidaridad_efectivo');
                m_input_solidaridad_efectivo.val(data['val']);
                /*FIN TRX 702 */
                break;
        }


    };

    transaccion.list_transacciones();

});




//SUBMIT FORMULARIO PRINCIPAL CAJA TRANSACCION

document.addEventListener('DOMContentLoaded', function (e) {


    const form = document.getElementById('frmTransaccion');
    fv = FormValidation.formValidation(form, {
        locale: 'es_ES',
        localization: FormValidation.locales.es_ES,
        plugins: {
            trigger: new FormValidation.plugins.Trigger(),
            submitButton: new FormValidation.plugins.SubmitButton(),
            bootstrap: new FormValidation.plugins.Bootstrap(),
            icon: new FormValidation.plugins.Icon({
                valid: 'fa fa-check',
                invalid: 'fa fa-times',
                validating: 'fa fa-refresh',
            }),
        },
        // fields: {
        //     nro_acta: {
        //         validators: {
        //             notEmpty: {
        //                 message: 'Nro. de Acta es obligatorio'
        //             },
        //         }
        //     },
        //     nro_socio: {
        //         validators: {
        //             notEmpty: {
        //                 message: 'Nro. de Socio es obligatorio'
        //             },
        //             remote: {
        //                 url: pathname,
        //                 data: function () {
        //                     return {
        //                         obj: form.querySelector('[name="nro_socio"]').value,
        //                         type: 'nro_socio',
        //                         action: 'validate_data'
        //                     };
        //                 },
        //                 message: 'El Nro. de Socio ya se encuentra registrado',
        //                 method: 'POST'
        //             },
        //             callback: {
        //                 message: 'Nro. de Socio es obligatorio',
        //                 callback: function (input) {
        //                     return nro_socio.val() > 0;
        //                 }
        //             }
        //         }
        //     },
        //     motivo_rechazo: {
        //         validators: {
        //             callback: {
        //                 message: 'Debe indicar un motivo de rechazo',
        //                 callback: function (input) {
        //                     value = form.querySelector('[name="motivo_rechazo"]').value
        //                     if (aprobado.val() == 'false') {
        //                         return value.trim().length > 0
        //                     }
        //                     return true
        //                 }
        //             }
        //         }
        //     },
        //     autorizado_por: {
        //         validators: {
        //             notEmpty: {
        //                 message: 'Autorizado por es obligatorio'
        //             },
        //         }
        //     },
        //     fec_resolucion: {
        //         validators: {
        //             notEmpty: {
        //                 message: 'La fecha es obligatoria'
        //             },
        //             date: {
        //                 format: 'DD/MM/YYYY',
        //                 message: 'La fecha no es válida'
        //             }
        //         }
        //     },
        // },
    }
    )
        .on('core.element.validated', function (e) {
            if (e.valid) {
                const groupEle = FormValidation.utils.closest(e.element, '.form-group');
                if (groupEle) {
                    FormValidation.utils.classSet(groupEle, {
                        'has-success': false,
                    });
                }
                FormValidation.utils.classSet(e.element, {
                    'is-valid': false,
                });
            }
            const iconPlugin = fv.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            if (!e.result.valid) {
                const messages = [].slice.call(form.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
            }
        })
        .on('core.form.valid', function () {
            // submit_formdata_with_ajax_form(fv);
            var form = fv.form;
            var parameters = new FormData($(form)[0]);
            submit_formdata_with_ajax('Notificación',
                '¿Procesar Transacciones de Caja?',
                window.location.pathname,
                parameters,
                function (data) {
                    if (!data.hasOwnProperty('error')) {
                        console.log(data.val)
                        if (data.rtn != 0) {
                            message_warning(data.msg);
                            return false;
                        }
                        else {
                            alert_sweetalert('success', 'OK', "", function () {
                                location.href = form.getAttribute('data-url');
                            }, null, data.msg);
                        };
                        return false;
                    };

                });

        });
});