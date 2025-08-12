# experiments/urls.py
from django.urls import path

# Importamos los dos módulos de vistas que hemos creado
from .views import experiment_management_views, experiment_results_views

app_name = 'experiments'

urlpatterns = [
    # --- Rutas para la GESTIÓN de experimentos ---
    path('create/for-project/<int:project_id>/',
         experiment_management_views.ml_experiment_create,
         name='ml_experiment_create'),

    path('<int:pk>/update/',
         experiment_management_views.MLExperimentUpdateView.as_view(),
         name='ml_experiment_update'),

    path('<int:pk>/delete/',
         experiment_management_views.MLExperimentDeleteView.as_view(),
         name='ml_experiment_delete'),

    # --- Ruta para los RESULTADOS (Ver detalle) ---
    # Esta ruta ahora apunta correctamente a la vista en el archivo 'experiment_results_views.py'
    path('<int:pk>/',
         experiment_results_views.ml_experiment_detail,
         name='ml_experiment_detail'),
]