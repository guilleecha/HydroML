from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from ..models import Project


class ProjectForm(forms.ModelForm):
    """
    Form for creating and updating Projects.
    """
    class Meta:
        model = Project
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Let the template handle the form tag
        self.helper.label_class = 'block text-sm font-medium text-gray-700 mb-1'
        self.helper.field_class = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
