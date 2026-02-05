/*
===================================================================
Autor: xO
Descripción: Relación dinámica entre Dependencia Padre e Hija
===================================================================
*/

$(function () {
  // 1. Referencias a los selectores (usando los IDs que definimos en el FilterForm)
  const selectPadre = $("#id_dependencia_padre");
  const selectHija = $("#id_dependencia_hija");

  // 2. Inicialización de Dependencia Hija con AJAX
  selectHija.select2({
    theme: "bootstrap4",
    language: "es",
    placeholder: "(Seleccione una dependencia inferior)",
    allowClear: true,
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
          padre_id: selectPadre.val(), // Enviamos el ID del padre seleccionado
          action: "search_dependencia_hija",
        };
      },
      processResults: function (data) {
        return {
          results: data,
        };
      },
    },
  });

  // 3. Evento: Cuando cambia el PADRE
  selectPadre.on("change", function () {
    // Limpiamos la selección de la hija
    selectHija.val(null).trigger("change");

    // Si el DataTable (registros) existe, recargamos la lista
    if (typeof registros !== "undefined" && typeof tblData !== "undefined") {
      registros.list(false);
    }
  });

  // 4. Evento: Cuando cambia la HIJA
  selectHija.on("change", function () {
    // Si el DataTable existe, recargamos la lista con el nuevo filtro
    if (typeof registros !== "undefined" && typeof tblData !== "undefined") {
      registros.list(false);
    }
  });
});
