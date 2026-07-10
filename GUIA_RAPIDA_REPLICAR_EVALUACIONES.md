# 🚀 GUÍA RÁPIDA: REPLICAR EVALUACIONES A OTROS MÓDULOS

## 📌 CONTEXTO
El sistema de evaluación de desempeño funciona en **PRODUCCIONUVA1 (ID_AREA=13)**.
Los **procedimientos almacenados YA FUNCIONAN** para todos los módulos (solo se diferencian por `id_area`).

---

## 🎯 OBJETIVO
Replicar el sistema de evaluaciones a otro módulo siguiendo la estructura de PRODUCCIONUVA1.

---

## 📋 PASOS SIMPLIFICADOS

### PASO 1: Identificar ID_AREA del módulo destino

**Ejecutar en SQL Server:**
```sql
SELECT ID_AREA, NOMBRE, DESCRIPCION 
FROM AREA 
WHERE NOMBRE LIKE '%[nombre del módulo]%'
```

**Ejemplo para PRODUCCIONUVA2:**
```sql
SELECT ID_AREA, NOMBRE, DESCRIPCION 
FROM AREA 
WHERE NOMBRE LIKE '%UVA%' OR NOMBRE LIKE '%PRODUCCION%'
```

**Guardar el ID_AREA encontrado** - Lo usaremos en todos los archivos.

---

### PASO 2: Copiar y Adaptar Backend (views.py)

#### 2.1 Copiar estas clases desde `apps/PRODUCCIONUVA1/views.py` (líneas 3580-4800):
- `class evaluacion_desempeño(TemplateView)` (línea 3580)
- `class ObjetivosEvaluacionView(View)` (línea 3585)
- `class DetallesObjetivosView(View)` (después de ObjetivosEvaluacionView)
- `class CompetenciasEvaluacionDetailView(View)` (línea 3977)
- `class FaseIntermediaEvaluacionesView(View)` (línea 4285)
- `class DetallesEvaluacionModalView(View)` (línea 4434)

#### 2.2 Pegar en `apps/[NOMBRE_MODULO]/views.py`

#### 2.3 Realizar SOLO estos reemplazos:

| Buscar | Reemplazar con |
|--------|----------------|
| `class evaluacion_desempeño` | `class evaluacion_desempeño_[codigo_modulo]` |
| `'modulo_produccion_uva_1'` | `'modulo_[nombre_modulo]'` |
| `'PRODUCCION_UVA1/components/DonLuis/eva_desempeno/rrhh_evaluacion_desempeño.html'` | `'[NOMBRE_MODULO]/components/[Empresa]/eva_desempeno/rrhh_evaluacion_desempeño.html'` |
| `13` (en llamadas a SP) | `[TU_ID_AREA]` |

**⚠️ CRÍTICO:** Buscar y reemplazar el `13` SOLO en estas líneas específicas:

```python
# En ObjetivosEvaluacionView - método get:
cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @id_campania=?", [13, campania])
# CAMBIAR A:
cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @id_campania=?", [TU_ID_AREA, campania])

# En DetallesObjetivosView - método get:
cursor.execute("EXEC RRHH_EV_OBJETIVOS 13")
# CAMBIAR A:
cursor.execute("EXEC RRHH_EV_OBJETIVOS TU_ID_AREA")

# En CompetenciasEvaluacionDetailView - método get:
cursor.execute("EXEC RRHH_EV_COMPETENCIAS 13")
# CAMBIAR A:
cursor.execute("EXEC RRHH_EV_COMPETENCIAS TU_ID_AREA")
```

**Comando para encontrar todas las ocurrencias:**
```bash
grep -n "13" apps/[NOMBRE_MODULO]/views.py | grep -E "EXEC|id_area"
```

---

### PASO 3: Configurar Rutas (urls.py)

#### 3.1 Agregar imports en `apps/[NOMBRE_MODULO]/urls.py`:
```python
from .views import (
    evaluacion_desempeño_[codigo_modulo],
    ObjetivosEvaluacionView,
    DetallesObjetivosView,
    CompetenciasEvaluacionDetailView,
    FaseIntermediaEvaluacionesView,
    DetallesEvaluacionModalView
)
```

#### 3.2 Agregar rutas:
```python
urlpatterns = [
    # ... rutas existentes ...
    
    # EVALUACIÓN DE DESEMPEÑO
    path('evaluacion-desempeno/', 
         evaluacion_desempeño_[codigo_modulo].as_view(), 
         name='evaluacion_desempeno_[codigo_modulo]'),
    
    path('objetivos_evaluacion/', 
         ObjetivosEvaluacionView.as_view(), 
         name='objetivos_evaluacion'),
    
    path('detalles_objetivos/', 
         DetallesObjetivosView.as_view(), 
         name='detalles_objetivos'),
    
    path('detalles_competencias/', 
         CompetenciasEvaluacionDetailView.as_view(), 
         name='detalles_competencias'),
    
    path('detalles_competencias/<int:id>/', 
         CompetenciasEvaluacionDetailView.as_view(), 
         name='detalles_competencias_detail'),
    
    path('api/fase-intermedia/', 
         FaseIntermediaEvaluacionesView.as_view(), 
         name='fase_intermedia_evaluaciones'),
    
    path('api/detalles-evaluacion-modal/', 
         DetallesEvaluacionModalView.as_view(), 
         name='detalles_evaluacion_modal'),
]
```

---

### PASO 4: Copiar Templates HTML

#### 4.1 Crear estructura:
```
templates/[NOMBRE_MODULO]/components/[Empresa]/eva_desempeno/
```

#### 4.2 Copiar archivos desde:
```
DESDE: templates/PRODUCCION_UVA1/components/DonLuis/eva_desempeno/
HACIA: templates/[NOMBRE_MODULO]/components/[Empresa]/eva_desempeno/

Archivos:
- rrhh_evaluacion_desempeño.html
```

#### 4.3 En el HTML copiado, reemplazar:

| Buscar | Reemplazar con |
|--------|----------------|
| `PRODUCCION UVA 1` | `[NOMBRE VISIBLE DEL MÓDULO]` |
| `/produccionuva1/` | `/[nombre_modulo]/` |
| `id_area=13` | `id_area=[TU_ID_AREA]` |

**En la función JavaScript `filtrarPorCampania()`:**
```javascript
// BUSCAR:
objetivosTable.ajax.url("/produccionuva1/objetivos_evaluacion/?campania=" + campania).load();
intermedioTable.ajax.url("/produccionuva1/api/fase-intermedia/?id_area=13&campania=" + campania).load();

// REEMPLAZAR CON:
objetivosTable.ajax.url("/[nombre_modulo]/objetivos_evaluacion/?campania=" + campania).load();
intermedioTable.ajax.url("/[nombre_modulo]/api/fase-intermedia/?id_area=[TU_ID_AREA]&campania=" + campania).load();
```

---

### PASO 5: Agregar al Menú

Agregar entrada en el sidebar del módulo:

```html
<li>
    <a href="{% url 'evaluacion_desempeno_[codigo_modulo]' %}">
        <i class="fas fa-chart-line"></i>
        <span>Evaluación de Desempeño</span>
    </a>
</li>
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Backend
- [ ] ID_AREA identificado correctamente
- [ ] Clases copiadas a `views.py`
- [ ] TODOS los `13` en procedimientos almacenados reemplazados por el ID_AREA correcto
- [ ] Nombre de clase `evaluacion_desempeño` actualizado
- [ ] Template path actualizado
- [ ] Rutas agregadas a `urls.py`
- [ ] Imports correctos en `urls.py`

### Frontend - HTML
- [ ] Carpeta `eva_desempeno` creada
- [ ] Archivo HTML copiado
- [ ] URLs `/produccionuva1/` reemplazadas
- [ ] ID_AREA actualizado en HTML
- [ ] Función `filtrarPorCampania()` actualizada

### Configuración
- [ ] Entrada agregada al menú
- [ ] Servidor reiniciado

---

## 🧪 PRUEBAS

### 1. Probar Backend
```bash
python manage.py runserver
```

Acceder a:
```
http://localhost:8000/[nombre_modulo]/evaluacion-desempeno/
```

### 2. Verificar en Consola del Navegador
- Abrir DevTools (F12)
- Verificar que NO haya errores 404
- Verificar que las peticiones AJAX se hagan a las URLs correctas

### 3. Probar Funcionalidades
- [ ] La página carga correctamente
- [ ] El filtro de campaña funciona
- [ ] La tabla de objetivos carga datos
- [ ] La tabla de fase intermedia carga datos
- [ ] Se puede crear una nueva evaluación
- [ ] Se pueden editar evaluaciones existentes

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### Problema: "No se encontraron evaluaciones"
**Causa:** ID_AREA incorrecto
**Solución:** 
1. Verificar ID_AREA en la base de datos
2. Buscar TODAS las ocurrencias de `13` en el código
3. Reemplazar con el ID_AREA correcto

### Problema: Error 404 en peticiones AJAX
**Causa:** URLs no actualizadas
**Solución:**
```bash
# Buscar todas las URLs antiguas
grep -r "produccionuva1" apps/[NOMBRE_MODULO]/
grep -r "produccionuva1" templates/[NOMBRE_MODULO]/
```

### Problema: Las tablas no cargan datos
**Causa:** Procedimientos almacenados no reciben el ID_AREA correcto
**Solución:**
```sql
-- Probar manualmente los procedimientos
DECLARE @id_area INT = [TU_ID_AREA]
DECLARE @campania VARCHAR(20) = 'CAMP2025'

EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area, @campania
EXEC RRHH_EV_OBJETIVOS @id_area
EXEC RRHH_EV_COMPETENCIAS @id_area
EXEC SP_FASE_INTERMEDIA_EVALUACIONES @id_area, @campania
```

---

## 📊 EJEMPLO PARA PRODUCCIONUVA2

### Valores:
- **ID_AREA:** 14 (ejemplo)
- **NOMBRE_MODULO:** PRODUCCIONUVA2
- **nombre_modulo:** produccionuva2
- **Empresa:** DonLuis
- **codigo_modulo:** uva2

### Reemplazos en código:

```python
# views.py
class evaluacion_desempeño_uva2(TemplateView):
    permission_required = 'modulo_produccion_uva_2'
    template_name = 'PRODUCCIONUVA2/components/DonLuis/eva_desempeno/rrhh_evaluacion_desempeño.html'

# Procedimientos almacenados
cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @id_campania=?", [14, campania])
cursor.execute("EXEC RRHH_EV_OBJETIVOS 14")
cursor.execute("EXEC RRHH_EV_COMPETENCIAS 14")
```

```javascript
// JavaScript en HTML
objetivosTable.ajax.url("/produccionuva2/objetivos_evaluacion/?campania=" + campania).load();
intermedioTable.ajax.url("/produccionuva2/api/fase-intermedia/?id_area=14&campania=" + campania).load();
```

---

## 📝 RESUMEN DE ARCHIVOS

### Archivos a Modificar/Crear:

```
Backend (2 archivos):
├── apps/[NOMBRE_MODULO]/views.py (agregar ~1200 líneas)
└── apps/[NOMBRE_MODULO]/urls.py (agregar ~15 líneas)

Templates (1 archivo):
└── templates/[NOMBRE_MODULO]/components/[Empresa]/eva_desempeno/
    └── rrhh_evaluacion_desempeño.html

TOTAL: 3 archivos
```

---

## ⏱️ TIEMPO ESTIMADO

- Identificar ID_AREA: 5 min
- Copiar y adaptar Backend: 20 min
- Copiar y adaptar Template: 10 min
- Configurar rutas y menú: 10 min
- Testing: 15 min

**TOTAL: ~1 hora**

---

## 🎯 COMANDO PARA KIRO

```
Necesito replicar el sistema de evaluación de desempeño de PRODUCCIONUVA1 al módulo [NOMBRE_MODULO].

Pasos:
1. Identificar el ID_AREA del módulo [NOMBRE_MODULO]
2. Copiar las 6 clases de evaluación desde apps/PRODUCCIONUVA1/views.py a apps/[NOMBRE_MODULO]/views.py
3. Reemplazar el "13" por [TU_ID_AREA] en las 3 llamadas a procedimientos almacenados
4. Actualizar el nombre de la clase principal y el template path
5. Agregar las 7 rutas en apps/[NOMBRE_MODULO]/urls.py
6. Copiar el template HTML y actualizar las URLs
7. Agregar entrada en el menú
8. Probar todas las funcionalidades

Los procedimientos almacenados YA FUNCIONAN para todos los módulos, solo se diferencian por id_area.
```

---

**¡Listo para usar!** 🚀
