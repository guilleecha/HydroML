"""
Session initialization and validation.
Handles session creation, existence checks, and cleanup.
"""

import logging

import pandas as pd

from .session_cache import SessionCache
from .session_metadata import SessionMetadataManager, SessionConfig

logger = logging.getLogger(__name__)


class SessionInitializer:
    """Handles session initialization and validation."""
    
    def __init__(self, user_id: int, datasource_id: int, config: SessionConfig):
        self.user_id = user_id
        self.datasource_id = datasource_id
        self.config = config
        
        self.cache = SessionCache(user_id, datasource_id, config.timeout_minutes)
        
        session_prefix = f"unified_session:{user_id}:{datasource_id}"
        metadata_key = f"{session_prefix}:metadata"
        timeout = config.timeout_minutes * 60
        
        self.metadata_mgr = SessionMetadataManager(metadata_key, timeout)
    
    def initialize_session(self, df: pd.DataFrame, force: bool = False) -> bool:
        """Initialize a new session."""
        try:
            if not force and self.session_exists():
                logger.warning(f"Session already exists for user {self.user_id}")
                return False
            
            if force:
                self.clear_session()
            
            # Store original and current DataFrames
            self.cache.store_dataframe('original', df)
            self.cache.store_dataframe('current', df)
            
            # Create and store metadata
            metadata = self.metadata_mgr.create(self.user_id, self.datasource_id, 
                                              df.shape, self.config)
            self.metadata_mgr.store(metadata)
            
            logger.info(f"Initialized session for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            return False
    
    def session_exists(self) -> bool:
        """Check if session exists and is valid."""
        try:
            metadata = self.metadata_mgr.get()
            if metadata is None:
                return False
            
            if self.metadata_mgr.is_expired(metadata):
                if self.config.cleanup_on_timeout:
                    self.clear_session()
                return False
            
            return self.cache.exists()
        except Exception as e:
            logger.error(f"Error checking session existence: {e}")
            return False
    
    def clear_session(self) -> bool:
        """Clear entire session."""
        try:
            # Clear cache data
            self.cache.clear_all()
            
            # Clear metadata
            from django.core.cache import cache
            cache.delete(self.metadata_mgr.metadata_key)
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False