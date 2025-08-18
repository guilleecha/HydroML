"""
Modular Celery tasks for the connectors app.

This module serves as the main entry point for connectors tasks,
importing from specialized components for better maintainability.
"""

# Import tasks from modular components
from .tasks.components.import_tasks import import_data_from_database_task
from .tasks.components.connection_tasks import test_database_connection_task, get_database_tables_task

# Re-export for backward compatibility
__all__ = [
    'import_data_from_database_task',
    'test_database_connection_task',
    'get_database_tables_task'
]
