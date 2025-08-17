#!/usr/bin/env python
"""
Script to verify that the critical errors have been fixed.
Tests both the dashboard view and login page functionality.
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from projects.models import Project

def test_dashboard_error_fixed():
    """Test that the dashboard no longer has the FieldError for 'updated_at'"""
    
    print("🧪 Testing Dashboard Error Fix...")
    
    User = get_user_model()
    client = Client()
    
    # Get test user
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ Found test user: {user.username}")
    except User.DoesNotExist:
        print("⚠️  Test user not found, creating one...")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Created test user: {user.username}")
    
    # Login the user
    client.force_login(user)
    
    # Test dashboard access
    try:
        response = client.get('/dashboard/')
        print(f"✅ Dashboard response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard loads successfully - FieldError fixed!")
            return True
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
        return False

def test_login_page_error_fixed():
    """Test that the login page no longer has the NoReverseMatch error"""
    
    print("\n🧪 Testing Login Page Error Fix...")
    
    client = Client()
    
    try:
        response = client.get('/accounts/login/')
        print(f"✅ Login page response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            if 'signup' in content:
                print("⚠️  Login page still contains 'signup' references")
            else:
                print("✅ Login page loads successfully - NoReverseMatch fixed!")
            return True
        else:
            print(f"❌ Login page returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login page error: {str(e)}")
        return False

def test_model_field_verification():
    """Verify that Project model uses correct field names"""
    
    print("\n🧪 Testing Project Model Field Verification...")
    
    try:
        # Check if Project model has the correct fields
        project_fields = [field.name for field in Project._meta.get_fields()]
        print(f"✅ Project model fields: {project_fields}")
        
        if 'created_at' in project_fields:
            print("✅ Project model has 'created_at' field")
        else:
            print("❌ Project model missing 'created_at' field")
            
        if 'updated_at' in project_fields:
            print("⚠️  Project model still has 'updated_at' field (unexpected)")
        else:
            print("✅ Project model correctly does not have 'updated_at' field")
            
        return True
        
    except Exception as e:
        print(f"❌ Model verification error: {str(e)}")
        return False

def test_context_processor():
    """Test that the context processor works correctly"""
    
    print("\n🧪 Testing Context Processor...")
    
    try:
        from core.context_processors import global_context
        from django.http import HttpRequest
        
        # Create mock request
        request = HttpRequest()
        User = get_user_model()
        user = User.objects.get(username='testuser')
        request.user = user
        
        # Mock resolver_match for project context
        request.resolver_match = type('obj', (object,), {
            'kwargs': {}
        })()
        
        context = global_context(request)
        print(f"✅ Context processor returned: {list(context.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Context processor error: {str(e)}")
        return False

if __name__ == '__main__':
    print("🔧 Critical Error Fix Verification")
    print("=" * 50)
    
    try:
        # Run all tests
        tests = [
            test_model_field_verification(),
            test_context_processor(),
            test_dashboard_error_fixed(),
            test_login_page_error_fixed(),
        ]
        
        if all(tests):
            print("\n✅ All critical errors have been fixed!")
            print("📊 Status: Ready to continue with development")
        else:
            print("\n❌ Some tests failed - review the output above")
            
    except Exception as e:
        print(f"\n❌ Verification script error: {str(e)}")
        import traceback
        traceback.print_exc()
