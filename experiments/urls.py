# experiments/urls.py
from django.urls import path
from .views import experiment_management_views, experiment_results_views

app_name = 'experiments'

urlpatterns = [
    # CAMBIO AQUÍ: de <int:project_id> a <uuid:project_id>
    path('create/for-project/<uuid:project_id>/',
         experiment_management_views.ml_experiment_create,
         name='ml_experiment_create'),

    # CAMBIO AQUÍ: de <int:pk> a <uuid:pk>
    path('<uuid:pk>/update/',
         experiment_management_views.MLExperimentUpdateView.as_view(),
         name='ml_experiment_update'),

    # CAMBIO AQUÍ: de <int:pk> a <uuid:pk>
    path('<uuid:pk>/delete/',
         experiment_management_views.MLExperimentDeleteView.as_view(),
         name='ml_experiment_delete'),

    # CAMBIO AQUÍ: de <int:pk> a <uuid:pk>
    path('<uuid:pk>/',
         experiment_results_views.ml_experiment_detail,
         name='ml_experiment_detail'),

    path('<uuid:experiment_id>/trigger-split/',
         experiment_management_views.trigger_split_task,
         name='trigger_split_task'),

    path('<uuid:experiment_id>/trigger-training/',
         experiment_management_views.trigger_training_task,
         name='trigger_training_task'),

    path('<uuid:experiment_id>/trigger-final-evaluation/',
         experiment_management_views.trigger_final_evaluation_task,
         name='trigger_final_evaluation_task'),
]