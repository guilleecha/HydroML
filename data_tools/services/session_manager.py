"""
Session Manager for Data Studio.
REFACTORED: Now delegates to focused components following CLAUDE.md philosophy.
"""

import logging
from typing import Optional, Dict, Any

# Import from focused components
from .session_operations import SessionOperations
from .session_metadata import SessionConfig
from .session_cache import SessionCache

logger = logging.getLogger(__name__)


class DataStudioSessionManager:
    """Simplified session manager delegating to focused components."""
    
    def __init__(self, user_id: int, datasource_id: int, config: SessionConfig = None):
        self.user_id = user_id
        self.datasource_id = datasource_id
        self.config = config or SessionConfig.default()
        
        self.operations = SessionOperations(user_id, datasource_id, self.config)
        self.cache = SessionCache(user_id, datasource_id, self.config.timeout_minutes)
    
    def initialize_session(self, df, force: bool = False) -> bool:
        """Initialize session."""
        return self.operations.initialize_session(df, force)
    
    def session_exists(self) -> bool:
        """Check if session exists."""
        return self.operations.session_exists()
    
    def get_current_dataframe(self):
        """Get current DataFrame."""
        self.operations.metadata_mgr.update_last_accessed()
        return self.cache.get_dataframe('current')
    
    def get_original_dataframe(self):
        """Get original DataFrame."""
        return self.cache.get_dataframe('original')
    
    def apply_transformation(self, df_transformed, operation_name: str, 
                           operation_params: Dict[str, Any] = None) -> bool:
        """Apply transformation."""
        return self.operations.apply_transformation(df_transformed, operation_name, operation_params)
    
    def undo_operation(self):
        """Undo last operation."""
        return self.operations.undo_operation()
    
    def redo_operation(self):
        """Redo next operation."""
        return self.operations.redo_operation()
    
    def reset_to_original(self) -> bool:
        """Reset to original state."""
        return self.operations.reset_to_original()
    
    def pause_session(self) -> bool:
        """Pause session."""
        return self.operations.pause_session()
    
    def resume_session(self) -> bool:
        """Resume session."""
        return self.operations.resume_session()
    
    def clear_session(self) -> bool:
        """Clear session."""
        return self.operations.clear_session()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return _format_session_info(self.operations, self.get_current_dataframe())


def _format_session_info(operations, current_df) -> Dict[str, Any]:
    """Utility: Format session information."""
    try:
        metadata = operations.metadata_mgr.get()
        if metadata is None:
            return {'session_exists': False}
        
        history_summary = operations.history.get_summary(metadata.current_step)
        
        return {
            'session_exists': True,
            'user_id': metadata.user_id,
            'datasource_id': metadata.datasource_id,
            'created_at': metadata.created_at,
            'last_accessed': metadata.last_accessed,
            'status': metadata.status,
            'current_shape': current_df.shape if current_df is not None else None,
            'original_shape': metadata.original_shape,
            'current_step': metadata.current_step,
            'total_operations': metadata.total_operations,
            'can_undo': metadata.current_step > 0,
            'can_redo': metadata.current_step < metadata.total_operations,
            'operations_history': history_summary,
            'timeout_minutes': metadata.config.timeout_minutes,
            'expires_at': operations.metadata_mgr.get_expiration_time(metadata),
            'is_expired': operations.metadata_mgr.is_expired(metadata)
        }
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        return {'session_exists': False}


def get_session_manager(user_id: int, datasource_id: int, 
                               config: SessionConfig = None) -> DataStudioSessionManager:
    """Factory function for creating session manager."""
    return DataStudioSessionManager(user_id, datasource_id, config)