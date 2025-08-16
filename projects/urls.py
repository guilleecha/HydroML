# projects/urls.py
from django.urls import path
from .views import project_views, datasource_views

app_name = 'projects'

urlpatterns = [
    path('', project_views.project_list, name='project_list'),
    path('create/', project_views.project_create, name='project_create'),

    # CAMBIO AQUÍ: de <int:pk> a <uuid:pk>
    path('<uuid:pk>/', project_views.project_detail, name='project_detail'),

    # CAMBIO AQUÍ: de <int:project_id> a <uuid:project_id>
    path('<uuid:project_id>/upload/', datasource_views.datasource_upload, name='datasource_upload'),
    
    # Partial form for AJAX loading
    path('datasource/upload-form-partial/', 
         datasource_views.datasource_upload_form_partial, 
         name='datasource_upload_form_partial'),

    # Upload summary page (polls for processing status)
    path('datasource/<uuid:datasource_id>/upload-summary/',
         datasource_views.datasource_upload_summary,
         name='datasource_upload_summary'),

    # DataSource update page
    path('datasource/<uuid:pk>/update/',
         datasource_views.DataSourceUpdateView.as_view(),
         name='datasource_update'),

    # Esta ruta ya debería estar correcta si DataSource usa UUID
    path('datasource/<uuid:pk>/delete/',
         datasource_views.DataSourceDeleteView.as_view(),
         name='datasource_delete'),
]