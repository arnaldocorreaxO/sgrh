var tblData;

// Definición de columnas para Empleado Posición (Solo Admin)
let columnas = [
  { data: "id" },
  { data: "empleado_nombre_apellido_legajo" },
  { data: "dependencia_posicion__denominacion" },
  { data: "tipo_movimiento__denominacion" },
  { data: "fecha_inicio" },
  { data: "fecha_fin" },
  { data: "cargo_puesto_actual_text" }, // Campo Sí/No del toJSON
  { data: "archivo_pdf" },
  { data: "id" },
];

const colArchivoIndice = columnas.length - 2;
const colOpcionesIndice = columnas.length - 1;
const colFechaInicioIndice = columnas.findIndex(
  (col) => col.data === "fecha_inicio",
);

var registros = {
  list: function (all) {
    const select_sucursal = $('select[name="sucursal"]');
    const select_empleado = $('select[name="empleado"]');
    const select_dependencia_padre = $('select[name="dependencia_padre"]');
    const select_dependencia_hija = $('select[name="dependencia_hija"]');
    const select_tipo_movimiento = $('select[name="tipo_movimiento"]');
    const rango_fecha = $("#id_rango_fecha");
    const current_date = new moment().format("DD/MM/YYYY");

    var parameters = {
      action: "search",
      sucursal: select_sucursal.val() || "",
      empleado: select_empleado.val() || "",
      dependencia_padre: select_dependencia_padre.val() || "",
      dependencia_hija: select_dependencia_hija.val() || "",
      tipo_movimiento: select_tipo_movimiento.val() || "",
      rango_fecha: rango_fecha.val() || "",
    };

    if (all) {
      parameters.sucursal = "";
      parameters.empleado = "";
      parameters.dependencia_padre = "";
      parameters.dependencia_hija = "";
      parameters.tipo_movimiento = "";
      parameters.rango_fecha = "";
      if (!select_sucursal.prop("disabled"))
        select_sucursal.val("").trigger("change.select2");
      select_empleado.val("").trigger("change.select2");
      select_dependencia_padre.val("").trigger("change.select2");
      select_dependencia_hija.val("").trigger("change.select2");
      select_tipo_movimiento.val("").trigger("change.select2");
    }

    tblData = $("#data").DataTable({
      responsive: true,
      autoWidth: false,
      destroy: true,
      deferRender: true,
      processing: true,
      serverSide: true,
      paging: true,
      ajax: {
        url: pathname,
        type: "POST",
        data: parameters,
        headers: { "X-CSRFToken": csrftoken },
      },
      order: [[colFechaInicioIndice, "desc"]], // Orden por inicio más reciente
      dom: "Blfrtip",
      buttons: [
        {
          extend: "excelHtml5",
          text: "Excel <i class='fas fa-file-excel'></i>",
          className: "btn btn-success btn-flat btn-xs",
          exportOptions: {
            columns: ":not(:last-child)",
            format: {
              body: function (data, row, column, node) {
                if (column === colArchivoIndice) {
                  var url = $(node).find("a").attr("href");
                  return url ? window.location.origin + url : "Sin archivo";
                }
                return data;
              },
            },
          },
        },
        {
          extend: "pdfHtml5",
          text: "PDF <i class='fas fa-file-pdf'></i>",
          className: "btn btn-danger btn-flat btn-xs",
          orientation: "landscape",
          pageSize: "LEGAL",
          exportOptions: {
            columns: ":not(:last-child)",
            format: {
              body: function (data, row, column, node) {
                if (column === colArchivoIndice) {
                  var url = $(node).find("a").attr("href");
                  return url
                    ? "Ver Archivo|" + window.location.origin + url
                    : "Sin archivo";
                }
                return data;
              },
            },
          },
          customize: function (doc) {
            const colCount = doc.content[1].table.body[0].length;
            doc.content[1].table.widths = Array(colCount).fill("*");
            doc.defaultStyle.fontSize = 8;
            doc.styles.tableHeader = {
              bold: true,
              fontSize: 9,
              color: "white",
              fillColor: "#2d4154",
              alignment: "center",
            };
            var tableBody = doc.content[1].table.body;
            for (var i = 1; i < tableBody.length; i++) {
              var cell = tableBody[i][colArchivoIndice];
              if (cell && cell.text && cell.text.includes("|")) {
                var parts = cell.text.split("|");
                cell.text = parts[0];
                cell.link = parts[1];
                cell.color = "blue";
                cell.decoration = "underline";
              }
            }
          },
        },
      ],
      columns: columnas,
      columnDefs: [
        {
          targets: [0],
          render: function (data) {
            return formatoNumero(data);
          },
        },
        {
          targets: [5], // Columna Fecha Fin
          render: function (data, type, row) {
            return data
              ? data
              : '<span class="badge badge-success">Vigente</span>';
          },
        },
        {
          targets: [6], // Columna Cargo Actual
          className: "text-center",
          render: function (data, type, row) {
            let badge = row.cargo_puesto_actual
              ? "badge-primary"
              : "badge-secondary";
            return `<span class="badge ${badge}">${data}</span>`;
          },
        },
        {
          targets: [colArchivoIndice],
          className: "text-center",
          orderable: false,
          render: function (data, type, row) {
            if (row.archivo_pdf_url) {
              return `<a href="${row.archivo_pdf_url}" class="btn btn-xs btn-danger btn-flat" target="_blank"><i class="fas fa-file-pdf"></i></a>`;
            }
            return '<span class="text-muted">Sin archivo</span>';
          },
        },
        {
          targets: [colOpcionesIndice],
          className: "text-center",
          orderable: false,
          render: function (data, type, row) {
            return `<a href="${pathname}update/${row.id}/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> 
                                <a href="${pathname}delete/${row.id}/" class="btn btn-xs btn-danger btn-flat"><i class="fas fa-trash-alt"></i></a>`;
          },
        },
      ],
    });
  },
};

$(function () {
  // Configuración de Flatpickr para el rango de fechas
  const getRangoDefault = () => {
    const hoy = new Date();
    const inicioAnio = new Date(hoy.getFullYear(), 0, 1);
    const format = (d) =>
      d.getDate().toString().padStart(2, "0") +
      "/" +
      (d.getMonth() + 1).toString().padStart(2, "0") +
      "/" +
      d.getFullYear();
    return [format(inicioAnio), format(hoy)];
  };

  const fp = $("#id_rango_fecha").flatpickr({
    mode: "range",
    locale: "es",
    dateFormat: "d/m/Y",
    defaultDate: getRangoDefault(),
    maxDate: "today",
    conjunction: " a ",
    onChange: function (selectedDates) {
      if (selectedDates.length === 2) registros.list(false);
    },
  });

  // Carga inicial
  registros.list(false);

  // Eventos de filtros
  $(
    'select[name="sucursal"], select[name="empleado"], select[name="dependencia_padre"], select[name="dependencia_hija"]',
  ).on("change", function () {
    if (typeof tblData !== "undefined") registros.list(false);
  });

  // Botón reset (si existe en filter.html)
  $("#btnResetFiltros").on("click", function () {
    $('select[name="empleado"]').val(null).trigger("change");
    $('select[name="dependencia_padre"]').val(null).trigger("change");
    $('select[name="dependencia_hija"]').val(null).trigger("change");
    $('select[name="sucursal"]').val("").trigger("change.select2");
    $('select[name="tipo_movimiento"]').val("").trigger("change.select2");
    fp.setDate(getRangoDefault());
    registros.list(false);
  });
});
