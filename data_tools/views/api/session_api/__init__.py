"""
Session API Package - Refactored session management API views.
Organized following CLAUDE.md architecture philosophy.
"""

# Import all views for URL patterns
from .session_lifecycle_views import initialize_session, get_session_status, clear_session, save_as_new_datasource
from .session_operations_views import undo_operation, redo_operation
from .column_transformation_views import rename_column, change_column_type, fill_missing_values
from .data_analysis_views import get_column_statistics

__all__ = [
    'initialize_session', 'get_session_status', 'clear_session', 'save_as_new_datasource',
    'undo_operation', 'redo_operation', 
    'rename_column', 'change_column_type', 'fill_missing_values',
    'get_column_statistics'
]