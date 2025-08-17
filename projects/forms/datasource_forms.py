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
    Includes optional project selection when needed.
    """
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=False,
        empty_label="Seleccionar proyecto...",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-lg border border-border-default dark:border-darcula-border bg-background-primary dark:bg-darcula-background text-foreground-default dark:text-darcula-foreground placeholder-foreground-muted dark:placeholder-darcula-foreground-muted focus:border-brand-500 dark:focus:border-darcula-accent focus:ring-brand-500 dark:focus:ring-darcula-accent sm:text-sm'
        })
    )
    
    class Meta:
        model = DataSource
        fields = ['project', 'name', 'description', 'file']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        project = kwargs.pop('project', None)
        show_project_selection = kwargs.pop('show_project_selection', False)
        super().__init__(*args, **kwargs)
        
        # Configure project field
        if user:
            self.fields['project'].queryset = Project.objects.filter(owner=user).order_by('name')
            
        if project and not show_project_selection:
            # Hide project field and set initial value
            self.fields['project'].widget = forms.HiddenInput()
            self.fields['project'].initial = project
            self.fields['project'].required = False
        elif show_project_selection:
            # Show project dropdown
            self.fields['project'].required = True
            if project:
                self.fields['project'].initial = project
        else:
            # Remove project field entirely if no user context
            del self.fields['project']
            
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Upload DataSource', css_class='btn btn-primary'))
