"""
Preparation Controller - Bridge between old and new views.
This file manages the transition from monolithic to modular views.
"""
import json
import logging
import sentry_sdk
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from projects.models import DataSource
from .data_studio_views import data_studio_page
from .session_views import (
    handle_start_session, handle_session_column_removal,
    handle_end_session, handle_undo_operation
)
from .api.pagination_api import data_studio_pagination_api

logger = logging.getLogger(__name__)


@login_required
def data_preparer_page(request, pk):
    """
    Main controller for Data Studio (legacy name: data_preparer_page).
    Routes GET requests to the new modular view and POST requests to session handlers.
    """
    datasource = get_object_or_404(DataSource, pk=pk, project__owner=request.user)
    
    if request.method == 'GET':
        # Route to new modular Data Studio view
        return data_studio_page(request, pk)
    
    elif request.method == 'POST':
        # Route POST requests to appropriate session handlers
        try:
            # Check if this is an AJAX request for session management
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                action = request.POST.get('action')
                
                if action == 'start_session':
                    return handle_start_session(request, datasource)
                elif action == 'end_session':
                    return handle_end_session(request, datasource)
                elif action == 'undo_operation':
                    return handle_undo_operation(request, datasource)
                elif action == 'apply_transformation':
                    return handle_feature_engineering_transformation(request, datasource)
                elif 'removed_columns' in request.POST:
                    return handle_session_column_removal(request, datasource)
            
            # Handle other POST operations (legacy)
            return handle_legacy_post_operations(request, datasource)
            
        except Exception as e:
            logger.error(f"Error in data_preparer_page POST: {e}")
            sentry_sdk.capture_exception(e)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


def handle_legacy_post_operations(request, datasource):
    """
    Handle legacy POST operations that haven't been migrated yet.
    This function can be expanded as needed during the migration process.
    """
    # For now, return a message indicating the operation needs to be implemented
    return JsonResponse({
        'success': False,
        'error': 'This operation is being migrated to the new modular system. Please use the Data Studio interface.'
    })


def handle_feature_engineering_transformation(request, datasource):
    """
    Placeholder for feature engineering transformation.
    This should be moved to a dedicated feature engineering module.
    """
    return JsonResponse({
        'success': False,
        'error': 'Feature engineering transformations are being migrated to a dedicated module.'
    })