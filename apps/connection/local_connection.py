"""Permite iniciar el proyecto sin abrir conexiones empresariales en modo local."""
import pyodbc
import re
from django.conf import settings
from django.db import OperationalError


class UnavailableLocalConnection:
    def cursor(self, *args, **kwargs):
        raise OperationalError('SQL Server no está conectado en el entorno local de desarrollo.')

    def close(self):
        pass


def open_connection(*args, **kwargs):
    if getattr(settings, 'LOCAL_DEVELOPMENT', False):
        return UnavailableLocalConnection()
    if getattr(settings, 'SQLSERVER_VPN', False):
        connection_string = args[0]
        connection_string = re.sub(r'DRIVER=[^;]+', 'DRIVER={ODBC Driver 18 for SQL Server}', connection_string, count=1)
        server = re.search(r'(?:^|;)SERVER=(?:tcp:)?([^,;]+)', connection_string)
        trusted = server and server.group(1) == settings.SQLSERVER_TRUSTED_HOST
        connection_string += ';Encrypt=yes;TrustServerCertificate=' + ('yes' if trusted else 'no')
        args = (connection_string,) + args[1:]
        kwargs.setdefault('timeout', 8)
    return pyodbc.connect(*args, **kwargs)
