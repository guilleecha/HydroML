# data_tools/views/missing_data_views.py
import json
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from projects.models import DataSource
from core.utils.breadcrumbs import create_basic_breadcrumbs
from ..tasks import deep_missing_data_analysis_task

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def run_deep_missing_analysis_api(request):
    """
    API endpoint to run deep missing data analysis using Celery.
    
    Expected JSON payload:
    {
        "datasource_id": "uuid",
        "target_column": "column_name",
        "required_variables": ["var1", "var2", ...]
    }
    """
    try:
        # Parse JSON body
        data = json.loads(request.body)
        datasource_id = data.get('datasource_id')
        target_column = data.get('target_column')
        required_variables = data.get('required_variables', [])
        
        # Validate input
        if not datasource_id:
            return JsonResponse({
                'success': False,
                'error': 'datasource_id is required'
            }, status=400)
        
        if not target_column:
            return JsonResponse({
                'success': False,
                'error': 'target_column is required'
            }, status=400)
        
        if not required_variables or len(required_variables) == 0:
            return JsonResponse({
                'success': False,
                'error': 'At least one required variable must be specified'
            }, status=400)
        
        # Check if datasource exists and user has access
        try:
            datasource = DataSource.objects.get(
                id=datasource_id, 
                project__owner=request.user
            )
        except DataSource.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'DataSource not found or access denied'
            }, status=404)
        
        logger.info(f"Starting deep missing data analysis for DataSource {datasource_id}")
        logger.info(f"Target column: {target_column}")
        logger.info(f"Required variables: {required_variables}")
        
        # Start the Celery task
        task = deep_missing_data_analysis_task.delay(
            datasource_id=str(datasource_id),
            target_column=target_column,
            required_variables=required_variables
        )
        
        logger.info(f"Celery task started with ID: {task.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Análisis profundo iniciado correctamente',
            'task_id': task.id,
            'datasource_id': str(datasource_id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Deep missing data analysis API error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)


@login_required
def missing_data_results_page(request, task_id):
    """
    Display the results of a deep missing data analysis.
    
    Args:
        task_id (str): Celery task ID
    """
    try:
        # Import Celery here to avoid circular imports
        from celery.result import AsyncResult
        from django.conf import settings
        
        # Get task result
        task_result = AsyncResult(task_id)
        
        # Initialize context
        context = {
            'task_id': task_id,
            'task_status': task_result.status,
            'task_ready': task_result.ready(),
            'analysis_results': None,
            'datasource': None,
            'error_message': None,
            'breadcrumbs': []
        }
        
        # Check task status
        if task_result.ready():
            if task_result.successful():
                # Task completed successfully
                task_data = task_result.get()
                
                if task_data.get('status') == 'success':
                    # Get datasource ID from task result
                    if 'datasource_id' in task_data:
                        try:
                            datasource = DataSource.objects.get(
                                id=task_data['datasource_id'],
                                project__owner=request.user
                            )
                            context['datasource'] = datasource
                            
                            # Load analysis results from datasource
                            if datasource.missing_data_report:
                                context['analysis_results'] = datasource.missing_data_report
                                
                                # Build breadcrumbs
                                context['breadcrumbs'] = create_basic_breadcrumbs(
                                    ('Workspace', reverse('projects:project_list')),
                                    (datasource.project.name, reverse('projects:project_detail', kwargs={'pk': datasource.project.pk})),
                                    (datasource.name, reverse('data_tools:data_studio_page', kwargs={'pk': datasource.pk})),
                                    'Resultados de Análisis de Datos Faltantes'
                                )
                            else:
                                context['error_message'] = 'Los resultados del análisis no están disponibles en el DataSource'
                                
                        except DataSource.DoesNotExist:
                            context['error_message'] = 'DataSource no encontrado o acceso denegado'
                    else:
                        context['error_message'] = 'ID de DataSource no encontrado en los resultados de la tarea'
                else:
                    # Task completed but with error
                    context['error_message'] = task_data.get('message', 'Error desconocido en el análisis')
            else:
                # Task failed
                context['error_message'] = f'El análisis falló: {str(task_result.info)}'
        else:
            # Task is still running
            context['task_status'] = 'PENDING'
            context['error_message'] = 'El análisis aún se está ejecutando. Por favor, espera...'
        
        return render(request, 'data_tools/missing_data_results.html', context)
        
    except Exception as e:
        logger.error(f"Missing data results page error: {e}", exc_info=True)
        
        context = {
            'task_id': task_id,
            'task_status': 'ERROR',
            'task_ready': True,
            'analysis_results': None,
            'datasource': None,
            'error_message': f'Error al cargar los resultados: {str(e)}',
            'breadcrumbs': []
        }
        
        return render(request, 'data_tools/missing_data_results.html', context)
