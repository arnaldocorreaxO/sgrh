var historico_disciplinario = {
  list: function () {
    $("#data").DataTable({
      responsive: true,
      autoWidth: false,
      destroy: true,
      deferRender: true,
      processing: true,
      serverSide: true,
      paging: true,
      ordering: true,
      searching: true,
      lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, "Todos"],
      ],
      pagingType: "full_numbers",
      pageLength: 10,
      ajax: {
        url: pathname,
        type: "POST",
        data: {
          action: "search",
        },
        headers: {
          "X-CSRFToken": csrftoken,
        },
      },
      order: [[0, "asc"]],
      columns: [
        { data: "id" },
        { data: "tipo_falta_denominacion" },
        { data: "tipo_sancion_denominacion" },
        { data: "tipo_documento_denominacion" },
        { data: "estado_documento_denominacion" },
        { data: "archivo_pdf" },
        { data: "id" },
      ],
      columnDefs: [
        {
          targets: [0],
          className: "text-left",
          orderable: true,
          render: function (data) {
            return formatoNumero(data);
          },
        },
        {
          targets: [1, 2, 3],
          className: "text-left",
          orderable: true,
        },
        {
          targets: [-2],
          className: "text-center",
          orderable: false,
          render: function (data, type, row) {
            if (row.archivo_pdf_url) {
              return (
                '<a href="' +
                row.archivo_pdf_url +
                '" class="btn btn-xs btn-danger btn-flat" data-toggle="tooltip" title="Ver PDF" target="_blank">' +
                '<i class="fas fa-file-pdf"></i></a>'
              );
            }
            return '<span class="text-muted">Sin archivo</span>';
          },
        },
        {
          targets: [-1],
          className: "text-center",
          orderable: false,
          render: function (data, type, row) {
            return (
              '<a href="' +
              pathname +
              "/update/" +
              row.id +
              '/" class="btn btn-warning btn-xs btn-flat" data-toggle="tooltip" title="Editar">' +
              '<i class="fas fa-edit"></i></a> ' +
              '<a href="' +
              pathname +
              "/delete/" +
              row.id +
              '/" class="btn btn-danger btn-xs btn-flat" data-toggle="tooltip" title="Eliminar">' +
              '<i class="fas fa-trash-alt"></i></a>'
            );
          },
        },
      ],
      initComplete: function () {
        // Espacio para filtros o inicialización adicional
      },
    });
  },
};

$(function () {
  historico_disciplinario.list();
});
