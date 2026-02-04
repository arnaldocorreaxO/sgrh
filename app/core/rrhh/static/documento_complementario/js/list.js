var tblData;
let columnas = [
  { data: "id" }, //Siempre con un ID
];

// Usamos la variable global de la ventana
if (!window.isSelf) {
  columnas.push({ data: "empleado" });
}

columnas.push(
  { data: "fecha_documento" },
  { data: "tipo_documento__denominacion" },
  { data: "descripcion" },
  { data: "estado_documento__denominacion" },
  { data: "archivo_pdf" },
  { data: "id" },
);

// Como "archivo_pdf" es la penúltima: esto utilizamos para generar el link del archivo
const colArchivoIndice = columnas.length - 2;
const colOpcionesIndice = columnas.length - 1;

var documentoComplementario = {
  list: function (all) {
    const select_sucursal = $('select[name="sucursal"]');
    const select_empleado = $('select[name="empleado"]');
    const tipo_documento = $('select[name="tipo_documento"]');
    const rango_fecha = $('input[name="rango_fecha"]');
    const current_date = new moment().format("DD/MM/YYYY");

    var parameters = {
      action: "search",
      sucursal:
        select_sucursal.val() || localStorage.getItem("last_sucursal") || "",
      empleado:
        select_empleado.val() || localStorage.getItem("last_empleado") || "",
      tipo_documento: tipo_documento.val() || "",
      rango_fecha: rango_fecha.val() || "",
    };

    if (all) {
      parameters.sucursal = "";
      parameters.empleado = "";
      if (!select_sucursal.prop("disabled"))
        select_sucursal.val("").trigger("change.select2");
      select_empleado.val("").trigger("change.select2");
      tipo_documento.val("").trigger("change.select2");
      rango_fecha.val("");
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
      order: [[0, "desc"]],
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

            // Lógica para Links funcionales
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
      columns: columnas,
      columnDefs: [
        {
          targets: [0],
          className: "text-left",
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
            return `<a href="${pathname}update/${row.id}/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> 
                                <a href="${pathname}delete/${row.id}/" class="btn btn-xs btn-danger btn-flat"><i class="fas fa-trash-alt"></i></a>`;
          },
        },
      ],
    });
  },
};

$(function () {
  // Función para obtener el rango inicial [01/01/YYYY, Hoy]
  const getRangoDefault = () => {
    const hoy = new Date();
    const inicioAnio = new Date(hoy.getFullYear(), 0, 1);

    // Función auxiliar para pad (01, 02, etc)
    const formatDMY = (date) => {
      const d = date.getDate().toString().padStart(2, "0");
      const m = (date.getMonth() + 1).toString().padStart(2, "0");
      const y = date.getFullYear();
      return `${d}/${m}/${y}`;
    };

    const fechaInicioStr = formatDMY(inicioAnio);
    const fechaFinStr = formatDMY(hoy);

    console.log("Rango Formateado:", `${fechaInicioStr} a ${fechaFinStr}`);

    // Para Flatpickr devolvemos el array de objetos Date
    return [fechaInicioStr, fechaFinStr];
  };

  const rangoInput = $("#id_rango_fecha");

  // 1. Inicializar Flatpickr
  const fp = $("#id_rango_fecha").flatpickr({
    mode: "range",
    locale: "es",
    dateFormat: "d/m/Y",
    // altInput genera un campo visualmente más limpio y compatible
    altInput: true,
    altFormat: "d/m/Y",
    conjunction: " a ", // <--- CRUCIAL: Define cómo se unen las fechas
    defaultDate: getRangoDefault(),

    static: true,
    maxDate: "today",
    onReady: function (selectedDates, dateStr, instance) {
      // Estilo para que no parezca deshabilitado y use el ancho completo
      $(instance.altInput).addClass("form-control bg-white");
    },
    onChange: function (selectedDates, dateStr, instance) {
      if (selectedDates.length === 2) {
        documentoComplementario.list(false);
      }
    },
  });

  // 2. Eventos para Selectores
  $('select[name="empleado"], select[name="tipo_documento"]').on(
    "change",
    function () {
      documentoComplementario.list(false);
    },
  );

  // --- Tu lógica de Reset ---
  $("#btnResetFiltros").on("click", function () {
    $('select[name="empleado"], select[name="tipo_documento"]')
      .val(null)
      .trigger("change.select2");
    if (fp) {
      fp.setDate(getRangoDefault()); // Esto forzará de nuevo el rango completo
    }
    documentoComplementario.list(false);
  });

  // 4. Carga inicial de la tabla
  documentoComplementario.list(false);
});
