/*
===================================================================
Author: xO | Optimized Version
====================================================================
*/
$(function () {
  // Configuración base de Select2 para evitar repetir código
  const select2_config = {
    theme: "bootstrap4",
    language: "es",
    width: "100%",
  };

  // Inicializar todos los select2 estándar
  $(".select2").select2(select2_config);

  const select2_ciudad = $('select[name="ciudad"]');
  const select2_barrio = $('select[name="barrio"]');
  const csrftoken = $("[name=csrfmiddlewaretoken]").val();

  // --- SELECT2 CIUDAD (AJAX REMOTE) ---
  select2_ciudad.select2({
    ...select2_config,
    placeholder: "Buscar ciudad...",
    allowClear: true,
    minimumInputLength: 1,
    ajax: {
      url: "/base/ajax/ciudades",
      type: "GET",
      delay: 250,
      headers: { "X-CSRFToken": csrftoken },
      data: (params) => ({ q: params.term }),
      processResults: (data) => ({ results: data }),
    },
  });

  // --- SELECT2 BARRIO (DEPENDIENTE) ---
  // Inicializamos barrio como un select2 normal vacío
  select2_barrio.select2(select2_config);

  select2_ciudad.on("change", function () {
    const id_ciudad = $(this).val();

    // Limpiar barrios si no hay ciudad
    if (!id_ciudad) {
      select2_barrio
        .empty()
        .append('<option value="">(Todos)</option>')
        .trigger("change");
      return;
    }

    $.ajax({
      url: "/base/ajax/barrios/",
      type: "GET",
      data: { id: id_ciudad }, // Eliminado params.term que causaba error
      dataType: "json",
      beforeSend: function () {
        // Opcional: mostrar estado de carga
        select2_barrio.prop("disabled", true);
      },
    })
      .done(function (data) {
        if (!data.hasOwnProperty("error")) {
          // La mejor forma de actualizar Select2 con nuevos datos:
          select2_barrio
            .empty()
            .select2({
              ...select2_config,
              data: data,
            })
            .trigger("change");
        } else {
          message_error(data.error);
        }
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Error en barrios:", textStatus, errorThrown);
      })
      .always(function () {
        select2_barrio.prop("disabled", false);
      });
  });

  // Evento al cambiar barrio
  select2_barrio.on("select2:select", function (e) {
    const data = e.params.data;
    console.log("Barrio seleccionado:", data);
    // Si necesitas los datos de la ciudad adjuntos en el barrio:
    if (data.data) {
      console.log("Datos extra de ciudad:", data.data);
    }
  });
});
