from django.db import models
from projects.models import Project
from .ml_experiment import MLExperiment

class ExperimentSuite(models.Model):
    """
    Representa una colección de experimentos de ML, como un estudio de ablación
    o una búsqueda de combinaciones de hiperparámetros.
    """
    class SuiteType(models.TextChoices):
        COMBINATION_SEARCH = 'COMBINATION_SEARCH', 'Búsqueda de Combinaciones'
        ABLATION_STUDY = 'ABLATION_STUDY', 'Análisis de Ablación'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        RUNNING = 'RUNNING', 'En Ejecución'
        COMPLETED = 'COMPLETED', 'Completada'
        FAILED = 'FAILED', 'Fallida'

    name = models.CharField(max_length=255, help_text="Nombre de la suite de experimentos.")
    description = models.TextField(blank=True, null=True, help_text="Descripción opcional de la suite.")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='experiment_suites')
    
    suite_type = models.CharField(
        max_length=50,
        choices=SuiteType.choices,
        default=SuiteType.ABLATION_STUDY
    )
    
    base_experiment = models.ForeignKey(
        MLExperiment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suites_as_base',
        help_text="Experimento base que sirve como plantilla para la suite."
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_suite_type_display()})"

    class Meta:
        verbose_name = "Suite de Experimentos"
        verbose_name_plural = "Suites de Experimentos"
        ordering = ['-created_at']