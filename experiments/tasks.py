# experiments/tasks.py
from celery import shared_task
from .models import MLExperiment
from . import services
from .services import perform_train_test_split
from .models import MLExperiment

@shared_task
def run_train_test_split_task(experiment_id):
    """
    Tarea de Celery para realizar la división de datos.
    """
    experiment = MLExperiment.objects.get(id=experiment_id)
    try:
        experiment.status = 'SPLITTING'
        experiment.save(update_fields=['status'])

        # El servicio ahora contiene la lógica condicional
        perform_train_test_split(experiment)

        # El estado final es 'SPLIT', independientemente de la estrategia
        experiment.status = 'SPLIT'
        experiment.save(update_fields=['status'])
    except Exception as e:
        experiment.status = 'FAILED'
        experiment.results['error_message'] = str(e)
        experiment.save(update_fields=['status', 'results'])
        raise e

@shared_task
def run_model_training_task(experiment_id):
    """
    Tarea de Celery para ejecutar el servicio de entrenamiento y validación de modelos.
    """
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = 'TRAINING'
        experiment.save()

        # Llamar al servicio de entrenamiento
        training_results = services.perform_model_training_and_validation(experiment)

        # Guardar resultados y actualizar estado
        if experiment.results is None:
            experiment.results = {}
        experiment.results.update(training_results)
        # El modelo ha sido validado y está listo para la evaluación final.
        experiment.status = 'VALIDATED'
        experiment.save()

        return f"Entrenamiento completado para el experimento {experiment.name}."

    except MLExperiment.DoesNotExist:
        return f"Error: Experimento con id {experiment_id} no encontrado."
    except Exception as e:
        if 'experiment' in locals() and isinstance(experiment, MLExperiment):
            experiment.status = 'FAILED'
            if experiment.results is None:
                experiment.results = {}
            experiment.results['error'] = str(e)
            experiment.save()
        return f"Error durante el entrenamiento del modelo: {str(e)}"

@shared_task
def run_final_evaluation_task(experiment_id):
    """
    Tarea de Celery para ejecutar el servicio de evaluación final del modelo.
    """
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = 'EVALUATING'
        experiment.save()

        # Llamar al servicio de evaluación final
        evaluation_results = services.perform_final_evaluation(experiment)

        # Actualizar resultados y estado final
        if experiment.results is None:
            experiment.results = {}
        experiment.results.update(evaluation_results) 
        experiment.status = 'COMPLETED'  # El experimento ha finalizado con éxito
        experiment.save()

        return f"Evaluación final completada para el experimento {experiment.name}."

    except MLExperiment.DoesNotExist:
        return f"Error: Experimento con id {experiment_id} no encontrado."
    except Exception as e:
        if 'experiment' in locals() and isinstance(experiment, MLExperiment):
            experiment.status = 'FAILED'
            if experiment.results is None:
                experiment.results = {}
            experiment.results['error'] = str(e)
            experiment.save()
        return f"Error durante la evaluación final: {str(e)}"



@shared_task
def run_feature_importance_task(experiment_id):
    """
    Tarea de Celery para calcular la importancia de las variables.
    """
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = 'ANALYZING'
        experiment.save()

        # Calcular la importancia de las variables
        feature_importance = calculate_feature_importance(experiment)

        # Guardar los resultados
        experiment.results['feature_importance'] = feature_importance
        experiment.status = 'ANALYZED'
        experiment.save()
    except Exception as e:
        experiment.status = 'FAILED'
        experiment.save()
        sentry_sdk.capture_exception(e)  # Registrar el error en Sentry
        raise e
