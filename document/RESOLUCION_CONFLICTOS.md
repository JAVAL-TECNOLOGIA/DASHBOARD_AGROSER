# 🚨 Guía de Resolución de Conflictos - PORTAL AEI

## 🎯 Escenarios Comunes de Conflictos

### 📄 **Conflicto en JavaScript (script_req_interno.js)**

#### **Situación**: JHON y YERSON modifican la misma función

**Archivo**: `static/core/js/script/script_req_interno.js`

```javascript
// ========== CONFLICTO DETECTADO ==========
function ejecutarAprobacionMasiva() {
<<<<<<< HEAD
    // Código de JHON
    if (registrosSeleccionados.length === 0) {
        Swal.fire({
            title: "Sin Selección",
            text: "Debes seleccionar al menos un registro.",
            icon: "warning"
        });
        return;
    }
=======
    // Código de YERSON  
    if (registrosSeleccionados.length === 0) {
        alert("No hay registros seleccionados");
        return;
    }
>>>>>>> feature/yerson-garcia
    
    // Resto del código...
}
```

#### **✅ Solución Recomendada**:
```javascript
// Mantener la versión más moderna (SweetAlert2)
function ejecutarAprobacionMasiva() {
    if (registrosSeleccionados.length === 0) {
        Swal.fire({
            title: "⚠️ Sin Selección",
            text: "Debes seleccionar al menos un registro para continuar.",
            icon: "warning",
            confirmButtonText: "Entendido"
        });
        return;
    }
    
    // Resto del código...
}
```

---

### 🎨 **Conflicto en Template HTML**

#### **Situación**: Ambos agregan botones en la misma sección

**Archivo**: `templates/script/req_interno.html`

```html
<!-- ========== CONFLICTO DETECTADO ========== -->
<div class="col-md-2">
<<<<<<< HEAD
    <!-- Código de JHON -->
    <button type="button" id="btnExportar" class="btn btn-info form-control">
        <i class="fa fa-download mr-1"></i>
        Exportar Excel
    </button>
=======
    <!-- Código de YERSON -->
    <button type="button" id="btnImprimir" class="btn btn-secondary form-control">
        <i class="fa fa-print mr-1"></i>
        Imprimir Reporte
    </button>
>>>>>>> feature/yerson-garcia
</div>
```

#### **✅ Solución Recomendada**:
```html
<!-- Mantener ambos botones, ajustar layout -->
<div class="col-md-1">
    <button type="button" id="btnExportar" class="btn btn-info form-control">
        <i class="fa fa-download mr-1"></i>
        Excel
    </button>
</div>
<div class="col-md-1">
    <button type="button" id="btnImprimir" class="btn btn-secondary form-control">
        <i class="fa fa-print mr-1"></i>
        PDF
    </button>
</div>
```

---

### 🐍 **Conflicto en Views.py**

#### **Situación**: Modificaciones en la misma vista

**Archivo**: `apps/script/views.py`

```python
# ========== CONFLICTO DETECTADO ==========
def UpdateReqInternos(request, idorden):
<<<<<<< HEAD
    # Código de JHON
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE tabla SET estado='AP' WHERE idorden=%s", [idorden])
        cursor.close()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
=======
    # Código de YERSON
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE tabla SET estado='AP', fecha_aprobacion=GETDATE() WHERE idorden=%s", [idorden])
        connection.commit()
        cursor.close()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
>>>>>>> feature/yerson-garcia
```

#### **✅ Solución Recomendada**:
```python
def UpdateReqInternos(request, idorden):
    # Combinar mejores prácticas de ambos
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE tabla SET estado='AP', fecha_aprobacion=GETDATE() WHERE idorden=%s", 
            [idorden]
        )
        connection.commit()
        cursor.close()
        
        return JsonResponse({
            'status': 'success',
            'success': True,
            'message': 'Requerimiento aprobado correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'success': False,
            'message': f'Error al aprobar: {str(e)}'
        })
```

---

## 🛠️ Paso a Paso: Resolución Práctica

### **Paso 1: Detectar el Conflicto**
```bash
# Al hacer merge verás:
git merge feature/jhon-gutierrez
Auto-merging static/core/js/script/script_req_interno.js
CONFLICT (content): Merge conflict in static/core/js/script/script_req_interno.js
Automatic merge failed; fix conflicts and then commit the result.
```

### **Paso 2: Identificar Archivos Afectados**
```bash
git status
# Output:
# On branch DESARROLLO
# You have unmerged paths.
#   (fix conflicts and run "git commit")
#   (use "git merge --abort" to abort the merge)
#
# Unmerged paths:
#   (use "git add <file>..." to mark resolution)
#         both modified:   static/core/js/script/script_req_interno.js
#         both modified:   templates/script/req_interno.html
```

### **Paso 3: Abrir Archivo en Editor**
```bash
# Usar VS Code para mejor visualización
code static/core/js/script/script_req_interno.js
```

### **Paso 4: Entender los Marcadores**
```javascript
<<<<<<< HEAD
// Código actual en DESARROLLO
=======
// Código de la rama que se está integrando
>>>>>>> feature/jhon-gutierrez
```

### **Paso 5: Decidir Estrategia**

#### **Opción A: Mantener Código Actual**
```javascript
// Eliminar marcadores y mantener solo código de HEAD
function miFuncion() {
    // código actual
}
```

#### **Opción B: Usar Código Nuevo**
```javascript
// Eliminar marcadores y mantener solo código de la rama
function miFuncion() {
    // código nuevo
}
```

#### **Opción C: Combinar Ambos (Recomendado)**
```javascript
// Combinar lo mejor de ambos códigos
function miFuncion() {
    // lógica combinada
}
```

### **Paso 6: Marcar como Resuelto**
```bash
# Guardar archivo sin marcadores de conflicto
git add static/core/js/script/script_req_interno.js
```

### **Paso 7: Verificar Resolución**
```bash
git status
# Debería mostrar:
# All conflicts fixed but you are still merging.
#   (use "git commit" to conclude merge)
```

### **Paso 8: Completar Merge**
```bash
git commit -m "MERGE: Resolver conflictos entre JHON y YERSON

- Combinado funcionalidad de aprobación masiva
- Mantenido SweetAlert2 como estándar
- Agregado logging mejorado en views
- Unificado formato de respuesta JSON"
```

---

## 🧪 Testing Después de Resolver Conflictos

### **Checklist de Verificación**

#### ✅ **Funcionalidad Básica**
```bash
# 1. Verificar que el servidor inicia
python manage.py runserver

# 2. Verificar que no hay errores de sintaxis
python manage.py check

# 3. Probar funcionalidades principales
# - Cargar página de requerimientos
# - Ejecutar aprobación individual
# - Ejecutar aprobación masiva
```

#### ✅ **Testing JavaScript**
```javascript
// Abrir consola del navegador (F12) y probar:

// 1. Verificar que las funciones existen
typeof ejecutarAprobacionMasiva === 'function'

// 2. Probar función manualmente
ejecutarAprobacionMasiva()

// 3. Verificar que no hay errores en consola
```

#### ✅ **Testing Backend**
```bash
# Probar endpoints directamente
curl -X GET "http://127.0.0.1:8000/req_interno_log_filter/0/"
curl -X GET "http://127.0.0.1:8000/actualizar-req-interno/76F0I612E58108/"
```

---

## 🚨 Errores Comunes y Soluciones

### **Error 1: Marcadores de Conflicto No Resueltos**
```
error: Merge conflict in static/core/js/script/script_req_interno.js
```

**Solución**:
```bash
# Buscar marcadores restantes
grep -n "<<<<<<\|======\|>>>>>>" static/core/js/script/script_req_interno.js

# Eliminar todos los marcadores manualmente
```

### **Error 2: Archivo No Agregado**
```
error: Committing is not possible because you have unmerged files.
```

**Solución**:
```bash
# Verificar estado
git status

# Agregar archivos resueltos
git add .

# Intentar commit nuevamente
git commit
```

### **Error 3: Funcionalidad Rota Después del Merge**
```
TypeError: Cannot read property 'length' of undefined
```

**Solución**:
```bash
# Abortar merge y empezar de nuevo
git merge --abort

# Revisar cada archivo cuidadosamente
git merge feature/jhon-gutierrez
```

---

## 🎯 Estrategias de Prevención

### **1. Comunicación Entre Desarrolladores**
```markdown
# Antes de empezar a trabajar, coordinar:
- ¿En qué archivo vas a trabajar?
- ¿Qué función vas a modificar?
- ¿Cuándo planeas hacer push?
```

### **2. Merges Frecuentes**
```bash
# Hacer merge de DESARROLLO a tu rama frecuentemente
git checkout feature/tu-rama
git merge DESARROLLO
```

### **3. Commits Específicos**
```bash
# En lugar de:
git commit -m "Varios cambios"

# Hacer:
git commit -m "JHON: FEAT - Agregar validación en modal"
git commit -m "JHON: STYLE - Mejorar botones de aprobación"
```

### **4. Testing Antes de Push**
```bash
# Siempre probar antes de push
python manage.py runserver
# Verificar funcionalidad en navegador
git push origin feature/tu-rama
```

---

## 📋 Plantilla de Reporte de Conflictos

```markdown
### 🚨 REPORTE DE CONFLICTO

**Fecha**: [fecha]
**Desarrolladores Involucrados**: JHON y YERSON
**Archivos Afectados**: 
- static/core/js/script/script_req_interno.js (líneas 45-67)
- templates/script/req_interno.html (líneas 120-135)

**Descripción del Conflicto**:
Ambos desarrolladores modificaron la función ejecutarAprobacionMasiva()

**Solución Aplicada**:
- Mantenido SweetAlert2 de JHON
- Agregado logging de YERSON
- Combinado validaciones

**Testing Realizado**:
✅ Servidor inicia correctamente
✅ Funcionalidad de aprobación funciona
✅ No hay errores en consola

**Tiempo de Resolución**: 15 minutos
```

---

**🎯 Recuerda**: Los conflictos son normales en el desarrollo colaborativo. Lo importante es resolverlos de manera sistemática y comunicativa.

**📞 Contacto**: En caso de conflictos complejos, contactar inmediatamente a JOGUTIERREZ.
