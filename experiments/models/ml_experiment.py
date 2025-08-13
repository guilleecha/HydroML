# experiments/models/ml_experiment.py
from django.db import models
from projects.models import Project, DataSource # Importamos desde la app 'projects'

class MLExperiment(models.Model):
    """Representa un experimento de Machine Learning completo."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ml_experiments')

    # Configuración del experimento
    input_datasource = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='ml_experiments')
    target_column = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    feature_set = models.JSONField(default=list)
    hyperparameters = models.JSONField(default=dict, blank=True, null=True)
    # Estado y resultados
    status = models.CharField(max_length=20, default='DRAFT')
    results = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Experimento: {self.name} en {self.project.name}"