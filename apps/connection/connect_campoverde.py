import pyodbc
import threading
from apps.connection.odbc_config import build_pyodbc_connection_string

#funcion de conexion a la base de datos del nisira
""" host = 'TIC-JHON\SQLEXPRESS'
name = 'CAMPOVERDE'
user = 'django'
password = '@SADL.2023' """
 


#funcion de conexion a la base de datos del nisira

host = '192.168.100.5'
name = 'CMPA2022'
user = 'sa'
password = '@eisac2020'


connection_string = build_pyodbc_connection_string(host, name, user, password, mars=True)

# Variable para almacenar la conexión original (para mantener compatibilidad)
connection_campoverde = None

# Clase para manejar conexiones por hilo
class ThreadLocalConnection_cv(threading.local):
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        if self.connection is None:
            try:
                self.connection = pyodbc.connect(connection_string)
            except Exception as e:
                print("---> Error al crear conexión:", str(e))
                raise
        return self.connection
    
    def close(self):
        if self.connection is not None:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None

# Crear instancia thread-local
thread_local_connection_cv = ThreadLocalConnection_cv()

# Establecer conexión inicial (para compatibilidad con el código existente)
try:
    connection_campoverde = pyodbc.connect(connection_string)
    print("---> OK! Conexión Exitosa Campoverde.")
except Exception as e:
    print("---> Conexion Fallida...", str(e))

# Función para obtener una conexión para el hilo actual
def get_thread_connection_cv():
    """
    Retorna una conexión exclusiva para el hilo actual.
    Cada hilo tendrá su propia conexión independiente.
    """
    return thread_local_connection_cv.get_connection()

# Función para cerrar la conexión del hilo actual
def close_thread_connection_cv():
    """
    Cierra la conexión del hilo actual.
    Es recomendable llamar a esta función cuando el hilo termina su trabajo.
    """
    thread_local_connection_cv.close()
