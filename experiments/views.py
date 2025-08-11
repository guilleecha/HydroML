# experiments/views.py

import json
import io # <-- Import para la tarea de Celery
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.core.files.base import ContentFile # <-- Y este
from django.views.decorators.csrf import csrf_exempt # Para nuestra API simple
from django.http import JsonResponse # <-- Importante

import pandas as pd

from .forms import ExperimentForm, ExperimentUpdateForm, MLExperimentForm
from .models import Experiment, FusedData
from projects.models import Project
from .tasks import process_data_fusion_task


def create_experiment(request, project_id):
    """
    Gestiona la creación de un nuevo experimento.
    """
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ExperimentForm(project.datasources.all(), request.POST)
        if form.is_valid():
            experiment = form.save(commit=False)
            experiment.project = project
            experiment.status = Experiment.StatusChoices.PENDING

            merge_column = request.POST.get('merge_column')
            experiment.merge_key = merge_column

            experiment.save()
            form.save_m2m()
            process_data_fusion_task.delay(experiment.id)
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ExperimentForm(datasources_queryset=project.datasources.all())

    # --- RUTA DE PLANTILLA CORREGIDA ---
    return render(request, 'experiments/create_experiment.html', {
        'form': form,
        'project': project
    })


def experiment_detail(request, pk):
    """
    Muestra los detalles y resultados de un único experimento.
    """
    experiment = get_object_or_404(Experiment.objects.select_related('fused_data'), pk=pk)

    chart_labels = []
    chart_data = []

    if experiment.status == 'COMPLETE' and hasattr(experiment, 'fused_data') and experiment.fused_data.summary:
        summary = experiment.fused_data.summary
        if 'mean' in summary:
            chart_labels = list(summary['mean'].keys())
            chart_data = list(summary['mean'].values())

    # --- RUTA DE PLANTILLA CORREGIDA ---
    return render(request, 'experiments/experiment_detail.html', {
        'experiment': experiment,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    })

class ExperimentUpdateView(UpdateView):
    model = Experiment
    form_class = ExperimentUpdateForm
    # --- RUTA DE PLANTILLA CORREGIDA ---
    template_name = 'experiments/update_experiment.html'

    def get_success_url(self):
        project_id = self.object.project.id
        return reverse_lazy('projects:project_detail', kwargs={'project_id': project_id})


class ExperimentDeleteView(DeleteView):
    model = Experiment
    # --- RUTA DE PLANTILLA CORREGIDA ---
    template_name = 'experiments/experiment_confirm_delete.html'

    def get_success_url(self):
        project_id = self.object.project.id
        return reverse_lazy('projects:project_detail', kwargs={'project_id': project_id})


def get_common_columns(request):
    if request.method == 'POST':
        try:
            # Obtenemos la lista de IDs de los archivos seleccionados
            datasource_ids = json.loads(request.body).get('datasource_ids', [])
            if not datasource_ids:
                return JsonResponse({'columns': []})

            # Obtenemos los objetos DataSource
            from projects.models import DataSource
            datasources = DataSource.objects.filter(pk__in=datasource_ids)

            if not datasources:
                return JsonResponse({'columns': []})

            # Usamos pandas para leer solo las cabeceras de cada archivo
            column_sets = []
            for ds in datasources:
                # nrows=0 es un truco para leer solo la cabecera, es muy rápido
                df_header = pd.read_csv(ds.file.path, nrows=0)
                column_sets.append(set(df_header.columns))

            # Encontramos la intersección de todas las columnas
            common_columns = set.intersection(*column_sets)

            return JsonResponse({'columns': sorted(list(common_columns))})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def create_ml_experiment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    form = MLExperimentForm(request.POST or None)

    # Filtramos el queryset para mostrar solo datasets de este proyecto
    form.fields['source_dataset'].queryset = project.datasources.all()

    if request.method == 'POST' and form.is_valid():
        ml_experiment = form.save(commit=False)
        ml_experiment.project = project

        # Convertimos el string de features a una lista
        features_str = form.cleaned_data['feature_set']
        ml_experiment.feature_set = [feature.strip() for feature in features_str.split(',')]

        ml_experiment.save()
        # Por ahora, solo guardamos la configuración.
        # En el futuro, aquí podríamos lanzar la tarea de train/test split.
        return redirect('projects:project_detail', project_id=project.id)

    return render(request, 'experiments/create_ml_experiment.html', {
        'form': form,
        'project': project
    })