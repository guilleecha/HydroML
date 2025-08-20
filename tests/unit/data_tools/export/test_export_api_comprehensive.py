"""
Comprehensive API tests for Export endpoints.

Tests all API functionality including:
- Authentication and authorization
- CRUD operations for ExportJob and ExportTemplate
- Permission validation
- Input validation and error handling
- Bulk operations
- Status transitions
- File download functionality
"""

import json
import uuid
from datetime import timedelta
from unittest.mock import patch, Mock

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from data_tools.models.export_job import ExportJob
from data_tools.models.export_template import ExportTemplate
from projects.models.project import Project
from projects.models.datasource import DataSource

User = get_user_model()


class ExportAPIAuthenticationTest(APITestCase):
    """Test authentication requirements for export APIs."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_export_jobs_requires_authentication(self):
        """Test that export jobs API requires authentication."""
        url = reverse('data_tools:export_jobs_api')
        
        # Unauthenticated request
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticated request
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_export_templates_requires_authentication(self):
        """Test that export templates API requires authentication."""
        url = reverse('data_tools:export_templates_api')
        
        # Unauthenticated request
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticated request
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_export_job_detail_requires_authentication(self):
        """Test that export job detail API requires authentication."""
        job_id = uuid.uuid4()
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': job_id})
        
        # Unauthenticated request
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ExportJobAPITest(APITestCase):
    """Comprehensive tests for ExportJob API endpoints."""

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
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test project and datasource
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project',
            user=self.user
        )
        self.project.members.add(self.user)
        
        # Create test CSV file
        csv_content = b"id,name,age,salary\n1,Alice,25,50000\n2,Bob,30,60000\n3,Charlie,35,70000"
        csv_file = SimpleUploadedFile(
            "test_data.csv",
            csv_content,
            content_type="text/csv"
        )
        
        self.datasource = DataSource.objects.create(
            name='Test DataSource',
            file=csv_file,
            format='csv',
            user=self.user,
            status=DataSource.Status.READY
        )
        self.datasource.projects.add(self.project)
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)

    def test_create_export_job_success(self):
        """Test successful export job creation."""
        url = reverse('data_tools:export_jobs_api')
        data = {
            'datasource': str(self.datasource.id),
            'format': 'csv',
            'filters': {
                'columns': ['name', 'age'],
                'limit': 100
            },
            'options': {
                'delimiter': ',',
                'encoding': 'utf-8'
            }
        }
        
        with patch('data_tools.services.export_service.ExportService.create_export_job') as mock_create:
            mock_job = Mock()
            mock_job.id = uuid.uuid4()
            mock_job.status = 'pending'
            mock_job.format = 'csv'
            mock_job.created_at = timezone.now()
            mock_create.return_value = mock_job
            
            response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        self.assertEqual(response_data['data']['status'], 'pending')

    def test_create_export_job_validation_errors(self):
        """Test export job creation with validation errors."""
        url = reverse('data_tools:export_jobs_api')
        
        # Missing required fields
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid format
        data = {
            'datasource': str(self.datasource.id),
            'format': 'invalid_format'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid datasource UUID
        data = {
            'datasource': 'invalid-uuid',
            'format': 'csv'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-existent datasource
        data = {
            'datasource': str(uuid.uuid4()),
            'format': 'csv'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_export_job_no_access(self):
        """Test export job creation without datasource access."""
        # Create datasource for different user
        other_project = Project.objects.create(
            name='Other Project',
            user=self.other_user
        )
        other_project.members.add(self.other_user)
        
        other_datasource = DataSource.objects.create(
            name='Other DataSource',
            file_type='csv',
            user=self.other_user
        )
        other_datasource.projects.add(other_project)
        
        url = reverse('data_tools:export_jobs_api')
        data = {
            'datasource': str(other_datasource.id),
            'format': 'csv'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_export_jobs(self):
        """Test listing user's export jobs."""
        # Create export jobs for user
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
        
        url = reverse('data_tools:export_jobs_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        
        # Should only see current user's jobs
        jobs = response_data['data']['export_jobs']
        self.assertEqual(len(jobs), 2)
        
        job_ids = [job['id'] for job in jobs]
        self.assertIn(str(job1.id), job_ids)
        self.assertIn(str(job2.id), job_ids)

    def test_list_export_jobs_with_filters(self):
        """Test listing export jobs with status filter."""
        # Create jobs with different statuses
        completed_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='pending'
        )
        
        url = reverse('data_tools:export_jobs_api')
        response = self.client.get(url, {'status': 'completed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        jobs = response_data['data']['export_jobs']
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['id'], str(completed_job.id))

    def test_list_export_jobs_pagination(self):
        """Test export jobs list pagination."""
        # Create multiple jobs
        for i in range(15):
            ExportJob.objects.create(
                user=self.user,
                datasource=self.datasource,
                format='csv',
                status='completed'
            )
        
        url = reverse('data_tools:export_jobs_api')
        response = self.client.get(url, {'page': 1, 'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(len(response_data['data']['export_jobs']), 10)
        
        pagination = response_data['data']['pagination']
        self.assertEqual(pagination['total_count'], 15)
        self.assertEqual(pagination['page'], 1)
        self.assertEqual(pagination['page_size'], 10)
        self.assertEqual(pagination['total_pages'], 2)

    def test_get_export_job_detail(self):
        """Test retrieving specific export job."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            progress=100,
            row_count=1000,
            file_size=50000
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        job_data = response_data['data']
        self.assertEqual(job_data['id'], str(job.id))
        self.assertEqual(job_data['status'], 'completed')
        self.assertEqual(job_data['progress'], 100)
        self.assertEqual(job_data['row_count'], 1000)
        self.assertEqual(job_data['file_size'], 50000)

    def test_get_export_job_permission_denied(self):
        """Test accessing other user's export job."""
        job = ExportJob.objects.create(
            user=self.other_user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_export_job_not_found(self):
        """Test retrieving non-existent export job."""
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_export_job_success(self):
        """Test successful export job deletion."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': job.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Job should be deleted
        with self.assertRaises(ExportJob.DoesNotExist):
            ExportJob.objects.get(id=job.id)

    def test_delete_export_job_processing(self):
        """Test deleting job that's currently processing."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='processing'
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': job.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        
        # Job should still exist
        job.refresh_from_db()
        self.assertEqual(job.status, 'processing')

    def test_cancel_export_job_success(self):
        """Test successful export job cancellation."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='processing'
        )
        
        url = reverse('data_tools:export_job_cancel_api', kwargs={'pk': job.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')

    def test_cancel_export_job_already_completed(self):
        """Test cancelling already completed job."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        url = reverse('data_tools:export_job_cancel_api', kwargs={'pk': job.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')  # Unchanged

    def test_retry_export_job_success(self):
        """Test successful export job retry."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='failed',
            error_message='Test error',
            progress=50
        )
        
        url = reverse('data_tools:export_job_retry_api', kwargs={'pk': job.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress, 0)
        self.assertEqual(job.error_message, '')

    def test_retry_export_job_not_failed(self):
        """Test retrying job that hasn't failed."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        url = reverse('data_tools:export_job_retry_api', kwargs={'pk': job.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_download_export_file_success(self):
        """Test successful file download."""
        import tempfile
        
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
            
            url = reverse('data_tools:export_job_download_api', kwargs={'pk': job.id})
            
            try:
                response = self.client.get(url)
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response['Content-Type'], 'text/csv')
                self.assertIn('attachment', response['Content-Disposition'])
                
            finally:
                import os
                os.unlink(tmp_file.name)

    def test_download_export_file_not_completed(self):
        """Test downloading file from non-completed job."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='processing'
        )
        
        url = reverse('data_tools:export_job_download_api', kwargs={'pk': job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_bulk_delete_export_jobs(self):
        """Test bulk deletion of export jobs."""
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
            status='failed'
        )
        
        # Create job for other user (should not be deleted)
        other_job = ExportJob.objects.create(
            user=self.other_user,
            datasource=self.datasource,
            format='parquet',
            status='completed'
        )
        
        url = reverse('data_tools:export_jobs_bulk_delete_api')
        data = {
            'job_ids': [str(job1.id), str(job2.id), str(other_job.id)]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['data']['deleted_count'], 2)  # Only user's jobs
        
        # Check that jobs are deleted
        with self.assertRaises(ExportJob.DoesNotExist):
            ExportJob.objects.get(id=job1.id)
        
        with self.assertRaises(ExportJob.DoesNotExist):
            ExportJob.objects.get(id=job2.id)
        
        # Other user's job should still exist
        other_job.refresh_from_db()
        self.assertEqual(other_job.status, 'completed')

    def test_export_job_status_updates(self):
        """Test that job status updates are reflected in API."""
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': job.id})
        
        # Check initial status
        response = self.client.get(url)
        self.assertEqual(response.json()['data']['status'], 'pending')
        
        # Update status and check again
        job.status = 'processing'
        job.progress = 50
        job.save()
        
        response = self.client.get(url)
        data = response.json()['data']
        self.assertEqual(data['status'], 'processing')
        self.assertEqual(data['progress'], 50)


class ExportTemplateAPITest(APITestCase):
    """Comprehensive tests for ExportTemplate API endpoints."""

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
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.client.force_authenticate(user=self.user)

    def test_create_export_template_success(self):
        """Test successful export template creation."""
        url = reverse('data_tools:export_templates_api')
        data = {
            'name': 'Test Template',
            'description': 'Test template description',
            'configuration': {
                'format': 'csv',
                'filters': {
                    'columns': ['name', 'age']
                },
                'options': {
                    'delimiter': ',',
                    'encoding': 'utf-8'
                }
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Check created template
        template = ExportTemplate.objects.get(id=response_data['data']['id'])
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.user, self.user)
        self.assertEqual(template.template_type, 'user')

    def test_create_export_template_validation_errors(self):
        """Test export template creation with validation errors."""
        url = reverse('data_tools:export_templates_api')
        
        # Missing required fields
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid configuration (missing format)
        data = {
            'name': 'Invalid Template',
            'configuration': {}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid format
        data = {
            'name': 'Invalid Template',
            'configuration': {'format': 'invalid_format'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_export_template_duplicate_name(self):
        """Test creating template with duplicate name."""
        # Create initial template
        ExportTemplate.objects.create(
            name='Duplicate Name',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_templates_api')
        data = {
            'name': 'Duplicate Name',
            'configuration': {'format': 'json'}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_export_templates(self):
        """Test listing available export templates."""
        # Create user template
        user_template = ExportTemplate.objects.create(
            name='User Template',
            user=self.user,
            template_type='user',
            configuration={'format': 'csv'}
        )
        
        # Create system template
        system_template = ExportTemplate.objects.create(
            name='System Template',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'json'}
        )
        
        # Create template for other user (should not appear)
        ExportTemplate.objects.create(
            name='Other User Template',
            user=self.other_user,
            template_type='user',
            configuration={'format': 'parquet'}
        )
        
        url = reverse('data_tools:export_templates_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        templates = response_data['data']['templates']
        
        self.assertEqual(len(templates), 2)
        template_names = [t['name'] for t in templates]
        self.assertIn('User Template', template_names)
        self.assertIn('System Template', template_names)
        self.assertNotIn('Other User Template', template_names)

    def test_list_export_templates_with_type_filter(self):
        """Test listing templates with type filter."""
        # Create templates of different types
        ExportTemplate.objects.create(
            name='User Template',
            user=self.user,
            template_type='user',
            configuration={'format': 'csv'}
        )
        
        ExportTemplate.objects.create(
            name='System Template',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'json'}
        )
        
        url = reverse('data_tools:export_templates_api')
        response = self.client.get(url, {'template_type': 'system'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        templates = response.json()['data']['templates']
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]['name'], 'System Template')

    def test_get_export_template_detail(self):
        """Test retrieving specific export template."""
        template = ExportTemplate.objects.create(
            name='Test Template',
            description='Test description',
            user=self.user,
            configuration={'format': 'csv', 'filters': {'columns': ['name']}},
            usage_count=5
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        template_data = response_data['data']
        
        self.assertEqual(template_data['id'], str(template.id))
        self.assertEqual(template_data['name'], 'Test Template')
        self.assertEqual(template_data['description'], 'Test description')
        self.assertEqual(template_data['usage_count'], 5)
        self.assertEqual(template_data['configuration']['format'], 'csv')

    def test_update_export_template_success(self):
        """Test successful export template update."""
        template = ExportTemplate.objects.create(
            name='Original Name',
            description='Original description',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        data = {
            'name': 'Updated Name',
            'description': 'Updated description',
            'configuration': {
                'format': 'json',
                'filters': {'columns': ['name', 'age']}
            }
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        template.refresh_from_db()
        self.assertEqual(template.name, 'Updated Name')
        self.assertEqual(template.description, 'Updated description')
        self.assertEqual(template.configuration['format'], 'json')

    def test_update_export_template_permission_denied(self):
        """Test updating other user's template."""
        template = ExportTemplate.objects.create(
            name='Other User Template',
            user=self.other_user,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        data = {'name': 'Hacked Name'}
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        template.refresh_from_db()
        self.assertEqual(template.name, 'Other User Template')  # Unchanged

    def test_delete_export_template_success(self):
        """Test successful export template deletion."""
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Template should be deleted
        with self.assertRaises(ExportTemplate.DoesNotExist):
            ExportTemplate.objects.get(id=template.id)

    def test_delete_system_template_admin_only(self):
        """Test that only admins can delete system templates."""
        system_template = ExportTemplate.objects.create(
            name='System Template',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': system_template.id})
        response = self.client.delete(url)
        
        # Regular user should not be able to delete system template
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Template should still exist
        system_template.refresh_from_db()
        self.assertEqual(system_template.name, 'System Template')

    def test_duplicate_export_template(self):
        """Test duplicating an export template."""
        original_template = ExportTemplate.objects.create(
            name='Original Template',
            description='Original description',
            user=self.user,
            configuration={'format': 'csv', 'filters': {'columns': ['name']}}
        )
        
        url = reverse('data_tools:export_template_duplicate_api', kwargs={'pk': original_template.id})
        data = {'name': 'Duplicated Template'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response_data = response.json()
        duplicate_id = response_data['data']['id']
        
        duplicate = ExportTemplate.objects.get(id=duplicate_id)
        self.assertEqual(duplicate.name, 'Duplicated Template')
        self.assertEqual(duplicate.description, original_template.description)
        self.assertEqual(duplicate.user, self.user)
        self.assertEqual(duplicate.configuration, original_template.configuration)
        self.assertEqual(duplicate.usage_count, 0)  # Reset usage count

    def test_get_popular_templates(self):
        """Test getting popular templates."""
        # Create popular system templates
        template1 = ExportTemplate.objects.create(
            name='Popular Template 1',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'csv'},
            usage_count=100
        )
        
        template2 = ExportTemplate.objects.create(
            name='Popular Template 2',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'json'},
            usage_count=50
        )
        
        # Create user template (should not appear in popular)
        ExportTemplate.objects.create(
            name='User Template',
            user=self.user,
            template_type='user',
            configuration={'format': 'parquet'},
            usage_count=200
        )
        
        url = reverse('data_tools:export_templates_popular_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        templates = response.json()['data']['templates']
        self.assertEqual(len(templates), 2)
        
        # Should be ordered by usage count descending
        self.assertEqual(templates[0]['name'], 'Popular Template 1')
        self.assertEqual(templates[1]['name'], 'Popular Template 2')

    def test_admin_template_management(self):
        """Test admin-specific template management features."""
        # Switch to admin user
        self.client.force_authenticate(user=self.admin_user)
        
        # Admin can create system templates
        url = reverse('data_tools:export_templates_api')
        data = {
            'name': 'Admin System Template',
            'template_type': 'system',
            'configuration': {'format': 'csv'}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        template = ExportTemplate.objects.get(id=response.json()['data']['id'])
        self.assertEqual(template.template_type, 'system')
        
        # Admin can see all templates
        url = reverse('data_tools:export_templates_api')
        response = self.client.get(url, {'include_all': True})
        
        # Should include templates from all users
        templates = response.json()['data']['templates']
        self.assertGreater(len(templates), 0)

    def test_template_usage_tracking(self):
        """Test that template usage is tracked correctly."""
        template = ExportTemplate.objects.create(
            name='Usage Template',
            user=self.user,
            configuration={'format': 'csv'},
            usage_count=0
        )
        
        # Simulate template usage
        url = reverse('data_tools:export_template_use_api', kwargs={'pk': template.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        template.refresh_from_db()
        self.assertEqual(template.usage_count, 1)
        self.assertIsNotNone(template.last_used_at)

    def test_export_import_templates(self):
        """Test template export and import functionality."""
        # Create template for export
        template = ExportTemplate.objects.create(
            name='Export Template',
            description='Template for export test',
            user=self.user,
            configuration={'format': 'json', 'filters': {'limit': 1000}}
        )
        
        # Export template
        export_url = reverse('data_tools:export_template_export_api', kwargs={'pk': template.id})
        response = self.client.get(export_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        exported_data = response.json()
        
        # Import template
        import_url = reverse('data_tools:export_templates_import_api')
        response = self.client.post(import_url, exported_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check imported template exists
        imported_template = ExportTemplate.objects.get(
            name=exported_data['name'] + ' (Imported)'
        )
        self.assertEqual(imported_template.configuration, template.configuration)