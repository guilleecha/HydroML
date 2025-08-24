"""
Session API Utilities - Shared helper functions for session operations.
Implements DRY principle for common validation, response formatting, and session management.
"""

import json
import logging
from typing import Dict, Any, Optional
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from projects.models import DataSource
from data_tools.services.session_manager import get_session_manager

logger = logging.getLogger(__name__)


def validate_session_and_datasource(user: User, datasource_id: str) -> tuple:
    """
    Validate datasource ownership and get session manager.
    Returns: (datasource, session_manager) or raises appropriate exceptions.
    """
    datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=user)
    session_manager = get_session_manager(user.id, datasource_id)
    return datasource, session_manager


def validate_active_session(session_manager) -> Optional[pd.DataFrame]:
    """
    Validate that session has active data.
    Returns DataFrame if valid, None if invalid.
    """
    current_df = session_manager.get_current_dataframe()
    if current_df is None:
        return None
    return current_df


def get_data_preview(df: pd.DataFrame, num_rows: int = 100) -> list:
    """
    Generate standardized data preview for API responses.
    """
    return df.head(num_rows).fillna('').to_dict('records')


def get_column_info(df: pd.DataFrame) -> list:
    """
    Get standardized column information for API responses.
    """
    return list(df.columns)


def format_success_response(message: str, session_manager=None, df: pd.DataFrame = None, 
                          extra_data: Dict = None) -> Dict[str, Any]:
    """
    Format standardized success response with session info and data preview.
    """
    response = {
        'success': True,
        'message': message
    }
    
    if session_manager:
        response['session_info'] = session_manager.get_session_info()
    
    if df is not None:
        response['data_preview'] = get_data_preview(df)
        response['column_info'] = get_column_info(df)
    
    if extra_data:
        response.update(extra_data)
        
    return response


def format_error_response(error_message: str, status_code: int = 400) -> JsonResponse:
    """
    Format standardized error response.
    """
    return JsonResponse({
        'success': False,
        'error': str(error_message)
    }, status=status_code)


def log_and_handle_exception(operation: str, error: Exception, status_code: int = 500) -> JsonResponse:
    """
    Log exception and return standardized error response.
    """
    logger.error(f"Failed to {operation}: {error}")
    return format_error_response(str(error), status_code)


def parse_json_body(request) -> Dict[str, Any]:
    """
    Safely parse JSON request body.
    """
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return {}


def validate_required_fields(data: Dict, required_fields: list) -> Optional[str]:
    """
    Validate that all required fields are present in request data.
    Returns error message if validation fails, None if valid.
    """
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    return None


def validate_columns_exist(df: pd.DataFrame, columns: list) -> Optional[str]:
    """
    Validate that specified columns exist in DataFrame.
    Returns error message if validation fails, None if valid.
    """
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        return f"Columns not found: {missing_columns}"
    return None