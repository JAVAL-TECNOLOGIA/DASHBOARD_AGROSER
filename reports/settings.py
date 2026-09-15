import os
from pathlib import Path
from django.contrib.messages import constants as messages
from apps.connection.odbc_config import get_django_db_options

# Define la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Fuente de boletas ERG para el arranque habitual de producción y WSGI.
# La cuenta del servicio debe tener acceso de lectura a esta carpeta.
ERG_TXT_ROOT = os.getenv(
    'ERG_TXT_ROOT',
    r'\\192.168.100.3\NISIRA\NISIRA_GCH\AGROSERVICE\EMPLEADOS REMIGEN GENERAL',
)
ERA_TXT_ROOT = os.getenv(
    'ERA_TXT_ROOT',
    r'\\192.168.100.3\NISIRA\NISIRA_GCH\AGROSERVICE\EMPLEADOS REGIMEN AGRARIO',
)
OBP_TXT_ROOT = os.getenv(
    'OBP_TXT_ROOT',
    r'\\192.168.100.3\NISIRA\NISIRA_GCH\AGROSERVICE\OBREROS PLANTA',
)


# Ruta para archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    str(BASE_DIR / 'static'),  # Convertir a cadena de texto
]


# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-mail.outlook.com'  # Servidor SMTP
EMAIL_PORT = 587  # Puerto SMTP
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'soporteti@agricoladonluis.com'  # Correo remitente
EMAIL_HOST_PASSWORD = '@TI2026.RAR'  # Contraseña del correo
DEFAULT_FROM_EMAIL = 'Recursos Humanos <soporteti@agricoladonluis.com>'




MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

PDF_MEDIA_URL = '/media/'
PDF_MEDIA_ROOT = str(BASE_DIR / 'media')  # Convertir a cadena de texto

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')  # Convertir a cadena de texto

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5250i4iq)yaoh=ew$buf$-$!8(25#kgg3(vq2k5jzi9jx8p%bu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['p5kyqq-ip-38-250-176-120.tunnelmole.net','oakstp-ip-38-250-176-120.tunnelmole.net','38.250.176.120', '192.168.10.3', '190.187.236.42', '127.0.0.1', 'localhost','192.168.100.3','38.43.135.224', 'ea2c-190-187-236-42.ngrok-free.app']

# Application definition

INSTALLED_APPS = [ 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.login',
    'apps.home',
    'apps.user',
    'apps.script',
    'apps.line_celulares',
    'apps.rrhh',
    'apps.contabilidad', 
    'apps.TIC',
    'apps.FITOSANIDAD',
    'apps.COSTOS',
    'apps.LOGISTICA',
    'apps.LEGAL',
    'apps.SEGURIDAD',
    'apps.CALIDAD',
    'apps.EVALUACIONES',
    'apps.APLICACIONES',
    'apps.RIEGO',
    'apps.PRODUCCIONUVA1',
    'apps.PRODUCCIONUVA2',
    'apps.PRODUCCIONPALTA',
    'apps.GERENCIA',
    'apps.GERENCIA_PRODUCCION',
    'apps.RIEGO_PALTA',
    'apps.RIEGO_UVA',
    'apps.PresupuestoAgricola',
    'apps.cartillas_agricolas',
    'apps.CONTROLLER_PROD',
    'apps.SALUD',
    'apps.SST',
    'apps.boletas',
    'apps.contratos',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
   
]

ROOT_URLCONF = 'reports.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR / 'templates')],  # Convertir a cadena de texto
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cartillas_agricolas.context_processors.cartillas_areas',
            ],
        },
    },
]

WSGI_APPLICATION = 'reports.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases




DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'PORTAL_AEI',
        'USER': 'sa',
        'PASSWORD': '@eisac2020',
        'HOST': '192.168.100.5',
        'PORT': '1433',
        'OPTIONS': get_django_db_options(),
    },
}

DATABASES['payroll'] = {
    **DATABASES['default'],
    'NAME': os.getenv('PAYSLIP_DB_NAME', 'CMPA2022'),
    'CONN_MAX_AGE': int(os.getenv('PAYSLIP_CONN_MAX_AGE', '300')),
}

# Cache local de lecturas repetidas de boletas (puede sustituirse por Redis en
# varios servidores sin cambiar el código de la aplicación).
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'agroservice-boletas-cache',
        'TIMEOUT': 300,
    }
}

PAYSLIP_COMPANY_ID = os.getenv('PAYSLIP_COMPANY_ID', '001')
PAYSLIP_CURRENCY = os.getenv('PAYSLIP_CURRENCY', 'N')



# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'es-pe'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'user.User'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
