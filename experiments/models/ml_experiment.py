# experiments/models/ml_experiment.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from projects.models import Project, DataSource
import uuid

class MLExperiment(models.Model):
    """Representa un experimento de Machine Learning completo."""

    # --- AÑADE ESTAS OPCIONES DE ESTADO ---
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        RUNNING = 'RUNNING', 'En Ejecución'
        FINISHED = 'FINISHED', 'Finalizado'
        ANALYZED = 'ANALYZED', 'Analizado'
        PUBLISHED = 'PUBLISHED', 'Publicado'
        ERROR = 'ERROR', 'Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # El related_name es 'experiments' para mayor consistencia
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='experiments')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # --- CAMPO 'status' CORREGIDO (UNA SOLA DEFINICIÓN) ---
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Configuración del experimento
    input_datasource = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='experiments_as_input')
    target_column = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    feature_set = models.JSONField(default=list)
    hyperparameters = models.JSONField(blank=True, null=True)
    results = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    test_split_size = models.FloatField(default=0.2, help_text="Proporción de datos para el conjunto de prueba.")
    split_random_state = models.IntegerField(default=42, help_text="Semilla para la división aleatoria de datos.")
    
    SPLIT_STRATEGY_CHOICES = [
        ('RANDOM', 'Aleatorio'),
        ('TIMESERIES', 'Serie Temporal'),
    ]
    split_strategy = models.CharField(
        max_length=20,
        choices=SPLIT_STRATEGY_CHOICES,
        default='RANDOM',
        help_text="Estrategia para la división de datos en entrenamiento y prueba."
    )

    # --- NUEVOS CAMPOS PARA VERSIONADO Y PUBLICACIÓN ---
    version = models.PositiveIntegerField(default=1, help_text="Versión del experimento")
    is_public = models.BooleanField(default=False, help_text="Indica si el experimento es visible públicamente")
    published_at = models.DateTimeField(null=True, blank=True, help_text="Fecha de publicación")
    parent_experiment = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='versions',
        help_text="Experimento original del cual este es una nueva versión"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (v{self.version}) - {self.project.name}"

    class Meta:
        ordering = ['-created_at']