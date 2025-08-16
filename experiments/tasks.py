"""
Main entry point for HydroML experiment tasks.

This module serves as the main entry point that imports all Celery tasks
from the organized task modules, ensuring they are discoverable by Celery
while maintaining a clean package structure.

The tasks are organized into logical modules:
- experiment_tasks: Individual ML experiment pipeline tasks
- suite_tasks: Experiment suite orchestration and optimization tasks
- utils: Shared helper functions and utilities
"""

# Import all tasks from organized modules to make them discoverable by Celery
from .tasks.experiment_tasks import (
    run_train_test_split_task,
    run_model_training_task,
    run_final_evaluation_task,
    set_experiment_status_as_finished,
    run_full_experiment_pipeline_task
)

from .tasks.suite_tasks import (
    run_experiment_suite_task
)

# Import utility functions for backwards compatibility
from .tasks.utils import (
    generate_shap_plots,
    extract_optimization_metric,
    create_child_experiment_for_optuna,
    run_single_experiment_sync
)

# Ensure all tasks are available for Celery autodiscovery
__all__ = [
    # Individual experiment tasks
    'run_train_test_split_task',
    'run_model_training_task',
    'run_final_evaluation_task',
    'set_experiment_status_as_finished',
    'run_full_experiment_pipeline_task',
    
    # Suite orchestration tasks
    'run_experiment_suite_task',
    
    # Utility functions
    'generate_shap_plots',
    'extract_optimization_metric',
    'create_child_experiment_for_optuna',
    'run_single_experiment_sync'
]
