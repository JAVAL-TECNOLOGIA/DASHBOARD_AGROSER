<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Marcaciones | Asistencias</title>
    <link rel="stylesheet" href="plugins/datatables-bs4/css/dataTables.bootstrap4.min.css">
    <link rel="stylesheet" href="plugins/datatables-responsive/css/responsive.bootstrap4.min.css">
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/buttons.dataTables.min.css">
    <style>
        .custom-alert .close {
            padding: 90px; /* Ajusta este valor según tus preferencias */
            /* Agrega otros estilos según sea necesario */}
        .btn-link {
            display: inline-block;
            padding: 7px 14px;
            background-color: #28a745;
            color: white;
            border: 1px solid #28a745;
            border-radius: 5px;
            text-decoration: none;
        }
        .btn-link:hover {
            background-color: #28a745;
            color: white;
        }
        a#mostrar-todos {
            text-decoration: none;
            color: #ffffff; /* Color blanco para el texto del enlace */
        }
    </style>
</head>
<body style="background:#eee">
    <nav class="navbar" style="background:#fff">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="#">Asistencias - Don Luis</a>
            </div>
            <ul class="nav navbar-nav">
                <!-- ... (código HTML existente) ... -->
                
            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href="#"><span class="glyphicon glyphicon-user"></span> Sign Up</a></li>
                <li><a href="index.php"><span class="glyphicon glyphicon-log-in"></span> Marcador</a></li>
            </ul>
        </div>
    </nav>
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <?php
                if (isset($_SESSION['error'])) {
                    echo '
                    <div class="alert alert-danger alert-dismissible" style="background:red;color:#fff">
                        <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
                        <h4><i class="icon fa fa-warning"></i> Error!</h4>
                        ' . $_SESSION['error'] . '
                    </div>
                    ';
                    unset($_SESSION['error']);
                }
                if (isset($_SESSION['success'])) {
                    echo '
                    <div class="alert alert-success alert-dismissible" style="background:green;color:#fff">
                        <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
                        <h4><i class="icon fa fa-check"></i> Correcto !</h4>
                        ' . $_SESSION['success'] . '
                    </div>
                    ';
                    unset($_SESSION['success']);
                }
                ?>
            </div>
            <div class="col-12">
                <div style="border-radius: 5px;padding:10px;background:#fff;">
                    <p>Asistencias</p>
                    <form method="POST"  style="padding:20px;">
                        <input type="date" name="filter_date" >
                        <label for="filter_mname">Filtrar por Empresa:</label>
                        <select name="filter_mname" id="filter_mname">
                            <option value="">Selecciona una Empresa</option>
                            <option value="CAMPO VERDE">CAMPO VERDE</option>
                            <option value="DON LUIS">DON LUIS</option>
                            <option value="INVERSIONES AJS">INVERSIONES AJS</option>
                        </select>
                        <button type="submit" class="btn btn-primary" style="margin-left: 14px;">Filtrar </button>
                        <a href="attendance.php" id="mostrar-todos" class="btn-link">Mostrar Todos</a>
                        <button type="button" class="btn btn-warning" id="exportButton">Exportar para Nisira</button>
                    </form>
                    <table id="example1" class="table table-striped">
                        <thead>
                            <tr>
                                <th>NOMBRE</th>
                                <th>ID TRABAJADOR</th>
                                <th>ENTRADA</th>
                                <th>SALIDA</th>
                                <th>FECHA</th>
                                <th>EMPRESA</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php
                            require_once 'conn.php';
                            date_default_timezone_set('America/Lima');

                            if ($conn->connect_error) {
                                die("Connection failed" . $conn->connect_error);
                            }

                            // Verificar si se ha enviado un filtro de fecha
                            $filter_date = isset($_POST['filter_date']) ? $_POST['filter_date'] : '';
                            $filter_mname = isset($_POST['filter_mname']) ? $_POST['filter_mname'] : '';

                            if (!empty($filter_date)) {
                                $sql = "SELECT * FROM attendance LEFT JOIN student ON attendance.STUDENTID=student.STUDENTID WHERE LOGDATE = '$filter_date'";
                                if (!empty($filter_mname)) {
                                    $sql .= " AND MNAME = '$filter_mname'";
                                }
                            } elseif (!empty($filter_mname)) {
                                $sql = "SELECT * FROM attendance LEFT JOIN student ON attendance.STUDENTID=student.STUDENTID WHERE MNAME = '$filter_mname'";
                            } else {
                                $sql = "SELECT * FROM attendance LEFT JOIN student ON attendance.STUDENTID=student.STUDENTID";
                            }

                            $query = $conn->query($sql);

                            while ($row = $query->fetch_assoc()) {
                                ?>
                                <tr>
                                    <td><?php echo $row['FIRSTNAME'] . ', ' . $row['LASTNAME'] ; ?></td>
                                    <td><?php echo $row['STUDENTID']; ?></td>
                                    <td><?php echo $row['TIMEIN']; ?></td>
                                    <td><?php echo $row['TIMEOUT']; ?></td>
                                    <td><?php echo $row['LOGDATE']; ?></td>
                                    <td><?php echo $row['MNAME']; ?></td>
                                </tr>
                            <?php
                            }
                            ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function Export() {
            var conf = confirm("Please confirm if you wish to proceed in exporting the attendance into an Excel File");
            if (conf == true) {
                window.open("export.php", '_blank');
            }
        }
    </script>

    <script src="plugins/jquery/jquery.min.js"></script>
    <script src="plugins/bootstrap/js/bootstrap.min.js"></script>
    <script src="plugins/datatables/jquery.dataTables.min.js"></script>
    <script src="plugins/datatables-bs4/js/dataTables.bootstrap4.min.js"></script>
    <script src="plugins/datatables-responsive/js/dataTables.responsive.min.js"></script>
    <script src="plugins/datatables-responsive/js/responsive.bootstrap4.min.js"></script>
    <script src="js/dataTables.buttons.min.js"></script>
    <script src="js/jszip.min.js"></script>
    <script src="js/pdfmake.min.js"></script>
    <script src="js/vfs_fonts.js"></script>
    <script src="js/buttons.html5.min.js"></script>
    <script src="js/buttons.print.min.js"></script>
    <script src="js/export.js"></script>

    <script>
        $(document).ready(function () {
            $('#example1').DataTable({
                dom: 'Bfrtip',
                buttons: [
                    'copy', 'csv', 'excel', 'pdf', 'print'
                ]
            });
        });
    </script>
</body>
</html>
