#!/usr/bin/env python
"""
Integration tests for Django context processors.
Tests enhanced breadcrumb context with special characters for Enhanced Grove Headbar.
"""

import os
import sys
import django
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import Mock

# Setup Django environment for standalone execution
if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
    django.setup()

from projects.models import Project
from core.context_processors import enhanced_breadcrumb_context, navigation_counts


class ContextProcessorTestCase(TestCase):
    """Test case for Enhanced Grove Headbar context processors."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.User = get_user_model()
        
        # Create test user
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test project/workspace
        self.project = Project.objects.create(
            name='Test Workspace',
            description='Test workspace for breadcrumb testing',
            owner=self.user
        )
    
    def _create_mock_request(self, path='/', user=None, namespace=None, url_name=None, kwargs=None):
        """Create a mock request with resolver_match."""
        request = self.factory.get(path)
        request.user = user or self.user
        
        # Mock resolver_match
        resolver_match = Mock()
        resolver_match.namespace = namespace
        resolver_match.url_name = url_name
        resolver_match.kwargs = kwargs or {}
        request.resolver_match = resolver_match
        
        return request
    
    def test_enhanced_breadcrumb_context_unauthenticated(self):
        """Test enhanced breadcrumb context with unauthenticated user."""
        from django.contrib.auth.models import AnonymousUser
        
        request = self._create_mock_request(user=AnonymousUser())
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], None)
        self.assertEqual(context['current_workspace'], None)
        self.assertEqual(context['breadcrumb_user'], None)
        self.assertEqual(context['breadcrumb_parts'], [])
    
    def test_enhanced_breadcrumb_context_dashboard(self):
        """Test enhanced breadcrumb context for dashboard section."""
        request = self._create_mock_request(
            path='/dashboard/',
            namespace='core',
            url_name='dashboard'
        )
        
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], 'dashboard')
        self.assertEqual(context['breadcrumb_user'], 'testuser')
        self.assertEqual(context['breadcrumb_parts'], ['@testuser'])
    
    def test_enhanced_breadcrumb_context_workspace_list(self):
        """Test enhanced breadcrumb context for workspace list."""
        request = self._create_mock_request(
            path='/projects/',
            namespace='projects',
            url_name='project_list'
        )
        
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], 'workspace')
        self.assertEqual(context['breadcrumb_user'], 'testuser')
        self.assertEqual(context['breadcrumb_parts'], ['@testuser', '&workspace'])
    
    def test_enhanced_breadcrumb_context_specific_workspace(self):
        """Test enhanced breadcrumb context for specific workspace."""
        request = self._create_mock_request(
            path=f'/projects/{self.project.pk}/',
            namespace='projects',
            url_name='project_detail',
            kwargs={'pk': str(self.project.pk)}
        )
        
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], 'workspace')
        self.assertEqual(context['breadcrumb_user'], 'testuser')
        self.assertEqual(context['current_workspace'], self.project)
        self.assertEqual(context['breadcrumb_parts'], ['@testuser', '&Test Workspace'])
    
    def test_enhanced_breadcrumb_context_experiments(self):
        """Test enhanced breadcrumb context for experiments section."""
        request = self._create_mock_request(
            path='/experiments/',
            namespace='experiments',
            url_name='experiment_list'
        )
        
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], 'experiments')
        self.assertEqual(context['breadcrumb_user'], 'testuser')
        self.assertEqual(context['breadcrumb_parts'], ['@testuser', '#experiments'])
    
    def test_enhanced_breadcrumb_context_datasources(self):
        """Test enhanced breadcrumb context for data sources section."""
        request = self._create_mock_request(
            path='/connectors/',
            namespace='connectors',
            url_name='connector_list'
        )
        
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], 'datasources')
        self.assertEqual(context['breadcrumb_user'], 'testuser')
        self.assertEqual(context['breadcrumb_parts'], ['@testuser', '§datasources'])
    
    def test_enhanced_breadcrumb_context_data_tools(self):
        """Test enhanced breadcrumb context for data tools section."""
        request = self._create_mock_request(
            path='/data-tools/',
            namespace='data_tools',
            url_name='data_studio'
        )
        
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], 'datasources')
        self.assertEqual(context['breadcrumb_user'], 'testuser')
        self.assertEqual(context['breadcrumb_parts'], ['@testuser', '§datasources'])
    
    def test_enhanced_breadcrumb_context_invalid_workspace(self):
        """Test enhanced breadcrumb context with invalid workspace ID."""
        request = self._create_mock_request(
            path='/projects/invalid-uuid/',
            namespace='projects',
            url_name='project_detail',
            kwargs={'pk': 'invalid-uuid'}
        )
        
        context = enhanced_breadcrumb_context(request)
        
        self.assertEqual(context['current_section'], 'workspace')
        self.assertEqual(context['current_workspace'], None)
        self.assertEqual(context['breadcrumb_parts'], ['@testuser', '&workspace'])
    
    def test_navigation_counts_authenticated(self):
        """Test navigation counts for authenticated user."""
        request = self._create_mock_request()
        context = navigation_counts(request)
        
        # Should include counts for workspaces, datasources, and experiments
        self.assertIn('total_workspaces_count', context)
        self.assertIn('total_datasources_count', context)
        self.assertIn('total_experiments_count', context)
        
        # Check that workspace count is correct
        self.assertEqual(context['total_workspaces_count'], 1)  # We created one project
    
    def test_navigation_counts_unauthenticated(self):
        """Test navigation counts for unauthenticated user."""
        from django.contrib.auth.models import AnonymousUser
        
        request = self._create_mock_request(user=AnonymousUser())
        context = navigation_counts(request)
        
        # Should return zero counts for unauthenticated user
        self.assertEqual(context['total_workspaces_count'], 0)
        self.assertEqual(context['total_datasources_count'], 0)
        self.assertEqual(context['total_experiments_count'], 0)


def run_standalone_tests():
    """Run tests when script is executed directly."""
    print("🧪 Testing Enhanced Grove Headbar Context Processors")
    print("=" * 60)
    
    # Import and run tests
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific test case
    failures = test_runner.run_tests(['__main__.ContextProcessorTestCase'])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All context processor tests passed!")
        return True


if __name__ == '__main__':
    try:
        success = run_standalone_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)