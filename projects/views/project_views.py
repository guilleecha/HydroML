# projects/views/project_views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Project


@login_required
def project_list(request):
    """
    Muestra una lista de todos los proyectos que pertenecen al usuario logueado.
    """
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'projects': projects,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, pk):
    """
    Muestra la página de detalle de un proyecto específico, incluyendo
    todas sus fuentes de datos (DataSources) asociadas.
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    # Obtenemos todos los datasources asociados a este proyecto para listarlos.
    # El related_name 'datasources' que definimos en el modelo es muy útil aquí.
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
            project.user = request.user  # Asigna el usuario actual como dueño
            project.save()
            return redirect('projects:project_detail', pk=project.id)
    else:
        form = ProjectForm()

    context = {
        'form': form
    }
    return render(request, 'projects/project_form.html', context)