"""
Comprehensive unit tests for ExportService.

Tests service layer functionality including:
- Export job creation and validation
- Data processing and transformation
- Format conversion coordination
- Error handling and edge cases
- Performance considerations
- Security validation
"""

import os
import tempfile
import uuid
import pandas as pd
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock, call

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.conf import settings

from data_tools.models.export_job import ExportJob
from data_tools.models.export_template import ExportTemplate
from data_tools.services.export_service import ExportService
from data_tools.services.export_formats import ExportFormatHandler
from data_tools.services.file_manager import ExportFileManager
from projects.models.project import Project
from projects.models.datasource import DataSource

User = get_user_model()


class ExportServiceComprehensiveTest(TestCase):
    """Comprehensive test suite for ExportService."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
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
        
        # Create test DataFrame
        self.test_df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000.0, 60000.0, 75000.0, 55000.0, 65000.0],
            'active': [True, False, True, True, False]
        })
        
        self.export_service = ExportService()

    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_create_export_job_success(self, mock_process):
        """Test successful export job creation."""
        mock_process.return_value = self.test_df
        
        with patch.object(self.export_service, '_queue_export_job') as mock_queue:
            job = self.export_service.create_export_job(
                user=self.user,
                datasource_id=self.datasource.id,
                export_format='csv',
                filters={'columns': ['name', 'age']},
                options={'delimiter': ',', 'encoding': 'utf-8'}
            )
            
            self.assertIsInstance(job, ExportJob)
            self.assertEqual(job.user, self.user)
            self.assertEqual(job.datasource, self.datasource)
            self.assertEqual(job.format, 'csv')
            self.assertEqual(job.status, 'pending')
            self.assertEqual(job.filters['columns'], ['name', 'age'])
            
            # Should queue the job for processing
            mock_queue.assert_called_once_with(job)

    def test_create_export_job_invalid_datasource(self):
        """Test export job creation with invalid datasource ID."""
        invalid_id = uuid.uuid4()
        
        with self.assertRaises(ValidationError) as cm:
            self.export_service.create_export_job(
                user=self.user,
                datasource_id=invalid_id,
                export_format='csv'
            )
        
        self.assertIn('DataSource not found', str(cm.exception))

    def test_create_export_job_no_access(self):
        """Test export job creation without datasource access."""
        with self.assertRaises(PermissionDenied) as cm:
            self.export_service.create_export_job(
                user=self.other_user,
                datasource_id=self.datasource.id,
                export_format='csv'
            )
        
        self.assertIn('Access denied', str(cm.exception))

    def test_create_export_job_invalid_format(self):
        """Test export job creation with invalid format."""
        with self.assertRaises(ValidationError) as cm:
            self.export_service.create_export_job(
                user=self.user,
                datasource_id=self.datasource.id,
                export_format='invalid_format'
            )
        
        self.assertIn('Invalid export format', str(cm.exception))

    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_create_export_job_with_template(self, mock_process):
        """Test export job creation using a template."""
        mock_process.return_value = self.test_df
        
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user,
            configuration={
                'format': 'json',
                'filters': {'columns': ['id', 'name']},
                'options': {'indent': 2}
            }
        )
        
        with patch.object(self.export_service, '_queue_export_job'):
            job = self.export_service.create_export_job(
                user=self.user,
                datasource_id=self.datasource.id,
                template_id=template.id
            )
            
            self.assertEqual(job.format, 'json')
            self.assertEqual(job.filters['columns'], ['id', 'name'])
            
            # Template usage should be incremented
            template.refresh_from_db()
            self.assertEqual(template.usage_count, 1)
            self.assertIsNotNone(template.last_used_at)

    def test_create_export_job_template_not_accessible(self):
        """Test export job creation with inaccessible template."""
        template = ExportTemplate.objects.create(
            name='Other User Template',
            user=self.other_user,
            template_type='user',
            configuration={'format': 'csv'}
        )
        
        with self.assertRaises(PermissionDenied):
            self.export_service.create_export_job(
                user=self.user,
                datasource_id=self.datasource.id,
                template_id=template.id
            )

    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_create_export_job_empty_dataset(self, mock_process):
        """Test export job creation with empty dataset."""
        empty_df = pd.DataFrame()
        mock_process.return_value = empty_df
        
        with self.assertRaises(ValidationError) as cm:
            self.export_service.create_export_job(
                user=self.user,
                datasource_id=self.datasource.id,
                export_format='csv'
            )
        
        self.assertIn('No data to export', str(cm.exception))

    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_process_export_success(self, mock_process_data):
        """Test successful export processing."""
        mock_process_data.return_value = self.test_df
        
        # Create export job
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        with patch.object(self.export_service.file_manager, 'generate_file_path') as mock_path, \
             patch.object(self.export_service.format_handler, 'to_csv') as mock_to_csv:
            
            test_file_path = '/tmp/test_export.csv'
            mock_path.return_value = test_file_path
            mock_to_csv.return_value = None  # Successful conversion
            
            with patch('os.path.getsize', return_value=1024):
                success = self.export_service.process_export(str(job.id))
            
            self.assertTrue(success)
            
            # Verify job was updated correctly
            job.refresh_from_db()
            self.assertEqual(job.status, 'completed')
            self.assertEqual(job.file_path, test_file_path)
            self.assertEqual(job.file_size, 1024)
            self.assertEqual(job.row_count, 5)
            self.assertEqual(job.progress, 100)

    def test_process_export_job_not_found(self):
        """Test processing non-existent export job."""
        invalid_id = str(uuid.uuid4())
        
        success = self.export_service.process_export(invalid_id)
        
        self.assertFalse(success)

    def test_process_export_wrong_status(self):
        """Test processing job with wrong status."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'  # Already completed
        )
        
        success = self.export_service.process_export(str(job.id))
        
        self.assertFalse(success)
        # Status should remain unchanged
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')

    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_process_export_data_processing_error(self, mock_process_data):
        """Test export processing with data processing error."""
        mock_process_data.side_effect = Exception("Data processing failed")
        
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        success = self.export_service.process_export(str(job.id))
        
        self.assertFalse(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertIn('Data processing failed', job.error_message)

    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_process_export_format_conversion_error(self, mock_process_data):
        """Test export processing with format conversion error."""
        mock_process_data.return_value = self.test_df
        
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        with patch.object(self.export_service.file_manager, 'generate_file_path') as mock_path, \
             patch.object(self.export_service.format_handler, 'to_csv') as mock_to_csv:
            
            mock_path.return_value = '/tmp/test_export.csv'
            mock_to_csv.side_effect = Exception("Conversion failed")
            
            success = self.export_service.process_export(str(job.id))
        
        self.assertFalse(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertIn('Conversion failed', job.error_message)

    def test_cancel_export_success(self):
        """Test successful export cancellation."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        success = self.export_service.cancel_export(str(job.id), self.user)
        
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')
        self.assertIsNotNone(job.completed_at)

    def test_cancel_export_already_processing(self):
        """Test cancelling job that's already processing."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='processing'
        )
        
        # Should still allow cancellation of processing jobs
        success = self.export_service.cancel_export(str(job.id), self.user)
        
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')

    def test_cancel_export_already_completed(self):
        """Test cancelling job that's already completed."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        success = self.export_service.cancel_export(str(job.id), self.user)
        
        self.assertFalse(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')  # Should remain unchanged

    def test_cancel_export_wrong_user(self):
        """Test cancelling job by wrong user."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        success = self.export_service.cancel_export(str(job.id), self.other_user)
        
        self.assertFalse(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'pending')  # Should remain unchanged

    def test_cancel_export_job_not_found(self):
        """Test cancelling non-existent job."""
        invalid_id = str(uuid.uuid4())
        
        success = self.export_service.cancel_export(invalid_id, self.user)
        
        self.assertFalse(success)

    def test_get_export_file_success(self):
        """Test getting export file for download."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(b'id,name,age\n1,Alice,25\n2,Bob,30\n')
            tmp_file.flush()
            
            job = ExportJob.objects.create(
                user=self.user,
                datasource=self.datasource,
                format='csv',
                status='completed',
                file_path=tmp_file.name
            )
            
            try:
                file_path, filename = self.export_service.get_export_file(str(job.id), self.user)
                
                self.assertEqual(file_path, tmp_file.name)
                self.assertIsNotNone(filename)
                self.assertTrue(filename.endswith('.csv'))
                self.assertIn(self.datasource.name.replace(' ', '_'), filename)
                
            finally:
                os.unlink(tmp_file.name)

    def test_get_export_file_not_completed(self):
        """Test getting file for non-completed job."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='processing'
        )
        
        file_path, filename = self.export_service.get_export_file(str(job.id), self.user)
        
        self.assertIsNone(file_path)
        self.assertIsNone(filename)

    def test_get_export_file_expired(self):
        """Test getting expired export file."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_path='/tmp/expired_file.csv'
        )
        job.expires_at = timezone.now() - timedelta(days=1)
        job.save()
        
        file_path, filename = self.export_service.get_export_file(str(job.id), self.user)
        
        self.assertIsNone(file_path)
        self.assertIsNone(filename)

    def test_get_export_file_wrong_user(self):
        """Test getting file by wrong user."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_path='/tmp/test_file.csv'
        )
        
        file_path, filename = self.export_service.get_export_file(str(job.id), self.other_user)
        
        self.assertIsNone(file_path)
        self.assertIsNone(filename)

    def test_get_export_file_file_not_exists(self):
        """Test getting file that doesn't exist on filesystem."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_path='/nonexistent/file.csv'
        )
        
        file_path, filename = self.export_service.get_export_file(str(job.id), self.user)
        
        self.assertIsNone(file_path)
        self.assertIsNone(filename)

    def test_get_user_export_jobs(self):
        """Test getting user's export jobs."""
        # Create jobs for user
        job1 = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        job2 = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='pending'
        )
        
        # Create job for other user (should not appear)
        ExportJob.objects.create(
            user=self.other_user,
            datasource=self.datasource,
            format='parquet',
            status='failed'
        )
        
        user_jobs = self.export_service.get_user_export_jobs(self.user)
        
        self.assertEqual(user_jobs.count(), 2)
        job_ids = list(user_jobs.values_list('id', flat=True))
        self.assertIn(job1.id, job_ids)
        self.assertIn(job2.id, job_ids)

    def test_get_user_export_jobs_with_status_filter(self):
        """Test getting user's export jobs with status filter."""
        # Create jobs with different statuses
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        pending_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='pending'
        )
        
        pending_jobs = self.export_service.get_user_export_jobs(self.user, status='pending')
        
        self.assertEqual(pending_jobs.count(), 1)
        self.assertEqual(pending_jobs.first(), pending_job)

    def test_get_export_statistics(self):
        """Test getting export statistics."""
        # Create various export jobs
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_size=1024,
            row_count=100
        )
        
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='completed',
            file_size=2048,
            row_count=200
        )
        
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='parquet',
            status='failed'
        )
        
        stats = self.export_service.get_export_statistics(self.user)
        
        self.assertEqual(stats['total_jobs'], 3)
        self.assertEqual(stats['completed_jobs'], 2)
        self.assertEqual(stats['failed_jobs'], 1)
        self.assertEqual(stats['pending_jobs'], 0)
        self.assertEqual(stats['total_file_size'], 3072)  # 1024 + 2048
        self.assertEqual(stats['total_rows_exported'], 300)  # 100 + 200

    def test_cleanup_user_exports(self):
        """Test cleanup of user's old export files."""
        # Create old completed job
        old_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            file_path='/tmp/old_export.csv'
        )
        old_job.expires_at = timezone.now() - timedelta(days=1)
        old_job.save()
        
        # Create recent completed job  
        recent_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='completed',
            file_path='/tmp/recent_export.json'
        )
        recent_job.expires_at = timezone.now() + timedelta(days=1)
        recent_job.save()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove:
            
            cleaned_count = self.export_service.cleanup_user_exports(self.user)
        
        self.assertEqual(cleaned_count, 1)
        
        old_job.refresh_from_db()
        self.assertEqual(old_job.status, 'expired')
        
        recent_job.refresh_from_db()
        self.assertEqual(recent_job.status, 'completed')  # Should remain unchanged

    @patch('celery.current_app.send_task')
    def test_queue_export_job(self, mock_send_task):
        """Test queuing export job for processing."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        # Call private method directly for testing
        self.export_service._queue_export_job(job)
        
        mock_send_task.assert_called_once_with(
            'data_tools.tasks.export_tasks.process_export_job',
            args=[str(job.id)],
            kwargs={},
            queue='exports'
        )

    def test_validate_export_format(self):
        """Test export format validation."""
        # Test valid formats
        valid_formats = ['csv', 'json', 'parquet', 'excel']
        
        for format_type in valid_formats:
            try:
                self.export_service._validate_export_format(format_type)
            except ValidationError:
                self.fail(f"ValidationError raised for valid format: {format_type}")
        
        # Test invalid format
        with self.assertRaises(ValidationError):
            self.export_service._validate_export_format('invalid_format')

    def test_validate_export_filters(self):
        """Test export filters validation."""
        # Valid filters
        valid_filters = [
            {},
            {'columns': ['col1', 'col2']},
            {'limit': 1000},
            {'where': 'age > 25'},
            {'columns': ['name'], 'limit': 500, 'where': 'active = true'}
        ]
        
        for filters in valid_filters:
            try:
                self.export_service._validate_export_filters(filters)
            except ValidationError:
                self.fail(f"ValidationError raised for valid filters: {filters}")
        
        # Invalid filters
        invalid_filters = [
            "invalid_string",  # Should be dict
            {'columns': 'invalid_list'},  # columns should be list
            {'limit': 'invalid_number'},  # limit should be number
            {'limit': -10},  # limit should be positive
            {'unknown_filter': 'value'}  # unknown filter key
        ]
        
        for filters in invalid_filters:
            with self.assertRaises(ValidationError):
                self.export_service._validate_export_filters(filters)

    def test_check_datasource_access(self):
        """Test datasource access validation."""
        # User has access through project membership
        try:
            self.export_service._check_datasource_access(self.user, self.datasource)
        except PermissionDenied:
            self.fail("PermissionDenied raised for valid access")
        
        # Other user doesn't have access
        with self.assertRaises(PermissionDenied):
            self.export_service._check_datasource_access(self.other_user, self.datasource)

    def test_generate_export_filename(self):
        """Test export filename generation."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv'
        )
        
        filename = self.export_service._generate_export_filename(job)
        
        self.assertTrue(filename.endswith('.csv'))
        self.assertIn(self.datasource.name.replace(' ', '_'), filename)
        self.assertIn(str(job.created_at.date()), filename)

    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_apply_export_filters_columns(self, mock_process_data):
        """Test applying column filters."""
        mock_process_data.return_value = self.test_df
        
        filters = {'columns': ['name', 'age']}
        
        filtered_df = self.export_service._apply_export_filters(
            self.test_df, 
            filters
        )
        
        self.assertEqual(list(filtered_df.columns), ['name', 'age'])
        self.assertEqual(len(filtered_df), len(self.test_df))

    def test_apply_export_filters_limit(self):
        """Test applying limit filter."""
        filters = {'limit': 3}
        
        filtered_df = self.export_service._apply_export_filters(
            self.test_df,
            filters
        )
        
        self.assertEqual(len(filtered_df), 3)

    def test_apply_export_filters_combined(self):
        """Test applying multiple filters."""
        filters = {
            'columns': ['name', 'age', 'salary'],
            'limit': 2
        }
        
        filtered_df = self.export_service._apply_export_filters(
            self.test_df,
            filters
        )
        
        self.assertEqual(list(filtered_df.columns), ['name', 'age', 'salary'])
        self.assertEqual(len(filtered_df), 2)

    def test_memory_management_large_dataset(self):
        """Test memory management with large dataset simulation."""
        # Create a large DataFrame simulation
        large_df = pd.DataFrame({
            'col1': range(100000),
            'col2': ['data'] * 100000
        })
        
        with patch('data_tools.services.export_service.process_datasource_to_df', 
                   return_value=large_df):
            
            # Test that the service handles large datasets appropriately
            # This would typically involve chunked processing in a real implementation
            job = ExportJob.objects.create(
                user=self.user,
                datasource=self.datasource,
                format='csv'
            )
            
            with patch.object(self.export_service.file_manager, 'generate_file_path'), \
                 patch.object(self.export_service.format_handler, 'to_csv'), \
                 patch('os.path.getsize', return_value=10*1024*1024):  # 10MB
                
                success = self.export_service.process_export(str(job.id))
                
                self.assertTrue(success)
                
                job.refresh_from_db()
                self.assertEqual(job.row_count, 100000)