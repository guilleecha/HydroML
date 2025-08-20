#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from django.contrib.auth.models import User

# Borrar usuario existente y crear uno nuevo
User.objects.filter(username='testuser').delete()
user = User.objects.create_user('testuser', 'test@test.com', 'testpass')
print(f'Test user created: {user.username}/testpass')
