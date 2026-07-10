<!DOCTYPE html>
<html>
<head>
    <title>Formulario de Trabajadores</title>
    <link rel="stylesheet" href="plugins/datatables-bs4/css/dataTables.bootstrap4.min.css">
		<link rel="stylesheet" href="plugins/datatables-responsive/css/responsive.bootstrap4.min.css">
		<link rel="stylesheet" href="css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.min.js"></script>

		<link rel="stylesheet" href="css/buttons.dataTables.min.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }

        h2 {
            text-align: center;
            margin-top: 20px;
        }

        form {
            background-color: #fff;
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        input[type="text"],
        select {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        input[type="submit"] {
            background-color: #007BFF;
            color: #fff;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
        }

        .success {
            color: green;
            margin-top: 10px;
        }

        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
   
</head>
<body>
<nav class="navbar" style="background:#fff">
		  <div class="container-fluid">
			<div class="navbar-header">
			  <a class="navbar-brand" href="#">Asistencias - Don Luis</a>
			</div>
			<ul class="nav navbar-nav">
			  <li class="active"><a href="attendance.php"><span class="glyphicon glyphicon-home"></span> Asistencias</a></li>
			  <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><span class="glyphicon glyphicon-cog"></span> Movimientos <span class="caret"></span></a>
				<ul class="dropdown-menu">
				  <li><a href="lista.php"><span class="glyphicon glyphicon-user"></span> Trabajadores</a></li>
				  <li><a href="agregar.php"><span class="glyphicon glyphicon-plus-sign"></span> Agregar Nuevos</a></li>
				  <li><a href="attendance.php"><span class="glyphicon glyphicon-calendar"></span> Marcaciones</a></li>

				</ul>
			  </li>
			  <li><a href="#"><span class="glyphicon glyphicon-align-justify"></span> Reports</a></li>
              <li><a href="index.php"><span class="glyphicon glyphicon-time"></span> Ir al Marcador</a></li>
			</ul>
			<ul class="nav navbar-nav navbar-right">
			  <li><a href="#"><span class="glyphicon glyphicon-user"></span> Sign Up</a></li>
			  <li><a href="login.html"><span class="glyphicon glyphicon-log-in"></span> Login</a></li>
			</ul>
		  </div>
		</nav>
        <h2>Formulario para agregar Trabajador</h2>

    <?php
    // Incluye tu archivo de conexión conn.php
    include('conn.php');

    $message = ""; // Inicializa el mensaje como cadena vacía

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // Recibe los datos del formulario
        $studentid = $_POST['studentid'];
        $firstname = $_POST['firstname'];
        $mname = $_POST['mname'];
        $lastname = $_POST['lastname'];
        $age = $_POST['age'];
        $gender = $_POST['gender'];

        // Consulta SQL de inserción
        $sql = "INSERT INTO student (studentid, firstname, mname, lastname, age, gender) 
                VALUES ('$studentid', '$firstname', '$mname', '$lastname', '$age', '$gender')";

        if ($conn->query($sql) === TRUE) {
            $message = "trabajador agregado con éxito.";
            echo "<script>alert('{$message}');</script>"; // Muestra la alerta
        } else {
            $message = "Error al agregar trabajador: " . $conn->error;
            echo "<script>alert('{$message}');</script>"; // Muestra la alerta de error
        }
    }
    ?>

    <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
        <label for="studentid">DNI Trabajador:</label>
        <input type="text" name="studentid" required><br>

        <label for="firstname">Nombres</label>
        <input type="text" name="firstname" required><br>

       

        <label for="lastname">Apellidos:</label>
        <input type="text" name="lastname" required><br>
        <label for="mname">Empresa:</label>
        <input type="text" name="mname"><br>

        <label for="age">Edad:</label>
        <input type="text" name="age" required><br>

        <label for="gender">Género:</label>
        <select name="gender" required>
            <option value="Masculino">Masculino</option>
            <option value="Femenino">Femenino</option>
        </select><br>

        <input type="submit" value="Agregar Trabajador">
    </form>
</body>
</html>
