#  Manual de Instalación - PORTAL AEI DESARROLLO

##  Descripción del Proyecto
Portal web para la gestión de requerimientos internos de almacén, aprobaciones masivas y administración de recursos empresariales para Don Luis.

## 📋 Requisitos Previos

### Software Necesario
- **Python 3.7 - 3.8** (Recomendado 3.8)
- **SQL Server** (2016 o superior)
- **Git** para control de versiones
- **Visual Studio Code** (Recomendado)

### Drivers de Base de Datos
- **ODBC Driver for SQL Server** (versión 17 o superior)
- **Microsoft Visual C++ 14.0** o superior

## 🚀 Pasos de Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/PORTALDONLUIS/DASHBOARD_DONLUIS.git
cd PORTAL-AEI_DESARROLLO
```

### 2. Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### 4. Configuración de Base de Datos

#### 4.1 Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# Configuración de Base de Datos Principal
DB_NAME=PORTALAEI
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=1433

# Configuración de Bases de Datos Adicionales
DB_DONLUIS_NAME=DONLUIS
DB_DONLUIS_USER=tu_usuario
DB_DONLUIS_PASSWORD=tu_contraseña
DB_DONLUIS_HOST=localhost

DB_CAMPOVERDE_NAME=CAMPOVERDE
DB_CAMPOVERDE_USER=tu_usuario
DB_CAMPOVERDE_PASSWORD=tu_contraseña
DB_CAMPOVERDE_HOST=localhost

# Configuración de Seguridad
SECRET_KEY=tu_clave_secreta_muy_segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de Redis (opcional)
REDIS_URL=redis://localhost:6379/0
```

#### 4.2 Configurar Conexiones de Base de Datos
Verificar y ajustar las conexiones en:
- `apps/connection/connect_portalaei.py`
- `apps/connection/connect_donluis.py`
- `apps/connection/connect_campoverde.py`

### 5. Migraciones de Base de Datos
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 6. Recopilar Archivos Estáticos
```bash
python manage.py collectstatic --noinput
```

##  Ejecutar el Proyecto

### Modo Desarrollo
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar servidor de desarrollo
python manage.py runserver

# El proyecto estará disponible en: http://127.0.0.1:8000
```

### Modo Producción
```bash
# Configurar variables de entorno para producción
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Usar un servidor WSGI como Gunicorn
pip install gunicorn
gunicorn reports.wsgi:application --bind 0.0.0.0:8000
```

## 📁 Estructura del Proyecto

```
PORTAL-AEI_DESARROLLO/
├── apps/                   # Aplicaciones Django
│   ├── aei_help/          # Sistema de ayuda
│   ├── ALMACEN/           # Gestión de almacén
│   ├── connection/        # Conexiones a BD
│   ├── login/             # Autenticación
│   ├── script/            # Scripts y vistas principales
│   └── ...                # Otras apps
├── static/                # Archivos estáticos
│   ├── assets/           # CSS, JS, imágenes
│   └── core/             # Scripts personalizados
├── templates/             # Plantillas HTML
├── media/                 # Archivos subidos
├── document/             # Documentación
├── reports/              # Configuración Django
├── manage.py             # Script de gestión Django
└── requirements.txt      # Dependencias
```

## 🔧 Configuración Adicional

### NGROK (Túnel Local)
Si necesitas exponer el servidor local:
```bash
# Ejecutar ngrok (incluido en el proyecto)
./ngrok.exe http 8000
```

### Base de Datos
- **Motor**: SQL Server
- **Múltiples bases de datos**: PORTALAEI, DONLUIS, CAMPOVERDE
- **ORM**: Django ORM + consultas SQL nativas
- **Procedimientos almacenados**: Incluidos en scripts SQL

### Características Principales
- ✅ Gestión de requerimientos internos
- ✅ Aprobaciones masivas
- ✅ Sistema multiempresa
- ✅ Autenticación y permisos
- ✅ Reportes y dashboard
- ✅ API REST
- ✅ Interfaz responsiva

## 🛠️ Comandos Útiles

```bash
# Verificar estado del proyecto
python manage.py check

# Crear nueva aplicación
python manage.py startapp nombre_app

# Shell interactivo de Django
python manage.py shell

# Limpiar sesiones expiradas
python manage.py clearsessions

# Verificar migraciones pendientes
python manage.py showmigrations

# Crear datos de prueba (si existen fixtures)
python manage.py loaddata nombre_fixture.json
```

## 🐛 Solución de Problemas Comunes

### Error de Conexión a SQL Server
1. Verificar que SQL Server esté ejecutándose
2. Confirmar credenciales en archivo `.env`
3. Verificar firewall y puertos (1433)
4. Instalar ODBC Driver for SQL Server

### Error de Dependencias
```bash
# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Error de Archivos Estáticos
```bash
# Recopilar archivos estáticos
python manage.py collectstatic --clear --noinput
```

### Error de Permisos
```bash
# En Windows, ejecutar como administrador
# En Linux/Mac, verificar permisos de directorio
chmod -R 755 static/
chmod -R 755 media/
```

## 📞 Soporte

Para soporte técnico o consultas:
- **Desarrollador**: JOGUTIERREZ
- **Empresa**: DON LUIS
- **Email**: soporteti@agricoladonluis.com

## 📄 Licencia

Proyecto propietario de DON LUIS. Todos los derechos reservados.

---

**Última actualización**: Agosto 2025
**Versión**: 1.0
**Estado**: Desarrollo Activo
