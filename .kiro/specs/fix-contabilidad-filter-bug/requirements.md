# Fix: Filtro de Campaña en Contabilidad muestra todos los registros cuando no hay datos

## Descripción del Problema

En el módulo de **Contabilidad**, cuando se selecciona una campaña (año) que no tiene datos registrados, el sistema muestra **TODOS los registros** ignorando el filtro. En cambio, en **RRHH** (que tiene el mismo código adaptado), cuando no hay datos para la campaña seleccionada, la tabla se queda vacía correctamente.

## Análisis Realizado

### Archivos Comparados:
- `static/core/js/RRHH/remuneracion_dl.js` vs `static/core/js/CONTABILIDAD/remuneracion_dl.js`
- `templates/rrhh/pages/rrhh_presupuesto_dl.html` vs `templates/contabilidad/pages/contabilidad_presupuesto_dl.html`
- `apps/rrhh/views.py` (CostoSueldosView) vs `apps/contabilidad/views.py` (CostoSueldosView)

### Diferencia Clave Encontrada:

El template de **Contabilidad** tiene un script adicional al final que NO existe en RRHH:

```html
<script>
    $(document).ready(function() {
        setTimeout(function() {
            var campaniaInicial = $('#filtroAnioPresupuesto').val();
            console.log("[INIT] Aplicando filtro inicial de campaña:", campaniaInicial);
            if (typeof filtrarPorAnio === 'function') {
                filtrarPorAnio();
            }
        }, 500);
    });
</script>
```

### Lógica del Backend (Idéntica en ambos):

```python
if campania:
    query = """SELECT ... WHERE id_area = X AND id_remuneracion = 1 AND ID_CAMPANIA = ?"""
    cursor.execute(query, [campania])
else:
    query = """SELECT ... WHERE id_area = X AND id_remuneracion = 1"""
    cursor.execute(query)
```

El backend retorna TODOS los registros cuando no se proporciona el parámetro `year`.

## Hipótesis del Bug

El problema podría estar en una de estas situaciones:

1. **Timing Issue**: El script adicional de inicialización en contabilidad podría estar ejecutándose antes de que el valor del filtro esté disponible, causando que se envíe una petición sin el parámetro `year`.

2. **Doble Inicialización**: Las tablas se inicializan en el `document.ready` del JS con el filtro, pero luego el script adicional del HTML vuelve a llamar a `filtrarPorAnio()` que podría estar causando conflictos.

3. **Diferencia en el manejo de respuestas vacías**: Podría haber código que detecta respuestas vacías y recarga sin filtro.

## User Stories

### US-001: Mantener filtro cuando no hay datos
**Como** usuario de Contabilidad  
**Quiero** que cuando seleccione una campaña sin datos, la tabla se muestre vacía  
**Para** saber que no hay registros para esa campaña específica

### Criterios de Aceptación:
- [ ] Cuando se selecciona una campaña sin datos, la tabla debe mostrar "No hay datos disponibles"
- [ ] El filtro de campaña debe mantenerse activo
- [ ] No debe cargar todos los registros automáticamente
- [ ] El comportamiento debe ser idéntico al de RRHH

## Solución Aplicada

Se eliminó el script de inicialización adicional en `templates/contabilidad/pages/contabilidad_presupuesto_dl.html` que llamaba a `filtrarPorAnio()` después de 500ms.

### Razón:
Las tablas ya se inicializan correctamente con el filtro de campaña en los archivos JS (`remuneracion_dl.js`, etc.) dentro del `document.ready`. El script adicional causaba una doble carga de datos que podría estar generando condiciones de carrera o conflictos.

### Cambio Realizado:
```html
<!-- ANTES -->
<script>
    $(document).ready(function() {
        setTimeout(function() {
            var campaniaInicial = $('#filtroAnioPresupuesto').val();
            if (typeof filtrarPorAnio === 'function') {
                filtrarPorAnio();
            }
        }, 500);
    });
</script>

<!-- DESPUÉS -->
<!-- Comentario explicando que el script fue removido -->
```

## Archivos Modificados

1. `templates/contabilidad/pages/contabilidad_presupuesto_dl.html` - Removido script de inicialización adicional

## Notas Adicionales

- RRHH referencia un archivo `campania_global_dl.js` que no existe, pero esto no afecta el funcionamiento
- Ambos módulos usan la misma lógica de backend para filtrar por campaña
- La diferencia de `id_area` (1 para Contabilidad, 12 para RRHH) es correcta
