# experiments/urls.py
from django.urls import path
from .views import experiment_management_views, experiment_results_views, api_views
from experiments.views.experiment_management_views import trigger_feature_importance_task

app_name = 'experiments'

urlpatterns = [
    # --- Vistas de Gestión ---
    # La creación sigue dependiendo de un project_id que sí es UUID
    path('create/for-project/<uuid:project_id>/',
         experiment_management_views.ml_experiment_create,
         name='ml_experiment_create'),
    
    # CAMBIO: La clave primaria (pk) de un experimento es un entero (int)
    path('<int:pk>/update/',
         experiment_management_views.MLExperimentUpdateView.as_view(),
         name='ml_experiment_update'),
    
    # CAMBIO: La clave primaria (pk) de un experimento es un entero (int)
    path('<int:pk>/delete/',
         experiment_management_views.MLExperimentDeleteView.as_view(),
         name='ml_experiment_delete'),

    # --- Vistas de Resultados y Disparadores de Tareas ---
    # CAMBIO: La clave primaria (pk) de un experimento es un entero (int)
    path('<int:pk>/',
         experiment_results_views.ml_experiment_detail,
         name='ml_experiment_detail'),
    
    # CAMBIO: El id de un experimento es un entero (int)
    path('<int:experiment_id>/trigger-split/',
         experiment_management_views.trigger_split_task,
         name='trigger_split_task'),
    
    # CAMBIO: El id de un experimento es un entero (int)
    path('<int:experiment_id>/trigger-training/',
         experiment_management_views.trigger_training_task,
         name='trigger_training_task'),

    # CAMBIO: El id de un experimento es un entero (int)
    path('<int:experiment_id>/trigger-final-evaluation/',
         experiment_management_views.trigger_final_evaluation_task,
         name='trigger_final_evaluation_task'),
    
    # CAMBIO: El id de un experimento es un entero (int)
    path('<int:experiment_id>/trigger-importance/',
         trigger_feature_importance_task,
         name='trigger_feature_importance_task'),

    # --- API Endpoints ---
    # CAMBIO: El id de un experimento es un entero (int)
    path('api/status/<int:experiment_id>/',
         api_views.get_experiment_status,
         name='get_experiment_status'),
]