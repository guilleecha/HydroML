# Sample Migration Examples - Wave to Grove Components

This document demonstrates the practical conversion process from Wave/Tailwind patterns to Grove Design System components.

## Example 1: Experiment Configuration Card Migration

### BEFORE (Current Wave Pattern)
**File**: `experiments/templates/experiments/partials/_experiment_config_card.html` (Lines 1-10)

```html
<!-- Configuración Card -->
<div class="bg-white dark:bg-darcula-background-lighter rounded-xl border border-border-default shadow-card p-6 hover:shadow-lg transition-shadow">
    <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-foreground-default dark:text-darcula-foreground">Configuración</h3>
        <svg class="w-5 h-5 text-brand-600 dark:text-darcula-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
    </div>
    <!-- Content continues... -->
</div>
```

### AFTER (Grove Component Migration)

```html
<!-- Configuración Card -->
<div class="grove-card">
    <div class="grove-card-header">
        <h3 class="grove-card-title">Configuración</h3>
        <div class="grove-card-icon">
            {% include "core/components/grove_icon.html" with icon="settings" class="w-5 h-5 text-brand-600" %}
        </div>
    </div>
    <div class="grove-card-content">
        <!-- Content continues... -->
    </div>
</div>
```

**Migration Benefits:**
- ✅ Semantic class names indicating purpose
- ✅ Consistent spacing via design tokens
- ✅ Built-in hover and focus states
- ✅ Automatic dark mode support
- ✅ Reduced custom styling requirements

## Example 2: TanStack Table Container Migration

### BEFORE (Current Tailwind Pattern)
**File**: `data_tools/templates/data_tools/partials/_tanstack_table.html` (Lines 4-8)

```html
<div class="bg-white border border-gray-200 rounded-lg shadow-sm">
    <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">Data Table</h2>
    </div>
    <!-- Table content... -->
</div>
```

### AFTER (Grove Component Migration)

```html
<div class="grove-card">
    <div class="grove-card-header">
        <h2 class="grove-card-title">Data Table</h2>
    </div>
    <div class="grove-card-content">
        <!-- Table content... -->
    </div>
</div>
```

**Migration Benefits:**
- ✅ Consistent with other cards across the app
- ✅ Uses design tokens for spacing
- ✅ Automatic theme inheritance
- ✅ Simplified markup

## Example 3: Dashboard Statistics Card Migration

### BEFORE (Mixed Pattern)
**File**: `core/templates/core/dashboard.html` (Lines 58-69)

```html
<!-- DataSources Card -->
<div class="grove-card stat-card">
    <div class="grove-card-content flex items-center justify-between">
        <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Fuentes de Datos</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">{{ total_datasources }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">Datasets disponibles</p>
        </div>
        <div class="bg-blue-100 dark:bg-blue-900/20 rounded-full p-3">
            {% tabler_icon_outline 'database' 'w-6 h-6 text-blue-600 dark:text-blue-400' %}
        </div>
    </div>
</div>
```

### AFTER (Full Grove Implementation)

```html
<!-- DataSources Card -->
<div class="grove-card grove-card--info stat-card">
    <div class="grove-card-content grove-stat-layout">
        <div class="grove-stat-content">
            <p class="grove-stat-label">Fuentes de Datos</p>
            <p class="grove-stat-value">{{ total_datasources }}</p>
            <p class="grove-stat-description">Datasets disponibles</p>
        </div>
        <div class="grove-stat-icon grove-stat-icon--info">
            {% tabler_icon_outline 'database' 'w-6 h-6' %}
        </div>
    </div>
</div>
```

**Enhanced CSS Required:**
```css
/* Add to grove-card.css */
.grove-stat-layout {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.grove-stat-value {
    font-size: 1.875rem;
    font-weight: 700;
    color: var(--grove-text-primary);
    margin-top: var(--space-1);
}

.grove-stat-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--grove-text-secondary);
}

.grove-stat-description {
    font-size: 0.75rem;
    color: var(--grove-text-tertiary);
    margin-top: var(--space-1);
}

.grove-stat-icon {
    padding: var(--space-3);
    border-radius: 50%;
}

.grove-stat-icon--info {
    background-color: var(--grove-info-subtle);
    color: var(--grove-info);
}
```

## Example 4: Form Input Migration

### BEFORE (Manual Tailwind Styling)

```html
<div class="mb-4">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Dataset Name
    </label>
    <input type="text" 
           name="name" 
           class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
           required>
</div>
```

### AFTER (Grove Form Components)

```html
<div class="grove-input-group">
    <label class="grove-input-label">Dataset Name</label>
    <input type="text" 
           name="name" 
           class="grove-input-field" 
           required>
</div>
```

**New Grove Form CSS Required:**
```css
/* Add to grove-form.css */
.grove-input-group {
    margin-bottom: var(--space-4);
}

.grove-input-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--grove-text-secondary);
    margin-bottom: var(--space-2);
}

.grove-input-field {
    width: 100%;
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--grove-border-primary);
    border-radius: var(--radius-md);
    background-color: var(--grove-bg-surface);
    color: var(--grove-text-primary);
    font-size: 0.875rem;
    transition: var(--transition-all);
}

.grove-input-field:focus {
    outline: none;
    border-color: var(--grove-focus-ring);
    box-shadow: 0 0 0 2px var(--grove-focus-ring-offset);
}
```

## Migration Checklist Template

For each component migration, follow this systematic approach:

### Pre-Migration Analysis
- [ ] Identify all instances of the component pattern
- [ ] Document current functionality and interactions
- [ ] Note any custom CSS or JavaScript dependencies
- [ ] Take screenshots for visual regression testing

### Migration Implementation
- [ ] Replace container elements with Grove equivalents
- [ ] Convert headers to `grove-card-header` + `grove-card-title`
- [ ] Wrap content in `grove-card-content`
- [ ] Apply appropriate semantic variants if needed
- [ ] Update any related CSS classes
- [ ] Test JavaScript functionality

### Post-Migration Validation
- [ ] Visual comparison with original design
- [ ] Functional testing of all interactions
- [ ] Dark mode compatibility check
- [ ] Mobile responsiveness verification
- [ ] Accessibility audit (keyboard navigation, screen readers)
- [ ] Performance impact assessment

### Code Quality
- [ ] Remove unused Tailwind classes
- [ ] Update any related JavaScript selectors
- [ ] Add comments explaining Grove component usage
- [ ] Update documentation if component is reused

## Common Migration Patterns

### Pattern 1: Card Container
```diff
- <div class="bg-white dark:bg-gray-800 rounded-lg border shadow-sm p-6">
+ <div class="grove-card">
+   <div class="grove-card-content">
```

### Pattern 2: Card with Header
```diff
- <div class="bg-white rounded-lg border">
-   <div class="px-6 py-4 border-b">
-     <h3 class="text-lg font-semibold">Title</h3>
-   </div>
-   <div class="p-6">Content</div>
- </div>
+ <div class="grove-card">
+   <div class="grove-card-header">
+     <h3 class="grove-card-title">Title</h3>
+   </div>
+   <div class="grove-card-content">Content</div>
+ </div>
```

### Pattern 3: Status Cards
```diff
- <div class="bg-green-50 border-green-200 text-green-800 rounded-lg p-4">
+ <div class="grove-card grove-card--success">
+   <div class="grove-card-content">
```

## Testing Strategy for Migrations

### Visual Regression Testing
1. **Before**: Screenshot all components in both light and dark modes
2. **After**: Screenshot migrated components
3. **Compare**: Use tools like Percy or Chromatic for pixel-perfect comparison
4. **Approve**: Sign off on acceptable differences (improved spacing, better colors)

### Functional Testing
1. **Interactive Elements**: Click all buttons, test hover states
2. **Form Validation**: Ensure error states work correctly
3. **Responsive Design**: Test on mobile, tablet, desktop breakpoints
4. **Accessibility**: Use axe-core or similar tools for automated testing

### Performance Testing
1. **Bundle Size**: Measure CSS size before/after migration
2. **Render Time**: Check for any performance regressions
3. **Memory Usage**: Monitor for memory leaks in JavaScript components

This systematic approach ensures high-quality migrations that maintain functionality while improving consistency and maintainability.