"""
NaN Cleaning API - Quick removal of NaN values.
Provides fast cleaning operations for Data Studio.
"""
import logging
import pandas as pd
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .mixins import BaseAPIView
from data_tools.services.session_manager import get_session_manager
from data_tools.services.data_cleaning_service import DataCleaningService

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class QuickNaNCleaningAPIView(BaseAPIView, View):
    """
    API view for quick NaN cleaning operations in Data Studio.
    """
    
    def post(self, request, datasource_id):
        """
        Quick clean NaN values from current session data.
        
        Args:
            request: HTTP request with cleaning options
            datasource_id: UUID of the DataSource
            
        Returns:
            JsonResponse: Cleaned data summary and status
        """
        try:
            # Get session manager and current DataFrame
            session_manager = get_session_manager(request.user.id, datasource_id)
            current_df = session_manager.get_current_dataframe()
            
            if current_df is None:
                return self.error_response('No hay datos cargados en la sesión actual')
            
            # Get cleaning options from request
            remove_nan_rows = request.POST.get('remove_nan_rows', 'true').lower() == 'true'
            remove_nan_columns = request.POST.get('remove_nan_columns', 'true').lower() == 'true'
            
            # Store original shape
            original_shape = current_df.shape
            
            # Apply quick NaN cleaning
            cleaned_df = current_df.copy()
            
            # Track what was removed
            cleaning_summary = {
                'original_rows': original_shape[0],
                'original_columns': original_shape[1],
                'rows_removed': 0,
                'columns_removed': 0,
                'columns_dropped': [],
                'operations_performed': []
            }
            
            # 1. Remove columns that are completely NaN
            if remove_nan_columns:
                nan_columns = cleaned_df.columns[cleaned_df.isna().all()].tolist()
                if nan_columns:
                    cleaned_df = cleaned_df.drop(columns=nan_columns)
                    cleaning_summary['columns_removed'] = len(nan_columns)
                    cleaning_summary['columns_dropped'] = nan_columns
                    cleaning_summary['operations_performed'].append({
                        'operation': 'remove_nan_columns',
                        'columns_removed': len(nan_columns),
                        'column_names': nan_columns
                    })
            
            # 2. Remove rows with any NaN values
            if remove_nan_rows:
                rows_before = len(cleaned_df)
                cleaned_df = cleaned_df.dropna(axis=0, how='any')
                rows_removed = rows_before - len(cleaned_df)
                
                if rows_removed > 0:
                    cleaning_summary['rows_removed'] = rows_removed
                    cleaning_summary['operations_performed'].append({
                        'operation': 'remove_nan_rows',
                        'rows_removed': rows_removed
                    })
            
            # Final shape
            final_shape = cleaned_df.shape
            cleaning_summary['final_rows'] = final_shape[0]
            cleaning_summary['final_columns'] = final_shape[1]
            
            # Check if any cleaning was performed
            if final_shape == original_shape:
                return self.success_response({
                    'message': '¡No se encontraron valores NaN para limpiar!',
                    'summary': cleaning_summary,
                    'data_changed': False
                })
            
            # Save cleaned DataFrame to session with operation tracking
            operation_params = {
                'operation': 'quick_nan_cleaning',
                'remove_nan_rows': remove_nan_rows,
                'remove_nan_columns': remove_nan_columns,
                'summary': cleaning_summary
            }
            
            session_manager.apply_transformation(
                cleaned_df, 
                'quick_nan_cleaning', 
                operation_params
            )
            
            # Prepare success response
            return self.success_response({
                'message': f'¡Limpieza completada! {cleaning_summary["rows_removed"]} filas y {cleaning_summary["columns_removed"]} columnas eliminadas.',
                'summary': cleaning_summary,
                'data_changed': True,
                'new_shape': final_shape,
                'original_shape': original_shape
            })
            
        except Exception as e:
            logger.error(f"Quick NaN cleaning failed: {e}")
            return self.error_response(f'Error en la limpieza: {str(e)}')


@method_decorator(login_required, name='dispatch')  
class NaNAnalysisAPIView(BaseAPIView, View):
    """
    API view for analyzing NaN values in current data.
    """
    
    def get(self, request, datasource_id):
        """
        Analyze NaN values in current session data.
        
        Args:
            request: HTTP request
            datasource_id: UUID of the DataSource
            
        Returns:
            JsonResponse: NaN analysis report
        """
        try:
            # Get session manager and current DataFrame
            session_manager = get_session_manager(request.user.id, datasource_id)
            current_df = session_manager.get_current_dataframe()
            
            if current_df is None:
                return self.error_response('No hay datos cargados en la sesión actual')
            
            # Analyze NaN values
            analysis = {
                'total_rows': len(current_df),
                'total_columns': len(current_df.columns),
                'total_cells': len(current_df) * len(current_df.columns),
                'nan_analysis': {}
            }
            
            # Analyze each column
            columns_with_nan = []
            columns_completely_nan = []
            total_nan_cells = 0
            
            for column in current_df.columns:
                nan_count = current_df[column].isna().sum()
                if nan_count > 0:
                    nan_percentage = (nan_count / len(current_df)) * 100
                    
                    column_analysis = {
                        'column': column,
                        'nan_count': int(nan_count),
                        'nan_percentage': round(nan_percentage, 2),
                        'total_values': len(current_df),
                        'is_completely_nan': nan_count == len(current_df)
                    }
                    
                    columns_with_nan.append(column_analysis)
                    total_nan_cells += nan_count
                    
                    if nan_count == len(current_df):
                        columns_completely_nan.append(column)
            
            # Rows with any NaN
            rows_with_nan = current_df.isna().any(axis=1).sum()
            
            # Overall statistics
            analysis.update({
                'total_nan_cells': int(total_nan_cells),
                'nan_cell_percentage': round((total_nan_cells / analysis['total_cells']) * 100, 2),
                'columns_with_nan': len(columns_with_nan),
                'columns_completely_nan': len(columns_completely_nan),
                'rows_with_nan': int(rows_with_nan),
                'rows_with_nan_percentage': round((rows_with_nan / len(current_df)) * 100, 2),
                'column_details': columns_with_nan,
                'completely_nan_columns': columns_completely_nan
            })
            
            # Recommendations
            recommendations = []
            
            if len(columns_completely_nan) > 0:
                recommendations.append(f"Eliminar {len(columns_completely_nan)} columnas completamente vacías")
            
            if rows_with_nan > 0:
                recommendations.append(f"Considerar eliminar {rows_with_nan} filas con valores faltantes")
            
            if len(columns_with_nan) == 0:
                recommendations.append("¡Excelente! No se encontraron valores NaN en los datos")
            
            analysis['recommendations'] = recommendations
            
            return self.success_response(analysis)
            
        except Exception as e:
            logger.error(f"NaN analysis failed: {e}")
            return self.error_response(f'Error en el análisis: {str(e)}')