"""
Data Studio Views - Main view for data visualization and preparation.
"""
import json
import pandas as pd
import numpy as np
import logging
import sentry_sdk
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.core.files.base import ContentFile

from projects.models import DataSource
from core.utils.breadcrumbs import create_basic_breadcrumbs
from data_tools.services.data_analysis_service import calculate_nullity_report
from data_tools.services.session_service import (
    session_exists, load_current_dataframe, get_session_path
)

logger = logging.getLogger(__name__)


@login_required
def data_studio_page(request, pk):
    """
    Main Data Studio view for data visualization and preparation.
    Handles GET requests for initial page load.
    """
    try:
        datasource = get_object_or_404(DataSource, pk=pk, project__owner=request.user)

        # Build breadcrumbs
        breadcrumbs = create_basic_breadcrumbs(
            ('Workspace', reverse('projects:project_list')),
            (datasource.project.name, reverse('projects:project_detail', kwargs={'pk': datasource.project.pk})),
            (datasource.name, None),
        )

        # Load dataframe for analysis
        df = load_dataframe_from_source(datasource)
        if df is None:
            return render(request, 'data_tools/error.html', {
                'error_message': 'Failed to load data from source file.'
            })

        # Check if active session exists
        has_active_session = session_exists(datasource, request.user)
        session_data = None
        
        if has_active_session:
            session_path = get_session_path(datasource, request.user)
            session_df = load_current_dataframe(session_path)
            if session_df is not None:
                df = session_df  # Use session data instead of original

        # Generate automated analysis
        automated_analysis = generate_data_analysis(df)

        # Prepare column information for frontend
        column_list = prepare_column_info(df)
        
        # Prepare grid data for AG Grid with NaN handling
        # Load ALL data for client-side pagination (AG Grid can handle large datasets efficiently)
        if not df.empty:
            # For very large datasets (>50k rows), we might want to implement chunking
            # But for typical datasets, AG Grid's virtualization handles this well
            max_rows = 10000  # Safety limit for frontend performance
            if len(df) > max_rows:
                logger.warning(f"Large dataset detected ({len(df)} rows). Loading first {max_rows} rows for frontend.")
                sample_data = df.head(max_rows).fillna('').to_dict('records')
            else:
                # Load all data for client-side processing
                sample_data = df.fillna('').to_dict('records')
        else:
            sample_data = []
        grid_data_json = json.dumps(sample_data, default=str)
        
        # Prepare optimized column definitions for AG Grid with proper sizing
        column_defs = []
        for col in df.columns:
            # Determine column type for better filtering and rendering
            col_dtype = str(df[col].dtype)
            col_def = {
                'field': col,
                'headerName': col,
                'filter': True,
                'sortable': True,
                'resizable': True,
                'flex': 1,  # Allow flexible sizing
                'minWidth': 100,  # Minimum width to ensure readability
                'maxWidth': 300,  # Maximum width to prevent over-stretching
            }
            
            # Set specific filter types based on data type (without custom types to avoid warnings)
            if 'int' in col_dtype or 'float' in col_dtype:
                col_def['filter'] = 'agNumberColumnFilter'
                col_def['cellDataType'] = 'number'
            elif 'datetime' in col_dtype or 'date' in col_dtype:
                col_def['filter'] = 'agDateColumnFilter'
                col_def['cellDataType'] = 'date'
            else:
                col_def['filter'] = 'agTextColumnFilter'
                col_def['cellDataType'] = 'text'
            
            column_defs.append(col_def)
        
        column_defs_json = json.dumps(column_defs)

        context = {
            'datasource': datasource,
            'breadcrumbs': breadcrumbs,
            'automated_analysis': automated_analysis,
            'column_list': column_list,
            'has_active_session': has_active_session,
            'session_data': session_data,
            'grid_data_json': grid_data_json,
            'column_defs_json': column_defs_json,
        }

        return render(request, 'data_tools/data_studio.html', context)

    except Exception as e:
        logger.error(f"Error in data_studio_page: {e}")
        sentry_sdk.capture_exception(e)
        return render(request, 'data_tools/error.html', {
            'error_message': f'An error occurred while loading the Data Studio: {str(e)}'
        })


def load_dataframe_from_source(datasource):
    """
    Load dataframe from datasource file.
    
    Args:
        datasource: DataSource model instance
        
    Returns:
        pd.DataFrame or None: Loaded dataframe
    """
    try:
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
        logger.error(f"Error loading dataframe from {file_path}: {e}")
        sentry_sdk.capture_exception(e)
        return None


def generate_data_analysis(df):
    """
    Generate comprehensive data analysis for the dataframe.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        dict: Analysis results
    """
    try:
        # Basic information
        basic_info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
        }

        # Missing data analysis
        missing_data = calculate_nullity_report(df)

        # Data quality metrics
        quality_metrics = {
            'duplicate_rows': df.duplicated().sum(),
            'duplicate_percentage': round((df.duplicated().sum() / len(df)) * 100, 2),
        }

        return {
            'basic_info': basic_info,
            'missing_data': missing_data,
            'quality_metrics': quality_metrics,
        }

    except Exception as e:
        logger.error(f"Error generating data analysis: {e}")
        sentry_sdk.capture_exception(e)
        return {
            'basic_info': {'total_rows': 0, 'total_columns': 0},
            'missing_data': {'missing_percentage': 0},
            'quality_metrics': {'duplicate_rows': 0},
            'error': str(e)
        }


def prepare_column_info(df):
    """
    Prepare column information for frontend display.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        list: Column information
    """
    try:
        column_info = []
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_percentage = round((null_count / len(df)) * 100, 2) if len(df) > 0 else 0
            
            column_info.append({
                'name': col,
                'dtype': str(df[col].dtype),
                'missing_count': int(null_count),
                'missing_percentage': null_percentage,
                'total_values': len(df),
                'unique_values': df[col].nunique() if df[col].dtype != 'object' else min(df[col].nunique(), 100)
            })
        
        return column_info

    except Exception as e:
        logger.error(f"Error preparing column info: {e}")
        sentry_sdk.capture_exception(e)
        return []