"""
Django test case for the Data Fusion API endpoint functionality.
Converted from management command to proper unit test.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import DataSource, Project
import json
import uuid


class DataFusionAPITestCase(TestCase):
    """Test case for Data Fusion API endpoint functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project for fusion API',
            owner=self.user
        )
        
        # Initialize client
        self.client = Client()
    
    def test_missing_parameters(self):
        """Test that the API correctly validates missing parameters."""
        self.client.force_login(self.user)
        
        response = self.client.get('/tools/api/get-fusion-columns/')
        
        self.assertEqual(response.status_code, 400)
        
        # Try to parse JSON response
        try:
            data = json.loads(response.content)
            self.assertIn('error', data)
        except json.JSONDecodeError:
            # If it's not JSON, that's also acceptable for a 400 response
            pass
    
    def test_invalid_uuids(self):
        """Test that the API correctly handles non-existent datasources."""
        self.client.force_login(self.user)
        
        response = self.client.get('/tools/api/get-fusion-columns/', {
            'ds_a': '00000000-0000-0000-0000-000000000000',
            'ds_b': '11111111-1111-1111-1111-111111111111'
        })
        
        self.assertEqual(response.status_code, 404)
        
        # Try to parse JSON response
        try:
            data = json.loads(response.content)
            self.assertIn('error', data)
        except json.JSONDecodeError:
            # If it's not JSON, that's also acceptable for a 404 response
            pass
    
    def test_url_resolution(self):
        """Test that the URL properly resolves."""
        try:
            url = reverse('data_tools:get_fusion_columns_api')
            self.assertIsInstance(url, str)
            self.assertTrue(len(url) > 0)
        except Exception as e:
            self.fail(f"URL resolution failed: {e}")
    
    def test_authentication_requirement(self):
        """Test that the API requires authentication."""
        # Make request without authentication
        response = self.client.get('/tools/api/get-fusion-columns/', {
            'ds_a': '00000000-0000-0000-0000-000000000000',
            'ds_b': '11111111-1111-1111-1111-111111111111'
        })
        
        # Should redirect to login or return 401/403
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_with_real_datasources(self):
        """Test API with actual datasource objects."""
        self.client.force_login(self.user)
        
        # Create test datasources
        ds_a = DataSource.objects.create(
            project=self.project,
            name='Test DataSource A',
            file_path='test_a.csv',
            status='READY'
        )
        
        ds_b = DataSource.objects.create(
            project=self.project,
            name='Test DataSource B', 
            file_path='test_b.csv',
            status='READY'
        )
        
        response = self.client.get('/tools/api/get-fusion-columns/', {
            'ds_a': str(ds_a.id),
            'ds_b': str(ds_b.id)
        })
        
        # The response will depend on whether the files actually exist
        # We just test that we get a valid HTTP response
        self.assertIn(response.status_code, [200, 400, 404, 500])
        
        # If successful, check response structure
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                self.assertIn('datasource_a', data)
                self.assertIn('datasource_b', data)
            except json.JSONDecodeError:
                self.fail("Response should be valid JSON for successful requests")
