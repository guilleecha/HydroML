"""
Mixins for data_tools API views.
Provides common functionality across different API endpoints.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models.datasource import DataSource


class DataSourceAccessMixin:
    """
    Mixin that provides methods for secure DataSource access.
    Ensures users can only access DataSources from their own projects.
    """
    
    def get_datasource(self, datasource_id):
        """
        Get a DataSource ensuring it belongs to the current user's project.
        
        Args:
            datasource_id: UUID of the DataSource
            
        Returns:
            DataSource: The requested DataSource object
            
        Raises:
            Http404: If DataSource doesn't exist or doesn't belong to user
        """
        return get_object_or_404(
            DataSource, 
            id=datasource_id, 
            project__owner=self.request.user
        )
    
    def validate_datasource_status(self, datasource):
        """
        Validate that a DataSource is ready for operations.
        
        Args:
            datasource: DataSource object to validate
            
        Returns:
            dict: Error response if validation fails, None if valid
        """
        if datasource.status != DataSource.Status.READY:
            return {
                'error': f'DataSource "{datasource.name}" no está listo (estado: {datasource.status})'
            }
        
        if not datasource.file:
            return {
                'error': f'DataSource "{datasource.name}" no tiene archivo asociado'
            }
        
        return None


class APIResponseMixin:
    """
    Mixin that provides consistent API response formatting.
    """
    
    def json_response(self, data, status=200):
        """
        Create a standardized JSON response.
        
        Args:
            data: Data to include in response
            status: HTTP status code
            
        Returns:
            JsonResponse: Formatted JSON response
        """
        return JsonResponse(data, status=status)
    
    def error_response(self, message, status=400, error_code=None):
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            status: HTTP status code
            error_code: Optional error code for client handling
            
        Returns:
            JsonResponse: Formatted error response
        """
        response_data = {'error': message}
        if error_code:
            response_data['error_code'] = error_code
        
        return JsonResponse(response_data, status=status)
    
    def success_response(self, data=None, message=None):
        """
        Create a standardized success response.
        
        Args:
            data: Optional data to include
            message: Optional success message
            
        Returns:
            JsonResponse: Formatted success response
        """
        response_data = {}
        if data is not None:
            response_data.update(data)
        if message:
            response_data['message'] = message
        
        return self.json_response(response_data)


class BaseAPIView(LoginRequiredMixin, DataSourceAccessMixin, APIResponseMixin):
    """
    Base class for all data_tools API views.
    Combines common mixins and provides shared functionality.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to add common error handling.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            return self.error_response(
                f'Error inesperado: {str(e)}',
                status=500
            )
