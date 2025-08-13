import os
from celery import Celery
from dotenv import load_dotenv  # <-- 1. AÑADE ESTA IMPORTACIÓN



load_dotenv()
# Establece el módulo de configuración de Django por defecto para el programa 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')

# Crea la instancia de la aplicación Celery
app = Celery('hydroML')

# Carga la configuración desde el settings.py de Django.
# El namespace 'CELERY' significa que todas las opciones de configuración de Celery
# deben empezar con CELERY_ en settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carga automáticamente los módulos de tareas (tasks.py) de todas las apps registradas.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')