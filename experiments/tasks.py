# experiments/tasks.py
from celery import shared_task
from .models import MLExperiment
from . import services

@shared_task
def run_train_test_split_task(experiment_id):
    """
    Celery task to call the data splitting service.
    """
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = 'PROCESSING'
        experiment.save()

        # The task passes the heavy lifting to the service
        success_message = services.perform_train_test_split(experiment)

        experiment.status = 'PREPARED'
        experiment.save()
        return success_message

    except MLExperiment.DoesNotExist:
        # Handle the case where the experiment doesn't exist
        return f"Error: Experiment with id {experiment_id} not found."
    except Exception as e:
        # The task manages failures
        if 'experiment' in locals() and isinstance(experiment, MLExperiment):
            experiment.status = 'FAILED'
            experiment.save()
        return f"Error during splitting: {str(e)}"

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
        experiment.status = 'COMPLETED'
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
