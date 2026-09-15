"""Entorno local: SQLite y servicios externos deshabilitados."""
from .settings import *

LOCAL_DEVELOPMENT = True
# Las pruebas locales conservan su fuente aislada de SQL Server y de la red.
ERG_TXT_ROOT = os.getenv('ERG_TXT_ROOT', str(BASE_DIR / 'runtime_logs' / 'erg-source'))
ERA_TXT_ROOT = os.getenv('ERA_TXT_ROOT', str(BASE_DIR / 'runtime_logs' / 'era-source'))
OBP_TXT_ROOT = os.getenv('OBP_TXT_ROOT', str(BASE_DIR / 'runtime_logs' / 'obp-source'))
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
SECRET_KEY = 'agroservice-local-development-only'
DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'development.sqlite3'},
    'payroll': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'payroll-local.sqlite3'},
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cada petición refleja las modificaciones en las plantillas durante el desarrollo.
TEMPLATES[0]['APP_DIRS'] = False
TEMPLATES[0]['OPTIONS']['loaders'] = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]
# Evita compartir la sesión con otras aplicaciones locales en distintos puertos.
SESSION_COOKIE_NAME = 'agroservice_local_sessionid'
CSRF_COOKIE_NAME = 'agroservice_local_csrftoken'
