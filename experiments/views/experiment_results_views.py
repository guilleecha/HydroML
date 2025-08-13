# experiments/views/experiment_results_views.py
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

# Importamos el modelo usando '..' para subir un nivel y encontrar la carpeta 'models'
from ..models import MLExperiment


@login_required
def ml_experiment_detail(request, pk):
    """
    Muestra los detalles y la configuración de un experimento de ML.
    Este es el "Dashboard" del experimento.
    """
    # Se asegura de que el experimento exista y pertenezca al usuario logueado
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)

    scatter_data_json = None
    if experiment.results and 'prediction_data' in experiment.results:
        scatter_data_json = json.dumps(experiment.results['prediction_data'])

    context = {
        'experiment': experiment,
        'scatter_data_json': scatter_data_json,
    }

    return render(request, 'experiments/ml_experiment_detail.html', context)
