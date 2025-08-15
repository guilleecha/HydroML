from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from ..models import DataSource


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
    """
    class Meta:
        model = DataSource
        fields = ['name', 'description', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Upload DataSource', css_class='btn btn-primary'))
