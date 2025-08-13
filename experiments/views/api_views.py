# experiments/views/api_views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import MLExperiment

@login_required
def get_experiment_status(request, experiment_id):
    """
    API endpoint para obtener el estado actual de un experimento.
    """
    # La consulta correcta debe ser 'project__owner' para atravesar la relación
    # desde MLExperiment -> Project -> User (owner).
    experiment = get_object_or_404(
        MLExperiment, 
        id=experiment_id, 
        project__owner=request.user
    )
    
    return JsonResponse({
        'status': experiment.status,
        'status_display': experiment.get_status_display(),
        'results': experiment.results
    })
