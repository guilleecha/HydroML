# projects/views/project_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from core.utils.breadcrumbs import create_basic_breadcrumbs
from ..models import Project
from ..forms import ProjectForm


@login_required
def project_list(request):
    """
    Muestra una lista de todos los proyectos que pertenecen al usuario logueado.
    """
    # La consulta correcta: filtra el campo 'owner' con el objeto 'request.user'
    projects = Project.objects.filter(owner=request.user).order_by('-created_at').select_related().prefetch_related('datasources', 'experiments')
    context = {
        'projects': projects,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, pk):
    """
    Muestra la página de detalle de un proyecto específico.
    """
    # La consulta correcta
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    datasources = project.datasources.all().order_by('-uploaded_at')
    experiments = project.experiments.all().order_by('-created_at')
    experiment_suites = project.experiment_suites.all().order_by('-created_at')
    
    # Create breadcrumbs for navigation
    breadcrumbs = create_basic_breadcrumbs(
        ('Workspace', reverse('projects:project_list')),
        project.name
    )
    
    context = {
        'project': project,
        'datasources': datasources,
        'experiments': experiments,
        'experiment_suites': experiment_suites,
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'projects/project_detail.html', context)


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