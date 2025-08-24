"""
Session lifecycle management.
Handles pause, resume, reset operations.
"""

import logging

import pandas as pd

from .session_cache import SessionCache
from .session_metadata import SessionMetadataManager, SessionConfig
from .session_history import SessionHistory

logger = logging.getLogger(__name__)


class SessionLifecycle:
    """Handles session lifecycle operations."""
    
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
    
    def reset_to_original(self) -> bool:
        """Reset to original state."""
        try:
            original_df = self.cache.get_dataframe('original')
            if original_df is None:
                return False
            
            self.history.clear_all()
            self.cache.store_dataframe('current', original_df)
            
            metadata = self.metadata_mgr.get()
            if metadata:
                metadata.current_step = 0
                metadata.total_operations = 0
                metadata.status = 'active'
                metadata.last_accessed = pd.Timestamp.now().isoformat()
                self.metadata_mgr.store(metadata)
            
            return True
        except Exception as e:
            logger.error(f"Failed to reset session: {e}")
            return False
    
    def pause_session(self) -> bool:
        """Pause session."""
        try:
            metadata = self.metadata_mgr.get()
            if metadata is None:
                return False
            
            metadata.status = 'paused'
            metadata.last_accessed = pd.Timestamp.now().isoformat()
            return self.metadata_mgr.store(metadata)
        except Exception as e:
            logger.error(f"Failed to pause session: {e}")
            return False
    
    def resume_session(self) -> bool:
        """Resume paused session."""
        try:
            metadata = self.metadata_mgr.get()
            if metadata is None or metadata.status != 'paused':
                return False
            
            metadata.status = 'active'
            metadata.last_accessed = pd.Timestamp.now().isoformat()
            return self.metadata_mgr.store(metadata)
        except Exception as e:
            logger.error(f"Failed to resume session: {e}")
            return False