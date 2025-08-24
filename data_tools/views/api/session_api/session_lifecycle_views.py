"""
Session Lifecycle API Views - Session creation, status, and cleanup operations.
Handles session CRUD operations with proper validation and error handling.
"""

import uuid
import io
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile

from data_tools.services.data_loader import load_data_from_parquet
from data_tools.services.api_performance_service import rate_limit, monitor_performance
from .utils import (
    validate_session_and_datasource, validate_active_session, 
    format_success_response, log_and_handle_exception, parse_json_body
)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
@rate_limit(limit=10, window_seconds=3600)
@monitor_performance
def initialize_session(request, datasource_id):
    """Initialize a new Data Studio session with the original DataFrame."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        # Check if session already exists with data
        session_info = session_manager.get_session_info()
        if session_info['session_exists']:
            current_df = session_manager.get_current_dataframe()
            if current_df is not None:
                return JsonResponse(format_success_response(
                    'Session already exists', session_manager, current_df
                ))
            else:
                # Session exists but no data, reinitialize
                session_manager.clear_session()
        
        # Load and initialize session
        df = load_data_from_parquet(datasource.file.path)
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to load data from source file'
            }, status=400)
        
        success = session_manager.initialize_session(df)
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to initialize session'
            }, status=500)
        
        return JsonResponse(format_success_response(
            'Session initialized successfully', session_manager, df
        ))
        
    except Exception as e:
        return log_and_handle_exception("initialize session", e)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_session_status(request, datasource_id):
    """Get the current status of the Data Studio session."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        session_info = session_manager.get_session_info()
        response_data = {
            'success': True,
            'session_info': session_info,
            'data_preview': None,
            'column_info': None
        }
        
        if session_info['session_exists']:
            current_df = session_manager.get_current_dataframe()
            if current_df is not None:
                response_data['data_preview'] = current_df.head(100).fillna('').to_dict('records')
                response_data['column_info'] = list(current_df.columns)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return log_and_handle_exception("get session status", e)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def clear_session(request, datasource_id):
    """Clear the current Data Studio session."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
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
        return log_and_handle_exception("clear session", e)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def save_as_new_datasource(request, datasource_id):
    """Save the current session state as a new DataSource."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        current_df = validate_active_session(session_manager)
        if current_df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            }, status=400)
        
        # Parse request data
        data = parse_json_body(request)
        new_name = data.get('name', f"{datasource.name}_transformed")
        description = data.get('description', f"Transformed version of {datasource.name}")
        
        # Create new DataSource
        new_datasource = _create_datasource_from_dataframe(
            current_df, new_name, description, datasource.project
        )
        
        # Clear session after successful save
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
        return log_and_handle_exception("save as new datasource", e)


def _create_datasource_from_dataframe(df, name, description, project):
    """Helper function to create DataSource from DataFrame."""
    from projects.models import DataSource
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}_{name.replace(' ', '_')}.parquet"
    
    # Convert DataFrame to parquet bytes
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    
    # Create new DataSource
    return DataSource.objects.create(
        name=name,
        description=description,
        project=project,
        source_type='file',
        file_format='parquet',
        file=ContentFile(buffer.getvalue(), name=unique_filename)
    )