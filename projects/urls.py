# projects/urls.py
from django.urls import path
from .views import project_views, datasource_views

app_name = 'projects'

urlpatterns = [
    # Ruta para la lista de proyectos
    path('', project_views.project_list, name='project_list'),

    # --- ESTA ES LA LÍNEA CRÍTICA QUE RESUELVE EL ERROR ---
    # Ruta para la página de creación de un nuevo proyecto
    path('create/', project_views.project_create, name='project_create'),

    # Ruta para el detalle de un proyecto
    path('<int:pk>/', project_views.project_detail, name='project_detail'),

    # Rutas para DataSource
    path('<int:project_id>/upload/', datasource_views.datasource_upload, name='datasource_upload'),
    path('datasource/<int:pk>/delete/',
         datasource_views.DataSourceDeleteView.as_view(),
         name='datasource_delete'),
]