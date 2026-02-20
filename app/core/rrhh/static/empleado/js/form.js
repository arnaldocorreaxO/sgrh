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
                type: "ci",
                action: "validate_data",
              };
            },
            message: "El numero de cedula ya se encuentra registrado",
            method: "POST",
          },
        },
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
                type: "ruc",
                action: "validate_data",
              };
            },
            message: "El numero de RUC ya se encuentra registrado",
            method: "POST",
          },
        },
      },
      nombre: {
        validators: {
          notEmpty: { message: "El nombre es obligatorio" },
          stringLength: {
            min: 2,
          },
        },
      },
      apellido: {
        validators: {
          notEmpty: { message: "El apellido es obligatorio" },
          stringLength: {
            min: 2,
          },
        },
      },

      celular: {
        validators: {
          notEmpty: {
            message: "El número de celular es obligatorio",
          },
          stringLength: {
            min: 10,
            max: 10,
            message: "El número debe tener exactamente 10 dígitos",
          },
          regexp: {
            regexp: /^[0-9]{10}$/,
            message: "Solo se permiten números (10 dígitos)",
          },
        },
      },

      sexo: {
        validators: {
          notEmpty: { message: "El campo sexo es obligatorio" },
          stringLength: {
            min: 1,
          },
          // digits: {},
        },
      },
      nacionalidad: {
        validators: {
          notEmpty: { message: "La nacionalidad es obligatorio" },
          stringLength: {
            min: 1,
          },
          // digits: {},
        },
      },
      estado_civil: {
        validators: {
          notEmpty: { message: "El estado civil es obligatorio" },
          stringLength: {
            min: 1,
          },
          //   digits: {},
        },
      },
      email: {
        validators: {
          notEmpty: { message: "El correo electrónico es obligatorio" },
          stringLength: {
            min: 5,
          },
          regexp: {
            regexp: /^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$/i,
            message: "El formato email no es correcto",
          },
        },
      },
      ciudad: {
        validators: {
          notEmpty: { message: "La ciudad es obligatoria" },
          stringLength: {
            min: 1,
          },
        },
      },
      // Campos de Selección (Select2)
      sucursal: {
        validators: { notEmpty: { message: "Seleccione una sucursal" } },
      },
      nacionalidad: {
        validators: { notEmpty: { message: "La nacionalidad es obligatoria" } },
      },
      ciudad: {
        validators: { notEmpty: { message: "La ciudad es obligatoria" } },
      },
      sexo: {
        validators: { notEmpty: { message: "El campo sexo es obligatorio" } },
      },
      estado_civil: {
        validators: { notEmpty: { message: "El estado civil es obligatorio" } },
      },
      direccion: {
        validators: {
          notEmpty: { message: "La dirección es obligatoria" },
          stringLength: {
            min: 2,
          },
        },
      },
      fecha_vencimiento_ci: {
        validators: {
          notEmpty: {
            message: "La fecha de vencimiento de la CI es obligatoria",
          },
          date: {
            format: "YYYY-MM-DD", // El estándar de los navegadores para inputs de tipo fecha
            message: "La fecha no es válida",
          },
          callback: {
            message: "La cédula no puede estar vencida",
            callback: function (input) {
              const value = input.value;
              if (!value) return true;

              // Formato esperado: YYYY-MM-DD
              const partes = value.split("-");
              if (partes.length !== 3) return false;

              // Crear fecha local (año, mes-1, día) para evitar problemas de zona horaria
              const fechaVencimiento = new Date(
                partes[0],
                partes[1] - 1,
                partes[2],
              );

              const hoy = new Date();
              hoy.setHours(0, 0, 0, 0);

              return fechaVencimiento >= hoy;
            },
          },
        },
      },
      fecha_nacimiento: {
        validators: {
          notEmpty: {
            message: "La fecha es obligatoria",
          },
          date: {
            format: "YYYY-MM-DD", // El estándar de los navegadores para inputs de tipo fecha
            message: "La fecha no es válida",
          },
          remote: {
            url: pathname,
            data: function () {
              return {
                obj: form.querySelector('[name="fecha_nacimiento"]').value,
                type: "fecha_nacimiento",
                action: "validate_data",
              };
            },
            message: "La fecha de nacimiento no corresponde a un mayor de edad",
            method: "POST",
          },
        },
      },
      archivo_pdf_ci: {
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
      fecha_ingreso: {
        validators: {
          notEmpty: {
            message: "La fecha de ingreso es obligatoria",
          },
          date: {
            format: "YYYY-MM-DD", // El estándar de los navegadores para inputs de tipo fecha
            message: "La fecha no es válida",
          },
        },
      },
      fecha_egreso: {
        validators: {
          date: {
            format: "YYYY-MM-DD", // El estándar de los navegadores para inputs de tipo fecha
            message: "La fecha no es válida",
          },
          callback: {
            message:
              "La fecha de egreso no puede ser anterior a la fecha de ingreso",
            callback: function (input) {
              const value = input.value;
              if (!value) return true;

              const partes = value.split("-");
              if (partes.length !== 3) return false;

              const fechaEgreso = new Date(partes[0], partes[1] - 1, partes[2]);
              const fechaIngresoInput = form.querySelector(
                '[name="fecha_ingreso"]',
              );
              const fechaIngresoValue = fechaIngresoInput
                ? fechaIngresoInput.value
                : null;

              if (!fechaIngresoValue) return true;

              const partesIngreso = fechaIngresoValue.split("-");
              if (partesIngreso.length !== 3) return false;

              const fechaIngreso = new Date(
                partesIngreso[0],
                partesIngreso[1] - 1,
                partesIngreso[2],
              );

              return fechaEgreso >= fechaIngreso;
            },
          },
        },
      },
    },
  }).on("core.form.valid", function () {
    submit_formdata_with_ajax_form(fv);
  });
});

$(document).ready(function () {
  $('input[name="celular"]').keypress(function (e) {
    return validate_form_text("numbers", e, null);
  });

  $("#btnVerificar").click(function () {
    var vCi = $("#id_ci").val();
    // console.log(vCi);
    $("#id_ruc").val("");
    $("#id_nombre").val("");
    $("#id_apellido").val("");
    $("#id_direccion").val("");
    $("#id_nacionalidad").val("");
    $("#fecha_nacimiento").val("");
    $("#id_estado_civil").val("");
    $.ajax({
      url: "/base/persona/get_datos_persona",
      data: {
        ci: vCi,
      },
      success: function (data) {
        $("#id_ruc").val(data[0].per_ruc);
        $("#id_nombre").val(data[0].per_nombres);
        $("#id_apellido").val(data[0].per_apynom);
        $("#id_direccion").val(data[0].per_desdomi);
        $("#id_nacionalidad").val(data[0].per_codpais).trigger("change");
        $("#id_fecha_nacimiento").val(data[0].per_fchnaci).trigger("change");
        $("#id_estado_civil").val(data[0].civ_codeciv).trigger("change");
      },
    });
  });

  // --- REGLA DE ORO PARA SELECT2 Y FORMVALIDATION ---
  // Revalidar el campo cuando Select2 cambie su valor
  $(".select2").on("select2:select", function (e) {
    let fieldName = $(this).attr("name");
    if (fv) {
      fv.revalidateField(fieldName);
    }
  });

  $('input[name="ci_archivo_pdf"]').on("change", function () {
    fv.revalidateField("ci_archivo_pdf");
  });
});
