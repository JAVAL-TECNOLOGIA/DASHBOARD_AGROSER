import pyodbc
from apps.connection.local_connection import open_connection
from apps.connection.odbc_config import build_pyodbc_connection_string

#funcion de conexion a la base de datos del nisira


""" host = 'JAVAL-TECNOLOGI'
name = 'PORTAL_AEI'
user = 'sa'
password = 'SADL.2024'
 """


host = '192.168.100.5'
name = 'PORTAL_AEI'
user = 'sa'
password = '@eisac2020'

try:
    connection_portalaei = open_connection(
        build_pyodbc_connection_string(host, name, user, password, mars=True)
    )
    print("---> Conector inicializado PORTAL AEI.")
except Exception as e:
    print("---> Conexion Fallida...", str(e))
