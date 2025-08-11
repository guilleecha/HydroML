import os
from celery import Celery

# Ya no necesitamos las líneas de eventlet aquí

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')

app = Celery('hydroML')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()