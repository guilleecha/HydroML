"""
Session history management for unified sessions.
Handles undo/redo operations and history cleanup.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, asdict

import pandas as pd
from django.core.cache import cache

from .secure_serialization import serialize_dataframe, deserialize_dataframe, serialize_metadata, deserialize_metadata

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """Single operation in session history."""
    operation_name: str
    operation_params: Dict[str, Any]
    timestamp: str
    shape_before: Tuple[int, int]
    shape_after: Tuple[int, int]
    dataframe_key: str


class SessionHistory:
    """Manages session history for undo/redo operations."""
    
    def __init__(self, session_prefix: str, timeout: int, max_entries: int = 50):
        self.session_prefix = session_prefix
        self.history_prefix = f"{session_prefix}:history"
        self.timeout = timeout
        self.max_entries = max_entries
    
    def add_entry(self, df: pd.DataFrame, operation_name: str, 
                  operation_params: Dict[str, Any], current_step: int,
                  df_transformed: pd.DataFrame) -> bool:
        """Add new history entry."""
        try:
            history_key = f"{self.history_prefix}:{current_step}"
            
            # Store DataFrame state before transformation
            cache.set(history_key, serialize_dataframe(df), timeout=self.timeout)
            
            # Create and store history entry metadata
            entry = HistoryEntry(
                operation_name=operation_name,
                operation_params=operation_params or {},
                timestamp=pd.Timestamp.now().isoformat(),
                shape_before=df.shape,
                shape_after=df_transformed.shape,
                dataframe_key=history_key
            )
            
            history_meta_key = f"{history_key}:meta"
            cache.set(history_meta_key, serialize_metadata(asdict(entry)), timeout=self.timeout)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add history entry: {e}")
            return False
    
    def get_entry(self, step: int) -> Optional[pd.DataFrame]:
        """Get DataFrame from history step."""
        try:
            history_key = f"{self.history_prefix}:{step}"
            df_bytes = cache.get(history_key)
            if df_bytes is None:
                return None
            return deserialize_dataframe(df_bytes)
        except Exception as e:
            logger.error(f"Failed to get history entry {step}: {e}")
            return None
    
    def get_summary(self, current_step: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history summary for UI."""
        summary = []
        
        for i in range(min(current_step, limit)):
            history_meta_key = f"{self.history_prefix}:{i}:meta"
            history_data = cache.get(history_meta_key)
            
            if history_data:
                try:
                    entry = deserialize_metadata(history_data)
                    summary.append({
                        'step': i,
                        'operation_name': entry.get('operation_name', 'Unknown'),
                        'timestamp': entry.get('timestamp'),
                        'shape_before': entry.get('shape_before'),
                        'shape_after': entry.get('shape_after')
                    })
                except Exception:
                    continue
        
        return summary
    
    def cleanup_old(self, total_operations: int) -> None:
        """Remove old history entries."""
        _cleanup_old_entries(self.history_prefix, total_operations, self.max_entries)
    
    def clear_entry(self, step: int) -> None:
        """Clear specific history entry."""
        _clear_history_entry(self.history_prefix, step)
    
    def clear_all(self, total_operations: int = None) -> None:
        """Clear all history entries."""
        _clear_all_entries(self.history_prefix, total_operations)


def _cleanup_old_entries(history_prefix: str, total_ops: int, max_entries: int) -> None:
    """Utility: Remove old history entries."""
    if total_ops > max_entries:
        entries_to_remove = total_ops - max_entries
        for i in range(entries_to_remove):
            _clear_history_entry(history_prefix, i)


def _clear_history_entry(history_prefix: str, step: int) -> None:
    """Utility: Clear specific history entry."""
    history_key = f"{history_prefix}:{step}"
    history_meta_key = f"{history_key}:meta"
    cache.delete(history_key)
    cache.delete(history_meta_key)


def _clear_all_entries(history_prefix: str, total_operations: int = None) -> None:
    """Utility: Clear all history entries."""
    operations = total_operations or 100  # Safe fallback
    for i in range(operations):
        _clear_history_entry(history_prefix, i)