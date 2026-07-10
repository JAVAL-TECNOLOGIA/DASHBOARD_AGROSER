<!DOCTYPE html>
<html>
<head>
    <title>Lista de Trabajadores</title>
    <link rel="stylesheet" href="css-login/csslista.css">
    <link rel="stylesheet" href="plugins/datatables-bs4/css/dataTables.bootstrap4.min.css">
		<link rel="stylesheet" href="plugins/datatables-responsive/css/responsive.bootstrap4.min.css">
		<link rel="stylesheet" href="css/bootstrap.min.css"> 
       <script src='https://code.jquery.com/jquery-3.5.1.slim.min.js'></script>
    <script src='https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js'></script>
    <script src='https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js'></script>

    <script>
        function confirmDelete(studentid) {
            if (confirm('¿Estás seguro de que deseas eliminar a este trabajador?')) {
                window.location.href = 'eliminar_estudiante.php?id=' + studentid;
            }
        }
    </script>
</head>
<body>
<nav class="navbar" style="background:#fff">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="#">Asistencias - Don Luis</a>
            </div>
            <ul class="nav navbar-nav">
                <li class="active"><a href="attendance.php"><span class="glyphicon glyphicon-home"></span> Asistencias</a></li>
                <li class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#"><span class="glyphicon glyphicon-cog"></span> Movimientos <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="lista.php"><span class="glyphicon glyphicon-user"></span> Trabajadores</a></li>
                        <li><a href="agregar.php"><span class="glyphicon glyphicon-plus-sign"></span> Agregar Nuevos</a></li>
                        <li><a href="attendance.php"><span class="glyphicon glyphicon-calendar"></span> Marcaciones</a></li>
                    </ul>
                </li>
                <li><a href="#"><span class="glyphicon glyphicon-align-justify"></span> Reports</a></li>
                <li><a href="index.php"><span class="glyphicon glyphicon-time"></span> Ir al Marcador<z</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href=""></a></li>
                <li><a href=""></a></li>
            </ul>
        </div>
    </nav>

    <div class="container">
        <?php
        // Incluye tu archivo de conexión conn.php
        include('conn.php');

        // Consulta SQL para seleccionar todos los trabajadores sin mostrar la columna "id"
        $sql = "SELECT studentid, firstname, mname, lastname, age, gender FROM student";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) {
            echo "<h2>Lista de Trabajadores</h2>";
            echo "<table id='example1' class='table table-striped'>";
            echo "<thead><tr><th>Dni Trabajadores</th><th>Nombres</th><th>Apellidos</th><th>Empresa</th><th>Edad</th><th>Genero</th><th>Acciones</th></tr></thead><tbody>";

            while ($row = $result->fetch_assoc()) {
                echo "<tr>";
                echo "<td>" . $row['studentid'] . "</td>";
                echo "<td>" . $row['firstname'] . "</td>";  
                echo "<td>" . $row['lastname'] . "</td>";
                echo "<td>" . $row['mname'] . "</td>";
                echo "<td>" . $row['age'] . "</td>";
                echo "<td>" . $row['gender'] . "</td>";
                echo "<td>";
                echo "<a href='editar_estudiante.php?id=" . $row['studentid'] . "' class='btn btn-info btn-sm'>Editar</a>";
                echo "<a href='javascript:void(0);' class='btn btn-danger btn-sm' onclick='confirmDelete(" . $row['studentid'] . ");'>Eliminar</a>";
                echo "</td>";
                echo "</tr>";
            }

            echo "</tbody></table>";
        } else {
            echo "No se encontraron trabajadores.";
        }

        // Cierra la conexión a la base de datos
        $conn->close();
        ?>
    </div>

    <script>
        $(document).ready(function() {
            $('#example1').DataTable();
        });
    </script>
</body>
</html>
