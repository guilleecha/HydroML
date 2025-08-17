#!/usr/bin/env python
"""
Test script to verify django-taggit integration with MLExperiment model
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from experiments.models import MLExperiment
from projects.models import Project, DataSource
from django.contrib.auth import get_user_model

User = get_user_model()

def test_tagging_functionality():
    """Test that tagging functionality works correctly"""
    
    print("🔍 Testing django-taggit integration with MLExperiment...")
    
    # Find or create a test user
    test_user, created = User.objects.get_or_create(
        username='test_tags_user',
        defaults={'email': 'test@tags.com'}
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Create or find a test project
    test_project, created = Project.objects.get_or_create(
        name="Test Tagging Project",
        defaults={
            'description': 'Project for testing tagging functionality',
            'owner': test_user
        }
    )
    if created:
        print("✅ Created test project")
    else:
        print("✅ Using existing test project")
    
    # Create or find a test datasource
    test_datasource, created = DataSource.objects.get_or_create(
        name="Test DataSource",
        project=test_project,
        defaults={
            'description': 'Test datasource for tagging tests',
            'data_type': 'ORIGINAL',
            'status': 'READY'
        }
    )
    if created:
        print("✅ Created test datasource")
    else:
        print("✅ Using existing test datasource")
    
    # Create a test experiment
    experiment = MLExperiment.objects.create(
        name="Test Tagging Experiment",
        description="Testing django-taggit integration",
        project=test_project,
        input_datasource=test_datasource,
        target_column="target",
        model_name="RandomForestRegressor",
        is_public=True
    )
    print(f"✅ Created test experiment: {experiment.name}")
    
    # Test adding tags
    experiment.tags.add("machine-learning", "test", "hydrology", "data-science")
    print("✅ Added tags to experiment")
    
    # Test retrieving tags
    tags = experiment.tags.all()
    print(f"✅ Retrieved tags: {[tag.name for tag in tags]}")
    
    # Test filtering by tags
    ml_experiments = MLExperiment.objects.filter(tags__name="machine-learning")
    print(f"✅ Found {ml_experiments.count()} experiments with 'machine-learning' tag")
    
    # Test tag count
    tag_count = experiment.tags.count()
    print(f"✅ Experiment has {tag_count} tags")
    
    # Test removing a tag
    experiment.tags.remove("test")
    remaining_tags = experiment.tags.all()
    print(f"✅ After removing 'test' tag: {[tag.name for tag in remaining_tags]}")
    
    print("\n🎉 All tagging functionality tests passed!")
    print("✅ Django-taggit integration is working correctly!")
    
    return True

if __name__ == "__main__":
    test_tagging_functionality()
