# Test for the Data Fusion API endpoint
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, DataSource
import json
import uuid


class DataFusionAPITestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        
        # Create test datasources (assuming they exist in READY status)
        self.datasource_a = DataSource.objects.create(
            name='DataSource A',
            project=self.project,
            status=DataSource.Status.READY
        )
        self.datasource_b = DataSource.objects.create(
            name='DataSource B', 
            project=self.project,
            status=DataSource.Status.READY
        )
        
        self.client = Client()
        
    def test_get_fusion_columns_api_success(self):
        """Test successful API call with valid datasources"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('data_tools:get_fusion_columns_api')
        response = self.client.get(url, {
            'ds_a': str(self.datasource_a.id),
            'ds_b': str(self.datasource_b.id)
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verify response structure
        self.assertIn('datasource_a', data)
        self.assertIn('datasource_b', data)
        self.assertEqual(data['datasource_a']['id'], str(self.datasource_a.id))
        self.assertEqual(data['datasource_b']['id'], str(self.datasource_b.id))
        
    def test_get_fusion_columns_api_missing_params(self):
        """Test API call with missing parameters"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('data_tools:get_fusion_columns_api')
        response = self.client.get(url, {'ds_a': str(self.datasource_a.id)})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
    def test_get_fusion_columns_api_unauthorized(self):
        """Test API call without authentication"""
        url = reverse('data_tools:get_fusion_columns_api')
        response = self.client.get(url, {
            'ds_a': str(self.datasource_a.id),
            'ds_b': str(self.datasource_b.id)
        })
        
        # Should redirect to login (302) since @login_required
        self.assertEqual(response.status_code, 302)
