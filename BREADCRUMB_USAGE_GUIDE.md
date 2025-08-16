# Breadcrumb Navigation System

This document explains how to implement and use the breadcrumb navigation system in the HydroML application.

## Overview

The breadcrumb system provides consistent navigation patterns across the application, helping users understand their current location and navigate back to parent pages.

## Frontend Implementation (Template)

The breadcrumb system is built into the base template (`core/templates/core/base.html`) using a dedicated block:

```django
{% block breadcrumbs %}
    {% if breadcrumbs %}
        <nav class="flex items-center space-x-2 text-sm" aria-label="Breadcrumb">
            <ol class="flex items-center space-x-2">
                {% for breadcrumb in breadcrumbs %}
                    <li class="flex items-center">
                        {% if not forloop.first %}
                            <!-- Separator icon -->
                        {% endif %}
                        
                        {% if forloop.last %}
                            <!-- Current page (no link) -->
                            <span class="text-foreground-default font-medium">{{ breadcrumb.name }}</span>
                        {% else %}
                            <!-- Link to previous pages -->
                            <a href="{{ breadcrumb.url }}" class="text-foreground-muted hover:text-foreground-default">
                                {{ breadcrumb.name }}
                            </a>
                        {% endif %}
                    </li>
                {% endfor %}
            </ol>
        </nav>
    {% endif %}
{% endblock %}
```

## Backend Implementation (Views)

### Method 1: Using Utility Functions (Recommended)

```python
from core.utils.breadcrumbs import create_project_breadcrumbs, create_experiment_breadcrumbs

# For project-related pages
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    breadcrumbs = create_project_breadcrumbs(project)
    # Current page is automatically added as the final breadcrumb
    
    context = {
        'project': project,
        'breadcrumbs': breadcrumbs
    }
    return render(request, 'template.html', context)

# For experiment-related pages
def experiment_detail(request, pk):
    experiment = get_object_or_404(MLExperiment, pk=pk)
    breadcrumbs = create_experiment_breadcrumbs(experiment)
    
    context = {
        'experiment': experiment,
        'breadcrumbs': breadcrumbs
    }
    return render(request, 'template.html', context)

# For custom breadcrumbs
def custom_view(request):
    breadcrumbs = create_basic_breadcrumbs(
        ('Home', reverse('home')),
        ('Section', reverse('section')),
        'Current Page'  # No URL for current page
    )
    
    context = {'breadcrumbs': breadcrumbs}
    return render(request, 'template.html', context)
```

### Method 2: Manual Creation

```python
def my_view(request):
    breadcrumbs = [
        {'name': 'Proyectos', 'url': reverse('projects:project_list')},
        {'name': 'My Project', 'url': reverse('projects:project_detail', kwargs={'pk': project_id})},
        {'name': 'Current Page'}  # No 'url' key for current page
    ]
    
    context = {'breadcrumbs': breadcrumbs}
    return render(request, 'template.html', context)
```

## Available Utility Functions

### `create_basic_breadcrumbs(*items)`
Creates breadcrumbs from (name, url) tuples. The last item should be a string (current page).

```python
breadcrumbs = create_basic_breadcrumbs(
    ('Home', '/'),
    ('Projects', '/projects/'),
    'Current Page'
)
```

### `create_project_breadcrumbs(project, current_page_name=None)`
Creates standard breadcrumbs for project-related pages.

```python
# Just project breadcrumb
breadcrumbs = create_project_breadcrumbs(project)

# Project + custom current page
breadcrumbs = create_project_breadcrumbs(project, 'Settings')
```

### `create_experiment_breadcrumbs(experiment, current_page_name=None)`
Creates standard breadcrumbs for experiment-related pages.

```python
# Just experiment breadcrumb
breadcrumbs = create_experiment_breadcrumbs(experiment)

# Experiment + custom current page  
breadcrumbs = create_experiment_breadcrumbs(experiment, 'Edit')
```

## Breadcrumb Structure

Each breadcrumb is a dictionary with:
- `name` (required): Display text
- `url` (optional): Link URL. If missing, renders as plain text (current page)

Example:
```python
[
    {'name': 'Proyectos', 'url': '/projects/'},
    {'name': 'My Project', 'url': '/projects/123/'},
    {'name': 'Current Page'}  # No URL = current page
]
```

## Styling

The breadcrumbs use the application's design system:
- `text-foreground-muted`: For clickable links
- `text-foreground-default`: For current page
- `hover:text-foreground-default`: Hover state for links
- Chevron separators between items
- Responsive text sizing

## Best Practices

1. **Always use utility functions** when possible for consistency
2. **Keep breadcrumb names short** but descriptive
3. **The last item should never have a URL** (represents current page)
4. **Include breadcrumbs in all detail/form pages** for better UX
5. **Test breadcrumb links** to ensure they work correctly

## Examples in Codebase

- Project Detail: `projects/views/project_views.py`
- Experiment Detail: `experiments/views/experiment_results_views.py`
- Experiment Create: `experiments/views/experiment_management_views.py`
