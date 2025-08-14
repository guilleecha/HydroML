# experiments/urls.py
from django.urls import path
from .views import experiment_management_views, experiment_results_views, api_views, ablation_suite_create

app_name = 'experiments'

urlpatterns = [
    # --- Vistas de Gestión ---
    path('create/for-project/<uuid:project_id>/',
         experiment_management_views.ml_experiment_create,
         name='ml_experiment_create'),
    
    path('<uuid:pk>/update/',
         experiment_management_views.MLExperimentUpdateView.as_view(),
         name='ml_experiment_update'),
    
    path('<uuid:pk>/publish/',
         experiment_management_views.publish_experiment,
         name='ml_experiment_publish'),
    
    path('<uuid:pk>/delete/',
         experiment_management_views.MLExperimentDeleteView.as_view(),
         name='ml_experiment_delete'),

    # --- Vistas de Resultados y Disparadores de Tareas ---
    path('<uuid:pk>/',
         experiment_results_views.ml_experiment_detail,
         name='ml_experiment_detail'),
    
    # Nueva URL para el pipeline completo
    path('<uuid:experiment_id>/trigger-full-pipeline/',
         experiment_management_views.trigger_full_experiment_task,
         name='trigger_full_experiment_task'),
    
    path('<uuid:experiment_id>/trigger-importance/',
         experiment_management_views.trigger_feature_importance_task,
         name='trigger_feature_importance_task'),

    # --- API Endpoints ---
    path('api/status/<uuid:experiment_id>/',
         api_views.get_experiment_status,
         name='get_experiment_status'),

    # --- Rutas para Suites de Experimentos ---
    path('suite/create/ablation/for-project/<uuid:project_id>/',
        ablation_suite_create,
        name='ablation_suite_create'),
]