"""
Base mixins for data_tools API views.
"""

from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from projects.models.datasource import DataSource
import logging
import json

logger = logging.getLogger(__name__)


class BaseAPIView(View):
    """
    Base API view with common functionality for data_tools APIs.
    """
    
    def get_datasource(self, datasource_id):
        """
        Get DataSource by ID with proper error handling.
        
        Args:
            datasource_id: UUID of the DataSource
            
        Returns:
            DataSource: The DataSource instance
            
        Raises:
            Http404: If DataSource is not found
        """
        return get_object_or_404(DataSource, id=datasource_id)
    
    def validate_datasource_status(self, datasource):
        """
        Validate DataSource status and file existence.
        
        Args:
            datasource: DataSource instance to validate
            
        Returns:
            dict or None: Error dict if validation fails, None if valid
        """
        # Check if DataSource is ready
        if datasource.status != DataSource.Status.READY:
            return {
                'error': f'DataSource no está listo. Estado actual: {datasource.get_status_display()}'
            }
        
        # Check if file exists
        if not datasource.file:
            return {
                'error': 'No hay archivo asociado con esta fuente de datos'
            }
        
        # Check if file path exists on disk
        try:
            if not datasource.file.path:
                return {
                    'error': 'Ruta de archivo no válida'
                }
        except ValueError:
            return {
                'error': 'Archivo no accesible'
            }
        
        return None  # All validations passed
    
    def handle_exception(self, exc):
        """
        Custom exception handling for consistent error responses.
        """
        logger.error(f"API error in {self.__class__.__name__}: {str(exc)}")
        
        status_code = getattr(exc, 'status_code', 500)
        
        return JsonResponse(
            {'error': str(exc)}, 
            status=status_code
        )
    
    def success_response(self, data=None, message=None, status_code=200):
        """
        Standard success response format.
        """
        response_data = {
            'success': True
        }
        
        if message:
            response_data['message'] = message
            
        if data is not None:
            response_data['data'] = data
            
        return JsonResponse(response_data, status=status_code)
    
    def error_response(self, message, status_code=400):
        """
        Standard error response format.
        """
        return JsonResponse(
            {
                'success': False,
                'error': message
            },
            status=status_code
        )
