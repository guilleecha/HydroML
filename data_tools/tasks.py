"""
Modular Celery tasks for the data_tools app.

This module serves as the main entry point for data_tools tasks,
importing from the old tasks file for backward compatibility.
"""

# Import tasks from the old tasks file for now
from .tasks_old import convert_file_to_parquet_task, process_datasource_task, deep_missing_data_analysis_task

# Re-export for backward compatibility
__all__ = [
    'convert_file_to_parquet_task',
    'process_datasource_task',
    'deep_missing_data_analysis_task'
]
