"""
Individual experiment pipeline tasks.

This module contains Celery tasks that handle individual ML experiment
execution including train/test splitting, model training, evaluation,
and pipeline orchestration.
"""

from celery import shared_task, chain
from ..models import MLExperiment
from django.contrib.auth.models import User
from django.urls import reverse
from .utils import generate_shap_plots
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_train_test_split_task(experiment_id):
    """
    Perform train/test data splitting for an ML experiment.
    
    This task loads data from the experiment's designated datasource, validates
    the target column, and splits the data into training and testing sets based
    on the experiment's configuration. The resulting datasets are saved as
    Parquet files in the experiment's artifact directory.
    
    The task supports multiple splitting strategies and multiple validation strategies
    including simple train/test split and time series cross-validation.
    
    Args:
        experiment_id (str): UUID of the experiment to process.
        
    Returns:
        str: Status message indicating completion with sample counts.
        
    Raises:
        ValueError: If target column is not found in the datasource.
        MLExperiment.DoesNotExist: If experiment with given ID doesn't exist.
        Exception: For any other processing errors, with experiment status set to ERROR.
        
    Side Effects:
        - Updates experiment status to RUNNING
        - Creates artifact directory structure
        - Saves train/test datasets as Parquet files (for simple split)
        - Saves full dataset as Parquet file (for cross-validation)
        - Updates experiment.artifact_paths with file locations
    """
    print(f"Running train/test split for experiment {experiment_id}")
    
    try:
        # Get the experiment
        experiment = MLExperiment.objects.get(id=experiment_id)
        experiment.status = MLExperiment.Status.RUNNING
        experiment.save()
        
        # Import required modules
        import os
        import uuid
        from django.conf import settings
        from sklearn.model_selection import train_test_split
        from data_tools.services import process_datasource_to_df
        
        # Load data from target datasource
        print(f"Loading data from datasource {experiment.input_datasource.id}")
        df = process_datasource_to_df(experiment.input_datasource.id)
        
        # Validate target column exists
        target_column = experiment.target_column
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in datasource")
        
        # Prepare features (X) and target (y)
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Create experiment artifacts directory
        artifacts_dir = os.path.join(settings.MEDIA_ROOT, 'experiments', str(experiment.id))
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Handle different validation strategies
        if experiment.validation_strategy == 'TIME_SERIES_CV':
            # For time series cross-validation, save the full dataset
            full_X_path = os.path.join(artifacts_dir, 'full_X.parquet')
            full_y_path = os.path.join(artifacts_dir, 'full_y.parquet')
            
            X.to_parquet(full_X_path, index=False)
            y.to_frame().to_parquet(full_y_path, index=False)
            
            # Update experiment with artifact paths for time series CV
            artifact_paths = {
                'full_X': f'experiments/{experiment.id}/full_X.parquet',
                'full_y': f'experiments/{experiment.id}/full_y.parquet'
            }
            
            print(f"Data preparation for time series CV completed: {X.shape[0]} total samples")
            return f"Data preparation for time series CV completed: {X.shape[0]} total samples"
            
        else:
            # Default: Simple train/test split
            test_size = experiment.test_split_size / 100.0  # Convert percentage to decimal
            random_state = 42  # For reproducibility
            
            print(f"Splitting data with test_size={test_size}")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Save train and test datasets as Parquet files
            train_X_path = os.path.join(artifacts_dir, 'train_X.parquet')
            train_y_path = os.path.join(artifacts_dir, 'train_y.parquet')
            test_X_path = os.path.join(artifacts_dir, 'test_X.parquet')
            test_y_path = os.path.join(artifacts_dir, 'test_y.parquet')
            
            X_train.to_parquet(train_X_path, index=False)
            y_train.to_frame().to_parquet(train_y_path, index=False)  
            X_test.to_parquet(test_X_path, index=False)
            y_test.to_frame().to_parquet(test_y_path, index=False)  
            
            # Update experiment with artifact paths
            artifact_paths = {
                'train_X': f'experiments/{experiment.id}/train_X.parquet',
                'train_y': f'experiments/{experiment.id}/train_y.parquet',
                'test_X': f'experiments/{experiment.id}/test_X.parquet',
                'test_y': f'experiments/{experiment.id}/test_y.parquet'
            }
            
            print(f"Train/test split completed: {X_train.shape[0]} train samples, {X_test.shape[0]} test samples")
            return f"Train/test split completed: {X_train.shape[0]} train samples, {X_test.shape[0]} test samples"
        
        experiment.artifact_paths = artifact_paths
        experiment.save()
        
        print(f"Data preparation completed for experiment {experiment_id}")
        
    except Exception as e:
        print(f"Error in train/test split for experiment {experiment_id}: {str(e)}")
        try:
            experiment = MLExperiment.objects.get(id=experiment_id)
            experiment.status = MLExperiment.Status.ERROR
            experiment.save()
        except:
            pass
        raise


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
        import mlflow
        import mlflow.sklearn
        
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
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.metrics import (
            mean_squared_error, mean_absolute_error, r2_score,
            accuracy_score, precision_score, recall_score, f1_score
        )
        
        # Check if artifact paths exist
        if not experiment.artifact_paths:
            raise ValueError("No artifact paths found. Data preparation must be completed first.")
        
        artifacts_dir = os.path.join(settings.MEDIA_ROOT, 'experiments', str(experiment.id))
        
        # Load full dataset from Parquet files
        full_X_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['full_X'])
        full_y_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['full_y'])
        
        X = pd.read_parquet(full_X_path)
        y = pd.read_parquet(full_y_path).iloc[:, 0]  # Get first column as series
        
        # Get model configuration
        model_type = experiment.model_name
        model_params = experiment.hyperparameters or {}
        
        # Log cross-validation parameters to MLflow
        if mlflow_context:
            mlflow.log_param("validation_strategy", "TIME_SERIES_CV")
            mlflow.log_param("total_samples", len(X))
            mlflow.log_param("feature_count", X.shape[1])
            
            # Log all hyperparameters with model prefix
            for param_name, param_value in model_params.items():
                mlflow.log_param(f"model_{param_name}", param_value)
        
        # Initialize TimeSeriesSplit (default n_splits=5)
        n_splits = 5
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        print(f"Performing {n_splits}-fold time series cross-validation")
        
        # Store results from each fold
        fold_scores = []
        fold_results = []
        
        # Perform cross-validation
        for fold_idx, (train_idx, test_idx) in enumerate(tscv.split(X)):
            print(f"Processing fold {fold_idx + 1}/{n_splits}")
            
            # Split data for this fold
            X_train_fold, X_test_fold = X.iloc[train_idx], X.iloc[test_idx]
            y_train_fold, y_test_fold = y.iloc[train_idx], y.iloc[test_idx]
            
            # Initialize model for this fold
            if model_type == 'RandomForestRegressor':
                model = RandomForestRegressor(**model_params)
            elif model_type == 'LinearRegression':
                model = LinearRegression(**model_params)
            elif model_type == 'GradientBoostingRegressor':
                model = GradientBoostingRegressor(**model_params)
            else:
                # Fallback to RandomForest if unknown
                model = RandomForestRegressor(**model_params)
            
            # Train the model on this fold
            model.fit(X_train_fold, y_train_fold)
            
            # Make predictions on this fold's test set
            y_pred_fold = model.predict(X_test_fold)
            
            # Calculate metrics for this fold (assuming regression)
            fold_metrics = {
                'fold': fold_idx + 1,
                'train_samples': len(X_train_fold),
                'test_samples': len(X_test_fold),
                'mse': float(mean_squared_error(y_test_fold, y_pred_fold)),
                'mae': float(mean_absolute_error(y_test_fold, y_pred_fold)),
                'r2': float(r2_score(y_test_fold, y_pred_fold)),
            }
            fold_metrics['rmse'] = float(fold_metrics['mse'] ** 0.5)
            
            fold_scores.append(fold_metrics['r2'])  # Use R² as primary metric
            fold_results.append(fold_metrics)
            
            print(f"Fold {fold_idx + 1} - R²: {fold_metrics['r2']:.4f}, RMSE: {fold_metrics['rmse']:.4f}")
            
            # Log fold metrics to MLflow
            if mlflow_context:
                mlflow.log_metric(f"fold_{fold_idx + 1}_r2", fold_metrics['r2'])
                mlflow.log_metric(f"fold_{fold_idx + 1}_rmse", fold_metrics['rmse'])
                mlflow.log_metric(f"fold_{fold_idx + 1}_mae", fold_metrics['mae'])
        
        # Calculate aggregated metrics
        mean_score = np.mean(fold_scores)
        std_score = np.std(fold_scores)
        
        # Calculate mean and std for all metrics
        aggregated_metrics = {
            'cv_strategy': 'TIME_SERIES_CV',
            'n_splits': n_splits,
            'mean_r2': float(mean_score),
            'std_r2': float(std_score),
            'mean_mse': float(np.mean([fold['mse'] for fold in fold_results])),
            'std_mse': float(np.std([fold['mse'] for fold in fold_results])),
            'mean_mae': float(np.mean([fold['mae'] for fold in fold_results])),
            'std_mae': float(np.std([fold['mae'] for fold in fold_results])),
            'mean_rmse': float(np.mean([fold['rmse'] for fold in fold_results])),
            'std_rmse': float(np.std([fold['rmse'] for fold in fold_results])),
            'fold_results': fold_results
        }
        
        print(f"Cross-validation completed - Mean R²: {mean_score:.4f} (±{std_score:.4f})")
        
        # Log aggregated metrics to MLflow
        if mlflow_context:
            mlflow.log_metric("cv_mean_r2", mean_score)
            mlflow.log_metric("cv_std_r2", std_score)
            mlflow.log_metric("cv_mean_rmse", aggregated_metrics['mean_rmse'])
            mlflow.log_metric("cv_std_rmse", aggregated_metrics['std_rmse'])
            
            # Train final model on full dataset for deployment
            if model_type == 'RandomForestRegressor':
                final_model = RandomForestRegressor(**model_params)
            elif model_type == 'LinearRegression':
                final_model = LinearRegression(**model_params)
            elif model_type == 'GradientBoostingRegressor':
                final_model = GradientBoostingRegressor(**model_params)
            else:
                final_model = RandomForestRegressor(**model_params)
            
            final_model.fit(X, y)
            
            # Log the final model to MLflow
            try:
                mlflow.sklearn.log_model(
                    sk_model=final_model,
                    artifact_path="model",
                    registered_model_name=f"HydroML_Model_{experiment_id}"
                )
                print(f"Final model logged to MLflow for experiment {experiment_id}")
            except Exception as e:
                print(f"Warning: Could not log model to MLflow: {e}")
        
        # Save cross-validation results
        cv_results_path = os.path.join(artifacts_dir, 'cv_results.json')
        with open(cv_results_path, 'w') as f:
            json.dump(aggregated_metrics, f, indent=2)
        
        # Update artifact paths
        if not experiment.artifact_paths:
            experiment.artifact_paths = {}
        experiment.artifact_paths['cv_results'] = f'experiments/{experiment.id}/cv_results.json'
        
        # Store results in database for easy template access
        experiment.results = {
            'performance_metrics': aggregated_metrics,
            'validation_strategy': 'TIME_SERIES_CV'
        }
        
        # Mark experiment as completed
        experiment.status = MLExperiment.Status.FINISHED
        experiment.save()
        
        # End MLflow run successfully
        if mlflow_context:
            mlflow.end_run(status="FINISHED")
        
        print(f"Time series cross-validation completed for experiment {experiment_id}")
        return experiment_id
        
    except Exception as e:
        # End MLflow run on error
        if 'mlflow_context' in locals() and mlflow_context:
            try:
                mlflow.end_run(status="FAILED")
            except:
                pass
        
        print(f"Error in time series cross-validation for experiment {experiment_id}: {str(e)}")
        try:
            experiment = MLExperiment.objects.get(id=experiment_id)
            experiment.status = MLExperiment.Status.ERROR
            experiment.save()
        except:
            pass
        raise


@shared_task
def run_model_training_task(experiment_id):
    """
    Train the ML model using prepared training data.
    
    This task loads the training datasets created by the train/test split task,
    initializes the specified ML algorithm with configured hyperparameters,
    trains the model, and saves the trained model as a pickle file. The task
    integrates with MLflow for experiment tracking and parameter logging.
    
    The task supports multiple ML algorithms including RandomForest, LinearRegression,
    and GradientBoosting regressors. Model selection is based on the experiment's
    model_name configuration, with RandomForest as the fallback option.
    
    Args:
        experiment_id (str): UUID of the experiment to process.
        
    Returns:
        str: The experiment ID for task chaining purposes.
        
    Raises:
        ValueError: If artifact paths are missing or invalid.
        MLExperiment.DoesNotExist: If experiment with given ID doesn't exist.
        Exception: For any other training errors, with experiment status set to ERROR.
        
    Side Effects:
        - Updates experiment status to RUNNING
        - Creates and saves trained model pickle file
        - Updates experiment.artifact_paths with model location
        - Logs parameters and metrics to MLflow
        - May create or resume MLflow run for tracking
    """
    print(f"Running model training for experiment {experiment_id}")
    
    try:
        import mlflow
        
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
        import pandas as pd
        from django.conf import settings
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.linear_model import LinearRegression, LogisticRegression
        from sklearn.svm import SVR, SVC
        from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
        
        # Check if artifact paths exist
        if not experiment.artifact_paths:
            raise ValueError("No artifact paths found. Train/test split must be completed first.")
        
        artifacts_dir = os.path.join(settings.MEDIA_ROOT, 'experiments', str(experiment.id))
        
        # Load training data from Parquet files
        train_X_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['train_X'])
        train_y_path = os.path.join(settings.MEDIA_ROOT, experiment.artifact_paths['train_y'])
        
        X_train = pd.read_parquet(train_X_path)
        y_train = pd.read_parquet(train_y_path).iloc[:, 0]  # Get first column as series
        
        # Get model configuration
        model_type = experiment.model_name
        model_params = experiment.hyperparameters or {}
        
        # Log model parameters to MLflow
        if mlflow_context:
            mlflow.log_param("training_samples", len(X_train))
            mlflow.log_param("feature_count", X_train.shape[1])
            
            # Log all hyperparameters with model prefix
            for param_name, param_value in model_params.items():
                mlflow.log_param(f"model_{param_name}", param_value)
        
        # Initialize model based on algorithm (for now we'll assume regression since that's what's in the form)
        # TODO: Add problem_type field to MLExperiment model to distinguish regression/classification
        if model_type == 'RandomForestRegressor':
            model = RandomForestRegressor(**model_params)
        elif model_type == 'LinearRegression':
            model = LinearRegression(**model_params)
        elif model_type == 'GradientBoostingRegressor':
            # Need to import GradientBoostingRegressor
            from sklearn.ensemble import GradientBoostingRegressor
            model = GradientBoostingRegressor(**model_params)
        else:
            # Fallback to RandomForest if unknown
            model = RandomForestRegressor(**model_params)
        
        # Train the model
        print(f"Training {model_type} model")
        model.fit(X_train, y_train)
        
        # Save the trained model
        model_path = os.path.join(artifacts_dir, 'trained_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Update artifact paths
        experiment.artifact_paths['trained_model'] = f'experiments/{experiment.id}/trained_model.pkl'
        experiment.save()
        
        # End MLflow context if we started one
        if mlflow_context:
            mlflow.end_run()
        
        print(f"Model training completed for experiment {experiment_id}")
        logger.info(f"Entrenamiento completado para el experimento {experiment_id}.")
        return experiment_id  # Aseguramos que el ID se pase a la siguiente tarea
        
    except Exception as e:
        # End MLflow run on error
        if 'mlflow_context' in locals() and mlflow_context:
            try:
                mlflow.end_run(status="FAILED")
            except:
                pass
                
        print(f"Error in model training for experiment {experiment_id}: {str(e)}")
        logger.error(f"Error en run_model_training_task para {experiment_id}: {e}")
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
        import mlflow
        import mlflow.sklearn
        
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

        # Create notification for experiment completion
        # completion_notification = Notification.objects.create(
        #     user=experiment.project.owner,
        #     message=f"Tu experimento '{experiment.name}' ha finalizado exitosamente.",
        #     notification_type='experiment',
        #     related_object_id=experiment.id,
        #     link=reverse('experiments:detail', kwargs={'pk': experiment.id})
        # )
        # logger.info(f"Created completion notification {completion_notification.id} for experiment {experiment_id}")

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
            
            # Create error notification
            # error_notification = Notification.objects.create(
            #     user=experiment.project.owner,
            #     message=f"Tu experimento '{experiment.name}' ha finalizado con errores.",
            #     notification_type='experiment',
            #     related_object_id=experiment.id,
            #     link=reverse('experiments:detail', kwargs={'pk': experiment.id})
            # )
            # logger.info(f"Created error notification {error_notification.id} for experiment {experiment_id}")
        except:
            pass
        raise


@shared_task
def set_experiment_status_as_finished(experiment_id):
    """
    Set the experiment status to FINISHED as the final step in the pipeline.
    
    This is a utility task used as the final step in the task chain to ensure
    the experiment status is properly set to FINISHED. It provides a clean
    separation between the evaluation logic and the final status update.
    
    Args:
        experiment_id (str): UUID of the experiment to update.
        
    Raises:
        MLExperiment.DoesNotExist: If experiment with given ID doesn't exist.
        
    Side Effects:
        - Updates experiment status to FINISHED
        - Updates experiment.updated_at timestamp
    """
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

        # Create notification for experiment start
        # start_notification = Notification.objects.create(
        #     user=experiment.project.owner,
        #     message=f"Tu experimento '{experiment.name}' ha comenzado a ejecutarse.",
        #     notification_type='experiment',
        #     related_object_id=experiment.id,
        #     link=reverse('experiments:detail', kwargs={'pk': experiment.id})
        # )
        # logger.info(f"Created start notification {start_notification.id} for experiment {experiment_id}")

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
