from django.urls import path
from . import views
from .views import ExperimentDeleteView, ExperimentUpdateView


app_name = 'projects'

urlpatterns = [
    # URL para la lista de proyectos (página principal)
    path('', views.project_list, name='project_list'),

    # URL para crear un proyecto
    path('project/new/', views.create_project, name='create_project'),

    # URL para el detalle de un proyecto específico
    path('project/<uuid:project_id>/', views.project_detail, name='project_detail'),

    # URL para la subida de archivos (ya la teníamos)
    path('project/<uuid:project_id>/upload/', views.upload_datasource, name='upload_datasource'),

    path('project/<uuid:project_id>/experiment/new/', views.create_experiment, name='create_experiment'),

    path('experiment/<uuid:pk>/', views.experiment_detail, name='experiment_detail'),

    path('experiment/<uuid:pk>/edit/', ExperimentUpdateView.as_view(), name='update_experiment'),

    path('experiment/<uuid:pk>/delete/', ExperimentDeleteView.as_view(), name='delete_experiment'),
]