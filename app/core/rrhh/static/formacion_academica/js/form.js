var fv;

// Variable para controlar la obligatoriedad en tiempo real
let pdfIsRequired = false;

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("frmForm");
  // Detectamos si existe un link al PDF (esto indica que ya hay uno cargado en el servidor)
  // Ajusta el selector si el link está en un contenedor específico
  const tieneArchivo =
    document.querySelector("a.pdf-link") !== null ||
    document.querySelector('a[href*=".pdf"]') !== null;

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
          callback: {
            message: "El archivo PDF es obligatorio para el nivel seleccionado",
            callback: function (input) {
              const value = input.value;

              // REGLA: Si el nivel exige PDF...
              if (pdfIsRequired) {
                // Si el input está vacío PERO ya existe un archivo previo, es VÁLIDO
                if (value === "" && tieneArchivo) {
                  return true;
                }
                // Si el input está vacío y NO hay archivo previo, es INVÁLIDO
                return value !== "";
              }

              // Si no es obligatorio por nivel, siempre es válido
              return true;
            },
          },
          file: {
            extension: "pdf",
            type: "application/pdf",
            maxSize: 5 * 1024 * 1024,
            message: "Debe ser un PDF de hasta 5MB",
          },
        },
      },
    },
  }).on("core.form.valid", function () {
    submit_formdata_with_ajax_form(fv);
  });
});

$(document).ready(function () {
  // 1. Escuchar el cambio del nivel académico
  $('select[name="nivel_academico"]').on("change", function () {
    let id = $(this).val();
    if (id) {
      $.ajax({
        url: pathname,
        type: "POST",
        data: {
          action: "validate_data",
          type: "check_pdf_requirement",
          id: id,
        },
        success: function (response) {
          pdfIsRequired = response.is_required;
          // Forzamos a FormValidation a re-evaluar el PDF con el nuevo valor
          fv.revalidateField("archivo_pdf");
        },
      });
    }
  });
  if (pdfIsRequired) {
    $(".label-pdf").html('Archivo PDF <span class="text-danger">*</span>');
  } else {
    $(".label-pdf").text("Archivo PDF");
  }
  // --- REGLA DE ORO PARA SELECT2 Y FORMVALIDATION ---
  // Revalidar el campo cuando Select2 cambie su valor
  $(".select2").on("select2:select", function (e) {
    let fieldName = $(this).attr("name");
    if (fv) {
      fv.revalidateField(fieldName);
    }
  });
});
