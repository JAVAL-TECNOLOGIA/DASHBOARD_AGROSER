# 📋 **FLUJO COMPLETO DE REVISIÓN INTERMEDIA - SISTEMA RRHH**

## 🎯 **RESUMEN EJECUTIVO**

El sistema de **Revisión Intermedia** permite hacer seguimiento del avance de evaluaciones de desempeño durante el período intermedio del año. Facilita la actualización de objetivos y competencias, incluyendo porcentajes de cumplimiento y comentarios.

---

## 🏗️ **ARQUITECTURA DEL SISTEMA**

### **1. FRONTEND (Interfaz de Usuario)**
- **Template HTML:** `rrhh_fase_intermedio.html`  
- **JavaScript:** `rrhh_fase_intermedio.js`
- **Framework:** jQuery + DataTables + Bootstrap
- **Componentes UI:** Tablas dinámicas, modales, formularios

### **2. BACKEND (Servidor Django)**
- **Vista API Principal:** `FaseIntermediaEvaluacionesView` 
- **Vista Detalles:** `DetallesEvaluacionModalView`
- **Endpoints:** `/api/fase-intermedia/` y `/api/detalles-evaluacion/`

### **3. BASE DE DATOS**
- **Tablas principales:**
  - `RRHH_EVALUACIONES` - Evaluaciones principales
  - `RRHH_OBJETIVOS` - Objetivos específicos
  - `RRHH_COMPETENCIAS` - Competencias a evaluar
- **Procedimientos almacenados:**
  - `SP_OBTENER_FASE_INTERMEDIA`
  - `SP_OBTENER_DETALLES_EVALUACION_MODAL`

---

## 🔄 **FLUJO FUNCIONAL DETALLADO**

### **FASE 1: CARGA INICIAL**

#### **1.1 Inicialización del Sistema**
```javascript
// Al cargar la página
$(document).ready(function() {
    console.log("Inicializando Fase Intermedia...");
    inicializarTablaEvaluacionesIntermedio();
    initializarEventosAvance();
    initializarEventosAvanceRapido();
});
```

#### **1.2 Configuración de DataTable**
```javascript
function inicializarTablaEvaluacionesIntermedio() {
    tablaEvaluacionesIntermedio = $("#tablaEvaluaciones_intermedio").DataTable({
        dom: "Bfrtip",
        ajax: {
            url: '/rrhh/api/fase-intermedia/?id_area=12',
            type: 'GET',
            dataSrc: function(json) {
                if (json.status === 'success') {
                    return json.data;
                } else {
                    console.error("Error en la respuesta de la API:", json.message);
                    return [];
                }
            }
        },
        columns: [
            { data: 'id_evaluacion', title: 'ID', visible: false },
            { data: null, title: 'Evaluado', render: renderEvaluado },
            { data: null, title: 'Evaluador', render: renderEvaluador },
            { data: 'periodo', title: 'Período' },
            { data: 'nombre_area', title: 'Área' },
            { data: null, title: 'Objetivos', render: renderObjetivos },
            { data: null, title: 'Competencias', render: renderCompetencias },
            { data: 'porcentaje_general', title: 'Avance General', render: renderAvanceGeneral },
            { data: 'estado_avance', title: 'Estado', render: renderEstado },
            { data: null, title: 'Acciones', render: renderAcciones }
        ]
    });
}
```

### **FASE 2: INTERACCIÓN DEL USUARIO**

#### **2.1 Eventos de Tabla**
- **Doble clic en fila:** Abre modal de seguimiento rápido
- **Botón "Registrar Avance":** Abre modal detallado
- **Botón "Generar PDF":** Genera reporte en PDF

#### **2.2 Modal de Seguimiento de Avance**
```javascript
function abrirModalSeguimientoAvance(id_evaluacion) {
    // 1. Asignar ID de evaluación
    evaluacionActualRapido = id_evaluacion;
    
    // 2. Resetear el modal
    resetModalseguimiento_avance();
    
    // 3. Cargar datos del evaluado
    cargarDatosSeguimientoAvance(id_evaluacion);
    
    // 4. Mostrar el modal
    $("#Modal_Seguimiento_Avance").modal("show");
}
```

### **FASE 3: CARGA DE DATOS DINÁMICOS**

#### **3.1 Información del Evaluado**
```javascript
function cargarDatosSeguimientoAvance(id_evaluacion) {
    $.ajax({
        url: `/rrhh/api/fase-intermedia/`,
        type: 'GET',
        success: function(response) {
            const datosFiltrados = response.data.filter(
                item => item.id_evaluacion === id_evaluacion
            );
            mostrarInformacionEvaluado(datosFiltrados);
        }
    });
}
```

#### **3.2 Carga de Objetivos**
```javascript
function cargarTablaObjetivosAvance(id_evaluacion) {
    $.ajax({
        url: `/rrhh/api/detalles-evaluacion/?id_evaluacion=${id_evaluacion}&tipo=1`,
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                // Generar filas dinámicas con inputs editables
                let filas = '';
                response.data.forEach(function(objetivo, index) {
                    filas += generarFilaObjetivo(objetivo, index);
                });
                $("#tabla_objetivos_avance").html(filas);
            }
        }
    });
}
```

#### **3.3 Carga de Competencias**
```javascript
function cargarTablaCompetenciasAvance(id_evaluacion) {
    $.ajax({
        url: `/rrhh/api/detalles-evaluacion/?id_evaluacion=${id_evaluacion}&tipo=2`,
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                // Generar filas dinámicas con inputs editables
                let filas = '';
                response.data.forEach(function(competencia, index) {
                    filas += generarFilaCompetencia(competencia, index);
                });
                $("#tabla_competencias_avance").html(filas);
            }
        }
    });
}
```

### **FASE 4: ACTUALIZACIÓN DE DATOS**

#### **4.1 Guardado de Objetivos**
```javascript
function guardarAvanceObjetivos() {
    // 1. Recopilar datos de inputs
    const actualizaciones = [];
    $("#tabla_objetivos_avance input.avance-input").each(function() {
        const input = $(this);
        const objetivoId = input.data('objetivo-id');
        const porcentajeActual = parseFloat(input.val()) || 0;
        const comentarios = $(`#comentarios_objetivos_${objetivoId}`).val() || '';
        
        actualizaciones.push({
            id: objetivoId,
            porcentaje_avance: porcentajeActual,
            comentarios_objetivos: comentarios
        });
    });
    
    // 2. Enviar al servidor
    actualizarAvancesEnServidor(1, actualizaciones, 'objetivos', null, {
        comentarios_objetivos_general: $("#comentarios_objetivos_general").val(),
        id_evaluacion: evaluacionActualRapido
    });
}
```

#### **4.2 Guardado de Competencias**
```javascript
function guardarAvanceCompetencias() {
    // Similar a objetivos pero con tipo = 2
    const actualizaciones = [];
    $("#tabla_competencias_avance input.avance-input").each(function() {
        // Recopilar datos...
        actualizaciones.push({
            id: competenciaId,
            porcentaje_avance: porcentajeActual,
            comentarios_competencias: comentarios
        });
    });
    
    actualizarAvancesEnServidor(2, actualizaciones, 'competencias', null, {
        comentarios_competencias_general: $("#comentarios_competencias_general").val(),
        id_evaluacion: evaluacionActualRapido
    });
}
```

#### **4.3 Envío al Servidor**
```javascript
function actualizarAvancesEnServidor(tipo, actualizaciones, tipoNombre, callback, comentarios = {}) {
    $.ajax({
        url: '/rrhh/api/detalles-evaluacion/',
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({
            tipo: tipo,
            actualizaciones: actualizaciones,
            ...comentarios
        }),
        success: function(response) {
            if (response.status === 'success') {
                mostrarMensaje(`${tipoNombre} actualizados exitosamente`, 'success');
                actualizarBarrasProgreso(tipo, actualizaciones);
            }
        }
    });
}
```

---

## 🌐 **ENDPOINTS DE LA API**

### **1. Lista de Evaluaciones - GET**
```
GET /rrhh/api/fase-intermedia/?id_area=12
```
**Respuesta:**
```json
{
    "status": "success",
    "message": "Datos obtenidos correctamente",
    "data": [
        {
            "id_evaluacion": 189,
            "nombre_evaluado": "Juan",
            "apellido_evaluado": "García", 
            "nombre_evaluador": "María Pérez",
            "periodo": "2025",
            "nombre_area": "Recursos Humanos",
            "total_objetivos": 5,
            "total_competencias": 8,
            "porcentaje_objetivos": 60,
            "porcentaje_competencias": 70,
            "porcentaje_general": 65,
            "estado_avance": "En Progreso"
        }
    ],
    "total_registros": 1
}
```

### **2. Detalles de Objetivos/Competencias - GET**
```
GET /rrhh/api/detalles-evaluacion/?id_evaluacion=189&tipo=1
```
**Respuesta (Objetivos):**
```json
{
    "status": "success",
    "message": "Objetivos obtenidos correctamente",
    "data": [
        {
            "id": 123,
            "nombre_objetivo": "Mejorar eficiencia en procesos",
            "descripcion": "Optimizar procesos de selección",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31",
            "indicador": "Porcentaje de reducción de tiempo",
            "meta": "Reducir 30% tiempo selección",
            "porcentaje_actual": 60,
            "comentarios_objetivos": ""
        }
    ]
}
```

### **3. Actualización de Datos - PUT**
```
PUT /rrhh/api/detalles-evaluacion/
Content-Type: application/json
```
**Request Body:**
```json
{
    "tipo": 1,
    "id_evaluacion": 189,
    "actualizaciones": [
        {
            "id": 123,
            "porcentaje_avance": 75,
            "comentarios_objetivos": "Avance significativo"
        }
    ],
    "comentarios_objetivos_general": "Progreso general satisfactorio"
}
```

**Respuesta:**
```json
{
    "status": "success",
    "message": "Todas las actualizaciones fueron exitosas (1/1) y comentarios generales actualizados",
    "data": {
        "tipo": "objetivos",
        "total_procesadas": 1,
        "exitosas": 1,
        "fallidas": 0,
        "comentarios_actualizados": true,
        "id_evaluacion": 189
    }
}
```

---

## 🎨 **COMPONENTES DE LA INTERFAZ**

### **1. Tabla Principal**
- **DataTable responsiva** con paginación
- **Botones de acción:** Refrescar, Exportar Excel
- **Columnas dinámicas** con indicadores visuales
- **Eventos de doble clic** para acceso rápido

### **2. Modal de Seguimiento de Avance**
- **Header:** Información del evaluado con avatar
- **Pestañas:** Objetivos y Competencias 
- **Tablas editables** con inputs numéricos
- **Barras de progreso** actualizables
- **Comentarios generales** por categoría

### **3. Elementos Visuales**
- **Progress bars** con códigos de colores:
  - 🔴 0-24%: Peligro (bg-danger)
  - 🟡 25-49%: Advertencia (bg-warning) 
  - 🔵 50-74%: Información (bg-info)
  - 🟢 75-100%: Éxito (bg-success)
- **Badges** para tipos de competencias
- **Avatars** con iniciales del evaluado

---

## 🔒 **VALIDACIONES Y CONTROLES**

### **1. Validaciones Frontend**
```javascript
// Validación de rango de porcentajes
if (porcentajeActual < 0 || porcentajeActual > 100) {
    mostrarMensaje(`El porcentaje debe estar entre 0 y 100`, 'warning');
    return;
}

// Validación de ID de evaluación
if (!evaluacionActualRapido) {
    console.error("ERROR: evaluacionActualRapido es null");
    mostrarMensaje('Error: No se pudo identificar la evaluación', 'error');
    return;
}
```

### **2. Validaciones Backend**
```python
# Validación de estructura de datos
if 'tipo' not in data or 'actualizaciones' not in data:
    return JsonResponse({
        'status': 'error',
        'message': 'Se requieren los campos "tipo" y "actualizaciones"'
    }, status=400)

# Validación de tipo de tabla
if tipo_tabla not in [1, 2]:
    return JsonResponse({
        'status': 'error',
        'message': 'El campo "tipo" debe ser 1 (Objetivos) o 2 (Competencias)'
    }, status=400)

# Validación de existencia de registros
cursor.execute(f"SELECT {id_campo} FROM {tabla} WHERE {id_campo} = ? AND estado = 1", [registro_id])
if not cursor.fetchone():
    actualizaciones_fallidas.append({
        'id': registro_id,
        'error': f'{"Objetivo" if tipo_tabla == 1 else "Competencia"} no encontrado'
    })
```

---

## 🗄️ **ESTRUCTURA DE BASE DE DATOS**

### **1. Tabla RRHH_EVALUACIONES**
```sql
-- Campos principales
id                               INT PRIMARY KEY
id_empleado                     INT
id_evaluador                    INT  
periodo                         VARCHAR(4)
estado                         INT
comentarios_objetivos_general   TEXT
comentarios_competencias_general TEXT
fecha_creacion                 DATETIME
```

### **2. Tabla RRHH_OBJETIVOS**
```sql  
-- Campos principales
id                    INT PRIMARY KEY
id_evaluacion        INT FOREIGN KEY
nombre_objetivo      VARCHAR(255)
descripcion          TEXT
fecha_inicio         DATE
fecha_fin           DATE
indicador           VARCHAR(255)
meta                TEXT
porc_cumplimiento   DECIMAL(5,2)
comentarios_objetivos TEXT
estado              INT
```

### **3. Tabla RRHH_COMPETENCIAS**
```sql
-- Campos principales  
id                      INT PRIMARY KEY
id_evaluacion          INT FOREIGN KEY
nombre_competencia     VARCHAR(255)
descripcion_competencia TEXT
tipo_competencia       VARCHAR(50)
meta                   TEXT
porc_cumplimiento      DECIMAL(5,2)
comentarios_competencias TEXT
estado                 INT
```

---

## 🚀 **PROCESO DE ACTUALIZACIÓN COMPLETO**

### **Flujo de Guardado:**

1. **Usuario modifica porcentajes** en los inputs
2. **Clic en "Guardar Avance"** (Objetivos/Competencias)
3. **JavaScript recopila datos** de todos los inputs modificados
4. **Validación frontend** de rangos y formatos
5. **AJAX PUT request** al endpoint `/api/detalles-evaluacion/`
6. **Backend valida datos** y estructura JSON
7. **Actualización transaccional** en base de datos:
   - Actualiza `porc_cumplimiento` en tabla específica
   - Actualiza comentarios individuales 
   - Actualiza comentarios generales en `RRHH_EVALUACIONES`
8. **Commit de transacción** si todo es exitoso
9. **Respuesta JSON** con resultado detallado
10. **Frontend actualiza UI** con nuevos valores
11. **Mensaje de confirmación** al usuario

### **Manejo de Errores:**
- **Rollback automático** en caso de error
- **Respuestas parciales** (207 Multi-Status) para éxitos parciales
- **Logs detallados** en consola y servidor
- **Mensajes informativos** para el usuario

---

## 📱 **CARACTERÍSTICAS RESPONSIVE**

- **Tablas adaptativas** con scroll horizontal
- **Modales full-width** en móviles (90% ancho)
- **Inputs táctiles** optimizados para dispositivos móviles
- **Botones de tamaño apropiado** para touch

---

## 🔄 **ACTUALIZACIÓN DE LA TABLA PRINCIPAL**

```javascript
// Después de guardar exitosamente
if (tablaEvaluacionesIntermedio) {
    tablaEvaluacionesIntermedio.destroy();
}
inicializarTablaEvaluacionesIntermedio();
```

---

## 📊 **INDICADORES VISUALES**

### **Estados de Avance:**
- 🔴 **Sin Datos** - badge-secondary
- 🔵 **Pendiente** - badge-info  
- 🟡 **En Progreso** - badge-warning
- 🟢 **Completado** - badge-success

### **Tipos de Competencias:**
- 🔵 **ESENCIAL** - badge-primary
- 🟦 **TECNICA** - badge-info
- 🟢 **INTERPERSONAL** - badge-success
- 🟡 **GERENCIAL** - badge-warning

---

## ✅ **CASOS DE USO PRINCIPALES**

1. **Supervisor revisa avances** de su equipo
2. **Actualiza porcentajes** de objetivos cumplidos
3. **Agrega comentarios específicos** por objetivo/competencia  
4. **Registra observaciones generales** por categoría
5. **Exporta reportes** para presentaciones
6. **Genera PDFs** para documentación formal

---

Este flujo está completamente funcional y preparado para ser extendido a **Revisión Final**. Los componentes son reutilizables y la arquitectura permite escalar fácilmente a nuevas funcionalidades.