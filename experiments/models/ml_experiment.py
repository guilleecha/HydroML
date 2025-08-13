# experiments/models/ml_experiment.py
from django.db import models
from projects.models import Project, DataSource # Importamos desde la app 'projects'

class MLExperiment(models.Model):
    """Representa un experimento de Machine Learning completo."""

    # --- AÑADE ESTAS OPCIONES DE ESTADO ---
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        SPLIT = 'SPLIT', 'Datos Divididos'
        TRAINING = 'TRAINING', 'Entrenando'
        COMPLETED = 'COMPLETED', 'Validación Completa'
        EVALUATING = 'EVALUATING', 'Evaluando Test Final'
        FINISHED = 'FINISHED', 'Finalizado'
        ANALYZING = 'ANALYZING', 'Analizando Modelo'
        ANALYZED = 'ANALYZED', 'Analizado'
        FAILED = 'FAILED', 'Fallido'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ml_experiments')

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

    # --- ACTUALIZA EL CAMPO 'status' ---
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    def __str__(self):
        return self.name