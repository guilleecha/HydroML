"""
Experiment suite orchestration tasks.

This module contains Celery tasks that handle ExperimentSuite execution
including Optuna optimization and grid search strategies.
"""

from celery import shared_task
from experiments.models import ExperimentSuite, MLExperiment
from .utils import (
    extract_optimization_metric,
    create_child_experiment_for_optuna,
    run_single_experiment_sync
)
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_experiment_suite_task(suite_id):
    """
    Execute an ExperimentSuite with support for both grid search and Optuna optimization.
    
    This task orchestrates the execution of a complete experiment suite by checking the
    study_type and routing to the appropriate execution strategy:
    
    - For HYPERPARAMETER_SWEEP: Uses Optuna for intelligent optimization
    - For other study types: Uses traditional grid search approach
    
    Optuna Integration:
    - Creates an Optuna study with appropriate optimization direction
    - Defines an objective function that suggests parameters and runs experiments
    - Collects trial data and parameter importances for visualization
    - Saves optimization results to the suite model
    
    Args:
        suite_id (str): UUID of the ExperimentSuite to execute.
        
    Returns:
        str: Status message indicating completion with experiment count.
        
    Raises:
        ExperimentSuite.DoesNotExist: If suite with given ID doesn't exist.
        Exception: For any processing errors, with suite status set to FAILED.
        
    Side Effects:
        - Updates suite status to RUNNING, then COMPLETED
        - Creates multiple MLExperiment objects as children
        - For Optuna: Saves trial_data and param_importances to suite
        - Launches experiment pipeline tasks for each experiment
        - Updates suite timestamps (started_at, completed_at)
    """
    print(f"Running experiment suite {suite_id}")
    
    try:
        import json
        import itertools
        from django.utils import timezone
        
        # Get the experiment suite
        suite = ExperimentSuite.objects.get(id=suite_id)
        
        # Update status to RUNNING and set started_at
        suite.start_execution()
        logger.info(f"Starting execution of experiment suite: {suite.name} ({suite_id})")
        
        # Check study type and route to appropriate execution strategy
        if suite.study_type == 'HYPERPARAMETER_SWEEP':
            return _run_optuna_optimization_suite(suite)
        else:
            return _run_grid_search_suite(suite)
            
    except ExperimentSuite.DoesNotExist:
        error_msg = f"ExperimentSuite with id {suite_id} not found"
        print(error_msg)
        logger.error(error_msg)
        raise
        
    except Exception as e:
        error_msg = f"Error in experiment suite execution for {suite_id}: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        
        # Mark suite as failed
        try:
            suite = ExperimentSuite.objects.get(id=suite_id)
            suite.fail_execution()
        except:
            pass
        
        raise


def _run_optuna_optimization_suite(suite):
    """
    Execute suite using Optuna for intelligent hyperparameter optimization.
    
    This function:
    1. Creates an Optuna study with appropriate optimization direction
    2. Defines an objective function that runs single experiments
    3. Optimizes using the specified number of trials
    4. Saves trial data and parameter importances
    
    Args:
        suite (ExperimentSuite): The suite to optimize.
        
    Returns:
        str: Status message with optimization results.
    """
    try:
        import optuna
        import optuna.importance
        from django.utils import timezone
        
        print(f"Starting Optuna optimization for suite {suite.id}")
        
        # Determine optimization direction based on metric
        lower_is_better_metrics = ['mse', 'mae', 'rmse', 'mean_squared_error', 'mean_absolute_error']
        is_lower_better = any(metric in suite.optimization_metric.lower() for metric in lower_is_better_metrics)
        direction = 'minimize' if is_lower_better else 'maximize'
        
        # Create Optuna study
        study = optuna.create_study(direction=direction)
        
        # Storage for trial data
        trial_data = []
        
        def objective(trial):
            """
            Optuna objective function that suggests parameters and runs a single experiment.
            
            Args:
                trial: Optuna trial object for parameter suggestion.
                
            Returns:
                float: The optimization metric value for this trial.
            """
            try:
                # Suggest hyperparameters based on search space
                suggested_params = {}
                search_space = suite.search_space
                
                for param_name, param_config in search_space.items():
                    if isinstance(param_config, dict):
                        # Handle structured parameter definition
                        param_type = param_config.get('type', 'float')
                        
                        if param_type == 'int':
                            suggested_params[param_name] = trial.suggest_int(
                                param_name, 
                                param_config['low'], 
                                param_config['high']
                            )
                        elif param_type == 'float':
                            suggested_params[param_name] = trial.suggest_float(
                                param_name, 
                                param_config['low'], 
                                param_config['high']
                            )
                        elif param_type == 'categorical':
                            suggested_params[param_name] = trial.suggest_categorical(
                                param_name, 
                                param_config['choices']
                            )
                    elif isinstance(param_config, list):
                        # Handle simple list of values (categorical)
                        suggested_params[param_name] = trial.suggest_categorical(param_name, param_config)
                
                print(f"Trial {trial.number}: Testing parameters {suggested_params}")
                
                # Create child experiment with suggested parameters
                child_experiment = create_child_experiment_for_optuna(suite, trial.number, suggested_params)
                
                # Run the experiment synchronously 
                experiment_result = run_single_experiment_sync(child_experiment)
                
                # Extract the optimization metric value
                metric_value = extract_optimization_metric(experiment_result, suite.optimization_metric)
                
                # Store trial data for visualization
                trial_data.append({
                    'trial_number': trial.number,
                    'parameters': suggested_params,
                    'value': metric_value,
                    'experiment_id': str(child_experiment.id)
                })
                
                print(f"Trial {trial.number} completed with {suite.optimization_metric}: {metric_value}")
                return metric_value
                
            except Exception as e:
                print(f"Error in trial {trial.number}: {str(e)}")
                # Return worst possible value for failed trials
                return float('inf') if direction == 'minimize' else float('-inf')
        
        # Run optimization with default 50 trials (configurable in future)
        n_trials = 50
        print(f"Starting Optuna optimization with {n_trials} trials")
        study.optimize(objective, n_trials=n_trials)
        
        # Calculate parameter importances
        try:
            param_importances = optuna.importance.get_param_importances(study)
            print(f"Parameter importances: {param_importances}")
        except Exception as e:
            print(f"Could not calculate parameter importances: {e}")
            param_importances = {}
        
        # Save optimization results to suite
        suite.trial_data = trial_data
        suite.param_importances = param_importances
        
        # Save best trial results
        best_trial = study.best_trial
        best_params = best_trial.params if best_trial else {}
        best_value = best_trial.value if best_trial else None
        
        print(f"Optuna optimization completed:")
        print(f"Best value: {best_value}")
        print(f"Best parameters: {best_params}")
        
        # Mark suite as completed
        suite.complete_execution()
        
        completion_message = f"Optuna optimization completed: {len(trial_data)} trials, best {suite.optimization_metric}: {best_value}"
        logger.info(f"Completed Optuna optimization for suite {suite.id}: {completion_message}")
        
        return completion_message
        
    except Exception as e:
        print(f"Error in Optuna optimization: {str(e)}")
        suite.fail_execution()
        raise


def _run_grid_search_suite(suite):
    """
    Execute suite using traditional grid search approach.
    
    This function maintains the original grid search logic for non-HYPERPARAMETER_SWEEP
    study types, generating all parameter combinations and launching experiments.
    
    Args:
        suite (ExperimentSuite): The suite to execute.
        
    Returns:
        str: Status message with experiment count.
    """
    try:
        import itertools
        from .experiment_tasks import run_full_experiment_pipeline_task
        
        # Parse the search space JSON
        search_space = suite.search_space
        if not search_space:
            raise ValueError("Search space is empty or invalid")
        
        # Generate all parameter combinations
        param_names = list(search_space.keys())
        param_values = list(search_space.values())
        
        # Create cartesian product of all parameter values
        combinations = list(itertools.product(*param_values))
        
        print(f"Generated {len(combinations)} parameter combinations from search space")
        logger.info(f"Generated {len(combinations)} parameter combinations for suite {suite.id}")
        
        # Check if we have a base experiment to copy from
        if not suite.base_experiment:
            raise ValueError("No base experiment found for suite")
        
        base_experiment = suite.base_experiment
        child_experiments_created = 0
        
        # Loop through each parameter combination
        for i, combination in enumerate(combinations):
            # Create hyperparameters dict for this combination
            hyperparameters = dict(zip(param_names, combination))
            
            # Create a new child experiment
            child_experiment = MLExperiment(
                # Copy settings from base experiment
                project=base_experiment.project,
                name=f"{suite.name} - Run {i+1}",
                description=f"Child experiment {i+1} of suite '{suite.name}'. Parameters: {hyperparameters}",
                input_datasource=base_experiment.input_datasource,
                target_column=base_experiment.target_column,
                model_name=base_experiment.model_name,
                feature_set=base_experiment.feature_set,
                test_split_size=base_experiment.test_split_size,
                split_random_state=base_experiment.split_random_state,
                split_strategy=base_experiment.split_strategy,
                
                # Set specific parameters for this child
                hyperparameters=hyperparameters,
                suite=suite,  # Link to parent suite
                status=MLExperiment.Status.QUEUED,
                version=1,
                is_public=False
            )
            
            # Save the child experiment
            child_experiment.save()
            child_experiments_created += 1
            
            print(f"Created child experiment {i+1}/{len(combinations)}: {child_experiment.name}")
            
            # Launch the experiment pipeline task
            run_full_experiment_pipeline_task.delay(str(child_experiment.id))
            logger.info(f"Launched pipeline task for child experiment {child_experiment.id}")
        
        # Mark suite as completed
        suite.complete_execution()
        
        completion_message = f"Grid search completed: {child_experiments_created} child experiments created and launched"
        print(completion_message)
        logger.info(f"Completed grid search for suite {suite.id}: {child_experiments_created} experiments created")
        
        return completion_message
        
    except Exception as e:
        print(f"Error in grid search execution: {str(e)}")
        suite.fail_execution()
        raise
