# data_tools/urls.py
from django.urls import path
# Importamos todos nuestros módulos de vistas
from .views import visualization_views, preparation_views, fusion_views, api_views
from .views.feature_engineering_views import feature_engineering_page
from .views.api_views import get_datasource_columns

app_name = 'data_tools'

urlpatterns = [
    # --- Ruta para Data Studio (anteriormente Data Preparer) ---
    path('studio/<uuid:pk>/',
         preparation_views.data_preparer_page,
         name='data_studio_page'),

    path('api/get_data/<uuid:pk>/',
         visualization_views.get_datasource_json,
         name='get_datasource_json'),

    # --- RUTA NUEVA PARA LA HERRAMIENTA DE FUSIÓN ---
    path('tools/fuse-datasources/for-project/<uuid:pk>/',
         fusion_views.data_fusion_page,
         name='data_fusion'),

    # --- API Endpoints ---
    path('api/get-columns/<uuid:datasource_id>/',
         api_views.get_columns_api,
         name='get_columns_api'),

    path(
        "api/datasource-columns/<uuid:datasource_id>/",
        get_datasource_columns,
        name="get_datasource_columns"
    ),

    path('api/get-fusion-columns/',
         api_views.get_fusion_columns_api,
         name='get_fusion_columns_api'),

    # New Chart Generation API
    path('api/generate-chart/',
         api_views.generate_chart_api,
         name='generate_chart_api'),

    # --- Ruta para la Ingeniería de Características ---
    path("feature-engineering/<uuid:datasource_id>/",
         feature_engineering_page,
         name="feature_engineering_page"
         ),

    path('datasource/<uuid:datasource_id>/feature-engineering/', feature_engineering_page, name='feature_engineering'),
]
