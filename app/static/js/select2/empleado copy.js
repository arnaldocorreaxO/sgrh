$(function () {
  // 1. Definir los selectores
  var select_sucursal = $('select[name="Sucursal"]'); // Nombre según tu FormChoiceField
  var select_empleado = $('select[name="empleado"]');
  var token = $('input[name="csrfmiddlewaretoken"]');

  // 2. Inicializar Select2 para Empleado con AJAX
  select_empleado.select2({
    theme: "bootstrap4",
    language: "es",
    allowClear: true,
    placeholder: "(Seleccione un empleado)",
    ajax: {
      delay: 250,
      type: "POST",
      url: window.location.pathname,
      headers: { "X-CSRFToken": token.val() },
      data: function (params) {
        return {
          term: params.term,
          action: "search_empleado",
          sucursal_id: select_sucursal.val(), // <-- Enviamos la sucursal seleccionada
        };
      },
      processResults: function (data) {
        return { results: data };
      },
    },
    minimumInputLength: 0, // Permite ver resultados al hacer clic
  });

  // 3. Evento cuando cambia la Sucursal
  select_sucursal.on("change", function () {
    // Al cambiar la sucursal, limpiamos el empleado seleccionado
    select_empleado.val(null).trigger("change");

    // Opcional: Si quieres cargar los empleados inmediatamente al cambiar sucursal
    // sin esperar a que el usuario escriba, podemos forzar un refresco.
    if ($(this).val() === "") {
      // Si no hay sucursal, podrías deshabilitar el select de empleados
      // select_empleado.prop('disabled', true);
    } else {
      // select_empleado.prop('disabled', false);
    }
  });
});

// /*
// ===================================================================
// Autor: xO
// Descripción: Inicialización de Select2 y búsqueda dinámica de empleados
// ===================================================================
// */

// $(function () {
//   // Inicialización general de Select2 para todos los elementos con la clase .select2 en la plantilla base base.html

//   // Inicialización específica: SELECT2 para Empleado
//   const select2Empleado = $('select[name="empleado"]');

//   select2Empleado.select2({
//     theme: "bootstrap4",
//     language: "es",
//     placeholder: "(Seleccione un empleado)",
//     minimumInputLength: 1,
//     // allowClear: true, // Activar si se desea permitir limpiar selección

//     ajax: {
//       url: "/rrhh/empleado/add/",
//       type: "POST",
//       delay: 250,
//       headers: {
//         "X-CSRFToken": csrftoken,
//       },
//       data: function (params) {
//         return {
//           sucursal: $('select[name="sucursal"]').val(), // Obtener el valor seleccionado de Sucursal
//           term: params.term,
//           action: "search_empleado",
//         };
//       },
//       processResults: function (data) {
//         return {
//           results: data,
//         };
//       },
//     },
//   });
// });
