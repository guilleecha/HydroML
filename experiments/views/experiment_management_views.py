# experiments/views/experiment_management_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from projects.models import Project, FeatureSet
from ..models import MLExperiment
from ..forms import MLExperimentForm
# Se importan las tareas de Celery
from ..tasks import (
    run_train_test_split_task, 
    run_model_training_task, 
    run_final_evaluation_task, 
    run_feature_importance_task
)

@login_required
def ml_experiment_create(request, project_id):
    """
    Gestiona la creación de un nuevo Experimento de Machine Learning.
    """
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == 'POST':
        # Se le pasa el proyecto y los datos del POST al formulario
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
            
            # Se asigna el diccionario directamente (el modelo usa JSONField)
            experiment.hyperparameters = hyperparams
            experiment.save()
            
            messages.success(request, f"Experimento '{experiment.name}' creado con éxito.")
            return redirect('projects:project_detail', pk=project.id)
    else:
        # En peticiones GET, se le pasa el proyecto para filtrar los DataSources
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
        # Es necesario pasar el objeto project para el enlace "Cancelar"
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
def trigger_split_task(request, experiment_id):
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    run_train_test_split_task.delay(experiment.id)
    messages.info(request, "La tarea de división de datos ha sido iniciada.")
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
def trigger_training_task(request, experiment_id):
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    run_model_training_task.delay(experiment.id)
    messages.info(request, "La tarea de entrenamiento del modelo ha sido iniciada.")
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
def trigger_final_evaluation_task(request, experiment_id):
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    run_final_evaluation_task.delay(experiment.id)
    messages.info(request, "La tarea de evaluación final ha sido iniciada.")
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
def trigger_feature_importance_task(request, experiment_id):
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    run_feature_importance_task.delay(experiment.id)
    messages.info(request, "El análisis de importancia de variables ha comenzado.")
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)