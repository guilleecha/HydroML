from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from projects.models import Project
from ..models import ExperimentSuite
from ..forms import AblationSuiteForm

@login_required
def ablation_suite_create(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        form = AblationSuiteForm(project=project, data=request.POST)
        if form.is_valid():
            suite = form.save(commit=False)
            suite.project = project
            suite.suite_type = ExperimentSuite.SuiteType.ABLATION_STUDY
            suite.status = ExperimentSuite.Status.DRAFT
            suite.save()
            
            # La lógica para crear los experimentos se manejará con una tarea de Celery
            # que llamaremos desde la página de detalle de la suite.
            
            # Redirigir a la página del proyecto por ahora
            return redirect(reverse('projects:project_detail', kwargs={'pk': project.id}))
    else:
        form = AblationSuiteForm(project=project)
        
    context = {
        'form': form,
        'project': project,
        'view_title': 'Crear Nueva Suite de Análisis de Ablación'
    }
    return render(request, 'experiments/ablation_suite_form.html', context)