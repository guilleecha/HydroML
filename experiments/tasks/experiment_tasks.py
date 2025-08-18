"""
Modular Celery tasks for the experiments app.

This module serves as the main entry point for experiment tasks,
importing from specialized components for better maintainability.
"""

# Import tasks from modular components
from .components.training_tasks import run_train_test_split_task, run_model_training_task
from .components.evaluation_tasks import run_time_series_cross_validation_task, run_final_evaluation_task
from .components.pipeline_tasks import run_full_experiment_pipeline_task, set_experiment_status_as_finished
from .components.suite_tasks import run_experiment_suite_task

# Re-export for backward compatibility
__all__ = [
    'run_train_test_split_task',
    'run_model_training_task', 
    'run_time_series_cross_validation_task',
    'run_final_evaluation_task',
    'run_full_experiment_pipeline_task',
    'set_experiment_status_as_finished',
    'run_experiment_suite_task'
]
