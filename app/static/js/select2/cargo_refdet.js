$(function () {
  const select2Cargo = $('select[name="cargo"]');

  select2Cargo.select2({
    theme: "bootstrap4",
    language: "es",
    placeholder: "(Seleccione un cargo)",
    // minimumInputLength: 1,
    tags: true,

    createTag: function (params) {
      const term = $.trim(params.term);
      if (term === "") return null;

      return {
        id: "new:" + term,
        text: term,
        newOption: true,
      };
    },

    templateResult: function (data) {
      if (data.newOption) {
        return $(
          '<span style="color: green;">➕ Crear: ' + data.text + "</span>",
        );
      }
      return data.text;
      d;
    },

    ajax: {
      url: "/rrhh/ajax/cargos/", // ← URL correcta
      type: "GET",
      delay: 250,
      data: function (params) {
        return { q: params.term };
      },
      processResults: function (data) {
        return { results: data };
      },
    },
  });
});
