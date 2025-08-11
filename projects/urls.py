# projects/urls.py
from django.urls import path
# Importamos los módulos de vistas que hemos creado
from .views import project_views, datasource_views

# app_name nos permite usar espacios de nombres en las plantillas (ej: 'projects:project_detail')
app_name = 'projects'

urlpatterns = [
    # --- Rutas para la gestión de PROYECTOS ---

    # URL: /projects/
    # Muestra la lista de todos los proyectos del usuario.
    path('', project_views.project_list, name='project_list'),

    # URL: /projects/create/
    # Muestra el formulario para crear un nuevo proyecto.
    path('create/', project_views.project_create, name='project_create'),

    # URL: /projects/5/
    # Muestra la página de detalle de un proyecto específico (el 5 en este caso).
    path('<int:pk>/', project_views.project_detail, name='project_detail'),

    # --- Rutas para la gestión de FUENTES DE DATOS (DataSource) ---

    # URL: /projects/5/upload/
    # Muestra el formulario para subir un nuevo archivo al proyecto 5.
    path('<int:project_id>/upload/', datasource_views.datasource_upload, name='datasource_upload'),

    # URL: /projects/datasource/12/delete/
    # Muestra la página de confirmación para eliminar el datasource con ID 12.
    path('datasource/<int:pk>/delete/',
         datasource_views.DataSourceDeleteView.as_view(),
         name='datasource_delete'),
]