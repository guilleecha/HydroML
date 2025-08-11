import sys

# Comprobamos si el comando que se está ejecutando es de Celery.
# sys.argv es la lista de argumentos pasados por la línea de comandos.
# ej: ['manage.py', 'celery', '-A', 'hydroML', 'worker']
is_celery_command = len(sys.argv) > 1 and 'celery' in sys.argv[1]

# Solo aplicamos el parche de eventlet si estamos ejecutando un worker de Celery.
# Esto evita que interfiera con 'runserver' y otros comandos de Django.
if is_celery_command:
    import eventlet
    eventlet.monkey_patch()

# La configuración para que Celery se descubra se mantiene igual.
from .celery import app as celery_app

__all__ = ('celery_app',)