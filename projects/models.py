# projects/models.py

import uuid
import os
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Nombre del Proyecto")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class DataSourceType(models.TextChoices):
    ORIGINAL = 'ORIGINAL', 'Original'
    PREPARED = 'PREPARED', 'Preparado'
    FUSED = 'FUSED', 'Fusionado'


class DataSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="datasources")
    name = models.CharField(max_length=255, verbose_name="Nombre de la Fuente de Datos")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    file = models.FileField(upload_to='datasources/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Ahora Python ya conoce DataSourceType cuando lee esta línea
    data_type = models.CharField(max_length=10, choices=DataSourceType.choices, default=DataSourceType.ORIGINAL)
    parents = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='children')

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.name or f"Fuente de datos {self.id}"