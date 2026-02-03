var tblData;

let columnas = [
  { data: "id" }, //Siempre con un ID
];

// Usamos la variable global de la ventana
if (!window.isSelf) {
  columnas.push({ data: "empleado" });
}

columnas.push(
  { data: "nombre_capacitacion" },
  { data: "tipo_certificacion__denominacion" },
  { data: "institucion__denominacion" },
  { data: "fecha_inicio" },
  { data: "fecha_fin" },
  { data: "archivo_pdf" },
  { data: "id" },
);

// Como "archivo_pdf" es la penúltima: esto utilizamos para generar el link del archivo
const colArchivoIndice = columnas.length - 2;
const colOpcionesIndice = columnas.length - 1;
const colFechaFinIndice = columnas.findIndex((col) => col.data === "fecha_fin");

var capacitacion = {
  list: function (all) {
    const select_sucursal = $('select[name="sucursal"]');
    const select_empleado = $('select[name="empleado"]');
    const current_date = new moment().format("DD/MM/YYYY");

    var parameters = {
      action: "search",
      sucursal:
        select_sucursal.val() || localStorage.getItem("last_sucursal") || "",
      empleado:
        select_empleado.val() || localStorage.getItem("last_empleado") || "",
    };

    if (all) {
      parameters.sucursal = "";
      parameters.empleado = "";
      if (!select_sucursal.prop("disabled"))
        select_sucursal.val("").trigger("change.select2");
      select_empleado.val("").trigger("change.select2");
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
      order: [[colFechaFinIndice, "desc"]], // Ordenamos por fecha fin descendente
      dom: "Blfrtip",
      buttons: [
        {
          extend: "excelHtml5",
          text: "Descargar Excel <i class='fas fa-file-excel'></i>",
          className: "btn btn-success btn-flat btn-xs",
          exportOptions: {
            columns: ":not(:last-child)",
            format: {
              body: function (data, row, column, node) {
                // Si es la columna de archivo, extrae el link para Excel
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
          text: "Descargar PDF <i class='fas fa-file-pdf'></i>",
          className: "btn btn-danger btn-flat btn-xs",
          orientation: "landscape",
          pageSize: "LEGAL", // Tamaño Oficio
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
            // Fit automático de columnas
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
            doc.pageMargins = [20, 20, 20, 20];

            // Convertir texto en Link clickeable
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

            doc.footer = function (page, pages) {
              return {
                columns: [
                  {
                    alignment: "left",
                    text: ["Generado: ", { text: current_date }],
                    margin: [20, 0],
                  },
                  {
                    alignment: "right",
                    text: [
                      "Página ",
                      { text: page.toString() },
                      " de ",
                      { text: pages.toString() },
                    ],
                    margin: [0, 0, 20, 0],
                  },
                ],
                fontSize: 8,
              };
            };
          },
        },
      ],
      columns: columnas, //Definimos mas arriba
      // columns: [
      //   { data: "id" }, // 0
      //   { data: "empleado" }, // 1
      //   { data: "nombre_capacitacion" }, // 2
      //   { data: "tipo_certificacion_denominacion" }, // 3
      //   { data: "institucion_denominacion" }, // 4
      //   { data: "fecha_inicio" }, // 5
      //   { data: "fecha_fin" }, // 6
      //   { data: "archivo_pdf" }, // 7
      //   { data: "id" }, // 8 (Botones)
      // ],
      columnDefs: [
        {
          targets: [0],
          render: function (data) {
            return formatoNumero(data);
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
          targets: [-1],
          className: "text-center",
          orderable: false,
          render: function (data, type, row) {
            return `<a href="${pathname}update/${row.id}/" class="btn btn-warning btn-xs btn-flat" title="Editar"><i class="fas fa-edit"></i></a> 
                                <a href="${pathname}delete/${row.id}/" class="btn btn-xs btn-danger btn-flat" title="Eliminar"><i class="fas fa-trash-alt"></i></a>`;
          },
        },
      ],
    });
  },
};

$(function () {
  // Carga inicial (usará los valores restaurados por empleado.js)
  capacitacion.list(false);

  // Evento de refresco automático
  $('select[name="sucursal"], select[name="empleado"]').on(
    "change",
    function () {
      // Solo recargamos si no es una limpieza masiva para evitar doble petición
      if (typeof tblData !== "undefined") {
        capacitacion.list(false);
      }
    },
  );
});
