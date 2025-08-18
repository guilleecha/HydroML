"""
Data Studio Session Manager for stateful data transformations.
Manages temporary DataFrame states in Redis cache with undo/redo functionality.
"""

import json
import pickle
import logging
from typing import Optional, Dict, Any, List
from datetime import timedelta

import pandas as pd
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class DataStudioSessionManager:
    """Manages stateful data transformations with caching and history."""
    
    CACHE_TIMEOUT = 60 * 60 * 4  # 4 hours
    
    def __init__(self, user_id: int, datasource_id: int):
        self.user_id = user_id
        self.datasource_id = datasource_id
        self.session_key = f"datastudio:{user_id}:{datasource_id}"
        self.current_key = f"{self.session_key}:current"
        self.history_key = f"{self.session_key}:history"
        self.metadata_key = f"{self.session_key}:metadata"
        
    def initialize_session(self, df: pd.DataFrame) -> bool:
        """
        Initialize a new Data Studio session with the original DataFrame.
        
        Args:
            df: The original DataFrame to start the session with
            
        Returns:
            bool: True if session was initialized successfully
        """
        try:
            # Store the current DataFrame state
            self._store_dataframe(self.current_key, df)
            
            # Initialize empty history
            cache.set(self.history_key, [], timeout=self.CACHE_TIMEOUT)
            
            # Store session metadata
            metadata = {
                'created_at': pd.Timestamp.now().isoformat(),
                'original_shape': df.shape,
                'current_step': 0,
                'total_steps': 0
            }
            cache.set(self.metadata_key, metadata, timeout=self.CACHE_TIMEOUT)
            
            logger.info(f"Initialized Data Studio session for user {self.user_id}, datasource {self.datasource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            return False
    
    def get_current_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get the current DataFrame state from cache.
        
        Returns:
            DataFrame or None if not found
        """
        try:
            return self._retrieve_dataframe(self.current_key)
        except Exception as e:
            logger.error(f"Failed to retrieve current DataFrame: {e}")
            return None
    
    def apply_transformation(self, df_transformed: pd.DataFrame, 
                           operation_name: str, 
                           operation_params: Dict[str, Any] = None) -> bool:
        """
        Apply a transformation by saving current state to history and updating current state.
        
        Args:
            df_transformed: The transformed DataFrame
            operation_name: Name of the operation performed
            operation_params: Parameters used for the operation
            
        Returns:
            bool: True if transformation was applied successfully
        """
        try:
            # Get current DataFrame for history
            current_df = self.get_current_dataframe()
            if current_df is None:
                logger.error("No current DataFrame found to save to history")
                return False
            
            # Save current state to history
            self._add_to_history(current_df, operation_name, operation_params)
            
            # Update current state
            self._store_dataframe(self.current_key, df_transformed)
            
            # Update metadata
            self._update_metadata_after_transformation()
            
            logger.info(f"Applied transformation '{operation_name}' to session {self.session_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply transformation: {e}")
            return False
    
    def undo_last_operation(self) -> Optional[pd.DataFrame]:
        """
        Undo the last operation by restoring from history.
        
        Returns:
            DataFrame or None if undo failed
        """
        try:
            history = cache.get(self.history_key, [])
            metadata = cache.get(self.metadata_key, {})
            
            current_step = metadata.get('current_step', 0)
            
            if current_step <= 0 or not history:
                logger.warning("No operations to undo")
                return None
            
            # Get the previous state
            previous_state = history[current_step - 1]
            previous_df = pickle.loads(previous_state['dataframe'])
            
            # Update current state
            self._store_dataframe(self.current_key, previous_df)
            
            # Update metadata
            metadata['current_step'] = current_step - 1
            cache.set(self.metadata_key, metadata, timeout=self.CACHE_TIMEOUT)
            
            logger.info(f"Undid operation in session {self.session_key}")
            return previous_df
            
        except Exception as e:
            logger.error(f"Failed to undo operation: {e}")
            return None
    
    def redo_last_operation(self) -> Optional[pd.DataFrame]:
        """
        Redo the next operation from history.
        
        Returns:
            DataFrame or None if redo failed
        """
        try:
            history = cache.get(self.history_key, [])
            metadata = cache.get(self.metadata_key, {})
            
            current_step = metadata.get('current_step', 0)
            total_steps = metadata.get('total_steps', 0)
            
            if current_step >= total_steps or current_step >= len(history):
                logger.warning("No operations to redo")
                return None
            
            # Apply the next operation from history
            next_state = history[current_step]
            # For redo, we need to re-apply the transformation
            # This is a simplified version - in practice, you might want to store 
            # the result of each transformation as well
            
            # Update metadata
            metadata['current_step'] = current_step + 1
            cache.set(self.metadata_key, metadata, timeout=self.CACHE_TIMEOUT)
            
            logger.info(f"Redid operation in session {self.session_key}")
            return self.get_current_dataframe()
            
        except Exception as e:
            logger.error(f"Failed to redo operation: {e}")
            return None
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            Dictionary with session information
        """
        try:
            metadata = cache.get(self.metadata_key, {})
            history = cache.get(self.history_key, [])
            current_df = self.get_current_dataframe()
            
            return {
                'session_exists': current_df is not None,
                'current_shape': current_df.shape if current_df is not None else None,
                'original_shape': metadata.get('original_shape'),
                'current_step': metadata.get('current_step', 0),
                'total_steps': len(history),
                'can_undo': metadata.get('current_step', 0) > 0,
                'can_redo': metadata.get('current_step', 0) < len(history),
                'created_at': metadata.get('created_at'),
                'operations_history': [
                    {
                        'name': op.get('operation_name', 'Unknown'),
                        'params': op.get('operation_params', {}),
                        'timestamp': op.get('timestamp')
                    }
                    for op in history[:metadata.get('current_step', 0)]
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            return {'session_exists': False}
    
    def clear_session(self) -> bool:
        """
        Clear the current session from cache.
        
        Returns:
            bool: True if session was cleared successfully
        """
        try:
            cache.delete(self.current_key)
            cache.delete(self.history_key)
            cache.delete(self.metadata_key)
            
            logger.info(f"Cleared Data Studio session {self.session_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False
    
    def _store_dataframe(self, key: str, df: pd.DataFrame) -> None:
        """Store DataFrame in cache using pickle serialization."""
        df_bytes = pickle.dumps(df)
        cache.set(key, df_bytes, timeout=self.CACHE_TIMEOUT)
    
    def _retrieve_dataframe(self, key: str) -> Optional[pd.DataFrame]:
        """Retrieve DataFrame from cache using pickle deserialization."""
        df_bytes = cache.get(key)
        if df_bytes is None:
            return None
        return pickle.loads(df_bytes)
    
    def _add_to_history(self, df: pd.DataFrame, operation_name: str, 
                       operation_params: Dict[str, Any] = None) -> None:
        """Add current state to history."""
        history = cache.get(self.history_key, [])
        metadata = cache.get(self.metadata_key, {})
        
        current_step = metadata.get('current_step', 0)
        
        # Remove any future history if we're not at the end
        history = history[:current_step]
        
        # Add new state to history
        history_entry = {
            'dataframe': pickle.dumps(df),
            'operation_name': operation_name,
            'operation_params': operation_params or {},
            'timestamp': pd.Timestamp.now().isoformat(),
            'shape': df.shape
        }
        history.append(history_entry)
        
        # Update cache
        cache.set(self.history_key, history, timeout=self.CACHE_TIMEOUT)
    
    def _update_metadata_after_transformation(self) -> None:
        """Update metadata after a transformation is applied."""
        metadata = cache.get(self.metadata_key, {})
        history = cache.get(self.history_key, [])
        
        metadata['current_step'] = len(history)
        metadata['total_steps'] = len(history)
        metadata['last_modified'] = pd.Timestamp.now().isoformat()
        
        cache.set(self.metadata_key, metadata, timeout=self.CACHE_TIMEOUT)


def get_session_manager(user_id: int, datasource_id: int) -> DataStudioSessionManager:
    """
    Factory function to get a DataStudioSessionManager instance.
    
    Args:
        user_id: ID of the user
        datasource_id: ID of the datasource
        
    Returns:
        DataStudioSessionManager instance
    """
    return DataStudioSessionManager(user_id, datasource_id)
