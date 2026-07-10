<?php
// Incluye tu archivo de conexión conn.php
include('conn.php');

if (isset($_GET['id']) && is_numeric($_GET['id'])) {
    $studentid = $_GET['id'];

    // Consulta SQL para eliminar al trabajador
    $sql = "DELETE FROM student WHERE studentid = $studentid";

    if ($conn->query($sql) === TRUE) {
        // Muestra la ventana emergente de eliminación exitosa
        echo '<script>alert("trabajador eliminado con éxito.");</script>';
        // Redirige a lista.php después de la eliminación exitosa
        echo '<script>window.location.href = "lista.php";</script>';
        exit; // Asegura que no se ejecuten más instrucciones
    } else {
        echo "Error al eliminar trabajador: " . $conn->error;
    }
} else {
    echo "ID de trabajador no válido.";
}

// Cierra la conexión a la base de datos
$conn->close();
?>
