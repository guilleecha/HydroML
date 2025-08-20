"""
Export API views for managing export jobs and templates.
Handles CRUD operations and custom actions for data export functionality.
"""

import os
import logging
from django.views import View
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from .mixins import BaseAPIView
from data_tools.models.export_job import ExportJob
from data_tools.models.export_template import ExportTemplate
from data_tools.serializers.export_serializers import ExportJobSerializer, ExportTemplateSerializer

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ExportJobAPIView(BaseAPIView, View):
    """
    API view for ExportJob operations.
    Supports CRUD operations and custom actions for export job management.
    """
    
    def get(self, request, pk=None):
        """
        Retrieve export job(s).
        
        Args:
            request: HTTP request object
            pk: Optional UUID of specific export job
            
        Returns:
            JsonResponse: Export job data or list of export jobs
        """
        try:
            if pk:
                # Retrieve specific export job
                return self._get_export_job(request, pk)
            else:
                # List export jobs with pagination and filtering
                return self._list_export_jobs(request)
                
        except Exception as e:
            logger.error(f"Error in ExportJobAPIView.get: {str(e)}")
            return self.error_response('Error retrieving export jobs')
    
    def post(self, request, pk=None):
        """
        Create a new export job.
        
        Args:
            request: HTTP request object
            pk: Not used for creation
            
        Returns:
            JsonResponse: Created export job data
        """
        if pk:
            return self.error_response('Invalid endpoint for creation', status_code=405)
        
        try:
            return self._create_export_job(request)
        except Exception as e:
            logger.error(f"Error in ExportJobAPIView.post: {str(e)}")
            return self.error_response('Error creating export job')
    
    def delete(self, request, pk=None):
        """
        Delete an export job.
        
        Args:
            request: HTTP request object
            pk: UUID of export job to delete
            
        Returns:
            JsonResponse: Success or error response
        """
        if not pk:
            return self.error_response('Export job ID is required', status_code=400)
        
        try:
            return self._delete_export_job(request, pk)
        except Exception as e:
            logger.error(f"Error in ExportJobAPIView.delete: {str(e)}")
            return self.error_response('Error deleting export job')
    
    def _get_export_job(self, request, pk):
        """Get specific export job by ID."""
        export_job = get_object_or_404(ExportJob, id=pk, user=request.user)
        
        return self.success_response(
            data=ExportJobSerializer.to_dict(export_job),
            message='Export job retrieved successfully'
        )
    
    def _list_export_jobs(self, request):
        """List export jobs with pagination and filtering."""
        queryset = ExportJob.objects.filter(user=request.user)
        
        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter and status_filter in dict(ExportJob.STATUS_CHOICES):
            queryset = queryset.filter(status=status_filter)
        
        format_filter = request.GET.get('format')
        if format_filter and format_filter in dict(ExportJob.FORMAT_CHOICES):
            queryset = queryset.filter(format=format_filter)
        
        datasource_filter = request.GET.get('datasource')
        if datasource_filter:
            queryset = queryset.filter(datasource__id=datasource_filter)
        
        # Search by datasource name
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(datasource__name__icontains=search) |
                Q(error_message__icontains=search)
            )
        
        # Order by creation date (newest first)
        queryset = queryset.select_related('datasource', 'user').order_by('-created_at')
        
        # Pagination
        page = request.GET.get('page', 1)
        page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 per page
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize export jobs
        export_jobs = [
            ExportJobSerializer.to_dict(job) for job in page_obj.object_list
        ]
        
        return self.success_response(
            data={
                'export_jobs': export_jobs,
                'pagination': {
                    'total_count': paginator.count,
                    'page_count': paginator.num_pages,
                    'current_page': page_obj.number,
                    'has_previous': page_obj.has_previous(),
                    'has_next': page_obj.has_next(),
                    'page_size': page_size
                }
            },
            message='Export jobs retrieved successfully'
        )
    
    def _create_export_job(self, request):
        """Create a new export job."""
        import json
        
        # Parse request data
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                # Handle JSON string fields from form data
                if 'filters' in data and isinstance(data['filters'], str):
                    data['filters'] = json.loads(data['filters'])
        except (json.JSONDecodeError, ValueError) as e:
            return self.error_response('Invalid JSON data')
        
        # Validate data
        try:
            validated_data = ExportJobSerializer.validate_create_data(data, request.user)
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                return self.error_response(e.error_dict)
            else:
                return self.error_response(str(e))
        
        # Create export job using the service
        from data_tools.services.export_service import ExportService
        
        try:
            export_service = ExportService()
            export_job = export_service.create_export_job(
                user=request.user,
                datasource_id=validated_data['datasource'].id,
                export_format=validated_data['format'],
                filters=validated_data.get('filters', {}),
                options=validated_data.get('options', {})
            )
            
            logger.info(f"Export job created: {export_job.id} by user {request.user.username}")
            
            return self.success_response(
                data=ExportJobSerializer.to_dict(export_job),
                message='Export job created successfully',
                status_code=201
            )
        except Exception as e:
            logger.error(f"Error creating export job via service: {str(e)}")
            return self.error_response(f'Export job creation failed: {str(e)}')
    
    def _delete_export_job(self, request, pk):
        """Delete an export job."""
        export_job = get_object_or_404(ExportJob, id=pk, user=request.user)
        
        # Only allow deletion of completed, failed, or cancelled jobs
        if export_job.status in ['pending', 'processing']:
            return self.error_response(
                'Cannot delete job that is currently processing. Cancel it first.',
                status_code=409
            )
        
        # Delete physical file if it exists
        if export_job.file_path and os.path.exists(export_job.file_path):
            try:
                os.remove(export_job.file_path)
            except OSError as e:
                logger.warning(f"Failed to delete export file {export_job.file_path}: {str(e)}")
        
        job_id = str(export_job.id)
        export_job.delete()
        
        logger.info(f"Export job deleted: {job_id} by user {request.user.username}")
        
        return self.success_response(
            message='Export job deleted successfully'
        )


@method_decorator(login_required, name='dispatch')
class ExportJobActionAPIView(BaseAPIView, View):
    """
    API view for custom export job actions (cancel, download, retry).
    """
    
    def post(self, request, pk, action):
        """
        Execute custom action on export job.
        
        Args:
            request: HTTP request object
            pk: UUID of export job
            action: Action name (cancel, retry)
            
        Returns:
            JsonResponse: Action result
        """
        export_job = get_object_or_404(ExportJob, id=pk, user=request.user)
        
        if action == 'cancel':
            return self._cancel_export_job(request, export_job)
        elif action == 'retry':
            return self._retry_export_job(request, export_job)
        else:
            return self.error_response(f'Unknown action: {action}', status_code=400)
    
    def get(self, request, pk, action):
        """
        Execute custom GET action on export job.
        
        Args:
            request: HTTP request object
            pk: UUID of export job
            action: Action name (download)
            
        Returns:
            HttpResponse or JsonResponse
        """
        export_job = get_object_or_404(ExportJob, id=pk, user=request.user)
        
        if action == 'download':
            return self._download_export_file(request, export_job)
        else:
            return self.error_response(f'Unknown action: {action}', status_code=400)
    
    def _cancel_export_job(self, request, export_job):
        """Cancel an export job."""
        from data_tools.services.export_service import ExportService
        
        export_service = ExportService()
        
        success = export_service.cancel_export(str(export_job.id), request.user)
        
        if success:
            # Refresh job from database
            export_job.refresh_from_db()
            
            return self.success_response(
                data=ExportJobSerializer.to_dict(export_job),
                message='Export job cancelled successfully'
            )
        else:
            return self.error_response(
                'Failed to cancel export job',
                status_code=409
            )
    
    def _retry_export_job(self, request, export_job):
        """Retry a failed export job."""
        if export_job.status not in ['failed', 'cancelled']:
            return self.error_response(
                'Only failed or cancelled jobs can be retried',
                status_code=409
            )
        
        # Reset job status and clear error
        export_job.status = 'pending'
        export_job.progress = 0
        export_job.error_message = ''
        export_job.started_at = None
        export_job.completed_at = None
        export_job.save(update_fields=[
            'status', 'progress', 'error_message', 
            'started_at', 'completed_at'
        ])
        
        # TODO: Trigger new Celery task
        # from data_tools.tasks import process_export_job
        # process_export_job.delay(export_job.id)
        
        logger.info(f"Export job retried: {export_job.id} by user {request.user.username}")
        
        return self.success_response(
            data=ExportJobSerializer.to_dict(export_job),
            message='Export job queued for retry'
        )
    
    def _download_export_file(self, request, export_job):
        """Download completed export file."""
        from data_tools.services.export_service import ExportService
        
        export_service = ExportService()
        
        file_path, filename = export_service.get_export_file(str(export_job.id), request.user)
        
        if not file_path:
            return self.error_response(
                'Export file is not available for download',
                status_code=404
            )
        
        try:
            # Prepare file response
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type based on format
            content_types = {
                'csv': 'text/csv',
                'json': 'application/json',
                'parquet': 'application/octet-stream',
                'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            
            content_type = content_types.get(export_job.format, 'application/octet-stream')
            
            # Create response
            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = len(content)
            
            logger.info(f"Export file downloaded: {export_job.id} by user {request.user.username}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error downloading export file {export_job.id}: {str(e)}")
            return self.error_response('Error downloading file')


@method_decorator(login_required, name='dispatch')
class ExportTemplateAPIView(BaseAPIView, View):
    """
    API view for ExportTemplate operations.
    Supports CRUD operations for export template management.
    """
    
    def get(self, request, pk=None):
        """
        Retrieve export template(s).
        
        Args:
            request: HTTP request object
            pk: Optional UUID of specific export template
            
        Returns:
            JsonResponse: Export template data or list of export templates
        """
        try:
            if pk:
                # Retrieve specific export template
                return self._get_export_template(request, pk)
            else:
                # List export templates with filtering
                return self._list_export_templates(request)
                
        except Exception as e:
            logger.error(f"Error in ExportTemplateAPIView.get: {str(e)}")
            return self.error_response('Error retrieving export templates')
    
    def post(self, request, pk=None):
        """
        Create a new export template.
        
        Args:
            request: HTTP request object
            pk: Not used for creation
            
        Returns:
            JsonResponse: Created export template data
        """
        if pk:
            return self.error_response('Invalid endpoint for creation', status_code=405)
        
        try:
            return self._create_export_template(request)
        except Exception as e:
            logger.error(f"Error in ExportTemplateAPIView.post: {str(e)}")
            return self.error_response('Error creating export template')
    
    def put(self, request, pk=None):
        """
        Update an export template.
        
        Args:
            request: HTTP request object
            pk: UUID of export template to update
            
        Returns:
            JsonResponse: Updated export template data
        """
        if not pk:
            return self.error_response('Template ID is required', status_code=400)
        
        try:
            return self._update_export_template(request, pk)
        except Exception as e:
            logger.error(f"Error in ExportTemplateAPIView.put: {str(e)}")
            return self.error_response('Error updating export template')
    
    def delete(self, request, pk=None):
        """
        Delete an export template.
        
        Args:
            request: HTTP request object
            pk: UUID of export template to delete
            
        Returns:
            JsonResponse: Success or error response
        """
        if not pk:
            return self.error_response('Template ID is required', status_code=400)
        
        try:
            return self._delete_export_template(request, pk)
        except Exception as e:
            logger.error(f"Error in ExportTemplateAPIView.delete: {str(e)}")
            return self.error_response('Error deleting export template')
    
    def _get_export_template(self, request, pk):
        """Get specific export template by ID."""
        export_template = get_object_or_404(ExportTemplate, id=pk)
        
        # Check access permissions
        if not self._can_access_template(export_template, request.user):
            raise Http404("Export template not found")
        
        return self.success_response(
            data=ExportTemplateSerializer.to_dict(export_template),
            message='Export template retrieved successfully'
        )
    
    def _list_export_templates(self, request):
        """List export templates with filtering."""
        # Get templates available to user
        queryset = ExportTemplate.get_available_for_user(request.user)
        
        # Apply filters
        template_type = request.GET.get('type')
        if template_type and template_type in ['user', 'system', 'shared']:
            queryset = queryset.filter(template_type=template_type)
        
        format_filter = request.GET.get('format')
        if format_filter:
            queryset = queryset.filter(configuration__format=format_filter)
        
        # Search by name or description
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Order by usage and update time
        queryset = queryset.order_by('-usage_count', '-updated_at')
        
        # Serialize templates
        templates = [
            ExportTemplateSerializer.to_dict(template) for template in queryset
        ]
        
        return self.success_response(
            data={
                'templates': templates,
                'total_count': len(templates)
            },
            message='Export templates retrieved successfully'
        )
    
    def _create_export_template(self, request):
        """Create a new export template."""
        import json
        
        # Parse request data
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                # Handle JSON string fields from form data
                if 'configuration' in data and isinstance(data['configuration'], str):
                    data['configuration'] = json.loads(data['configuration'])
        except (json.JSONDecodeError, ValueError) as e:
            return self.error_response('Invalid JSON data')
        
        # Validate data
        try:
            validated_data = ExportTemplateSerializer.validate_create_data(data, request.user)
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                return self.error_response(e.error_dict)
            else:
                return self.error_response(str(e))
        
        # Create export template
        export_template = ExportTemplate.objects.create(**validated_data)
        
        logger.info(f"Export template created: {export_template.id} by user {request.user.username}")
        
        return self.success_response(
            data=ExportTemplateSerializer.to_dict(export_template),
            message='Export template created successfully',
            status_code=201
        )
    
    def _update_export_template(self, request, pk):
        """Update an export template."""
        import json
        
        export_template = get_object_or_404(ExportTemplate, id=pk)
        
        # Check permission
        if not self._can_modify_template(export_template, request.user):
            return self.error_response(
                'You do not have permission to modify this template',
                status_code=403
            )
        
        # Parse request data
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                # Handle JSON string fields from form data
                if 'configuration' in data and isinstance(data['configuration'], str):
                    data['configuration'] = json.loads(data['configuration'])
        except (json.JSONDecodeError, ValueError) as e:
            return self.error_response('Invalid JSON data')
        
        # Validate data
        try:
            validated_data = ExportTemplateSerializer.validate_update_data(
                data, export_template, request.user
            )
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                return self.error_response(e.error_dict)
            else:
                return self.error_response(str(e))
        
        # Update template
        for field, value in validated_data.items():
            setattr(export_template, field, value)
        
        export_template.save()
        
        logger.info(f"Export template updated: {export_template.id} by user {request.user.username}")
        
        return self.success_response(
            data=ExportTemplateSerializer.to_dict(export_template),
            message='Export template updated successfully'
        )
    
    def _delete_export_template(self, request, pk):
        """Delete an export template."""
        export_template = get_object_or_404(ExportTemplate, id=pk)
        
        # Check permission
        if not self._can_modify_template(export_template, request.user):
            return self.error_response(
                'You do not have permission to delete this template',
                status_code=403
            )
        
        template_id = str(export_template.id)
        template_name = export_template.name
        export_template.delete()
        
        logger.info(f"Export template deleted: {template_id} ({template_name}) by user {request.user.username}")
        
        return self.success_response(
            message='Export template deleted successfully'
        )
    
    def _can_access_template(self, template, user):
        """Check if user can access template."""
        return (
            template.user == user or
            template.template_type in ['system', 'shared'] or
            user.is_superuser
        )
    
    def _can_modify_template(self, template, user):
        """Check if user can modify template."""
        return template.user == user or user.is_superuser