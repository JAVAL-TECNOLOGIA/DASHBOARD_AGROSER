import pyodbc
from apps.connection.odbc_config import build_pyodbc_connection_string

# Conexión a APP_AGRICOLA - PlantillaRegistro, PlantillaCampo, etc.

host = '192.168.100.5'
name = 'PORTAL_AEI'
user = 'sa'
password = '@eisac2020'

connection_app_agricola = None

try:
    connection_app_agricola = pyodbc.connect(
        build_pyodbc_connection_string(host, name, user, password, mars=True)
    )
    print("---> OK! Conexión Exitosa APP_AGRICOLA.")
except Exception as e:
    print("---> Conexión Fallida APP_AGRICOLA:", str(e))
