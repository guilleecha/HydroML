# experiments/views/api_views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import MLExperiment

@login_required
def get_experiment_status(request, experiment_id):
    """
    API endpoint que devuelve el estado y los resultados de un experimento.
    """
    try:
        experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
        
        response_data = {
            'status': experiment.status,
            'status_display': experiment.get_status_display(),
            'results': experiment.results or {}
        }
        
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
