# experiments/urls.py

from django.urls import path
from .views import experiment_detail, ExperimentUpdateView, ExperimentDeleteView, get_common_columns
from . import views

app_name = 'experiments'

urlpatterns = [
    path('api/get-common-columns/', views.get_common_columns, name='api_get_common_columns'),
    path('<uuid:pk>/', experiment_detail, name='experiment_detail'),
    path('<uuid:pk>/edit/', ExperimentUpdateView.as_view(), name='update_experiment'),
    path('<uuid:pk>/delete/', ExperimentDeleteView.as_view(), name='delete_experiment'),
]