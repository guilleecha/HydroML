# data_tools/views/api/column_flags_api.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from projects.models import DataSource
from projects.utils.column_analyzer import ColumnAnalyzer
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
@login_required
def get_column_flags_api(request, datasource_id):
    """
    API endpoint to get column flags for ML validation
    
    Returns column-by-column analysis including:
    - Data quality flags (NaN, outliers, etc.)
    - ML suitability indicators
    - Warnings and recommendations
    """
    try:
        # Get datasource with permission check
        datasource = DataSource.objects.get(
            id=datasource_id,
            projects__owner=request.user
        )
        
        # Get or generate column flags
        if not datasource.column_flags:
            logger.info(f"Generating column flags for datasource {datasource.name}")
            flags = ColumnAnalyzer.update_datasource_flags(datasource)
        else:
            flags = datasource.column_flags
            logger.info(f"Using cached column flags for datasource {datasource.name}")
        
        # Extract column names and flags for frontend
        columns_info = {}
        metadata = flags.get('_metadata', {})
        
        for column_name, column_data in flags.items():
            if column_name.startswith('_'):  # Skip metadata
                continue
                
            columns_info[column_name] = {
                'name': column_name,
                'data_type': column_data.get('data_type', 'unknown'),
                'has_nan': column_data.get('has_nan', False),
                'nan_percentage': column_data.get('nan_percentage', 0),
                'unique_values': column_data.get('unique_values', 0),
                'warnings': column_data.get('warnings', []),
                'suitable_for_target': column_data.get('suitable_for_target', True),
                'suitable_for_features': column_data.get('suitable_for_features', True),
                'ml_problem_type': column_data.get('ml_problem_type', 'unknown'),
                'zero_variance': column_data.get('zero_variance', False),
                'is_numeric': column_data.get('is_numeric', False),
                'is_categorical': column_data.get('is_categorical', False),
                'outliers_percentage': column_data.get('outliers_percentage', 0)
            }
        
        return JsonResponse({
            'success': True,
            'columns': columns_info,
            'metadata': metadata,
            'datasource_name': datasource.name
        })
        
    except DataSource.DoesNotExist:
        logger.warning(f"Datasource {datasource_id} not found or no permission for user {request.user}")
        return JsonResponse({
            'success': False,
            'error': 'Datasource no encontrado o sin permisos'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error getting column flags for {datasource_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error obteniendo flags de columnas: {str(e)}'
        }, status=500)