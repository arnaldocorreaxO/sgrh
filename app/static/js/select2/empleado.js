// static/js/select2/empleado.js
$(document).ready(function () {
  // Definimos los nombres que pediste para el LocalStorage
  const keys = {
    sucursal: "last_sucursal",
    empleado: "last_empleado",
    empleado_text: "last_empleado_text",
  };

  var select_sucursal = $('select[name="sucursal"]');
  var select_empleado = $('select[name="empleado"]');
  var token = $('input[name="csrfmiddlewaretoken"]');

  // 1. Inicializar Sucursal
  select_sucursal.select2({
    theme: "bootstrap4",
    language: "es",
    placeholder: "(Seleccione sucursal)",
    allowClear: true,
  });

  // 2. Inicializar Empleado (AJAX)
  select_empleado.select2({
    theme: "bootstrap4",
    language: "es",
    allowClear: true,
    placeholder: "(Seleccione un empleado)",
    ajax: {
      delay: 250,
      type: "POST",
      url: "/rrhh/empleado/add/",
      headers: { "X-CSRFToken": token.val() },
      data: function (params) {
        return {
          term: params.term,
          action: "search_empleado",
          sucursal_id: select_sucursal.val(),
        };
      },
      processResults: function (data) {
        return { results: data };
      },
    },
    minimumInputLength: 0,
  });

  // 3. RESTAURACIÓN usando las nuevas llaves
  function restaurarFiltros() {
    const resSuc = localStorage.getItem(keys.sucursal);
    const resEmpId = localStorage.getItem(keys.empleado);
    const resEmpText = localStorage.getItem(keys.empleado_text);

    if (resSuc) {
      select_sucursal.val(resSuc).trigger("change.select2");
    }

    if (resEmpId && resEmpText) {
      var newOption = new Option(resEmpText, resEmpId, true, true);
      select_empleado.append(newOption).trigger("change.select2");
    }
  }

  restaurarFiltros();

  // 4. EVENTOS DE GUARDADO
  select_sucursal.on("change", function () {
    const val = $(this).val();
    localStorage.setItem(keys.sucursal, val || "");

    // Limpiar empleado si la sucursal cambia de la guardada anteriormente
    if (val !== localStorage.getItem("temp_suc_check")) {
      select_empleado.val(null).trigger("change");
      localStorage.removeItem(keys.empleado);
      localStorage.removeItem(keys.empleado_text);
    }
    localStorage.setItem("temp_suc_check", val || "");
  });

  select_empleado.on("select2:select", function (e) {
    const data = e.params.data;
    localStorage.setItem(keys.empleado, data.id);
    localStorage.setItem(keys.empleado_text, data.text);
  });

  select_empleado.on("change", function () {
    if (!$(this).val()) {
      localStorage.removeItem(keys.empleado);
      localStorage.removeItem(keys.empleado_text);
    }
  });

  // 5. BOTÓN RESET
  $("#btnResetFiltros").on("click", function () {
    localStorage.removeItem(keys.sucursal);
    localStorage.removeItem(keys.empleado);
    localStorage.removeItem(keys.empleado_text);
    localStorage.removeItem("temp_suc_check");

    select_sucursal.val(null).trigger("change.select2");
    select_empleado.val(null).trigger("change.select2");

    if (typeof capacitacion !== "undefined") {
      capacitacion.list(false);
    }
  });
});

// $(function () {
//   // 1. Definir los selectores
//   var select_sucursal = $('select[name="sucursal"]'); // Nombre según tu FormChoiceField
//   var select_empleado = $('select[name="empleado"]');
//   var token = $('input[name="csrfmiddlewaretoken"]');

//   // 2. Inicializar Select2 para Empleado con AJAX
//   select_empleado.select2({
//     theme: "bootstrap4",
//     language: "es",
//     allowClear: true,
//     placeholder: "(Seleccione un empleado)",
//     ajax: {
//       delay: 250,
//       type: "POST",
//       url: "/rrhh/empleado/add/",
//       headers: { "X-CSRFToken": token.val() },
//       data: function (params) {
//         return {
//           term: params.term,
//           action: "search_empleado",
//           sucursal_id: select_sucursal.val(), // <-- Enviamos la sucursal seleccionada
//         };
//       },
//       processResults: function (data) {
//         return { results: data };
//       },
//     },
//     minimumInputLength: 0, // Permite ver resultados al hacer clic
//   });

//   // 3. Evento cuando cambia la Sucursal
//   select_sucursal.on("change", function () {
//     // Al cambiar la sucursal, limpiamos el empleado seleccionado
//     select_empleado.val(null).trigger("change");

//     // Opcional: Si quieres cargar los empleados inmediatamente al cambiar sucursal
//     // sin esperar a que el usuario escriba, podemos forzar un refresco.
//     if ($(this).val() === "") {
//       // Si no hay sucursal, podrías deshabilitar el select de empleados
//       // select_empleado.prop('disabled', true);
//     } else {
//       // select_empleado.prop('disabled', false);
//     }
//   });
// });

// // static/js/select2/empleado.js
// $(document).ready(function () {
//     const keys = {
//         sucursal: 'persist_capacitacion_sucursal',
//         empleado: 'persist_capacitacion_empleado'
//     };

//     // 1. Inicializar Select2 primero
//     $('.select2').select2({
//         theme: 'bootstrap4',
//         language: "es",
//         placeholder: "(Seleccione)",
//         allowClear: true
//     });

//     // 2. Función para restaurar con validación
//     function restaurarFiltros() {
//         const resSuc = localStorage.getItem(keys.sucursal);
//         const resEmp = localStorage.getItem(keys.empleado);

//         if (resSuc) {
//             $('select[name="sucursal"]').val(resSuc).trigger('change.select2');
//         }

//         if (resEmp) {
//             // Un pequeño delay ayuda si el select de empleados depende del de sucursal
//             setTimeout(function() {
//                 $('select[name="empleado"]').val(resEmp).trigger('change.select2');
//             }, 100);
//         }
//     }

//     // Ejecutar restauración
//     restaurarFiltros();

//     // 3. Guardar automáticamente al cambiar
//     $('select[name="sucursal"], select[name="empleado"]').on('change', function () {
//         const name = $(this).attr('name');
//         localStorage.setItem(keys[name], $(this).val() || "");
//     });

//     // 4. Botón Reset
//     $('#btnResetFiltros').on('click', function () {
//         localStorage.removeItem(keys.sucursal);
//         localStorage.removeItem(keys.empleado);

//         // Limpiamos visualmente
//         $('select[name="sucursal"], select[name="empleado"]').val(null).trigger('change.select2');

//         if (typeof capacitacion !== 'undefined') {
//             capacitacion.list(false);
//         }
//     });
// });
