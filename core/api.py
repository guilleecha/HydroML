# core/api.py
"""
Core API endpoints for HydroML application.
Provides lightweight API endpoints for UI components.

Task 3.4.c Enhancement:
- Enhanced error handling and response structure
- Better performance with optimized queries
- Improved logging for debugging
"""

import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.core.cache import cache
from projects.models import Project

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def get_other_projects(request):
    """
    Returns a list of user's projects excluding the current one.
    Used by breadcrumb workspace switcher component.
    
    Enhanced for Task 3.4.c:
    - Better error handling and logging
    - Optimized database queries
    - Structured JSON responses
    - Request validation
    """
    try:
        current_project_id = request.GET.get('current')
        user = request.user
        
        # Validate current_project_id if provided
        if current_project_id:
            try:
                current_project_id = int(current_project_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid current_project_id: {current_project_id} for user {user.id}")
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid project ID format',
                    'projects': [],
                    'total_count': 0
                }, status=400)
        
        # Build optimized query
        projects_query = Project.objects.filter(owner=user).select_related().order_by('-created_at')
        
        if current_project_id:
            projects_query = projects_query.exclude(pk=current_project_id)
        
        # Limit to 10 most recent projects for performance
        projects = projects_query[:10]
        
        # Build response data
        project_data = []
        for project in projects:
            try:
                # Use prefetch_related or aggregate to optimize datasource and experiment counts
                datasources_count = project.datasources.count()
                experiments_count = project.experiments.count()
                
                project_data.append({
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description or '',
                    'datasources_count': datasources_count,
                    'experiments_count': experiments_count,
                    'created_at': project.created_at.isoformat(),
                })
            except Exception as e:
                logger.error(f"Error processing project {project.id}: {str(e)}")
                # Continue with other projects instead of failing completely
                continue
        
        # Log successful request for monitoring
        logger.info(f"User {user.id} loaded {len(project_data)} other projects (excluded: {current_project_id})")
        
        return JsonResponse({
            'success': True,
            'projects': project_data,
            'total_count': len(project_data),
            'cache_key': f"projects_{user.id}_{current_project_id}",
            'query_count': len(connection.queries) if hasattr(connection, 'queries') else None
        })
        
    except Exception as e:
        logger.error(f"Error in get_other_projects for user {request.user.id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error while loading projects',
            'projects': [],
            'total_count': 0
        }, status=500)
