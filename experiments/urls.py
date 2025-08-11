# experiments/urls.py
from django.urls import path
# Importamos directamente desde los nuevos archivos de vistas
from .views import experiment_management_views, experiment_results_views

# app_name nos permite usar espacios de nombres en las plantillas (ej: 'experiments:ml_experiment_detail')
app_name = 'experiments'

urlpatterns = [
    # --- Rutas para la GESTIÓN de experimentos (Crear, Actualizar, Borrar) ---
    # Ejemplo: /experiments/create/for-project/5/
    path('create/for-project/<int:project_id>/',
         experiment_management_views.ml_experiment_create,
         name='ml_experiment_create'),

    # Ejemplo: /experiments/12/update/
    path('<int:pk>/update/',
         experiment_management_views.MLExperimentUpdateView.as_view(),
         name='ml_experiment_update'),

    # Ejemplo: /experiments/12/delete/
    path('<int:pk>/delete/',
         experiment_management_views.MLExperimentDeleteView.as_view(),
         name='ml_experiment_delete'),

    # --- Ruta para los RESULTADOS (Ver detalle) ---
    # Por ahora, apunta a una vista de detalle simple que crearemos después.
    # Ejemplo: /experiments/12/
    path('<int:pk>/',
         experiment_results_views.ml_experiment_detail,
         # Asumimos que esta vista estará en 'experiment_results_views.py'
         name='ml_experiment_detail'),
]