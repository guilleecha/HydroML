# connectors/views/database_connection_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from ..models import DatabaseConnection
from ..forms import DatabaseConnectionForm, DatabaseConnectionTestForm


class DatabaseConnectionListView(LoginRequiredMixin, ListView):
    """List all database connections for the current user."""
    
    model = DatabaseConnection
    template_name = 'connectors/database_connections/list.html'
    context_object_name = 'connections'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = DatabaseConnection.objects.filter(user=self.request.user)
        # Handle project filter if provided in URL parameters
        project_id = self.request.GET.get('project')
        if project_id:
            # For now, we'll just filter by user as the project relation may not exist yet
            # This would be enhanced when implementing proper data source models
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Data Sources'
        
        # Pass project to the template if provided
        project_id = self.request.GET.get('project')
        if project_id:
            from projects.models import Project
            try:
                context['project'] = Project.objects.get(id=project_id)
                context['current_project'] = context['project']  # For consistency with other templates
            except Project.DoesNotExist:
                pass
            
        return context


class DatabaseConnectionCreateView(LoginRequiredMixin, CreateView):
    """Create a new database connection."""
    
    model = DatabaseConnection
    form_class = DatabaseConnectionForm
    template_name = 'connectors/database_connections/form.html'
    
    def get_success_url(self):
        return reverse('connectors:database_connections')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Database connection "{form.instance.name}" created successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Database Connection'
        context['form_action'] = 'Create'
        return context


class DatabaseConnectionUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing database connection."""
    
    model = DatabaseConnection
    form_class = DatabaseConnectionForm
    template_name = 'connectors/database_connections/form.html'
    
    def get_success_url(self):
        return reverse('connectors:database_connections')
    
    def get_queryset(self):
        return DatabaseConnection.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Database connection "{form.instance.name}" updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit {self.object.name}'
        context['form_action'] = 'Update'
        return context


class DatabaseConnectionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a database connection."""
    
    model = DatabaseConnection
    template_name = 'connectors/database_connections/confirm_delete.html'  # Using the current template structure
    success_url = reverse_lazy('connectors:database_connections')
    
    def get_queryset(self):
        return DatabaseConnection.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Database connection "{name}" deleted successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete {self.object.name}'
        return context


@login_required
@require_POST
def database_connection_test_view(request):
    """AJAX view to test a database connection."""
    
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        
        if not connection_id:
            return JsonResponse({
                'success': False,
                'message': 'Connection ID is required.'
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
                'message': 'Connection not found or you don\'t have permission to test it.'
            }, status=404)
        
        # Test the connection
        success, message = connection.test_connection()
        
        return JsonResponse({
            'success': success,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)
