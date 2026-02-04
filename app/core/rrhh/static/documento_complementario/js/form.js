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
        validators: {
          notEmpty: { message: "Debe seleccionar un empleado" },
        },
      },
      fecha_documento: {
        validators: {
          notEmpty: { message: "Debe indicar la fecha del documento" },
          date: {
            format: "YYYY-MM-DD",
            message: "La fecha no es válida",
          },
          callback: {
            message: "La fecha no puede ser posterior a la fecha actual",
            callback: function (input) {
              if (input.value === "") return true;

              const fechaInput = new Date(input.value);
              const hoy = new Date();

              // Seteamos la hora de "hoy" a las 00:00:00 para comparar solo fechas
              hoy.setHours(0, 0, 0, 0);

              return fechaInput <= hoy;
            },
          },
        },
      },
      tipo_documento: {
        validators: {
          notEmpty: { message: "Debe seleccionar el tipo de documento" },
        },
      },
      estado_documento_empleado: {
        validators: {
          notEmpty: { message: "Debe seleccionar el estado del documento" },
        },
      },
      descripcion: {
        validators: {
          stringLength: {
            max: 255,
            message: "La descripción no puede exceder los 255 caracteres",
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

  // // Inicializar Flatpickr en el campo de fecha
  // flatpickr('input[name="fecha_documento"]', {
  //   locale: "es",
  //   dateFormat: "Y-m-d", //Como se guarda el valor en la base de datos
  //   altInput: true, // Crea un campo visual mas amigable
  //   altFormat: "d/m/Y", //Como se muestra al usuario
  //   maxDate: "today",
  //   disableMobile: "true", // Siempre usar la version de escritorio
  //   allowInput: true, // Permitir escribir manualmente
  //   onChange: function (selectedDates, dateStr, instance) {
  //     // Revalidar el campo cuando la fecha cambie
  //     fv.revalidateField("fecha_documento");
  //   },
  // });
});
