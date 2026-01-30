var fv;

document.addEventListener("DOMContentLoaded", function () {
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
        validators: { notEmpty: { message: "Debe seleccionar un empleado" } },
      },
      tipo_falta: {
        validators: { notEmpty: { message: "Seleccione el tipo de falta" } },
      },
      tipo_sancion: {
        validators: { notEmpty: { message: "Seleccione el tipo de sanción" } },
      },
      tipo_documento: {
        validators: {
          notEmpty: { message: "Seleccione el tipo de documento" },
        },
      },
      fecha_emision: {
        validators: {
          notEmpty: { message: "Indique la fecha de emisión" },
          date: { format: "YYYY-MM-DD", message: "Formato de fecha inválido" },
        },
      },
      descripcion: {
        validators: {
          stringLength: {
            max: 255,
            message: "La descripción no debe exceder los 255 caracteres",
          },
        },
      },
      institucion_emisora: {
        validators: {
          // notEmpty: { message: "Indique la Institución Emisora" },
          stringLength: { max: 150, message: "Máximo 150 caracteres" },
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
      estado_documento: {
        validators: {
          notEmpty: { message: "Seleccione el estado del documento" },
        },
      },
    },
  }).on("core.form.valid", function () {
    submit_formdata_with_ajax_form(fv);
  });
});

$(document).ready(function () {
  // Revalidar selects al cambiar con Select2
  $(".select2").on("select2:select", function (e) {
    fv.revalidateField($(this).attr("name"));
  });

  // Revalidar archivo inmediatamente al cambiar
  $('input[name="archivo_pdf"]').on("change", function () {
    fv.revalidateField("archivo_pdf");
  });

  // Revalidar fecha al cambiar manualmente o por picker
  $('input[name="fecha_emision"]').on("change", function () {
    fv.revalidateField("fecha_emision");
  });
});
