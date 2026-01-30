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
      empleado: {
        validators: {
          notEmpty: { message: "Debe seleccionar un empleado" },
        },
      },
      nivel_academico: {
        validators: {
          notEmpty: { message: "Debe seleccionar el nivel académico" },
        },
      },
      institucion: {
        validators: {
          notEmpty: { message: "Debe seleccionar una institución" },
        },
      },
      titulo_obtenido: {
        validators: {
          notEmpty: { message: "Debe seleccionar el título obtenido" },
        },
      },
      denominacion_carrera: {
        validators: {
          notEmpty: { message: "Debe indicar el nombre de la carrera" },
          stringLength: {
            min: 3,
            max: 150,
            message: "La carrera debe tener entre 3 y 150 caracteres",
          },
        },
      },
      anho_graduacion: {
        validators: {
          notEmpty: { message: "Debe seleccionar el año de graduación" },
          digits: { message: "El año debe contener solo números" },
        },
      },
      archivo_pdf: {
        validators: {
          // notEmpty eliminado porque es opcional
          file: {
            extension: "pdf",
            type: "application/pdf",
            maxSize: 5 * 1024 * 1024, // 5MB
            message: "Si sube un archivo, debe ser PDF de hasta 5MB",
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
});
