"""
Project model for the HydroML platform.

This module defines the core Project model that represents a data science project
within the HydroML platform. Projects serve as containers for DataSources,
experiments, and analytical workflows.
"""
from django.db import models
from django.conf import settings
import uuid


class Project(models.Model):
    """
    Represents a data science project within the HydroML platform.
    
    Projects serve as the organizational unit for data science workflows,
    containing DataSources, experiments, and analytical results. Each project
    is owned by a user and can optionally be made public for collaboration.
    
    Attributes:
        id (UUIDField): Unique identifier for the project
        name (CharField): Human-readable name for the project
        description (TextField): Optional detailed description of the project
        owner (ForeignKey): User who owns and manages the project
        is_public (BooleanField): Whether the project is visible to other users
        created_at (DateTimeField): Timestamp when the project was created
    
    Relationships:
        - One project belongs to one owner (User)
        - One project can have many DataSources
        - One project can have many ExperimentSuites
        
    Example:
        >>> project = Project.objects.create(
        ...     name="Water Quality Analysis",
        ...     description="Analysis of water quality parameters in Lake Michigan",
        ...     owner=user,
        ...     is_public=True
        ... )
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the project"
    )
    
    name = models.CharField(
        max_length=255, 
        verbose_name="Nombre del Proyecto",
        help_text="Descriptive name for the project"
    )
    
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción",
        help_text="Detailed description of the project goals and methodology"
    )
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="projects",
        help_text="User who owns and manages this project"
    )
    
    is_public = models.BooleanField(
        default=False, 
        verbose_name="Proyecto Público", 
        help_text="Permite que otros usuarios vean este proyecto"
    )
    
    is_favorite = models.BooleanField(
        default=False,
        verbose_name="Proyecto Favorito",
        help_text="Marca este proyecto como favorito para el usuario"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the project was created"
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]

    def __str__(self):
        """
        Return string representation of the project.
        
        Returns:
            str: The project name
        """
        return self.name
    
    def get_absolute_url(self):
        """
        Get the absolute URL for this project.
        
        Returns:
            str: URL path for the project detail view
        """
        from django.urls import reverse
        return reverse('projects:project_detail', kwargs={'pk': self.pk})
    
    def can_be_accessed_by(self, user):
        """
        Check if a user can access this project.
        
        Args:
            user: User instance to check access for
            
        Returns:
            bool: True if user can access the project, False otherwise
        """
        return self.owner == user or self.is_public