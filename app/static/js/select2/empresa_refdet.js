$(function () {
  const select2Empresa = $('select[name="empresa"]');

  select2Empresa.select2({
    theme: "bootstrap4",
    language: "es",
    placeholder: "(Seleccione una empresa)",
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
    },

    ajax: {
      url: "/rrhh/ajax/empresas/", // ← URL correcta
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
