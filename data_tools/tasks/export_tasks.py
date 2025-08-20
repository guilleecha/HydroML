"""
Export Tasks - Celery tasks for asynchronous export processing.

This module contains Celery tasks for handling data export operations,
including progress tracking, error handling, and cleanup tasks.
"""

import logging
from datetime import timedelta

from celery import shared_task, Task
from celery.exceptions import Retry
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task class with callback functionality for progress updates."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        logger.info(f"Export task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        logger.error(f"Export task {task_id} failed: {exc}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        logger.warning(f"Export task {task_id} retrying: {exc}")


@shared_task(bind=True, base=CallbackTask, max_retries=3, default_retry_delay=60)
def process_data_export(self, job_id):
    """
    Async task for processing data export.
    
    This task handles the complete export process including:
    - Loading data from datasource
    - Applying filters and transformations
    - Converting to requested format
    - Saving to file
    - Progress updates and error handling
    
    Args:
        job_id: String UUID of the ExportJob to process
        
    Returns:
        Dict with processing results
    """
    from data_tools.services.export_service import ExportService
    from data_tools.models.export_job import ExportJob
    
    export_service = ExportService()
    
    try:
        # Update task state to PROGRESS
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting export...'}
        )
        
        logger.info(f"Starting export processing for job {job_id}")
        
        # Verify job exists and is in pending state
        try:
            export_job = ExportJob.objects.get(id=job_id)
        except ExportJob.DoesNotExist:
            logger.error(f"Export job {job_id} not found")
            return {'status': 'ERROR', 'message': 'Export job not found'}
        
        if export_job.status != 'pending':
            logger.warning(f"Export job {job_id} is not in pending state: {export_job.status}")
            return {'status': 'ERROR', 'message': f'Job is not pending (status: {export_job.status})'}
        
        # Update progress - job validation complete
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Validating export parameters...'}
        )
        
        # Process the export using the service
        success = export_service.process_export(job_id)
        
        if success:
            logger.info(f"Export job {job_id} processed successfully")
            return {
                'status': 'SUCCESS',
                'message': 'Export completed successfully',
                'job_id': job_id
            }
        else:
            logger.error(f"Export job {job_id} processing failed")
            return {
                'status': 'ERROR',
                'message': 'Export processing failed',
                'job_id': job_id
            }
    
    except Exception as exc:
        logger.error(f"Error in export task for job {job_id}: {str(exc)}")
        
        # Update job status on error
        try:
            export_job = ExportJob.objects.get(id=job_id)
            export_job.mark_as_failed(f"Task error: {str(exc)}")
        except ExportJob.DoesNotExist:
            pass
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying export task for job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=60)
        else:
            logger.error(f"Max retries exceeded for export job {job_id}")
            return {
                'status': 'ERROR',
                'message': f'Max retries exceeded: {str(exc)}',
                'job_id': job_id
            }


@shared_task(bind=True)
def cancel_export_job(self, job_id):
    """
    Cancel a running export job.
    
    This task attempts to cancel a running export job by updating its status.
    Note: This doesn't actually stop a running process, it just marks it as cancelled.
    
    Args:
        job_id: String UUID of the ExportJob to cancel
        
    Returns:
        Dict with cancellation results
    """
    from data_tools.models.export_job import ExportJob
    
    try:
        export_job = ExportJob.objects.get(id=job_id)
        
        if export_job.status in ['pending', 'processing']:
            export_job.status = 'cancelled'
            export_job.completed_at = timezone.now()
            export_job.save(update_fields=['status', 'completed_at'])
            
            logger.info(f"Export job {job_id} cancelled successfully")
            return {
                'status': 'SUCCESS',
                'message': 'Export job cancelled',
                'job_id': job_id
            }
        else:
            logger.warning(f"Cannot cancel export job {job_id} with status {export_job.status}")
            return {
                'status': 'ERROR',
                'message': f'Cannot cancel job with status: {export_job.status}',
                'job_id': job_id
            }
            
    except ExportJob.DoesNotExist:
        logger.error(f"Export job {job_id} not found for cancellation")
        return {
            'status': 'ERROR',
            'message': 'Export job not found',
            'job_id': job_id
        }
    except Exception as exc:
        logger.error(f"Error cancelling export job {job_id}: {str(exc)}")
        return {
            'status': 'ERROR',
            'message': str(exc),
            'job_id': job_id
        }


@shared_task
def cleanup_expired_exports():
    """
    Periodic task to clean up expired export files.
    
    This task should be run regularly (e.g., daily) to remove old export files
    and free up storage space.
    
    Returns:
        Dict with cleanup statistics
    """
    from data_tools.services.export_service import ExportService
    from data_tools.services.file_manager import ExportFileManager
    
    try:
        logger.info("Starting cleanup of expired export files")
        
        export_service = ExportService()
        file_manager = ExportFileManager()
        
        # Clean up expired export jobs and their files
        cleaned_jobs = export_service.cleanup_expired_exports()
        
        # Get retention days from settings
        retention_days = getattr(settings, 'EXPORT_FILE_RETENTION_DAYS', 7)
        
        # Clean up any orphaned files
        file_stats = file_manager.cleanup_expired_files(retention_days)
        
        total_files = cleaned_jobs + file_stats.get('files_deleted', 0)
        total_bytes = file_stats.get('bytes_freed', 0)
        
        logger.info(
            f"Export cleanup completed: {total_files} files removed, "
            f"{total_bytes / 1024 / 1024:.1f} MB freed"
        )
        
        return {
            'status': 'SUCCESS',
            'cleaned_jobs': cleaned_jobs,
            'cleaned_files': file_stats.get('files_deleted', 0),
            'bytes_freed': total_bytes,
            'errors': file_stats.get('errors', 0)
        }
        
    except Exception as exc:
        logger.error(f"Error during export cleanup: {str(exc)}")
        return {
            'status': 'ERROR',
            'message': str(exc),
            'cleaned_jobs': 0,
            'cleaned_files': 0,
            'bytes_freed': 0
        }


@shared_task
def health_check_export_system():
    """
    Health check task for the export system.
    
    This task verifies that the export system is functioning properly
    by checking storage, permissions, and system resources.
    
    Returns:
        Dict with health check results
    """
    from data_tools.services.file_manager import ExportFileManager
    from data_tools.models.export_job import ExportJob
    from django.db.models import Count
    
    try:
        logger.info("Running export system health check")
        
        file_manager = ExportFileManager()
        health_results = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Check storage health
        storage_health = file_manager.check_storage_health()
        health_results['checks']['storage'] = storage_health
        
        if storage_health['status'] != 'healthy':
            health_results['status'] = storage_health['status']
        
        # Check job queue health
        active_jobs = ExportJob.get_active_jobs().count()
        stuck_jobs = ExportJob.objects.filter(
            status='processing',
            started_at__lt=timezone.now() - timedelta(hours=2)
        ).count()
        
        health_results['checks']['job_queue'] = {
            'active_jobs': active_jobs,
            'stuck_jobs': stuck_jobs,
            'status': 'warning' if stuck_jobs > 0 else 'healthy'
        }
        
        if stuck_jobs > 0:
            health_results['status'] = 'warning'
        
        # Check recent job success rate
        from django.db.models import Q
        recent_jobs = ExportJob.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        ).aggregate(
            total=Count('id'),
            successful=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed'))
        )
        
        total_recent = recent_jobs['total']
        success_rate = 0
        if total_recent > 0:
            success_rate = (recent_jobs['successful'] / total_recent) * 100
        
        health_results['checks']['success_rate'] = {
            'total_jobs_24h': total_recent,
            'success_rate': success_rate,
            'status': 'warning' if success_rate < 90 else 'healthy'
        }
        
        if success_rate < 90 and total_recent > 5:  # Only warn if we have enough data
            health_results['status'] = 'warning'
        
        logger.info(f"Export system health check completed: {health_results['status']}")
        
        return health_results
        
    except Exception as exc:
        logger.error(f"Error during export system health check: {str(exc)}")
        return {
            'status': 'error',
            'timestamp': timezone.now().isoformat(),
            'error': str(exc),
            'checks': {}
        }


@shared_task
def generate_export_metrics():
    """
    Generate metrics and statistics about export system usage.
    
    This task collects usage metrics for monitoring and optimization.
    
    Returns:
        Dict with export system metrics
    """
    from data_tools.models.export_job import ExportJob
    from data_tools.services.file_manager import ExportFileManager
    from django.db.models import Count, Sum, Avg, Q
    from django.db.models.functions import TruncDate
    
    try:
        logger.info("Generating export system metrics")
        
        file_manager = ExportFileManager()
        now = timezone.now()
        
        metrics = {
            'generated_at': now.isoformat(),
            'period': '30_days',
            'jobs': {},
            'storage': {},
            'performance': {}
        }
        
        # Job metrics for last 30 days
        thirty_days_ago = now - timedelta(days=30)
        recent_jobs = ExportJob.objects.filter(created_at__gte=thirty_days_ago)
        
        # Job statistics
        job_stats = recent_jobs.aggregate(
            total_jobs=Count('id'),
            completed_jobs=Count('id', filter=Q(status='completed')),
            failed_jobs=Count('id', filter=Q(status='failed')),
            total_rows_exported=Sum('row_count'),
            total_file_size=Sum('file_size'),
            avg_processing_time=Avg('duration_seconds')
        )
        
        metrics['jobs'] = {
            'total': job_stats['total_jobs'] or 0,
            'completed': job_stats['completed_jobs'] or 0,
            'failed': job_stats['failed_jobs'] or 0,
            'success_rate': ((job_stats['completed_jobs'] or 0) / max(job_stats['total_jobs'] or 1, 1)) * 100,
            'total_rows_exported': job_stats['total_rows_exported'] or 0,
            'total_file_size_mb': (job_stats['total_file_size'] or 0) / (1024 * 1024),
            'avg_processing_time_seconds': job_stats['avg_processing_time'] or 0
        }
        
        # Jobs by format
        format_stats = recent_jobs.values('format').annotate(
            count=Count('id')
        ).order_by('-count')
        
        metrics['jobs']['by_format'] = {
            item['format']: item['count'] for item in format_stats
        }
        
        # Jobs by day (last 7 days for trends)
        seven_days_ago = now - timedelta(days=7)
        daily_stats = recent_jobs.filter(
            created_at__gte=seven_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        metrics['jobs']['daily_trend'] = {
            item['date'].isoformat(): item['count'] for item in daily_stats
        }
        
        # Storage metrics
        storage_stats = file_manager.get_storage_stats()
        metrics['storage'] = {
            'total_files': storage_stats['total_files'],
            'total_size_mb': storage_stats['total_size'] / (1024 * 1024),
            'by_extension': {
                ext: {
                    'count': stats['count'],
                    'size_mb': stats['size'] / (1024 * 1024)
                }
                for ext, stats in storage_stats['by_extension'].items()
            }
        }
        
        # Performance metrics
        metrics['performance'] = {
            'avg_file_size_mb': metrics['jobs']['total_file_size_mb'] / max(metrics['jobs']['completed'], 1),
            'avg_rows_per_job': (metrics['jobs']['total_rows_exported'] / max(metrics['jobs']['completed'], 1)),
            'processing_efficiency': {
                'fast_jobs': recent_jobs.filter(duration_seconds__lt=30).count(),
                'medium_jobs': recent_jobs.filter(duration_seconds__gte=30, duration_seconds__lt=300).count(),
                'slow_jobs': recent_jobs.filter(duration_seconds__gte=300).count()
            }
        }
        
        logger.info("Export system metrics generated successfully")
        return metrics
        
    except Exception as exc:
        logger.error(f"Error generating export metrics: {str(exc)}")
        return {
            'generated_at': timezone.now().isoformat(),
            'error': str(exc),
            'jobs': {},
            'storage': {},
            'performance': {}
        }