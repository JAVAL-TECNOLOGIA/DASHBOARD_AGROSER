<?php
include('conn.php');

$studentid = null;

if (isset($_GET['id']) && is_numeric($_GET['id'])) {
    $studentid = $_GET['id'];

    $sql = "SELECT * FROM student WHERE studentid = $studentid";
    $result = $conn->query($sql);

    if ($result->num_rows == 1) {
        $row = $result->fetch_assoc();

        $firstname = isset($row['firstname']) ? $row['firstname'] : '';
        $mname = isset($row['mname']) ? $row['mname'] : '';
        $lastname = isset($row['lastname']) ? $row['lastname'] : '';
        $age = isset($row['age']) ? $row['age'] : '';
        $gender = isset($row['gender']) ? $row['gender'] : '';
    } else {
        echo "trabajador no encontrado.";
        exit;
    }
} else {
    echo "ID de trabajador no válido.";
    exit;
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['cancel'])) {
        // Si se presionó "Cancelar", redirige a lista.php
        header("Location: lista.php");
        exit;
    }

    $new_firstname = $_POST['firstname'];
    $new_mname = $_POST['mname'];
    $new_lastname = $_POST['lastname'];
    $new_age = $_POST['age'];
    $new_gender = $_POST['gender'];

    if ($new_firstname && $new_lastname && $new_age && $new_gender) {
        $update_sql = "UPDATE student SET firstname='$new_firstname', mname='$new_mname', lastname='$new_lastname', age=$new_age, gender='$new_gender' WHERE studentid = $studentid";

        if ($conn->query($update_sql) === TRUE) {
            echo '<script>';
            echo 'alert("Actualización exitosa.");';
            echo 'window.location.href = "lista.php";';
            echo '</script>';
            exit;
        } else {
            echo "Error al actualizar la información del trabajador: " . $conn->error;
        }
    } else {
        echo "Por favor, complete todos los campos.";
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html>
<head>
    

    <title>Editar trabajador</title>
    <link rel="stylesheet" href="tu-archivo-de-estilos.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh; /* Asegura una altura mínima de la página */
        }

        h2 {
            text-align: center;
            margin-top: 20px;
        }

        form {
            background-color: #fff;
            width: 400px;
            padding: 33px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
            text-align: center;
            margin-top: 20px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        .btn {
            background-color: #007BFF;
            color: #fff;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .btn:hover {
            background-color: #0056b3;
        }

        .cancel-button {
            background-color: #ccc;
            color: #fff;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none; /* Agrega esto para que el enlace se vea como un botón */
            display: inline-block;
        }

        .cancel-button:hover {
            background-color: #999;
        }
    </style>

</head>
<body>
    
    <form method="post">
        <div class="form-group">
            <label for="studentid">Student ID:</label>
            <input type="text" class="form-control" name="studentid" value="<?php echo $studentid; ?>" readonly>
        </div>
        <div class="form-group">
            <label for="firstname">Nombres</label>
            <input type="text" class="form-control" name="firstname" autocomplete="off" value="<?php echo $firstname; ?>">
        </div>
        <div class="form-group">
            <label for="lastname">Apellidos:</label>
            <input type="text" class="form-control" name="lastname" autocomplete="off" value="<?php echo $lastname; ?>">
        </div>
        <div class="form-group">
            <label for="mname">Empresas</label>
            <input type="text" class="form-control" name="mname" autocomplete="off" value="<?php echo $mname; ?>">
        </div>
        
        <div class="form-group">
            <label for="age">Edad:</label>
            <input type="text" class="form-control" name="age" autocomplete="off" value="<?php echo $age; ?>">
        </div>
        <div class="form-group">
            <label for="gender">Género:</label>
            <input type="text" class="form-control" name="gender"autocomplete="off" value="<?php echo $gender; ?>">
        </div>
        <a href="lista.php" class="cancel-button" style="background-color: #ffc107; color: #fff;">Cancelar</a>

        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
    </form>
</body>
</html>
