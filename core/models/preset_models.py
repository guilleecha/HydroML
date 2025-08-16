from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json
from ..constants import ML_MODEL_CHOICES

User = get_user_model()


class HyperparameterPreset(models.Model):
    """
    Model for storing user-specific hyperparameter presets that can be reused across experiments.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of the hyperparameter preset"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this preset is for"
    )
    model_type = models.CharField(
        max_length=100,
        choices=ML_MODEL_CHOICES,
        help_text="ML model type this preset is designed for"
    )
    hyperparameters = models.JSONField(
        help_text="JSON object containing hyperparameter names and values"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hyperparameter_presets',
        help_text="User who owns this preset"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('name', 'user', 'model_type')  # Prevent duplicate preset names per user per model
        ordering = ['-updated_at', 'name']
        verbose_name = "Hyperparameter Preset"
        verbose_name_plural = "Hyperparameter Presets"
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def clean(self):
        """
        Validate that hyperparameters is a valid JSON object.
        """
        if self.hyperparameters:
            if not isinstance(self.hyperparameters, dict):
                raise ValidationError({
                    'hyperparameters': 'Hyperparameters must be a JSON object (dictionary).'
                })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def hyperparameters_count(self):
        """
        Return the number of hyperparameters in this preset.
        """
        if isinstance(self.hyperparameters, dict):
            return len(self.hyperparameters)
        return 0
    
    def get_hyperparameter_summary(self):
        """
        Return a short summary of the hyperparameters for display purposes.
        """
        if not isinstance(self.hyperparameters, dict):
            return "No parameters"
        
        if len(self.hyperparameters) == 0:
            return "No parameters"
        
        # Show first few parameter names
        param_names = list(self.hyperparameters.keys())[:3]
        summary = ", ".join(param_names)
        
        if len(self.hyperparameters) > 3:
            summary += f" (+{len(self.hyperparameters) - 3} more)"
        
        return summary
