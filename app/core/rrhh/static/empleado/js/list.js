var tblData;

let columnas = [
  { data: "id" },
  { data: "sucursal__cod" },
  { data: "ci" },
  { data: "legajo" },
  { data: "nombre" },
  { data: "apellido" },
  { data: "edad" },
  { data: "antiguedad" },
  { data: "celular" },
  { data: "progreso_perfil" },
  { data: "id" },
];

// Como "archivo_pdf" es la penúltima: esto utilizamos para generar el link del archivo
// Archivo Indice y Opciones Indice están en la misma columna en las exportaciones de Excel y PDF
// pero acá no se usan
const colArchivoIndice = columnas.length;
const colOpcionesIndice = columnas.length - 1;
const colPerfilIndice = columnas.length - 2;
const colNombreIndice = columnas.findIndex((col) => col.data === "nombre");
const colApellidoIndice = columnas.findIndex((col) => col.data === "apellido");

var registros = {
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
      lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, "Todos"],
      ],
      pageLength: 10,

      ajax: {
        url: pathname,
        type: "POST",
        data: parameters,
        headers: { "X-CSRFToken": csrftoken },
      },
      language: {
        sProcessing:
          '<div class="spinner-border text-primary" role="status"></div><br>Procesando...',
      },
      order: [
        [colApellidoIndice, "asc"],
        [colNombreIndice, "asc"],
      ], // Ordenamos por apellido asc y nombre ascendente
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
                if (column === colPerfilIndice) {
                  // Buscamos el texto del badge y los pendientes
                  var text = $(node).text().trim(); // "Incompleto (Faltan 5)"
                  var title = $(node).find("span").attr("title") || ""; // "Pendiente: ..."

                  return title ? text + " - " + title : text;
                }
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
                if (column === colPerfilIndice) {
                  // Buscamos el texto del badge y los pendientes
                  var text = $(node).text().trim(); // "Incompleto (Faltan 5)"
                  var title = $(node).find("span").attr("title") || ""; // "Pendiente: ..."

                  return title ? text + " - " + title : text;
                }
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
      columnDefs: [
        { targets: [0], visible: false, searchable: false }, // Ocultamos ID, que se usará para acciones pero no es relevante mostrarlo

        {
          targets: [2],
          class: "text-left",
          orderable: true,
          render: function (data, type, row) {
            return formatoNumero(data);
          },
        },
        {
          targets: [-5],
          class: "text-center",
          data: "edad",
          orderable: true,
          render: function (data, type, row) {
            if (type === "sort") {
              return data.timestamp; // Ordena por fecha YYYYMMDD
            }
            return data.display; // Muestra "25 años"
          },
        },
        {
          targets: [-4],
          class: "text-center",
          data: "antiguedad",
          orderable: true,
          render: function (data, type, row) {
            if (type === "sort") {
              return data.timestamp; // Ordena por fecha YYYYMMDD
            }
            return data.display; // Muestra "3 años"
          },
        },
        {
          targets: [-2], // La posición de la nueva columna perfil_completado
          class: "text-center",
          data: "progreso_perfil",
          render: function (data, type, row) {
            // 'data' será el diccionario que definimos en la @property de Django
            if (!data)
              return '<span class="badge bg-secondary">Sin datos</span>';

            if (type === "sort") {
              console.log("Ordenando por porcentaje:", data.porcentaje);
              return data.porcentaje; // Ordena por el porcentaje (0, 50, 100...)
            }

            let s = data.display;

            // Construimos el texto para el tooltip si hay pendientes
            let tooltip =
              s.faltantes && s.faltantes.length > 0
                ? 'title="Pendiente: ' + s.faltantes.join(", ") + '"'
                : 'title="Perfil completo"';

            let color = s.color; // success, warning, danger

            return `
                  <div class="d-flex align-items-center" style="min-width: 150px; cursor: help;" data-toggle="tooltip" data-html="true" ${tooltip}>
                      <div class="progress flex-grow-1" style="height: 18px; background-color: #e9ecef; border-radius: 4px;">
                          <div class="progress-bar bg-${color}" 
                              role="progressbar" 
                              style="width: ${data.porcentaje}%; transition: width 0.6s ease;" 
                              aria-valuenow="${data.porcentaje}" 
                              aria-valuemin="0" 
                              aria-valuemax="100">
                          </div>
                      </div>
                      <span class="ml-2 font-weight-bold text-dark" style="min-width: 45px; font-size: 0.95rem; letter-spacing: -0.5px;">
                          ${data.porcentaje}%
                      </span>
                  </div>
              `;
          },
        },
        {
          targets: [-1],
          class: "text-center",
          orderable: false,
          render: function (data, type, row) {
            var buttons = "";
            buttons +=
              '<a href="' +
              pathname +
              "cv/pdf/" +
              row.id +
              '/" class="btn btn-danger btn btn-flat btn-xs" data-toggle="tooltip" title="Ver CV PDF" target="_blank"><i class="fas fa-file-pdf"></i></a> ';
            buttons +=
              '<a href="' +
              pathname +
              "update/" +
              row.id +
              '/" class="btn btn-warning btn btn-flat btn-xs" data-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a> ';
            buttons +=
              '<a href="' +
              pathname +
              "delete/" +
              row.id +
              '/" type="button" class="btn btn-dark btn btn-flat btn-xs" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash-alt"></i></a>';
            return buttons;
          },
        },
      ],
      drawCallback: function (settings) {
        $('[data-toggle="tooltip"]').tooltip({
          html: true, // Esto permite que los <br> que pusimos en los faltantes funcionen
        });
      },
    });
  },
};

$(function () {
  // Carga inicial (usará los valores restaurados por empleado.js)
  registros.list(false);

  // Evento de refresco automático
  $('select[name="sucursal"], select[name="empleado"]').on(
    "change",
    function () {
      // Solo recargamos si no es una limpieza masiva para evitar doble petición
      if (typeof tblData !== "undefined") {
        registros.list(false);
      }
    },
  );
});
