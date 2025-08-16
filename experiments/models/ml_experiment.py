# experiments/models/ml_experiment.py
"""
Machine Learning experiment models for the HydroML project.

This module contains the core model definition for ML experiments, which represent
complete machine learning workflows from data preparation to model evaluation.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from projects.models import Project, DataSource
from taggit.managers import TaggableManager
from core.models.tag_models import UUIDTaggedItem
import uuid


class MLExperiment(models.Model):
    """
    Represents a complete Machine Learning experiment within the HydroML system.
    
    An MLExperiment encapsulates all aspects of a machine learning workflow including
    data preparation, model training, hyperparameter configuration, and result storage.
    It provides version control, MLflow integration, and comprehensive tracking of
    experiment lifecycle and artifacts.
    
    The experiment follows a state-based workflow managed through the Status enum,
    ensuring proper execution order and error handling throughout the ML pipeline.
    
    Attributes:
        id (UUIDField): Primary key using UUID4 for global uniqueness.
        project (ForeignKey): Associated project that owns this experiment.
        name (CharField): Human-readable experiment name.
        description (TextField): Optional detailed description of the experiment.
        status (CharField): Current experiment status from Status choices.
        input_datasource (ForeignKey): Source data for training and testing.
        target_column (CharField): Name of the target variable column.
        model_name (CharField): ML algorithm identifier (e.g., 'RandomForestRegressor').
        feature_set (JSONField): List of feature column names to use.
        hyperparameters (JSONField): Model hyperparameter configuration.
        results (JSONField): Stored experiment results and metrics.
        artifact_paths (JSONField): File paths to generated experiment artifacts.
        test_split_size (FloatField): Proportion of data reserved for testing.
        split_random_state (IntegerField): Random seed for reproducible data splits.
        split_strategy (CharField): Strategy for train/test splitting.
        version (PositiveIntegerField): Version number for experiment iterations.
        is_public (BooleanField): Whether experiment is publicly visible.
        published_at (DateTimeField): Timestamp when experiment was published.
        parent_experiment (ForeignKey): Reference to original experiment for versions.
        mlflow_run_id (CharField): Associated MLflow run identifier.
        created_at (DateTimeField): Experiment creation timestamp.
        updated_at (DateTimeField): Last modification timestamp.
    """

    class Status(models.TextChoices):
        """
        Enumeration of possible experiment states throughout its lifecycle.
        
        The status progression typically follows:
        DRAFT -> RUNNING -> FINISHED -> ANALYZED -> PUBLISHED
        
        ERROR can occur at any point during RUNNING state.
        """
        DRAFT = 'DRAFT', 'Borrador'
        RUNNING = 'RUNNING', 'En Ejecución'
        FINISHED = 'FINISHED', 'Finalizado'
        ANALYZED = 'ANALYZED', 'Analizado'
        PUBLISHED = 'PUBLISHED', 'Publicado'
        ERROR = 'ERROR', 'Error'

    # Core identification and metadata fields
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the experiment using UUID4 format."
    )
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='experiments',
        help_text="The project that owns this experiment."
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Human-readable name for the experiment."
    )
    
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Optional detailed description of the experiment's purpose and methodology."
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Current state of the experiment in its lifecycle."
    )
    
    # Data and model configuration fields
    input_datasource = models.ForeignKey(
        DataSource, 
        on_delete=models.CASCADE, 
        related_name='experiments_as_input',
        help_text="The datasource containing the training and testing data."
    )
    
    target_column = models.CharField(
        max_length=100,
        help_text="Name of the column to be predicted (target variable)."
    )
    
    model_name = models.CharField(
        max_length=100,
        help_text="Identifier of the ML algorithm to use (e.g., 'RandomForestRegressor')."
    )
    
    feature_set = models.JSONField(
        default=list,
        help_text="List of column names to use as features for model training."
    )
    
    hyperparameters = models.JSONField(
        blank=True, 
        null=True,
        help_text="Dictionary of hyperparameters specific to the chosen model."
    )
    
    # Results and artifacts storage
    results = models.JSONField(
        blank=True, 
        null=True, 
        default=dict,
        help_text="Stored experiment results including metrics and evaluation data."
    )
    
    artifact_paths = models.JSONField(
        blank=True, 
        null=True, 
        default=dict, 
        help_text="File paths to generated artifacts like trained models and datasets."
    )
    
    # Data splitting configuration
    test_split_size = models.FloatField(
        default=0.2, 
        help_text="Proportion of data reserved for testing (e.g., 0.2 = 20%)."
    )
    
    split_random_state = models.IntegerField(
        default=42, 
        help_text="Random seed for reproducible train/test data splitting."
    )
    
    SPLIT_STRATEGY_CHOICES = [
        ('RANDOM', 'Aleatorio'),
        ('TIMESERIES', 'Serie Temporal'),
    ]
    split_strategy = models.CharField(
        max_length=20,
        choices=SPLIT_STRATEGY_CHOICES,
        default='RANDOM',
        help_text="Strategy used for splitting data into training and testing sets."
    )

    VALIDATION_STRATEGY_CHOICES = [
        ('TRAIN_TEST_SPLIT', 'Simple Train/Test Split'),
        ('TIME_SERIES_CV', 'Time Series Cross-Validation'),
    ]
    validation_strategy = models.CharField(
        max_length=20,
        choices=VALIDATION_STRATEGY_CHOICES,
        default='TRAIN_TEST_SPLIT',
        help_text="Validation strategy used for model evaluation."
    )

    # Version control and publication fields
    version = models.PositiveIntegerField(
        default=1, 
        help_text="Version number for experiment iterations and comparisons."
    )
    
    is_public = models.BooleanField(
        default=False, 
        help_text="Whether this experiment is visible to other users."
    )
    
    published_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Timestamp when the experiment was made public."
    )
    
    parent_experiment = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='versions',
        help_text="Reference to the original experiment if this is a new version."
    )
    
    forked_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forks',
        help_text="Reference to the original experiment if this is a fork."
    )

    # Suite relationship for multi-experiment studies
    suite = models.ForeignKey(
        'ExperimentSuite',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='experiments',
        help_text="The experiment suite this experiment belongs to, if any."
    )

    # External integration fields
    mlflow_run_id = models.CharField(
        max_length=64, 
        null=True, 
        blank=True, 
        help_text="MLflow run identifier for experiment tracking integration."
    )

    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the experiment was created."
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the experiment was last modified."
    )

    # Tagging system
    tags = TaggableManager(
        through=UUIDTaggedItem,
        blank=True,
        help_text="Keywords to categorize and filter experiments."
    )

    def __str__(self):
        """
        Return a string representation of the experiment.
        
        Returns:
            str: Formatted string containing experiment name, version, and project.
        """
        return f"{self.name} (v{self.version}) - {self.project.name}"

    def get_absolute_url(self):
        """
        Get the canonical URL for viewing this experiment.
        
        Returns:
            str: URL path to the experiment detail view.
        """
        from django.urls import reverse
        return reverse('experiments:ml_experiment_detail', kwargs={'pk': self.pk})

    def can_be_executed(self):
        """
        Check if the experiment is in a state that allows execution.
        
        Returns:
            bool: True if experiment can be run, False otherwise.
        """
        return self.status == self.Status.DRAFT

    def can_be_published(self):
        """
        Check if the experiment is eligible for publication.
        
        Returns:
            bool: True if experiment can be published, False otherwise.
        """
        return self.status in [self.Status.FINISHED, self.Status.ANALYZED]

    def is_complete(self):
        """
        Check if the experiment has completed successfully.
        
        Returns:
            bool: True if experiment finished without errors, False otherwise.
        """
        return self.status == self.Status.FINISHED

    def has_results(self):
        """
        Check if the experiment has generated results.
        
        Returns:
            bool: True if results are available, False otherwise.
        """
        return bool(self.results and self.results.get('performance_metrics'))

    def get_primary_metric(self):
        """
        Get the primary evaluation metric for this experiment.
        
        For regression tasks, returns R-squared score.
        For classification tasks, returns accuracy score.
        
        Returns:
            float or None: Primary metric value, or None if not available.
        """
        if not self.has_results():
            return None
            
        metrics = self.results.get('performance_metrics', {})
        
        # Determine task type based on available metrics
        if 'r2' in metrics:
            return metrics['r2']  # Regression
        elif 'accuracy' in metrics:
            return metrics['accuracy']  # Classification
        
        return None

    def get_model_artifacts_path(self):
        """
        Get the file path to the trained model artifact.
        
        Returns:
            str or None: Path to the trained model file, or None if not available.
        """
        if not self.artifact_paths:
            return None
        return self.artifact_paths.get('trained_model')

    class Meta:
        """
        Metadata options for the MLExperiment model.
        """
        ordering = ['-created_at']
        verbose_name = "ML Experiment"
        verbose_name_plural = "ML Experiments"
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['project', 'version']),
            models.Index(fields=['is_public', 'published_at']),
        ]