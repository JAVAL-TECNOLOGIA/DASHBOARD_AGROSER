# EmailManager - Módulo de Gestión de Correos Electrónicos

## Descripción

El `EmailManager` es un módulo modular y escalable diseñado para manejar la funcionalidad de envío de correos electrónicos y generación de PDFs en el sistema de evaluaciones de objetivos de RRHH.

## Características Principales

### ✅ Estructura Modular

- Configuración centralizada
- Separación clara de responsabilidades
- Fácil mantenimiento y extensión

### ✅ Manejo Robusto de Errores

- Validación de entradas
- Mensajes de error consistentes
- Fallbacks para diferentes escenarios

### ✅ Escalabilidad

- Configuración extensible
- Múltiples rutas de scripts de respaldo
- Sistema de logging integrado

## Uso Básico

### Inicialización

```javascript
// El módulo se inicializa automáticamente al cargar la página
EmailManager.inicializar();
```

### Envío de PDF por Correo

```javascript
// Desde un botón en la tabla
EmailManager.generarEnviarPDFEvaluacion(idEvaluacion);
```

## Configuración

### Endpoints

```javascript
config: {
  endpoints: {
    evaluaciones: "/evaluaciones/objetivos_evaluacion/",
    detallesObjetivos: "/evaluaciones/detalles_objetivos/"
  }
}
```

### Scripts de Competencias

```javascript
scripts: {
  competenciasPaths: [
    "/static/core/js/EVALUACIONES/DonLuis/rrhh_ev_competencias.js",
    "/static/core/js/COSTOS/DonLuis/rrhh_ev_competencias.js",
    "/static/core/js/RIEGO/DonLuis/rrhh_ev_competencias.js",
  ];
}
```

### Mensajes Personalizables

```javascript
messages: {
  confirmation: {
    title: "Confirmación",
    text: "¿Desea generar el PDF de esta evaluación y enviarlo por correo?"
  },
  loading: {
    title: "Procesando",
    text: "Generando PDF y preparando envío..."
  },
  errors: {
    invalidId: "No se pudo identificar la evaluación",
    scriptLoad: "No se pudo cargar el script necesario",
    functionNotFound: "No se pudo cargar la funcionalidad"
  }
}
```

## Métodos Principales

### `generarEnviarPDFEvaluacion(idEvaluacion)`

Función principal que maneja todo el flujo de generación y envío de PDF.

**Parámetros:**

- `idEvaluacion` (number): ID de la evaluación a procesar

**Flujo:**

1. Valida el ID de evaluación
2. Muestra confirmación al usuario
3. Intenta cargar la función de generación de PDF
4. Ejecuta la generación y envío

### `validarIdEvaluacion(idEvaluacion)`

Valida que el ID proporcionado sea válido.

**Retorna:** `boolean`

### `mostrarError(mensaje)`

Muestra errores de forma consistente usando SweetAlert2.

### `esFuncionPDFDisponible()`

Verifica si la función `generarPDFEvaluacion` está disponible.

**Retorna:** `boolean`

## Métodos de Utilidad

### `extenderConfiguracion(nuevaConfig)`

Permite extender la configuración del módulo dinámicamente.

```javascript
EmailManager.extenderConfiguracion({
  nuevoEndpoint: "/api/nuevo-endpoint/",
  customMessages: {
    success: "¡Operación exitosa!",
  },
});
```

### `obtenerEstadisticas()`

Obtiene estadísticas del estado actual del módulo.

```javascript
const stats = EmailManager.obtenerEstadisticas();
console.log(stats);
// Output: {
//   moduloActivo: true,
//   funcionPDFDisponible: false,
//   ultimaInicializacion: "2024-01-15T10:30:00.000Z"
// }
```

## Integración en HTML

### Botón de Envío en DataTable

```javascript
{
  title: "Enviar",
  data: null,
  orderable: false,
  render: function (data, type, row) {
    return `
      <div class="btn-group btn-group-sm" role="group">
        <button type="button"
                class="btn btn-info btn-ls"
                onclick="EmailManager.generarEnviarPDFEvaluacion(${row.id})"
                title="Generar PDF y enviar por correo"
                data-id-evaluacion="${row.id}">
          <i class='bx bx-envelope-open'></i>
        </button>
      </div>`;
  }
}
```

## Extensibilidad

### Añadir Nuevos Scripts

```javascript
EmailManager.extenderConfiguracion({
  scripts: {
    competenciasPaths: [
      ...EmailManager.config.scripts.competenciasPaths,
      "/ruta/nuevo/script.js",
    ],
  },
});
```

### Personalizar Mensajes

```javascript
EmailManager.extenderConfiguracion({
  messages: {
    confirmation: {
      title: "Nuevo Título",
      text: "Nuevo mensaje de confirmación",
    },
  },
});
```

## Ventajas de esta Implementación

1. **Modularidad**: Código organizado en módulos independientes
2. **Reutilización**: Fácil de implementar en otros archivos
3. **Mantenibilidad**: Cambios centralizados en configuración
4. **Escalabilidad**: Fácil añadir nuevas funcionalidades
5. **Robustez**: Manejo completo de errores y casos edge
6. **Logging**: Sistema de seguimiento integrado

## Ejemplo de Implementación Completa

```javascript
// 1. Inicialización automática
document.addEventListener("DOMContentLoaded", function () {
  EmailManager.inicializar();
  // ... resto de inicializaciones
});

// 2. Uso en tabla DataTable
columns: [
  // ... otras columnas
  {
    title: "Enviar",
    data: null,
    orderable: false,
    render: function (data, type, row) {
      return `<button onclick="EmailManager.generarEnviarPDFEvaluacion(${row.id})">
                <i class='bx bx-envelope-open'></i>
              </button>`;
    },
  },
];

// 3. Extensión de funcionalidad (opcional)
EmailManager.extenderConfiguracion({
  analytics: {
    trackClicks: true,
    sendMetrics: true,
  },
});
```

## Dependencias

- jQuery
- SweetAlert2
- DataTables (para integración en tablas)
- Script de competencias (se carga dinámicamente)

---

_Esta documentación corresponde a la implementación modular y escalable del sistema de envío de correos electrónicos en el módulo de evaluaciones de objetivos._
