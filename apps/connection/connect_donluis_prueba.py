import pyodbc
from apps.connection.odbc_config import build_pyodbc_connection_string


host = '192.168.100.5'
name = 'CMPA2022'
user = 'sa'
password = '@eisac2020'

try:
    connection_donluis_prueba = pyodbc.connect(
        build_pyodbc_connection_string(host, name, user, password, mars=True)
    )
    print("---> OK! Conexión Exitosa DL_PRUEBA.")
except Exception as e:
    print("---> Conexion Fallida...", str(e))
