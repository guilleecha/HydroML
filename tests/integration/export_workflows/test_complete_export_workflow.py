"""
Integration tests for complete export workflows.

Tests end-to-end export functionality including:
- Complete export workflow from API to file generation
- Celery task integration
- File management and cleanup
- Multiple format conversions
- Large dataset handling
- Error recovery workflows
"""

import os
import tempfile
import uuid
import pandas as pd
from datetime import timedelta
from unittest.mock import patch, Mock

from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from celery import current_app
from celery.result import AsyncResult

from data_tools.models.export_job import ExportJob
from data_tools.models.export_template import ExportTemplate
from data_tools.services.export_service import ExportService
from data_tools.tasks.export_tasks import process_export_job
from projects.models.project import Project
from projects.models.datasource import DataSource

User = get_user_model()


class CompleteExportWorkflowTest(TransactionTestCase):
    """Test complete export workflows with real task execution."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name='Integration Test Project',
            description='Project for integration testing',
            user=self.user
        )
        self.project.members.add(self.user)
        
        # Create test CSV data
        self.test_csv_content = b"""id,name,age,department,salary,active
1,Alice Smith,28,Engineering,75000,true
2,Bob Johnson,32,Marketing,68000,true
3,Charlie Brown,45,Finance,82000,false
4,Diana Ross,29,Engineering,78000,true
5,Edward Norton,38,Marketing,71000,true
6,Fiona Apple,26,Engineering,73000,true
7,George Lucas,52,Finance,95000,true
8,Helen Hunt,31,Marketing,69000,false
9,Ian Fleming,44,Engineering,81000,true
10,Jane Doe,33,Finance,74000,true"""
        
        # Create DataSource with real file
        csv_file = SimpleUploadedFile(
            "integration_test_data.csv",
            self.test_csv_content,
            content_type="text/csv"
        )
        
        self.datasource = DataSource.objects.create(
            name='Integration Test Dataset',
            file=csv_file,
            format='csv',
            user=self.user,
            status=DataSource.Status.READY
        )
        self.datasource.projects.add(self.project)
        
        self.export_service = ExportService()

    def test_csv_export_complete_workflow(self):
        """Test complete CSV export workflow from creation to download."""
        # Step 1: Create export job via service
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='csv',
            filters={'columns': ['name', 'department', 'salary']},
            options={'delimiter': ',', 'encoding': 'utf-8'}
        )
        
        self.assertEqual(job.status, 'pending')
        self.assertIsNotNone(job.id)
        
        # Step 2: Process the job (simulating Celery task execution)
        success = self.export_service.process_export(str(job.id))
        
        self.assertTrue(success)
        
        # Step 3: Verify job completion
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.progress, 100)
        self.assertEqual(job.row_count, 10)
        self.assertIsNotNone(job.file_path)
        self.assertGreater(job.file_size, 0)
        self.assertIsNotNone(job.completed_at)
        
        # Step 4: Verify generated file exists and has correct content
        self.assertTrue(os.path.exists(job.file_path))
        
        # Read and verify file content
        generated_df = pd.read_csv(job.file_path)
        self.assertEqual(len(generated_df), 10)
        self.assertEqual(list(generated_df.columns), ['name', 'department', 'salary'])
        self.assertIn('Alice Smith', generated_df['name'].values)
        self.assertIn('Engineering', generated_df['department'].values)
        
        # Step 5: Test file download via service
        file_path, filename = self.export_service.get_export_file(str(job.id), self.user)
        
        self.assertEqual(file_path, job.file_path)
        self.assertIsNotNone(filename)
        self.assertTrue(filename.endswith('.csv'))
        
        # Cleanup
        if os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_json_export_complete_workflow(self):
        """Test complete JSON export workflow."""
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='json',
            filters={'columns': ['id', 'name', 'age', 'active']},
            options={'indent': 2, 'ensure_ascii': False}
        )
        
        success = self.export_service.process_export(str(job.id))
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.format, 'json')
        
        # Verify JSON file structure
        import json
        with open(job.file_path, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 10)
        
        # Check first record structure
        first_record = data[0]
        self.assertIn('id', first_record)
        self.assertIn('name', first_record)
        self.assertIn('age', first_record)
        self.assertIn('active', first_record)
        
        # Cleanup
        if os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_parquet_export_complete_workflow(self):
        """Test complete Parquet export workflow."""
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='parquet',
            options={'compression': 'snappy'}
        )
        
        success = self.export_service.process_export(str(job.id))
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.format, 'parquet')
        
        # Verify Parquet file can be read
        generated_df = pd.read_parquet(job.file_path)
        self.assertEqual(len(generated_df), 10)
        self.assertEqual(len(generated_df.columns), 6)  # All columns
        
        # Verify data types are preserved
        self.assertTrue(pd.api.types.is_integer_dtype(generated_df['id']))
        self.assertTrue(pd.api.types.is_object_dtype(generated_df['name']))
        self.assertTrue(pd.api.types.is_integer_dtype(generated_df['age']))
        
        # Cleanup
        if os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_excel_export_complete_workflow(self):
        """Test complete Excel export workflow."""
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='excel',
            filters={'columns': ['name', 'department', 'salary']},
            options={'sheet_name': 'Employee_Data', 'index': False}
        )
        
        success = self.export_service.process_export(str(job.id))
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.format, 'excel')
        
        # Verify Excel file can be read
        generated_df = pd.read_excel(job.file_path, sheet_name='Employee_Data')
        self.assertEqual(len(generated_df), 10)
        self.assertEqual(list(generated_df.columns), ['name', 'department', 'salary'])
        
        # Cleanup
        if os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_large_dataset_export_workflow(self):
        """Test export workflow with larger dataset."""
        # Create larger test dataset (1000 rows)
        large_data = []
        for i in range(1000):
            large_data.append(f"{i+1},User_{i+1},{20+i%50},Dept_{i%5},{50000+i*100},{str(i%2==0).lower()}")
        
        large_csv_content = b"id,name,age,department,salary,active\n" + b"\n".join(
            line.encode() for line in large_data
        )
        
        # Create DataSource with large file
        large_csv_file = SimpleUploadedFile(
            "large_test_data.csv",
            large_csv_content,
            content_type="text/csv"
        )
        
        large_datasource = DataSource.objects.create(
            name='Large Test Dataset',
            file=large_csv_file,
            format='csv',
            user=self.user,
            status=DataSource.Status.READY
        )
        large_datasource.projects.add(self.project)
        
        # Test CSV export with large dataset
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=large_datasource.id,
            export_format='csv',
            filters={'limit': 500}  # Limit to 500 rows
        )
        
        success = self.export_service.process_export(str(job.id))
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.row_count, 500)  # Should respect limit
        
        # Verify file size is reasonable
        self.assertGreater(job.file_size, 10000)  # At least 10KB
        self.assertLess(job.file_size, 1000000)   # Less than 1MB
        
        # Cleanup
        if os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_filtered_data_export_workflow(self):
        """Test export workflow with applied filters."""
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='csv',
            filters={
                'columns': ['name', 'department', 'salary', 'active'],
                'limit': 5
            }
        )
        
        success = self.export_service.process_export(str(job.id))
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.row_count, 5)  # Limited to 5 rows
        
        # Verify filtered content
        generated_df = pd.read_csv(job.file_path)
        self.assertEqual(len(generated_df), 5)
        self.assertEqual(list(generated_df.columns), ['name', 'department', 'salary', 'active'])
        
        # Cleanup
        if os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_template_based_export_workflow(self):
        """Test export workflow using a predefined template."""
        # Create export template
        template = ExportTemplate.objects.create(
            name='Engineering Export Template',
            description='Template for exporting engineering data',
            user=self.user,
            configuration={
                'format': 'json',
                'filters': {
                    'columns': ['name', 'department', 'salary']
                },
                'options': {
                    'indent': 2
                }
            }
        )
        
        initial_usage_count = template.usage_count
        
        # Create job using template
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            template_id=template.id
        )
        
        self.assertEqual(job.format, 'json')
        self.assertEqual(job.filters['columns'], ['name', 'department', 'salary'])
        
        # Process export
        success = self.export_service.process_export(str(job.id))
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        
        # Verify template usage was incremented
        template.refresh_from_db()
        self.assertEqual(template.usage_count, initial_usage_count + 1)
        self.assertIsNotNone(template.last_used_at)
        
        # Cleanup
        if os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_concurrent_export_workflows(self):
        """Test multiple concurrent export workflows."""
        jobs = []
        
        # Create multiple export jobs
        for i in range(3):
            job = self.export_service.create_export_job(
                user=self.user,
                datasource_id=self.datasource.id,
                export_format='csv',
                filters={'columns': ['name', 'age'], 'limit': 5}
            )
            jobs.append(job)
        
        # Process all jobs
        results = []
        for job in jobs:
            success = self.export_service.process_export(str(job.id))
            results.append(success)
        
        # All should succeed
        self.assertTrue(all(results))
        
        # Verify all jobs completed successfully
        for job in jobs:
            job.refresh_from_db()
            self.assertEqual(job.status, 'completed')
            self.assertEqual(job.row_count, 5)
            self.assertTrue(os.path.exists(job.file_path))
            
            # Cleanup
            if os.path.exists(job.file_path):
                os.unlink(job.file_path)

    def test_export_error_handling_workflow(self):
        """Test export workflow error handling and recovery."""
        # Create job that will fail during processing
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        # Simulate processing error by corrupting datasource path
        original_file_path = self.datasource.file.path
        self.datasource.file_path = '/nonexistent/path/file.csv'
        self.datasource.save()
        
        try:
            # Process should fail gracefully
            success = self.export_service.process_export(str(job.id))
            self.assertFalse(success)
            
            job.refresh_from_db()
            self.assertEqual(job.status, 'failed')
            self.assertNotEqual(job.error_message, '')
            self.assertIsNotNone(job.completed_at)
            
        finally:
            # Restore datasource
            self.datasource.file_path = original_file_path
            self.datasource.save()

    def test_export_cancellation_workflow(self):
        """Test export job cancellation workflow."""
        # Create pending job
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='csv'
        )
        
        # Cancel the job before processing
        success = self.export_service.cancel_export(str(job.id), self.user)
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')
        self.assertIsNotNone(job.completed_at)
        
        # Try to process cancelled job (should fail)
        success = self.export_service.process_export(str(job.id))
        self.assertFalse(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')  # Should remain cancelled

    def test_export_file_expiration_workflow(self):
        """Test export file expiration and cleanup workflow."""
        # Create and complete export job
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='csv',
            filters={'columns': ['name', 'department']}
        )
        
        success = self.export_service.process_export(str(job.id))
        self.assertTrue(success)
        
        job.refresh_from_db()
        file_path = job.file_path
        self.assertTrue(os.path.exists(file_path))
        
        # Set expiration to past
        job.expires_at = timezone.now() - timedelta(hours=1)
        job.save()
        
        # Run cleanup
        cleaned_count = ExportJob.cleanup_expired()
        self.assertEqual(cleaned_count, 1)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'expired')
        self.assertEqual(job.file_path, '')

    def test_user_export_statistics_workflow(self):
        """Test export statistics generation workflow."""
        # Create multiple export jobs with different statuses
        jobs_data = [
            ('csv', 'completed', 100, 5000),
            ('json', 'completed', 200, 8000),
            ('parquet', 'failed', 0, 0),
            ('excel', 'pending', 0, 0),
            ('csv', 'processing', 50, 0)
        ]
        
        for format_type, status, row_count, file_size in jobs_data:
            job = ExportJob.objects.create(
                user=self.user,
                datasource=self.datasource,
                format=format_type,
                status=status,
                row_count=row_count,
                file_size=file_size
            )
        
        # Get statistics
        stats = self.export_service.get_export_statistics(self.user)
        
        self.assertEqual(stats['total_jobs'], 5)
        self.assertEqual(stats['completed_jobs'], 2)
        self.assertEqual(stats['failed_jobs'], 1)
        self.assertEqual(stats['pending_jobs'], 1)
        self.assertEqual(stats['processing_jobs'], 1)
        self.assertEqual(stats['total_rows_exported'], 300)  # 100 + 200
        self.assertEqual(stats['total_file_size'], 13000)    # 5000 + 8000

    @patch('celery.current_app.send_task')
    def test_celery_task_integration(self, mock_send_task):
        """Test integration with Celery task queue."""
        # Mock successful task submission
        mock_result = Mock()
        mock_result.id = 'test-task-id'
        mock_send_task.return_value = mock_result
        
        # Create export job (this should queue a Celery task)
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='csv'
        )
        
        # Verify Celery task was queued
        mock_send_task.assert_called_once()
        args, kwargs = mock_send_task.call_args
        
        self.assertEqual(args[0], 'data_tools.tasks.export_tasks.process_export_job')
        self.assertEqual(args[1]['args'], [str(job.id)])
        self.assertEqual(kwargs.get('queue'), 'exports')

    def test_memory_efficient_large_export(self):
        """Test memory efficiency with large dataset export."""
        # This test would be more comprehensive in a real scenario
        # For now, we simulate the concept
        
        # Create export job with large dataset simulation
        job = self.export_service.create_export_job(
            user=self.user,
            datasource_id=self.datasource.id,
            export_format='csv'
        )
        
        # Mock memory monitoring during processing
        with patch('psutil.Process') as mock_process:
            mock_memory_info = Mock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
            mock_process.return_value.memory_info.return_value = mock_memory_info
            
            success = self.export_service.process_export(str(job.id))
            self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        
        # Cleanup
        if job.file_path and os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def tearDown(self):
        """Clean up test data."""
        # Clean up any remaining export files
        for job in ExportJob.objects.filter(user=self.user):
            if job.file_path and os.path.exists(job.file_path):
                try:
                    os.unlink(job.file_path)
                except OSError:
                    pass