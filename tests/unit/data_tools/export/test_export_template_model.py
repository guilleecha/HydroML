"""
Comprehensive unit tests for ExportTemplate model.

Tests all model functionality including:
- Template creation and validation
- Configuration validation
- Template types and access control
- Usage tracking
- Template duplication
- Default template creation
"""

import uuid
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from data_tools.models.export_template import ExportTemplate

User = get_user_model()


class ExportTemplateModelTest(TestCase):
    """Test ExportTemplate model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

    def test_export_template_creation_basic(self):
        """Test basic ExportTemplate creation."""
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        self.assertIsInstance(template.id, uuid.UUID)
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.user, self.user)
        self.assertEqual(template.template_type, 'user')  # Default
        self.assertTrue(template.is_active)  # Default
        self.assertEqual(template.usage_count, 0)  # Default
        self.assertEqual(template.description, '')  # Default
        self.assertIsNotNone(template.created_at)
        self.assertIsNotNone(template.updated_at)
        self.assertIsNone(template.last_used_at)

    def test_export_template_creation_with_all_fields(self):
        """Test ExportTemplate creation with all fields."""
        config = {
            'format': 'json',
            'filters': {'columns': ['col1', 'col2']},
            'options': {'indent': 2}
        }
        
        template = ExportTemplate.objects.create(
            name='Complex Template',
            description='A complex export template',
            user=self.admin_user,
            template_type='system',
            is_active=False,
            configuration=config,
            usage_count=10
        )
        
        self.assertEqual(template.name, 'Complex Template')
        self.assertEqual(template.description, 'A complex export template')
        self.assertEqual(template.template_type, 'system')
        self.assertFalse(template.is_active)
        self.assertEqual(template.configuration, config)
        self.assertEqual(template.usage_count, 10)

    def test_export_template_string_representation(self):
        """Test ExportTemplate string representation."""
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user,
            template_type='shared',
            configuration={'format': 'parquet'}
        )
        
        expected_str = "Test Template (Shared Template)"
        self.assertEqual(str(template), expected_str)

    def test_export_template_validation_invalid_config_type(self):
        """Test validation with invalid configuration type."""
        template = ExportTemplate(
            name='Invalid Template',
            user=self.user,
            configuration="invalid_string_config"  # Should be dict
        )
        
        with self.assertRaises(ValidationError) as cm:
            template.full_clean()
        
        self.assertIn('Configuration must be a valid JSON object', str(cm.exception))

    def test_export_template_validation_missing_format(self):
        """Test validation with missing required format field."""
        template = ExportTemplate(
            name='Missing Format Template',
            user=self.user,
            configuration={}  # Missing format
        )
        
        with self.assertRaises(ValidationError) as cm:
            template.full_clean()
        
        self.assertIn("Configuration must include 'format' field", str(cm.exception))

    def test_export_template_validation_invalid_format(self):
        """Test validation with invalid format value."""
        template = ExportTemplate(
            name='Invalid Format Template',
            user=self.user,
            configuration={'format': 'invalid_format'}
        )
        
        with self.assertRaises(ValidationError) as cm:
            template.full_clean()
        
        self.assertIn('Format must be one of:', str(cm.exception))

    def test_export_template_validation_valid_formats(self):
        """Test validation with all valid formats."""
        valid_formats = ['csv', 'json', 'parquet', 'excel']
        
        for format_type in valid_formats:
            template = ExportTemplate(
                name=f'Template {format_type}',
                user=self.user,
                configuration={'format': format_type}
            )
            
            try:
                template.full_clean()
            except ValidationError:
                self.fail(f"ValidationError raised for valid format: {format_type}")

    def test_unique_constraint_name_per_user(self):
        """Test unique constraint on template name per user."""
        # Create first template
        ExportTemplate.objects.create(
            name='Duplicate Name',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        # Try to create another template with same name for same user
        with self.assertRaises(IntegrityError):
            ExportTemplate.objects.create(
                name='Duplicate Name',
                user=self.user,
                configuration={'format': 'json'}
            )

    def test_unique_constraint_different_users(self):
        """Test that same template name is allowed for different users."""
        # Create template for first user
        template1 = ExportTemplate.objects.create(
            name='Same Name',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        # Create template with same name for different user (should work)
        template2 = ExportTemplate.objects.create(
            name='Same Name',
            user=self.other_user,
            configuration={'format': 'json'}
        )
        
        self.assertEqual(template1.name, template2.name)
        self.assertNotEqual(template1.user, template2.user)

    def test_format_property(self):
        """Test format property."""
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user,
            configuration={'format': 'parquet', 'other_field': 'value'}
        )
        
        self.assertEqual(template.format, 'parquet')

    def test_format_property_default(self):
        """Test format property with default value."""
        # Create template without format (bypassing validation for testing)
        template = ExportTemplate.objects.create(
            name='Test Template',
            user=self.user,
            configuration={'format': 'csv'}  # Will be valid during creation
        )
        
        # Modify configuration to remove format
        template.configuration = {'other_field': 'value'}
        template.save(update_fields=['configuration'])  # Skip validation
        
        self.assertEqual(template.format, 'csv')  # Default fallback

    def test_has_filters_property(self):
        """Test has_filters property."""
        # Template without filters
        template1 = ExportTemplate.objects.create(
            name='No Filters Template',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        self.assertFalse(template1.has_filters)
        
        # Template with empty filters
        template2 = ExportTemplate.objects.create(
            name='Empty Filters Template',
            user=self.user,
            configuration={'format': 'csv', 'filters': {}}
        )
        
        self.assertFalse(template2.has_filters)
        
        # Template with filters
        template3 = ExportTemplate.objects.create(
            name='With Filters Template',
            user=self.user,
            configuration={
                'format': 'csv',
                'filters': {'columns': ['col1', 'col2']}
            }
        )
        
        self.assertTrue(template3.has_filters)

    def test_increment_usage_method(self):
        """Test increment_usage method."""
        template = ExportTemplate.objects.create(
            name='Usage Template',
            user=self.user,
            configuration={'format': 'json'}
        )
        
        initial_count = template.usage_count
        initial_time = timezone.now()
        
        template.increment_usage()
        
        template.refresh_from_db()
        self.assertEqual(template.usage_count, initial_count + 1)
        self.assertIsNotNone(template.last_used_at)
        self.assertGreaterEqual(template.last_used_at, initial_time)
        
        # Test multiple increments
        template.increment_usage()
        template.refresh_from_db()
        self.assertEqual(template.usage_count, initial_count + 2)

    def test_duplicate_for_user_method(self):
        """Test duplicate_for_user method."""
        original_template = ExportTemplate.objects.create(
            name='Original Template',
            description='Original description',
            user=self.user,
            template_type='user',
            configuration={'format': 'csv', 'filters': {'columns': ['col1']}}
        )
        
        # Duplicate for different user
        duplicate = original_template.duplicate_for_user(self.other_user)
        
        self.assertNotEqual(duplicate.id, original_template.id)
        self.assertEqual(duplicate.name, 'Original Template (Copy)')
        self.assertEqual(duplicate.description, original_template.description)
        self.assertEqual(duplicate.user, self.other_user)
        self.assertEqual(duplicate.template_type, 'user')  # Always user for duplicates
        self.assertEqual(duplicate.configuration, original_template.configuration)
        self.assertEqual(duplicate.usage_count, 0)  # Reset usage count

    def test_duplicate_for_user_with_custom_name(self):
        """Test duplicate_for_user method with custom name."""
        original_template = ExportTemplate.objects.create(
            name='Original Template',
            user=self.user,
            configuration={'format': 'json'}
        )
        
        duplicate = original_template.duplicate_for_user(
            self.other_user,
            new_name='Custom Duplicate Name'
        )
        
        self.assertEqual(duplicate.name, 'Custom Duplicate Name')
        self.assertEqual(duplicate.user, self.other_user)

    def test_get_available_for_user_class_method(self):
        """Test get_available_for_user class method."""
        # Create user template
        user_template = ExportTemplate.objects.create(
            name='User Template',
            user=self.user,
            template_type='user',
            configuration={'format': 'csv'}
        )
        
        # Create system template
        system_template = ExportTemplate.objects.create(
            name='System Template',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'json'}
        )
        
        # Create shared template
        shared_template = ExportTemplate.objects.create(
            name='Shared Template',
            user=self.admin_user,
            template_type='shared',
            configuration={'format': 'parquet'}
        )
        
        # Create another user's template (should not be accessible)
        ExportTemplate.objects.create(
            name='Other User Template',
            user=self.other_user,
            template_type='user',
            configuration={'format': 'excel'}
        )
        
        # Create inactive template (should not be accessible)
        ExportTemplate.objects.create(
            name='Inactive Template',
            user=self.admin_user,
            template_type='system',
            is_active=False,
            configuration={'format': 'csv'}
        )
        
        # Get available templates for user
        available_templates = ExportTemplate.get_available_for_user(self.user)
        
        self.assertEqual(available_templates.count(), 3)
        template_names = list(available_templates.values_list('name', flat=True))
        self.assertIn('User Template', template_names)
        self.assertIn('System Template', template_names)
        self.assertIn('Shared Template', template_names)
        self.assertNotIn('Other User Template', template_names)
        self.assertNotIn('Inactive Template', template_names)

    def test_get_available_for_user_with_type_filter(self):
        """Test get_available_for_user with template type filter."""
        # Create templates of different types
        ExportTemplate.objects.create(
            name='User Template',
            user=self.user,
            template_type='user',
            configuration={'format': 'csv'}
        )
        
        ExportTemplate.objects.create(
            name='System Template',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'json'}
        )
        
        # Filter by type
        system_templates = ExportTemplate.get_available_for_user(
            self.user,
            template_type='system'
        )
        
        self.assertEqual(system_templates.count(), 1)
        self.assertEqual(system_templates.first().name, 'System Template')

    def test_get_popular_templates_class_method(self):
        """Test get_popular_templates class method."""
        # Create templates with different usage counts
        template1 = ExportTemplate.objects.create(
            name='Popular Template 1',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'csv'},
            usage_count=100
        )
        template1.last_used_at = timezone.now()
        template1.save()
        
        template2 = ExportTemplate.objects.create(
            name='Popular Template 2',
            user=self.admin_user,
            template_type='shared',
            configuration={'format': 'json'},
            usage_count=50
        )
        template2.last_used_at = timezone.now()
        template2.save()
        
        # Create user template (should not appear in popular templates)
        ExportTemplate.objects.create(
            name='User Template',
            user=self.user,
            template_type='user',
            configuration={'format': 'parquet'},
            usage_count=200
        )
        
        # Create template with zero usage (should not appear)
        ExportTemplate.objects.create(
            name='Unused Template',
            user=self.admin_user,
            template_type='system',
            configuration={'format': 'excel'},
            usage_count=0
        )
        
        popular_templates = ExportTemplate.get_popular_templates(limit=5)
        
        self.assertEqual(popular_templates.count(), 2)
        # Should be ordered by usage count descending
        self.assertEqual(popular_templates[0], template1)
        self.assertEqual(popular_templates[1], template2)

    def test_get_popular_templates_with_limit(self):
        """Test get_popular_templates with custom limit."""
        # Create multiple popular templates
        for i in range(5):
            template = ExportTemplate.objects.create(
                name=f'Popular Template {i}',
                user=self.admin_user,
                template_type='system',
                configuration={'format': 'csv'},
                usage_count=10 - i  # Descending usage count
            )
            template.last_used_at = timezone.now()
            template.save()
        
        popular_templates = ExportTemplate.get_popular_templates(limit=3)
        
        self.assertEqual(popular_templates.count(), 3)

    @patch('django.contrib.auth.get_user_model')
    def test_create_default_templates_success(self, mock_get_user_model):
        """Test successful creation of default templates."""
        mock_get_user_model.return_value = User
        
        created_templates = ExportTemplate.create_default_templates()
        
        # Should create 4 default templates
        self.assertEqual(len(created_templates), 4)
        
        # Check that all default templates were created
        template_names = [t.name for t in created_templates]
        expected_names = [
            'CSV - Full Export',
            'JSON - Full Export', 
            'Parquet - Optimized Export',
            'Excel - Report Export'
        ]
        
        for name in expected_names:
            self.assertIn(name, template_names)
        
        # Check that all are system templates
        for template in created_templates:
            self.assertEqual(template.template_type, 'system')

    @patch('django.contrib.auth.get_user_model')
    def test_create_default_templates_already_exist(self, mock_get_user_model):
        """Test create_default_templates when templates already exist."""
        mock_get_user_model.return_value = User
        
        # Create one default template manually
        system_user = User.objects.filter(is_superuser=True).first() or self.admin_user
        ExportTemplate.objects.create(
            name='CSV - Full Export',
            user=system_user,
            template_type='system',
            configuration={'format': 'csv'}
        )
        
        created_templates = ExportTemplate.create_default_templates()
        
        # Should create 3 new templates (one already existed)
        self.assertEqual(len(created_templates), 3)

    @patch('django.contrib.auth.get_user_model')
    def test_create_default_templates_no_superuser(self, mock_get_user_model):
        """Test create_default_templates when no superuser exists."""
        mock_get_user_model.return_value = User
        
        # Remove all superusers
        User.objects.filter(is_superuser=True).delete()
        
        created_templates = ExportTemplate.create_default_templates()
        
        # Should still create templates with a system user
        self.assertEqual(len(created_templates), 4)
        
        # Check that a system user was created
        system_user = User.objects.get(username='system')
        self.assertFalse(system_user.is_active)

    @patch('django.contrib.auth.get_user_model')
    def test_create_default_templates_user_creation_fails(self, mock_get_user_model):
        """Test create_default_templates when user creation fails."""
        # Mock User model to raise exception
        mock_user_model = Mock()
        mock_user_model.objects.filter.side_effect = Exception("Database error")
        mock_get_user_model.return_value = mock_user_model
        
        created_templates = ExportTemplate.create_default_templates()
        
        # Should return empty list when user setup fails
        self.assertEqual(created_templates, [])

    def test_model_ordering(self):
        """Test that templates are ordered by updated_at descending."""
        # Create templates with different update times
        template1 = ExportTemplate.objects.create(
            name='Template 1',
            user=self.user,
            configuration={'format': 'csv'}
        )
        
        template2 = ExportTemplate.objects.create(
            name='Template 2',
            user=self.user,
            configuration={'format': 'json'}
        )
        
        # Update template1 to make it more recent
        template1.description = 'Updated description'
        template1.save()
        
        templates = list(ExportTemplate.objects.all())
        
        # Should be ordered by updated_at descending (most recently updated first)
        self.assertEqual(templates[0], template1)
        self.assertEqual(templates[1], template2)

    def test_database_indexes(self):
        """Test that database indexes are created properly."""
        # This test mainly verifies that the model definition is correct
        # The actual index creation is tested at the database migration level
        
        template = ExportTemplate.objects.create(
            name='Index Test Template',
            user=self.user,
            template_type='system',
            configuration={'format': 'csv'},
            usage_count=10
        )
        
        # Test queries that should use indexes
        # These should execute without errors and efficiently
        
        # Index on user, template_type, updated_at
        user_templates = ExportTemplate.objects.filter(
            user=self.user,
            template_type='user'
        ).order_by('-updated_at')
        self.assertTrue(user_templates.exists())
        
        # Index on template_type, is_active
        active_system_templates = ExportTemplate.objects.filter(
            template_type='system',
            is_active=True
        )
        # May or may not exist, but query should work
        list(active_system_templates)
        
        # Index on usage_count, last_used_at
        popular_templates = ExportTemplate.objects.filter(
            usage_count__gt=0
        ).order_by('-last_used_at')
        list(popular_templates)