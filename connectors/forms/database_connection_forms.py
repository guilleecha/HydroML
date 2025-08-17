# connectors/forms/database_connection_forms.py

from django import forms
from django.core.exceptions import ValidationError
from ..models import DatabaseConnection


class DatabaseConnectionForm(forms.ModelForm):
    """Form for creating and editing database connections."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        required=False,
        help_text="Leave blank to keep current password when editing"
    )
    
    class Meta:
        model = DatabaseConnection
        fields = ['name', 'database_type', 'host', 'port', 'database_name', 'username', 'password']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Connection name'
            }),
            'database_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'host': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'localhost'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5432'
            }),
            'database_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Database name'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Make fields conditional based on database type
        self.fields['host'].required = False
        self.fields['port'].required = False
        self.fields['username'].required = False
        
        # Add JavaScript to handle conditional fields
        self.fields['database_type'].widget.attrs.update({
            'x-on:change': 'handleDatabaseTypeChange($event)'
        })
    
    def clean_name(self):
        name = self.cleaned_data['name']
        
        # Check for duplicate names for the same user
        queryset = DatabaseConnection.objects.filter(
            user=self.user,
            name=name
        )
        
        # Exclude current instance when editing
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError("You already have a connection with this name.")
        
        return name
    
    def clean(self):
        cleaned_data = super().clean()
        database_type = cleaned_data.get('database_type')
        
        # Validate required fields based on database type
        if database_type in ['postgresql', 'mysql']:
            required_fields = ['host', 'port', 'username']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f"This field is required for {database_type}.")
        
        return cleaned_data
    
    def save(self, commit=True):
        connection = super().save(commit=False)
        
        if self.user:
            connection.user = self.user
        
        # Only update password if it was provided
        if self.cleaned_data.get('password'):
            connection.password = self.cleaned_data['password']
        elif not self.instance.pk:
            # New instance must have a password
            if not self.cleaned_data.get('password'):
                raise ValidationError("Password is required for new connections.")
        
        if commit:
            connection.save()
        
        return connection


class DatabaseConnectionTestForm(forms.Form):
    """Form for testing database connections."""
    
    connection_id = forms.UUIDField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_connection_id(self):
        connection_id = self.cleaned_data['connection_id']
        
        try:
            connection = DatabaseConnection.objects.get(
                id=connection_id,
                user=self.user
            )
            self.cleaned_data['connection'] = connection
            return connection_id
        except DatabaseConnection.DoesNotExist:
            raise ValidationError("Connection not found or you don't have permission to test it.")
    
    def test_connection(self):
        """Test the database connection."""
        if not self.is_valid():
            return False, "Form validation failed."
        
        connection = self.cleaned_data['connection']
        return connection.test_connection()
