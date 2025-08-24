## 📋 Descripción

El frontend del Data Studio presenta dos problemas críticos que afectan la experiencia del usuario:

1. **Export Wizard aparece instantáneamente al recargar la página** - El componente Alpine.js se carga automáticamente debido a persistencia no deseada
2. **Tabla de datos no es visible** - La implementación TanStack Table no se está renderizando correctamente

## 🔍 Investigación Realizada

### Problema 1: Export Wizard Persistencia
- **Causa identificada**: Alpine.js `$persist` plugin está causando que el estado se restaure desde localStorage
- **Evidencia**: Context7 y Exa confirman que `$persist` automáticamente guarda/restaura estado entre recargas
- **Ubicación**: `data_tools/templates/data_tools/partials/_export_wizard.html`

### Problema 2: Tabla TanStack No Visible  
- **Commit funcional anterior**: `d13b63a` tenía AG Grid funcionando correctamente
- **Diferencia**: Migración de AG Grid a TanStack Table no completada correctamente
- **Ubicación**: `data_tools/templates/data_tools/data_studio.html`

## 🛠️ Solución Propuesta

### Fase 1: Eliminar Export Wizard Persistencia
- [ ] Eliminar completamente Alpine.js del Export Wizard
- [ ] Convertir a componente JavaScript puro sin persistencia
- [ ] Asegurar que solo se abra manualmente desde sidebar

### Fase 2: Reparar Tabla TanStack
- [ ] Revisar documentación TanStack Table para vanilla JS
- [ ] Verificar inicialización correcta en `data-studio-main.js`
- [ ] Asegurar que `window.gridRowData` y `window.columnDefsData` se pasen correctamente
- [ ] Validar que el contenedor `#data-preview-grid` se renderice

### Fase 3: Testing
- [ ] Verificar que Export Wizard no aparezca en reload
- [ ] Confirmar que tabla muestre datos correctamente
- [ ] Probar funcionalidad de export manual

## 📚 Referencias Técnicas

### Alpine.js Persistencia (Context7)
```javascript
// Problema identificado
<div x-data="{ isOpen: $persist(false) }">
// Solución: eliminar $persist completamente
<div x-data="{ isOpen: false }">
```

### TanStack Table Vanilla JS (Context7)
```javascript
import { createTable } from '@tanstack/table-core'
const table = createTable(options)
```

## 🔗 Archivos Afectados

- `data_tools/templates/data_tools/partials/_export_wizard.html`
- `data_tools/templates/data_tools/data_studio.html`
- `data_tools/static/data_tools/js/data-studio-main.js`
- `data_tools/static/data_tools/js/modules/tanstack-table-controller.js`

## ⚡ Prioridad

**Alta** - Afecta funcionalidad principal del Data Studio

## 🏷️ Labels

frontend, bug, data-studio, alpine.js, tanstack-table