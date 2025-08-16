"""
Utility functions shared across experiment tasks.

This module contains helper functions that are used by multiple tasks
in the experiment pipeline, including SHAP plot generation, metric extraction,
and common model operations.
"""

import logging

logger = logging.getLogger(__name__)


def generate_shap_plots(experiment, model, X_test, artifacts_dir):
    """
    Generate SHAP interpretability plots for the given model and test data.
    
    This function creates SHAP explanations and generates a summary plot
    that shows feature importance and value distributions. The plot is
    saved as a PNG file in the experiment's artifacts directory.
    
    Args:
        experiment (MLExperiment): The experiment instance.
        model: The trained scikit-learn model.
        X_test (pd.DataFrame): Test features for SHAP analysis.
        artifacts_dir (str): Directory to save the SHAP plot.
        
    Returns:
        str or None: Relative path to the saved SHAP plot, or None if failed.
    """
    try:
        import shap
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend for server environment
        import matplotlib.pyplot as plt
        import numpy as np
        import os
        
        print(f"Generating SHAP plots for experiment {experiment.id}")
        
        # Limit test data for SHAP analysis (performance considerations)
        max_samples_for_shap = min(500, len(X_test))
        if len(X_test) > max_samples_for_shap:
            # Use random sampling for representative analysis
            sample_indices = np.random.choice(len(X_test), max_samples_for_shap, replace=False)
            X_test_sample = X_test.iloc[sample_indices]
        else:
            X_test_sample = X_test
        
        print(f"Using {len(X_test_sample)} samples for SHAP analysis")
        
        # Choose appropriate SHAP explainer based on model type
        model_type = experiment.model_name
        explainer = None
        
        # Tree-based models: use TreeExplainer for efficiency
        if any(tree_model in model_type for tree_model in ['RandomForest', 'GradientBoosting', 'XGBoost', 'LightGBM']):
            print(f"Using TreeExplainer for model type: {model_type}")
            explainer = shap.TreeExplainer(model)
            
        # Linear models: use LinearExplainer
        elif any(linear_model in model_type for linear_model in ['LinearRegression', 'LogisticRegression', 'Ridge', 'Lasso']):
            print(f"Using LinearExplainer for model type: {model_type}")
            explainer = shap.LinearExplainer(model, X_test_sample)
            
        # Default fallback: use KernelExplainer (slower but works for any model)
        else:
            print(f"Using KernelExplainer for model type: {model_type}")
            # Use a smaller background dataset for KernelExplainer efficiency
            background_size = min(100, len(X_test_sample))
            background = X_test_sample.sample(n=background_size, random_state=42)
            explainer = shap.KernelExplainer(model.predict, background)
        
        # Calculate SHAP values
        print("Calculating SHAP values...")
        if 'Kernel' in str(type(explainer)):
            # For KernelExplainer, use fewer samples to avoid timeout
            analysis_size = min(100, len(X_test_sample))
            X_for_analysis = X_test_sample.sample(n=analysis_size, random_state=42)
            shap_values = explainer.shap_values(X_for_analysis)
        else:
            shap_values = explainer.shap_values(X_test_sample)
        
        # Handle different SHAP value formats
        if isinstance(shap_values, list):
            # For multi-output models (e.g., classification), use first output
            shap_values = shap_values[0]
        
        # Create summary plot
        print("Generating SHAP summary plot...")
        plt.figure(figsize=(10, 8))
        
        # Generate summary plot with show=False to prevent GUI display
        shap.summary_plot(
            shap_values, 
            X_test_sample if not 'Kernel' in str(type(explainer)) else X_for_analysis,
            feature_names=X_test.columns.tolist(),
            show=False,
            max_display=min(20, len(X_test.columns))  # Limit features for readability
        )
        
        # Save the plot
        shap_plot_filename = 'shap_summary.png'
        shap_plot_path = os.path.join(artifacts_dir, shap_plot_filename)
        plt.tight_layout()
        plt.savefig(shap_plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()  # Important: close the figure to free memory
        
        # Return relative path for storage in artifact_paths
        relative_path = f'experiments/{experiment.id}/{shap_plot_filename}'
        print(f"SHAP summary plot saved to: {shap_plot_path}")
        
        return relative_path
        
    except ImportError as e:
        print(f"SHAP library not available: {e}")
        return None
        
    except Exception as e:
        print(f"Error generating SHAP plots: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def extract_optimization_metric(experiment_results, optimization_metric):
    """
    Extract the optimization metric value from experiment results.
    
    Args:
        experiment_results (dict): Results from experiment execution.
        optimization_metric (str): Name of the metric to optimize.
        
    Returns:
        float: The metric value, or worst possible value if not found.
    """
    try:
        if not experiment_results or 'performance_metrics' not in experiment_results:
            return float('inf')  # Default to worst case
        
        metrics = experiment_results['performance_metrics']
        
        # Handle various metric naming conventions
        metric_value = metrics.get(optimization_metric)
        if metric_value is None:
            # Try alternative names
            metric_aliases = {
                'r2': ['r2_score', 'r_squared'],
                'r2_score': ['r2', 'r_squared'],
                'mse': ['mean_squared_error'],
                'mae': ['mean_absolute_error'],
                'rmse': ['root_mean_squared_error']
            }
            
            for alias in metric_aliases.get(optimization_metric, []):
                metric_value = metrics.get(alias)
                if metric_value is not None:
                    break
        
        if metric_value is None:
            print(f"Warning: Optimization metric '{optimization_metric}' not found in results")
            return float('inf')
        
        return float(metric_value)
        
    except Exception as e:
        print(f"Error extracting optimization metric: {str(e)}")
        return float('inf')


def create_child_experiment_for_optuna(suite, trial_number, hyperparameters):
    """
    Create a child experiment for an Optuna trial.
    
    Args:
        suite (ExperimentSuite): Parent suite.
        trial_number (int): Optuna trial number.
        hyperparameters (dict): Suggested hyperparameters.
        
    Returns:
        MLExperiment: Created child experiment.
    """
    from ..models import MLExperiment
    
    base_experiment = suite.base_experiment
    
    child_experiment = MLExperiment(
        # Copy settings from base experiment
        project=base_experiment.project,
        name=f"{suite.name} - Trial {trial_number + 1}",
        description=f"Optuna trial {trial_number + 1} of suite '{suite.name}'. Parameters: {hyperparameters}",
        input_datasource=base_experiment.input_datasource,
        target_column=base_experiment.target_column,
        model_name=base_experiment.model_name,
        feature_set=base_experiment.feature_set,
        test_split_size=base_experiment.test_split_size,
        split_random_state=base_experiment.split_random_state,
        split_strategy=base_experiment.split_strategy,
        
        # Set specific parameters for this trial
        hyperparameters=hyperparameters,
        suite=suite,  # Link to parent suite
        status=MLExperiment.Status.QUEUED,
        version=1,
        is_public=False
    )
    
    child_experiment.save()
    print(f"Created Optuna trial experiment: {child_experiment.name}")
    return child_experiment


def run_single_experiment_sync(experiment):
    """
    Run a single experiment synchronously for Optuna optimization.
    
    This function executes the complete ML pipeline for a single experiment
    and waits for completion to return the results.
    
    Args:
        experiment (MLExperiment): Experiment to run.
        
    Returns:
        dict: Experiment results including metrics.
    """
    try:
        # Import the individual tasks from the experiment_tasks module
        from .experiment_tasks import (
            run_train_test_split_task,
            run_model_training_task,
            run_final_evaluation_task
        )
        
        # Run pipeline steps synchronously
        run_train_test_split_task(str(experiment.id))
        run_model_training_task(str(experiment.id))
        run_final_evaluation_task(str(experiment.id))
        
        # Reload experiment to get updated results
        experiment.refresh_from_db()
        
        return experiment.results
        
    except Exception as e:
        print(f"Error running experiment {experiment.id}: {str(e)}")
        experiment.status = experiment.__class__.Status.ERROR
        experiment.save()
        raise
