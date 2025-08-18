"""
Database connection testing and management tasks for connectors app.
"""
import logging
from celery import shared_task
from django.contrib.auth.models import User

from connectors.models import DatabaseConnection
from connectors.services import DatabaseConnectionService

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def test_database_connection_task(self, connection_id: str, user_id: int):
    """
    Celery task to test a database connection.
    
    Args:
        connection_id: UUID of the DatabaseConnection
        user_id: ID of the user testing the connection
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Testing connection...'}
        )
        
        # Get connection and user
        try:
            connection = DatabaseConnection.objects.get(id=connection_id)
            user = User.objects.get(id=user_id)
        except (DatabaseConnection.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f"Task failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        # Verify user owns the connection
        if connection.user != user:
            error_msg = "User does not have permission to test this connection"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Test connection
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Connecting to database...'}
        )
        
        success, message = DatabaseConnectionService.test_connection(connection)
        
        logger.info(f"Connection test completed for {connection.name}: {message}")
        return {
            'success': success,
            'message': message,
            'connection_name': connection.name
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in connection test task: {str(e)}")
        return {'success': False, 'error': f"Unexpected error: {str(e)}"}


@shared_task(bind=True)
def get_database_tables_task(self, connection_id: str, user_id: int):
    """
    Celery task to get list of tables from a database connection.
    
    Args:
        connection_id: UUID of the DatabaseConnection
        user_id: ID of the user requesting tables
    """
    try:
        # Get connection and user
        try:
            connection = DatabaseConnection.objects.get(id=connection_id)
            user = User.objects.get(id=user_id)
        except (DatabaseConnection.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f"Task failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        # Verify user owns the connection
        if connection.user != user:
            error_msg = "User does not have permission to access this connection"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Get tables
        success, result = DatabaseConnectionService.get_table_list(connection)
        
        if success:
            logger.info(f"Retrieved {len(result)} tables from {connection.name}")
            return {
                'success': True,
                'tables': result,
                'connection_name': connection.name
            }
        else:
            logger.error(f"Failed to get tables from {connection.name}: {result}")
            return {'success': False, 'error': result}
        
    except Exception as e:
        logger.error(f"Unexpected error in get tables task: {str(e)}")
        return {'success': False, 'error': f"Unexpected error: {str(e)}"}
