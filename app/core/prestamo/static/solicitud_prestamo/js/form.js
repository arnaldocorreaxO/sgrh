var fv;
var input_fec_solicitud;
var input_fec_charla;

document.addEventListener('DOMContentLoaded', function (e) {
    const form = document.getElementById('frmForm');
    const fv = FormValidation.formValidation(form, {
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
            sucursal: {
                validators: {
                    notEmpty: {
                        message: 'Sucursal es obligatorio'
                    },
                }
            },
            persona: {
                validators: {
                    notEmpty: {
                        message: 'Persona es obligatorio'
                    },
                    remote: {
                        url: pathname,
                        data: function () {
                            return {
                                obj: form.querySelector('[name="id_persona"]').value,
                                type: 'id_persona',
                                action: 'validate_data'
                            };
                        },
                        message: 'La persona ya posee una solicitud de ingreso',
                        method: 'POST'
                    },
                }
            },
            promocion: {
                validators: {
                    notEmpty: {
                        message: 'Promoción es obligatorio'
                    },

                }
            },
            fec_solicitud: {
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
                '¿Está seguro que desea realizar la siguiente operación?',
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
    input_fec_solicitud = $('input[name="fec_solicitud"]');
    input_fec_solicitud.datetimepicker({
        format: 'DD/MM/YYYY',
        locale: 'es',
        keepOpen: false,
        date: new moment().format("YYYY-MM-DD")
    });
    input_fec_charla = $('input[name="fec_charla"]');
    input_fec_charla.datetimepicker({
        format: 'DD/MM/YYYY',
        locale: 'es',
        keepOpen: false,
        date: new moment().format("YYYY-MM-DD")
    });

    input_fec_solicitud.on('change.datetimepicker', function () {
        fv.revalidateField('fec_solicitud');
    });
    input_fec_charla.on('change.datetimepicker', function () {
        fv.revalidateField('fec_charla');
    });


});






