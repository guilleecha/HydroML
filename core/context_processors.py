"""
Context processors for HydroML core application.
Provides global template variables across all views.
"""

from projects.models import Project, DataSource
from connectors.models import DatabaseConnection
from experiments.models import MLExperiment
from django.shortcuts import get_object_or_404
import os


def navigation_context(request):
    """
    Add navigation-related context variables to all templates.
    
    This processor determines the current project context based on:
    1. URL parameters (project_pk, project_id)
    2. Session data
    3. View-specific logic
    
    Returns:
        dict: Context variables for navigation
    """
    context = {
        'current_project': None,
        'is_project_context': False,
    }
    
    # Method 1: Check URL parameters for project context
    project_pk = None
    
    # Look for project_pk in URL kwargs
    if hasattr(request, 'resolver_match') and request.resolver_match:
        kwargs = request.resolver_match.kwargs
        namespace = request.resolver_match.namespace
        
        # Only treat 'pk' as project_pk if we're in project-related namespaces
        # Avoid treating DataSource UUIDs as Project UUIDs in data_tools namespace
        if namespace == 'projects':
            project_pk = kwargs.get('project_pk') or kwargs.get('pk')
        else:
            project_pk = kwargs.get('project_pk')
        
        # Also check for project_id parameter
        if not project_pk:
            project_pk = kwargs.get('project_id')
    
    # Method 2: Check GET/POST parameters
    if not project_pk:
        project_pk = request.GET.get('project') or request.POST.get('project')
    
    # Method 3: Check if we're in project-related namespaces/URLs
    if not project_pk and hasattr(request, 'resolver_match') and request.resolver_match:
        namespace = request.resolver_match.namespace
        url_name = request.resolver_match.url_name
        
        # If we're in project detail views, try to extract from path
        if namespace == 'projects' and url_name in ['project_detail']:
            # Extract from path: /projects/uuid/ -> uuid
            path_parts = [p for p in request.path.split('/') if p]
            if len(path_parts) >= 2 and path_parts[0] == 'projects':
                try:
                    project_pk = path_parts[1]  # UUID as string
                except (ValueError, IndexError):
                    pass
    
    # If we found a project_pk, try to load the project
    if project_pk:
        try:
            if request.user.is_authenticated:
                current_project = get_object_or_404(Project, pk=project_pk, owner=request.user)
                context['current_project'] = current_project
                context['is_project_context'] = True
        except (Project.DoesNotExist, ValueError, TypeError):
            # Invalid project_pk or no access
            pass
    
    return context


def breadcrumb_context(request):
    """
    Generate breadcrumb navigation based on current URL and context.
    
    Returns:
        dict: Breadcrumb navigation data
    """
    breadcrumbs = []
    
    if hasattr(request, 'resolver_match') and request.resolver_match:
        namespace = request.resolver_match.namespace
        url_name = request.resolver_match.url_name
        
        # Always start with Home
        breadcrumbs.append({
            'name': 'Overview',
            'url': '/dashboard/',
            'active': False
        })
        
        # Add namespace-specific breadcrumbs
        if namespace == 'projects':
            breadcrumbs.append({
                'name': 'Workspaces',
                'url': '/projects/',
                'active': url_name == 'project_list'
            })
            
            # Add project-specific breadcrumb if in project context
            # Reuse the same logic from navigation_context to avoid circular import
            project_pk = None
            if hasattr(request, 'resolver_match') and request.resolver_match:
                kwargs = request.resolver_match.kwargs
                # Only treat 'pk' as project_pk if we're in project namespace
                if namespace == 'projects':
                    project_pk = kwargs.get('project_pk') or kwargs.get('pk') or kwargs.get('project_id')
                else:
                    project_pk = kwargs.get('project_pk') or kwargs.get('project_id')
            
            current_project = None
            if project_pk and request.user.is_authenticated:
                try:
                    current_project = get_object_or_404(Project, pk=project_pk, owner=request.user)
                except (Project.DoesNotExist, ValueError, TypeError):
                    current_project = None
            
            if current_project and url_name in ['project_detail']:
                breadcrumbs.append({
                    'name': current_project.name,
                    'url': f'/projects/{current_project.pk}/',
                    'active': url_name == 'project_detail'
                })
        
        elif namespace == 'experiments':
            breadcrumbs.append({
                'name': 'Experiments',
                'url': '/experiments/',
                'active': url_name in ['experiment_list', 'public_experiment_list']
            })
        
        elif namespace == 'data_tools':
            breadcrumbs.append({
                'name': 'Data Tools',
                'url': '/data-tools/',
                'active': True
            })
        
        elif namespace == 'connectors':
            breadcrumbs.append({
                'name': 'Data Sources',
                'url': '/connectors/',
                'active': True
            })
    
    return {
        'breadcrumbs': breadcrumbs
    }


def sentry_dsn(request):
    """
    Inject SENTRY_DSN from environment into all templates so the frontend
    can initialize Sentry Browser SDK without hardcoding secrets.
    """
    return {
        'SENTRY_DSN': os.getenv('SENTRY_DSN', '')
    }


def navigation_counts(request):
    """
    Provide counts for navigation badges (GitHub-style).
    
    Returns:
        dict: Count variables for navigation items
    """
    context = {
        'total_workspaces_count': 0,
        'total_datasources_count': 0,
        'total_experiments_count': 0,
    }
    
    if request.user.is_authenticated:
        try:
            # Count workspaces owned by user
            context['total_workspaces_count'] = Project.objects.filter(owner=request.user).count()
            
            # Count data sources (uploaded files + database connections)
            datasources_count = DataSource.objects.filter(owner=request.user).count()
            connections_count = DatabaseConnection.objects.filter(user=request.user).count()
            context['total_datasources_count'] = datasources_count + connections_count
            
            # Count experiments owned by user
            context['total_experiments_count'] = MLExperiment.objects.filter(
                project__owner=request.user
            ).count()
            
        except Exception:
            # If any model doesn't exist or there's an error, just use defaults
            pass
    
    return context
