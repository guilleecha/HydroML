# data_tools/views/api_views.py
"""
Refactored API Views - Imports from Modular Architecture.
This file maintains backward compatibility while leveraging the new modular API structure.
"""

# Import all API views from the modular structure
from .api import (
    # DataSource APIs
    get_columns_api,
    get_fusion_columns_api,
    get_datasource_columns,
    
    # Chart APIs  
    generate_chart_api,
    
    # SQL APIs
    execute_sql_api,
    get_query_history_api
)

# Re-export for backward compatibility
__all__ = [
    'get_columns_api',
    'get_fusion_columns_api', 
    'get_datasource_columns',
    'generate_chart_api',
    'execute_sql_api',
    'get_query_history_api'
]