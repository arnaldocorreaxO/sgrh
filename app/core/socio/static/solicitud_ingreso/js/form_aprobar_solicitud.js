var fv;
var input_fec_resolucion;

document.addEventListener('DOMContentLoaded', function (e) {


    const form = document.getElementById('frmForm');
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
        fields: {
            nro_acta: {
                validators: {
                    notEmpty: {
                        message: 'Nro. de Acta es obligatorio'
                    },
                }
            },
            nro_socio: {
                validators: {
                    notEmpty: {
                        message: 'Nro. de Socio es obligatorio'
                    },
                    remote: {
                        url: pathname,
                        data: function () {
                            return {
                                obj: form.querySelector('[name="nro_socio"]').value,
                                type: 'nro_socio',
                                action: 'validate_data'
                            };
                        },
                        message: 'El Nro. de Socio ya se encuentra registrado',
                        method: 'POST'
                    },
                    callback: {
                        message: 'Nro. de Socio es obligatorio',
                        callback: function (input) {
                            return nro_socio.val() > 0;
                        }
                    }
                }
            },
            motivo_rechazo: {
                validators: {
                    callback: {
                        message: 'Debe indicar un motivo de rechazo',
                        callback: function (input) {
                            value = form.querySelector('[name="motivo_rechazo"]').value
                            if (aprobado.val() == 'false') {
                                return value.trim().length > 0
                            }
                            return true
                        }
                    }
                }
            },
            autorizado_por: {
                validators: {
                    notEmpty: {
                        message: 'Autorizado por es obligatorio'
                    },
                }
            },
            fec_resolucion: {
                validators: {
                    notEmpty: {
                        message: 'La fecha es obligatoria'
                    },
                    date: {
                        format: 'DD/MM/YYYY',
                        message: 'La fecha no es válida'
                    }
                }
            },
        },
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
                '¿Procesar Solicitud de Ingreso de Socio?',
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




$(function () {

    nro_socio = $('input[name="nro_socio"]');
    aprobado = $('select[name="aprobado"]');
    $('#id_motivo_rechazo').hide();

    input_fec_resolucion = $('input[name="fec_resolucion"]');
    input_fec_resolucion.datetimepicker({
        format: 'DD/MM/YYYY',
        locale: 'es',
        keepOpen: false,
        date: new moment().format("YYYY-MM-DD")
    });

    input_fec_resolucion.on('change.datetimepicker', function () {
        fv.revalidateField('fec_resolucion');
    });



    // MOTIVO RECHAZO
    aprobado.on("change", function () {
        $('#id_motivo_rechazo').hide()
        if ($(this).val() == 'false') {
            $('#id_motivo_rechazo').show()
        };

    });
});