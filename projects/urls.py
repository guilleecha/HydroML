# projects/urls.py
from django.urls import path

# --- CAMBIO CLAVE: Importamos directamente desde los archivos ---
from .views import project_views, datasource_views

app_name = 'projects'

urlpatterns = [
    # Rutas que usan vistas de 'project_views.py'
    path('', project_views.project_list, name='project_list'),
    path('create/', project_views.project_create, name='project_create'),
    path('<int:pk>/', project_views.project_detail, name='project_detail'),

    # Rutas que usan vistas de 'datasource_views.py'
    path('<int:project_id>/upload/', datasource_views.datasource_upload, name='datasource_upload'),
    path('datasource/<int:pk>/delete/',
         datasource_views.DataSourceDeleteView.as_view(),
         name='datasource_delete'),
]