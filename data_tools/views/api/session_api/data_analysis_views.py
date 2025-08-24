"""
Data Analysis API Views - Statistical analysis and data profiling operations.
Provides comprehensive column statistics and data insights for session DataFrames.
"""

import pandas as pd
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from data_tools.services.api_performance_service import monitor_performance
from .utils import (
    validate_session_and_datasource, validate_active_session,
    log_and_handle_exception
)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
@monitor_performance
def get_column_statistics(request, datasource_id):
    """Get comprehensive descriptive statistics for all columns in the current session."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        current_df = validate_active_session(session_manager)
        if current_df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            }, status=400)
        
        # Generate column and dataset statistics
        column_stats = _generate_column_statistics(current_df)
        dataset_stats = _generate_dataset_statistics(current_df)
        
        return JsonResponse({
            'success': True,
            'column_statistics': column_stats,
            'dataset_statistics': dataset_stats
        })
        
    except Exception as e:
        return log_and_handle_exception("get column statistics", e)


def _generate_column_statistics(df: pd.DataFrame) -> dict:
    """Generate comprehensive statistics for each column."""
    stats_dict = {}
    
    for col in df.columns:
        col_stats = _get_basic_column_stats(df[col], col)
        
        # Add type-specific statistics
        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats.update(_get_numeric_column_stats(df[col]))
        elif pd.api.types.is_object_dtype(df[col]):
            col_stats.update(_get_categorical_column_stats(df[col]))
        
        stats_dict[col] = col_stats
    
    return stats_dict


def _get_basic_column_stats(series: pd.Series, col_name: str) -> dict:
    """Get basic statistics available for all column types."""
    return {
        'name': col_name,
        'dtype': str(series.dtype),
        'non_null_count': int(series.count()),
        'null_count': int(series.isnull().sum()),
        'null_percentage': float((series.isnull().sum() / len(series)) * 100),
        'unique_count': int(series.nunique()),
        'memory_usage': int(series.memory_usage(deep=True))
    }


def _get_numeric_column_stats(series: pd.Series) -> dict:
    """Get statistics specific to numeric columns."""
    return {
        'mean': float(series.mean()) if pd.notnull(series.mean()) else None,
        'median': float(series.median()) if pd.notnull(series.median()) else None,
        'std': float(series.std()) if pd.notnull(series.std()) else None,
        'min': float(series.min()) if pd.notnull(series.min()) else None,
        'max': float(series.max()) if pd.notnull(series.max()) else None,
    }


def _get_categorical_column_stats(series: pd.Series) -> dict:
    """Get statistics specific to categorical/object columns."""
    top_value = series.mode().iloc[0] if len(series.mode()) > 0 else None
    return {
        'top_value': str(top_value) if top_value is not None else None,
        'top_value_freq': int(series.value_counts().iloc[0]) if len(series.value_counts()) > 0 else 0
    }


def _generate_dataset_statistics(df: pd.DataFrame) -> dict:
    """Generate overall dataset statistics."""
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage_mb': float(df.memory_usage(deep=True).sum() / (1024 * 1024)),
        'total_null_values': int(df.isnull().sum().sum())
    }