# Grove Modal & Panel Components

Sistema completo de componentes modal y panel para HydroML usando Grove Design System.

## 📁 Archivos

- **`grove-modal.css`** - Estilos CSS del sistema modal/panel
- **`grove-modal.js`** - Funcionalidad JavaScript con gestión de accesibilidad
- **`README_grove_modal.md`** - Esta documentación

## 🎯 Características

### ✅ Modales
- **Tamaños**: `sm`, `md`, `lg`, `xl`, `2xl`, `full`
- **Backdrop**: Con fade-in/out animado
- **Responsive**: Adaptación automática en móviles
- **Accesibilidad**: Focus management, keyboard navigation, ARIA attributes

### ✅ Paneles Laterales
- **Posiciones**: Left/right slide-out panels
- **Tamaños**: `sm`, `md`, `lg`, `xl`
- **Animaciones**: Smooth slide transitions

### ✅ Dark Mode
- Soporte completo usando variables Grove (`--grove-bg-primary-dark`, etc.)

### ✅ Design System
- Usa design tokens Grove: `--shadow-modal`, `--z-index-modal`, `--grove-text-primary`
- Sin directivas `@apply` problemáticas
- Consistente con el ecosistema Grove

## 🚀 Uso Básico

### Modal Simple

```html
<!-- Trigger Button -->
<button data-grove-modal-target="#example-modal">
    Abrir Modal
</button>

<!-- Modal Structure -->
<div id="example-modal-backdrop" class="grove-modal-backdrop">
    <div id="example-modal" class="grove-modal grove-modal-md" role="dialog" aria-labelledby="modal-title">
        <!-- Header -->
        <div class="grove-modal-header">
            <h2 id="modal-title" class="grove-modal-title">Título del Modal</h2>
            <button class="grove-modal-close" aria-label="Cerrar">&times;</button>
        </div>
        
        <!-- Body -->
        <div class="grove-modal-body">
            <p>Contenido del modal aquí...</p>
        </div>
        
        <!-- Footer -->
        <div class="grove-modal-footer">
            <button class="btn-secondary">Cancelar</button>
            <button class="btn-primary">Guardar</button>
        </div>
    </div>
</div>
```

### Panel Lateral

```html
<!-- Trigger -->
<button data-grove-modal-target="#example-panel">
    Abrir Panel
</button>

<!-- Panel -->
<div id="example-panel-backdrop" class="grove-panel-backdrop">
    <div id="example-panel" class="grove-panel grove-panel-right grove-panel-lg" role="dialog">
        <div class="grove-panel-header">
            <h2 class="grove-panel-title">Configuración</h2>
            <button class="grove-modal-close">&times;</button>
        </div>
        
        <div class="grove-panel-body">
            <!-- Panel content -->
        </div>
        
        <div class="grove-panel-footer">
            <button class="btn-primary">Aplicar</button>
        </div>
    </div>
</div>
```

## 📐 Tamaños Disponibles

### Modales
- **`grove-modal-sm`**: 320px max-width
- **`grove-modal-md`**: 448px max-width (por defecto)
- **`grove-modal-lg`**: 512px max-width
- **`grove-modal-xl`**: 672px max-width
- **`grove-modal-2xl`**: 896px max-width
- **`grove-modal-full`**: 90vw width, 90vh height

### Paneles
- **`grove-panel-sm`**: 320px width
- **`grove-panel-md`**: 448px width
- **`grove-panel-lg`**: 512px width
- **`grove-panel-xl`**: 672px width

## 🎨 Variantes de Estilo

### Header Variants
```html
<div class="grove-modal-header">
    <div>
        <h2 class="grove-modal-title">Título Principal</h2>
        <p class="grove-modal-subtitle">Subtítulo opcional</p>
    </div>
    <button class="grove-modal-close">&times;</button>
</div>
```

### Body Variants
```html
<!-- Padding reducido -->
<div class="grove-modal-body grove-modal-body-sm">...</div>

<!-- Padding estándar -->
<div class="grove-modal-body">...</div>

<!-- Padding aumentado -->
<div class="grove-modal-body grove-modal-body-lg">...</div>
```

### Footer Variants
```html
<!-- Botones a la derecha (por defecto) -->
<div class="grove-modal-footer">
    <button>Cancelar</button>
    <button>Confirmar</button>
</div>

<!-- Botones a la izquierda -->
<div class="grove-modal-footer grove-modal-footer-start">
    <button>Confirmar</button>
</div>

<!-- Botones centrados -->
<div class="grove-modal-footer grove-modal-footer-center">
    <button>OK</button>
</div>

<!-- Botones separados (izq/der) -->
<div class="grove-modal-footer grove-modal-footer-between">
    <button>Cancelar</button>
    <button>Confirmar</button>
</div>
```

## 🎮 JavaScript API

### Inicialización Automática
Los modales se inicializan automáticamente al cargar la página.

### Control Manual
```javascript
// Abrir modal
groveModal.open('#my-modal-backdrop');

// Cerrar modal específico
groveModal.close('#my-modal-backdrop');

// Cerrar todos los modales
groveModal.closeAll();

// Control directo de instancia
const modalElement = document.querySelector('#my-modal');
modalElement.groveModal.open();
modalElement.groveModal.close();
```

### Eventos
```javascript
// Escuchar eventos de modal
document.addEventListener('grove-modal:opened', (e) => {
    console.log('Modal abierto:', e.detail.modal);
});

document.addEventListener('grove-modal:closed', (e) => {
    console.log('Modal cerrado:', e.detail.modal);
});
```

### Opciones de Configuración
```javascript
// Configuración personalizada
const modal = new GroveModal(element, {
    closeOnBackdrop: true,    // Cerrar al hacer click en backdrop
    closeOnEscape: true,      // Cerrar con tecla Escape
    focusOnOpen: true,        // Enfocar modal al abrir
    returnFocus: true         // Devolver focus al elemento anterior
});
```

## ♿ Accesibilidad

### Características Implementadas
- **Focus Management**: El focus se mantiene dentro del modal
- **Tab Trapping**: La navegación con Tab se limita al modal
- **Return Focus**: Al cerrar, devuelve el focus al elemento que abrió el modal
- **Keyboard Navigation**: Soporte para Escape key
- **ARIA Attributes**: `role="dialog"`, `aria-labelledby`
- **Screen Reader Support**: Estructura semántica adecuada

### Buenas Prácticas
```html
<!-- Usar ARIA labels adecuados -->
<div class="grove-modal" role="dialog" aria-labelledby="modal-title" aria-describedby="modal-description">
    <div class="grove-modal-header">
        <h2 id="modal-title" class="grove-modal-title">Título</h2>
    </div>
    <div class="grove-modal-body">
        <p id="modal-description">Descripción del contenido...</p>
    </div>
</div>

<!-- Focus inicial personalizado -->
<input data-grove-modal-focus placeholder="Este input recibe focus al abrir">

<!-- Botón de cierre accesible -->
<button class="grove-modal-close" aria-label="Cerrar modal">
    <svg><!-- icono X --></svg>
</button>
```

## 📱 Responsive Behavior

### Mobile (<640px)
- Los modales ocupan casi toda la pantalla
- `grove-modal-full` se convierte en fullscreen
- Los paneles ocupan 90vw como máximo

### Tablet y Desktop
- Mantienen sus tamaños definidos
- Centrados en viewport
- Máximo 90vh de altura

## 🎨 Integración con Grove Design System

### Variables CSS Utilizadas
```css
/* Colores */
--grove-bg-primary
--grove-bg-secondary  
--grove-text-primary
--grove-text-secondary
--grove-border-primary

/* Espaciado */
--space-1, --space-2, --space-3, --space-4, --space-6, --space-8

/* Typography */
--font-size-sm, --font-size-lg
--font-weight-medium, --font-weight-semibold

/* Borders & Shadows */
--radius-md, --radius-lg
--shadow-modal, --shadow-focus

/* Z-index */
--z-index-modal

/* Animations */
--duration-fast, --duration-normal
--ease-out
```

## 🔧 Personalización

### CSS Custom Properties
```css
/* Personalizar duración de animaciones */
.grove-modal-backdrop {
    --duration-normal: 200ms; /* Override default */
}

/* Personalizar z-index */
.my-special-modal {
    --z-index-modal: 60; /* Más alto que default */
}
```

### Clases CSS Personalizadas
```css
/* Modal con estilo especial */
.grove-modal-success {
    border-left: 4px solid var(--grove-success);
}

.grove-modal-success .grove-modal-title {
    color: var(--grove-success);
}
```

## 🔄 Migración desde Modales Existentes

### Antes (código existente)
```html
<div class="fixed inset-0 bg-black bg-opacity-50 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md">
        <div class="px-6 py-4 border-b">
            <h3 class="text-lg font-semibold">Title</h3>
        </div>
    </div>
</div>
```

### Después (Grove Modal)
```html
<div class="grove-modal-backdrop">
    <div class="grove-modal grove-modal-md">
        <div class="grove-modal-header">
            <h3 class="grove-modal-title">Title</h3>
            <button class="grove-modal-close">&times;</button>
        </div>
    </div>
</div>
```

## 🐛 Troubleshooting

### Modal no se abre
1. Verificar que el JavaScript está cargado
2. Comprobar que el selector en `data-grove-modal-target` es correcto
3. Asegurar que el elemento tiene la clase `grove-modal`

### Focus no funciona correctamente
1. Verificar que los elementos focusables no están disabled
2. Comprobar que no hay `tabindex="-1"` en elementos que deberían ser focusables
3. Usar `data-grove-modal-focus` para control manual del focus inicial

### Animaciones no fluidas
1. Verificar que las variables CSS de duración están definidas
2. Comprobar que no hay conflictos con otras animaciones CSS
3. Revisar que `transition-duration` usa variables Grove

## 📚 Ejemplos Avanzados

### Modal con Formulario
```html
<div class="grove-modal-backdrop">
    <div class="grove-modal grove-modal-lg">
        <form>
            <div class="grove-modal-header">
                <h2 class="grove-modal-title">Crear Usuario</h2>
                <button type="button" class="grove-modal-close">&times;</button>
            </div>
            
            <div class="grove-modal-body">
                <div class="form-group">
                    <label for="user-name">Nombre</label>
                    <input id="user-name" data-grove-modal-focus>
                </div>
                <div class="form-group">
                    <label for="user-email">Email</label>
                    <input id="user-email" type="email">
                </div>
            </div>
            
            <div class="grove-modal-footer">
                <button type="button" class="btn-secondary">Cancelar</button>
                <button type="submit" class="btn-primary">Crear Usuario</button>
            </div>
        </form>
    </div>
</div>
```

### Panel de Configuración
```html
<div class="grove-panel-backdrop">
    <div class="grove-panel grove-panel-right grove-panel-xl">
        <div class="grove-panel-header">
            <h2 class="grove-panel-title">Configuración Avanzada</h2>
            <button class="grove-modal-close">&times;</button>
        </div>
        
        <div class="grove-panel-body">
            <div class="config-section">
                <h3>Notificaciones</h3>
                <!-- Config options -->
            </div>
            <div class="config-section">
                <h3>Privacidad</h3>
                <!-- Config options -->
            </div>
        </div>
        
        <div class="grove-panel-footer">
            <button class="btn-secondary">Restablecer</button>
            <button class="btn-primary">Guardar Cambios</button>
        </div>
    </div>
</div>
```

---

## ✅ Checklist de Implementación

- [x] CSS compilado sin errores
- [x] JavaScript funcional con events
- [x] Accesibilidad completa (focus, keyboard, ARIA)
- [x] Responsive design
- [x] Dark mode support
- [x] Grove design tokens integration
- [x] Auto-initialization
- [x] Documentación completa

**Estado**: ✅ **Completamente implementado y listo para usar**