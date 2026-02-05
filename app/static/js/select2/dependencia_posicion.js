/*
===================================================================
Autor: xO
Descripción: Inicialización de Select2 y búsqueda dinámica de dependencias/posiciones
===================================================================
*/

$(function () {
  // Inicialización general de Select2 para todos los elementos con la clase .select2 en la plantilla base base.html

  const select2DependenciaPosicion = $('select[name="dependencia_posicion"]');

  select2DependenciaPosicion.select2({
    theme: "bootstrap4",
    language: "es",
    placeholder: "(Seleccione una dependencia/posición)",
    minimumInputLength: 1,
    // allowClear: true, // Activar si se desea permitir limpiar selección

    ajax: {
      url: "/rrhh/empleado_posicion/add/",
      type: "POST",
      delay: 250,
      headers: {
        "X-CSRFToken": csrftoken,
      },
      data: function (params) {
        return {
          term: params.term,
          action: "search_dependencia_posicion",
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
