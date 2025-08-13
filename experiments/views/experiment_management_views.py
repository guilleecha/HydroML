# experiments/views/experiment_management_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from projects.models import Project
# Importaciones relativas: usamos '..' para subir un nivel desde 'views' y encontrar 'models' y 'forms'
from ..models import MLExperiment
from ..forms import MLExperimentForm
from ..tasks import run_train_test_split_task, run_model_training_task, run_final_evaluation_task, run_feature_importance_task


@login_required
def ml_experiment_create(request, project_id):
    """
    Vista basada en función para crear un nuevo Experimento de Machine Learning.
    Se asocia a un proyecto existente.
    """
    # Se asegura de que el proyecto exista y pertenezca al usuario logueado
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == 'POST':
        # Al recibir datos, se instancia el formulario con el proyecto y los datos del request
        form = MLExperimentForm(project, request.POST)
        if form.is_valid():
            # Si el formulario es válido, se guarda el objeto pero sin enviarlo a la BD (commit=False)
            ml_experiment = form.save(commit=False)
            # Se asignan los campos que no venían en el formulario
            ml_experiment.project = project
            ml_experiment.status = 'DRAFT'  # Estado inicial por defecto
            # Ahora sí, se guarda el objeto completo en la base de datos
            ml_experiment.save()
            # Se redirige al usuario a la página de detalle del proyecto
            return redirect('projects:project_detail', pk=project.id)
    else:
        # Si es una petición GET (primera visita), se crea un formulario vacío
        # pasándole el proyecto para que el queryset de DataSources se filtre correctamente.
        form = MLExperimentForm(project)

    context = {
        'form': form,
        'project': project,
        'view_title': 'Crear Nuevo Experimento de ML' # Título para la plantilla
    }
    # Se renderiza la plantilla del formulario
    return render(request, 'experiments/ml_experiment_form.html', context)


class MLExperimentUpdateView(UpdateView):
    """
    Vista basada en clase para actualizar los datos de un experimento existente.
    Hereda de UpdateView para automatizar gran parte del proceso.
    """
    model = MLExperiment
    form_class = MLExperimentForm
    # Reutilizamos la misma plantilla que la vista de creación
    template_name = 'experiments/ml_experiment_form.html'

    def get_context_data(self, **kwargs):
        """Añade variables extra al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Editando Experimento: {self.object.name}"
        return context

    def get_form_kwargs(self):
        """
        Este método es fundamental: se asegura de pasar el 'project' al __init__ del formulario
        para que pueda filtrar los DataSources correctamente durante la edición.
        """
        kwargs = super().get_form_kwargs()
        # El 'project' se obtiene del experimento que se está editando (self.object)
        kwargs['project'] = self.object.project
        return kwargs

    def get_success_url(self):
        """Define a dónde redirigir al usuario después de una actualización exitosa."""
        # Al terminar la edición, volvemos a la página de detalle del experimento.
        return reverse('experiments:ml_experiment_detail', kwargs={'pk': self.object.pk})


class MLExperimentDeleteView(DeleteView):
    """
    Vista basada en clase para confirmar y eliminar un experimento de ML.
    """
    model = MLExperiment
    template_name = 'experiments/ml_experiment_confirm_delete.html'

    def get_success_url(self):
        """Define a dónde redirigir al usuario después de una eliminación exitosa."""
        # Al eliminar, volvemos a la página del proyecto al que pertenecía.
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})

@login_required
def trigger_split_task(request, experiment_id):
    """
    Dispara la tarea de Celery para la división de datos.
    """
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    
    run_train_test_split_task.delay(experiment.id)
    
    messages.success(request, "La tarea de división de datos ha sido iniciada. Los nuevos datasets aparecerán en la página del proyecto en unos momentos.")
    
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
def trigger_training_task(request, experiment_id):
    """
    Dispara la tarea de Celery para el entrenamiento del modelo.
    """
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    
    run_model_training_task.delay(experiment.id)
    
    messages.success(request, "La tarea de entrenamiento del modelo ha sido iniciada. Los resultados aparecerán en esta página en unos momentos.")
    
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
def trigger_final_evaluation_task(request, experiment_id):
    """
    Dispara la tarea de Celery para la evaluación final del modelo.
    """
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    
    run_final_evaluation_task.delay(experiment.id)
    
    messages.success(request, "La tarea de evaluación final ha sido iniciada. Los resultados finales aparecerán en esta página en unos momentos.")
    
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
def trigger_feature_importance_task(request, experiment_id):
    """
    Dispara la tarea de Celery para el análisis de importancia de variables.
    """
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    
    run_feature_importance_task.delay(experiment.id)
    
    messages.success(request, "El análisis de importancia de variables ha comenzado. El gráfico aparecerá en esta página en unos momentos.")
    
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)
