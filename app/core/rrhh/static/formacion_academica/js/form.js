var fv;

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("frmForm");

  fv = FormValidation.formValidation(form, {
    locale: "es_ES",
    localization: FormValidation.locales.es_ES,
    plugins: {
      trigger: new FormValidation.plugins.Trigger(),
      submitButton: new FormValidation.plugins.SubmitButton(),
      bootstrap: new FormValidation.plugins.Bootstrap(),
      icon: new FormValidation.plugins.Icon({
        valid: "fa fa-check",
        invalid: "fa fa-times",
        validating: "fa fa-refresh",
      }),
    },
    fields: {
      titulo: {
        validators: {
          notEmpty: { message: "El título es obligatorio" },
          stringLength: { min: 1 },
        },
      },
      denominacion_carrera: {
        validators: {
          notEmpty: { message: "La carrera es obligatoria" },
          stringLength: { min: 1 },
        },
      },
      institucion: {
        validators: {
          notEmpty: { message: "La institución es obligatoria" },
          stringLength: { min: 1 },
        },
      },
      nivel: {
        validators: {
          notEmpty: { message: "El nivel académico es obligatorio" },
        },
      },
      anio: {
        validators: {
          notEmpty: { message: "El año de graduación es obligatorio" },
          regexp: {
            regexp: /^[0-9]{4}$/,
            message: "Debe ser un año válido (4 dígitos)",
          },
        },
      },
      archivo: {
        validators: {
          notEmpty: { message: "Debe adjuntar un archivo" },
        },
      },
    },
  }).on("core.form.valid", function () {
    submit_formdata_with_ajax_form(fv);
  });
});

$(document).ready(function () {
  $(".select2").select2({
    theme: "bootstrap4",
    language: "es",
  });

  $('input[name="anio"]').keypress(function (e) {
    return validate_form_text("numbers", e, null);
  });
});
