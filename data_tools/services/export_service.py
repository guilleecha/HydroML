"""
Export Service - Core business logic for data export functionality.

This service handles the orchestration of data export processes,
including job management, data processing, and format conversion.
"""

import os
import logging
import uuid
from datetime import timedelta
from typing import Dict, Any, Optional, Tuple

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction

from data_tools.models.export_job import ExportJob
from projects.models.datasource import DataSource
from .export_formats import ExportFormatHandler
from .file_manager import ExportFileManager
from .engine import process_datasource_to_df

logger = logging.getLogger(__name__)


class ExportService:
    """
    Core service for data export functionality.
    
    This service provides the business logic layer for data export operations,
    handling job creation, processing coordination, and file management.
    """
    
    def __init__(self):
        self.format_handler = ExportFormatHandler()
        self.file_manager = ExportFileManager()
    
    def create_export_job(
        self,
        user,
        datasource_id: int,
        export_format: str,
        filters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ExportJob:
        """
        Create a new export job and queue it for processing.
        
        Args:
            user: Django User instance who requested the export
            datasource_id: ID of the DataSource to export
            export_format: Export format ('csv', 'json', 'parquet', 'excel')
            filters: Optional filters to apply to data (SQL conditions, column selections)
            options: Optional export-specific options (headers, encoding, etc.)
            
        Returns:
            ExportJob: Created export job instance
            
        Raises:
            ValidationError: If input parameters are invalid
            DataSource.DoesNotExist: If datasource doesn't exist or user lacks access
        """
        try:
            # Validate datasource access
            datasource = self._validate_datasource_access(user, datasource_id)
            
            # Validate export format
            if export_format not in dict(ExportJob.FORMAT_CHOICES):
                raise ValidationError(f"Invalid export format: {export_format}")
            
            # Validate and clean filters
            cleaned_filters = self._validate_filters(filters or {})
            
            # Validate options
            cleaned_options = self._validate_options(options or {}, export_format)
            
            # Create export job
            with transaction.atomic():
                export_job = ExportJob.objects.create(
                    user=user,
                    datasource=datasource,
                    format=export_format,
                    filters=cleaned_filters,
                    # Store options in filters for simplicity (could be separate field)
                    # We'll merge options into filters with 'export_options' key
                )
                
                # Set expiration (default 7 days)
                export_job.set_expiration(days=getattr(settings, 'EXPORT_FILE_RETENTION_DAYS', 7))
            
            logger.info(
                f"Export job created: {export_job.id} for datasource {datasource.name} "
                f"by user {user.username}"
            )
            
            # Queue the job for async processing
            self._queue_export_job(export_job.id)
            
            return export_job
            
        except Exception as e:
            logger.error(f"Error creating export job: {str(e)}")
            raise
    
    def process_export(self, job_id: str) -> bool:
        """
        Process an export job - load data, apply filters, convert format, and save file.
        
        This method is typically called by a Celery task for async processing.
        
        Args:
            job_id: UUID string of the export job to process
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # Get and validate job
            export_job = ExportJob.objects.select_related('datasource', 'user').get(id=job_id)
            
            if export_job.status != 'pending':
                logger.warning(f"Export job {job_id} is not pending (status: {export_job.status})")
                return False
            
            # Mark job as started
            export_job.mark_as_started()
            
            logger.info(f"Starting export processing for job {job_id}")
            
            # Load data from datasource
            dataframe = self._load_filtered_data(export_job)
            
            if dataframe is None or dataframe.empty:
                export_job.mark_as_failed("No data available for export")
                return False
            
            # Update progress
            export_job.update_progress(25)
            
            # Generate output file path
            output_path = self.file_manager.generate_file_path(export_job)
            
            # Convert to requested format
            self._convert_and_save_data(export_job, dataframe, output_path)
            
            # Update progress
            export_job.update_progress(75)
            
            # Get file info
            file_size = os.path.getsize(output_path)
            row_count = len(dataframe)
            
            # Mark job as completed
            export_job.mark_as_completed(
                file_path=output_path,
                file_size=file_size,
                row_count=row_count
            )
            
            logger.info(
                f"Export job {job_id} completed successfully. "
                f"Generated {row_count} rows in {file_size} bytes"
            )
            
            return True
            
        except ExportJob.DoesNotExist:
            logger.error(f"Export job {job_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error processing export job {job_id}: {str(e)}")
            
            # Mark job as failed
            try:
                export_job = ExportJob.objects.get(id=job_id)
                export_job.mark_as_failed(str(e))
            except ExportJob.DoesNotExist:
                pass
            
            return False
    
    def cancel_export(self, job_id: str, user) -> bool:
        """
        Cancel an export job.
        
        Args:
            job_id: UUID string of the export job to cancel
            user: User requesting cancellation (for permission check)
            
        Returns:
            bool: True if cancellation succeeded, False otherwise
        """
        try:
            export_job = ExportJob.objects.get(id=job_id, user=user)
            
            if export_job.status not in ['pending', 'processing']:
                logger.warning(
                    f"Cannot cancel export job {job_id} with status {export_job.status}"
                )
                return False
            
            # TODO: Cancel Celery task if running
            # This would require tracking Celery task IDs
            
            # Mark as cancelled
            export_job.status = 'cancelled'
            export_job.completed_at = timezone.now()
            export_job.save(update_fields=['status', 'completed_at'])
            
            logger.info(f"Export job {job_id} cancelled by user {user.username}")
            return True
            
        except ExportJob.DoesNotExist:
            logger.error(f"Export job {job_id} not found or access denied")
            return False
        except Exception as e:
            logger.error(f"Error cancelling export job {job_id}: {str(e)}")
            return False
    
    def get_export_file(self, job_id: str, user) -> Tuple[Optional[str], Optional[str]]:
        """
        Get export file path for download.
        
        Args:
            job_id: UUID string of the export job
            user: User requesting the file (for permission check)
            
        Returns:
            Tuple of (file_path, filename) or (None, None) if not available
        """
        try:
            export_job = ExportJob.objects.get(id=job_id, user=user)
            
            if export_job.status != 'completed':
                logger.warning(f"Export job {job_id} is not completed")
                return None, None
            
            if export_job.is_expired:
                logger.warning(f"Export job {job_id} has expired")
                return None, None
            
            if not export_job.file_path or not os.path.exists(export_job.file_path):
                logger.warning(f"Export file for job {job_id} not found")
                return None, None
            
            # Generate download filename
            filename = f"{export_job.datasource.name}_export_{export_job.id}.{export_job.format}"
            
            return export_job.file_path, filename
            
        except ExportJob.DoesNotExist:
            logger.error(f"Export job {job_id} not found or access denied")
            return None, None
        except Exception as e:
            logger.error(f"Error getting export file {job_id}: {str(e)}")
            return None, None
    
    def cleanup_expired_exports(self) -> int:
        """
        Clean up expired export files and update job statuses.
        
        This method should be called by a periodic Celery task.
        
        Returns:
            int: Number of export jobs cleaned up
        """
        try:
            logger.info("Starting cleanup of expired export files")
            
            # Use the model's cleanup method
            cleaned_count = ExportJob.cleanup_expired()
            
            logger.info(f"Cleaned up {cleaned_count} expired export files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during export cleanup: {str(e)}")
            return 0
    
    def get_user_export_stats(self, user) -> Dict[str, Any]:
        """
        Get export statistics for a user.
        
        Args:
            user: Django User instance
            
        Returns:
            Dict with user export statistics
        """
        try:
            from django.db.models import Count, Sum, Avg
            
            stats = ExportJob.objects.filter(user=user).aggregate(
                total_jobs=Count('id'),
                completed_jobs=Count('id', filter=models.Q(status='completed')),
                failed_jobs=Count('id', filter=models.Q(status='failed')),
                total_exported_rows=Sum('row_count'),
                total_file_size=Sum('file_size'),
                avg_processing_time=Avg('duration_seconds')
            )
            
            # Calculate success rate
            total = stats['total_jobs'] or 0
            completed = stats['completed_jobs'] or 0
            stats['success_rate'] = (completed / total * 100) if total > 0 else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting export stats for user {user.username}: {str(e)}")
            return {}
    
    # Private methods
    
    def _validate_datasource_access(self, user, datasource_id: int) -> DataSource:
        """Validate that user has access to the datasource."""
        try:
            # Check if datasource exists and user has access via projects
            datasource = DataSource.objects.select_related('project').get(id=datasource_id)
            
            # Check if user has access to the project containing this datasource
            if not datasource.project.members.filter(id=user.id).exists():
                if not user.is_superuser:
                    raise ValidationError("Access denied to datasource")
            
            return datasource
            
        except DataSource.DoesNotExist:
            raise ValidationError("Datasource not found")
    
    def _validate_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean filter parameters."""
        allowed_filter_keys = [
            'columns', 'where_conditions', 'limit', 'offset', 
            'order_by', 'group_by'
        ]
        
        cleaned_filters = {}
        
        for key, value in filters.items():
            if key in allowed_filter_keys:
                cleaned_filters[key] = value
            else:
                logger.warning(f"Unknown filter key ignored: {key}")
        
        return cleaned_filters
    
    def _validate_options(self, options: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """Validate export options based on format."""
        format_specific_options = {
            'csv': ['delimiter', 'encoding', 'include_header', 'quote_char'],
            'json': ['orient', 'date_format', 'indent'],
            'parquet': ['compression', 'engine'],
            'excel': ['sheet_name', 'index', 'freeze_panes']
        }
        
        allowed_options = format_specific_options.get(format_type, [])
        
        cleaned_options = {}
        for key, value in options.items():
            if key in allowed_options:
                cleaned_options[key] = value
            else:
                logger.warning(f"Unknown option for {format_type} ignored: {key}")
        
        return cleaned_options
    
    def _queue_export_job(self, job_id: str):
        """Queue export job for async processing."""
        try:
            # Import here to avoid circular imports
            from data_tools.tasks.export_tasks import process_data_export
            
            # Queue the Celery task
            process_data_export.delay(str(job_id))
            
        except ImportError:
            logger.error("Export tasks not available - running synchronously")
            # Fallback to synchronous processing in development
            self.process_export(str(job_id))
    
    def _load_filtered_data(self, export_job: ExportJob):
        """Load data from datasource with applied filters."""
        try:
            # Use the existing data processing engine
            dataframe = process_datasource_to_df(export_job.datasource)
            
            if dataframe is None or dataframe.empty:
                return None
            
            # Apply filters
            if export_job.filters:
                dataframe = self._apply_filters(dataframe, export_job.filters)
            
            return dataframe
            
        except Exception as e:
            logger.error(f"Error loading data for export job {export_job.id}: {str(e)}")
            raise
    
    def _apply_filters(self, dataframe, filters: Dict[str, Any]):
        """Apply filters to dataframe."""
        import pandas as pd
        
        try:
            # Column selection
            if 'columns' in filters and filters['columns']:
                selected_columns = [col for col in filters['columns'] if col in dataframe.columns]
                if selected_columns:
                    dataframe = dataframe[selected_columns]
            
            # Row limit
            if 'limit' in filters and filters['limit']:
                limit = int(filters['limit'])
                dataframe = dataframe.head(limit)
            
            # Offset (skip rows)
            if 'offset' in filters and filters['offset']:
                offset = int(filters['offset'])
                dataframe = dataframe.iloc[offset:]
            
            # Basic where conditions (simple column=value filters)
            if 'where_conditions' in filters and filters['where_conditions']:
                conditions = filters['where_conditions']
                if isinstance(conditions, dict):
                    for column, value in conditions.items():
                        if column in dataframe.columns:
                            dataframe = dataframe[dataframe[column] == value]
            
            # Order by
            if 'order_by' in filters and filters['order_by']:
                order_columns = filters['order_by']
                if isinstance(order_columns, str):
                    order_columns = [order_columns]
                
                valid_columns = [col for col in order_columns if col in dataframe.columns]
                if valid_columns:
                    dataframe = dataframe.sort_values(valid_columns)
            
            return dataframe
            
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            return dataframe  # Return unfiltered data rather than failing
    
    def _convert_and_save_data(self, export_job: ExportJob, dataframe, output_path: str):
        """Convert dataframe to requested format and save to file."""
        try:
            # Extract options from filters (we stored them there)
            options = export_job.filters.get('export_options', {})
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert based on format
            if export_job.format == 'csv':
                self.format_handler.to_csv(dataframe, output_path, options)
            elif export_job.format == 'json':
                self.format_handler.to_json(dataframe, output_path, options)
            elif export_job.format == 'parquet':
                self.format_handler.to_parquet(dataframe, output_path, options)
            elif export_job.format == 'excel':
                self.format_handler.to_excel(dataframe, output_path, options)
            else:
                raise ValueError(f"Unsupported export format: {export_job.format}")
            
            logger.info(f"Data converted to {export_job.format} format: {output_path}")
            
        except Exception as e:
            logger.error(f"Error converting data to {export_job.format}: {str(e)}")
            raise