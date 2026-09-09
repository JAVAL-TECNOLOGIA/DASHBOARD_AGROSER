import pyodbc
from apps.connection.local_connection import open_connection
from apps.connection.odbc_config import build_pyodbc_connection_string


""" host = 'TIC-JHON\SQLEXPRESS'
name = 'INVERSIONESAJS'
user = 'django'
password = '@SADL.2023'

 """

#funcion de conexion a la base de datos del nisira
host = '192.168.100.5'
name = 'CMPA2022'
user = 'sa'
password = '@eisac2020'


try:
    connection_inversioneajs = open_connection(
        build_pyodbc_connection_string(host, name, user, password)
    )
    print("---> Conector inicializado.")
except Exception as e:
    print("---> Conexion Fallida...", str(e))








