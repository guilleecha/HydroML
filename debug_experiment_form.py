#!/usr/bin/env python
"""
Debug script to test the experiment form column loading issue.
This script will simulate the frontend request to the get_columns_api endpoint.
"""

import requests
from django.core.management.base import BaseCommand
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from accounts.models import User
from projects.models import Project
from projects.models.datasource import DataSource
import pandas as pd
import tempfile
import uuid

def create_test_data():
    """Create test data for debugging"""
    print("🔍 Creating test data...")
    
    # Get or create a user
    user, created = User.objects.get_or_create(
        username='testuser', 
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created user: {user.username}")
    else:
        print(f"✓ User already exists: {user.username}")

    # Get or create a project
    project, created = Project.objects.get_or_create(
        name='Test Project ML', 
        defaults={
            'description': 'Test project for ML experiments', 
            'owner': user
        }
    )
    if created:
        print(f"✓ Created project: {project.name}")
    else:
        print(f"✓ Project already exists: {project.name}")

    # Check for existing datasources
    existing_ds = DataSource.objects.filter(project=project).first()
    if existing_ds:
        print(f"✓ Found existing datasource: {existing_ds.name} (ID: {existing_ds.id})")
        return user, project, existing_ds

    # Create a sample CSV file
    sample_data = pd.DataFrame({
        'feature_1': [1, 2, 3, 4, 5],
        'feature_2': [10, 20, 30, 40, 50],
        'target_variable': [100, 200, 300, 400, 500],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    
    # Save to a temporary parquet file
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
        sample_data.to_parquet(tmp_file.name)
        
        # Create datasource
        datasource = DataSource.objects.create(
            id=uuid.uuid4(),
            name='Test Dataset',
            project=project,
            status=DataSource.Status.READY,
        )
        
        # Save the file to the datasource
        datasource.file.save(
            'test_dataset.parquet',
            open(tmp_file.name, 'rb'),
            save=True
        )
        
        print(f"✓ Created datasource: {datasource.name} (ID: {datasource.id})")
        print(f"✓ File path: {datasource.file.path}")
        
        return user, project, datasource

def test_api_endpoint(datasource_id):
    """Test the get_columns_api endpoint directly"""
    print(f"\n🔍 Testing API endpoint with datasource_id: {datasource_id}")
    
    from data_tools.views.api_views import get_columns_api
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    # Create a mock request
    factory = RequestFactory()
    user, project, datasource = create_test_data()
    
    request = factory.get(f'/api/get-columns/{datasource_id}/')
    request.user = user
    
    print(f"✓ Mock request created for user: {request.user}")
    print(f"✓ Testing with datasource_id: {datasource_id}")
    
    try:
        response = get_columns_api(request, datasource_id)
        print(f"✓ API Response status: {response.status_code}")
        
        if hasattr(response, 'content'):
            import json
            content = json.loads(response.content.decode('utf-8'))
            print(f"✓ API Response content: {content}")
            
            if 'columns' in content:
                print(f"✓ Columns found: {content['columns']}")
            elif 'error' in content:
                print(f"❌ API Error: {content['error']}")
        
        return response
        
    except Exception as e:
        print(f"❌ Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return None

def test_file_reading(datasource_id):
    """Test direct file reading"""
    print(f"\n🔍 Testing direct file reading for datasource_id: {datasource_id}")
    
    try:
        datasource = DataSource.objects.get(id=datasource_id)
        print(f"✓ Found datasource: {datasource.name}")
        print(f"✓ File path: {datasource.file.path}")
        print(f"✓ File exists: {os.path.exists(datasource.file.path)}")
        
        if os.path.exists(datasource.file.path):
            df = pd.read_parquet(datasource.file.path)
            print(f"✓ File read successfully. Shape: {df.shape}")
            print(f"✓ Columns: {df.columns.tolist()}")
            return df.columns.tolist()
        else:
            print(f"❌ File does not exist: {datasource.file.path}")
            return None
            
    except DataSource.DoesNotExist:
        print(f"❌ DataSource with id {datasource_id} does not exist")
        return None
    except Exception as e:
        print(f"❌ Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return None

if __name__ == '__main__':
    print("🚀 Starting debug session for experiment form...")
    
    # Create test data and get datasource ID
    user, project, datasource = create_test_data()
    datasource_id = str(datasource.id)
    
    print(f"\n📋 Test Summary:")
    print(f"   User: {user.username}")
    print(f"   Project: {project.name} (ID: {project.id})")
    print(f"   DataSource: {datasource.name} (ID: {datasource.id})")
    
    # Test 1: Direct file reading
    columns = test_file_reading(datasource_id)
    
    # Test 2: API endpoint
    response = test_api_endpoint(datasource_id)
    
    print(f"\n🏁 Debug session completed!")
    print(f"   Next step: Open browser to http://localhost:8000/projects/{project.id}/")
    print(f"   Then click 'Nuevo Experimento ML' and select the datasource")
    print(f"   Check browser console for debugging messages")
