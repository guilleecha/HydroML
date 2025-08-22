"""
Context processors for Grove platform core application.
Provides global template variables across all views.
"""

from projects.models import Project, DataSource
from connectors.models import DatabaseConnection
from experiments.models import MLExperiment
from django.shortcuts import get_object_or_404
from django.conf import settings
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
    Enhanced breadcrumb navigation with dynamic path structure.
    
    Generates breadcrumbs in the format:
    - Main pages: @username/Data Sources, @username/Workspaces
    - Specific items: @username/Workspaces/project_name, @username/Data Sources/data_source_name
    
    Returns:
        dict: Breadcrumb navigation data with path structure
    """
    context = {
        'breadcrumb_path': '',
        'breadcrumb_parts': [],
        'current_section': None,
        'current_item': None,
    }
    
    if not request.user.is_authenticated:
        return context
    
    # Always start with username
    parts = [f"@{request.user.username}"]
    
    if hasattr(request, 'resolver_match') and request.resolver_match:
        namespace = request.resolver_match.namespace
        url_name = request.resolver_match.url_name
        kwargs = request.resolver_match.kwargs
        
        # Determine section and add specific items
        if namespace == 'projects':
            if url_name == 'project_list':
                # Main Workspaces page: @username/Workspaces
                parts.append("Workspaces")
                context['current_section'] = 'workspaces'
            elif url_name in ['project_detail', 'project_create']:
                # Specific project: @username/Workspaces/project_name
                parts.append("Workspaces")
                context['current_section'] = 'workspaces'
                
                # Try to get project name for detail page
                if url_name == 'project_detail':
                    project_pk = kwargs.get('pk') or kwargs.get('project_pk') or kwargs.get('project_id')
                    if project_pk:
                        try:
                            project = get_object_or_404(Project, pk=project_pk, owner=request.user)
                            parts.append(project.name)
                            context['current_item'] = project
                        except (Project.DoesNotExist, ValueError, TypeError):
                            parts.append("Unknown Project")
                elif url_name == 'project_create':
                    parts.append("New Workspace")
            
            elif url_name in ['datasource_upload', 'datasource_upload_summary', 'datasource_update']:
                # Data source within project context
                project_pk = kwargs.get('project_pk') or kwargs.get('project_id')
                if project_pk:
                    try:
                        project = get_object_or_404(Project, pk=project_pk, owner=request.user)
                        parts.extend(["Workspaces", project.name])
                        
                        # Add data source name if available
                        datasource_pk = kwargs.get('pk') or kwargs.get('datasource_id')
                        if datasource_pk and url_name != 'datasource_upload':
                            try:
                                datasource = get_object_or_404(DataSource, pk=datasource_pk, owner=request.user)
                                parts.append(datasource.name)
                                context['current_item'] = datasource
                            except (DataSource.DoesNotExist, ValueError, TypeError):
                                parts.append("Data Source")
                        elif url_name == 'datasource_upload':
                            parts.append("Upload Data")
                            
                        context['current_section'] = 'workspaces'
                    except (Project.DoesNotExist, ValueError, TypeError):
                        parts.extend(["Workspaces", "Unknown Project"])
        
        elif namespace == 'core':
            if url_name == 'data_sources_list':
                # Main Data Sources page: @username/Data Sources
                parts.append("Data Sources")
                context['current_section'] = 'data_sources'
            elif url_name in ['theme_demo', 'component_demo', 'grove_demo', 'layout_demo']:
                # Demo pages
                parts.append("System")
                if url_name == 'theme_demo':
                    parts.append("Theme Demo")
                elif url_name == 'component_demo':
                    parts.append("Component Demo")
                elif url_name == 'grove_demo':
                    parts.append("Grove Demo")
                elif url_name == 'layout_demo':
                    parts.append("Layout Demo")
                context['current_section'] = 'system'
        
        elif namespace == 'experiments':
            if url_name in ['experiment_list', 'public_experiment_list']:
                # Main Experiments page: @username/Experiments
                parts.append("Experiments")
                context['current_section'] = 'experiments'
            elif url_name in ['experiment_detail', 'experiment_create']:
                # Specific experiment: @username/Experiments/experiment_name
                parts.append("Experiments")
                context['current_section'] = 'experiments'
                
                if url_name == 'experiment_detail':
                    experiment_pk = kwargs.get('pk')
                    if experiment_pk:
                        try:
                            experiment = get_object_or_404(MLExperiment, pk=experiment_pk, project__owner=request.user)
                            parts.append(experiment.name)
                            context['current_item'] = experiment
                        except (MLExperiment.DoesNotExist, ValueError, TypeError):
                            parts.append("Unknown Experiment")
                elif url_name == 'experiment_create':
                    parts.append("New Experiment")
        
        elif namespace == 'data_tools':
            # Data Tools namespace
            parts.append("Data Sources")
            if url_name in ['datasource_detail', 'datasource_update']:
                datasource_pk = kwargs.get('pk')
                if datasource_pk:
                    try:
                        datasource = get_object_or_404(DataSource, pk=datasource_pk, owner=request.user)
                        parts.append(datasource.name)
                        context['current_item'] = datasource
                    except (DataSource.DoesNotExist, ValueError, TypeError):
                        parts.append("Unknown Data Source")
            context['current_section'] = 'data_sources'
        
        elif namespace == 'connectors':
            # Database Connections
            parts.append("Data Sources")
            if url_name in ['connection_detail', 'connection_edit']:
                connection_pk = kwargs.get('pk')
                if connection_pk:
                    try:
                        connection = get_object_or_404(DatabaseConnection, pk=connection_pk, user=request.user)
                        parts.append(connection.name)
                        context['current_item'] = connection
                    except (DatabaseConnection.DoesNotExist, ValueError, TypeError):
                        parts.append("Unknown Connection")
            context['current_section'] = 'data_sources'
    
    # Build the final breadcrumb path
    context['breadcrumb_path'] = '/'.join(parts)
    context['breadcrumb_parts'] = parts
    
    return context


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


def grove_branding(request):
    """
    Adds Grove platform branding variables to all template contexts.
    
    Usage in templates:
    - {{ SITE_NAME }} → "Grove"
    - {{ SITE_FULL_NAME }} → "GroveLab" 
    - {{ SITE_DESCRIPTION }} → "AI-powered machine learning platform..."
    - {{ SITE_LOGO }} → "core/img/logos/grove_logo.svg"
    - {{ SITE_ICON }} → "core/img/logos/grove_icon.svg"
    - {{ ECO_CREDITS_NAME }} → "Trees"
    """
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Grove'),
        'SITE_FULL_NAME': getattr(settings, 'SITE_FULL_NAME', 'GroveLab'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'AI-powered ML platform'),
        'SITE_LOGO': getattr(settings, 'SITE_LOGO', 'core/img/logos/grove_logo.svg'),
        'SITE_ICON': getattr(settings, 'SITE_ICON', 'core/img/logos/grove_icon.svg'),
        'ECO_CREDITS_NAME': getattr(settings, 'ECO_CREDITS_NAME', 'Trees'),
    }


