# Frontend CSS Best Practices - Grove Platform

## Component-Based CSS Architecture

### Principio Fundamental
**SIEMPRE usar clases CSS personalizadas para componentes reutilizables** en lugar de repetir largas cadenas de clases Tailwind en el HTML.

### Estructura Recomendada

```
core/static/core/css/
├── components/          # Componentes reutilizables
│   ├── buttons.css     # .btn, .btn-primary, .btn-secondary
│   ├── cards.css       # .card, .card-header, .card-content
│   ├── forms.css       # .form-input, .form-label, .form-error
│   └── badges.css      # .badge, .badge-success, .badge-warning
├── layouts/            # Layouts y grids
│   ├── grid.css       # .grid-main, .grid-sidebar
│   └── containers.css # .container, .section
└── utilities/          # Utilidades específicas del proyecto
    ├── spacing.css    # .spacing-section, .spacing-card
    └── colors.css     # Variables de color Grove
```

### Ejemplo: Antes vs Después

#### ❌ Malo - Repetir clases largas
```html
<div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
  <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
    <h3 class="text-lg font-semibold text-gray-900 leading-6">Título</h3>
  </div>
  <div class="px-6 py-4 space-y-4">
    Contenido
  </div>
</div>
```

#### ✅ Bueno - Clases semánticas
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Título</h3>
  </div>
  <div class="card-content">
    Contenido
  </div>
</div>
```

### Implementación con @apply

```css
/* core/static/core/css/components/cards.css */
.card {
  @apply bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden;
}

.card-header {
  @apply px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.card-title {
  @apply text-lg font-semibold text-gray-900 leading-6;
}

.card-content {
  @apply px-6 py-4 space-y-4;
}
```

### Nomenclatura (BEM-like)

```css
/* Componente base */
.btn { }

/* Variantes */
.btn-primary { }
.btn-secondary { }
.btn-ghost { }

/* Estados */
.btn-loading { }
.btn-disabled { }

/* Tamaños */
.btn-sm { }
.btn-lg { }
```

### Grove Design System Colors

```css
/* Seguir especificaciones monocromáticas */
:root {
  /* Monocromático base */
  --grove-gray-50: #f9fafb;
  --grove-gray-100: #f3f4f6;
  --grove-gray-800: #1f2937;
  --grove-gray-900: #111827;
  
  /* Acentos pasteles */
  --grove-green-100: #dcfce7;
  --grove-green-800: #166534;
  --grove-blue-100: #dbeafe;
  --grove-blue-800: #1e40af;
}

.btn-primary {
  @apply bg-gray-800 text-white border border-gray-800 hover:bg-gray-900;
}

.badge-success {
  @apply bg-green-100 text-green-800;
}
```

### Reglas de Aplicación

1. **Componentes complejos (3+ clases Tailwind)**: Crear clase personalizada
2. **Elementos reutilizables**: Siempre usar clases personalizadas
3. **Variaciones simples**: Usar clases Tailwind directamente
4. **Estados interactivos**: Definir con hover:, focus:, etc.

### Integración Django

```html
<!-- templates/base.html -->
{% load static %}
<link rel="stylesheet" href="{% static 'core/css/components/cards.css' %}">
<link rel="stylesheet" href="{% static 'core/css/components/buttons.css' %}">
```

### Herramientas de Desarrollo

- **Tailwind CSS IntelliSense**: Autocompletado para @apply
- **PostCSS**: Procesamiento de @apply
- **PurgeCSS**: Eliminación de CSS no usado

## Aplicación en Agentes

### Para `code-analyzer`
- Detectar repetición de clases Tailwind largas
- Sugerir extracción a clases personalizadas

### Para agentes de frontend
- Siempre usar esta arquitectura de CSS
- Crear archivos separados por tipo de componente
- Mantener consistencia con Grove Design System

## Beneficios Medibles

1. **Reducción de código HTML**: 60-80% menos clases
2. **Mantenimiento**: Cambios centralizados
3. **Performance**: CSS optimizado y cacheable
4. **Developer Experience**: Código más legible
5. **Design System**: Consistencia automática

## Ejemplo Completo: Wave Components

Ver implementación en:
- `core/static/core/css/components/wave/`
- `core/templates/core/wave_demo.html`

Esta estructura mantiene la flexibilidad de Tailwind con la organización de un sistema de componentes profesional.