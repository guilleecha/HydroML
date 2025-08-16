# experiments/urls.py
from django.urls import path
from .views import experiment_management_views, experiment_results_views, api_views, suite_views

app_name = 'experiments'

urlpatterns = [
    # --- Public Experiments List ---
    path('public/', experiment_management_views.public_experiment_list_view, name='public_experiment_list'),
    # --- Vistas de Gestión ---
    path('create/for-project/<uuid:project_id>/',
         experiment_management_views.ml_experiment_create,
         name='ml_experiment_create'),
    
    # Partial view for slide-over panel
    path('ml-experiment-form-partial/',
         experiment_management_views.ml_experiment_form_partial,
         name='ml_experiment_form_partial'),
    
    path('<uuid:pk>/update/',
         experiment_management_views.MLExperimentUpdateView.as_view(),
         name='ml_experiment_update'),
    
    path('<uuid:pk>/publish/',
         experiment_management_views.publish_experiment,
         name='ml_experiment_publish'),
    
    path('<uuid:pk>/fork/',
         experiment_management_views.fork_experiment,
         name='ml_experiment_fork'),
    
    path('<uuid:pk>/delete/',
         experiment_management_views.MLExperimentDeleteView.as_view(),
         name='ml_experiment_delete'),

    # --- Vistas de Resultados y Disparadores de Tareas ---
    path('<uuid:pk>/',
         experiment_results_views.ml_experiment_detail,
         name='ml_experiment_detail'),
    
    # Report views - HTML and PDF
    path('<uuid:pk>/report/',
         experiment_results_views.experiment_report_view,
         name='experiment_report_view'),
    
    path('<uuid:pk>/report/pdf/',
         experiment_results_views.experiment_report_pdf,
         name='experiment_report_pdf'),
    
    # Run experiment URL (new consistent pattern)
    path('<uuid:pk>/run/',
         experiment_management_views.run_experiment_view,
         name='run_experiment'),
    
    # Nueva URL para el pipeline completo (legacy)
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
    path('projects/<uuid:project_pk>/suites/create/',
         suite_views.ExperimentSuiteCreateView.as_view(),
         name='suite_create'),
    
    path('suites/<uuid:pk>/',
         suite_views.ExperimentSuiteDetailView.as_view(),
         name='suite_detail'),
    
    path('suites/<uuid:pk>/run/',
         suite_views.run_experiment_suite,
         name='suite_run'),
    
    path('suite/create/ablation/for-project/<uuid:project_id>/',
        suite_views.ablation_suite_create,
        name='ablation_suite_create'),
]