# En core/urls.py
from django.urls import path
from . import views
from .views import ProjectListView, DatasetUploadView, PrepareDataView
urlpatterns = [
    # Apunta a la nueva clase ProjectListView
    path('', ProjectListView.as_view(), name='project_list'),

    # Apunta a la nueva clase DatasetUploadView
    path('project/<int:project_id>/upload/', DatasetUploadView.as_view(), name='dataset_upload'),

    # Esta ya estaba refactorizada
    path('prepare/', PrepareDataView.as_view(), name='prepare_data'),
]