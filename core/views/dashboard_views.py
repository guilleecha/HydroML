"""
Core dashboard and main application views.
"""
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count
from projects.models import DataSource, Project
from experiments.models import MLExperiment, ExperimentSuite
from connectors.models import DatabaseConnection


def home(request):
    """
    Renderiza la página de bienvenida para usuarios no autenticados.
    Si el usuario ya ha iniciado sesión, lo redirige a su dashboard.
    """
    if request.user.is_authenticated:
        # Si el usuario ya está logueado, lo mandamos a su dashboard.
        return redirect(reverse('core:dashboard'))

    # Si no, le mostramos la página de bienvenida.
    return render(request, 'core/home.html')


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard principal para usuarios autenticados.
    Proporciona una visión general de su workspace con estadísticas clave y actividad reciente.
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener todos los proyectos del usuario para las consultas
        user_projects = Project.objects.filter(owner=user).order_by('-created_at')
        
        # Calcular estadísticas globales
        total_workspaces = user_projects.count()
        total_datasources = DataSource.objects.filter(project__owner=user).count()
        total_experiments = MLExperiment.objects.filter(project__owner=user).count()
        total_models = MLExperiment.objects.filter(
            project__owner=user, 
            status='FINISHED'
        ).count()
        
        # Actividad reciente - últimos 5 experimentos
        recent_experiments = MLExperiment.objects.filter(
            project__owner=user
        ).select_related('project').order_by('-created_at')[:5]
        
        # Proyectos más activos (con más experimentos recientes)
        active_projects = user_projects.annotate(
            experiment_count=Count('experiments'),
            datasource_count=Count('datasources')
        ).order_by('-experiment_count', '-created_at')[:6]
        
        # Get featured public experiments (últimos 3)
        featured_public_experiments = MLExperiment.objects.filter(
            is_public=True
        ).select_related(
            'project', 
            'project__owner'
        ).order_by('-created_at')[:3]
        
        context.update({
            'total_workspaces': total_workspaces,
            'total_datasources': total_datasources,
            'total_experiments': total_experiments,
            'total_models': total_models,
            'recent_experiments': recent_experiments,
            'user_projects': active_projects,
            'featured_public_experiments': featured_public_experiments,
        })
        
        return context


class HelpPageView(TemplateView):
    """
    Renders the help/FAQ page with common questions and answers about HydroML.
    """
    template_name = 'core/help_page.html'


# Legacy function-based view for backward compatibility
@login_required
def dashboard_view(request):
    """
    Legacy function-based view - redirects to class-based view.
    Kept for backward compatibility.
    """
    view = DashboardView.as_view()
    return view(request)


def help_page(request):
    """
    Legacy function-based view - redirects to class-based view.
    Kept for backward compatibility.
    """
    view = HelpPageView.as_view()
    return view(request)


class DataSourcesListView(LoginRequiredMixin, TemplateView):
    """
    Unified view for all user's data sources: uploaded files + database connections.
    This replaces the need for separate views and provides a GitHub-style unified listing.
    """
    template_name = 'core/data_sources_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get uploaded data sources (files)
        uploaded_datasources = DataSource.objects.filter(
            owner=user
        ).select_related('project').order_by('-uploaded_at')
        
        # Get database connections
        database_connections = DatabaseConnection.objects.filter(
            user=user
        ).order_by('-created_at')
        
        # Combine both types for unified display
        context.update({
            'uploaded_datasources': uploaded_datasources,
            'database_connections': database_connections,
            'total_uploaded': uploaded_datasources.count(),
            'total_connections': database_connections.count(),
        })
        
        return context


class ThemeTestView(TemplateView):
    """
    Theme testing and demonstration page for the HydroML design token system.
    Shows all available themes and design token variations.
    """
    template_name = 'core/theme_test.html'


class ComponentDemoView(TemplateView):
    """
    Component system demonstration page showing the HydroML component architecture.
    Demonstrates BaseComponent, FormComponent, DataComponent, and ComponentRegistry.
    """
    template_name = 'core/component_demo.html'


class LayoutDemoView(TemplateView):
    """
    Layout system demonstration page showing the HydroML layout patterns.
    Demonstrates dashboard, list, form, and detail layout templates.
    """
    template_name = 'core/layout_demo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sample data for layout demos
        context.update({
            'page_title': 'Layout System Demo',
            'total_projects': 12,
            'active_experiments': 8,
            'data_sources': 15,
            'model_accuracy': '94.2%',
            'items_start': 1,
            'items_end': 10,
            'total_items': 97,
        })
        
        return context


class ThemeDemoView(TemplateView):
    """
    Demonstration of the HydroML Runtime Theme Configuration System
    """
    template_name = 'core/theme_demo.html'


class GroveDemoView(TemplateView):
    """
    Demonstration of the Grove Component Library
    """
    template_name = 'core/grove_demo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add Wave component demonstration data
        context.update({
            'page_title': 'Wave Components Demo',
            'component_categories': [
                {
                    'name': 'Form Components',
                    'components': ['WaveInput', 'WaveButton', 'WaveSelect', 'WaveCheckbox', 'WaveRadio', 'WaveTextarea', 'WaveToggle']
                },
                {
                    'name': 'Data Display',
                    'components': ['WaveTable', 'WaveCard', 'WaveList', 'WaveStats', 'WaveBadge', 'WaveProgress']
                },
                {
                    'name': 'Navigation',
                    'components': ['WaveTabs', 'WaveBreadcrumbs', 'WavePagination', 'WaveMenu', 'WaveSidebar']
                },
                {
                    'name': 'Feedback',
                    'components': ['WaveModal', 'WaveToast', 'WaveAlert', 'WaveLoader', 'WaveSpinner']
                },
                {
                    'name': 'Interactive',
                    'components': ['WaveDropdown', 'WaveTooltip', 'WaveAccordion', 'WaveDrawer']
                }
            ],
            'design_principles': [
                'Monochromatic color palette (whites, blacks, grays)',
                'Pastel accent colors for tags and classifications',
                'Professional enterprise appearance',
                'Accessibility-first design approach',
                'Smooth animations and transitions',
                'Theme system integration'
            ]
        })
        
        return context
