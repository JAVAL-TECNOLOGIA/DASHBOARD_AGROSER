import pyodbc
from apps.connection.odbc_config import build_pyodbc_connection_string

#funcion de conexion a la base de datos del nisira
host = '192.168.100.5'
name = 'CMPA2022'
user = 'sa'
password = '@eisac2020'


try:
    connection_donluis2020 = pyodbc.connect(
        build_pyodbc_connection_string(host, name, user, password)
    )
    print("---> OK! Conexión Exitosa Don Luis 2020.")
except Exception as e:
    print("---> Conexion Fallida Don Luis 2020...", str(e))

