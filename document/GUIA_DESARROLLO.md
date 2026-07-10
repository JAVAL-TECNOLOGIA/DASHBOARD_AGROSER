# Guía de Desarrollo Rápido - PORTAL AEI

## 📝 Comandos de Inicio Rápido

### Activar Proyecto (Diario)
```bash
# 1. Navegar al directorio del proyecto
cd C:\Users\JOGUTIERREZ\Documents\PORTAL-AEI_DESARROLLO

# 2. Activar entorno virtual
.venv\Scripts\activate

# 3. Ejecutar servidor
python manage.py runserver

# 4. Abrir navegador en: http://127.0.0.1:8000
```

### Actualizar Dependencias
```bash
# Instalar nueva dependencia
pip install nombre_paquete

# Guardar en requirements.txt
pip freeze > requirements.txt

# O agregar manualmente a requirements.txt y ejecutar:
pip install -r requirements.txt
```

## 🛢️ Base de Datos - Comandos Frecuentes

### Migraciones
```bash
# Crear migración después de cambios en models.py
python manage.py makemigrations nombre_app

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations

# Migración específica
python manage.py migrate nombre_app 0001
```

### Datos de Prueba
```bash
# Crear superusuario
python manage.py createsuperuser

# Cargar datos de prueba (si existen)
python manage.py loaddata datos_prueba.json

# Exportar datos
python manage.py dumpdata app_name > datos_backup.json
```

## 📁 Estructura de Archivos Importantes

### Archivos de Configuración
- `reports/settings.py` - Configuración principal
- `reports/urls.py` - URLs principales
- `.env` - Variables de entorno (NO subir a Git)

### Archivos de Conexión BD
- `apps/connection/connect_*.py` - Conexiones a diferentes BD

### Templates Principales
- `templates/base/` - Plantillas base
- `templates/script/req_interno.html` - Requerimientos internos

### JavaScript Principal
- `static/core/js/script/script_req_interno.js` - Lógica requerimientos

## 🔧 Desarrollo - Mejores Prácticas

### Git Workflow
```bash
# Verificar estado
git status

# Crear nueva rama para feature
git checkout -b feature/nueva-funcionalidad

# Agregar cambios
git add .
git commit -m "DESCRIPCION: Descripción clara del cambio"

# Subir rama
git push origin feature/nueva-funcionalidad

# Merge a desarrollo
git checkout DESARROLLO
git merge feature/nueva-funcionalidad
```

### Debugging
```bash
# Modo debug activado
DEBUG=True en .env

# Ver logs en consola
python manage.py runserver --verbosity=2

# Shell de Django para pruebas
python manage.py shell
```

### Testing
```bash
# Ejecutar tests
python manage.py test

# Test específico
python manage.py test apps.nombre_app.tests

# Coverage (si está instalado)
coverage run manage.py test
coverage report
```

## 🎨 Frontend - Archivos Clave

### CSS Principal
- `static/assets/css/` - Estilos del tema
- Estilos inline en templates para componentes específicos

### JavaScript
- `static/assets/js/` - Librerías externas
- `static/core/js/script/` - Scripts personalizados
- DataTables, jQuery, Bootstrap incluidos

### Componentes UI
- Modales: Bootstrap modals
- Tablas: DataTables con AJAX
- Formularios: Django forms + Bootstrap
- Notificaciones: SweetAlert2

## 📊 Funcionalidades Principales

### Requerimientos Internos
- **Archivo**: `apps/script/views.py`
- **Template**: `templates/script/req_interno.html`
- **JS**: `static/core/js/script/script_req_interno.js`
- **Endpoints**: `/req_interno_*`

### Aprobaciones Masivas
- **Función**: `ejecutarAprobacionMasiva()` en JS
- **Backend**: Vista `UpdateReqInternos`
- **URL**: `/actualizar-req-interno/`

### Sistema de Usuarios
- **App**: `apps/login/`
- **Autenticación**: Django auth + sesiones
- **Permisos**: Por grupos y usuarios

## 🚨 Errores Comunes y Soluciones

### Error 500 - Server Error
1. Verificar logs en consola
2. Revisar configuración de BD en `.env`
3. Verificar migraciones: `python manage.py migrate`

### Error de CORS
1. Verificar `django-cors-headers` en INSTALLED_APPS
2. Configurar CORS_ALLOWED_ORIGINS en settings.py

### Error de Archivos Estáticos
```bash
# Recopilar archivos estáticos
python manage.py collectstatic --clear

# Verificar STATIC_URL y STATIC_ROOT en settings.py
```

### Error de SQL Server
1. Verificar servicio SQL Server activo
2. Comprobar credenciales en apps/connection/
3. Verificar ODBC Driver instalado

## 🔄 Workflow de Desarrollo

### Para Nueva Funcionalidad
1. Crear rama: `git checkout -b feature/nombre`
2. Desarrollar en apps correspondiente
3. Crear/actualizar templates si necesario
4. Agregar JavaScript si es frontend
5. Probar funcionalidad
6. Commit y push
7. Merge a DESARROLLO

### Para Bug Fix
1. Identificar problema
2. Crear rama: `git checkout -b bugfix/descripcion`
3. Corregir issue
4. Probar solución
5. Commit y merge

## 📱 URLs Importantes

- **Admin**: http://127.0.0.1:8000/admin/
- **Home**: http://127.0.0.1:8000/
- **Requerimientos**: http://127.0.0.1:8000/req_interno/
- **API Endpoints**: Ver `reports/urls.py`

## 💡 Tips de Productividad

### VS Code Extensions Recomendadas
- Python
- Django
- GitLens
- Auto Rename Tag
- Bracket Pair Colorizer

### Shortcuts Útiles
- `Ctrl + Shift + P` - Command Palette
- `Ctrl + `` - Terminal integrado
- `F5` - Debug
- `Ctrl + F5` - Run sin debug

---

**¡Happy Coding! 🚀**
