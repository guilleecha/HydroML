"""
Orchestrator for session operations.
Delegates to focused components following CLAUDE.md philosophy.
"""

import logging
from typing import Optional, Dict, Any

import pandas as pd

from .session_initializer import SessionInitializer
from .session_transformer import SessionTransformer
from .session_lifecycle import SessionLifecycle
from .session_cache import SessionCache
from .session_metadata import SessionMetadataManager, SessionConfig
from .session_history import SessionHistory

logger = logging.getLogger(__name__)


class SessionOperations:
    """Orchestrates session operations using focused components."""
    
    def __init__(self, user_id: int, datasource_id: int, config: SessionConfig):
        self.user_id = user_id
        self.datasource_id = datasource_id
        self.config = config
        
        # Initialize focused components
        self.initializer = SessionInitializer(user_id, datasource_id, config)
        self.transformer = SessionTransformer(user_id, datasource_id, config)
        self.lifecycle = SessionLifecycle(user_id, datasource_id, config)
        
        # Expose commonly used components for direct access
        self.metadata_mgr = self.initializer.metadata_mgr
        self.history = self.transformer.history
        self.cache = self.initializer.cache
    
    def initialize_session(self, df: pd.DataFrame, force: bool = False) -> bool:
        """Initialize session."""
        return self.initializer.initialize_session(df, force)
    
    def session_exists(self) -> bool:
        """Check if session exists."""
        return self.initializer.session_exists()
    
    def apply_transformation(self, df_transformed: pd.DataFrame, 
                           operation_name: str, 
                           operation_params: Dict[str, Any] = None) -> bool:
        """Apply transformation."""
        return self.transformer.apply_transformation(df_transformed, operation_name, operation_params)
    
    def undo_operation(self) -> Optional[pd.DataFrame]:
        """Undo operation."""
        return self.transformer.undo_operation()
    
    def redo_operation(self) -> Optional[pd.DataFrame]:
        """Redo operation."""
        return self.transformer.redo_operation()
    
    def reset_to_original(self) -> bool:
        """Reset to original."""
        return self.lifecycle.reset_to_original()
    
    def pause_session(self) -> bool:
        """Pause session."""
        return self.lifecycle.pause_session()
    
    def resume_session(self) -> bool:
        """Resume session."""
        return self.lifecycle.resume_session()
    
    def clear_session(self) -> bool:
        """Clear session."""
        return self.initializer.clear_session()