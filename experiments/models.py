# experiments/models.py

import uuid
from django.db import models
from projects.models import Project, DataSource



class Experiment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        COMPLETE = 'COMPLETE', 'Completado'
        FAILED = 'FAILED', 'Fallido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # --- CAMBIO AQUÍ ---
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name="experiments")
    name = models.CharField(max_length=255, verbose_name="Nombre del Experimento")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    merge_key = models.CharField(max_length=255, blank=True, null=True,
                                 help_text="Columna común para la fusión de datos.")
    error_message = models.TextField(blank=True, null=True, verbose_name="Mensaje de Error")
    datasources = models.ManyToManyField('projects.DataSource', related_name='experiments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.project.name})"


def fused_data_upload_path(instance, filename):
    return f'experiments/{instance.experiment.id}/fused/{filename}'


class FusedData(models.Model):
    experiment = models.OneToOneField(Experiment, on_delete=models.CASCADE, primary_key=True, related_name="fused_data")
    fused_file = models.FileField(upload_to=fused_data_upload_path)
    summary = models.JSONField(blank=True, null=True, help_text="Estadísticas resumidas del dataset fusionado.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Datos Fusionados para el Experimento: {self.experiment.name}"


class MLExperiment(models.Model):
    class ModelChoices(models.TextChoices):
        RANDOM_FOREST = 'Random Forest', 'Random Forest'
        GRADIENT_BOOSTING = 'Gradient Boosting', 'Gradient Boosting'

    class ValidationChoices(models.TextChoices):
        TIME_SERIES_CV = 'time_series_cv', 'Validación Cruzada de Series Temporales'
        K_FOLD = 'k_fold', 'Validación Cruzada K-Fold'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Ahora Python sabe qué es 'Project' y 'DataSource'
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="ml_experiments")
    name = models.CharField(max_length=255, verbose_name="Nombre del Experimento de ML")
    description = models.TextField(blank=True, null=True)
    source_dataset = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, related_name="ml_experiments")

    # Parámetros del modelo (extraídos de tu config.py)
    target_column = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100, choices=ModelChoices.choices, default=ModelChoices.RANDOM_FOREST)
    feature_set = models.JSONField(default=list, help_text="Lista de columnas usadas como features")
    hyperparameters = models.JSONField(default=dict, help_text="Hiperparámetros del modelo en formato JSON")

    # Estrategia de validación
    validation_strategy = models.CharField(max_length=50, choices=ValidationChoices.choices,
                                           default=ValidationChoices.TIME_SERIES_CV)

    # El archivo de configuración generado que mencionaste
    config_file = models.FileField(upload_to='ml_experiments/configs/', blank=True, null=True)

    # Estado y resultados
    status = models.CharField(max_length=20, choices=Experiment.StatusChoices.choices,
                              default=Experiment.StatusChoices.PENDING)
    error_message = models.TextField(blank=True, null=True)
    results = models.JSONField(blank=True, null=True, help_text="Resultados y métricas del experimento")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name