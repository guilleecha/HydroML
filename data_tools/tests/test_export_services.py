"""
Tests for export services functionality.

This module tests the export service layer, including format conversion,
file management, and job processing.
"""

import os
import tempfile
import pandas as pd
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from data_tools.models.export_job import ExportJob
from data_tools.services.export_service import ExportService
from data_tools.services.export_formats import ExportFormatHandler
from data_tools.services.file_manager import ExportFileManager
from projects.models.project import Project
from projects.models.datasource import DataSource


class ExportServiceTestCase(TestCase):
    """Test cases for ExportService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project description',
            owner=self.user
        )
        self.project.members.add(self.user)
        
        self.datasource = DataSource.objects.create(
            name='Test DataSource',
            project=self.project,
            file_type='csv',
            storage_type='local',
            file_path='test_data.csv'
        )
        
        self.export_service = ExportService()
    
    def test_create_export_job_success(self):
        """Test successful export job creation."""
        with patch('data_tools.services.export_service.process_datasource_to_df') as mock_process:
            mock_process.return_value = pd.DataFrame({'col1': [1, 2, 3]})
            
            with patch.object(self.export_service, '_queue_export_job'):
                job = self.export_service.create_export_job(
                    user=self.user,
                    datasource_id=self.datasource.id,
                    export_format='csv',
                    filters={'columns': ['col1']},
                    options={'delimiter': ','}
                )
                
                self.assertIsInstance(job, ExportJob)
                self.assertEqual(job.user, self.user)
                self.assertEqual(job.datasource, self.datasource)
                self.assertEqual(job.format, 'csv')
                self.assertEqual(job.status, 'pending')
    
    def test_create_export_job_invalid_format(self):
        """Test export job creation with invalid format."""
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            self.export_service.create_export_job(
                user=self.user,
                datasource_id=self.datasource.id,
                export_format='invalid_format'
            )
    
    def test_create_export_job_no_access(self):
        """Test export job creation without datasource access."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass'
        )
        
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            self.export_service.create_export_job(
                user=other_user,
                datasource_id=self.datasource.id,
                export_format='csv'
            )
    
    @patch('data_tools.services.export_service.process_datasource_to_df')
    def test_process_export_success(self, mock_process):
        """Test successful export processing."""
        # Create test DataFrame
        test_df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        mock_process.return_value = test_df
        
        # Create export job
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        with patch.object(self.export_service.file_manager, 'generate_file_path') as mock_path:
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
                mock_path.return_value = tmp_file.name
                
                try:
                    # Process export
                    success = self.export_service.process_export(str(job.id))
                    
                    self.assertTrue(success)
                    
                    # Refresh job from database
                    job.refresh_from_db()
                    self.assertEqual(job.status, 'completed')
                    self.assertEqual(job.row_count, 5)
                    self.assertTrue(os.path.exists(job.file_path))
                    
                finally:
                    # Clean up
                    if os.path.exists(tmp_file.name):
                        os.unlink(tmp_file.name)
    
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
    
    def test_cancel_export_wrong_user(self):
        """Test export cancellation with wrong user."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com', 
            password='testpass'
        )
        
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        success = self.export_service.cancel_export(str(job.id), other_user)
        
        self.assertFalse(success)
        job.refresh_from_db()
        self.assertEqual(job.status, 'pending')
    
    def test_get_export_file_success(self):
        """Test getting export file for download."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(b'col1,col2\n1,a\n2,b\n')
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
                self.assertIn('Test DataSource', filename)
                self.assertIn('.csv', filename)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_get_export_file_not_completed(self):
        """Test getting export file for non-completed job."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        file_path, filename = self.export_service.get_export_file(str(job.id), self.user)
        
        self.assertIsNone(file_path)
        self.assertIsNone(filename)


class ExportFormatHandlerTestCase(TestCase):
    """Test cases for ExportFormatHandler."""
    
    def setUp(self):
        """Set up test data."""
        self.test_df = pd.DataFrame({
            'int_col': [1, 2, 3, 4, 5],
            'str_col': ['a', 'b', 'c', 'd', 'e'],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'datetime_col': pd.date_range('2023-01-01', periods=5)
        })
        
        self.format_handler = ExportFormatHandler()
    
    def test_to_csv_success(self):
        """Test CSV conversion."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            try:
                self.format_handler.to_csv(self.test_df, tmp_file.name)
                
                self.assertTrue(os.path.exists(tmp_file.name))
                
                # Verify content
                loaded_df = pd.read_csv(tmp_file.name)
                self.assertEqual(len(loaded_df), 5)
                self.assertEqual(list(loaded_df.columns), ['int_col', 'str_col', 'float_col', 'datetime_col'])
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_to_csv_with_options(self):
        """Test CSV conversion with custom options."""
        options = {
            'delimiter': ';',
            'encoding': 'utf-8',
            'include_header': True
        }
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            try:
                self.format_handler.to_csv(self.test_df, tmp_file.name, options)
                
                # Read file content
                with open(tmp_file.name, 'r') as f:
                    content = f.read()
                    
                self.assertIn(';', content)  # Check delimiter
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_to_json_success(self):
        """Test JSON conversion."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            try:
                self.format_handler.to_json(self.test_df, tmp_file.name)
                
                self.assertTrue(os.path.exists(tmp_file.name))
                
                # Verify content
                loaded_df = pd.read_json(tmp_file.name)
                self.assertEqual(len(loaded_df), 5)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_to_parquet_success(self):
        """Test Parquet conversion."""
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
            try:
                self.format_handler.to_parquet(self.test_df, tmp_file.name)
                
                self.assertTrue(os.path.exists(tmp_file.name))
                
                # Verify content
                loaded_df = pd.read_parquet(tmp_file.name)
                self.assertEqual(len(loaded_df), 5)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_to_excel_success(self):
        """Test Excel conversion."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            try:
                self.format_handler.to_excel(self.test_df, tmp_file.name)
                
                self.assertTrue(os.path.exists(tmp_file.name))
                
                # Verify content
                loaded_df = pd.read_excel(tmp_file.name)
                self.assertEqual(len(loaded_df), 5)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_get_supported_formats(self):
        """Test supported formats information."""
        formats = self.format_handler.get_supported_formats()
        
        self.assertIn('csv', formats)
        self.assertIn('json', formats)
        self.assertIn('parquet', formats)
        self.assertIn('excel', formats)
        
        # Check format info structure
        csv_info = formats['csv']
        self.assertIn('name', csv_info)
        self.assertIn('extension', csv_info)
        self.assertIn('mime_type', csv_info)
        self.assertIn('options', csv_info)


class ExportFileManagerTestCase(TestCase):
    """Test cases for ExportFileManager."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project description', 
            owner=self.user
        )
        
        self.datasource = DataSource.objects.create(
            name='Test DataSource',
            project=self.project,
            file_type='csv'
        )
        
        self.export_job = Mock()
        self.export_job.id = 'test-job-id'
        self.export_job.user = self.user
        self.export_job.datasource = self.datasource
        self.export_job.format = 'csv'
        
        self.file_manager = ExportFileManager()
    
    def test_generate_file_path(self):
        """Test file path generation."""
        file_path = self.file_manager.generate_file_path(self.export_job)
        
        self.assertTrue(file_path.startswith(self.file_manager.base_export_dir))
        self.assertTrue(file_path.endswith('.csv'))
        self.assertIn('export_', file_path)
        
        # Check directory was created
        self.assertTrue(os.path.exists(os.path.dirname(file_path)))
    
    def test_validate_file_path_valid(self):
        """Test file path validation with valid path."""
        test_path = os.path.join(self.file_manager.base_export_dir, 'test', 'file.csv')
        
        result = self.file_manager.validate_file_path(test_path)
        
        self.assertTrue(result)
    
    def test_validate_file_path_invalid_extension(self):
        """Test file path validation with invalid extension."""
        test_path = os.path.join(self.file_manager.base_export_dir, 'test', 'file.exe')
        
        result = self.file_manager.validate_file_path(test_path)
        
        self.assertFalse(result)
    
    def test_validate_file_path_outside_base(self):
        """Test file path validation with path outside base directory."""
        test_path = '/tmp/malicious_file.csv'
        
        result = self.file_manager.validate_file_path(test_path)
        
        self.assertFalse(result)
    
    def test_delete_file_success(self):
        """Test successful file deletion."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            dir=self.file_manager.base_export_dir,
            suffix='.csv',
            delete=False
        ) as tmp_file:
            tmp_file.write(b'test,data\n1,a\n')
            tmp_file.flush()
            
            # Delete file
            success = self.file_manager.delete_file(tmp_file.name)
            
            self.assertTrue(success)
            self.assertFalse(os.path.exists(tmp_file.name))
    
    def test_get_file_info_existing_file(self):
        """Test getting info for existing file."""
        with tempfile.NamedTemporaryFile(
            dir=self.file_manager.base_export_dir,
            suffix='.csv',
            delete=False
        ) as tmp_file:
            tmp_file.write(b'test,data\n1,a\n')
            tmp_file.flush()
            
            try:
                info = self.file_manager.get_file_info(tmp_file.name)
                
                self.assertIsNotNone(info)
                self.assertEqual(info['extension'], '.csv')
                self.assertTrue(info['exists'])
                self.assertGreater(info['size'], 0)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_get_file_info_nonexistent_file(self):
        """Test getting info for non-existent file."""
        info = self.file_manager.get_file_info('/nonexistent/file.csv')
        
        self.assertIsNone(info)
    
    def test_get_storage_stats(self):
        """Test storage statistics."""
        # Create some test files
        test_files = []
        for ext in ['.csv', '.json']:
            with tempfile.NamedTemporaryFile(
                dir=self.file_manager.base_export_dir,
                suffix=ext,
                delete=False
            ) as tmp_file:
                tmp_file.write(b'test data')
                test_files.append(tmp_file.name)
        
        try:
            stats = self.file_manager.get_storage_stats()
            
            self.assertIsInstance(stats, dict)
            self.assertIn('total_files', stats)
            self.assertIn('total_size', stats)
            self.assertIn('by_extension', stats)
            self.assertGreaterEqual(stats['total_files'], 2)
            
        finally:
            # Clean up
            for file_path in test_files:
                try:
                    os.unlink(file_path)
                except OSError:
                    pass
    
    def test_check_storage_health(self):
        """Test storage health check."""
        health = self.file_manager.check_storage_health()
        
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)
        self.assertIn('storage_available', health)
        self.assertIn('permissions_ok', health)
        
        # Storage should be healthy in test environment
        self.assertTrue(health['storage_available'])
        self.assertTrue(health['permissions_ok'])