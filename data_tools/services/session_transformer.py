"""
Session transformation operations.
Handles apply, undo, redo operations with history tracking.
"""

import logging
from typing import Optional, Dict, Any

import pandas as pd

from .session_cache import SessionCache
from .session_metadata import SessionMetadataManager, SessionConfig
from .session_history import SessionHistory

logger = logging.getLogger(__name__)


class SessionTransformer:
    """Handles transformation operations with history tracking."""
    
    def __init__(self, user_id: int, datasource_id: int, config: SessionConfig):
        self.user_id = user_id
        self.datasource_id = datasource_id
        self.config = config
        
        self.cache = SessionCache(user_id, datasource_id, config.timeout_minutes)
        
        session_prefix = f"unified_session:{user_id}:{datasource_id}"
        metadata_key = f"{session_prefix}:metadata"
        timeout = config.timeout_minutes * 60
        
        self.metadata_mgr = SessionMetadataManager(metadata_key, timeout)
        self.history = SessionHistory(session_prefix, timeout, config.max_history_entries)
    
    def apply_transformation(self, df_transformed: pd.DataFrame, 
                           operation_name: str, 
                           operation_params: Dict[str, Any] = None) -> bool:
        """Apply transformation with history tracking."""
        return _apply_transformation_with_history(
            self.metadata_mgr, self.cache, self.history, 
            df_transformed, operation_name, operation_params
        )
    
    def undo_operation(self) -> Optional[pd.DataFrame]:
        """Undo last operation."""
        try:
            metadata = self.metadata_mgr.get()
            if metadata is None or metadata.current_step <= 0:
                return None
            
            previous_step = metadata.current_step - 1
            previous_df = self.history.get_entry(previous_step)
            
            if previous_df is None:
                return None
            
            self.cache.store_dataframe('current', previous_df)
            
            metadata.current_step = previous_step
            metadata.last_accessed = pd.Timestamp.now().isoformat()
            self.metadata_mgr.store(metadata)
            
            return previous_df
        except Exception as e:
            logger.error(f"Failed to undo operation: {e}")
            return None
    
    def redo_operation(self) -> Optional[pd.DataFrame]:
        """Redo next operation."""
        try:
            metadata = self.metadata_mgr.get()
            if metadata is None or metadata.current_step >= metadata.total_operations:
                return None
            
            # For redo, we need to re-apply the transformation stored in history
            # History stores the "before" state, so we need the transformation result
            # This is a simplified implementation - in a full system, we'd store 
            # the transformation details and re-apply them
            
            # For now, we'll use a workaround: assume redo means going back to 
            # the last transformed state which should be in cache as 'last_transformed'
            # Let's check if we have this stored somewhere
            
            # Since our current architecture doesn't store transformation results,
            # we'll implement a simple cache-based approach
            from django.core.cache import cache as django_cache
            redo_key = f"unified_session:{self.user_id}:{self.datasource_id}:redo:{metadata.current_step}"
            redo_df_bytes = django_cache.get(redo_key)
            
            if redo_df_bytes:
                from .secure_serialization import deserialize_dataframe
                redo_df = deserialize_dataframe(redo_df_bytes)
                
                self.cache.store_dataframe('current', redo_df)
                
                metadata.current_step += 1
                metadata.last_accessed = pd.Timestamp.now().isoformat()
                self.metadata_mgr.store(metadata)
                
                return redo_df
            
            # If no redo data is available, we can't redo
            return None
            
        except Exception as e:
            logger.error(f"Failed to redo operation: {e}")
            return None


def _apply_transformation_with_history(metadata_mgr, cache, history, 
                                     df_transformed, operation_name, operation_params):
    """Utility: Apply transformation with history tracking."""
    try:
        metadata = metadata_mgr.get()
        if metadata is None:
            return False
        
        current_df = cache.get_dataframe('current')
        if current_df is None:
            return False
        
        # Add to history
        history.add_entry(current_df, operation_name, operation_params,
                         metadata.current_step, df_transformed)
        
        # Store the transformation result for redo purposes
        from .secure_serialization import serialize_dataframe
        from django.core.cache import cache as django_cache
        user_id = metadata.user_id
        datasource_id = metadata.datasource_id
        redo_key = f"unified_session:{user_id}:{datasource_id}:redo:{metadata.current_step}"
        timeout = metadata.config.timeout_minutes * 60
        django_cache.set(redo_key, serialize_dataframe(df_transformed), timeout=timeout)
        
        # Update current state
        cache.store_dataframe('current', df_transformed)
        
        # Update metadata
        metadata.current_step += 1
        metadata.total_operations += 1
        metadata.last_accessed = pd.Timestamp.now().isoformat()
        metadata_mgr.store(metadata)
        
        # Cleanup old history
        history.cleanup_old(metadata.total_operations)
        
        return True
    except Exception as e:
        logger.error(f"Failed to apply transformation: {e}")
        return False