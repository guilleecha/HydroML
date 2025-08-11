# data_tools/urls.py
from django.urls import path
# Importamos el nuevo módulo de vistas que hemos creado
from .views import visualization_views, preparation_views

app_name = 'data_tools'

urlpatterns = [
    # --- Rutas para el Visor de Datos ---
    path('viewer/<int:pk>/',
         visualization_views.data_viewer_page,
         name='data_viewer_page'),

    path('api/get_data/<int:pk>/',
         visualization_views.get_datasource_json,
         name='get_datasource_json'),

    # --- RUTA NUEVA PARA LA HERRAMIENTA DE PREPARACIÓN ---
    # URL: /tools/preparer/12/
    # Carga la página de la herramienta para preparar el DataSource con ID 12.
    path('preparer/<int:pk>/',
         preparation_views.data_preparer_page,
         name='data_preparer_page'),
]