#!/usr/bin/env python
"""
Simple test to verify that the ML experiment form partial URL is accessible
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from projects.models import Project

def test_experiment_form_loading():
    """Test that the ML experiment form partial loads correctly"""
    print("🧪 Testing ML Experiment Form Loading...")
    
    # Create a test client with proper host
    client = Client(HTTP_HOST='localhost')
    
    # Get or create a test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    if created:
        user.set_password('testpass')
        user.save()
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")
    
    # Log in the user
    client.force_login(user)
    print("✅ User logged in")
    
    # Test the ML experiment form partial URL without project_id
    print("\n🔧 Testing form URL without project_id...")
    try:
        response = client.get('/experiments/ml-experiment-form-partial/')
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Form loads successfully without project_id")
            content = response.content.decode('utf-8')
            
            # Check for key elements
            if 'id="experiment-form"' in content:
                print("✅ Found experiment form element")
            else:
                print("❌ Missing experiment form element")
                
            if 'data-get-columns-url-template' in content:
                print("✅ Found get-columns URL template")
            else:
                print("❌ Missing get-columns URL template")
                
            if 'id_input_datasource' in content:
                print("✅ Found datasource input field")
            else:
                print("❌ Missing datasource input field")
        else:
            print(f"❌ Form failed to load: {response.status_code}")
            print(f"Response: {response.content.decode('utf-8')[:500]}")
    except Exception as e:
        print(f"❌ Error testing form: {str(e)}")
    
    # Test with a project_id if projects exist
    print("\n🔧 Testing form URL with project_id...")
    try:
        # Fix: Use 'owner' instead of 'user' for Project model
        projects = Project.objects.filter(owner=user)[:1]
        if projects.exists():
            project = projects.first()
            response = client.get(f'/experiments/ml-experiment-form-partial/?project_id={project.id}')
            print(f"📡 Response status with project {project.id}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Form loads successfully with project_id: {project.id}")
            else:
                print(f"❌ Form failed to load with project_id: {response.status_code}")
        else:
            print("⚠️  No projects found for user, skipping project_id test")
    except Exception as e:
        print(f"❌ Error testing with project_id: {str(e)}")
    
    print("\n🎯 Form loading test completed!")

if __name__ == '__main__':
    test_experiment_form_loading()