var fv;

document.addEventListener("DOMContentLoaded", function (e) {
  const form = document.getElementById("frmForm");

  // Extraer si el archivo es obligatorio (puedes pasar esto desde Django)
  // O verificar si existe el link de "Ver archivo actual" en el DOM
  const tieneArchivo = document.querySelector('a[href*=".pdf"]') !== null;

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
      institucion: {
        validators: {
          notEmpty: { message: "Debe seleccionar una institución" },
        },
      },
      nombre_capacitacion: {
        validators: {
          notEmpty: {
            message: "Debe indicar el nombre del curso / capacitación",
          },
        },
      },
      tipo_certificacion: {
        validators: {
          notEmpty: { message: "Debe seleccionar un tipo de certificación" },
        },
      },
      fecha_inicio: {
        validators: {
          notEmpty: { message: "Debe indicar la fecha de inicio" },
          date: {
            format: "YYYY-MM-DD",
            message: "La fecha no es válida",
          },
          callback: {
            message: "La fecha de inicio no puede ser mayor a la de fin",
            callback: function (input) {
              const fechaFin = form.querySelector('[name="fecha_fin"]').value;
              if (fechaFin === "" || input.value === "") {
                return true;
              }
              return new Date(input.value) <= new Date(fechaFin);
            },
          },
        },
      },
      fecha_fin: {
        validators: {
          notEmpty: { message: "Debe indicar la fecha de finalización" },
          date: {
            format: "YYYY-MM-DD",
            message: "La fecha no es válida",
          },
          callback: {
            message:
              "La fecha de finalización no puede ser menor a la de inicio",
            callback: function (input) {
              const fechaInicio = form.querySelector(
                '[name="fecha_inicio"]',
              ).value;
              if (fechaInicio === "" || input.value === "") {
                return true;
              }
              return new Date(input.value) >= new Date(fechaInicio);
            },
          },
        },
      },
      observaciones: {
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
          // Solo obligatorio si no hay un archivo previo cargado
          notEmpty: {
            enabled: !tieneArchivo,
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
