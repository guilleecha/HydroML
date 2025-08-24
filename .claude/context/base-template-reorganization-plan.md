# Base Template Reorganization Plan

**Target**: `core/templates/core/base_main.html`  
**Current Status**: 440 lines, complex structure, inline styles  
**Goal**: Modular, maintainable, Grove-compliant template architecture

## Current Issues Analysis

### 1. Template Structure Problems
```html
<!-- Current Issues -->
<head>
    <!-- 40+ lines of mixed CSS/JS/meta tags -->
    <style>
        /* Inline critical CSS - should be extracted */
        [x-cloak] { display: none !important; }
        html, body { min-height: 100%; }
    </style>
    <!-- Complex Alpine.js loading order issues -->
</head>
<body>
    <!-- 300+ lines of complex nested structures -->
    <!-- Duplicated panel patterns (upload, experiment) -->
    <!-- Inline Alpine.js data and methods -->
</body>
```

### 2. Specific Problems Identified
- ✅ **Inline CSS**: Critical styles mixed with template
- ✅ **Script Loading Complexity**: Complex Alpine.js initialization
- ✅ **Template Repetition**: Similar upload/experiment panel patterns
- ✅ **Low Modularity**: Difficult to maintain and test components
- ✅ **CSS Loading Issues**: Previously caused rendering failures

## Proposed Architecture

### 1. Template Hierarchy Restructure
```
New Template Structure:
├── core/templates/core/layouts/
│   └── base_grove.html           # New clean base
├── core/templates/core/partials/
│   ├── _head_grove.html          # Head section with proper loading
│   ├── _grove_navigation.html    # Enhanced headbar (already good)
│   ├── _grove_panels.html        # Reusable panel patterns
│   ├── _grove_scripts.html       # Proper script loading order
│   └── _grove_critical.html      # Critical CSS extraction
└── core/templates/core/
    └── base_main.html            # Simplified main template
```

### 2. Modular Component Design

#### Head Section (`_head_grove.html`)
```html
{% load static %}
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block page_title %}Grove{% endblock %} - Grove</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="{% static 'core/img/logos/grove_icon.svg' %}">
    
    <!-- Fonts -->
    {% include "core/partials/_grove_fonts.html" %}
    
    <!-- Grove Design System CSS -->
    {% include "core/partials/_grove_css_loading.html" %}
    
    <!-- Critical CSS -->
    {% include "core/partials/_grove_critical.html" %}
    
    {% block extra_css %}{% endblock %}
    
    <!-- Theme and Alpine.js Initialization -->
    {% include "core/partials/_grove_scripts_head.html" %}
    
    {% block extra_head %}{% endblock %}
</head>
```

#### CSS Loading Order (`_grove_css_loading.html`)
```html
<!-- Grove Design System Components FIRST -->
<link rel="stylesheet" href="{% static 'core/css/design-tokens.css' %}">
<link rel="stylesheet" href="{% static 'core/css/components/grove-navigation.css' %}">
<link rel="stylesheet" href="{% static 'core/css/components/grove-card.css' %}">
<link rel="stylesheet" href="{% static 'core/css/components/grove-button.css' %}">
<link rel="stylesheet" href="{% static 'core/css/components/grove-badge.css' %}">
<link rel="stylesheet" href="{% static 'core/css/components/grove-icon.css' %}">

<!-- Tailwind CSS AFTER Grove to avoid overriding -->
<link rel="stylesheet" href="{% static 'css/output.css' %}">

<!-- External libraries -->
<link rel="stylesheet" href="https://cdn.datatables.net/2.0.8/css/dataTables.dataTables.css" />
<link rel="stylesheet" href="https://cdn.datatables.net/responsive/3.0.2/css/responsive.dataTables.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.1.1/styles/ag-grid.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.1.1/styles/ag-theme-quartz.css">
```

#### Critical CSS (`_grove_critical.html`)
```html
<style>
/* Critical CSS for initial render - prevents FOUC */
[x-cloak] { display: none !important; }
html, body { min-height: 100%; }
.min-h-full { min-height: 100vh; }

/* Grove navigation critical styles */
.headbar-nav-link {
    @apply flex items-center px-3 py-2 text-sm font-medium transition-colors relative;
}
.headbar-nav-link-active {
    @apply text-blue-600 border-b-2 border-blue-600;
}
.headbar-nav-link-inactive {
    @apply text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white;
}
.headbar-nav-icon {
    @apply w-4 h-4 mr-2;
}
.nav-count-badge {
    @apply ml-2 bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full;
}
</style>
```

#### Script Loading (`_grove_scripts_head.html`)
```html
<!-- Sentry Browser SDK -->
{% if SENTRY_DSN %}
<script src="https://browser.sentry-cdn.com/8.38.0/bundle.tracing.min.js" crossorigin="anonymous"></script>
<script>
    window.__SENTRY_DSN__ = "{{ SENTRY_DSN }}";
</script>
{% endif %}

<!-- Alpine.js FIRST - Critical for component initialization -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<!-- Theme System - Load after Alpine.js -->
<script src="{% static 'core/js/theme/ThemeManager.js' %}"></script>
<script src="{% static 'core/js/theme/ThemeController.js' %}"></script>
```

#### Reusable Panel Pattern (`_grove_panels.html`)
```html
{% load tabler_icons %}

<!-- Generic Panel Template -->
{% with panel_id="upload-panel" panel_title="Upload Data Source" panel_width="max-w-2xl" %}
<div x-show="isUploadPanelOpen" 
     @close-upload-panel.window="isUploadPanelOpen = false"
     class="fixed inset-0 z-50"
     x-cloak>
    {% include "core/partials/_grove_panel_backdrop.html" %}
    {% include "core/partials/_grove_panel_content.html" %}
</div>
{% endwith %}

<!-- Experiment Panel - Reuses same pattern -->
{% with panel_id="experiment-panel" panel_title="Create New ML Experiment" panel_width="max-w-4xl" %}
<div x-show="isNewExperimentPanelOpen" 
     @close-new-experiment-panel.window="isNewExperimentPanelOpen = false"
     class="fixed inset-0 z-50"
     x-cloak>
    {% include "core/partials/_grove_panel_backdrop.html" %}
    {% include "core/partials/_grove_panel_content.html" %}
</div>
{% endwith %}
```

### 3. Simplified Main Template

#### New `base_main.html` (Target: 150 lines)
```html
{% extends "core/layouts/base_grove.html" %}
{% load static tabler_icons %}

{% block body_class %}h-full bg-white dark:bg-gray-900 font-sans antialiased{% endblock %}

{% block body_data %}x-data="hydroMLApp" x-init="init()"{% endblock %}

{% block panels %}
    {% include "core/partials/_grove_panels.html" %}
{% endblock %}

{% block navigation %}
    {% include "core/partials/_grove_enhanced_headbar.html" %}
{% endblock %}

{% block main %}
    <main class="min-h-screen bg-white dark:bg-gray-900">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Page Actions Header -->
            <div class="flex items-center justify-between mb-8">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {% block page_heading %}Grove{% endblock %}
                    </h1>
                    {% block page_subtitle %}{% endblock %}
                </div>
                <div class="flex items-center space-x-3">
                    {% block header_actions %}{% endblock %}
                </div>
            </div>

            <!-- Page Content -->
            {% block content %}
            {% endblock %}
        </div>
    </main>
{% endblock %}

{% block overlays %}
    {% include 'core/_loading_overlay.html' %}
{% endblock %}

{% block scripts %}
    {% include "core/partials/_grove_scripts_bottom.html" %}
    {% block extra_js %}{% endblock %}
{% endblock %}
```

#### Base Layout (`base_grove.html`)
```html
{% load static %}
<!DOCTYPE html>
<html lang="es" class="h-full">
{% include "core/partials/_head_grove.html" %}
<body class="{% block body_class %}{% endblock %}" {% block body_data %}{% endblock %}>
    {% block panels %}{% endblock %}
    
    <div class="min-h-full">
        {% block navigation %}{% endblock %}
        {% block main %}{% endblock %}
    </div>
    
    {% block overlays %}{% endblock %}
    {% block scripts %}{% endblock %}
</body>
</html>
```

## Implementation Benefits

### 1. Maintainability
- ✅ **Modular Components**: Each section in dedicated partial
- ✅ **Single Responsibility**: Each partial has one clear purpose
- ✅ **Easy Updates**: Change CSS loading order in one file
- ✅ **Testing**: Can test individual partials independently

### 2. Performance 
- ✅ **Optimal Loading**: CSS before JS, critical styles inline
- ✅ **Reduced Complexity**: Simpler templates = faster parsing
- ✅ **Cache Efficiency**: Partial templates can be cached separately

### 3. Developer Experience
- ✅ **Clear Structure**: Obvious where to make changes
- ✅ **Reusable Patterns**: Panel system can be extended
- ✅ **Grove Compliance**: Consistent with design system principles

### 4. Future-Proof
- ✅ **Component Evolution**: Easy to migrate to new Grove components
- ✅ **Theme Support**: Proper theme system integration
- ✅ **Scalability**: Template structure supports complex applications

## Migration Strategy

### Phase 1: Extract Critical Components
1. Create `_grove_critical.html` with current inline styles
2. Create `_grove_css_loading.html` with proper order
3. Create `_grove_scripts_head.html` with Alpine.js loading
4. Test that current template works with extracted partials

### Phase 2: Create Base Layout
1. Create `core/layouts/base_grove.html` 
2. Migrate `base_main.html` to extend base_grove.html
3. Test all pages still render correctly
4. Verify Alpine.js initialization works

### Phase 3: Modularize Components
1. Extract panel patterns to `_grove_panels.html`
2. Create reusable panel partials
3. Update scripts loading to `_grove_scripts_bottom.html`
4. Test all interactive functionality

### Phase 4: Optimize and Clean
1. Remove unused inline styles
2. Consolidate duplicated code
3. Add template documentation
4. Performance testing and optimization

## Risk Mitigation

### Low Risk Changes
- ✅ CSS extraction to partials (no logic change)
- ✅ Script loading optimization (improve order)
- ✅ Template documentation

### Medium Risk Changes
- ⚠️ Template inheritance restructure (test all pages)
- ⚠️ Panel pattern abstraction (verify Alpine.js binding)
- ⚠️ Script loading reorganization (check initialization order)

### High Risk Changes
- 🚨 Base template complete rewrite (requires extensive testing)

## Testing Requirements

### Manual Testing Checklist
- [ ] Dashboard loads and displays correctly
- [ ] Navigation works (all tabs, mobile menu)
- [ ] Upload panel opens and functions
- [ ] Experiment panel opens and functions
- [ ] Theme switching works
- [ ] User menu and notifications work
- [ ] Alpine.js components initialize correctly
- [ ] CSS styles load in correct order
- [ ] No JavaScript console errors
- [ ] Responsive design on mobile/tablet

### Automated Testing
- [ ] Playwright tests for all major user flows
- [ ] Template syntax validation
- [ ] CSS loading order verification
- [ ] Alpine.js initialization testing

---

**Next Step**: Create CCMP Epic for organized implementation with parallel agents