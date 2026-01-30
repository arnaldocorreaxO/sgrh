var fv;

document.addEventListener("DOMContentLoaded", function (e) {
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
      empleado: {
        validators: { notEmpty: { message: "Debe seleccionar un empleado" } },
      },
      empresa: {
        validators: { notEmpty: { message: "Debe seleccionar la empresa" } },
      },
      cargo: {
        validators: { notEmpty: { message: "Debe seleccionar el cargo" } },
      },
      fecha_desde: {
        validators: {
          notEmpty: { message: "Fecha de inicio requerida" },
          date: { format: "YYYY-MM-DD", message: "Formato inválido" },
          callback: {
            message: "No puede ser mayor a la fecha hasta",
            callback: function (input) {
              const fHasta = document.querySelector(
                '[name="fecha_hasta"]',
              ).value;
              if (!fHasta || !input.value) return true;
              return new Date(input.value) <= new Date(fHasta);
            },
          },
        },
      },
      fecha_hasta: {
        validators: {
          // No es estrictamente obligatorio en el modelo (null=True),
          // pero si decides pedirlo, añade notEmpty aquí.
          date: { format: "YYYY-MM-DD", message: "Formato inválido" },
          callback: {
            message: "No puede ser menor a la fecha desde",
            callback: function (input) {
              const fDesde = document.querySelector(
                '[name="fecha_desde"]',
              ).value;
              if (!fDesde || !input.value) return true;
              return new Date(input.value) >= new Date(fDesde);
            },
          },
        },
      },
      motivo_retiro: {
        validators: {
          stringLength: { max: 255, message: "Máximo 255 caracteres" },
        },
      },
      archivo_pdf: {
        validators: {
          file: {
            extension: "pdf",
            type: "application/pdf",
            maxSize: 5 * 1024 * 1024,
            message: "Solo se permite PDF de hasta 5MB",
          },
        },
      },
    },
  }).on("core.form.valid", function () {
    submit_formdata_with_ajax_form(fv);
  });
});
$(document).ready(function () {
  // --- REGLA DE ORO PARA SELECT2 Y FORMVALIDATION ---
  // Revalidar el campo cuando Select2 cambie su valor
  $(".select2").on("select2:select", function (e) {
    let fieldName = $(this).attr("name");
    if (fv) {
      fv.revalidateField(fieldName);
    }
  });
  $('input[name="archivo_pdf"]').on("change", function () {
    fv.revalidateField("archivo_pdf");
  });
});
