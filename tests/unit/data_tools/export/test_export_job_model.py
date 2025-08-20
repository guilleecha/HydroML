"""
Comprehensive unit tests for ExportJob model.

Tests all model functionality including:
- Model creation and validation
- Status transitions and properties
- Timestamp tracking
- Progress updates
- File management
- Cleanup operations
"""

import os
import tempfile
import uuid
from datetime import timedelta
from unittest.mock import patch, Mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError

from data_tools.models.export_job import ExportJob
from projects.models.project import Project
from projects.models.datasource import DataSource

User = get_user_model()


class ExportJobModelTest(TestCase):
    """Test ExportJob model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project',
            user=self.user
        )
        self.project.members.add(self.user)
        
        self.datasource = DataSource.objects.create(
            name='Test DataSource',
            file_type='csv',
            storage_type='local',
            file_path='test_data.csv'
        )
        self.datasource.projects.add(self.project)

    def test_export_job_creation_with_uuid(self):
        """Test ExportJob creation with UUID primary key."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # Check UUID is set and valid
        self.assertIsInstance(job.id, uuid.UUID)
        self.assertEqual(job.user, self.user)
        self.assertEqual(job.datasource, self.datasource)
        self.assertEqual(job.format, 'csv')
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress, 0)

    def test_export_job_creation_with_all_fields(self):
        """Test ExportJob creation with all optional fields."""
        filters = {'columns': ['col1', 'col2'], 'limit': 1000}
        
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            filters=filters,
            progress=50
        )
        
        self.assertEqual(job.format, 'json')
        self.assertEqual(job.filters, filters)
        self.assertEqual(job.progress, 50)

    def test_export_job_string_representation(self):
        """Test ExportJob string representation."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='parquet',
            status='processing'
        )
        
        expected_str = f"Export {job.id} - parquet - processing"
        self.assertEqual(str(job), expected_str)

    def test_export_job_default_values(self):
        """Test ExportJob default values."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='excel'
        )
        
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress, 0)
        self.assertEqual(job.filters, {})
        self.assertIsNone(job.file_size)
        self.assertIsNone(job.row_count)
        self.assertEqual(job.error_message, '')
        self.assertIsNotNone(job.created_at)
        self.assertIsNone(job.started_at)
        self.assertIsNone(job.completed_at)
        self.assertIsNone(job.expires_at)

    def test_export_job_invalid_format(self):
        """Test ExportJob creation with invalid format."""
        with self.assertRaises(ValidationError):
            job = ExportJob(
                user=self.user,
                datasource=self.datasource,
                format='invalid_format'
            )
            job.full_clean()

    def test_export_job_invalid_status(self):
        """Test ExportJob creation with invalid status."""
        with self.assertRaises(ValidationError):
            job = ExportJob(
                user=self.user,
                datasource=self.datasource,
                format='csv',
                status='invalid_status'
            )
            job.full_clean()

    def test_is_completed_property(self):
        """Test is_completed property for different statuses."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # Test non-completed statuses
        job.status = 'pending'
        self.assertFalse(job.is_completed)
        
        job.status = 'processing'
        self.assertFalse(job.is_completed)
        
        # Test completed statuses
        job.status = 'completed'
        self.assertTrue(job.is_completed)
        
        job.status = 'failed'
        self.assertTrue(job.is_completed)
        
        job.status = 'cancelled'
        self.assertTrue(job.is_completed)

    def test_is_expired_property(self):
        """Test is_expired property."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # No expiration set
        self.assertFalse(job.is_expired)
        
        # Future expiration
        job.expires_at = timezone.now() + timedelta(days=1)
        self.assertFalse(job.is_expired)
        
        # Past expiration
        job.expires_at = timezone.now() - timedelta(days=1)
        self.assertTrue(job.is_expired)

    def test_duration_seconds_property(self):
        """Test duration_seconds property."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # No start time
        self.assertIsNone(job.duration_seconds)
        
        # With start time but no completion
        now = timezone.now()
        job.started_at = now - timedelta(seconds=30)
        duration = job.duration_seconds
        self.assertIsNotNone(duration)
        self.assertGreater(duration, 25)  # At least 25 seconds
        
        # With both start and completion times
        job.completed_at = now
        job.started_at = now - timedelta(seconds=60)
        self.assertEqual(job.duration_seconds, 60.0)

    def test_set_expiration_method(self):
        """Test set_expiration method."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # Test default expiration (7 days)
        job.set_expiration()
        expected_expiry = timezone.now() + timedelta(days=7)
        self.assertAlmostEqual(
            job.expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=60  # 1 minute tolerance
        )
        
        # Test custom expiration
        job.set_expiration(days=30)
        expected_expiry = timezone.now() + timedelta(days=30)
        self.assertAlmostEqual(
            job.expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=60
        )

    def test_mark_as_started_method(self):
        """Test mark_as_started method."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        initial_time = timezone.now()
        job.mark_as_started()
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'processing')
        self.assertIsNotNone(job.started_at)
        self.assertGreaterEqual(job.started_at, initial_time)

    def test_mark_as_completed_method(self):
        """Test mark_as_completed method."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        file_path = '/path/to/export.csv'
        file_size = 1024
        row_count = 100
        
        initial_time = timezone.now()
        job.mark_as_completed(
            file_path=file_path,
            file_size=file_size,
            row_count=row_count
        )
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.progress, 100)
        self.assertEqual(job.file_path, file_path)
        self.assertEqual(job.file_size, file_size)
        self.assertEqual(job.row_count, row_count)
        self.assertIsNotNone(job.completed_at)
        self.assertGreaterEqual(job.completed_at, initial_time)
        self.assertIsNotNone(job.expires_at)  # Default expiration should be set

    def test_mark_as_completed_without_optional_args(self):
        """Test mark_as_completed without optional arguments."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        job.mark_as_completed()
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.progress, 100)
        self.assertEqual(job.file_path, '')  # Default empty string
        self.assertIsNone(job.file_size)
        self.assertIsNone(job.row_count)

    def test_mark_as_failed_method(self):
        """Test mark_as_failed method."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        error_message = 'Test error occurred'
        initial_time = timezone.now()
        
        job.mark_as_failed(error_message)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertEqual(job.error_message, error_message)
        self.assertIsNotNone(job.completed_at)
        self.assertGreaterEqual(job.completed_at, initial_time)

    def test_update_progress_method(self):
        """Test update_progress method."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # Valid progress updates
        job.update_progress(25)
        job.refresh_from_db()
        self.assertEqual(job.progress, 25)
        
        job.update_progress(75)
        job.refresh_from_db()
        self.assertEqual(job.progress, 75)
        
        job.update_progress(100)
        job.refresh_from_db()
        self.assertEqual(job.progress, 100)
        
        # Invalid progress values should not update
        original_progress = job.progress
        job.update_progress(-10)
        job.refresh_from_db()
        self.assertEqual(job.progress, original_progress)
        
        job.update_progress(150)
        job.refresh_from_db()
        self.assertEqual(job.progress, original_progress)

    def test_get_active_jobs_class_method(self):
        """Test get_active_jobs class method."""
        # Create various export jobs with different statuses
        active_job1 = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        active_job2 = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='processing'
        )
        
        # Completed job (should not appear in active jobs)
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='parquet',
            status='completed'
        )
        
        # Failed job (should not appear in active jobs)
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='excel',
            status='failed'
        )
        
        # Get all active jobs
        active_jobs = ExportJob.get_active_jobs()
        self.assertEqual(active_jobs.count(), 2)
        
        active_job_ids = list(active_jobs.values_list('id', flat=True))
        self.assertIn(active_job1.id, active_job_ids)
        self.assertIn(active_job2.id, active_job_ids)
        
        # Get active jobs for specific user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass'
        )
        
        ExportJob.objects.create(
            user=other_user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        user_active_jobs = ExportJob.get_active_jobs(user=self.user)
        self.assertEqual(user_active_jobs.count(), 2)

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_expired_class_method(self, mock_remove, mock_exists):
        """Test cleanup_expired class method."""
        # Mock file system operations
        mock_exists.return_value = True
        
        # Create expired completed job
        expired_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_path='/path/to/expired_file.csv'
        )
        expired_job.expires_at = timezone.now() - timedelta(days=1)
        expired_job.save()
        
        # Create non-expired completed job
        active_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='completed',
            file_path='/path/to/active_file.json'
        )
        active_job.expires_at = timezone.now() + timedelta(days=1)
        active_job.save()
        
        # Create expired but non-completed job (should not be cleaned up)
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='parquet',
            status='failed',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Run cleanup
        cleaned_count = ExportJob.cleanup_expired()
        
        # Check results
        self.assertEqual(cleaned_count, 1)
        
        expired_job.refresh_from_db()
        self.assertEqual(expired_job.status, 'expired')
        self.assertEqual(expired_job.file_path, '')
        
        active_job.refresh_from_db()
        self.assertEqual(active_job.status, 'completed')  # Should remain unchanged
        
        # Check that file removal was attempted
        mock_exists.assert_called_with('/path/to/expired_file.csv')
        mock_remove.assert_called_with('/path/to/expired_file.csv')

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_expired_file_not_exists(self, mock_remove, mock_exists):
        """Test cleanup_expired when file doesn't exist."""
        mock_exists.return_value = False
        
        expired_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_path='/path/to/nonexistent_file.csv'
        )
        expired_job.expires_at = timezone.now() - timedelta(days=1)
        expired_job.save()
        
        cleaned_count = ExportJob.cleanup_expired()
        
        self.assertEqual(cleaned_count, 1)
        mock_exists.assert_called_with('/path/to/nonexistent_file.csv')
        mock_remove.assert_not_called()  # Should not try to remove non-existent file

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_expired_file_removal_error(self, mock_remove, mock_exists):
        """Test cleanup_expired when file removal fails."""
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")
        
        expired_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_path='/path/to/protected_file.csv'
        )
        expired_job.expires_at = timezone.now() - timedelta(days=1)
        expired_job.save()
        
        # Should not raise exception even if file removal fails
        cleaned_count = ExportJob.cleanup_expired()
        
        self.assertEqual(cleaned_count, 1)
        
        expired_job.refresh_from_db()
        self.assertEqual(expired_job.status, 'expired')  # Should still update status

    def test_database_constraints(self):
        """Test database constraints and indexes."""
        # Test that user and datasource are required
        with self.assertRaises(IntegrityError):
            ExportJob.objects.create(
                datasource=self.datasource,
                format='csv'
                # Missing user
            )
        
        with self.assertRaises(IntegrityError):
            ExportJob.objects.create(
                user=self.user,
                format='csv'
                # Missing datasource
            )

    def test_model_ordering(self):
        """Test that jobs are ordered by created_at descending."""
        # Create jobs with slight time differences
        job1 = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        job2 = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json'
        )
        
        job3 = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='parquet'
        )
        
        jobs = list(ExportJob.objects.all())
        
        # Should be ordered by created_at descending (most recent first)
        self.assertEqual(jobs[0], job3)
        self.assertEqual(jobs[1], job2)
        self.assertEqual(jobs[2], job1)

    def test_related_name_functionality(self):
        """Test that related names work correctly."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # Test user.export_jobs related name
        user_jobs = self.user.export_jobs.all()
        self.assertEqual(user_jobs.count(), 1)
        self.assertEqual(user_jobs.first(), job)
        
        # Test datasource.export_jobs related name
        datasource_jobs = self.datasource.export_jobs.all()
        self.assertEqual(datasource_jobs.count(), 1)
        self.assertEqual(datasource_jobs.first(), job)