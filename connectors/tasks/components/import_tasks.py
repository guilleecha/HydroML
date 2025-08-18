"""
Database import and data synchronization tasks for connectors app.
"""
import logging
from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from connectors.models import DatabaseConnection
from connectors.services import DatabaseConnectionService
from projects.models import DataSource, Project

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def import_data_from_database_task(
    self,
    connection_id: str,
    query: str,
    datasource_name: str,
    project_id: str,
    user_id: int,
    description: str = None
):
    """
    Celery task to import data from a database connection.
    
    Args:
        connection_id: UUID of the DatabaseConnection
        query: SQL query to execute
        datasource_name: Name for the new DataSource
        project_id: UUID of the Project to create the DataSource in
        user_id: ID of the user creating the DataSource
        description: Optional description
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting data import...'}
        )
        
        # Get connection, project, and user
        try:
            connection = DatabaseConnection.objects.get(id=connection_id)
            project = Project.objects.get(id=project_id)
            user = User.objects.get(id=user_id)
        except (DatabaseConnection.DoesNotExist, Project.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f"Task failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        # Verify user owns the connection and project
        if connection.user != user or project.owner != user:
            error_msg = "User does not have permission to use this connection or project"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Testing database connection...'}
        )
        
        # Test connection first
        success, message = DatabaseConnectionService.test_connection(connection)
        if not success:
            logger.error(f"Connection test failed: {message}")
            return {'success': False, 'error': f"Connection failed: {message}"}
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 40, 'total': 100, 'status': 'Executing query...'}
        )
        
        # Execute query and create DataSource
        success, result = DatabaseConnectionService.create_datasource_from_query(
            connection=connection,
            query=query,
            datasource_name=datasource_name,
            project=project,
            description=description
        )
        
        if not success:
            logger.error(f"DataSource creation failed: {result}")
            return {'success': False, 'error': result}
        
        datasource = result
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Finalizing import...'}
        )
        
        # Send notification email if configured
        if hasattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED') and settings.EMAIL_NOTIFICATIONS_ENABLED:
            try:
                send_mail(
                    subject=f'Data Import Complete: {datasource_name}',
                    message=f'Your data import from {connection.name} has completed successfully.\n\n'
                           f'DataSource: {datasource_name}\n'
                           f'Rows: {datasource.quality_report.get("rows", "Unknown")}\n'
                           f'Columns: {len(datasource.quality_report.get("columns", []))}\n',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception as e:
                logger.warning(f"Failed to send notification email: {str(e)}")
        
        # Complete
        logger.info(f"Data import task completed successfully for {datasource_name}")
        return {
            'success': True,
            'datasource_id': str(datasource.id),
            'datasource_name': datasource.name,
            'rows': datasource.quality_report.get('rows', 0),
            'columns': len(datasource.quality_report.get('columns', []))
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in import task: {str(e)}")
        return {'success': False, 'error': f"Unexpected error: {str(e)}"}
