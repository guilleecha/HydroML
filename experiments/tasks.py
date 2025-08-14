# experiments/tasks.py
from celery import shared_task, chain
from .models import MLExperiment
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_train_test_split_task(experiment_id):
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        # Lógica de división de datos
        logger.info(f"División de datos completada para el experimento {experiment_id}.")
        return experiment_id  # Aseguramos que el ID se pase a la siguiente tarea
    except Exception as e:
        logger.error(f"Error en run_train_test_split_task para {experiment_id}: {e}")
        raise

@shared_task
def run_model_training_task(experiment_id):
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        # Lógica de entrenamiento del modelo
        logger.info(f"Entrenamiento completado para el experimento {experiment_id}.")
        return experiment_id  # Aseguramos que el ID se pase a la siguiente tarea
    except Exception as e:
        logger.error(f"Error en run_model_training_task para {experiment_id}: {e}")
        raise

@shared_task
def run_final_evaluation_task(experiment_id):
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        # Lógica de evaluación final
        logger.info(f"Evaluación final completada para el experimento {experiment_id}.")
        return experiment_id  # Aseguramos que el ID se pase a la siguiente tarea
    except Exception as e:
        logger.error(f"Error en run_final_evaluation_task para {experiment_id}: {e}")
        raise

@shared_task
def set_experiment_status_as_finished(experiment_id):
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = MLExperiment.Status.FINISHED
        experiment.save(update_fields=['status', 'updated_at'])
        logger.info(f"Estado del experimento {experiment_id} actualizado a FINISHED.")
    except MLExperiment.DoesNotExist:
        logger.error(f"El experimento {experiment_id} no existe.")

@shared_task(bind=True)
def run_full_experiment_pipeline_task(self, experiment_id):
    """
    Orquesta la ejecución completa de un experimento de ML.
    """
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        logger.info(f"Iniciando pipeline completo para el experimento: {experiment.name} ({experiment_id})")

        # 1. Marcar el experimento como 'En Ejecución'
        experiment.status = MLExperiment.Status.RUNNING
        experiment.save(update_fields=['status', 'updated_at'])

        # 2. Crear una cadena de tareas secuenciales
        pipeline = chain(
            run_train_test_split_task.s(experiment_id),
            run_model_training_task.s(),
            run_final_evaluation_task.s(),
            set_experiment_status_as_finished.s()
        )
        
        # 3. Ejecutar la cadena de tareas
        pipeline.delay()

    except MLExperiment.DoesNotExist:
        logger.error(f"No se pudo iniciar el pipeline para el experimento {experiment_id} porque no se encontró.")
    except Exception as e:
        logger.error(f"Error inesperado al iniciar el pipeline para el experimento {experiment_id}: {e}")
        # Marcar como error si la configuración inicial falla
        experiment.status = MLExperiment.Status.ERROR
        experiment.save(update_fields=['status', 'updated_at'])
