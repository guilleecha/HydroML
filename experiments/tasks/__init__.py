"""
Celery tasks package for HydroML experiments.

This package contains organized Celery tasks for ML experiment pipeline orchestration.
Tasks are logically separated into different modules for better maintainability.

Modules:
    - experiment_tasks: Individual experiment pipeline tasks
    - suite_tasks: Experiment suite orchestration tasks
    - utils: Helper functions shared across tasks
"""

# Import all tasks so they are discoverable by Celery
from .experiment_tasks import (
    run_train_test_split_task,
    run_model_training_task, 
    run_final_evaluation_task,
    set_experiment_status_as_finished,
    run_full_experiment_pipeline_task
)

from .suite_tasks import (
    run_experiment_suite_task
)

__all__ = [
    'run_train_test_split_task',
    'run_model_training_task',
    'run_final_evaluation_task', 
    'set_experiment_status_as_finished',
    'run_full_experiment_pipeline_task',
    'run_experiment_suite_task'
]
