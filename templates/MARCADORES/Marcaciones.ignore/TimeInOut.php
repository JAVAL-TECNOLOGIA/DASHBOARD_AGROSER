<?php
require_once 'conn.php';

if (isset($_POST['studentID'])) {
    $studentID = $_POST['studentID'];

    // Verificar si el campo studentID está vacío
    if (empty($studentID)) {
        $_SESSION['error'] = 'Por favor, ingrese su número de código de barras';
        header("location: index.php");
        exit;
    }

    date_default_timezone_set('America/Lima');
    $date = date('Y/m/d');
    $time = date('H:i:s');

    // Buscar al estudiante por ID
    $sql = "SELECT * FROM student WHERE STUDENTID = '$studentID'";
    $query = $conn->query($sql);

    if ($query->num_rows < 1) {
        // El ID del estudiante no se encontró, pero aún así registraremos el ingreso
        $sql = "INSERT INTO student(STUDENTID) VALUES('$studentID')";
        if ($conn->query($sql) === TRUE) {
            // Registro de estudiante exitoso con una clase de estilo específica
            $_SESSION['success2'] = '<span style="color: white; padding: 5px; font-size: 30px;">No se encontró DNI, pero ha sido registrado</span>';
            
            // También registramos la entrada en la tabla attendance
            $sql = "INSERT INTO attendance(STUDENTID, TIMEIN, LOGDATE, STATUS) VALUES('$studentID', '$time', '$date', '0')";
            if ($conn->query($sql) === TRUE) {
                $_SESSION['success2'] .= ' | Registro de Ingreso Exitoso: | Time: ' . $time;
            } else {
                $_SESSION['error'] = $conn->error;
            }
        } else {
            $_SESSION['error'] = $conn->error;
        }
    } else {
        $row = $query->fetch_assoc();
        $id = $row['STUDENTID'];

        // Verificar si hay una entrada reciente para el mismo estudiante y fecha
        $sql = "SELECT * FROM attendance WHERE STUDENTID='$id' AND LOGDATE='$date' AND STATUS='0'";
        $query = $conn->query($sql);

        if ($query->num_rows > 0) {
            $existingEntry = $query->fetch_assoc();
            $existingTimeIn = strtotime($existingEntry['TIMEIN']);
            $currentTime = strtotime($time);

            // Calcular la diferencia en segundos
            $timeDifference = $currentTime - $existingTimeIn;

            // Limitar la nueva entrada a 5 minutos (300 segundos)
            if ($timeDifference <= 300) {
                $_SESSION['error'] = '<span style="font-size: 35px;">Ya ha registrado una entrada o salida en los últimos 60 segundos.</span>';
            } else {
                // Actualizar la entrada existente con la hora de salida
                $sql = "UPDATE attendance SET TIMEOUT='$time', STATUS='1' WHERE STUDENTID='$studentID' AND LOGDATE='$date'";
                $query = $conn->query($sql);
                $_SESSION['success'] = '<span style="font-size: 35px;">' . $studentID . ' | Registro de Salida exitoso: | Time: ' . $time . '</span>';
            }
        } else {
            // Verificar si hay una salida reciente para el mismo estudiante y fecha
            $sql = "SELECT * FROM attendance WHERE STUDENTID='$id' AND LOGDATE='$date' AND STATUS='1'";
            $query = $conn->query($sql);

            if ($query->num_rows > 0) {
                $existingExit = $query->fetch_assoc();
                $existingTimeOut = strtotime($existingExit['TIMEOUT']);
                $currentTime = strtotime($time);

                // Calcular la diferencia en segundos
                $timeDifference = $currentTime - $existingTimeOut;

                // Limitar un nuevo ingreso a 5 minutos (300 segundos)
                if ($timeDifference <= 300) {
                    $_SESSION['error'] = '<span style="font-size: 35px;">Ya ha registrado una entrada o salida en los últimos 60 segundos</span>';
                } else {
                    // Registrar una nueva entrada si no hay una entrada o salida reciente
                    $sql = "INSERT INTO attendance(STUDENTID, TIMEIN, LOGDATE, STATUS) VALUES('$studentID', '$time', '$date', '0')";
                    if ($conn->query($sql) === TRUE) {
                        $_SESSION['success'] = '<span style="font-size: 35px;">' . $studentID . ' | Registro de Ingreso Exitoso: | Time: ' . $time . '</span>';
                    } else {
                        $_SESSION['error'] = $conn->error;
                    }
                }
            } else {
                // Registrar una nueva entrada si no hay una entrada o salida reciente
                $sql = "INSERT INTO attendance(STUDENTID, TIMEIN, LOGDATE, STATUS) VALUES('$studentID', '$time', '$date', '0')";
                if ($conn->query($sql) === TRUE) {
                    $_SESSION['success'] = '<span style="font-size: 35px;">' . $studentID . ' | Registro de Ingreso Exitoso: | Time: ' . $time . '</span>';
                } else {
                    $_SESSION['error'] = $conn->error;
                }
            }
        }
    }
} else {
    $_SESSION['error'] = 'Escanee su número de código de barras';
}

header("location: index.php");
$conn->close();
?>
