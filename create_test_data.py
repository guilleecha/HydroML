#!/usr/bin/env python
"""
Create test data for workspace switching demo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()

def create_test_data():
    # Create test user if not exists
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f'✅ Created user: {user.username}')
    else:
        print(f'👤 User exists: {user.username}')

    # Create test projects
    projects_created = 0
    for i in range(3):
        project, created = Project.objects.get_or_create(
            name=f'Test Project {i+1}',
            owner=user,
            defaults={'description': f'Test project {i+1} for workspace switching demo'}
        )
        if created:
            projects_created += 1
            print(f'✅ Created project: {project.name}')
        else:
            print(f'📁 Project exists: {project.name}')

    total_projects = Project.objects.filter(owner=user).count()
    print(f'\n📊 Summary:')
    print(f'   User: {user.username}')
    print(f'   Total projects: {total_projects}')
    print(f'   New projects created: {projects_created}')
    
    if total_projects >= 2:
        print(f'\n🎉 Ready for workspace switching testing!')
        print(f'   1. Login with username: testuser, password: testpass123')
        print(f'   2. Navigate to any project')
        print(f'   3. Click on project name in breadcrumb to test switching')
    else:
        print(f'\n⚠️  Need at least 2 projects for workspace switching demo')

if __name__ == '__main__':
    create_test_data()
