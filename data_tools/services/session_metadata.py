"""
Session metadata management.
Handles session state and configuration.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import timedelta

import pandas as pd
from django.core.cache import cache
from django.contrib.auth.models import User

from .secure_serialization import serialize_metadata, deserialize_metadata

logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    """Configuration settings for session management."""
    timeout_minutes: int = 240
    max_history_entries: int = 50
    compression_level: int = 6
    persist_to_file: bool = False
    cleanup_on_timeout: bool = True
    
    @classmethod
    def default(cls) -> 'SessionConfig':
        """Get default configuration."""
        return cls()
    
    @classmethod
    def from_user_preferences(cls, user: User) -> 'SessionConfig':
        """Load configuration from user preferences."""
        return cls.default()


@dataclass
class SessionMetadata:
    """Session metadata."""
    user_id: int
    datasource_id: int
    created_at: str
    last_accessed: str
    original_shape: tuple
    current_step: int
    total_operations: int
    status: str
    config: SessionConfig


class SessionMetadataManager:
    """Manages session metadata operations."""
    
    def __init__(self, metadata_key: str, timeout: int):
        self.metadata_key = metadata_key
        self.timeout = timeout
    
    def create(self, user_id: int, datasource_id: int, df_shape: tuple, 
               config: SessionConfig) -> SessionMetadata:
        """Create new session metadata."""
        return SessionMetadata(
            user_id=user_id,
            datasource_id=datasource_id,
            created_at=pd.Timestamp.now().isoformat(),
            last_accessed=pd.Timestamp.now().isoformat(),
            original_shape=df_shape,
            current_step=0,
            total_operations=0,
            status='active',
            config=config
        )
    
    def store(self, metadata: SessionMetadata) -> bool:
        """Store metadata in cache."""
        try:
            metadata_bytes = serialize_metadata(asdict(metadata))
            cache.set(self.metadata_key, metadata_bytes, timeout=self.timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to store metadata: {e}")
            return False
    
    def get(self) -> Optional[SessionMetadata]:
        """Get metadata from cache."""
        try:
            metadata_bytes = cache.get(self.metadata_key)
            if metadata_bytes is None:
                return None
            
            metadata_dict = deserialize_metadata(metadata_bytes)
            
            # Convert config back to SessionConfig object
            if 'config' in metadata_dict and isinstance(metadata_dict['config'], dict):
                metadata_dict['config'] = SessionConfig(**metadata_dict['config'])
            
            return SessionMetadata(**metadata_dict)
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return None
    
    def update_last_accessed(self) -> bool:
        """Update last accessed timestamp."""
        metadata = self.get()
        if metadata:
            metadata.last_accessed = pd.Timestamp.now().isoformat()
            return self.store(metadata)
        return False
    
    def is_expired(self, metadata: SessionMetadata) -> bool:
        """Check if session has expired."""
        return _is_session_expired(metadata)
    
    def get_expiration_time(self, metadata: SessionMetadata) -> str:
        """Get session expiration timestamp."""
        return _get_session_expiration_time(metadata)


def _is_session_expired(metadata: SessionMetadata) -> bool:
    """Utility: Check if session has expired."""
    try:
        last_accessed = pd.Timestamp(metadata.last_accessed)
        timeout_delta = timedelta(minutes=metadata.config.timeout_minutes)
        return pd.Timestamp.now() > (last_accessed + timeout_delta)
    except Exception:
        return True


def _get_session_expiration_time(metadata: SessionMetadata) -> str:
    """Utility: Get session expiration timestamp."""
    try:
        last_accessed = pd.Timestamp(metadata.last_accessed)
        timeout_delta = timedelta(minutes=metadata.config.timeout_minutes)
        return (last_accessed + timeout_delta).isoformat()
    except Exception:
        return pd.Timestamp.now().isoformat()