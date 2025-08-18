"""
Pipeline orchestration tasks for ML experiments.
"""
from celery import shared_task, chain
from experiments.models import MLExperiment
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_full_experiment_pipeline_task(self, experiment_id):
    """
    Orchestrate the complete ML experiment pipeline using Celery task chains.
    
    This is the main orchestration task that coordinates the entire ML experiment
    workflow from data splitting through final evaluation. It integrates with
    MLflow for comprehensive experiment tracking and uses Celery chains to
    ensure proper task sequencing and error handling.
    
    The pipeline consists of four sequential tasks:
    1. Train/test data splitting
    2. Model training with hyperparameters
    3. Model evaluation and metrics calculation
    4. Final status update to FINISHED
    
    The task includes comprehensive MLflow integration for experiment tracking,
    parameter logging, and model registry. Each step in the pipeline is
    tracked and can be monitored through both Django models and MLflow UI.
    
    Args:
        self: Celery task instance (bound task).
        experiment_id (str): UUID of the experiment to execute.
        
    Raises:
        MLExperiment.DoesNotExist: If experiment with given ID doesn't exist.
        Exception: For any pipeline setup errors, with experiment status set to ERROR.
        
    Side Effects:
        - Updates experiment status to RUNNING
        - Creates MLflow experiment and run
        - Stores MLflow run ID in experiment model
        - Logs experiment metadata to MLflow
        - Initiates task chain for sequential execution
        - Updates experiment status to ERROR on failure
        
    Note:
        This task uses Celery's bind=True to access the task instance,
        enabling better error handling and task introspection.
    """
    try:
        import mlflow
        
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = MLExperiment.Status.RUNNING
        experiment.save(update_fields=['status', 'updated_at'])
        logger.info(f"Iniciando pipeline completo para el experimento: {experiment.name} ({experiment_id})")

        # Set MLflow tracking URI
        mlflow.set_tracking_uri("http://mlflow:5000")
        
        # Create or set experiment in MLflow
        mlflow_experiment_name = f"HydroML_Experiment_{experiment_id}"
        try:
            mlflow_experiment = mlflow.get_experiment_by_name(mlflow_experiment_name)
            if mlflow_experiment is None:
                mlflow_experiment_id = mlflow.create_experiment(mlflow_experiment_name)
            else:
                mlflow_experiment_id = mlflow_experiment.experiment_id
        except Exception:
            mlflow_experiment_id = mlflow.create_experiment(mlflow_experiment_name)
        
        mlflow.set_experiment(mlflow_experiment_name)
        
        # Start MLflow run
        with mlflow.start_run() as mlflow_run:
            # Store MLflow run ID in our experiment
            experiment.mlflow_run_id = mlflow_run.info.run_id
            experiment.save(update_fields=['mlflow_run_id', 'updated_at'])
            
            # Log experiment metadata
            mlflow.log_param("experiment_id", experiment_id)
            mlflow.log_param("model_name", experiment.model_name)
            mlflow.log_param("datasource_id", experiment.input_datasource.id)
            mlflow.log_param("target_column", experiment.target_column)
            
            # Log hyperparameters if they exist
            if experiment.hyperparameters:
                for param_name, param_value in experiment.hyperparameters.items():
                    mlflow.log_param(f"hp_{param_name}", param_value)
            
            # Sync tags from Django to MLflow
            try:
                experiment_tags = list(experiment.tags.names())
                if experiment_tags:
                    # Convert tag list to a dictionary for MLflow
                    mlflow_tags = {f"tag_{i}": tag for i, tag in enumerate(experiment_tags)}
                    # Also add a combined tags field
                    mlflow_tags["all_tags"] = ",".join(experiment_tags)
                    mlflow_tags["tag_count"] = str(len(experiment_tags))
                    
                    mlflow.set_tags(mlflow_tags)
                    logger.info(f"Synced {len(experiment_tags)} tags to MLflow for experiment {experiment_id}: {experiment_tags}")
                else:
                    logger.info(f"No tags to sync for experiment {experiment_id}")
            except Exception as tag_error:
                logger.warning(f"Could not sync tags to MLflow for experiment {experiment_id}: {tag_error}")
            
            logger.info(f"Created MLflow run {mlflow_run.info.run_id} for experiment {experiment_id}")

        # Choose pipeline based on validation strategy
        validation_strategy = getattr(experiment, 'validation_strategy', 'TRAIN_TEST_SPLIT')
        
        # Import tasks from the new modular structure
        from .training_tasks import run_train_test_split_task, run_model_training_task
        from .evaluation_tasks import run_time_series_cross_validation_task, run_final_evaluation_task
        
        if validation_strategy == 'TIME_SERIES_CV':
            # Time series cross-validation pipeline (data prep + cross-validation)
            logger.info(f"Using time series cross-validation pipeline for experiment {experiment_id}")
            pipeline = chain(
                run_train_test_split_task.s(experiment_id),  # Prepare full dataset
                run_time_series_cross_validation_task.s(),   # Perform CV and complete analysis
            )
        else:
            # Traditional train/test split pipeline
            logger.info(f"Using traditional train/test split pipeline for experiment {experiment_id}")
            pipeline = chain(
                run_train_test_split_task.s(experiment_id),
                run_model_training_task.s(),
                run_final_evaluation_task.s(),
                set_experiment_status_as_finished.s()
            )
        
        # Execute the chain asynchronously
        pipeline.delay()

    except MLExperiment.DoesNotExist:
        logger.error(f"No se pudo iniciar el pipeline para el experimento {experiment_id} porque no se encontró.")
    except Exception as e:
        logger.error(f"Error inesperado al iniciar el pipeline para el experimento {experiment_id}: {e}")
        # Mark as error if initial setup fails
        try:
            experiment = MLExperiment.objects.get(id=experiment_id)
            experiment.status = MLExperiment.Status.ERROR
            experiment.save(update_fields=['status', 'updated_at'])
        except Exception:
            pass


@shared_task
def set_experiment_status_as_finished(experiment_id):
    """
    Final task to mark an experiment as finished.
    
    This task is used at the end of successful pipeline chains to ensure
    the experiment status is properly set to FINISHED after all other
    tasks have completed successfully.
    
    Args:
        experiment_id (str): UUID of the experiment to mark as finished.
        
    Returns:
        str: The experiment ID confirming completion.
    """
    try:
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = MLExperiment.Status.FINISHED
        experiment.save(update_fields=['status', 'updated_at'])
        
        logger.info(f"Experiment {experiment_id} marked as FINISHED")
        print(f"Experiment {experiment_id} pipeline completed successfully")
        
        return experiment_id
        
    except MLExperiment.DoesNotExist:
        logger.error(f"Could not mark experiment {experiment_id} as finished - not found")
        raise
    except Exception as e:
        logger.error(f"Error marking experiment {experiment_id} as finished: {e}")
        raise
