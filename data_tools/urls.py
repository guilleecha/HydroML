# data_tools/urls.py
from django.urls import path
# Importamos todos nuestros módulos de vistas
from .views import visualization_views, preparation_views, fusion_views

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
    # URL: /tools/fusion/for-project/e538ce76-.../
    # Carga la página de la herramienta para fusionar datasets del proyecto especificado.
    path('fusion/for-project/<uuid:project_id>/',
         fusion_views.data_fusion_page,
         name='data_fusion_page'),
]