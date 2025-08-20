"""
Serializers for Export models.
Provides data validation and transformation for ExportJob and ExportTemplate APIs.
"""

from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from projects.models.datasource import DataSource
from data_tools.models.export_job import ExportJob
from data_tools.models.export_template import ExportTemplate

User = get_user_model()


class ExportJobSerializer:
    """
    Serializer for ExportJob model.
    Handles validation and data transformation for export job operations.
    """
    
    # Read-only fields that should not be modified by user input
    READ_ONLY_FIELDS = [
        'id', 'status', 'progress', 'file_path', 'file_size', 
        'row_count', 'created_at', 'started_at', 'completed_at', 
        'expires_at', 'error_message', 'user'
    ]
    
    # Required fields for creating a new export job
    REQUIRED_FIELDS = ['datasource', 'format']
    
    # Valid export formats
    VALID_FORMATS = ['csv', 'json', 'parquet', 'excel']
    
    @classmethod
    def to_dict(cls, export_job):
        """
        Convert ExportJob instance to dictionary for JSON response.
        
        Args:
            export_job (ExportJob): ExportJob instance to serialize
            
        Returns:
            dict: Serialized export job data
        """
        return {
            'id': str(export_job.id),
            'user': export_job.user.username,
            'datasource': {
                'id': str(export_job.datasource.id),
                'name': export_job.datasource.name
            },
            'status': export_job.status,
            'format': export_job.format,
            'filters': export_job.filters,
            'progress': export_job.progress,
            'file_path': export_job.file_path,
            'file_size': export_job.file_size,
            'row_count': export_job.row_count,
            'error_message': export_job.error_message,
            'created_at': export_job.created_at.isoformat() if export_job.created_at else None,
            'started_at': export_job.started_at.isoformat() if export_job.started_at else None,
            'completed_at': export_job.completed_at.isoformat() if export_job.completed_at else None,
            'expires_at': export_job.expires_at.isoformat() if export_job.expires_at else None,
            'is_completed': export_job.is_completed,
            'is_expired': export_job.is_expired,
            'duration_seconds': export_job.duration_seconds
        }
    
    @classmethod
    def validate_create_data(cls, data, user):
        """
        Validate data for creating a new export job.
        
        Args:
            data (dict): Input data to validate
            user: User creating the export job
            
        Returns:
            dict: Validated and cleaned data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                errors[field] = f'{field} is required'
        
        if errors:
            raise ValidationError(errors)
        
        validated_data = {}
        
        # Validate datasource
        try:
            if isinstance(data['datasource'], str):
                datasource = DataSource.objects.get(id=data['datasource'])
            elif isinstance(data['datasource'], DataSource):
                datasource = data['datasource']
            else:
                raise ValidationError({'datasource': 'Invalid datasource format'})
            
            # Check if user has access to the datasource
            if not datasource.projects.filter(members=user).exists():
                raise ValidationError({'datasource': 'You do not have access to this datasource'})
            
            validated_data['datasource'] = datasource
            
        except DataSource.DoesNotExist:
            raise ValidationError({'datasource': 'DataSource not found'})
        
        # Validate format
        format_value = data['format'].lower() if isinstance(data['format'], str) else ''
        if format_value not in cls.VALID_FORMATS:
            raise ValidationError({
                'format': f'Invalid format. Must be one of: {", ".join(cls.VALID_FORMATS)}'
            })
        validated_data['format'] = format_value
        
        # Validate filters (optional)
        filters = data.get('filters', {})
        if filters and not isinstance(filters, dict):
            raise ValidationError({'filters': 'Filters must be a valid JSON object'})
        validated_data['filters'] = filters or {}
        
        # Add user
        validated_data['user'] = user
        
        return validated_data
    
    @classmethod
    def validate_filters(cls, filters):
        """
        Validate export filters structure.
        
        Args:
            filters (dict): Filter dictionary to validate
            
        Returns:
            dict: Validated filters
            
        Raises:
            ValidationError: If filters are invalid
        """
        if not isinstance(filters, dict):
            raise ValidationError('Filters must be a JSON object')
        
        valid_filter_keys = [
            'columns', 'where_conditions', 'limit', 'order_by', 
            'group_by', 'date_range'
        ]
        
        validated_filters = {}
        
        for key, value in filters.items():
            if key not in valid_filter_keys:
                continue  # Skip unknown keys but don't error
            
            if key == 'columns' and value:
                if not isinstance(value, list):
                    raise ValidationError('columns filter must be a list')
                validated_filters[key] = value
            
            elif key == 'where_conditions' and value:
                if not isinstance(value, list):
                    raise ValidationError('where_conditions filter must be a list')
                validated_filters[key] = value
            
            elif key == 'limit' and value:
                try:
                    limit = int(value)
                    if limit <= 0:
                        raise ValidationError('limit must be a positive integer')
                    validated_filters[key] = limit
                except (ValueError, TypeError):
                    raise ValidationError('limit must be a valid integer')
            
            elif key in ['order_by', 'group_by'] and value:
                if not isinstance(value, str):
                    raise ValidationError(f'{key} must be a string')
                validated_filters[key] = value
            
            elif key == 'date_range' and value:
                if not isinstance(value, dict) or 'start' not in value or 'end' not in value:
                    raise ValidationError('date_range must have start and end fields')
                validated_filters[key] = value
        
        return validated_filters


class ExportTemplateSerializer:
    """
    Serializer for ExportTemplate model.
    Handles validation and data transformation for export template operations.
    """
    
    # Read-only fields
    READ_ONLY_FIELDS = [
        'id', 'user', 'usage_count', 'created_at', 
        'updated_at', 'last_used_at'
    ]
    
    # Required fields
    REQUIRED_FIELDS = ['name', 'configuration']
    
    @classmethod
    def to_dict(cls, export_template):
        """
        Convert ExportTemplate instance to dictionary for JSON response.
        
        Args:
            export_template (ExportTemplate): ExportTemplate instance to serialize
            
        Returns:
            dict: Serialized export template data
        """
        return {
            'id': str(export_template.id),
            'name': export_template.name,
            'description': export_template.description,
            'user': export_template.user.username,
            'template_type': export_template.template_type,
            'is_active': export_template.is_active,
            'configuration': export_template.configuration,
            'usage_count': export_template.usage_count,
            'format': export_template.format,  # Property from configuration
            'has_filters': export_template.has_filters,  # Property
            'created_at': export_template.created_at.isoformat() if export_template.created_at else None,
            'updated_at': export_template.updated_at.isoformat() if export_template.updated_at else None,
            'last_used_at': export_template.last_used_at.isoformat() if export_template.last_used_at else None
        }
    
    @classmethod
    def validate_create_data(cls, data, user):
        """
        Validate data for creating a new export template.
        
        Args:
            data (dict): Input data to validate
            user: User creating the template
            
        Returns:
            dict: Validated and cleaned data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                errors[field] = f'{field} is required'
        
        if errors:
            raise ValidationError(errors)
        
        validated_data = {}
        
        # Validate name
        name = data['name'].strip() if isinstance(data['name'], str) else ''
        if len(name) < 1:
            raise ValidationError({'name': 'Template name cannot be empty'})
        if len(name) > 255:
            raise ValidationError({'name': 'Template name is too long (max 255 characters)'})
        
        # Check for duplicate template names for the same user
        if ExportTemplate.objects.filter(user=user, name=name).exists():
            raise ValidationError({'name': 'You already have a template with this name'})
        
        validated_data['name'] = name
        
        # Validate description (optional)
        description = data.get('description', '').strip()
        validated_data['description'] = description
        
        # Validate configuration
        configuration = data.get('configuration', {})
        if not isinstance(configuration, dict):
            raise ValidationError({'configuration': 'Configuration must be a JSON object'})
        
        # Validate required configuration fields
        if 'format' not in configuration:
            raise ValidationError({'configuration': 'Configuration must include format field'})
        
        format_value = configuration['format'].lower() if isinstance(configuration['format'], str) else ''
        if format_value not in ExportJobSerializer.VALID_FORMATS:
            raise ValidationError({
                'configuration': f'Invalid format in configuration. Must be one of: {", ".join(ExportJobSerializer.VALID_FORMATS)}'
            })
        configuration['format'] = format_value
        
        # Validate filters in configuration if present
        if 'filters' in configuration:
            try:
                configuration['filters'] = ExportJobSerializer.validate_filters(
                    configuration['filters']
                )
            except ValidationError as e:
                raise ValidationError({'configuration': f'Invalid filters: {str(e)}'})
        
        validated_data['configuration'] = configuration
        
        # Validate template_type (optional, defaults to 'user')
        template_type = data.get('template_type', 'user')
        if template_type not in ['user', 'system', 'shared']:
            raise ValidationError({'template_type': 'Invalid template type'})
        
        # Only superusers can create system templates
        if template_type == 'system' and not user.is_superuser:
            raise ValidationError({'template_type': 'Only administrators can create system templates'})
        
        validated_data['template_type'] = template_type
        
        # Validate is_active (optional, defaults to True)
        is_active = data.get('is_active', True)
        if not isinstance(is_active, bool):
            raise ValidationError({'is_active': 'is_active must be a boolean'})
        validated_data['is_active'] = is_active
        
        # Add user
        validated_data['user'] = user
        
        return validated_data
    
    @classmethod
    def validate_update_data(cls, data, instance, user):
        """
        Validate data for updating an export template.
        
        Args:
            data (dict): Input data to validate
            instance (ExportTemplate): Existing template instance
            user: User updating the template
            
        Returns:
            dict: Validated and cleaned data
            
        Raises:
            ValidationError: If validation fails
        """
        validated_data = {}
        
        # Check permission to update
        if instance.user != user and not user.is_superuser:
            raise ValidationError('You do not have permission to update this template')
        
        # Validate name if provided
        if 'name' in data:
            name = data['name'].strip() if isinstance(data['name'], str) else ''
            if len(name) < 1:
                raise ValidationError({'name': 'Template name cannot be empty'})
            if len(name) > 255:
                raise ValidationError({'name': 'Template name is too long (max 255 characters)'})
            
            # Check for duplicate names (excluding current instance)
            if (instance.name != name and 
                ExportTemplate.objects.filter(user=instance.user, name=name).exists()):
                raise ValidationError({'name': 'You already have a template with this name'})
            
            validated_data['name'] = name
        
        # Validate description if provided
        if 'description' in data:
            description = data.get('description', '').strip()
            validated_data['description'] = description
        
        # Validate configuration if provided
        if 'configuration' in data:
            configuration = data.get('configuration', {})
            if not isinstance(configuration, dict):
                raise ValidationError({'configuration': 'Configuration must be a JSON object'})
            
            # Merge with existing configuration to preserve other fields
            updated_config = instance.configuration.copy()
            updated_config.update(configuration)
            
            # Validate format if present
            if 'format' in updated_config:
                format_value = updated_config['format'].lower() if isinstance(updated_config['format'], str) else ''
                if format_value not in ExportJobSerializer.VALID_FORMATS:
                    raise ValidationError({
                        'configuration': f'Invalid format. Must be one of: {", ".join(ExportJobSerializer.VALID_FORMATS)}'
                    })
                updated_config['format'] = format_value
            
            # Validate filters if present
            if 'filters' in updated_config:
                try:
                    updated_config['filters'] = ExportJobSerializer.validate_filters(
                        updated_config['filters']
                    )
                except ValidationError as e:
                    raise ValidationError({'configuration': f'Invalid filters: {str(e)}'})
            
            validated_data['configuration'] = updated_config
        
        # Validate is_active if provided
        if 'is_active' in data:
            is_active = data.get('is_active')
            if not isinstance(is_active, bool):
                raise ValidationError({'is_active': 'is_active must be a boolean'})
            validated_data['is_active'] = is_active
        
        return validated_data