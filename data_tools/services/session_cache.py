"""
Redis cache operations for session management.
Simple, focused class for caching DataFrame operations.
"""

import logging
from typing import Optional
from django.core.cache import cache
from .secure_serialization import serialize_dataframe, deserialize_dataframe, serialize_metadata, deserialize_metadata

logger = logging.getLogger(__name__)


class SessionCache:
    """Simple Redis cache operations for session data."""
    
    def __init__(self, user_id: int, datasource_id: int, timeout_minutes: int = 240):
        self.user_id = user_id
        self.datasource_id = datasource_id
        self.timeout = timeout_minutes * 60
        self.prefix = f"session:{user_id}:{datasource_id}"
        
    def store_dataframe(self, key_suffix: str, df) -> bool:
        """Store DataFrame in cache."""
        try:
            key = f"{self.prefix}:{key_suffix}"
            data = serialize_dataframe(df)
            cache.set(key, data, timeout=self.timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to store DataFrame {key_suffix}: {e}")
            return False
    
    def get_dataframe(self, key_suffix: str):
        """Get DataFrame from cache."""
        try:
            key = f"{self.prefix}:{key_suffix}"
            data = cache.get(key)
            if data is None:
                return None
            return deserialize_dataframe(data)
        except Exception as e:
            logger.error(f"Failed to get DataFrame {key_suffix}: {e}")
            return None
    
    def store_metadata(self, data: dict) -> bool:
        """Store session metadata."""
        try:
            key = f"{self.prefix}:meta"
            metadata_bytes = serialize_metadata(data)
            cache.set(key, metadata_bytes, timeout=self.timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to store metadata: {e}")
            return False
    
    def get_metadata(self) -> Optional[dict]:
        """Get session metadata."""
        try:
            key = f"{self.prefix}:meta"
            data = cache.get(key)
            if data is None:
                return None
            return deserialize_metadata(data)
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return None
    
    def delete_key(self, key_suffix: str) -> bool:
        """Delete specific key."""
        try:
            key = f"{self.prefix}:{key_suffix}"
            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete key {key_suffix}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all session data."""
        try:
            keys = ['current', 'original', 'meta']
            for key_suffix in keys:
                self.delete_key(key_suffix)
            # Clear history keys
            for i in range(50):  # Max history entries
                self.delete_key(f"history:{i}")
                self.delete_key(f"history:{i}:meta")
            return True
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False
    
    def exists(self) -> bool:
        """Check if session exists."""
        try:
            key = f"{self.prefix}:current"
            return cache.get(key) is not None
        except Exception:
            return False