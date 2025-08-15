# data_tools/urls.py
from django.urls import path
# Importamos todos nuestros módulos de vistas
from .views import visualization_views, preparation_views, fusion_views, api_views
from .views.feature_engineering_views import feature_engineering_page
from .views.api_views import get_datasource_columns

app_name = 'data_tools'

urlpatterns = [
    # --- Rutas para el Visor de Datos ---
    path('viewer/<uuid:pk>/',
         visualization_views.data_viewer_page,
         name='data_viewer_page'),

    path('api/get_data/<uuid:pk>/',
         visualization_views.get_datasource_json,
         name='get_datasource_json'),

    # --- Ruta para la Herramienta de Preparación ---
    path('preparer/<uuid:pk>/',
         preparation_views.data_preparer_page,
         name='data_preparer_page'),

    # --- RUTA NUEVA PARA LA HERRAMIENTA DE FUSIÓN ---
    path('fusion/for-project/<uuid:project_id>/',
         fusion_views.data_fusion_page,
         name='data_fusion_page'),

    # --- API Endpoints ---
    path('api/get-columns/<uuid:datasource_id>/',
         api_views.get_columns_api,
         name='get_columns_api'),

    path(
        "api/datasource-columns/<uuid:datasource_id>/",
        get_datasource_columns,
        name="get_datasource_columns"
    ),

    # --- Ruta para la Ingeniería de Características ---
    path("feature-engineering/<uuid:datasource_id>/",
         feature_engineering_page,
         name="feature_engineering_page"
         ),

    path('datasource/<uuid:datasource_id>/feature-engineering/', feature_engineering_page, name='feature_engineering'),
]
