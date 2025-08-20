# data_tools/models/export_template.py
import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class ExportTemplate(models.Model):
    """
    Model for storing export templates that define reusable export configurations.
    
    Templates allow users to save and reuse export settings including:
    - Format preferences
    - Filter configurations
    - Column selections
    - Custom export parameters
    """
    
    TEMPLATE_TYPE_CHOICES = [
        ('user', 'User Template'),
        ('system', 'System Template'),
        ('shared', 'Shared Template'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the export template"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Descriptive name for the export template"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional description of what this template does"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_templates',
        help_text="User who created this template"
    )
    
    template_type = models.CharField(
        max_length=10,
        choices=TEMPLATE_TYPE_CHOICES,
        default='user',
        help_text="Type of template (user, system, or shared)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active and available for use"
    )
    
    configuration = models.JSONField(
        help_text="Template configuration including format, filters, and export settings"
    )
    
    usage_count = models.IntegerField(
        default=0,
        help_text="Number of times this template has been used"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the template was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the template was last updated"
    )
    
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the template was last used for an export"
    )
    
    class Meta:
        verbose_name = "Export Template"
        verbose_name_plural = "Export Templates"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'template_type', '-updated_at']),
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['usage_count', '-last_used_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_template_name_per_user'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def clean(self):
        """Validate the template configuration."""
        super().clean()
        
        if not isinstance(self.configuration, dict):
            raise ValidationError("Configuration must be a valid JSON object")
        
        # Validate required configuration fields
        required_fields = ['format']
        for field in required_fields:
            if field not in self.configuration:
                raise ValidationError(f"Configuration must include '{field}' field")
        
        # Validate format choice
        valid_formats = ['csv', 'json', 'parquet', 'excel']
        if self.configuration.get('format') not in valid_formats:
            raise ValidationError(
                f"Format must be one of: {', '.join(valid_formats)}"
            )
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def format(self):
        """Get the export format from the configuration."""
        return self.configuration.get('format', 'csv')
    
    @property
    def has_filters(self):
        """Check if the template has any filters configured."""
        filters = self.configuration.get('filters', {})
        return bool(filters)
    
    def increment_usage(self):
        """Increment the usage count and update last used timestamp."""
        from django.utils import timezone
        
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])
    
    def duplicate_for_user(self, new_user, new_name=None):
        """
        Create a duplicate of this template for another user.
        
        Args:
            new_user: User who will own the duplicate template
            new_name: Optional new name for the duplicate
            
        Returns:
            ExportTemplate: The duplicated template
        """
        if new_name is None:
            new_name = f"{self.name} (Copy)"
        
        duplicate = ExportTemplate(
            name=new_name,
            description=self.description,
            user=new_user,
            template_type='user',  # Duplicates are always user templates
            configuration=self.configuration.copy(),
        )
        duplicate.save()
        return duplicate
    
    @classmethod
    def get_available_for_user(cls, user, template_type=None):
        """
        Get all templates available to a specific user.
        
        Args:
            user: User to get templates for
            template_type: Optional filter by template type
            
        Returns:
            QuerySet of available ExportTemplate objects
        """
        from django.db.models import Q
        
        # User can see their own templates + system templates + shared templates
        queryset = cls.objects.filter(
            Q(user=user) | Q(template_type='system') | Q(template_type='shared'),
            is_active=True
        )
        
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        return queryset.select_related('user')
    
    @classmethod
    def get_popular_templates(cls, limit=10):
        """
        Get the most popular templates based on usage count.
        
        Args:
            limit: Maximum number of templates to return
            
        Returns:
            QuerySet of popular ExportTemplate objects
        """
        return cls.objects.filter(
            template_type__in=['system', 'shared'],
            is_active=True,
            usage_count__gt=0
        ).order_by('-usage_count', '-last_used_at')[:limit]
    
    @classmethod
    def create_default_templates(cls):
        """
        Create default system templates for common export scenarios.
        This method should be called during system initialization.
        
        Returns:
            list: List of created template objects
        """
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Try to get a system user, or use the first superuser
        try:
            system_user = User.objects.filter(is_superuser=True).first()
            if not system_user:
                # Create a system user if none exists
                system_user = User.objects.create_user(
                    username='system',
                    email='system@hydroml.local',
                    is_active=False
                )
        except Exception:
            return []  # Skip template creation if user setup fails
        
        default_templates = [
            {
                'name': 'CSV - Full Export',
                'description': 'Export all data to CSV format with headers',
                'configuration': {
                    'format': 'csv',
                    'include_headers': True,
                    'filters': {},
                    'options': {
                        'delimiter': ',',
                        'encoding': 'utf-8'
                    }
                }
            },
            {
                'name': 'JSON - Full Export',
                'description': 'Export all data to JSON format',
                'configuration': {
                    'format': 'json',
                    'filters': {},
                    'options': {
                        'indent': 2,
                        'ensure_ascii': False
                    }
                }
            },
            {
                'name': 'Parquet - Optimized Export',
                'description': 'Export data to Parquet format for analytics',
                'configuration': {
                    'format': 'parquet',
                    'filters': {},
                    'options': {
                        'compression': 'snappy'
                    }
                }
            },
            {
                'name': 'Excel - Report Export',
                'description': 'Export data to Excel format with formatting',
                'configuration': {
                    'format': 'excel',
                    'include_headers': True,
                    'filters': {},
                    'options': {
                        'sheet_name': 'Data Export',
                        'index': False
                    }
                }
            }
        ]
        
        created_templates = []
        for template_config in default_templates:
            template, created = cls.objects.get_or_create(
                name=template_config['name'],
                user=system_user,
                template_type='system',
                defaults={
                    'description': template_config['description'],
                    'configuration': template_config['configuration']
                }
            )
            if created:
                created_templates.append(template)
        
        return created_templates