var complementario = {
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
        { data: "empleado" },
        { data: "tipo_documento_denominacion" },
        { data: "descripcion" },
        { data: "estado_documento_denominacion" },
        { data: "archivo_pdf" },
        { data: "id" },
      ],
      columnDefs: [
        {
          targets: [0],
          class: "text-left",
          orderable: true,
          render: function (data, type, row) {
            return formatoNumero(data);
          },
        },
        {
          targets: [-2],
          class: "text-center",
          orderable: false,
          render: function (data, type, row) {
            var buttons = "";
            if (row.archivo_pdf_url) {
              buttons +=
                '<a href="' +
                row.archivo_pdf_url +
                '" class="btn btn-xs btn-danger btn-flat" data-toggle="tooltip" title="Ver PDF" target="_blank">' +
                '<i class="fas fa-file-pdf"></i></a>';
            } else {
              buttons += '<span class="text-muted">Sin archivo</span>';
            }
            return buttons;
          },
        },
        {
          targets: [-1],
          class: "text-center",
          orderable: false,
          render: function (data, type, row) {
            var buttons =
              '<a href="' +
              pathname +
              "update/" +
              row.id +
              '/" class="btn btn-warning btn btn-xs btn-flat" data-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a> ';
            buttons +=
              '<a href="' +
              pathname +
              "delete/" +
              row.id +
              '/" type="button" class="btn btn-xs btn-danger btn btn-flat" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash-alt"></i></a>';
            return buttons;
          },
        },
      ],
      initComplete: function (settings, json) {},
    });
  },
};

$(function () {
  $(document).ready(function () {
    complementario.list(false);
  });
});

var tblData;
var input_daterange;
var columns = [];

capacitacion = {
  list: function (all) {
    const select_empleado = $("#empleado");
    const current_date = new moment().format("YYYY-MM-DD");
    var parameters = {
      action: "search",
      // start_date: input_daterange
      //   .data("daterangepicker")
      //   .startDate.format("YYYY-MM-DD"),
      // end_date: input_daterange
      //   .data("daterangepicker")
      //   .endDate.format("YYYY-MM-DD"),
      empleado: select_empleado.val(),
      // institucion: select_institucion.val().join(", "),
      // tipo_certificacion: select_tipo_certificacion.val().join(", "),
    };

    if (all) {
      parameters.start_date = "";
      parameters.end_date = "";
      parameters.empleado = "";
      parameters.institucion = "";
      parameters.tipo_certificacion = "";
    }

    tblData = $("#data").DataTable({
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
        data: parameters,
      },
      order: [[1, "asc"]],
      dom: "Blfrtip",
      buttons: [
        {
          extend: "excelHtml5",
          text: "Descargar Excel <i class='fas fa-file-excel'></i>",
          className: "btn btn-success btn-flat btn-xs",
        },
        {
          extend: "pdfHtml5",
          text: "Descargar PDF <i class='fas fa-file-pdf'></i>",
          className: "btn btn-danger btn-flat btn-xs",
          orientation: "landscape",
          pageSize: "A4",
          customize: function (doc) {
            doc.styles.tableHeader = {
              bold: true,
              fontSize: 11,
              color: "white",
              fillColor: "#2d4154",
              alignment: "center",
            };
            doc.content[1].table.widths = columns;
            doc.content[1].margin = [0, 35, 0, 0];
            doc.footer = function (page, pages) {
              return {
                columns: [
                  {
                    alignment: "left",
                    text: ["Fecha de creación: ", { text: current_date }],
                  },
                  {
                    alignment: "right",
                    text: [
                      "Página ",
                      { text: page.toString() },
                      " de ",
                      { text: pages.toString() },
                    ],
                  },
                ],
                margin: 20,
              };
            };
          },
        },
      ],
      columns: [
        { data: "id" },
        { data: "empleado" },
        { data: "tipo_certificacion_denominacion" },
        { data: "institucion_denominacion" },
        { data: "fecha_inicio" },
        { data: "fecha_fin" },
        { data: "archivo_pdf" },
        { data: "id" },
      ],
      columnDefs: [
        {
          targets: [-2],
          className: "text-center",
          orderable: false,
          render: function (data, type, row) {
            if (row.archivo_pdf_url) {
              return `<a href="${row.archivo_pdf_url}" class="btn btn-xs btn-danger btn-flat" target="_blank" title="Ver PDF"><i class="fas fa-file-pdf"></i></a>`;
            }
            return '<span class="text-muted">Sin archivo</span>';
          },
        },
        {
          targets: [-1],
          className: "text-center",
          orderable: false,
          render: function (data, type, row) {
            var buttons =
              '<a href="' +
              pathname +
              "update/" +
              row.id +
              '/" class="btn btn-warning btn btn-xs btn-flat" data-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a> ';
            buttons +=
              '<a href="' +
              pathname +
              "delete/" +
              row.id +
              '/" type="button" class="btn btn-xs btn-danger btn btn-flat" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash-alt"></i></a>';
            return buttons;
          },
        },
      ],
      initComplete: function () {
        $.each(tblData.settings()[0].aoColumns, function (key, value) {
          columns.push(value.sWidthOrig);
        });
      },
    });
  },
};

$(function () {
  input_daterange = $("#input_daterange");
  $(".select2").select2({ theme: "bootstrap4", language: "es" });

  capacitacion.list(false);

  $("#btnBuscar").on("click", function () {
    capacitacion.list(false);
  });

  $("#btnTodos").on("click", function () {
    capacitacion.list(true);
  });
});
