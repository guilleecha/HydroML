"""
Evaluation and metrics calculation tasks for ML experiments.
"""
from celery import shared_task
from experiments.models import MLExperiment
from experiments.tasks.utils import generate_shap_plots
import logging
import os
import uuid
from django.conf import settings
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import mlflow
import mlflow.sklearn
import numpy as np
import joblib
import traceback
import pandas as pd
import shap
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.io import to_html

logger = logging.getLogger(__name__)


@shared_task
def run_time_series_cross_validation_task(experiment_id):
    """
    Perform Time Series Cross-Validation for ML experiments.
    
    This task implements time series cross-validation using sklearn's TimeSeriesSplit,
    which is specifically designed for time-dependent data. It trains and evaluates
    the model across multiple folds, calculating performance metrics for each fold
    and aggregating them to provide robust performance estimates.
    
    Args:
        experiment_id (str): UUID of the experiment to process.
        
    Returns:
        str: The experiment ID indicating successful completion.
        
    Raises:
        ValueError: If artifact paths are missing or invalid.
        MLExperiment.DoesNotExist: If experiment with given ID doesn't exist.
        Exception: For any other processing errors, with experiment status set to ERROR.
        
    Side Effects:
        - Updates experiment status to RUNNING, then FINISHED
        - Saves cross-validation results as JSON file
        - Updates experiment.results with aggregated metrics
        - Updates experiment.artifact_paths with CV results
        - Logs metrics to MLflow
    """
    print(f"Running time series cross-validation for experiment {experiment_id}")
    
    try:
        
        # Get the experiment
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = MLExperiment.Status.RUNNING
        experiment.save()
        
        # Set MLflow tracking URI and resume run
        mlflow.set_tracking_uri("http://mlflow:5000")
        
        # Resume the MLflow run if we have a run ID
        mlflow_context = None
        if experiment.mlflow_run_id:
            try:
                mlflow_context = mlflow.start_run(run_id=experiment.mlflow_run_id)
            except Exception as e:
                print(f"Warning: Could not resume MLflow run {experiment.mlflow_run_id}: {e}")
        
        # Import required modules
        import os
        import pickle
        import json
        import pandas as pd
        import numpy as np
        from django.conf import settings
        from sklearn.model_selection import TimeSeriesSplit
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.linear_model import LinearRegression, LogisticRegression
        from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
        from sklearn.svm import SVR, SVC
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        # Check if artifact paths exist
        if not experiment.artifact_paths or 'full_X' not in experiment.artifact_paths:
            raise ValueError("Full dataset not found. Train/test split with TIME_SERIES_CV must be run first.")
        
        artifacts_dir = os.path.join(settings.MEDIA_ROOT, 'experiments', str(experiment.id))
        
        # Load full data from Parquet files
        full_X_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['full_X'])
        full_y_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['full_y'])
        
        X = pd.read_parquet(full_X_path)
        y = pd.read_parquet(full_y_path).iloc[:, 0]  # Get first column as series
        
        # Parse hyperparameters
        hyperparameters = experiment.hyperparameters
        
        # Set up time series cross-validation
        n_splits = 5  # Can be made configurable in the future
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        # Create model based on type
        model_type = experiment.model_type
        
        # Initialize lists to store metrics for each fold
        fold_metrics = []
        
        print(f"Starting {n_splits}-fold time series cross-validation for {model_type}")
        
        for fold, (train_index, test_index) in enumerate(tscv.split(X)):
            print(f"Processing fold {fold + 1}/{n_splits}")
            
            # Split data for this fold
            X_train_fold, X_test_fold = X.iloc[train_index], X.iloc[test_index]
            y_train_fold, y_test_fold = y.iloc[train_index], y.iloc[test_index]
            
            # Create model for this fold
            if model_type == 'RandomForest':
                if y.dtype == 'object' or len(y.unique()) < 10:
                    model = RandomForestClassifier(**hyperparameters)
                else:
                    model = RandomForestRegressor(**hyperparameters)
            elif model_type == 'LinearRegression':
                model = LinearRegression(**hyperparameters)
            elif model_type == 'LogisticRegression':
                model = LogisticRegression(**hyperparameters)
            elif model_type == 'GradientBoosting':
                if y.dtype == 'object' or len(y.unique()) < 10:
                    model = GradientBoostingClassifier(**hyperparameters)
                else:
                    model = GradientBoostingRegressor(**hyperparameters)
            elif model_type == 'SVM':
                if y.dtype == 'object' or len(y.unique()) < 10:
                    model = SVC(**hyperparameters)
                else:
                    model = SVR(**hyperparameters)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Train model on training fold
            model.fit(X_train_fold, y_train_fold)
            
            # Make predictions on test fold
            y_pred_fold = model.predict(X_test_fold)
            
            # Calculate metrics for this fold (assuming regression)
            fold_mse = mean_squared_error(y_test_fold, y_pred_fold)
            fold_mae = mean_absolute_error(y_test_fold, y_pred_fold)
            fold_r2 = r2_score(y_test_fold, y_pred_fold)
            fold_rmse = fold_mse ** 0.5
            
            fold_metric = {
                'fold': fold + 1,
                'mse': fold_mse,
                'mae': fold_mae,
                'r2': fold_r2,
                'rmse': fold_rmse,
                'train_size': len(X_train_fold),
                'test_size': len(X_test_fold)
            }
            
            fold_metrics.append(fold_metric)
            print(f"Fold {fold + 1} - MSE: {fold_mse:.4f}, MAE: {fold_mae:.4f}, R²: {fold_r2:.4f}")
        
        # Calculate aggregated metrics across all folds
        metrics_mean = {
            'mse_mean': np.mean([m['mse'] for m in fold_metrics]),
            'mae_mean': np.mean([m['mae'] for m in fold_metrics]),
            'r2_mean': np.mean([m['r2'] for m in fold_metrics]),
            'rmse_mean': np.mean([m['rmse'] for m in fold_metrics])
        }
        
        metrics_std = {
            'mse_std': np.std([m['mse'] for m in fold_metrics]),
            'mae_std': np.std([m['mae'] for m in fold_metrics]),
            'r2_std': np.std([m['r2'] for m in fold_metrics]),
            'rmse_std': np.std([m['rmse'] for m in fold_metrics])
        }
        
        # Combine all results
        cv_results = {
            'cross_validation_type': 'time_series',
            'n_splits': n_splits,
            'fold_metrics': fold_metrics,
            'aggregated_metrics': {**metrics_mean, **metrics_std}
        }
        
        print(f"Cross-validation completed - Mean R²: {metrics_mean['r2_mean']:.4f} ± {metrics_std['r2_std']:.4f}")
        
        # Log aggregated metrics to MLflow
        if mlflow_context:
            mlflow.log_metric("cv_mse_mean", metrics_mean['mse_mean'])
            mlflow.log_metric("cv_mae_mean", metrics_mean['mae_mean'])
            mlflow.log_metric("cv_r2_mean", metrics_mean['r2_mean'])
            mlflow.log_metric("cv_rmse_mean", metrics_mean['rmse_mean'])
            mlflow.log_metric("cv_mse_std", metrics_std['mse_std'])
            mlflow.log_metric("cv_mae_std", metrics_std['mae_std'])
            mlflow.log_metric("cv_r2_std", metrics_std['r2_std'])
            mlflow.log_metric("cv_rmse_std", metrics_std['rmse_std'])
            mlflow.log_param("validation_strategy", "TIME_SERIES_CV")
            mlflow.log_param("n_splits", n_splits)
        
        # Save cross-validation results
        cv_results_path = os.path.join(artifacts_dir, 'cv_results.json')
        with open(cv_results_path, 'w') as f:
            json.dump(cv_results, f, indent=2)
        
        # Update artifact paths
        experiment.artifact_paths['cv_results'] = f'experiments/{experiment.id}/cv_results.json'
        
        # Store results in database for easy template access
        experiment.results = {
            'cross_validation_results': cv_results,
            'performance_metrics': metrics_mean
        }
        
        # Mark experiment as completed
        experiment.status = MLExperiment.Status.FINISHED
        experiment.save()
        
        # End MLflow run successfully
        if mlflow_context:
            mlflow.end_run(status="FINISHED")
        
        print(f"Time series cross-validation completed for experiment {experiment_id}")
        logger.info(f"Cross-validation completada para el experimento {experiment_id}.")
        return experiment_id
        
    except Exception as e:
        # End MLflow run on error
        if 'mlflow_context' in locals() and mlflow_context:
            try:
                mlflow.end_run(status="FAILED")
            except:
                pass
        
        print(f"Error in time series cross-validation for experiment {experiment_id}: {str(e)}")
        logger.error(f"Error en run_time_series_cross_validation_task para {experiment_id}: {e}")
        try:
            experiment = MLExperiment.objects.get(id=experiment_id)
            experiment.status = MLExperiment.Status.ERROR
            experiment.save()
        except:
            pass
        raise


@shared_task
def run_final_evaluation_task(experiment_id):
    """
    Evaluate the trained model on test data and generate comprehensive metrics.
    
    This task loads the trained model and test datasets, performs predictions,
    calculates evaluation metrics, and stores results for visualization and
    analysis. It handles both regression and classification metrics (though
    currently focuses on regression) and integrates with MLflow for tracking.
    
    The task generates multiple outputs including:
    - Performance metrics (MSE, MAE, R², RMSE for regression)
    - Prediction results stored as CSV
    - Chart-ready prediction data (limited to 1000 points for performance)
    - MLflow model logging for production deployment
    
    Args:
        experiment_id (str): UUID of the experiment to evaluate.
        
    Returns:
        str: The experiment ID indicating successful completion.
        
    Raises:
        ValueError: If trained model artifact is missing.
        MLExperiment.DoesNotExist: If experiment with given ID doesn't exist.
        Exception: For any other evaluation errors, with experiment status set to ERROR.
        
    Side Effects:
        - Updates experiment status to RUNNING, then FINISHED
        - Saves evaluation metrics as JSON file
        - Saves predictions as CSV file
        - Updates experiment.results with metrics and prediction data
        - Updates experiment.artifact_paths with evaluation artifacts
        - Logs metrics and model to MLflow
        - Ends MLflow run with appropriate status
    """
    print(f"Running final evaluation for experiment {experiment_id}")
    
    try:
        
        # Get the experiment
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = MLExperiment.Status.RUNNING
        experiment.save()
        
        # Set MLflow tracking URI and resume run
        mlflow.set_tracking_uri("http://mlflow:5000")
        
        # Resume the MLflow run if we have a run ID
        mlflow_context = None
        if experiment.mlflow_run_id:
            try:
                mlflow_context = mlflow.start_run(run_id=experiment.mlflow_run_id)
            except Exception as e:
                print(f"Warning: Could not resume MLflow run {experiment.mlflow_run_id}: {e}")
        
        # Import required modules
        import os
        import pickle
        import json
        import pandas as pd
        import numpy as np
        from django.conf import settings
        from sklearn.metrics import (
            mean_squared_error, mean_absolute_error, r2_score,
            accuracy_score, precision_score, recall_score, f1_score, classification_report
        )
        
        # Check if artifact paths exist
        if not experiment.artifact_paths or 'trained_model' not in experiment.artifact_paths:
            raise ValueError("No trained model found. Model training must be completed first.")
        
        artifacts_dir = os.path.join(settings.MEDIA_ROOT, 'experiments', str(experiment.id))
        
        # Load test data from Parquet files
        test_X_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['test_X'])
        test_y_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['test_y'])
        
        X_test = pd.read_parquet(test_X_path)
        y_test = pd.read_parquet(test_y_path).iloc[:, 0]  # Get first column as series
        
        # Load trained model
        model_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['trained_model'])
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics (assuming regression for now since that's what's in the form)
        # TODO: Add problem_type field to distinguish regression/classification
        metrics = {}
        
        # For now, treat everything as regression
        metrics['mse'] = float(mean_squared_error(y_test, y_pred))
        metrics['mae'] = float(mean_absolute_error(y_test, y_pred))
        metrics['r2'] = float(r2_score(y_test, y_pred))
        metrics['rmse'] = float(metrics['mse'] ** 0.5)
        
        print(f"Regression Metrics - MSE: {metrics['mse']:.4f}, MAE: {metrics['mae']:.4f}, R²: {metrics['r2']:.4f}")
        
        # Log metrics to MLflow
        if mlflow_context:
            mlflow.log_metric("mse", metrics['mse'])
            mlflow.log_metric("mae", metrics['mae'])
            mlflow.log_metric("r2_score", metrics['r2'])
            mlflow.log_metric("rmse", metrics['rmse'])
            mlflow.log_metric("test_samples", len(X_test))
            
            # Log the model to MLflow
            try:
                mlflow.sklearn.log_model(
                    sk_model=model,
                    artifact_path="model",
                    registered_model_name=f"HydroML_Model_{experiment_id}"
                )
                print(f"Model logged to MLflow for experiment {experiment_id}")
            except Exception as e:
                print(f"Warning: Could not log model to MLflow: {e}")
        
        # Save metrics
        metrics_path = os.path.join(artifacts_dir, 'evaluation_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Save predictions
        predictions_df = pd.DataFrame({
            'y_true': y_test,
            'y_pred': y_pred
        })
        predictions_path = os.path.join(artifacts_dir, 'predictions.csv')
        predictions_df.to_csv(predictions_path, index=False)
        
        # Prepare prediction data for charts (limit to 1000 points for performance)
        prediction_data = []
        max_points = min(1000, len(y_test))
        indices = np.random.choice(len(y_test), max_points, replace=False) if len(y_test) > max_points else range(len(y_test))
        
        for i in indices:
            prediction_data.append({
                'actual': float(y_test.iloc[i]),
                'predicted': float(y_pred[i])
            })
        
        # Update artifact paths
        experiment.artifact_paths['evaluation_metrics'] = f'experiments/{experiment.id}/evaluation_metrics.json'
        experiment.artifact_paths['predictions'] = f'experiments/{experiment.id}/predictions.csv'
        
        # Store results in database for easy template access
        experiment.results = {
            'performance_metrics': metrics,
            'prediction_data': prediction_data,
            'y_test': y_test.tolist()[:max_points],
            'predictions': y_pred.tolist()[:max_points]
        }
        
        # Generate SHAP interpretability plots
        try:
            shap_plot_path = generate_shap_plots(experiment, model, X_test, artifacts_dir)
            if shap_plot_path:
                experiment.artifact_paths['shap_summary'] = shap_plot_path
                print(f"SHAP summary plot generated for experiment {experiment_id}")
        except Exception as shap_error:
            print(f"Warning: Could not generate SHAP plots for experiment {experiment_id}: {shap_error}")
            logger.warning(f"SHAP generation failed for experiment {experiment_id}: {shap_error}")
        
        # Mark experiment as completed
        experiment.status = MLExperiment.Status.FINISHED
        experiment.save()
        
        # End MLflow run successfully
        if mlflow_context:
            mlflow.end_run(status="FINISHED")
        
        print(f"Final evaluation completed for experiment {experiment_id}")
        logger.info(f"Evaluación final completada para el experimento {experiment_id}.")
        return experiment_id
        
    except Exception as e:
        # End MLflow run on error
        if 'mlflow_context' in locals() and mlflow_context:
            try:
                mlflow.end_run(status="FAILED")
            except:
                pass
        
        print(f"Error in final evaluation for experiment {experiment_id}: {str(e)}")
        logger.error(f"Error en run_final_evaluation_task para {experiment_id}: {e}")
        try:
            experiment = MLExperiment.objects.get(id=experiment_id)
            experiment.status = MLExperiment.Status.ERROR
            experiment.save()
        except:
            pass
        raise
