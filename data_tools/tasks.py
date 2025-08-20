"""
Modular Celery tasks for the data_tools app.

This module serves as the main entry point for data_tools tasks,
using the new modular architecture that follows CLAUDE.md principles.
"""

# Import from new modular architecture
from .tasks import (
    convert_file_to_parquet_task,
    process_datasource_task,
    deep_missing_data_analysis_task
)

# Re-export for backward compatibility
__all__ = [
    'convert_file_to_parquet_task',
    'process_datasource_task',
    'deep_missing_data_analysis_task'
]
