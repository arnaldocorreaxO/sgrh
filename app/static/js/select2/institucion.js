/*
===================================================================
Autor: xO
Descripción: Inicialización de Select2 y búsqueda dinámica de instituciones
===================================================================
*/

$(function () {
  // Inicialización general de Select2 para todos los elementos con la clase .select2 en la plantilla base base.html

  const select2Institucion = $('select[name="institucion"]');

  select2Institucion.select2({
    theme: "bootstrap4",
    language: "es",
    placeholder: "(Seleccione una institución)",
    minimumInputLength: 1,
    // allowClear: true, // Activar si se desea permitir limpiar selección

    ajax: {
      url: "/rrhh/formacion_academica/add/",
      type: "POST",
      delay: 250,
      headers: {
        "X-CSRFToken": csrftoken,
      },
      data: function (params) {
        return {
          term: params.term,
          action: "search_institucion",
        };
      },
      processResults: function (data) {
        return {
          results: data,
        };
      },
    },
  });
});
