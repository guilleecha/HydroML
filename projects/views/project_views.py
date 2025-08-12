# projects/views/project_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Project
from ..forms import ProjectForm


@login_required
def project_list(request):
    """
    Muestra una lista de todos los proyectos que pertenecen al usuario logueado.
    """
    # La consulta correcta: filtra el campo 'owner' con el objeto 'request.user'
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
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
    context = {
        'project': project,
        'datasources': datasources,
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