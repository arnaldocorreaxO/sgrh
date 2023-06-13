var fv;

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
            ci: {
                validators: {
                    notEmpty: {},
                    stringLength: {
                        min: 6,
                    },
                    remote: {
                        url: pathname,
                        data: function () {
                            return {
                                obj: form.querySelector('[name="ci"]').value,
                                type: 'ci',
                                action: 'validate_data'
                            };
                        },
                        message: 'El numero de cedula ya se encuentra registrado',
                        method: 'POST'
                    }

                }

            },
            ruc: {
                validators: {
                    notEmpty: {},
                    stringLength: {
                        min: 8,
                    },
                    remote: {
                        url: pathname,
                        data: function () {
                            return {
                                obj: form.querySelector('[name="ruc"]').value,
                                type: 'ruc',
                                action: 'validate_data'
                            };
                        },
                        message: 'El numero de RUC ya se encuentra registrado',
                        method: 'POST'
                    }

                }

            },
            nombre: {
                validators: {
                    notEmpty: {},
                    stringLength: {
                        min: 2,
                    },

                }

            },
            apellido: {
                validators: {
                    notEmpty: {},
                    stringLength: {
                        min: 2,
                    },

                }

            },

            celular: {
                validators: {
                    notEmpty: {},
                    stringLength: {
                        min: 10,
                    },
                    digits: {},
                }
            },
            // telefono: {
            //     validators: {
            //         notEmpty: {},
            //         stringLength: {
            //             min: 6,
            //         },
            //         digits: {},
            //     }
            // },
            // email: {
            //     validators: {
            //         notEmpty: {},
            //         stringLength: {
            //             min: 5
            //         },
            //         regexp: {
            //             regexp: /^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$/i,
            //             message: 'El formato email no es correcto'
            //         }
            //     }
            // },
            direccion: {
                validators: {
                    notEmpty: {},
                    stringLength: {
                        min: 2,
                    },
                }
            },
            fec_nacimiento: {
                validators: {
                    notEmpty: {
                        message: 'La fecha es obligatoria'
                    },
                    date: {
                        format: 'DD/MM/YYYY',
                        message: 'La fecha no es válida'
                    },
                    remote: {
                        url: pathname,
                        data: function () {
                            return {
                                obj: form.querySelector('[name="fec_nacimiento"]').value,
                                type: 'fec_nacimiento',
                                action: 'validate_data'
                            };
                        },
                        message: 'La fecha de nacimiento no corresponde a un mayor de edad',
                        method: 'POST'
                    },
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
            submit_formdata_with_ajax_form(fv);
        });
});




$(document).ready(function () {

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es"
    });

    $('input[name="celular"]').keypress(function (e) {
        return validate_form_text('numbers', e, null);
    });


    $('#btnVerificar').click(function () {
        var vCi = $("#id_ci").val();
        // console.log(vCi);
        $('#id_ruc').val('');
        $('#id_nombre').val('');
        $('#id_apellido').val('');
        $('#id_direccion').val('');
        $('#id_nacionalidad').val('');
        $('#fec_nacimiento').val('');
        $('#id_estado_civil').val('');
        $.ajax({
            url: '/base/persona/get_datos_persona',
            data: {
                'ci': vCi
            },
            success: function (data) {

                $('#id_ruc').val(data[0].per_ruc);
                $('#id_nombre').val(data[0].per_nombres);
                $('#id_apellido').val(data[0].per_apynom);
                $('#id_direccion').val(data[0].per_desdomi);
                $('#id_nacionalidad').val(data[0].per_codpais).trigger('change');
                $('#fec_nacimiento').val(data[0].per_fchnaci.split("-").reverse().join("/"));
                $('#id_estado_civil').val(data[0].civ_codeciv).trigger('change');
                // $('#id_nacionalidad').trigger('change.select2');
                // $('#id_estado_civil').trigger('change.select2');

            }
        });

    });


    input_fec_nacimiento = $('input[name="fec_nacimiento"]');
    input_fec_nacimiento.datetimepicker({
        format: 'DD/MM/YYYY',
        locale: 'es',
        keepOpen: false,
        date: new moment().format("YYYY-MM-DD")
    });

    input_fec_nacimiento.on('change.datetimepicker', function () {
        fv.revalidateField('fec_nacimiento');
    });
});
