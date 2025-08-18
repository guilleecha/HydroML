# projects/views/project_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from core.utils.breadcrumbs import create_basic_breadcrumbs
from ..models import Project
from ..forms import ProjectForm


class ProjectListView(LoginRequiredMixin, ListView):
    """
    Muestra una lista de todos los proyectos que pertenecen al usuario logueado.
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        return Project.objects.filter(
            owner=self.request.user
        ).order_by('-created_at').select_related().prefetch_related('datasources', 'experiments')


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra la página de detalle de un proyecto específico.
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Get related data
        datasources = project.datasources.all().order_by('-uploaded_at')
        experiments = project.experiments.all().order_by('-created_at')
        experiment_suites = project.experiment_suites.all().order_by('-created_at')
        
        # Create unified ML activities list combining experiments and suites
        ml_activities = []
        
        # Add experiments to the activities list
        for experiment in experiments:
            ml_activities.append({
                'type': 'experiment',
                'type_display': 'Experimento',
                'object': experiment,
                'name': experiment.name,
                'status': experiment.status,
                'status_display': experiment.get_status_display(),
                'created_at': experiment.created_at,
                'updated_at': experiment.updated_at,
                'url': reverse('experiments:ml_experiment_detail', kwargs={'pk': experiment.pk}),
                'icon': 'experiment',  # For template icon rendering
                'description': getattr(experiment, 'description', '') or 'Sin descripción',
            })
        
        # Add experiment suites to the activities list
        for suite in experiment_suites:
            ml_activities.append({
                'type': 'suite',
                'type_display': 'Suite',
                'object': suite,
                'name': suite.name,
                'status': suite.status,
                'status_display': suite.get_status_display(),
                'created_at': suite.created_at,
                'updated_at': suite.updated_at,
                'url': reverse('experiments:suite_detail', kwargs={'pk': suite.pk}),
                'icon': 'suite',  # For template icon rendering
                'description': getattr(suite, 'description', '') or 'Sin descripción',
                'experiment_count': suite.get_experiment_count() if hasattr(suite, 'get_experiment_count') else 0,
                'study_type_display': suite.get_study_type_display() if hasattr(suite, 'get_study_type_display') else '',
            })
        
        # Sort the unified list by created_at (most recent first)
        ml_activities.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Add to context
        context['datasources'] = datasources
        context['experiments'] = experiments  # Keep for backward compatibility
        context['experiment_suites'] = experiment_suites  # Keep for backward compatibility
        context['ml_activities'] = ml_activities  # New unified list
        
        # Create breadcrumbs for navigation
        context['breadcrumbs'] = create_basic_breadcrumbs(
            ('Workspace', reverse('projects:project_list')),
            project.name
        )
        
        return context


# Legacy function-based views for backward compatibility and AJAX endpoints
@login_required
def project_list(request):
    """
    Legacy function-based view - redirects to class-based view.
    """
    return ProjectListView.as_view()(request)


@login_required
def project_detail(request, pk):
    """
    Legacy function-based view - redirects to class-based view.
    """
    return ProjectDetailView.as_view()(request, pk=pk)


@login_required
def project_create(request):
    """
    Gestiona la creación de un nuevo proyecto.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            # La asignación correcta
            project.owner = request.user
            project.save()
            return redirect('projects:project_detail', pk=project.id)
    else:
        form = ProjectForm()

    context = {
        'form': form
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_create_partial(request):
    """
    Returns the project creation form as a partial template for AJAX loading.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            
            # Return JSON response for AJAX
            return JsonResponse({
                'success': True,
                'message': 'Proyecto creado exitosamente',
                'redirect_url': f'/projects/{project.id}/'
            })
        else:
            # Return form with errors
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    else:
        form = ProjectForm()

    context = {
        'form': form,
    }
    return render(request, 'projects/project_form_partial.html', context)


@login_required
def project_toggle_favorite(request, pk):
    """
    Toggle favorite status of a project via AJAX.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    project.is_favorite = not project.is_favorite
    project.save()
    
    return JsonResponse({
        'success': True,
        'is_favorite': project.is_favorite
    })


@login_required
def project_delete(request, pk):
    """
    Delete a project via AJAX.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    project.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Proyecto eliminado exitosamente'
    })