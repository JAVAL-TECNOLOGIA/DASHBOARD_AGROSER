# Análisis para el módulo "Cartillas Agrícolas > Evaluaciones"

**Fecha:** 23 de marzo de 2025  
**Referencia:** Módulo Presupuesto Agrícola  
**Objetivo:** Documentar el patrón del sistema y definir la estrategia de implementación del nuevo módulo.

---

## 1. RESUMEN EJECUTIVO DEL ANÁLISIS

### Cómo está construido el sistema
El proyecto DASHBOARD_DONLUIS es un sistema Django 2.1 con múltiples apps modulares. Cada módulo se integra mediante:
- **Prefijo URL único** (ej: `presupuesto-agricola/`, `evaluaciones/`)
- **Inclusión en `reports/urls.py`** con `path('prefijo/', include('apps.NombreApp.urls'))`
- **Menú/sidebar** definido en `templates/base/sidebar.html` con bloques condicionales `{% if perms.APP.permission %}`
- **Layout sin herencia**: cada template incluye explícitamente `header`, `sidebar` y `footer`; no usa `{% extends %}`
- **Datos**: consultas directas a SQL Server vía pyodbc (`connection_portalaei`, `connection_donluis`, etc.)
- **Frontend**: jQuery, Bootstrap 4, DataTables, SweetAlert; JS modular por carpeta de app

### Cómo está construido Presupuesto Agrícola
Es una app modular con **subapps por funcionalidad** (lotes, fundos, mapeo, produccion, consolidado, etc.). Cada subapp tiene su `urls.py` y `views.py`. Las vistas principales son `TemplateView` con `get_context_data`; las APIs CRUD son clases `View` con métodos `get/post/put/delete`. Usa `connection_portalaei` (BD PORTAL_AEI). Los permisos se definen en un modelo con `managed=False`.

### Conclusión: patrón recomendado para el nuevo módulo
Crear una **nueva app `CartillasAgricola`** (o `Cartillas_Agricola` según convención del proyecto) con:
- Prefijo URL `cartillas-agricolas/`
- Subapp `evaluaciones` dentro de ella
- Menú padre "Cartillas Agrícolas" con opción "Evaluaciones"
- Estructura de archivos y layout siguiendo Presupuesto Agrícola
- **No** reutilizar la app EVALUACIONES existente (es de presupuestos/costos por empresa)

---

## 2. MAPA TÉCNICO DEL MÓDULO "PRESUPUESTO AGRÍCOLA"

### Rutas
| Ruta completa | Nombre URL | Vista |
|---------------|------------|-------|
| `presupuesto-agricola/lotes/` | presupuesto_agricola_lotes | PresupuestoLotesView |
| `presupuesto-agricola/fundos/` | presupuesto_agricola_fundos | PresupuestoFundosView |
| `presupuesto-agricola/tipo-planta/` | presupuesto_agricola_tipo_planta | PresupuestoTipoPlantaView |
| `presupuesto-agricola/asignacion/` | presupuesto_agricola_asignacion_ingenieros | asignacion_ingenieros |
| `presupuesto-agricola/mapeo/` | presupuesto_agricola_mapeo | mapeo |
| `presupuesto-agricola/produccion_uva/` | presupuesto_agricola_produccion_uva | produccion_uva |
| `presupuesto-agricola/tipo-trabajo/` | presupuesto_agricola_tipo_trabajo | PresupuestoTipoTrabajoView |
| `presupuesto-agricola/config_tipo_trabajo/` | presupuesto_agricola_config_tipo_trabajo | config_tipo_trabajo |
| `presupuesto-agricola/parametro_costo_base/` | presupuesto_agricola_parametro_costo_base | parametro_costo_base |
| `presupuesto-agricola/presupuesto/` | presupuesto_agricola_presupuesto_in | PresupuestoAgricolaView |
| `presupuesto-agricola/consolidado/` | presupuesto_agricola_consolidados | evaluacion_fertilidad |
| `presupuesto-agricola/plantillas/` | test_template_evaluacion_fertilidad | (TestPlantillas) |
| `presupuesto-agricola/plantillas_offline/` | test_plantilla_offline | (TestPlantillasOffline) |

### Vistas
- **Vista principal**: `TemplateView` con `template_name` y `get_context_data` para cargar catálogos (fundos, campañas, variedades, etc.).
- **APIs CRUD**: Clases `View` con `@method_decorator(csrf_exempt)` y métodos `get/post/put/delete`.
- **Algunas vistas** usan `permission_required = 'modulo_presupuesto_agricola'` como atributo de clase (sin `PermissionRequiredMixin` explícito; el control efectivo es vía menú).

### Templates/componentes
| Template | Descripción |
|----------|-------------|
| `PresupuestoAgricola/rrhh_lotes.html` | Listado lotes con DataTable, filtro campaña, modales CRUD |
| `PresupuestoAgricola/mapeo.html` | Cards de fundos, selector campaña, modales lotes y mapeo CRUD |
| `PresupuestoAgricola/consolidado/consolidado_main.html` | Layout con tabs (Compras, Costo Prod. VID) |
| `PresupuestoAgricola/consolidado/compras.html` | Tab content (tabla compras) |
| `PresupuestoAgricola/consolidado/costo_prod_vid.html` | Tab content |

**Layout estándar de cada template:**
```html
{% load static %}
{% include 'base/header.html' %}
{% include 'base/sidebar.html' %}

{% block css %}
<!-- DataTables, datepicker, etc. -->
{% endblock %}

<div id="content" class="content">
    <div class="panel panel-inverse">
        <div class="panel-heading">...</div>
        <div class="panel-body">...</div>
    </div>
</div>

{% include 'base/footer.html' %}

{% block js %}
<!-- jQuery, DataTables, scripts propios -->
{% endblock %}
```

### Servicios
- **Conexión BD**: `apps.connection.connect_portalaei.connection_portalaei` (pyodbc a SQL Server PORTAL_AEI)
- **Queries**: directas con `cursor.execute()`, sin ORM
- **APIs**: respuestas JSON con `JsonResponse({'status': 'success', 'data': ...})`

### Menú
- **Ubicación**: `templates/base/sidebar.html` (aprox. líneas 1075-1200)
- **Estructura**:
  - Bloque `{% if perms.PRESUPUESTO_AGRICOLA.modulo_presupuesto_agricola %}`
  - Menú padre `<li class="has-sub">` con `javascript:;` y submenú `<ul class="sub-menu">`
  - Subopciones con `{% if perms.PRESUPUESTO_AGRICOLA.presupuesto_fundos %}`, etc.
  - Enlaces: `{% url 'presupuesto_agricola_fundos' %}`

### Permisos
- **Modelo**: `PresupuestoAgricola.models.PresupuestoAgricolaPermission` (managed=False)
- **Definidos en Meta.permissions**: `modulo_presupuesto_agricola`, `presupuesto_agricola_lotes`, `presupuesto_agricola_fundos`, `presupuesto_agricola_asignacion_ingenieros`
- **Inconsistencia**: El sidebar usa también `presupuesto_tipo_planta`, `mapeo`, `produccion_uva`, que NO aparecen en el modelo actual. Pueden venir de migraciones o estar faltantes.

### Archivos clave
```
apps/PresupuestoAgricola/
├── urls.py                    # Router a subapps
├── models.py                  # Permisos
├── lotes/urls.py, views.py
├── fundos/urls.py, views.py
├── mapeo/urls.py, views.py
├── produccion/urls.py, views.py
├── consolidado/urls.py, views.py
├── tipo_planta/urls.py, views.py
└── ...

templates/PresupuestoAgricola/
├── rrhh_lotes.html
├── mapeo.html
├── consolidado/
│   ├── consolidado_main.html
│   ├── compras.html
│   └── costo_prod_vid.html
└── ...

static/core/js/PRESUPUESTO_AGRICOLA/
├── mapeo.js
├── produccion.js
├── consolidado/
│   ├── compras.js
│   └── costo_prod_vid.js
└── ...
```

### Flujo general
1. Usuario accede a `/presupuesto-agricola/lotes/`
2. Vista `PresupuestoLotesView` ejecuta queries a PORTAL_AEI (FUNDO, VARIEDAD, CAMPANIA)
3. Renderiza `rrhh_lotes.html` con contexto (fundos, variedades, campanias)
4. Frontend carga DataTable vía `$.get('/presupuesto-agricola/lotes/api/lotes/')`
5. CRUD se hace con `$.ajax` POST/PUT/DELETE a la misma API

---

## 3. PATRÓN DE IMPLEMENTACIÓN RECOMENDADO PARA "CARTILLAS AGRÍCOLAS > EVALUACIONES"

### Estructura recomendada
```
apps/CartillasAgricola/          # o Cartillas_Agricola
├── __init__.py
├── apps.py
├── models.py                    # Permisos
├── urls.py                      # path('evaluaciones/', include(...))
├── evaluaciones/
│   ├── __init__.py
│   ├── urls.py
│   └── views.py
└── (futuras subapps si se necesitan)

templates/CartillasAgricola/
├── evaluaciones/
│   └── dashboard.html           # Vista principal (Fase 3+)

static/core/js/CARTILLAS_AGRICOLA/
└── evaluaciones/
    └── dashboard.js
```

### Archivos a crear (por fases)
| Fase | Archivo | Descripción |
|------|---------|-------------|
| 2 | `apps/CartillasAgricola/` (estructura) | App nueva |
| 2 | `reports/urls.py` | `path('cartillas-agricolas/', include(...))` |
| 2 | `templates/base/sidebar.html` | Bloque menú Cartillas Agrícolas > Evaluaciones |
| 3 | `templates/CartillasAgricola/evaluaciones/dashboard.html` | Vista base con layout |
| 3 | `apps/CartillasAgricola/evaluaciones/views.py` | TemplateView simple |
| 4 | `static/core/js/CARTILLAS_AGRICOLA/evaluaciones/dashboard.js` | Filtros mock, tabla mock |
| 5 | APIs para PlantillaRegistro, PlantillaCampo | (futuro) |

### Qué reutilizar
- **Layout base**: `{% include 'base/header.html' %}`, `{% include 'base/sidebar.html' %}`, `{% include 'base/footer.html' %}`
- **Estructura de panel**: `<div class="panel panel-inverse">`, `panel-heading`, `panel-body`
- **Patrón de permisos**: modelo con `managed=False` y permisos en Meta
- **Patrón de subapps**: `urls.py` con `include` a subapps
- **Convención de rutas API**: `path('api/...', View.as_view())`
- **Estilos**: DataTables, Bootstrap, `static/core/css/css.css`

### Qué no copiar tal cual
- **Credenciales hardcodeadas**: `connect_portalaei` tiene credenciales en código; para PlantillaRegistro verificar si se usará otra conexión o variables de entorno
- **Permisos incompletos**: Evitar la incoherencia sidebar vs models; definir todos los permisos usados en el menú
- **Include con case incorrecto**: En `consolidado_main.html` se usa `presupuestoAgricola`; usar `CartillasAgricola` de forma consistente
- **Duplicación de lógica de mapeo**: El mapeo de PresupuestoAgricola es CRUD de plantas por lote, no mapa geográfico; el mapa del nuevo módulo será distinto

### Cómo dejar preparado para la siguiente fase
- Crear la vista dashboard con **placeholders** para: zona de filtros, zona KPIs, zona tabla, zona mapa
- Usar IDs y clases CSS predefinidas (`#filtros-evaluaciones`, `#kpis-evaluaciones`, `#tabla-registros`, `#mapa-evaluaciones`)
- Dejar endpoints API mock que devuelvan `[]` o estructura vacía
- Documentar en el template qué datos llegará cada zona

---

## 4. RIESGOS Y OBSERVACIONES

### Riesgos de acoplamiento
- **EVALUACIONES existente**: La app `apps.EVALUACIONES` ya existe y maneja presupuestos/costos. No confundir ni mezclar con Cartillas Agrícolas > Evaluaciones.
- **connection_portalaei vs connect_donluis**: PresupuestoAgricola usa `connect_portalaei` (PORTAL_AEI). Las tablas PlantillaRegistro, PlantillaCampo pueden estar en otra BD. Verificar dónde residen antes de implementar.
- **Dependencias de mapeo**: PRODUCCIONUVA1 y PresupuestoAgricola comparten lógica de mapeo (GuardarMapeoNuevo, etc.). El mapa geográfico del nuevo módulo debe ser independiente.

### Riesgos de romper navegación
- Modificar `sidebar.html` sin respetar la indentación y estructura de los bloques `{% if %}` puede ocultar otros menús.
- El nombre de la URL (`name='...'`) debe coincidir exactamente con lo usado en `{% url %}`.

### Riesgos de copiar módulos demasiado específicos
- **Consolidado**: Tiene lógica muy específica (vw_compras_lotes, compras, costo_prod_vid). No copiar la lógica de negocio, solo el patrón de tabs.
- **Mapeo PresupuestoAgricola**: Es CRUD de mapeo de plantas, no mapa geográfico. El mapa de Evaluaciones será diferente (Leaflet/OpenLayers con coordenadas de lotes).

### Recomendaciones para aislar el futuro mapa
- Crear `static/core/js/CARTILLAS_AGRICOLA/evaluaciones/mapa.js` como módulo separado.
- El mapa debe recibir datos vía parámetros o API específica del módulo; no depender de scripts globales.
- Usar un contenedor con ID único (`#mapa-evaluaciones`) para evitar conflictos con otros mapas del sistema.
- Si se usa Leaflet, cargarlo solo en la vista de Evaluaciones (no global).

### Recomendaciones para no sobrediseñar
- En Fase 2-3: solo menú, ruta y vista vacía o con placeholders.
- En Fase 4: filtros y tabla con datos mock; no conectar aún a PlantillaRegistro/PlantillaCampo.
- Evitar crear servicios/repositorios genéricos si el patrón actual es queries directas en views.

---

## 5. PLAN DE FASES SIGUIENTES

### Fase 2: Menú y navegación
- Crear app `CartillasAgricola` en `apps/`
- Registrar en `INSTALLED_APPS`
- Agregar `path('cartillas-agricolas/', include('apps.CartillasAgricola.urls'))` en `reports/urls.py`
- Crear `models.py` con permisos: `modulo_cartillas_agricola`, `cartillas_evaluaciones`
- Crear estructura `evaluaciones/` con `urls.py` y vista placeholder
- Agregar bloque en `sidebar.html`: menú padre "Cartillas Agrícolas", subopción "Evaluaciones"
- Verificar que la ruta `/cartillas-agricolas/evaluaciones/` responde

### Fase 3: Vista base y layout
- Crear `templates/CartillasAgricola/evaluaciones/dashboard.html`
- Aplicar layout: header, sidebar, footer, `#content` con panel
- Dejar secciones con placeholders: filtros, KPIs, tabla, mapa
- Estructura de columnas: izquierda (tabla) y derecha (mapa) con grid Bootstrap

### Fase 4: Integración de filtros mock
- Añadir controles: cartilla, fecha, lote, evaluador, métrica principal
- Cargar opciones mock (arrays estáticos o API que devuelva `[]`)
- Tabla con DataTable vacía o con filas de ejemplo
- KPIs con valores 0 o placeholder
- Script `dashboard.js` para manejar filtros y recarga (sin lógica real)

### Fase 5: Conexión futura a PlantillaRegistro + PlantillaCampo
- Definir BD de origen (PORTAL_AEI, Don Luis u otra)
- Crear APIs: listado de registros, detalle, catálogo de campos
- Implementar cruce PlantillaCampo vs PlantillaRegistro.DataJson.body
- Conectar KPIs y tabla a datos reales
- Integrar mapa con coordenadas de lotes (si existen en BD)

---

## ANEXO: Observaciones adicionales

### app_label y permisos
- PresupuestoAgricola usa `perms.PRESUPUESTO_AGRICOLA` en el sidebar. El `app_label` por defecto es `PresupuestoAgricola`. Si hay problemas, definir `app_label = 'PRESUPUESTO_AGRICOLA'` en el `AppConfig` o en el Meta del modelo de permisos.

### Bug conocido
- En `consolidado_main.html` línea 61: `{% include 'presupuestoAgricola/consolidado/compras.html' %}` — debería ser `PresupuestoAgricola` (PascalCase) para consistencia en entornos case-sensitive.

### Conexiones existentes
- `connect_portalaei` → PORTAL_AEI (usada por PresupuestoAgricola, contabilidad, TIC, etc.)
- `connect_donluis` → Don Luis
- `connect_campoverde`, `connect_inversioneajs` → otras empresas
