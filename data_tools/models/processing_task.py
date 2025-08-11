# data_tools/models/processing_task.py
from django.db import models
from projects.models import DataSource  # Importamos desde la app 'projects'


class ProcessingTask(models.Model):
    """Representa una tarea de procesamiento de datos (fusión, limpieza, etc.)."""
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('IN_PROGRESS', 'En Progreso'),
        ('SUCCESS', 'Completada'),
        ('FAILURE', 'Fallida'),
    ]

    task_type = models.CharField(max_length=50, default="fusion")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    # Relaciones con los datos
    input_datasources = models.ManyToManyField(DataSource, related_name='processing_tasks_as_input')
    output_datasource = models.OneToOneField(
        DataSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generating_task'
    )

    def __str__(self):
        return f"Tarea {self.id} ({self.task_type}) - {self.status}"