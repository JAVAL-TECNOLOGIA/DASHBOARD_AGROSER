# 🌳 Manual de Git Workflow - PORTAL AEI

## 👥 Roles y Responsabilidades

### 🧑‍💻 **Desarrolladores Individuales**
- **JHON GUTIERREZ**: Rama `feature/jhon-gutierrez`
- **YERSON GARCIA**: Rama `feature/yerson-garcia`

### 👨‍💼 **Líder de Desarrollo**
- **JOGUTIERREZ**: Gestión de merges, resolución de conflictos, deploy

---

## 🔄 Workflow Completo del Proyecto

```
┌─────────────────┐    ┌─────────────────┐
│ feature/jhon    │    │ feature/yerson  │
│   (desarrollo)  │    │   (desarrollo)  │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          │    📥 SINCRONIZACIÓN │
          │  ← git pull origin   │
          │     master (cuando   │
          │     hay cambios en   │
          │     producción)      │
          │                      │
          └──────┬─────────┬─────┘
                 ▼         ▼
         ┌─────────────────────────┐
         │      DESARROLLO         │
         │   (testing/integración) │
         └─────────┬───────────────┘
                   │
                   ▼
         ┌─────────────────────────┐
         │        MASTER           │
         │     (producción)        │
         └─────────────────────────┘
```

### 🔄 **Flujo de Sincronización**
1. **Desarrollador A** sube cambios que llegan a producción (`master`)
2. **Desarrollador B** debe sincronizar su rama con `git pull origin master`
3. Resolver conflictos si los hay
4. Continuar desarrollo desde el punto actualizado

---

## 👨‍💻 PERFIL: DESARROLLADOR INDIVIDUAL

### 🚀 **Configuración Inicial (Solo una vez)**

```bash
# 1. Clonar el repositorio
git clone https://github.com/PORTALDONLUIS/DASHBOARD_DONLUIS.git
cd PORTAL-AEI_DESARROLLO

# 2. Configurar usuario Git (personalizar con tus datos)
git config user.name "JHON GUTIERREZ"  # o "YERSON GARCIA"
git config user.email "jhon@empresa.com"  # o email correspondiente

# 3. Cambiar a tu rama personal
git checkout feature/jhon-gutierrez  # o feature/yerson-garcia
```

### 📝 **Desarrollo Diario**

#### **Paso 1: Iniciar Trabajo**
```bash
# Cambiar a tu rama personal
git checkout feature/jhon-gutierrez  # o feature/yerson-garcia

# Actualizar tu rama con los últimos cambios
git pull origin feature/jhon-gutierrez  # o tu rama correspondiente

# Verificar que estás en la rama correcta
git branch
```

#### **Paso 2: Desarrollar y Guardar Cambios**
```bash
# Ver archivos modificados
git status

# Agregar archivos específicos
git add nombre_archivo.py
git add static/core/js/script/script_req_interno.js

# O agregar todos los archivos modificados
git add .

# Hacer commit con mensaje descriptivo
git commit -m "JHON: Implementar aprobación masiva en requerimientos"
# Formato: "NOMBRE: Descripción clara del cambio"
```

#### **Paso 3: Subir Cambios**
```bash
# Subir cambios a tu rama remota
git push origin feature/jhon-gutierrez  # o tu rama correspondiente
```

### � **Sincronizar con Cambios de Producción**

#### **¿Cuándo usar este proceso?**
- Cuando tu compañero haya subido cambios a producción (`master`)
- Al iniciar una nueva funcionalidad importante
- Después de un deploy para mantener tu rama actualizada
- Cuando notes que tu rama está desactualizada

#### **Paso 1: Verificar Estado Actual**
```bash
# Ver en qué rama estás
git branch

# Ver el estado de tu rama
git status

# Ver cuántos commits está por detrás tu rama
git fetch origin
git log --oneline master..HEAD  # Ver tus commits únicos
git log --oneline HEAD..master  # Ver commits de master que no tienes
```

#### **Paso 2: Traer Cambios de Master a Tu Rama**
```bash
# Asegurate de estar en tu rama personal
git checkout feature/jhon-gutierrez  # o feature/yerson-garcia

# Verifica que no tengas cambios sin guardar
git status

# Si tienes cambios sin guardar, haz commit primero
git add .
git commit -m "JHON: WIP - Guardando trabajo en progreso"

# Traer los cambios de master a tu rama
git pull origin master
```

#### **Paso 3: Resolver Conflictos (si los hay)**
```bash
# Si aparecen conflictos, Git te mostrará algo como:
# CONFLICT (content): Merge conflict in archivo.py

# Ver archivos con conflictos
git status

# Resolver manualmente cada archivo (ver sección "Resolución de Conflictos")
# Después de resolver:
git add archivo_resuelto.py
git commit -m "JHON: MERGE - Resolver conflictos con cambios de producción"
```

#### **Paso 4: Actualizar Rama Remota**
```bash
# Subir los cambios actualizados a tu rama remota
git push origin feature/jhon-gutierrez

# Verificar que todo esté sincronizado
git status
```

#### **Ejemplo Completo del Proceso**
```bash
# Situación: Yerson subió cambios a producción y quieres actualizar tu rama

# 1. Verificar estado
git checkout feature/jhon-gutierrez
git status
git fetch origin

# 2. Ver qué cambios nuevos hay en master
git log --oneline HEAD..origin/master

# 3. Traer los cambios
git pull origin master
# Output: Fast-forward o merge exitoso

# 4. Si hay conflictos, resolverlos y hacer commit

# 5. Subir cambios actualizados
git push origin feature/jhon-gutierrez

# 6. Verificar que todo esté bien
git log --oneline -5  # Ver últimos commits
```

#### **🚨 Casos Especiales**

**Si tu rama está muy desactualizada:**
```bash
# Opción 1: Rebase (recomendado para ramas personales)
git checkout feature/jhon-gutierrez
git rebase origin/master

# Si hay conflictos, resolverlos uno por uno:
# git add archivo_resuelto.py
# git rebase --continue

# Forzar push (solo en rama personal)
git push origin feature/jhon-gutierrez --force-with-lease
```

**Si quieres ver diferencias antes de traer cambios:**
```bash
# Ver qué archivos cambiaron en master
git diff HEAD..origin/master --name-only

# Ver cambios específicos en un archivo
git diff HEAD..origin/master -- archivo_especifico.py
```

### �📋 **Convenciones de Mensajes de Commit**

```bash
# Estructura: "NOMBRE: TIPO - Descripción"

# Ejemplos:
git commit -m "JHON: FEAT - Agregar modal de confirmación en aprobaciones"
git commit -m "YERSON: FIX - Corregir error en carga de datos del modal"
git commit -m "JHON: STYLE - Mejorar diseño responsive de la tabla"
git commit -m "YERSON: REFACTOR - Optimizar consultas SQL en views.py"
```

**Tipos de commit:**
- `FEAT`: Nueva funcionalidad
- `FIX`: Corrección de errores
- `STYLE`: Cambios de diseño/CSS
- `REFACTOR`: Mejoras de código sin cambiar funcionalidad
- `DOCS`: Documentación
- `TEST`: Pruebas

---

## 👨‍💼 PERFIL: LÍDER DE DESARROLLO

### 🔄 **Integración de Cambios a DESARROLLO**

#### **Paso 1: Revisar Cambios Pendientes**
```bash
# Ver estado de todas las ramas
git fetch --all
git branch -a

# Ver commits pendientes de cada desarrollador
git log --oneline origin/feature/jhon-gutierrez ^origin/DESARROLLO
git log --oneline origin/feature/yerson-garcia ^origin/DESARROLLO
```

#### **Paso 2: Integrar Cambios de JHON**
```bash
# Cambiar a DESARROLLO
git checkout DESARROLLO

# Actualizar DESARROLLO
git pull origin DESARROLLO

# Hacer merge de los cambios de JHON
git merge origin/feature/jhon-gutierrez

# Si hay conflictos, ir a "Resolución de Conflictos" más abajo
```

#### **Paso 3: Integrar Cambios de YERSON**
```bash
# Hacer merge de los cambios de YERSON
git merge origin/feature/yerson-garcia

# Si hay conflictos, ir a "Resolución de Conflictos"
```

#### **Paso 4: Testing y Subir a DESARROLLO**
```bash
# Probar la aplicación
python manage.py runserver

# Si todo funciona correctamente:
git push origin DESARROLLO
```

### 🚀 **Deploy a Producción (MASTER)**

```bash
# Cambiar a master
git checkout master

# Actualizar master
git pull origin master

# Merge desde DESARROLLO
git merge DESARROLLO

# Subir a producción
git push origin master

# Crear tag de versión (opcional)
git tag -a v1.0.1 -m "Release v1.0.1 - Mejoras en aprobaciones masivas"
git push origin v1.0.1
```

---

## ⚠️ RESOLUCIÓN DE CONFLICTOS

### 🔍 **Identificar Conflictos**

```bash
# Al hacer merge, si hay conflictos verás:
Auto-merging static/core/js/script/script_req_interno.js
CONFLICT (content): Merge conflict in static/core/js/script/script_req_interno.js
Automatic merge failed; fix conflicts and then commit the result.
```

### 🛠️ **Resolver Conflictos Paso a Paso**

#### **Paso 1: Ver Archivos con Conflictos**
```bash
git status
# Verás archivos marcados como "both modified"
```

#### **Paso 2: Abrir Archivo y Resolver**
El archivo tendrá marcadores como:
```javascript
function aprobarMasivo() {
<<<<<<< HEAD
    // Código de DESARROLLO actual
    console.log("Versión actual");
=======
    // Código del desarrollador
    console.log("Nueva versión de JHON/YERSON");
>>>>>>> feature/jhon-gutierrez
}
```

**Decidir qué código mantener:**
- Mantener solo el código de arriba (HEAD)
- Mantener solo el código de abajo (rama del desarrollador)
- Combinar ambos códigos
- Crear una nueva solución

#### **Paso 3: Marcar como Resuelto**
```bash
# Después de editar el archivo
git add archivo_resuelto.js

# Verificar que no quedan conflictos
git status
```

#### **Paso 4: Completar el Merge**
```bash
git commit -m "MERGE: Resolver conflictos entre JHON y YERSON en script_req_interno.js"
```

### 🚨 **Tipos Comunes de Conflictos**

#### **1. Conflictos en JavaScript**
- **Archivo**: `static/core/js/script/script_req_interno.js`
- **Causa**: Ambos modifican la misma función
- **Solución**: Combinar funcionalidades o usar la más reciente

#### **2. Conflictos en Templates**
- **Archivo**: `templates/script/req_interno.html`
- **Causa**: Cambios en la misma sección HTML
- **Solución**: Mantener ambos elementos si no se sobreponen

#### **3. Conflictos en Views**
- **Archivo**: `apps/script/views.py`
- **Causa**: Modificaciones en la misma vista
- **Solución**: Unificar lógica de negocio

#### **4. Conflictos en URLs**
- **Archivo**: `apps/script/urls.py`
- **Causa**: Agregado de URLs similares
- **Solución**: Mantener ambas URLs con nombres únicos

---

## 🔧 COMANDOS DE EMERGENCIA

### 🚨 **Deshacer Cambios Locales**
```bash
# Deshacer cambios no guardados
git checkout -- nombre_archivo.py

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Deshacer último commit (perder cambios)
git reset --hard HEAD~1
```

### 🔄 **Sincronizar con Cambios Remotos**
```bash
# Forzar actualización de tu rama
git fetch origin
git reset --hard origin/feature/tu-rama

# ⚠️ CUIDADO: Esto borrará cambios locales no guardados
```

### 🆘 **Recuperar de Errores Graves**
```bash
# Ver historial de comandos
git reflog

# Volver a un commit específico
git reset --hard HEAD@{2}

# Crear rama de backup antes de operaciones riesgosas
git checkout -b backup-$(date +%Y%m%d-%H%M%S)
```

---

## 📊 MONITOREO Y CONTROL

### 📈 **Ver Estado del Proyecto**
```bash
# Ver diferencias entre ramas
git diff DESARROLLO..feature/jhon-gutierrez

# Ver commits únicos por desarrollador
git log --oneline --author="JHON" --since="1 week ago"
git log --oneline --author="YERSON" --since="1 week ago"

# Ver archivos más modificados
git log --name-only --pretty=format: | sort | uniq -c | sort -rg
```

### 📋 **Reportes de Actividad**
```bash
# Resumen de commits por autor
git shortlog -sn --since="1 month ago"

# Ver líneas agregadas/eliminadas por autor
git log --author="JHON" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }'
```

---

## 🎯 MEJORES PRÁCTICAS

### ✅ **DO's (Hacer)**
- 🔄 Hacer `git pull` antes de empezar a trabajar
- � **Sincronizar con master después de cada deploy de producción**
- �📝 Commits pequeños y frecuentes con mensajes claros
- 🧪 Probar cambios antes de hacer push
- 📞 Comunicar cambios importantes al equipo
- 🔍 Revisar código antes de hacer merge
- 🔄 **Traer cambios de master al iniciar funcionalidades importantes**

### ❌ **DON'Ts (No Hacer)**
- 🚫 No trabajar directamente en DESARROLLO o MASTER
- 🚫 No hacer commits gigantes con muchos cambios
- 🚫 No ignorar conflictos de merge
- 🚫 No hacer push de código que no funciona
- 🚫 No hacer force push en ramas compartidas

---

## 📞 CONTACTOS Y ESCALACIÓN

### 🆘 **En caso de problemas:**

1. **Problemas menores**: Consultar este manual
2. **Conflictos complejos**: Contactar a JOGUTIERREZ
3. **Errores de producción**: Escalar inmediatamente


---

## 📚 RECURSOS ADICIONALES

### 🔗 **Enlaces Útiles**
- [Git Documentation](https://git-scm.com/doc)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Resolving Merge Conflicts](https://docs.github.com/en/github/collaborating-with-pull-requests/addressing-merge-conflicts)

### 🛠️ **Herramientas Recomendadas**
- **VS Code**: Con extensión GitLens
- **Git GUI**: SourceTree o GitHub Desktop
- **Diff Tools**: Beyond Compare o WinMerge

---

**📅 Última actualización**: Agosto 2025  
**👤 Creado por**: JOGUTIERREZ  
**🏢 Empresa**: DON LUIS
