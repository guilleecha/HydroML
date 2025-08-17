# connectors/urls.py

from django.urls import path
from .views import (
    # Database Connection CRUD
    DatabaseConnectionListView,
    DatabaseConnectionCreateView,
    DatabaseConnectionUpdateView,
    DatabaseConnectionDeleteView,
    database_connection_test_view,
    
    # Data Import Views
    DatabaseImportSelectConnectionView,
    DatabaseImportQueryView,
    get_database_tables_view,
    get_table_columns_view,
    preview_query_view
)

app_name = 'connectors'

urlpatterns = [
    # Database Connections CRUD
    path('', DatabaseConnectionListView.as_view(), name='database_connections'),
    path('create/', DatabaseConnectionCreateView.as_view(), name='database_connection_create'),
    path('<uuid:pk>/edit/', DatabaseConnectionUpdateView.as_view(), name='database_connection_edit'),
    path('<uuid:pk>/delete/', DatabaseConnectionDeleteView.as_view(), name='database_connection_delete'),
    
    # Database Connection AJAX endpoints
    path('test/', database_connection_test_view, name='database_connection_test'),
    
    # Data Import URLs
    path('import/', DatabaseImportSelectConnectionView.as_view(), name='import_select_connection'),
    path('import/project/<uuid:project_id>/', DatabaseImportSelectConnectionView.as_view(), name='import_select_connection_project'),
    path('import/<uuid:connection_id>/', DatabaseImportQueryView.as_view(), name='import_query'),
    path('import/<uuid:connection_id>/project/<uuid:project_id>/', DatabaseImportQueryView.as_view(), name='import_query_project'),
    
    # Data Import AJAX endpoints
    path('api/tables/', get_database_tables_view, name='api_get_tables'),
    path('api/columns/', get_table_columns_view, name='api_get_columns'),
    path('api/preview/', preview_query_view, name='api_preview_query'),
    
    # Data Sources URLs
    path('data-sources/', DatabaseConnectionListView.as_view(), name='data_source_list'),
]