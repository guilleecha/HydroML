from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Div, HTML
from ..models import Project


class ProjectForm(forms.ModelForm):
    """
    Form for creating and updating Projects.
    """
    class Meta:
        model = Project
        fields = ['name', 'description', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'sr-only peer',
                'x-model': 'isPublic'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Let the template handle the form tag
        self.helper.label_class = 'block text-sm font-medium text-foreground-default dark:text-darcula-foreground mb-1'
        self.helper.field_class = 'mt-1 block w-full rounded-md border-border-default dark:border-darcula-border shadow-sm focus:border-brand-500 focus:ring-brand-500 bg-background-primary dark:bg-darcula-background text-foreground-default dark:text-darcula-foreground'
        
        # Customize the is_public field to be a toggle switch
        self.fields['is_public'].widget.attrs.update({
            'class': 'sr-only peer',
            'x-model': 'isPublic'
        })
