"""
Session Management Views for Data Studio.
Handles session creation, operations, and cleanup.
"""
import os
import json
import pandas as pd
import logging
import sentry_sdk
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile

from projects.models import DataSource
from data_tools.services.session_service import (
    initialize_session, load_current_dataframe, save_current_dataframe,
    get_session_path, load_session_metadata, clear_session_files
)

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def handle_start_session(request, datasource):
    """
    Start a new editing session by creating a temporary copy of the dataset.
    
    Args:
        request: Django request object
        datasource: DataSource model instance
        
    Returns:
        JsonResponse: Success/error response
    """
    try:
        # Load original dataframe
        file_path = datasource.file.path
        
        if file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path, delimiter=',', encoding='latin-1')
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Unsupported file format'
            })

        # Initialize session
        success, session_path = initialize_session(datasource, request.user, df)
        
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to initialize session'
            })

        logger.info(f"Session started for user {request.user.id}, datasource {datasource.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Session started successfully',
            'session_path': session_path,
            'original_shape': df.shape
        })

    except Exception as e:
        logger.error(f"Error starting session: {e}")
        sentry_sdk.capture_exception(e)
        return JsonResponse({
            'success': False,
            'error': f'Failed to start session: {str(e)}'
        })


@csrf_exempt
@login_required
def handle_session_column_removal(request, datasource):
    """
    Handle column removal within an active session.
    
    Args:
        request: Django request object
        datasource: DataSource model instance
        
    Returns:
        JsonResponse: Success/error response
    """
    try:
        session_path = get_session_path(datasource, request.user)
        df = load_current_dataframe(session_path)
        
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            })

        # Parse removed columns
        removed_columns_json = request.POST.get('removed_columns', '[]')
        removed_columns = json.loads(removed_columns_json)

        if not removed_columns:
            return JsonResponse({
                'success': False,
                'error': 'No columns specified for removal'
            })

        # Remove specified columns
        original_columns = len(df.columns)
        df_modified = df.drop(columns=removed_columns, errors='ignore')
        removed_count = original_columns - len(df_modified.columns)

        # Save updated dataframe
        operation_name = f"remove_columns_{len(removed_columns)}"
        success = save_current_dataframe(df_modified, session_path, operation_name)

        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to save changes'
            })

        logger.info(f"Removed {removed_count} columns in session for user {request.user.id}")

        return JsonResponse({
            'success': True,
            'message': f'Successfully removed {removed_count} columns',
            'removed_columns': removed_columns,
            'new_shape': df_modified.shape
        })

    except Exception as e:
        logger.error(f"Error removing columns: {e}")
        sentry_sdk.capture_exception(e)
        return JsonResponse({
            'success': False,
            'error': f'Failed to remove columns: {str(e)}'
        })


@csrf_exempt
@login_required
def handle_end_session(request, datasource):
    """
    End the current session and optionally save as new DataSource.
    
    Args:
        request: Django request object
        datasource: DataSource model instance
        
    Returns:
        JsonResponse: Success/error response
    """
    try:
        session_path = get_session_path(datasource, request.user)
        df = load_current_dataframe(session_path)
        
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            })

        save_as_new = request.POST.get('save_as_new', 'false').lower() == 'true'
        new_datasource_id = None

        if save_as_new:
            # Create new DataSource with modified data
            new_name = request.POST.get('new_name', f"{datasource.name}_modified")
            new_description = request.POST.get('new_description', f"Modified version of {datasource.name}")

            # Save dataframe to new parquet file
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{new_name.replace(' ', '_')}.parquet"
            
            import io
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False)
            buffer.seek(0)

            new_datasource = DataSource.objects.create(
                name=new_name,
                description=new_description,
                project=datasource.project,
                owner=request.user,
                data_type=DataSource.DataSourceType.PREPARED,
                status=DataSource.Status.READY,
                file=ContentFile(buffer.getvalue(), name=unique_filename)
            )
            new_datasource_id = new_datasource.id

        # Clear session files
        clear_session_files(session_path)

        logger.info(f"Session ended for user {request.user.id}, saved_as_new: {save_as_new}")

        return JsonResponse({
            'success': True,
            'message': 'Session ended successfully',
            'saved_as_new': save_as_new,
            'new_datasource_id': new_datasource_id
        })

    except Exception as e:
        logger.error(f"Error ending session: {e}")
        sentry_sdk.capture_exception(e)
        return JsonResponse({
            'success': False,
            'error': f'Failed to end session: {str(e)}'
        })


@csrf_exempt
@login_required
def handle_undo_operation(request, datasource):
    """
    Undo the last operation in the current session.
    
    Args:
        request: Django request object
        datasource: DataSource model instance
        
    Returns:
        JsonResponse: Success/error response
    """
    try:
        session_path = get_session_path(datasource, request.user)
        metadata = load_session_metadata(session_path)

        if not metadata.get('backups'):
            return JsonResponse({
                'success': False,
                'error': 'No operations to undo'
            })

        # Get the previous backup
        last_backup = metadata['backups'][-1]
        backup_file = os.path.join(session_path, last_backup['file'])

        if not os.path.exists(backup_file):
            return JsonResponse({
                'success': False,
                'error': 'Backup file not found'
            })

        # Load previous state
        df_previous = pd.read_parquet(backup_file)

        # Save as current state (without creating new backup)
        success = save_current_dataframe(df_previous, session_path)

        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to restore previous state'
            })

        # Update metadata (remove last backup and operation)
        metadata['backups'].pop()
        if metadata.get('operations'):
            metadata['operations'].pop()
        metadata['current_step'] = len(metadata['operations'])

        import os
        metadata_file = os.path.join(session_path, "session_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        # Remove the backup file
        os.remove(backup_file)

        logger.info(f"Undo operation completed for user {request.user.id}")

        return JsonResponse({
            'success': True,
            'message': 'Operation undone successfully',
            'current_shape': df_previous.shape
        })

    except Exception as e:
        logger.error(f"Error in undo operation: {e}")
        sentry_sdk.capture_exception(e)
        return JsonResponse({
            'success': False,
            'error': f'Failed to undo operation: {str(e)}'
        })