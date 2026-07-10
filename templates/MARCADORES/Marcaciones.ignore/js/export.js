document.addEventListener("DOMContentLoaded", function () {
    var exportButton = document.getElementById("exportButton");

    exportButton.addEventListener("click", function () {
        var table = $('#example1').DataTable();
        var txtData = "";

        // Deshabilitar la paginación para obtener todas las filas a la vez
        table.page.len(-1).draw();

        // Obtener todas las filas de la tabla
        var rows = table.rows({ search: 'applied' }).nodes();

        // Recorrer todas las filas de la tabla
        for (var i = 0; i < rows.length; i++) {
            var cells = rows[i].getElementsByTagName("td");

            // Asegurarse de que hay suficientes celdas en la fila
            if (cells.length >= 5) {
                // Obtener los valores de las celdas
                var studentID = cells[1].textContent.trim();
                var logDate = cells[4].textContent.trim();
                var timeIn = cells[2].textContent.trim();
                var timeOut = cells[3].textContent.trim();

                // Reorganizar la fecha y la hora al formato DDMMYYYY y HHMMSS
                var formattedLogDate = formatDate(logDate);
                var formattedTimeIn = formatTime(timeIn);
                var formattedTimeOut = formatTime(timeOut);

                // Construir líneas de datos en el formato deseado
                var lineIn = studentID + "|" + formattedLogDate + "|" + formattedTimeIn;
                var lineOut = studentID + "|" + formattedLogDate + "|" + formattedTimeOut;

                txtData += lineIn + "\n" + lineOut + "\n"; // Dos líneas: entrada y salida
            }
        }

        // Restaurar la paginación original
        table.page.len(10).draw();

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

// Función para formatear la fecha al formato DDMMYYYY
function formatDate(date) {
    var parts = date.split("-");
    if (parts.length === 3) {
        var day = parts[2];
        var month = parts[1];
        var year = parts[0];
        return day + month + year;
    }
    return date;
}

// Función para formatear la hora al formato HHMMSS
function formatTime(time) {
    var parts = time.split(":");
    if (parts.length === 3) {
        var hour = parts[0];
        var minute = parts[1];
        var second = parts[2];
        return hour + minute + second;
    }
    return time;
}
