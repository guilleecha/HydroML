# En core/models.py
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Proyecto")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-created_at']


class Dataset(models.Model):
    # Clave Foránea: Cada Dataset pertenece a UN Proyecto.
    # on_delete=models.CASCADE significa que si se borra un Proyecto, se borran todos sus datasets.
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="datasets")

    name = models.CharField(max_length=200, verbose_name="Nombre del Dataset")
    uploaded_file = models.FileField(upload_to='datasets/%Y/%m/%d/', verbose_name="Archivo Subido")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")

    def __str__(self):
        return f"{self.name} (Proyecto: {self.project.name})"

    class Meta:
        verbose_name = "Dataset"
        verbose_name_plural = "Datasets"
        ordering = ['-created_at']