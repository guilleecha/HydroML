"""
API views package for data_tools.
Contains organized API endpoints grouped by functionality.
"""

# Import all API views for easy access
from .datasource_api_views import DataSourceColumnsAPIView, FusionColumnsAPIView, get_datasource_columns
from .sql_api_views import SQLExecutionAPIView, QueryHistoryAPIView
from .visualization_api_views import ChartGenerationAPIView
from .session_api.session_lifecycle_views import (
    initialize_session, get_session_status, clear_session, save_as_new_datasource
)
from .session_api.session_operations_views import (
    undo_operation, redo_operation
)
from .transformation_api_views import (
    apply_missing_data_imputation, apply_feature_encoding, apply_feature_scaling,
    apply_outlier_treatment, apply_feature_engineering, apply_column_operations
)
from .export_api_views import (
    ExportJobAPIView, ExportJobActionAPIView, ExportTemplateAPIView
)

# For backward compatibility with the old api_views.py imports
get_columns_api = DataSourceColumnsAPIView.as_view()
get_fusion_columns_api = FusionColumnsAPIView.as_view()
generate_chart_api = ChartGenerationAPIView.as_view()
execute_sql_api = SQLExecutionAPIView.as_view()
get_query_history_api = QueryHistoryAPIView.as_view()

__all__ = [
    # Class-based views
    'DataSourceColumnsAPIView',
    'FusionColumnsAPIView', 
    'SQLExecutionAPIView',
    'QueryHistoryAPIView',
    'ChartGenerationAPIView',
    'ExportJobAPIView',
    'ExportJobActionAPIView',
    'ExportTemplateAPIView',
    
    # Function-based views (for backward compatibility)
    'get_columns_api',
    'get_fusion_columns_api',
    'generate_chart_api',
    'execute_sql_api',
    'get_query_history_api',
    'get_datasource_columns',
    
    # Session management API views
    'initialize_session',
    'get_session_status',
    'undo_operation',
    'redo_operation',
    'clear_session',
    'save_as_new_datasource',
    
    # Transformation API views
    'apply_missing_data_imputation',
    'apply_feature_encoding',
    'apply_feature_scaling',
    'apply_outlier_treatment',
    'apply_feature_engineering',
    'apply_column_operations'
]
