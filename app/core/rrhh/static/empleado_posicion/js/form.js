var fv;

document.addEventListener("DOMContentLoaded", function (e) {
  const form = document.getElementById("frmForm");

  // Verificamos si existe un archivo previamente cargado para que no sea obligatorio en la edición
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
      legajo: {
        validators: {
          notEmpty: { message: "Debe indicar el número de legajo" },
          stringLength: {
            min: 1,
            max: 4,
            message: "El legajo no puede superar los 4 caracteres",
          },
        },
      },
      dependencia_posicion: {
        validators: {
          notEmpty: { message: "Debe seleccionar la dependencia y cargo" },
        },
      },
      tipo_movimiento: {
        validators: {
          notEmpty: { message: "Debe seleccionar el tipo de movimiento" },
        },
      },
      vinculo_laboral: {
        validators: {
          notEmpty: { message: "Debe seleccionar el vínculo laboral" },
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
              if (fechaFin === "" || input.value === "") return true;

              // Comparación segura parseando YYYY-MM-DD
              const pI = input.value.split("-");
              const pF = fechaFin.split("-");
              const fI = new Date(pI[0], pI[1] - 1, pI[2]);
              const fF = new Date(pF[0], pF[1] - 1, pF[2]);
              return fI <= fF;
            },
          },
        },
      },
      fecha_fin: {
        validators: {
          // fecha_fin es opcional en el modelo (null=True), por eso no lleva notEmpty
          date: {
            format: "YYYY-MM-DD",
            message: "La fecha no es válida",
          },
          callback: {
            callback: function (input) {
              const value = input.value;
              if (!value) return true; // Es opcional

              const hoy = new Date();
              hoy.setHours(0, 0, 0, 0);

              const partesFin = value.split("-");
              const fFin = new Date(
                partesFin[0],
                partesFin[1] - 1,
                partesFin[2],
              );
              fFin.setHours(0, 0, 0, 0);

              // 1. Validar contra Hoy
              if (fFin > hoy) {
                return {
                  valid: false,
                  message:
                    "La fecha de finalización no puede superar la fecha actual",
                };
              }

              // 2. Validar contra Fecha de Inicio
              const fechaInicio = form.querySelector(
                '[name="fecha_inicio"]',
              ).value;
              if (fechaInicio !== "") {
                const partesInicio = fechaInicio.split("-");
                const fInicio = new Date(
                  partesInicio[0],
                  partesInicio[1] - 1,
                  partesInicio[2],
                );
                fInicio.setHours(0, 0, 0, 0);

                if (fFin < fInicio) {
                  return {
                    valid: false,
                    message:
                      "La fecha de fin no puede ser anterior a la de inicio",
                  };
                }
              }
              return true;
            },
          },
        },
      },
      archivo_pdf: {
        validators: {
          notEmpty: {
            enabled: !tieneArchivo,
            message: "Debe subir el PDF de la resolución/contrato",
          },
          file: {
            extension: "pdf",
            type: "application/pdf",
            maxSize: 5 * 1024 * 1024, // 5MB
            message: "Solo se permiten archivos PDF de hasta 5MB",
          },
        },
      },
    },
  }).on("core.form.valid", function () {
    submit_formdata_with_ajax_form(fv);
  });
});

$(document).ready(function () {
  // Revalidar campos de Select2
  $(".select2").on("select2:select", function (e) {
    let fieldName = $(this).attr("name");
    if (fv) fv.revalidateField(fieldName);
  });

  // Disparar validación cruzada al cambiar fecha_inicio
  $('input[name="fecha_inicio"]').on("change", function () {
    if (fv) fv.revalidateField("fecha_fin");
  });

  $('input[name="archivo_pdf"]').on("change", function () {
    if (fv) fv.revalidateField("archivo_pdf");
  });
});
