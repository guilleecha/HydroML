#!/usr/bin/env python
"""
Test script to verify form and template integration with django-taggit
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from experiments.forms import MLExperimentForm
from experiments.models import MLExperiment
from django.contrib.auth import get_user_model

User = get_user_model()

def test_form_integration():
    """Test that form handles tags correctly"""
    
    print("🔍 Testing form integration with tags...")
    
    # Get test user and project first
    test_user = User.objects.first()
    if not test_user:
        print("❌ No user found for testing")
        return False
    
    project = test_user.projects.first()
    if not project:
        print("❌ No project found for testing")
        return False
    
    # Check if tags field is in the form
    form = MLExperimentForm(project=project)
    fields = list(form.fields.keys())
    
    if 'tags' in fields:
        print("✅ Tags field found in MLExperimentForm")
        print(f"   Form fields: {fields}")
    else:
        print("❌ Tags field NOT found in MLExperimentForm")
        print(f"   Available fields: {fields}")
        return False
    
    # Test form validation with tags
    datasource = project.datasources.first()
    if datasource:
        form_data = {
            'name': 'Form Test Experiment',
            'description': 'Testing form with tags',
            'input_datasource': datasource.id,
            'target_column': 'test_column',
            'model_name': 'RandomForestRegressor',
            'tags': 'form-test, validation, django-taggit'
        }
        
        form = MLExperimentForm(data=form_data, project=project)
        if form.is_valid():
            print("✅ Form validation passed with tags")
            # Don't save, just validate
        else:
            print("❌ Form validation failed:")
            for field, errors in form.errors.items():
                print(f"   {field}: {errors}")
    else:
        print("⚠️  No datasource found for testing")
    
    print("✅ Form integration test completed!")
    return True

if __name__ == "__main__":
    test_form_integration()
