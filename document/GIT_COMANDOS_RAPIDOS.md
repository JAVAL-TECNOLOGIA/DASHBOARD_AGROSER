# ⚡ Comandos Git - Referencia Rápida

## 👥 **PARA DESARROLLADORES (JHON/YERSON)**

### 🚀 **Inicio de Trabajo Diario**
```bash
git checkout feature/tu-nombre      # Cambiar a tu rama
git pull origin feature/tu-nombre   # Actualizar tu rama
git status                          # Verificar estado
```

### 📝 **Guardar y Subir Cambios**
```bash
git add .                                               # Agregar cambios
git commit -m "NOMBRE: TIPO - Descripción del cambio"  # Guardar con mensaje
git push origin feature/tu-nombre                      # Subir a tu rama
```

### 🔍 **Verificación**
```bash
git status          # Ver archivos modificados
git log --oneline   # Ver historial de commits
git branch          # Ver rama actual
```

---

## 👨‍💼 **PARA LÍDER (JOGUTIERREZ)**

### 🔄 **Integrar Cambios a DESARROLLO**
```bash
git checkout DESARROLLO                    # Cambiar a DESARROLLO
git pull origin DESARROLLO                 # Actualizar DESARROLLO
git merge origin/feature/jhon-gutierrez    # Integrar cambios de JHON
git merge origin/feature/yerson-garcia     # Integrar cambios de YERSON
git push origin DESARROLLO                 # Subir cambios integrados
```

### 🚀 **Deploy a Producción**
```bash
git checkout master        # Cambiar a master
git pull origin master     # Actualizar master
git merge DESARROLLO       # Integrar desde DESARROLLO
git push origin master     # Deploy a producción
```

---

## 🚨 **RESOLUCIÓN DE CONFLICTOS**

### 🔍 **Detectar Conflicto**
```bash
# Al hacer merge verás:
CONFLICT (content): Merge conflict in archivo.js
Automatic merge failed; fix conflicts and then commit the result.
```

### 🛠️ **Resolver Paso a Paso**
```bash
git status                           # Ver archivos con conflicto
# Editar archivo y eliminar marcadores <<<<<<< ======= >>>>>>>
git add archivo_resuelto.js          # Marcar como resuelto
git commit -m "MERGE: Resolver conflicto en archivo.js"  # Completar merge
```

### 🆘 **En Caso de Emergencia**
```bash
git merge --abort      # Cancelar merge y volver al estado anterior
```

---

## 📋 **CONVENCIONES**

### 💬 **Mensajes de Commit**
```bash
"JHON: FEAT - Agregar modal de confirmación"
"YERSON: FIX - Corregir error en carga de datos"
"JHON: STYLE - Mejorar diseño responsive"
"YERSON: REFACTOR - Optimizar consultas SQL"
```

### 🌳 **Estructura de Ramas**
```
master (producción)
├── DESARROLLO (testing)
    ├── feature/jhon-gutierrez
    └── feature/yerson-garcia
```

---

## 🚨 **COMANDOS DE EMERGENCIA**

### 🔄 **Deshacer Cambios**
```bash
git checkout -- archivo.py          # Deshacer cambios en archivo específico
git reset --soft HEAD~1             # Deshacer último commit (mantener cambios)
git reset --hard HEAD~1             # Deshacer último commit (perder cambios)
```

### 🆘 **Sincronizar Forzado**
```bash
git fetch origin
git reset --hard origin/tu-rama     # ⚠️ CUIDADO: Borra cambios locales
```

---

## ✅ **CHECKLIST DIARIO**

### **Antes de Empezar:**
- [ ] Estoy en mi rama personal
- [ ] Mi rama está actualizada
- [ ] No hay cambios pendientes de ayer

### **Antes de Hacer Push:**
- [ ] El código funciona localmente
- [ ] Los mensajes de commit son claros
- [ ] No hay archivos innecesarios agregados

### **Fin del Día:**
- [ ] Todos los cambios están en el repositorio
- [ ] No hay conflictos pendientes
- [ ] La rama personal está actualizada

---

## 📞 **CONTACTOS RÁPIDOS**

| Problema | Contacto |
|----------|----------|
| Conflictos simples | Consultar manual |
| Conflictos complejos | JOGUTIERREZ |
| Errores de producción | Escalar inmediatamente |
| Dudas de proceso | Chat del equipo |

---

## 🎯 **RECORDATORIOS IMPORTANTES**

- 🚫 **NUNCA** trabajar directamente en DESARROLLO o MASTER
- 📝 **SIEMPRE** hacer commit con mensajes descriptivos
- 🔄 **FRECUENTEMENTE** actualizar tu rama personal
- 🧪 **SIEMPRE** probar antes de hacer push
- 💬 **COMUNICAR** cambios importantes al equipo

---

**📅 Actualizado**: Agosto 2025  
**🏢 Proyecto**: PORTAL AEI - DON LUIS
