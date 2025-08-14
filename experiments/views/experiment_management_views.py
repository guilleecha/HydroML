# experiments/views/experiment_management_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

from projects.models import Project
from ..models import MLExperiment
from ..forms import MLExperimentForm
# Se importan las tareas de Celery
from ..tasks import (
    run_full_experiment_pipeline_task # Importar la nueva tarea orquestadora
)

@login_required
def ml_experiment_create(request, project_id):
    """
    Gestiona la creación de un nuevo Experimento de Machine Learning.
    """
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == 'POST':
        form = MLExperimentForm(project=project, data=request.POST)
        if form.is_valid():
            experiment = form.save(commit=False)
            experiment.project = project
            experiment.status = 'DRAFT'
            
            # Lógica para construir el diccionario de hiperparámetros
            hyperparams = {}
            model_name = form.cleaned_data.get('model_name')
            if model_name == 'RandomForestRegressor':
                if form.cleaned_data.get('rf_n_estimators'):
                    hyperparams['n_estimators'] = form.cleaned_data['rf_n_estimators']
                if form.cleaned_data.get('rf_max_depth'):
                    hyperparams['max_depth'] = form.cleaned_data['rf_max_depth']
            elif model_name == 'GradientBoostingRegressor':
                if form.cleaned_data.get('gb_n_estimators'):
                    hyperparams['n_estimators'] = form.cleaned_data['gb_n_estimators']
                if form.cleaned_data.get('gb_learning_rate'):
                    hyperparams['learning_rate'] = form.cleaned_data['gb_learning_rate']
            
            experiment.hyperparameters = hyperparams
            experiment.save()
            
            messages.success(request, f"Experimento '{experiment.name}' creado con éxito.")
            return redirect('projects:project_detail', pk=project.id)
        # Si el formulario NO es válido, la ejecución continúa y se renderiza
        # la plantilla de nuevo, esta vez con los errores del formulario.
    else:
        form = MLExperimentForm(project=project)

    context = {
        'form': form,
        'project': project,
        'view_title': 'Crear Nuevo Experimento de ML'
    }
    return render(request, 'experiments/ml_experiment_form.html', context)


class MLExperimentUpdateView(UpdateView):
    model = MLExperiment
    form_class = MLExperimentForm
    template_name = 'experiments/ml_experiment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Editando Experimento: {self.object.name}"
        context['project'] = self.object.project
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.object.project
        return kwargs

    def get_success_url(self):
        return reverse('experiments:ml_experiment_detail', kwargs={'pk': self.object.pk})


class MLExperimentDeleteView(DeleteView):
    model = MLExperiment
    template_name = 'experiments/ml_experiment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})

# --- VISTAS PARA DISPARAR TAREAS ---

@login_required
@require_POST
def trigger_full_experiment_task(request, experiment_id):
    """Dispara la tarea que ejecuta el pipeline completo del experimento."""
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    
    if experiment.status == MLExperiment.Status.DRAFT:
        run_full_experiment_pipeline_task.delay(experiment.id)
        messages.info(request, "El experimento completo ha sido iniciado. El estado se actualizará automáticamente.")
    else:
        messages.warning(request, "El experimento ya ha sido ejecutado.")
        
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)


@login_required
@require_POST
def trigger_feature_importance_task(request, experiment_id):
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)

    if experiment.status == MLExperiment.Status.FINISHED:
        run_feature_importance_task.delay(experiment.id)
        messages.info(request, "El análisis de importancia de variables ha comenzado.")
    else:
        messages.warning(request, "El análisis solo puede realizarse sobre un experimento finalizado.")

    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
@require_POST # Asegura que esta acción solo se pueda realizar con un método POST
def publish_experiment(request, pk):
    """
    Publica un experimento, haciéndolo inmutable y visible.
    """
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)

    # --- NUEVO: Validación de estado para mayor robustez ---
    if experiment.status not in [MLExperiment.Status.FINISHED, MLExperiment.Status.ANALYZED]:
        messages.error(request, "El experimento no se puede publicar porque no ha finalizado.")
        return redirect('experiments:ml_experiment_detail', pk=experiment.pk)
    # --- FIN DE LA VALIDACIÓN ---

    # Lógica de publicación
    experiment.is_public = True
    experiment.published_at = timezone.now()
    experiment.status = MLExperiment.Status.PUBLISHED
    experiment.save()

    messages.success(request, f"El experimento '{experiment.name}' ha sido publicado exitosamente.")
    
    return redirect('experiments:ml_experiment_detail', pk=experiment.pk)