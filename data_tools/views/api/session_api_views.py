"""
Data Studio Session API Views for stateful data transformations.
"""

import json
import logging
from typing import Dict, Any
import numpy as np

import pandas as pd
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from projects.models import DataSource
from data_tools.services.session_manager import get_session_manager
from data_tools.services.data_loader import load_data_from_parquet
from data_tools.services.api_performance_service import rate_limit, cache_response, monitor_performance
from data_tools.websockets.data_studio_consumer import sync_send_session_update

logger = logging.getLogger(__name__)



@csrf_exempt
@login_required
@require_http_methods(["POST"])
@rate_limit(limit=10, window_seconds=3600)  # 10 per hour
@monitor_performance
def initialize_session(request, datasource_id):
    """
    Initialize a new Data Studio session with the original DataFrame.
    """
    try:
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        session_manager = get_session_manager(request.user.id, datasource_id)
        
        # Check if session already exists and has data loaded
        session_info = session_manager.get_session_info()
        if session_info['session_exists']:
            # Verify that the session actually has data loaded
            current_df = session_manager.get_current_dataframe()
            if current_df is not None:
                # Session exists and has data, return existing session
                data_preview = current_df.head(100).fillna('').to_dict('records')
                column_info = [
                    {
                        'field': col,
                        'headerName': col,
                        'filter': True,
                        'sortable': True,
                        'resizable': True
                    }
                    for col in current_df.columns
                ]
                return JsonResponse({
                    'success': True,
                    'message': 'Session already exists',
                    'session_info': session_info,
                    'data_preview': data_preview,
                    'column_info': column_info
                })
            else:
                # Session metadata exists but no data, clear and reinitialize
                logger.warning(f"Session metadata exists but no data found for user {request.user.id}, datasource {datasource_id}. Clearing and reinitializing.")
                session_manager.clear_session()
        
        # Load the original DataFrame
        df = load_data_from_parquet(datasource.file.path)
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to load data from source file'
            }, status=400)
        
        # Initialize the session
        success = session_manager.initialize_session(df)
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to initialize session'
            }, status=500)
        
        # Get session info and data preview
        session_info = session_manager.get_session_info()
        data_preview = df.head(100).fillna('').to_dict('records')
        column_info = [
            {
                'field': col,
                'headerName': col,
                'filter': True,
                'sortable': True,
                'resizable': True
            }
            for col in df.columns
        ]
        
        return JsonResponse({
            'success': True,
            'message': 'Session initialized successfully',
            'session_info': session_info,
            'data_preview': data_preview,
            'column_info': column_info
        })
        
    except Exception as e:
        logger.error(f"Failed to initialize session: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_session_status(request, datasource_id):
    """
    Get the current status of the Data Studio session.
    """
    try:
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        session_manager = get_session_manager(request.user.id, datasource_id)
        
        session_info = session_manager.get_session_info()
        
        # If session exists, also return current data preview
        current_preview = None
        column_info = None
        
        if session_info['session_exists']:
            current_df = session_manager.get_current_dataframe()
            if current_df is not None:
                current_preview = current_df.head(100).fillna('').to_dict('records')
                column_info = [
                    {
                        'field': col,
                        'headerName': col,
                        'filter': True,
                        'sortable': True,
                        'resizable': True
                    }
                    for col in current_df.columns
                ]
        
        return JsonResponse({
            'success': True,
            'session_info': session_info,
            'data_preview': current_preview,
            'column_info': column_info
        })
        
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def undo_operation(request, datasource_id):
    """
    Undo the last operation in the Data Studio session.
    """
    try:
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        session_manager = get_session_manager(request.user.id, datasource_id)
        
        # Perform undo
        df = session_manager.undo_last_operation()
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'No operations to undo or undo failed'
            }, status=400)
        
        # Return updated session info and data preview
        session_info = session_manager.get_session_info()
        data_preview = df.head(100).fillna('').to_dict('records')
        column_info = [
            {
                'field': col,
                'headerName': col,
                'filter': True,
                'sortable': True,
                'resizable': True
            }
            for col in df.columns
        ]
        
        return JsonResponse({
            'success': True,
            'message': 'Operation undone successfully',
            'session_info': session_info,
            'data_preview': data_preview,
            'column_info': column_info
        })
        
    except Exception as e:
        logger.error(f"Failed to undo operation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def redo_operation(request, datasource_id):
    """
    Redo the next operation in the Data Studio session.
    """
    try:
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        session_manager = get_session_manager(request.user.id, datasource_id)
        
        # Perform redo
        df = session_manager.redo_last_operation()
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'No operations to redo or redo failed'
            }, status=400)
        
        # Return updated session info and data preview
        session_info = session_manager.get_session_info()
        data_preview = df.head(100).fillna('').to_dict('records')
        column_info = [
            {
                'field': col,
                'headerName': col,
                'filter': True,
                'sortable': True,
                'resizable': True
            }
            for col in df.columns
        ]
        
        return JsonResponse({
            'success': True,
            'message': 'Operation redone successfully',
            'session_info': session_info,
            'data_preview': data_preview,
            'column_info': column_info
        })
        
    except Exception as e:
        logger.error(f"Failed to redo operation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def clear_session(request, datasource_id):
    """
    Clear the current Data Studio session.
    """
    try:
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        session_manager = get_session_manager(request.user.id, datasource_id)
        
        success = session_manager.clear_session()
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to clear session'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': 'Session cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to clear session: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def save_as_new_datasource(request, datasource_id):
    """
    Save the current session state as a new DataSource.
    """
    try:
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        session_manager = get_session_manager(request.user.id, datasource_id)
        
        # Get the request data
        data = json.loads(request.body)
        new_name = data.get('name', f"{datasource.name}_transformed")
        description = data.get('description', f"Transformed version of {datasource.name}")
        
        # Get current DataFrame from session
        current_df = session_manager.get_current_dataframe()
        if current_df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            }, status=400)
        
        # Save DataFrame to new parquet file
        import os
        import uuid
        from django.core.files.base import ContentFile
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}_{new_name.replace(' ', '_')}.parquet"
        
        # Convert DataFrame to parquet bytes
        import io
        buffer = io.BytesIO()
        current_df.to_parquet(buffer, index=False)
        buffer.seek(0)
        
        # Create new DataSource
        new_datasource = DataSource.objects.create(
            name=new_name,
            description=description,
            project=datasource.project,
            source_type='file',
            file_format='parquet',
            file=ContentFile(buffer.getvalue(), name=unique_filename)
        )
        
        # Clear the session after successful save
        session_manager.clear_session()
        
        return JsonResponse({
            'success': True,
            'message': 'Data saved successfully as new datasource',
            'new_datasource': {
                'id': new_datasource.id,
                'name': new_datasource.name,
                'description': new_datasource.description,
                'created_at': new_datasource.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to save as new datasource: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
