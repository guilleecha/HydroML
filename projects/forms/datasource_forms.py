from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from ..models import DataSource, Project


class DataSourceUpdateForm(forms.ModelForm):
    """
    Form for updating DataSource name and description.
    """
    class Meta:
        model = DataSource
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Guardar Cambios', css_class='btn btn-primary'))


class DataSourceUploadForm(forms.ModelForm):
    """
    Form for uploading a new DataSource (name, description, file).
    Includes optional project selection when needed for many-to-many relationship.
    Enhanced with robust file validation.
    """
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        help_text="Select one or more projects to associate with this DataSource"
    )
    
    class Meta:
        model = DataSource
        fields = ['name', 'description', 'file']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        project = kwargs.pop('project', None)  # Current project context
        show_project_selection = kwargs.pop('show_project_selection', False)
        super().__init__(*args, **kwargs)
        
        # Configure projects field
        if user:
            self.fields['projects'].queryset = Project.objects.filter(owner=user).order_by('name')
            
        if project and not show_project_selection:
            # Pre-select current project and make it required
            self.fields['projects'].initial = [project]
            self.fields['projects'].required = True
            self.fields['projects'].help_text = f"This DataSource will be associated with '{project.name}'. You can select additional projects."
        elif show_project_selection:
            # Show project selection - NOT required to allow "Sin asignar" option
            self.fields['projects'].required = False
            if project:
                self.fields['projects'].initial = [project]
        else:
            # Remove projects field if no user context
            del self.fields['projects']
            
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Upload DataSource', css_class='btn btn-primary'))
        
    def save(self, commit=True):
        """
        Save the DataSource and handle many-to-many project relationships.
        """
        datasource = super().save(commit=False)
        
        # Set the owner (this will be set by the view)
        if commit:
            datasource.save()
            # Handle many-to-many relationships
            if 'projects' in self.cleaned_data:
                projects = self.cleaned_data['projects']
                for project in projects:
                    project.datasources.add(datasource)
            
        return datasource
    
    def clean_file(self):
        """
        Enhanced file validation for security and compatibility.
        """
        file = self.cleaned_data.get('file')
        if file:
            # File size validation (100MB limit)
            max_size = 100 * 1024 * 1024  # 100MB
            if file.size > max_size:
                raise forms.ValidationError(
                    f'El archivo es demasiado grande. Tamaño máximo permitido: 100MB. '
                    f'Tu archivo: {file.size / (1024*1024):.1f}MB'
                )
            
            # File extension validation
            allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
            file_extension = file.name.lower().split('.')[-1] if '.' in file.name else ''
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(
                    f'Tipo de archivo no válido. Extensiones permitidas: {", ".join(allowed_extensions)}'
                )
            
            # Basic file content validation
            if file_extension in ['csv', 'xlsx', 'xls']:
                try:
                    # Reset file pointer
                    file.seek(0)
                    # Basic content check - ensure it's not empty
                    content = file.read(1024)  # Read first 1KB
                    if not content:
                        raise forms.ValidationError('El archivo está vacío.')
                    # Reset file pointer for later processing
                    file.seek(0)
                except Exception as e:
                    raise forms.ValidationError(f'Error al leer el archivo: {str(e)}')
        
        return file
    
    def clean_name(self):
        """
        Validate datasource name for security and usability.
        """
        name = self.cleaned_data.get('name')
        if name:
            # Remove leading/trailing whitespace
            name = name.strip()
            
            # Length validation
            if len(name) < 3:
                raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
            
            if len(name) > 255:
                raise forms.ValidationError('El nombre no puede exceder 255 caracteres.')
            
            # Basic security check - no script tags or dangerous characters
            dangerous_patterns = ['<script', '<?', 'javascript:', 'data:']
            name_lower = name.lower()
            for pattern in dangerous_patterns:
                if pattern in name_lower:
                    raise forms.ValidationError('El nombre contiene caracteres no permitidos.')
        
        return name
