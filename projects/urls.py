# projects/urls.py

from django.urls import path
from . import views
from .views import DataSourceDeleteView  # Importamos la vista de borrado

# Importamos las vistas de la app 'experiments' con un alias para evitar confusiones
from experiments import views as experiment_views

app_name = 'projects'

urlpatterns = [
    # URLs para la gestión de Proyectos
    path('', views.project_list, name='project_list'),
    path('project/new/', views.create_project, name='create_project'),
    path('project/<uuid:project_id>/', views.project_detail, name='project_detail'),

    # URLs para la gestión de DataSources (anidadas bajo un proyecto)
    path('project/<uuid:project_id>/upload/', views.upload_datasource, name='upload_datasource'),
    path('datasource/<uuid:pk>/delete/', DataSourceDeleteView.as_view(), name='delete_datasource'),

    # URLs para las herramientas que operan sobre DataSources
    path('datasource/<uuid:pk>/view/', views.data_viewer_page, name='view_datasource_page'),
    path('datasource/<uuid:pk>/prepare/', views.prepare_datasource_view, name='prepare_data'),

    # URLs para las APIs
    path('api/datasource/<uuid:pk>/', views.view_datasource, name='api_view_datasource'),

    # --- URLs QUE APUNTAN A VISTAS EN LA APP 'EXPERIMENTS' ---
    # La URL para crear un experimento de FUSIÓN
    path('project/<uuid:project_id>/experiment/new/', experiment_views.create_experiment, name='create_experiment'),

    # LA URL QUE ESTÁ CAUSANDO EL ERROR:
    # La URL para crear un experimento de MACHINE LEARNING
    path('project/<uuid:project_id>/ml-experiment/new/', experiment_views.create_ml_experiment,
         name='create_ml_experiment'),
]