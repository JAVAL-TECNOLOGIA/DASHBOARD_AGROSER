import pyodbc
from apps.connection.local_connection import open_connection
from apps.connection.odbc_config import build_pyodbc_connection_string


host = '192.168.100.5'
name = 'CMPA2022'
user = 'sa'
password = '@eisac2020'

try:
    connection_donluis_prueba = open_connection(
        build_pyodbc_connection_string(host, name, user, password, mars=True)
    )
    print("---> Conector inicializado DL_PRUEBA.")
except Exception as e:
    print("---> Conexion Fallida...", str(e))
