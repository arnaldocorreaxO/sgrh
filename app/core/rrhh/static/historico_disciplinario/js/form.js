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
      tipo_documento: {
        validators: {
          notEmpty: {
            message: "Debe seleccionar un tipo de documento",
          },
        },
      },
      estado_documento: {
        validators: {
          notEmpty: {
            message: "Debe seleccionar el estado del documento",
          },
        },
      },
      descripcion: {
        validators: {
          stringLength: {
            min: 2,
            max: 255,
            message: "La descripción debe tener entre 2 y 255 caracteres",
          },
        },
      },
      archivo_pdf: {
        validators: {
          notEmpty: {
            message: "Debe subir un archivo PDF",
          },
          file: {
            extension: "pdf",
            type: "application/pdf",
            maxSize: 5 * 1024 * 1024, // 5MB
            message: "Solo se permite archivos PDF de hasta 5MB",
          },
        },
      },
    },
  })
    .on("core.element.validated", function (e) {
      if (e.valid) {
        const groupEle = FormValidation.utils.closest(e.element, ".form-group");
        if (groupEle) {
          FormValidation.utils.classSet(groupEle, {
            "has-success": false,
          });
        }
        FormValidation.utils.classSet(e.element, {
          "is-valid": false,
        });
      }
      const iconPlugin = fv.getPlugin("icon");
      const iconElement =
        iconPlugin && iconPlugin.icons.has(e.element)
          ? iconPlugin.icons.get(e.element)
          : null;
      if (iconElement) {
        iconElement.style.display = "none";
      }
    })
    .on("core.validator.validated", function (e) {
      if (!e.result.valid) {
        const messages = [].slice.call(
          form.querySelectorAll(
            '[data-field="' + e.field + '"][data-validator]'
          )
        );
        messages.forEach((messageEle) => {
          const validator = messageEle.getAttribute("data-validator");
          messageEle.style.display =
            validator === e.validator ? "block" : "none";
        });
      }
    })
    .on("core.form.valid", function () {
      submit_formdata_with_ajax_form(fv);
    });
});

$(document).ready(function () {
  $(".select2").select2({
    theme: "bootstrap4",
    language: "es",
  });

  $('input[name="archivo_pdf"]').on("change", function () {
    fv.revalidateField("archivo_pdf");
  });
});
