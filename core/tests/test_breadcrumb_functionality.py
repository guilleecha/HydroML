#!/usr/bin/env python
"""
Test script to verify breadcrumb navigation functionality.
Tests context processors, API endpoints, and template rendering.
"""

import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from projects.models import Project

def test_breadcrumb_functionality():
    """Test breadcrumb navigation components"""
    
    User = get_user_model()
    
    # Get test user
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ Found test user: {user.username}")
    except User.DoesNotExist:
        print("❌ Test user not found")
        return False
    
    # Get user's projects
    projects = Project.objects.filter(owner=user)
    print(f"✅ Found {projects.count()} projects for user")
    
    if projects.count() == 0:
        print("❌ No projects found for testing")
        return False
    
    # Test context processor
    from core.context_processors import global_context
    from django.http import HttpRequest
    from django.contrib.auth.models import AnonymousUser
    
    # Create mock request
    request = HttpRequest()
    request.user = user
    request.resolver_match = type('obj', (object,), {
        'kwargs': {'project_id': str(projects.first().id)}
    })()
    
    context = global_context(request)
    print(f"✅ Context processor returned: {list(context.keys())}")
    print(f"✅ Current project: {context.get('current_project', 'None')}")
    
    # Test API endpoint using Django test client
    client = Client()
    client.force_login(user)
    
    # Test API without current project
    response = client.get('/api/projects/other/')
    print(f"✅ API endpoint (no current): {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Projects returned: {len(data.get('projects', []))}")
    
    # Test API with current project
    current_project_id = str(projects.first().id)
    response = client.get(f'/api/projects/other/?current={current_project_id}')
    print(f"✅ API endpoint (with current): {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Projects returned: {len(data.get('projects', []))}")
        print(f"   Success: {data.get('success', False)}")
    
    # Test project page rendering
    response = client.get(f'/projects/{current_project_id}/')
    print(f"✅ Project page: {response.status_code}")
    if response.status_code == 200:
        content = response.content.decode()
        if 'breadcrumb' in content:
            print("✅ Breadcrumb component found in page")
        else:
            print("⚠️  Breadcrumb component not found in page")
    
    return True

def test_breadcrumb_urls():
    """Test that breadcrumb-related URLs are working"""
    
    print("\n=== Testing URLs ===")
    
    # URLs to test
    test_urls = [
        '/',
        '/projects/',
        '/api/projects/other/',
    ]
    
    # Test with requests (if server is running)
    base_url = 'http://localhost:8000'
    
    for url in test_urls:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            print(f"✅ {url}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {url}: {str(e)}")

if __name__ == '__main__':
    print("🧪 Testing Breadcrumb Navigation Functionality")
    print("=" * 50)
    
    try:
        # Test functionality
        success = test_breadcrumb_functionality()
        
        # Test URLs
        test_breadcrumb_urls()
        
        if success:
            print("\n✅ Breadcrumb functionality tests completed!")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
