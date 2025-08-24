"""
Session Operations API Views - Undo/redo functionality for session history management.
Handles session state navigation with proper validation and error handling.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from data_tools.services.api_performance_service import monitor_performance
from .utils import (
    validate_session_and_datasource, format_success_response, 
    log_and_handle_exception
)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def undo_operation(request, datasource_id):
    """Undo the last operation in the Data Studio session."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        # Perform undo
        df = session_manager.undo_operation()
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'No operations to undo or undo failed'
            }, status=400)
        
        return JsonResponse(format_success_response(
            'Operation undone successfully', session_manager, df
        ))
        
    except Exception as e:
        return log_and_handle_exception("undo operation", e)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def redo_operation(request, datasource_id):
    """Redo the next operation in the Data Studio session."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        # Perform redo
        df = session_manager.redo_operation()
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'No operations to redo or redo failed'
            }, status=400)
        
        return JsonResponse(format_success_response(
            'Operation redone successfully', session_manager, df
        ))
        
    except Exception as e:
        return log_and_handle_exception("redo operation", e)