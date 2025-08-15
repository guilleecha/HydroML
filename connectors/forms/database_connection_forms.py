from django import forms
from .models import DatabaseConnection
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class DatabaseConnectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar Conexión', css_class='btn-primary'))

    class Meta:
        model = DatabaseConnection
        fields = ['name', 'database_type', 'host', 'port', 'database_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
