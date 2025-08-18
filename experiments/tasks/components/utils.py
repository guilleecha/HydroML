"""
Utility functions for experiment tasks.
"""
import logging

logger = logging.getLogger(__name__)


def extract_optimization_metric(experiment):
    """
    Extract optimization metric from experiment results.
    """
    try:
        if hasattr(experiment, 'results') and experiment.results:
            results = experiment.results
            if isinstance(results, dict):
                # Look for common metric names
                for metric in ['r2_score', 'accuracy', 'f1_score', 'mse']:
                    if metric in results:
                        return results[metric]
                # If no standard metric found, return the first numeric value
                for key, value in results.items():
                    if isinstance(value, (int, float)):
                        return value
        return 0.0
    except Exception as e:
        logger.error(f"Error extracting optimization metric: {e}")
        return 0.0


def create_child_experiment_for_optuna(parent_suite, trial, hyperparams):
    """
    Create a child experiment for Optuna optimization.
    """
    from experiments.models import MLExperiment
    
    try:
        child_experiment = MLExperiment.objects.create(
            name=f"{parent_suite.name} - Trial {trial.number}",
            description=f"Auto-generated experiment for Optuna trial {trial.number}",
            project=parent_suite.project,
            datasource=parent_suite.base_datasource,
            target_column=parent_suite.target_column,
            model_type=parent_suite.model_type,
            hyperparameters=hyperparams,
            validation_strategy=parent_suite.validation_strategy,
            parent_suite=parent_suite,
            status=MLExperiment.ExperimentStatus.DRAFT
        )
        return child_experiment
    except Exception as e:
        logger.error(f"Error creating child experiment: {e}")
        return None


def run_single_experiment_sync(experiment):
    """
    Run a single experiment synchronously.
    """
    try:
        # Import here to avoid circular imports
        from experiments.tasks.experiment_tasks import run_full_experiment_pipeline_task
        
        # Execute the experiment task
        result = run_full_experiment_pipeline_task.apply(args=[experiment.id])
        return result.get() if result else None
    except Exception as e:
        logger.error(f"Error running single experiment: {e}")
        return None
