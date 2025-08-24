"""
Pagination API for Data Studio.
Handles server-side pagination for large datasets.
"""
import pandas as pd
import logging
import sentry_sdk
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from projects.models import DataSource
from data_tools.services.session_service import (
    session_exists, load_current_dataframe, get_session_path
)

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@login_required
def data_studio_pagination_api(request, pk):
    """
    API endpoint for paginated data loading in Data Studio.
    Returns paginated data for AG Grid with server-side pagination.
    
    Args:
        request: Django request object
        pk: DataSource primary key
        
    Returns:
        JsonResponse: Paginated data response
    """
    try:
        datasource = get_object_or_404(DataSource, pk=pk, project__owner=request.user)

        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 25))
        sort_field = request.GET.get('sortField', '')
        sort_order = request.GET.get('sortOrder', 'asc')

        # Load dataframe (prioritize session data)
        df = load_dataframe_for_pagination(datasource, request.user)
        
        if df is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to load data'
            }, status=500)

        # Apply sorting if specified
        if sort_field and sort_field in df.columns:
            ascending = sort_order.lower() == 'asc'
            df = df.sort_values(by=sort_field, ascending=ascending)

        # Calculate pagination
        total_rows = len(df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Extract page data
        page_df = df.iloc[start_idx:end_idx]
        
        # Convert to records format for AG Grid
        data = page_df.to_dict('records')
        
        # Generate column definitions
        column_defs = generate_column_definitions(df)

        response_data = {
            'success': True,
            'data': data,
            'totalRows': total_rows,
            'page': page,
            'pageSize': page_size,
            'totalPages': (total_rows + page_size - 1) // page_size,
            'columnDefs': column_defs
        }

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error in data_studio_pagination_api: {e}")
        sentry_sdk.capture_exception(e)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def load_dataframe_for_pagination(datasource, user):
    """
    Load dataframe for pagination, prioritizing session data.
    
    Args:
        datasource: DataSource model instance
        user: User model instance
        
    Returns:
        pd.DataFrame or None: Loaded dataframe
    """
    try:
        # Check for active session first
        if session_exists(datasource, user):
            session_path = get_session_path(datasource, user)
            session_df = load_current_dataframe(session_path)
            if session_df is not None:
                return session_df

        # Fallback to original file
        file_path = datasource.file.path
        
        if file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            return pd.read_csv(file_path, delimiter=',', encoding='latin-1')
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            # Try Parquet as fallback
            return pd.read_parquet(file_path)

    except Exception as e:
        logger.error(f"Error loading dataframe for pagination: {e}")
        sentry_sdk.capture_exception(e)
        return None


def generate_column_definitions(df):
    """
    Generate column definitions for TanStack Table from dataframe.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        list: Column names as simple string array for TanStack Table
    """
    try:
        return list(df.columns) if not df.empty else []

    except Exception as e:
        logger.error(f"Error generating column definitions: {e}")
        sentry_sdk.capture_exception(e)
        return []