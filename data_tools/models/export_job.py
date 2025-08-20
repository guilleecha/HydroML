# data_tools/models/export_job.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from projects.models.datasource import DataSource


class ExportJob(models.Model):
    """
    Model for managing data export jobs with various formats and status tracking.
    
    This model tracks:
    - Export job status and progress
    - User who initiated the export
    - DataSource being exported
    - Export format and configuration
    - File generation and storage details
    - Error handling and timestamps
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('parquet', 'Parquet'),
        ('excel', 'Excel'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the export job"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_jobs',
        help_text="User who initiated the export job"
    )
    
    datasource = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name='export_jobs',
        help_text="DataSource to be exported"
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the export job"
    )
    
    format = models.CharField(
        max_length=10, 
        choices=FORMAT_CHOICES,
        help_text="Export format for the data"
    )
    
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Applied filters for the export (SQL conditions, column selections, etc.)"
    )
    
    progress = models.IntegerField(
        default=0,
        help_text="Export progress as percentage (0-100)"
    )
    
    file_path = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Path to the generated export file"
    )
    
    file_size = models.BigIntegerField(
        null=True, 
        blank=True,
        help_text="Size of the generated file in bytes"
    )
    
    row_count = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Number of rows in the exported data"
    )
    
    error_message = models.TextField(
        blank=True,
        help_text="Error message if the export failed"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the export job was created"
    )
    
    started_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the export job started processing"
    )
    
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the export job completed (successfully or with failure)"
    )
    
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the export file will be automatically deleted"
    )
    
    class Meta:
        db_table = 'data_tools_export_job'
        verbose_name = "Export Job"
        verbose_name_plural = "Export Jobs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['datasource', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Export {self.id} - {self.format} - {self.status}"
    
    @property
    def is_completed(self):
        """Returns True if the job has finished processing (success or failure)."""
        return self.status in ['completed', 'failed', 'cancelled']
    
    @property
    def is_expired(self):
        """Returns True if the export file has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def duration_seconds(self):
        """
        Calculate the duration of the export job in seconds.
        Returns None if the job hasn't started or completed.
        """
        if not self.started_at:
            return None
        
        end_time = self.completed_at or timezone.now()
        return (end_time - self.started_at).total_seconds()
    
    def set_expiration(self, days=7):
        """
        Set the expiration date for the export file.
        Default is 7 days from creation.
        """
        self.expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=['expires_at'])
    
    def mark_as_started(self):
        """Mark the job as started and update timestamps."""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_as_completed(self, file_path=None, file_size=None, row_count=None):
        """
        Mark the job as completed successfully.
        
        Args:
            file_path: Path to the generated export file
            file_size: Size of the file in bytes
            row_count: Number of rows exported
        """
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress = 100
        
        if file_path:
            self.file_path = file_path
        if file_size is not None:
            self.file_size = file_size
        if row_count is not None:
            self.row_count = row_count
        
        # Set default expiration if not already set
        if not self.expires_at:
            self.set_expiration()
        
        self.save(update_fields=[
            'status', 'completed_at', 'progress', 'file_path', 
            'file_size', 'row_count', 'expires_at'
        ])
    
    def mark_as_failed(self, error_message):
        """
        Mark the job as failed with an error message.
        
        Args:
            error_message: Description of the error that occurred
        """
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=['status', 'completed_at', 'error_message'])
    
    def update_progress(self, progress):
        """
        Update the progress percentage of the export job.
        
        Args:
            progress: Integer between 0 and 100
        """
        if 0 <= progress <= 100:
            self.progress = progress
            self.save(update_fields=['progress'])
    
    @classmethod
    def get_active_jobs(cls, user=None):
        """
        Get all active (non-completed) export jobs.
        
        Args:
            user: Optional user to filter jobs by
            
        Returns:
            QuerySet of active ExportJob objects
        """
        queryset = cls.objects.filter(
            status__in=['pending', 'processing']
        )
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.select_related('user', 'datasource')
    
    @classmethod
    def cleanup_expired(cls):
        """
        Clean up expired export files and mark jobs as expired.
        This method should be called by a periodic task.
        
        Returns:
            int: Number of jobs cleaned up
        """
        import os
        from django.conf import settings
        
        expired_jobs = cls.objects.filter(
            expires_at__lt=timezone.now(),
            status='completed'
        )
        
        cleaned_count = 0
        for job in expired_jobs:
            # Remove the physical file if it exists
            if job.file_path and os.path.exists(job.file_path):
                try:
                    os.remove(job.file_path)
                except OSError:
                    pass  # File might already be deleted
            
            # Update the job status
            job.status = 'expired'
            job.file_path = ''
            job.save(update_fields=['status', 'file_path'])
            cleaned_count += 1
        
        return cleaned_count