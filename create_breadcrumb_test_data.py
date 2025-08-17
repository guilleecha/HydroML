#!/usr/bin/env python
"""
Script to create test data for breadcrumb navigation and workspace switcher testing.
Creates multiple projects to test the workspace switching functionality.
"""

import os
import sys
import django
from django.contrib.auth import get_user_model

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from projects.models import Project
from data_tools.models import DataSource
from experiments.models import Experiment

User = get_user_model()

def create_test_data():
    """Create test projects for breadcrumb testing"""
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Create test projects
    projects_data = [
        {
            'name': 'Water Quality Prediction',
            'description': 'ML models for predicting water quality parameters in urban watersheds',
        },
        {
            'name': 'Flood Risk Assessment',
            'description': 'Hydrological modeling for flood risk prediction and mitigation',
        },
        {
            'name': 'Drought Monitoring System',
            'description': 'Real-time drought monitoring using satellite data and ML',
        },
        {
            'name': 'Streamflow Forecasting',
            'description': 'LSTM-based models for streamflow prediction',
        },
        {
            'name': 'Groundwater Level Prediction',
            'description': 'Time series analysis for groundwater level forecasting',
        }
    ]
    
    created_projects = []
    
    for project_data in projects_data:
        project, created = Project.objects.get_or_create(
            name=project_data['name'],
            owner=user,
            defaults={
                'description': project_data['description']
            }
        )
        
        if created:
            print(f"Created project: {project.name}")
            
            # Create some test data sources for each project
            for i in range(2):
                datasource, ds_created = DataSource.objects.get_or_create(
                    name=f"{project.name} Dataset {i+1}",
                    project=project,
                    defaults={
                        'description': f'Test dataset {i+1} for {project.name}',
                        'data_type': 'csv'
                    }
                )
                if ds_created:
                    print(f"  Created datasource: {datasource.name}")
            
            # Create some test experiments for each project
            for i in range(3):
                experiment, exp_created = Experiment.objects.get_or_create(
                    name=f"{project.name} Experiment {i+1}",
                    project=project,
                    defaults={
                        'description': f'Test experiment {i+1} for {project.name}',
                        'status': 'completed' if i < 2 else 'running'
                    }
                )
                if exp_created:
                    print(f"  Created experiment: {experiment.name}")
        else:
            print(f"Project already exists: {project.name}")
        
        created_projects.append(project)
    
    print(f"\nTotal projects created/verified: {len(created_projects)}")
    print(f"User: {user.username} (ID: {user.id})")
    
    # Display project information for testing
    print("\n=== Project Information for Testing ===")
    for project in created_projects:
        print(f"Project: {project.name} (ID: {project.id})")
        print(f"  Description: {project.description}")
        print(f"  DataSources: {project.datasources.count()}")
        print(f"  Experiments: {project.experiments.count()}")
        print(f"  URL: http://localhost:8000/projects/{project.id}/")
        print()

if __name__ == '__main__':
    try:
        create_test_data()
        print("✅ Test data creation completed successfully!")
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()
