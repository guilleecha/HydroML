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
