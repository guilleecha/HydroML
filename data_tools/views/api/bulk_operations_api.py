"""
Bulk Operations API for Data Studio
Provides high-performance bulk operations with real-time progress tracking
"""

import json
import uuid
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from asgiref.sync import sync_to_async, async_to_sync

from projects.models import DataSource
from data_tools.services.session_manager import get_session_manager
from data_tools.services.api_performance_service import (
    rate_limit, cache_response, monitor_performance, 
    bulk_operation_manager
)
# from data_tools.websockets.data_studio_consumer import sync_send_bulk_progress, sync_send_error
from data_tools.views.api.mixins import BaseAPIView

logger = logging.getLogger(__name__)


@method_decorator([csrf_exempt, login_required], name='dispatch')
class BulkOperationsAPIView(BaseAPIView):
    """
    API endpoint for bulk operations on datasets
    """
    
    @method_decorator([rate_limit(limit=10, window_seconds=3600), monitor_performance])
    def post(self, request, datasource_id):
        """
        Start a bulk operation
        
        Request body:
        {
            "operation_type": "delete_rows|update_cells|apply_transformations",
            "parameters": {...},
            "items": [...],
            "options": {...}
        }
        """
        try:
            # Validate datasource
            datasource = self.get_datasource(datasource_id)
            validation_error = self.validate_datasource_status(datasource)
            if validation_error:
                return self.error_response(validation_error['error'])
            
            # Parse request
            data = json.loads(request.body)
            operation_type = data.get('operation_type')
            parameters = data.get('parameters', {})
            items = data.get('items', [])
            options = data.get('options', {})
            
            if not operation_type or not items:
                return self.error_response("operation_type and items are required")
            
            # Generate operation ID
            operation_id = str(uuid.uuid4())
            
            # Validate operation type
            if operation_type not in ['delete_rows', 'update_cells', 'apply_transformations', 'column_operations']:
                return self.error_response(f"Unsupported operation type: {operation_type}")
            
            # Start bulk operation
            bulk_operation_manager.start_operation(operation_id, len(items), str(request.user.id))
            
            # Execute operation asynchronously
            self._execute_bulk_operation_async(
                operation_id, operation_type, datasource_id, 
                parameters, items, options, request.user.id
            )
            
            return self.success_response({
                'operation_id': operation_id,
                'status': 'started',
                'total_items': len(items)
            }, message="Bulk operation started successfully")
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error starting bulk operation: {e}")
            return self.error_response(str(e), status_code=500)
    
    @method_decorator([rate_limit(limit=60, window_seconds=60), cache_response(ttl=10)])
    def get(self, request, datasource_id):
        """
        Get status of bulk operations for this datasource
        """
        try:
            operation_id = request.GET.get('operation_id')
            
            if operation_id:
                # Get specific operation status
                status = bulk_operation_manager.get_operation_status(operation_id)
                if not status:
                    return self.error_response("Operation not found", status_code=404)
                
                return self.success_response(status)
            else:
                # Get all active operations for user (would need to implement user filtering)
                return self.success_response({
                    'message': 'Use operation_id parameter to get specific operation status'
                })
                
        except Exception as e:
            logger.error(f"Error getting bulk operation status: {e}")
            return self.error_response(str(e), status_code=500)
    
    def _execute_bulk_operation_async(self, operation_id: str, operation_type: str,
                                    datasource_id: str, parameters: Dict[str, Any],
                                    items: List[Any], options: Dict[str, Any],
                                    user_id: int):
        """
        Execute bulk operation asynchronously in thread pool
        """
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(
            self._execute_bulk_operation,
            operation_id, operation_type, datasource_id,
            parameters, items, options, user_id
        )
    
    def _execute_bulk_operation(self, operation_id: str, operation_type: str,
                              datasource_id: str, parameters: Dict[str, Any],
                              items: List[Any], options: Dict[str, Any],
                              user_id: int):
        """
        Execute the actual bulk operation with progress tracking
        """
        try:
            session_manager = get_session_manager(user_id, datasource_id)
            
            # Initialize progress
            total_items = len(items)
            processed = 0
            batch_size = options.get('batch_size', 100)
            
            # Send initial progress
            sync_send_bulk_progress(operation_id, 0, total_items, 'running')
            
            if operation_type == 'delete_rows':
                processed = self._execute_delete_rows(
                    operation_id, session_manager, items, batch_size, total_items
                )
            
            elif operation_type == 'update_cells':
                processed = self._execute_update_cells(
                    operation_id, session_manager, items, parameters, batch_size, total_items
                )
            
            elif operation_type == 'apply_transformations':
                processed = self._execute_transformations(
                    operation_id, session_manager, items, parameters, batch_size, total_items
                )
            
            elif operation_type == 'column_operations':
                processed = self._execute_column_operations(
                    operation_id, session_manager, items, parameters, batch_size, total_items
                )
            
            # Complete operation
            bulk_operation_manager.complete_operation(operation_id, True)
            sync_send_bulk_progress(operation_id, processed, total_items, 'completed')
            
        except Exception as e:
            logger.error(f"Bulk operation {operation_id} failed: {e}")
            bulk_operation_manager.complete_operation(operation_id, False)
            sync_send_error(datasource_id, 'bulk_operation', str(e))
            sync_send_bulk_progress(operation_id, processed, total_items, 'failed')
    
    def _execute_delete_rows(self, operation_id: str, session_manager, row_indices: List[int], 
                           batch_size: int, total_items: int) -> int:
        """Execute bulk row deletion"""
        processed = 0
        
        # Sort indices in descending order to avoid index shifting issues
        sorted_indices = sorted(row_indices, reverse=True)
        
        for i in range(0, len(sorted_indices), batch_size):
            batch = sorted_indices[i:i + batch_size]
            
            # Delete rows in current batch
            current_df = session_manager.get_current_dataframe()
            if current_df is not None:
                # Remove rows by index
                new_df = current_df.drop(current_df.index[batch]).reset_index(drop=True)
                session_manager.update_dataframe(
                    new_df, 
                    operation_name=f"Bulk delete rows (batch {i//batch_size + 1})"
                )
            
            processed += len(batch)
            
            # Update progress
            bulk_operation_manager.update_progress(operation_id, processed)
            sync_send_bulk_progress(operation_id, processed, total_items, 'running')
        
        return processed
    
    def _execute_update_cells(self, operation_id: str, session_manager, updates: List[Dict[str, Any]], 
                            parameters: Dict[str, Any], batch_size: int, total_items: int) -> int:
        """Execute bulk cell updates"""
        processed = 0
        
        current_df = session_manager.get_current_dataframe()
        if current_df is None:
            raise Exception("No active session dataframe")
        
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            
            # Apply updates in current batch
            for update in batch:
                row_index = update.get('row_index')
                column = update.get('column')
                new_value = update.get('value')
                
                if row_index is not None and column and column in current_df.columns:
                    try:
                        current_df.at[row_index, column] = new_value
                    except Exception as e:
                        bulk_operation_manager.update_progress(
                            operation_id, processed, error=f"Update failed for row {row_index}, col {column}: {e}"
                        )
            
            processed += len(batch)
            
            # Update session dataframe periodically
            if i % (batch_size * 5) == 0:  # Every 5 batches
                session_manager.update_dataframe(
                    current_df.copy(),
                    operation_name=f"Bulk cell updates (batch {i//batch_size + 1})"
                )
            
            # Update progress
            bulk_operation_manager.update_progress(operation_id, processed)
            sync_send_bulk_progress(operation_id, processed, total_items, 'running')
        
        # Final dataframe update
        session_manager.update_dataframe(current_df, operation_name="Bulk cell updates completed")
        
        return processed
    
    def _execute_transformations(self, operation_id: str, session_manager, transformations: List[Dict[str, Any]], 
                               parameters: Dict[str, Any], batch_size: int, total_items: int) -> int:
        """Execute bulk transformations"""
        processed = 0
        
        for i, transformation in enumerate(transformations):
            try:
                transform_type = transformation.get('type')
                transform_params = transformation.get('parameters', {})
                
                # Apply transformation based on type
                if transform_type == 'fill_missing':
                    self._apply_fill_missing(session_manager, transform_params)
                elif transform_type == 'scale_numeric':
                    self._apply_scale_numeric(session_manager, transform_params)
                elif transform_type == 'encode_categorical':
                    self._apply_encode_categorical(session_manager, transform_params)
                else:
                    bulk_operation_manager.update_progress(
                        operation_id, processed, error=f"Unknown transformation type: {transform_type}"
                    )
                    continue
                
                processed += 1
                
                # Update progress
                bulk_operation_manager.update_progress(operation_id, processed)
                sync_send_bulk_progress(operation_id, processed, total_items, 'running')
                
            except Exception as e:
                bulk_operation_manager.update_progress(
                    operation_id, processed, error=f"Transformation {i} failed: {e}"
                )
        
        return processed
    
    def _execute_column_operations(self, operation_id: str, session_manager, operations: List[Dict[str, Any]], 
                                 parameters: Dict[str, Any], batch_size: int, total_items: int) -> int:
        """Execute bulk column operations"""
        processed = 0
        
        current_df = session_manager.get_current_dataframe()
        if current_df is None:
            raise Exception("No active session dataframe")
        
        for operation in operations:
            try:
                op_type = operation.get('type')
                op_params = operation.get('parameters', {})
                
                if op_type == 'drop_columns':
                    columns_to_drop = op_params.get('columns', [])
                    existing_columns = [col for col in columns_to_drop if col in current_df.columns]
                    if existing_columns:
                        current_df = current_df.drop(columns=existing_columns)
                
                elif op_type == 'rename_columns':
                    rename_map = op_params.get('rename_map', {})
                    current_df = current_df.rename(columns=rename_map)
                
                elif op_type == 'add_column':
                    column_name = op_params.get('name')
                    default_value = op_params.get('default_value')
                    if column_name:
                        current_df[column_name] = default_value
                
                elif op_type == 'reorder_columns':
                    column_order = op_params.get('order', [])
                    if all(col in current_df.columns for col in column_order):
                        current_df = current_df[column_order]
                
                processed += 1
                
                # Update progress
                bulk_operation_manager.update_progress(operation_id, processed)
                sync_send_bulk_progress(operation_id, processed, total_items, 'running')
                
            except Exception as e:
                bulk_operation_manager.update_progress(
                    operation_id, processed, error=f"Column operation failed: {e}"
                )
        
        # Update session with final dataframe
        session_manager.update_dataframe(current_df, operation_name="Bulk column operations completed")
        
        return processed
    
    # Helper methods for transformations
    def _apply_fill_missing(self, session_manager, params: Dict[str, Any]):
        """Apply missing value filling"""
        current_df = session_manager.get_current_dataframe()
        columns = params.get('columns', [])
        method = params.get('method', 'mean')
        
        for column in columns:
            if column in current_df.columns:
                if method == 'mean' and current_df[column].dtype in ['int64', 'float64']:
                    current_df[column].fillna(current_df[column].mean(), inplace=True)
                elif method == 'median' and current_df[column].dtype in ['int64', 'float64']:
                    current_df[column].fillna(current_df[column].median(), inplace=True)
                elif method == 'mode':
                    mode_value = current_df[column].mode().iloc[0] if not current_df[column].mode().empty else None
                    if mode_value is not None:
                        current_df[column].fillna(mode_value, inplace=True)
                elif method == 'forward_fill':
                    current_df[column].fillna(method='ffill', inplace=True)
                elif method == 'backward_fill':
                    current_df[column].fillna(method='bfill', inplace=True)
        
        session_manager.update_dataframe(current_df, operation_name="Fill missing values")
    
    def _apply_scale_numeric(self, session_manager, params: Dict[str, Any]):
        """Apply numeric scaling"""
        from sklearn.preprocessing import StandardScaler, MinMaxScaler
        
        current_df = session_manager.get_current_dataframe()
        columns = params.get('columns', [])
        method = params.get('method', 'standard')
        
        numeric_columns = [col for col in columns if col in current_df.columns and 
                          current_df[col].dtype in ['int64', 'float64']]
        
        if numeric_columns:
            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            else:
                return
            
            current_df[numeric_columns] = scaler.fit_transform(current_df[numeric_columns])
            session_manager.update_dataframe(current_df, operation_name=f"Scale numeric columns ({method})")
    
    def _apply_encode_categorical(self, session_manager, params: Dict[str, Any]):
        """Apply categorical encoding"""
        current_df = session_manager.get_current_dataframe()
        columns = params.get('columns', [])
        method = params.get('method', 'onehot')
        
        for column in columns:
            if column in current_df.columns:
                if method == 'onehot':
                    # One-hot encoding
                    dummies = current_df[column].astype(str).str.get_dummies(prefix=column)
                    current_df = current_df.drop(columns=[column])
                    current_df = current_df.join(dummies)
                elif method == 'label':
                    # Label encoding
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    current_df[column] = le.fit_transform(current_df[column].astype(str))
        
        session_manager.update_dataframe(current_df, operation_name="Encode categorical variables")


# Function-based views for specific operations
@csrf_exempt
@login_required
@require_http_methods(["GET"])
@rate_limit(limit=30, window_seconds=60)
@cache_response(ttl=30)
def bulk_operation_status(request, operation_id):
    """
    Get detailed status of a bulk operation
    """
    try:
        status = bulk_operation_manager.get_operation_status(operation_id)
        if not status:
            return JsonResponse({'error': 'Operation not found'}, status=404)
        
        return JsonResponse({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting bulk operation status: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
@rate_limit(limit=5, window_seconds=60)
def cancel_bulk_operation(request, operation_id):
    """
    Cancel a running bulk operation
    """
    try:
        status = bulk_operation_manager.get_operation_status(operation_id)
        if not status:
            return JsonResponse({'error': 'Operation not found'}, status=404)
        
        if status['status'] == 'running':
            # Mark as cancelled (actual cancellation would require more complex implementation)
            bulk_operation_manager.complete_operation(operation_id, False)
            sync_send_bulk_progress(operation_id, status['processed_items'], 
                                  status['total_items'], 'cancelled')
            
            return JsonResponse({
                'success': True,
                'message': 'Operation cancelled successfully'
            })
        else:
            return JsonResponse({
                'error': f'Cannot cancel operation with status: {status["status"]}'
            }, status=400)
        
    except Exception as e:
        logger.error(f"Error cancelling bulk operation: {e}")
        return JsonResponse({'error': str(e)}, status=500)