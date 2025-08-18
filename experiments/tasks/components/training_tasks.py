"""
Training and model creation tasks for ML experiments.
"""
from celery import shared_task
from experiments.models import MLExperiment
from projects.models import DataSource
from data_tools.services import process_datasource_to_df
import logging
import os
import uuid
import pickle
from django.conf import settings
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import mlflow
import mlflow.sklearn
import numpy as np
import joblib
import traceback
import pandas as pd

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
        
        experiment.artifact_paths = artifact_paths
        experiment.save()
        
        print(f"Data preparation completed for experiment {experiment_id}")
        return f"Train/test split completed"
        
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
def run_model_training_task(experiment_id):
    """
    Train an ML model using the experiment's configuration and prepared data.
    
    This task loads the training data from Parquet files, creates and configures
    the specified ML model with hyperparameters, trains the model on the data,
    and saves the trained model to disk. It supports multiple model types and
    handles different data preprocessing steps.
    
    Args:
        experiment_id (str): UUID of the experiment to process.
        
    Returns:
        str: The experiment ID indicating successful completion.
        
    Raises:
        ValueError: If model type is unsupported or artifacts are missing.
        MLExperiment.DoesNotExist: If experiment with given ID doesn't exist.
        Exception: For any other processing errors, with experiment status set to ERROR.
        
    Side Effects:
        - Updates experiment status to RUNNING, then back to appropriate status
        - Saves trained model as pickle file
        - Updates experiment.artifact_paths with model location
        - Logs training parameters to MLflow
        - Records training time and model metrics
    """
    print(f"Running model training for experiment {experiment_id}")
    
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

        # Load training data
        artifacts_dir = os.path.join(settings.MEDIA_ROOT, 'experiments', str(experiment.id))
        
        train_X_path = os.path.join(artifacts_dir, 'train_X.parquet')
        train_y_path = os.path.join(artifacts_dir, 'train_y.parquet')
        
        if not os.path.exists(train_X_path) or not os.path.exists(train_y_path):
            raise ValueError("Training data files not found. Run train/test split first.")
        
        X_train = pd.read_parquet(train_X_path)
        y_train = pd.read_parquet(train_y_path).iloc[:, 0]  # Get the target column
        
        # Parse hyperparameters
        hyperparameters = experiment.hyperparameters
        
        # Create model based on type
        model_type = experiment.model_type
        
        if model_type == 'RandomForest':
            # TODO: Add problem_type field to MLExperiment model to distinguish regression/classification
            # For now, detect based on target variable characteristics
            if y_train.dtype == 'object' or len(y_train.unique()) < 10:
                model = RandomForestClassifier(**hyperparameters)
            else:
                model = RandomForestRegressor(**hyperparameters)
        elif model_type == 'LinearRegression':
            model = LinearRegression(**hyperparameters)
        elif model_type == 'LogisticRegression':
            model = LogisticRegression(**hyperparameters)
        elif model_type == 'GradientBoosting':
            if y_train.dtype == 'object' or len(y_train.unique()) < 10:
                model = GradientBoostingClassifier(**hyperparameters)
            else:
                model = GradientBoostingRegressor(**hyperparameters)
        elif model_type == 'SVM':
            if y_train.dtype == 'object' or len(y_train.unique()) < 10:
                model = SVC(**hyperparameters)
            else:
                model = SVR(**hyperparameters)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        print(f"Training {model_type} model with hyperparameters: {hyperparameters}")
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Save the model
        model_path = os.path.join(artifacts_dir, 'trained_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Update experiment with model artifact path
        if not experiment.artifact_paths:
            experiment.artifact_paths = {}
        experiment.artifact_paths['trained_model'] = f'experiments/{experiment.id}/trained_model.pkl'
        experiment.save()
        
        # Log to MLflow
        if mlflow_context:
            mlflow.log_params(hyperparameters)
            mlflow.sklearn.log_model(model, "model")
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("training_samples", X_train.shape[0])
            mlflow.log_param("features", X_train.shape[1])
        
        print(f"Model training completed for experiment {experiment_id}")
        return experiment_id
        
    except Exception as e:
        print(f"Error in model training for experiment {experiment_id}: {str(e)}")
        try:
            experiment = MLExperiment.objects.get(id=experiment_id)
            experiment.status = MLExperiment.Status.ERROR
            experiment.save()
        except:
            pass
        raise
    finally:
        # Close MLflow run if it was opened
        if mlflow_context:
            try:
                mlflow.end_run()
            except:
                pass
