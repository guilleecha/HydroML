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
            # Show project selection
            self.fields['projects'].required = True
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
