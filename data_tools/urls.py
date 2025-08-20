# data_tools/urls.py
from django.urls import path
# Importamos todos nuestros módulos de vistas
from .views import visualization_views, fusion_views
from .views.preparation_controller import data_preparer_page
from .views.api.pagination_api import data_studio_pagination_api
from .views.feature_engineering_views import feature_engineering_page
from .views.missing_data_views import run_deep_missing_analysis_api, missing_data_results_page
# Import refactored API views
from .views.api import (
    get_columns_api, get_fusion_columns_api, generate_chart_api,
    execute_sql_api, get_query_history_api, get_datasource_columns
)
from .views.api.column_flags_api import get_column_flags_api
# Import new session and transformation API views
from .views.api.session_api_views import (
    initialize_session, get_session_status, undo_operation, redo_operation,
    clear_session, save_as_new_datasource
)
from .views.api.transformation_api_views import (
    apply_missing_data_imputation, apply_feature_encoding, apply_feature_scaling,
    apply_outlier_treatment, apply_feature_engineering, apply_column_operations
)
# Import NaN cleaning API views
from .views.api.nan_cleaning_api import QuickNaNCleaningAPIView, NaNAnalysisAPIView
# Import Export API views
from .views.api.export_api_views import ExportJobAPIView, ExportJobActionAPIView, ExportTemplateAPIView

app_name = 'data_tools'

urlpatterns = [
    # --- Ruta para Data Studio (anteriormente Data Preparer) ---
    path('studio/<uuid:pk>/',
         data_preparer_page,
         name='data_studio_page'),

    # --- Data Studio Pagination API ---
    path('api/studio/<uuid:pk>/data/',
         data_studio_pagination_api,
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

    # Column flags API for ML validation
    path('api/column-flags/<uuid:datasource_id>/',
         get_column_flags_api,
         name='get_column_flags_api'),

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

    # --- Data Studio Session Management API ---
    path('api/studio/<uuid:datasource_id>/session/initialize/',
         initialize_session,
         name='initialize_session'),

    path('api/studio/<uuid:datasource_id>/session/status/',
         get_session_status,
         name='get_session_status'),

    path('api/studio/<uuid:datasource_id>/session/undo/',
         undo_operation,
         name='undo_operation'),

    path('api/studio/<uuid:datasource_id>/session/redo/',
         redo_operation,
         name='redo_operation'),

    path('api/studio/<uuid:datasource_id>/session/clear/',
         clear_session,
         name='clear_session'),

    path('api/studio/<uuid:datasource_id>/session/save/',
         save_as_new_datasource,
         name='save_as_new_datasource'),

    # --- Data Studio Transformation API ---
    path('api/studio/<uuid:datasource_id>/transform/imputation/',
         apply_missing_data_imputation,
         name='apply_missing_data_imputation'),

    path('api/studio/<uuid:datasource_id>/transform/encoding/',
         apply_feature_encoding,
         name='apply_feature_encoding'),

    path('api/studio/<uuid:datasource_id>/transform/scaling/',
         apply_feature_scaling,
         name='apply_feature_scaling'),

    path('api/studio/<uuid:datasource_id>/transform/outliers/',
         apply_outlier_treatment,
         name='apply_outlier_treatment'),

    path('api/studio/<uuid:datasource_id>/transform/engineering/',
         apply_feature_engineering,
         name='apply_feature_engineering'),

    path('api/studio/<uuid:datasource_id>/transform/columns/',
         apply_column_operations,
         name='apply_column_operations'),

    # --- NaN Cleaning API ---
    path('api/studio/<uuid:datasource_id>/nan/quick-clean/',
         QuickNaNCleaningAPIView.as_view(),
         name='quick_nan_cleaning'),

    path('api/studio/<uuid:datasource_id>/nan/analysis/',
         NaNAnalysisAPIView.as_view(),
         name='nan_analysis'),
    
    # --- Export API ---
    # Export Jobs API endpoints
    path('api/v1/exports/',
         ExportJobAPIView.as_view(),
         name='export_jobs_api'),
    
    path('api/v1/exports/<uuid:pk>/',
         ExportJobAPIView.as_view(),
         name='export_job_detail_api'),
    
    # Export Job Actions
    path('api/v1/exports/<uuid:pk>/cancel/',
         ExportJobActionAPIView.as_view(),
         {'action': 'cancel'},
         name='export_job_cancel_api'),
    
    path('api/v1/exports/<uuid:pk>/download/',
         ExportJobActionAPIView.as_view(),
         {'action': 'download'},
         name='export_job_download_api'),
    
    path('api/v1/exports/<uuid:pk>/retry/',
         ExportJobActionAPIView.as_view(),
         {'action': 'retry'},
         name='export_job_retry_api'),
    
    # Export Templates API endpoints
    path('api/v1/export-templates/',
         ExportTemplateAPIView.as_view(),
         name='export_templates_api'),
    
    path('api/v1/export-templates/<uuid:pk>/',
         ExportTemplateAPIView.as_view(),
         name='export_template_detail_api'),
]
