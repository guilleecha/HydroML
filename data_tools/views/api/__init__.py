"""
API views package for data_tools.
Contains organized API endpoints grouped by functionality.
"""

# Import all API views for easy access
from .datasource_api_views import DataSourceColumnsAPIView, FusionColumnsAPIView, get_datasource_columns
from .sql_api_views import SQLExecutionAPIView, QueryHistoryAPIView
from .visualization_api_views import ChartGenerationAPIView

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
    
    # Function-based views (for backward compatibility)
    'get_columns_api',
    'get_fusion_columns_api',
    'generate_chart_api',
    'execute_sql_api',
    'get_query_history_api',
    'get_datasource_columns'
]
