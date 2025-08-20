"""
Session Service for Data Studio.
Handles temporary session management for data transformations.
"""
import os
import json
import pandas as pd
import logging
import sentry_sdk
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


def get_session_path(datasource, user):
    """
    Get the path for the session temporary files.
    
    Args:
        datasource: DataSource model instance
        user: User model instance
        
    Returns:
        str: Path to session directory
    """
    session_dir = os.path.join(
        settings.MEDIA_ROOT, 
        'temp_sessions', 
        f'user_{user.id}', 
        f'datasource_{datasource.id}'
    )
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def create_session_backup(df, session_path, step_name="backup"):
    """
    Create a backup of the current dataframe state.
    
    Args:
        df (pd.DataFrame): Current dataframe
        session_path (str): Session directory path
        step_name (str): Name for this backup step
        
    Returns:
        bool: Success status
    """
    try:
        backup_file = os.path.join(session_path, f"{step_name}.parquet")
        df.to_parquet(backup_file, index=False)
        
        # Update session metadata
        metadata_file = os.path.join(session_path, "session_metadata.json")
        metadata = load_session_metadata(session_path)
        metadata['backups'].append({
            'step': step_name,
            'file': f"{step_name}.parquet",
            'shape': df.shape,
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
            
        return True
        
    except Exception as e:
        logger.error(f"Error creating session backup: {e}")
        sentry_sdk.capture_exception(e)
        return False


def load_session_metadata(session_path):
    """
    Load session metadata or create default structure.
    
    Args:
        session_path (str): Session directory path
        
    Returns:
        dict: Session metadata
    """
    metadata_file = os.path.join(session_path, "session_metadata.json")
    
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading session metadata: {e}")
    
    # Return default metadata structure
    return {
        'created_at': pd.Timestamp.now().isoformat(),
        'current_step': 0,
        'backups': [],
        'operations': []
    }


def initialize_session(datasource, user, df):
    """
    Initialize a new session with the original dataframe.
    
    Args:
        datasource: DataSource model instance
        user: User model instance
        df (pd.DataFrame): Original dataframe
        
    Returns:
        tuple: (success: bool, session_path: str)
    """
    try:
        session_path = get_session_path(datasource, user)
        
        # Clear any existing session files
        clear_session_files(session_path)
        
        # Save original data
        original_file = os.path.join(session_path, "original.parquet")
        df.to_parquet(original_file, index=False)
        
        # Save current working copy
        current_file = os.path.join(session_path, "current.parquet")
        df.to_parquet(current_file, index=False)
        
        # Initialize metadata
        metadata = {
            'created_at': pd.Timestamp.now().isoformat(),
            'datasource_id': str(datasource.id),
            'user_id': user.id,
            'original_shape': df.shape,
            'current_step': 0,
            'backups': [],
            'operations': []
        }
        
        metadata_file = os.path.join(session_path, "session_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        logger.info(f"Session initialized for user {user.id}, datasource {datasource.id}")
        return True, session_path
        
    except Exception as e:
        logger.error(f"Error initializing session: {e}")
        sentry_sdk.capture_exception(e)
        return False, None


def load_current_dataframe(session_path):
    """
    Load the current working dataframe from session.
    
    Args:
        session_path (str): Session directory path
        
    Returns:
        pd.DataFrame or None: Current dataframe
    """
    try:
        current_file = os.path.join(session_path, "current.parquet")
        if os.path.exists(current_file):
            return pd.read_parquet(current_file)
        return None
        
    except Exception as e:
        logger.error(f"Error loading current dataframe: {e}")
        sentry_sdk.capture_exception(e)
        return None


def save_current_dataframe(df, session_path, operation_name=None):
    """
    Save the current dataframe state to session.
    
    Args:
        df (pd.DataFrame): Current dataframe
        session_path (str): Session directory path
        operation_name (str): Name of the operation performed
        
    Returns:
        bool: Success status
    """
    try:
        # Create backup before saving new state
        if operation_name:
            metadata = load_session_metadata(session_path)
            step_num = len(metadata['backups'])
            create_session_backup(df, session_path, f"step_{step_num}")
        
        # Save current state
        current_file = os.path.join(session_path, "current.parquet")
        df.to_parquet(current_file, index=False)
        
        # Update metadata if operation specified
        if operation_name:
            metadata = load_session_metadata(session_path)
            metadata['operations'].append({
                'name': operation_name,
                'timestamp': pd.Timestamp.now().isoformat(),
                'shape_after': df.shape
            })
            metadata['current_step'] = len(metadata['operations'])
            
            metadata_file = os.path.join(session_path, "session_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving current dataframe: {e}")
        sentry_sdk.capture_exception(e)
        return False


def clear_session_files(session_path):
    """
    Clear all files in the session directory.
    
    Args:
        session_path (str): Session directory path
    """
    try:
        if os.path.exists(session_path):
            for file in os.listdir(session_path):
                file_path = os.path.join(session_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
    except Exception as e:
        logger.error(f"Error clearing session files: {e}")
        sentry_sdk.capture_exception(e)


def session_exists(datasource, user):
    """
    Check if an active session exists for the given datasource and user.
    
    Args:
        datasource: DataSource model instance
        user: User model instance
        
    Returns:
        bool: True if session exists
    """
    try:
        session_path = get_session_path(datasource, user)
        current_file = os.path.join(session_path, "current.parquet")
        metadata_file = os.path.join(session_path, "session_metadata.json")
        
        return os.path.exists(current_file) and os.path.exists(metadata_file)
        
    except Exception as e:
        logger.error(f"Error checking session existence: {e}")
        return False