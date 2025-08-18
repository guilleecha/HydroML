# data_tools/urls.py
from django.urls import path
# Importamos todos nuestros módulos de vistas
from .views import visualization_views, preparation_views, fusion_views
from .views.feature_engineering_views import feature_engineering_page
from .views.missing_data_views import run_deep_missing_analysis_api, missing_data_results_page
# Import refactored API views
from .views.api import (
    get_columns_api, get_fusion_columns_api, generate_chart_api,
    execute_sql_api, get_query_history_api, get_datasource_columns
)

app_name = 'data_tools'

urlpatterns = [
    # --- Ruta para Data Studio (anteriormente Data Preparer) ---
    path('studio/<uuid:pk>/',
         preparation_views.data_preparer_page,
         name='data_studio_page'),

    # --- Data Studio Pagination API ---
    path('api/studio/<uuid:pk>/data/',
         preparation_views.data_studio_pagination_api,
         name='data_studio_pagination_api'),

    path('api/get_data/<uuid:pk>/',
         visualization_views.get_datasource_json,
         name='get_datasource_json'),

    # --- RUTA NUEVA PARA LA HERRAMIENTA DE FUSIÓN ---
    path('tools/fuse-datasources/for-project/<uuid:pk>/',
         fusion_views.data_fusion_page,
         name='data_fusion'),

    # --- API Endpoints ---
    path('api/get-columns/<uuid:datasource_id>/',
         get_columns_api,
         name='get_columns_api'),

    path(
        "api/datasource-columns/<uuid:datasource_id>/",
        get_datasource_columns,
        name="get_datasource_columns"
    ),

    path('api/get-fusion-columns/',
         get_fusion_columns_api,
         name='get_fusion_columns_api'),

    # New Chart Generation API
    path('api/generate-chart/',
         generate_chart_api,
         name='generate_chart_api'),

    # SQL Execution API
    path('api/execute-sql/',
         execute_sql_api,
         name='execute_sql_api'),

    # Query History API
    path('api/query-history/',
         get_query_history_api,
         name='get_query_history_api'),

    # --- Ruta para la Ingeniería de Características ---
    path("feature-engineering/<uuid:datasource_id>/",
         feature_engineering_page,
         name="feature_engineering_page"
         ),

    path('datasource/<uuid:datasource_id>/feature-engineering/', feature_engineering_page, name='feature_engineering'),

    # --- Missing Data Toolkit URLs ---
    path('run-deep-missing-analysis/',
         run_deep_missing_analysis_api,
         name='run_deep_missing_analysis_api'),

    path('missing-data-results/<str:task_id>/',
         missing_data_results_page,
         name='missing_data_results_page'),
]
