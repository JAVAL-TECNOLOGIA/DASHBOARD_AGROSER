"""Desarrollo con SQL Server real por VPN; confianza TLS autorizada por el usuario."""
from copy import deepcopy
from . import settings as original
from .settings_local import *

LOCAL_DEVELOPMENT = False
SQLSERVER_VPN = True
SQLSERVER_TRUSTED_HOST = '192.168.100.5'
ERG_TXT_ROOT = os.getenv('ERG_TXT_ROOT', r'\\192.168.100.3\NISIRA\NISIRA_GCH\AGROSERVICE\EMPLEADOS REMIGEN GENERAL')
ERA_TXT_ROOT = os.getenv('ERA_TXT_ROOT', r'\\192.168.100.3\NISIRA\NISIRA_GCH\AGROSERVICE\EMPLEADOS REGIMEN AGRARIO')
OBP_TXT_ROOT = os.getenv('OBP_TXT_ROOT', r'\\192.168.100.3\NISIRA\NISIRA_GCH\AGROSERVICE\OBREROS PLANTA')
DATABASES = deepcopy(original.DATABASES)
for database in DATABASES.values():
    database['OPTIONS'] = {
        'driver': 'ODBC Driver 18 for SQL Server',
        'connection_timeout': 8,
        'extra_params': 'Encrypt=yes;TrustServerCertificate=yes',
    }
    database['CONN_MAX_AGE'] = 60

# Mantener las sesiones de desarrollo en el equipo, sin escribirlas en SQL Server.
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = str(BASE_DIR / 'runtime_logs')
SESSION_COOKIE_NAME = 'agroservice_vpn_sessionid'
CSRF_COOKIE_NAME = 'agroservice_vpn_csrftoken'
