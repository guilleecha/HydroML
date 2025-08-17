#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from experiments.models import MLExperiment
from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

def test_fork_setup():
    # Check if we have any public experiments to fork
    public_experiments = MLExperiment.objects.filter(is_public=True)
    print(f'Public experiments available: {public_experiments.count()}')

    if public_experiments.exists():
        for exp in public_experiments:
            print(f'- {exp.name} (Owner: {exp.project.owner.username}, Project: {exp.project.name})')

    # Check if we have users and projects for testing
    users = User.objects.all()
    projects = Project.objects.all()
    print(f'Total users: {users.count()}')
    print(f'Total projects: {projects.count()}')

    # Print forked_from field info for verification
    print('\nChecking forked_from field...')
    experiment = MLExperiment.objects.first()
    if experiment:
        print(f'Sample experiment forked_from field exists: {hasattr(experiment, "forked_from")}')
        print(f'Forked_from value: {experiment.forked_from}')
    else:
        print('No experiments found')

if __name__ == '__main__':
    test_fork_setup()
