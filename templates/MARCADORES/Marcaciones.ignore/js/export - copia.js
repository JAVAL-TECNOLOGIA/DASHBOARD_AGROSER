document.addEventListener("DOMContentLoaded", function () {
    var exportButton = document.getElementById("exportButton");

    exportButton.addEventListener("click", function () {
        var table = document.getElementById("example1");
        var rows = table.getElementsByTagName("tr");
        var txtData = "";

        // Recorrer todas las filas de la tabla
        for (var i = 1; i < rows.length; i++) { // Comienza desde 1 para omitir la fila de encabezado
            var cells = rows[i].getElementsByTagName("td");
            for (var j = 0; j < cells.length; j++) {
                txtData += cells[j].textContent + "\t"; // Separados por tabulación
            }
            txtData += "\n"; // Nueva línea después de cada fila
        }

        // Crear un enlace <a> para descargar el archivo TXT
        var a = document.createElement("a");
        a.href = "data:text/plain;charset=utf-8," + encodeURIComponent(txtData);
        a.download = "exported_data.txt";
        a.style.display = "none";

        // Agregar el elemento <a> al DOM y activar el clic
        document.body.appendChild(a);
        a.click();

        // Eliminar el elemento <a> del DOM
        document.body.removeChild(a);
    });
});
