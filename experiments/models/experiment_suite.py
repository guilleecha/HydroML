# experiments/models/experiment_suite.py
"""
Experiment Suite models for the HydroML project.

This module contains the model definition for ExperimentSuite, which represents
collections of related ML experiments used for hyperparameter sweeps, ablation
studies, and other multi-experiment studies.
"""

from django.db import models
from django.utils import timezone
from projects.models import Project
from .ml_experiment import MLExperiment
import uuid


class ExperimentSuite(models.Model):
    """
    Represents a collection of related ML experiments for multi-experiment studies.
    
    An ExperimentSuite manages groups of experiments that explore different aspects
    of a machine learning problem, such as hyperparameter optimization, ablation
    studies, or comparative analysis across different algorithms.
    
    The suite coordinates the execution of multiple experiments based on a defined
    search space and tracks the overall progress and optimization metrics.
    
    Attributes:
        id (UUIDField): Primary key using UUID4 for global uniqueness.
        name (CharField): Human-readable suite name.
        description (TextField): Optional detailed description of the study.
        project (ForeignKey): Associated project that owns this suite.
        study_type (CharField): Type of study being conducted.
        base_experiment (ForeignKey): Template experiment for the suite.
        search_space (JSONField): Parameters and ranges to explore.
        optimization_metric (CharField): Target metric for optimization.
        status (CharField): Current suite execution status.
        created_at (DateTimeField): Suite creation timestamp.
        updated_at (DateTimeField): Last modification timestamp.
        started_at (DateTimeField): When the suite execution began.
        completed_at (DateTimeField): When the suite execution finished.
    """

    class StudyType(models.TextChoices):
        """
        Enumeration of different types of multi-experiment studies.
        
        Each study type defines a specific methodology for exploring
        the machine learning problem space.
        """
        HYPERPARAMETER_SWEEP = 'HYPERPARAMETER_SWEEP', 'Barrido de Hiperparámetros'
        ABLATION_STUDY = 'ABLATION_STUDY', 'Estudio de Ablación'
        ALGORITHM_COMPARISON = 'ALGORITHM_COMPARISON', 'Comparación de Algoritmos'
        FEATURE_SELECTION = 'FEATURE_SELECTION', 'Selección de Características'
        CROSS_VALIDATION = 'CROSS_VALIDATION', 'Validación Cruzada'

    class Status(models.TextChoices):
        """
        Enumeration of possible suite execution states.
        
        The status progression typically follows:
        DRAFT -> QUEUED -> RUNNING -> COMPLETED
        
        FAILED can occur during RUNNING state.
        CANCELLED can occur during QUEUED or RUNNING states.
        """
        DRAFT = 'DRAFT', 'Borrador'
        QUEUED = 'QUEUED', 'En Cola'
        RUNNING = 'RUNNING', 'En Ejecución'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Falló'
        CANCELLED = 'CANCELLED', 'Cancelado'

    # Core identification and metadata fields
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the experiment suite using UUID4 format."
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Human-readable name for the experiment suite."
    )
    
    description = models.TextField(
        default="",
        help_text="Detailed description of the experiment suite"
    )
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='experiment_suites',
        help_text="The project that owns this experiment suite."
    )
    
    study_type = models.CharField(
        max_length=30,
        choices=StudyType.choices,
        default=StudyType.HYPERPARAMETER_SWEEP,
        help_text="The type of multi-experiment study being conducted."
    )
    
    base_experiment = models.ForeignKey(
        MLExperiment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='derived_suites',
        help_text="The template experiment that serves as the baseline for the suite."
    )
    
    search_space = models.JSONField(
        default=dict,
        help_text="JSON definition of parameters, algorithms, or features to explore in the study."
    )
    
    optimization_metric = models.CharField(
        max_length=50,
        default='r2_score',
        help_text="The target metric to optimize (e.g., 'r2_score', 'accuracy', 'f1_score')."
    )
    
    # Optuna optimization data fields
    trial_data = models.JSONField(
        default=list,
        help_text="List of all trials (parameters and results) from Optuna optimization."
    )
    
    param_importances = models.JSONField(
        default=dict,
        help_text="Calculated hyperparameter importance data from Optuna study."
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Current execution status of the experiment suite."
    )
    
    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the suite was created."
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the suite was last modified."
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the suite execution began."
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the suite execution finished."
    )

    class Meta:
        """
        Meta configuration for the ExperimentSuite model.
        """
        verbose_name = "Experiment Suite"
        verbose_name_plural = "Experiment Suites"
        ordering = ['-created_at']
        
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['study_type', 'status']),
            models.Index(fields=['created_at']),
        ]
        
        # Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(optimization_metric__isnull=False) & 
                      ~models.Q(optimization_metric=''),
                name='experiments_experimentsuite_optimization_metric_required'
            ),
        ]

    def __str__(self):
        """
        String representation of the ExperimentSuite.
        
        Returns:
            str: Human-readable string representation.
        """
        return f"{self.name} ({self.get_study_type_display()})"

    def get_experiment_count(self):
        """
        Get the total number of experiments in this suite.
        
        Returns:
            int: Number of associated experiments.
        """
        return self.experiments.count()

    def get_completed_experiment_count(self):
        """
        Get the number of completed experiments in this suite.
        
        Returns:
            int: Number of experiments with FINISHED status.
        """
        return self.experiments.filter(status='FINISHED').count()

    def get_progress_percentage(self):
        """
        Calculate the completion percentage of the suite.
        
        Returns:
            float: Percentage of completed experiments (0-100).
        """
        total = self.get_experiment_count()
        if total == 0:
            return 0.0
        completed = self.get_completed_experiment_count()
        return (completed / total) * 100

    def get_best_experiment(self):
        """
        Get the experiment with the best performance according to optimization_metric.
        
        Returns:
            MLExperiment or None: The best performing experiment, or None if no experiments.
        """
        experiments = self.experiments.filter(
            status='FINISHED',
            results__isnull=False
        )
        
        if not experiments.exists():
            return None
            
        # Determine if higher or lower values are better for this metric
        # Most metrics are "higher is better", but some like MSE are "lower is better"
        lower_is_better_metrics = ['mse', 'mae', 'rmse', 'mean_squared_error', 'mean_absolute_error']
        is_lower_better = any(metric in self.optimization_metric.lower() for metric in lower_is_better_metrics)
        
        # Sort experiments by the optimization metric
        if is_lower_better:
            # For "lower is better" metrics, sort ascending
            return min(experiments, key=lambda exp: exp.results.get(self.optimization_metric, float('inf')))
        else:
            # For "higher is better" metrics, sort descending
            return max(experiments, key=lambda exp: exp.results.get(self.optimization_metric, float('-inf')))

    def start_execution(self):
        """
        Mark the suite as started and update the status.
        """
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def complete_execution(self):
        """
        Mark the suite as completed and update the status.
        """
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def fail_execution(self):
        """
        Mark the suite as failed.
        """
        self.status = self.Status.FAILED
        self.save(update_fields=['status', 'updated_at'])

    def cancel_execution(self):
        """
        Mark the suite as cancelled.
        """
        self.status = self.Status.CANCELLED
        self.save(update_fields=['status', 'updated_at'])