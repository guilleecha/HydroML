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
from data_tools.services.session_manager import (
    get_session_manager, SessionConfig
)
from data_tools.services.session_service import (
    session_exists, load_current_dataframe, get_session_path
)

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy/pandas data types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)


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

        # Initialize unified session manager
        session_config = SessionConfig.from_user_preferences(request.user)
        session_manager = get_session_manager(
            user_id=request.user.id, 
            datasource_id=datasource.id, 
            config=session_config
        )
        
        # Check if unified session exists, fallback to legacy system
        has_active_session = session_manager.session_exists()
        session_data = None
        
        if has_active_session:
            # Use unified session data
            session_df = session_manager.get_current_dataframe()
            if session_df is not None:
                df = session_df
                session_data = session_manager.get_session_info()
        else:
            # Fallback to legacy file-based session check
            legacy_session_exists = session_exists(datasource, request.user)
            if legacy_session_exists:
                session_path = get_session_path(datasource, request.user)
                session_df = load_current_dataframe(session_path)
                if session_df is not None:
                    # Migrate legacy session to unified system
                    if session_manager.initialize_session(df, force=False):
                        if session_manager.apply_transformation(
                            session_df, 
                            "legacy_migration", 
                            {"source": "file_based_session"}
                        ):
                            df = session_df
                            session_data = session_manager.get_session_info()
                            has_active_session = True
                            logger.info(f"Migrated legacy session for user {request.user.id}, datasource {datasource.id}")
        
        # Initialize new session if none exists and we have data
        if not has_active_session and df is not None:
            if session_manager.initialize_session(df, force=False):
                session_data = session_manager.get_session_info()
                has_active_session = True

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
        
        # Prepare column definitions for TanStack Table (simple string array)
        column_defs = list(df.columns) if not df.empty else []
        column_defs_json = json.dumps(column_defs)

        # Prepare sample data for HTML table (like debug version)
        sample_data_records = df.head(10).fillna('').to_dict('records') if not df.empty else []
        sample_data = {
            'columns': list(df.columns) if not df.empty else [],
            'data': [list(record.values()) for record in sample_data_records] if sample_data_records else []
        }

        context = {
            'datasource': datasource,
            'breadcrumbs': breadcrumbs,
            'automated_analysis': automated_analysis,
            'column_list': column_list,
            'has_active_session': has_active_session,
            'session_data': session_data,
            'grid_data_json': grid_data_json,
            'column_defs_json': column_defs_json,
            'sample_data': sample_data,  # For HTML table in new template
            'breadcrumb_path': f'@{request.user.username}/Data Sources/{datasource.name}',  # For base template breadcrumb
            # Unified session context
            'session_manager_data': {
                'user_id': request.user.id,
                'datasource_id': datasource.id,
                'session_info': session_data,
                'can_undo': session_data.get('can_undo', False) if session_data else False,
                'can_redo': session_data.get('can_redo', False) if session_data else False,
                'current_step': session_data.get('current_step', 0) if session_data else 0,
                'total_operations': session_data.get('total_operations', 0) if session_data else 0,
            }
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


@login_required
def data_studio_debug(request, pk):
    """
    Debug version of Data Studio with clean template for progressive enhancement.
    """
    try:
        datasource = get_object_or_404(DataSource, pk=pk, project__owner=request.user)

        # Load dataframe for analysis
        df = load_dataframe_from_source(datasource)
        if df is None:
            return render(request, 'data_tools/error.html', {
                'error_message': 'Failed to load data from source file.'
            })

        # Generate automated analysis
        automated_analysis = generate_data_analysis(df)

        # Prepare column information for frontend
        column_list = prepare_column_info(df)
        
        # Prepare grid data for TanStack Table (all data for client-side pagination)
        if not df.empty:
            # For TanStack Table, load more data (up to 1000 rows for testing)
            max_rows = 1000  # Sufficient for testing TanStack Table features
            if len(df) > max_rows:
                logger.warning(f"Large dataset detected ({len(df)} rows). Loading first {max_rows} rows for TanStack Table testing.")
                sample_data_records = df.head(max_rows).fillna('').to_dict('records')
            else:
                # Load all data for client-side processing
                sample_data_records = df.fillna('').to_dict('records')
        else:
            sample_data_records = []
        
        # Prepare sample data for HTML table
        sample_data = {
            'columns': list(df.columns) if not df.empty else [],
            'data': [list(record.values()) for record in sample_data_records] if sample_data_records else []
        }
        
        # Prepare column definitions for AG Grid
        column_defs = []
        if not df.empty:
            for col in df.columns:
                column_def = {
                    'field': col,
                    'headerName': col,
                    'sortable': True,
                    'filter': True,
                    'resizable': True,
                }
                column_defs.append(column_def)

        context = {
            'datasource': datasource,
            'automated_analysis': automated_analysis,
            'column_list': column_list,
            'sample_data': sample_data,  # For HTML table
            'grid_data_json': json.dumps(sample_data_records, cls=NumpyEncoder),  # For JS usage
            'column_defs_json': json.dumps(column_defs, cls=NumpyEncoder),
            'breadcrumb_path': f'@{request.user.username}/Data Sources/{datasource.name}',  # Complete breadcrumb path
        }

        return render(request, 'data_tools/data_studio_clean.html', context)

    except Exception as e:
        logger.error(f"Error in data_studio_debug: {e}")
        sentry_sdk.capture_exception(e)
        return render(request, 'data_tools/error.html', {
            'error_message': f'An error occurred: {str(e)}'
        })