"""
Tests for Export API views.
Tests ExportJob and ExportTemplate API endpoints with authentication,
permissions, CRUD operations, and custom actions.
"""

import json
import uuid
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from projects.models.project import Project
from projects.models.datasource import DataSource
from data_tools.models.export_job import ExportJob
from data_tools.models.export_template import ExportTemplate

User = get_user_model()


class ExportAPITestCase(TestCase):
    """Base test case with common setup for export API tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project for export API',
            user=self.user1
        )
        self.project.members.add(self.user1)
        
        # Create test datasource with a dummy CSV file
        csv_content = b"col1,col2,col3\n1,2,3\n4,5,6\n7,8,9"
        csv_file = SimpleUploadedFile(
            "test_data.csv",
            csv_content,
            content_type="text/csv"
        )
        
        self.datasource = DataSource.objects.create(
            name='Test DataSource',
            file=csv_file,
            format='csv',
            user=self.user1,
            status=DataSource.Status.READY
        )
        self.datasource.projects.add(self.project)
        
        # Login user1 by default
        self.client.login(username='testuser1', password='testpass123')


class ExportJobAPITest(ExportAPITestCase):
    """Tests for ExportJob API endpoints."""
    
    def test_create_export_job(self):
        """Test creating a new export job."""
        url = reverse('data_tools:export_jobs_api')
        data = {
            'datasource': str(self.datasource.id),
            'format': 'csv',
            'filters': {
                'columns': ['col1', 'col2'],
                'limit': 100
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        
        # Check created export job
        export_job = ExportJob.objects.get(id=response_data['data']['id'])
        self.assertEqual(export_job.user, self.user1)
        self.assertEqual(export_job.datasource, self.datasource)
        self.assertEqual(export_job.format, 'csv')
        self.assertEqual(export_job.status, 'pending')
    
    def test_create_export_job_validation(self):
        """Test export job creation validation."""
        url = reverse('data_tools:export_jobs_api')
        
        # Test missing required fields
        response = self.client.post(
            url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test invalid format
        data = {
            'datasource': str(self.datasource.id),
            'format': 'invalid_format'
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test invalid datasource
        data = {
            'datasource': str(uuid.uuid4()),
            'format': 'csv'
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_list_export_jobs(self):
        """Test listing export jobs."""
        # Create test export jobs
        ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='json',
            status='pending'
        )
        
        # Create export job for different user (should not appear)
        ExportJob.objects.create(
            user=self.user2,
            datasource=self.datasource,
            format='excel',
            status='failed'
        )
        
        url = reverse('data_tools:export_jobs_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        
        # Should only see current user's jobs
        export_jobs = response_data['data']['export_jobs']
        self.assertEqual(len(export_jobs), 2)
        
        # Check pagination info
        pagination = response_data['data']['pagination']
        self.assertEqual(pagination['total_count'], 2)
    
    def test_get_export_job_detail(self):
        """Test retrieving specific export job."""
        export_job = ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': export_job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['id'], str(export_job.id))
    
    def test_get_export_job_permission(self):
        """Test export job access permissions."""
        # Create export job for user2
        export_job = ExportJob.objects.create(
            user=self.user2,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        # User1 should not be able to access user2's job
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': export_job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_export_job(self):
        """Test deleting export job."""
        export_job = ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='csv',
            status='completed'
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': export_job.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Check that job is deleted
        with self.assertRaises(ExportJob.DoesNotExist):
            ExportJob.objects.get(id=export_job.id)
    
    def test_delete_processing_job_forbidden(self):
        """Test that processing jobs cannot be deleted."""
        export_job = ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='csv',
            status='processing'
        )
        
        url = reverse('data_tools:export_job_detail_api', kwargs={'pk': export_job.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 409)
        
        # Job should still exist
        export_job.refresh_from_db()
        self.assertEqual(export_job.status, 'processing')
    
    def test_cancel_export_job(self):
        """Test cancelling an export job."""
        export_job = ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='csv',
            status='processing'
        )
        
        url = reverse('data_tools:export_job_cancel_api', kwargs={'pk': export_job.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        
        export_job.refresh_from_db()
        self.assertEqual(export_job.status, 'cancelled')
        self.assertIsNotNone(export_job.completed_at)
    
    def test_retry_export_job(self):
        """Test retrying a failed export job."""
        export_job = ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='csv',
            status='failed',
            error_message='Test error'
        )
        
        url = reverse('data_tools:export_job_retry_api', kwargs={'pk': export_job.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        
        export_job.refresh_from_db()
        self.assertEqual(export_job.status, 'pending')
        self.assertEqual(export_job.progress, 0)
        self.assertEqual(export_job.error_message, '')
    
    def test_download_export_file_not_completed(self):
        """Test downloading file from non-completed job."""
        export_job = ExportJob.objects.create(
            user=self.user1,
            datasource=self.datasource,
            format='csv',
            status='pending'
        )
        
        url = reverse('data_tools:export_job_download_api', kwargs={'pk': export_job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 409)


class ExportTemplateAPITest(ExportAPITestCase):
    """Tests for ExportTemplate API endpoints."""
    
    def test_create_export_template(self):
        """Test creating a new export template."""
        url = reverse('data_tools:export_templates_api')
        data = {
            'name': 'Test Template',
            'description': 'Test template description',
            'configuration': {
                'format': 'csv',
                'filters': {
                    'columns': ['col1', 'col2']
                }
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        
        # Check created template
        template = ExportTemplate.objects.get(id=response_data['data']['id'])
        self.assertEqual(template.user, self.user1)
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.template_type, 'user')
    
    def test_create_template_duplicate_name(self):
        """Test creating template with duplicate name."""
        # Create initial template
        ExportTemplate.objects.create(
            name='Test Template',
            user=self.user1,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_templates_api')
        data = {
            'name': 'Test Template',  # Same name
            'configuration': {'format': 'json'}
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_list_export_templates(self):
        """Test listing export templates."""
        # Create user template
        user_template = ExportTemplate.objects.create(
            name='User Template',
            user=self.user1,
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
        
        # Create template for different user
        ExportTemplate.objects.create(
            name='Other User Template',
            user=self.user2,
            template_type='user',
            configuration={'format': 'excel'}
        )
        
        url = reverse('data_tools:export_templates_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Should see user's own templates + system templates
        templates = response_data['data']['templates']
        self.assertEqual(len(templates), 2)
        
        template_names = [t['name'] for t in templates]
        self.assertIn('User Template', template_names)
        self.assertIn('System Template', template_names)
        self.assertNotIn('Other User Template', template_names)
    
    def test_get_template_detail(self):
        """Test retrieving specific export template."""
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user1,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['id'], str(template.id))
    
    def test_update_export_template(self):
        """Test updating an export template."""
        template = ExportTemplate.objects.create(
            name='Original Name',
            user=self.user1,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        data = {
            'name': 'Updated Name',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        template.refresh_from_db()
        self.assertEqual(template.name, 'Updated Name')
        self.assertEqual(template.description, 'Updated description')
    
    def test_update_template_permission(self):
        """Test template update permissions."""
        # Create template owned by user2
        template = ExportTemplate.objects.create(
            name='User2 Template',
            user=self.user2,
            configuration={'format': 'csv'}
        )
        
        # User1 should not be able to update user2's template
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        data = {'name': 'Hacked Name'}
        
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        
        template.refresh_from_db()
        self.assertEqual(template.name, 'User2 Template')  # Unchanged
    
    def test_delete_export_template(self):
        """Test deleting an export template."""
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user1,
            configuration={'format': 'csv'}
        )
        
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': template.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Check that template is deleted
        with self.assertRaises(ExportTemplate.DoesNotExist):
            ExportTemplate.objects.get(id=template.id)
    
    def test_system_template_access(self):
        """Test that all users can access system templates."""
        # Create system template
        system_template = ExportTemplate.objects.create(
            name='System Template',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'csv'}
        )
        
        # User1 should be able to access system template
        url = reverse('data_tools:export_template_detail_api', kwargs={'pk': system_template.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertEqual(response_data['data']['template_type'], 'system')


class ExportAPIAuthenticationTest(TestCase):
    """Tests for export API authentication requirements."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_unauthenticated_access_forbidden(self):
        """Test that unauthenticated users cannot access export APIs."""
        # Test export jobs API
        url = reverse('data_tools:export_jobs_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test export templates API
        url = reverse('data_tools:export_templates_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login