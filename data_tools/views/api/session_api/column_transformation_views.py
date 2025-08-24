"""
Column Transformation API Views - Data column modification operations.
Handles column renaming, type changes, and missing value filling with session integration.
"""

import pandas as pd
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from data_tools.services.api_performance_service import monitor_performance
from .utils import (
    validate_session_and_datasource, validate_active_session, 
    format_success_response, log_and_handle_exception, 
    parse_json_body, validate_required_fields, validate_columns_exist
)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
@monitor_performance
def rename_column(request, datasource_id):
    """Rename a column in the current session DataFrame."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        current_df = validate_active_session(session_manager)
        if current_df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            }, status=400)
        
        # Validate request data
        data = parse_json_body(request)
        error_msg = validate_required_fields(data, ['old_name', 'new_name'])
        if error_msg:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        
        old_name, new_name = data['old_name'], data['new_name']
        
        # Validate column operations
        validation_error = _validate_column_rename(current_df, old_name, new_name)
        if validation_error:
            return JsonResponse({'success': False, 'error': validation_error}, status=400)
        
        # Apply transformation
        df_renamed = current_df.rename(columns={old_name: new_name})
        operation_params = {'old_name': old_name, 'new_name': new_name}
        
        success = session_manager.apply_transformation(df_renamed, "rename_column", operation_params)
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to apply column rename'
            }, status=500)
        
        return JsonResponse(format_success_response(
            f'Column renamed from "{old_name}" to "{new_name}"', session_manager, df_renamed
        ))
        
    except Exception as e:
        return log_and_handle_exception("rename column", e)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
@monitor_performance
def change_column_type(request, datasource_id):
    """Change the data type of a column in the current session DataFrame."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        current_df = validate_active_session(session_manager)
        if current_df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            }, status=400)
        
        # Validate request data
        data = parse_json_body(request)
        error_msg = validate_required_fields(data, ['column_name', 'new_type'])
        if error_msg:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        
        column_name, new_type = data['column_name'], data['new_type']
        
        # Validate column exists
        error_msg = validate_columns_exist(current_df, [column_name])
        if error_msg:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        
        # Apply type conversion
        df_converted, conversion_error = _convert_column_type(current_df, column_name, new_type)
        if conversion_error:
            return JsonResponse({'success': False, 'error': conversion_error}, status=400)
        
        # Store transformation
        operation_params = {
            'column_name': column_name,
            'old_type': str(current_df[column_name].dtype),
            'new_type': new_type
        }
        
        success = session_manager.apply_transformation(df_converted, "change_column_type", operation_params)
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to apply column type change'
            }, status=500)
        
        return JsonResponse(format_success_response(
            f'Column "{column_name}" converted to {new_type}', session_manager, df_converted
        ))
        
    except Exception as e:
        return log_and_handle_exception("change column type", e)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
@monitor_performance
def fill_missing_values(request, datasource_id):
    """Fill missing values in specified columns using various strategies."""
    try:
        datasource, session_manager = validate_session_and_datasource(request.user, datasource_id)
        
        current_df = validate_active_session(session_manager)
        if current_df is None:
            return JsonResponse({
                'success': False,
                'error': 'No active session found'
            }, status=400)
        
        # Validate request data
        data = parse_json_body(request)
        columns = data.get('columns', [])
        strategy = data.get('strategy', 'mean')
        fill_value = data.get('fill_value', None)
        
        if not columns:
            return JsonResponse({
                'success': False,
                'error': 'At least one column must be specified'
            }, status=400)
        
        # Validate columns exist
        error_msg = validate_columns_exist(current_df, columns)
        if error_msg:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        
        # Apply filling strategy
        df_filled, filled_count, fill_error = _apply_filling_strategy(
            current_df, columns, strategy, fill_value
        )
        if fill_error:
            return JsonResponse({'success': False, 'error': fill_error}, status=400)
        
        # Store transformation
        operation_params = {
            'columns': columns,
            'strategy': strategy,
            'fill_value': fill_value,
            'filled_count': int(filled_count)
        }
        
        success = session_manager.apply_transformation(df_filled, "fill_missing_values", operation_params)
        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Failed to apply missing value fill'
            }, status=500)
        
        return JsonResponse(format_success_response(
            f'Filled {filled_count} missing values using {strategy} strategy', 
            session_manager, df_filled
        ))
        
    except Exception as e:
        return log_and_handle_exception("fill missing values", e)


def _validate_column_rename(df: pd.DataFrame, old_name: str, new_name: str) -> str:
    """Validate column rename operation."""
    if old_name not in df.columns:
        return f'Column "{old_name}" not found'
    if new_name in df.columns:
        return f'Column "{new_name}" already exists'
    return None


def _convert_column_type(df: pd.DataFrame, column_name: str, new_type: str) -> tuple:
    """Convert column type and return (converted_df, error_message)."""
    type_mapping = {
        'int': 'int64', 'float': 'float64', 'string': 'object',
        'datetime': 'datetime64[ns]', 'boolean': 'bool', 'category': 'category'
    }
    
    pandas_dtype = type_mapping.get(new_type, new_type)
    df_converted = df.copy()
    
    try:
        if new_type == 'datetime':
            df_converted[column_name] = pd.to_datetime(df_converted[column_name], errors='coerce')
        else:
            df_converted[column_name] = df_converted[column_name].astype(pandas_dtype)
        return df_converted, None
    except (ValueError, TypeError) as e:
        return None, f'Failed to convert column to {new_type}: {str(e)}'


def _apply_filling_strategy(df: pd.DataFrame, columns: list, strategy: str, fill_value) -> tuple:
    """Apply missing value filling strategy and return (filled_df, count, error_message)."""
    df_filled = df.copy()
    total_filled = 0
    
    for column in columns:
        col_data = df_filled[column]
        original_nulls = col_data.isnull().sum()
        
        try:
            if strategy == 'mean' and pd.api.types.is_numeric_dtype(col_data):
                df_filled[column] = col_data.fillna(col_data.mean())
            elif strategy == 'median' and pd.api.types.is_numeric_dtype(col_data):
                df_filled[column] = col_data.fillna(col_data.median())
            elif strategy == 'mode':
                mode_value = col_data.mode().iloc[0] if len(col_data.mode()) > 0 else None
                if mode_value is not None:
                    df_filled[column] = col_data.fillna(mode_value)
            elif strategy == 'forward_fill':
                df_filled[column] = col_data.fillna(method='ffill')
            elif strategy == 'backward_fill':
                df_filled[column] = col_data.fillna(method='bfill')
            elif strategy == 'constant' and fill_value is not None:
                df_filled[column] = col_data.fillna(fill_value)
            else:
                return None, 0, f'Invalid strategy "{strategy}" for column "{column}" or missing fill_value'
        
            remaining_nulls = df_filled[column].isnull().sum()
            total_filled += original_nulls - remaining_nulls
            
        except Exception as e:
            return None, 0, f'Error filling column "{column}": {str(e)}'
    
    return df_filled, total_filled, None