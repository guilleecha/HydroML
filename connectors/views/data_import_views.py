# connectors/views/data_import_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from ..models import DatabaseConnection
from ..services import DatabaseConnectionService
from ..tasks import import_data_from_database_task, get_database_tables_task
from projects.models import Project


class DatabaseImportSelectConnectionView(LoginRequiredMixin, TemplateView):
    """View for selecting a database connection for data import."""
    
    template_name = 'connectors/data_import/select_connection.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get project if specified
        project_id = self.kwargs.get('project_id')
        if project_id:
            context['project'] = get_object_or_404(
                Project, 
                id=project_id, 
                owner=self.request.user
            )
        
        # Get user's database connections
        context['connections'] = DatabaseConnection.objects.filter(
            user=self.request.user
        ).order_by('name')
        
        context['page_title'] = 'Select Database Connection'
        return context


class DatabaseImportQueryView(LoginRequiredMixin, View):
    """View for building and executing database queries for import."""
    
    def get(self, request, connection_id, project_id=None):
        """Display the query builder interface."""
        connection = get_object_or_404(
            DatabaseConnection,
            id=connection_id,
            user=request.user
        )
        
        project = None
        if project_id:
            project = get_object_or_404(
                Project,
                id=project_id,
                owner=request.user
            )
        
        context = {
            'connection': connection,
            'project': project,
            'page_title': f'Import Data from {connection.name}'
        }
        
        return render(request, 'connectors/data_import/query_builder.html', context)
    
    def post(self, request, connection_id, project_id=None):
        """Execute the query and create a DataSource."""
        connection = get_object_or_404(
            DatabaseConnection,
            id=connection_id,
            user=request.user
        )
        
        project = None
        if project_id:
            project = get_object_or_404(
                Project,
                id=project_id,
                owner=request.user
            )
        
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            datasource_name = data.get('datasource_name', '').strip()
            description = data.get('description', '').strip()
            execute_async = data.get('async', False)
            
            # Validate input
            if not query:
                return JsonResponse({
                    'success': False,
                    'error': 'SQL query is required'
                }, status=400)
            
            if not datasource_name:
                return JsonResponse({
                    'success': False,
                    'error': 'DataSource name is required'
                }, status=400)
            
            if not project:
                return JsonResponse({
                    'success': False,
                    'error': 'Project is required'
                }, status=400)
            
            if execute_async:
                # Execute asynchronously using Celery
                task = import_data_from_database_task.delay(
                    connection_id=str(connection.id),
                    query=query,
                    datasource_name=datasource_name,
                    project_id=str(project.id),
                    user_id=request.user.id,
                    description=description
                )
                
                return JsonResponse({
                    'success': True,
                    'task_id': task.id,
                    'message': 'Data import started in background'
                })
            else:
                # Execute synchronously
                success, result = DatabaseConnectionService.create_datasource_from_query(
                    connection=connection,
                    query=query,
                    datasource_name=datasource_name,
                    project=project,
                    description=description
                )
                
                if success:
                    datasource = result
                    return JsonResponse({
                        'success': True,
                        'datasource_id': str(datasource.id),
                        'datasource_name': datasource.name,
                        'redirect_url': reverse('projects:datasource_detail', kwargs={
                            'project_id': project.id,
                            'datasource_id': datasource.id
                        })
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': result
                    }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }, status=500)


@login_required
@require_POST
def get_database_tables_view(request):
    """AJAX view to get tables from a database connection."""
    
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        
        if not connection_id:
            return JsonResponse({
                'success': False,
                'error': 'Connection ID is required'
            }, status=400)
        
        # Get the connection
        try:
            connection = DatabaseConnection.objects.get(
                id=connection_id,
                user=request.user
            )
        except DatabaseConnection.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Connection not found or you don\'t have permission to access it'
            }, status=404)
        
        # Get tables
        success, result = DatabaseConnectionService.get_table_list(connection)
        
        if success:
            return JsonResponse({
                'success': True,
                'tables': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result
            }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_POST
def get_table_columns_view(request):
    """AJAX view to get columns from a database table."""
    
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        table_name = data.get('table_name')
        
        if not connection_id or not table_name:
            return JsonResponse({
                'success': False,
                'error': 'Connection ID and table name are required'
            }, status=400)
        
        # Get the connection
        try:
            connection = DatabaseConnection.objects.get(
                id=connection_id,
                user=request.user
            )
        except DatabaseConnection.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Connection not found or you don\'t have permission to access it'
            }, status=404)
        
        # Get columns
        success, result = DatabaseConnectionService.get_table_columns(connection, table_name)
        
        if success:
            return JsonResponse({
                'success': True,
                'columns': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result
            }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_POST
def preview_query_view(request):
    """AJAX view to preview query results without creating a DataSource."""
    
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        query = data.get('query', '').strip()
        
        if not connection_id or not query:
            return JsonResponse({
                'success': False,
                'error': 'Connection ID and query are required'
            }, status=400)
        
        # Get the connection
        try:
            connection = DatabaseConnection.objects.get(
                id=connection_id,
                user=request.user
            )
        except DatabaseConnection.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Connection not found or you don\'t have permission to access it'
            }, status=404)
        
        # Execute query with limit for preview
        success, result = DatabaseConnectionService.execute_query(
            connection, 
            query, 
            limit=100  # Limit preview to 100 rows
        )
        
        if success:
            df = result
            return JsonResponse({
                'success': True,
                'data': {
                    'columns': list(df.columns),
                    'rows': df.values.tolist(),
                    'total_rows': len(df),
                    'preview_limit': 100
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result
            }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)
