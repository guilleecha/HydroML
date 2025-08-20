"""
WebSocket Consumer for Data Studio Real-time Updates
Provides live updates for data transformations, progress tracking, and notifications
"""

import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class DataStudioConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Data Studio real-time features
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datasource_id = None
        self.user_id = None
        self.session_group = None
        self.user_group = None
        
    async def connect(self):
        """
        Handle WebSocket connection
        """
        # Get datasource_id from URL route
        self.datasource_id = self.scope['url_route']['kwargs']['datasource_id']
        
        # Check authentication
        user = self.scope.get('user')
        if isinstance(user, AnonymousUser):
            logger.warning(f"Anonymous user attempted WebSocket connection for datasource {self.datasource_id}")
            await self.close(code=4001)
            return
            
        self.user_id = user.id
        
        # Verify user has access to this datasource
        has_access = await self.check_datasource_access(user, self.datasource_id)
        if not has_access:
            logger.warning(f"User {user.id} denied access to datasource {self.datasource_id}")
            await self.close(code=4003)
            return
        
        # Create group names
        self.session_group = f'data_studio_session_{self.datasource_id}'
        self.user_group = f'data_studio_user_{self.user_id}'
        
        # Join groups
        await self.channel_layer.group_add(self.session_group, self.channel_name)
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        
        # Accept connection
        await self.accept()
        
        # Send connection confirmation
        await self.send_message({
            'type': 'connection_established',
            'datasource_id': str(self.datasource_id),
            'timestamp': time.time(),
            'message': 'Real-time updates enabled'
        })
        
        logger.info(f"WebSocket connected: User {self.user_id}, Datasource {self.datasource_id}")
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection
        """
        # Leave groups
        if self.session_group:
            await self.channel_layer.group_discard(self.session_group, self.channel_name)
        if self.user_group:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
            
        logger.info(f"WebSocket disconnected: User {self.user_id}, Code {close_code}")
    
    async def receive(self, text_data):
        """
        Handle messages from WebSocket client
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send_message({
                    'type': 'pong',
                    'timestamp': time.time()
                })
            
            elif message_type == 'subscribe_to_operation':
                operation_id = data.get('operation_id')
                if operation_id:
                    await self.subscribe_to_operation(operation_id)
            
            elif message_type == 'unsubscribe_from_operation':
                operation_id = data.get('operation_id')
                if operation_id:
                    await self.unsubscribe_from_operation(operation_id)
            
            elif message_type == 'request_session_status':
                await self.send_session_status()
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    async def send_message(self, message: Dict[str, Any]):
        """
        Send message to WebSocket client with error handling
        """
        try:
            await self.send(text_data=json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    # Group message handlers
    async def data_transformation_update(self, event):
        """Handle data transformation progress updates"""
        await self.send_message({
            'type': 'transformation_progress',
            'operation_id': event['operation_id'],
            'progress': event['progress'],
            'status': event['status'],
            'message': event.get('message'),
            'timestamp': time.time()
        })
    
    async def session_state_changed(self, event):
        """Handle session state changes"""
        await self.send_message({
            'type': 'session_update',
            'session_info': event['session_info'],
            'timestamp': time.time()
        })
    
    async def bulk_operation_progress(self, event):
        """Handle bulk operation progress updates"""
        await self.send_message({
            'type': 'bulk_progress',
            'operation_id': event['operation_id'],
            'processed': event['processed'],
            'total': event['total'],
            'status': event['status'],
            'errors': event.get('errors', []),
            'timestamp': time.time()
        })
    
    async def data_preview_updated(self, event):
        """Handle data preview updates"""
        await self.send_message({
            'type': 'data_preview',
            'preview_data': event['preview_data'],
            'column_info': event['column_info'],
            'row_count': event.get('row_count'),
            'timestamp': time.time()
        })
    
    async def error_notification(self, event):
        """Handle error notifications"""
        await self.send_message({
            'type': 'error',
            'error_type': event.get('error_type', 'general'),
            'message': event['message'],
            'details': event.get('details'),
            'timestamp': time.time()
        })
    
    async def system_notification(self, event):
        """Handle system notifications"""
        await self.send_message({
            'type': 'notification',
            'level': event.get('level', 'info'),
            'message': event['message'],
            'title': event.get('title'),
            'timestamp': time.time()
        })
    
    # Utility methods
    async def subscribe_to_operation(self, operation_id: str):
        """Subscribe to specific operation updates"""
        operation_group = f'operation_{operation_id}'
        await self.channel_layer.group_add(operation_group, self.channel_name)
        
        await self.send_message({
            'type': 'subscription_confirmed',
            'operation_id': operation_id,
            'message': f'Subscribed to operation {operation_id}'
        })
    
    async def unsubscribe_from_operation(self, operation_id: str):
        """Unsubscribe from specific operation updates"""
        operation_group = f'operation_{operation_id}'
        await self.channel_layer.group_discard(operation_group, self.channel_name)
        
        await self.send_message({
            'type': 'subscription_cancelled',
            'operation_id': operation_id,
            'message': f'Unsubscribed from operation {operation_id}'
        })
    
    async def send_session_status(self):
        """Send current session status"""
        try:
            # This would integrate with the session manager
            session_status = await self.get_session_status()
            await self.send_message({
                'type': 'session_status',
                'session_info': session_status,
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
    
    @sync_to_async
    def check_datasource_access(self, user, datasource_id) -> bool:
        """
        Check if user has access to datasource
        """
        try:
            from projects.models import DataSource
            datasource = DataSource.objects.get(id=datasource_id)
            return datasource.project.owner == user
        except DataSource.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error checking datasource access: {e}")
            return False
    
    @sync_to_async
    def get_session_status(self) -> Dict[str, Any]:
        """
        Get current session status from session manager
        """
        try:
            from data_tools.services.session_manager import get_session_manager
            session_manager = get_session_manager(self.user_id, self.datasource_id)
            return session_manager.get_session_info()
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {'session_exists': False, 'error': str(e)}


class DataStudioNotifier:
    """
    Helper class for sending WebSocket notifications from Django views
    """
    
    @staticmethod
    async def send_transformation_update(datasource_id: str, operation_id: str, 
                                       progress: float, status: str, message: str = None):
        """Send transformation progress update"""
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        if channel_layer:
            await channel_layer.group_send(
                f'data_studio_session_{datasource_id}',
                {
                    'type': 'data_transformation_update',
                    'operation_id': operation_id,
                    'progress': progress,
                    'status': status,
                    'message': message
                }
            )
    
    @staticmethod
    async def send_session_update(datasource_id: str, session_info: Dict[str, Any]):
        """Send session state update"""
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        if channel_layer:
            await channel_layer.group_send(
                f'data_studio_session_{datasource_id}',
                {
                    'type': 'session_state_changed',
                    'session_info': session_info
                }
            )
    
    @staticmethod
    async def send_bulk_progress(operation_id: str, processed: int, total: int, 
                               status: str, errors: list = None):
        """Send bulk operation progress"""
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        if channel_layer:
            await channel_layer.group_send(
                f'operation_{operation_id}',
                {
                    'type': 'bulk_operation_progress',
                    'operation_id': operation_id,
                    'processed': processed,
                    'total': total,
                    'status': status,
                    'errors': errors or []
                }
            )
    
    @staticmethod
    async def send_data_preview_update(datasource_id: str, preview_data: list, 
                                     column_info: list, row_count: int = None):
        """Send data preview update"""
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        if channel_layer:
            await channel_layer.group_send(
                f'data_studio_session_{datasource_id}',
                {
                    'type': 'data_preview_updated',
                    'preview_data': preview_data,
                    'column_info': column_info,
                    'row_count': row_count
                }
            )
    
    @staticmethod
    async def send_error(datasource_id: str, error_type: str, message: str, details: str = None):
        """Send error notification"""
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        if channel_layer:
            await channel_layer.group_send(
                f'data_studio_session_{datasource_id}',
                {
                    'type': 'error_notification',
                    'error_type': error_type,
                    'message': message,
                    'details': details
                }
            )
    
    @staticmethod
    async def send_notification(target: str, level: str, message: str, title: str = None):
        """Send system notification"""
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        if channel_layer:
            await channel_layer.group_send(
                target,  # Can be session or user group
                {
                    'type': 'system_notification',
                    'level': level,
                    'message': message,
                    'title': title
                }
            )


# Synchronous wrapper functions for Django views
def sync_send_transformation_update(datasource_id: str, operation_id: str, 
                                  progress: float, status: str, message: str = None):
    """Synchronous wrapper for sending transformation updates"""
    import asyncio
    from asgiref.sync import async_to_sync
    
    async_to_sync(DataStudioNotifier.send_transformation_update)(
        datasource_id, operation_id, progress, status, message
    )


def sync_send_session_update(datasource_id: str, session_info: Dict[str, Any]):
    """Synchronous wrapper for sending session updates"""
    from asgiref.sync import async_to_sync
    
    async_to_sync(DataStudioNotifier.send_session_update)(datasource_id, session_info)


def sync_send_bulk_progress(operation_id: str, processed: int, total: int, 
                          status: str, errors: list = None):
    """Synchronous wrapper for sending bulk progress updates"""
    from asgiref.sync import async_to_sync
    
    async_to_sync(DataStudioNotifier.send_bulk_progress)(
        operation_id, processed, total, status, errors
    )


def sync_send_error(datasource_id: str, error_type: str, message: str, details: str = None):
    """Synchronous wrapper for sending error notifications"""
    from asgiref.sync import async_to_sync
    
    async_to_sync(DataStudioNotifier.send_error)(datasource_id, error_type, message, details)