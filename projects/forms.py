# projects/forms.py
from django import forms
from .models import Project, DataSource

class ProjectForm(forms.ModelForm):
    """
    Formulario para crear y actualizar un Proyecto.
    Directamente vinculado al modelo Project.
    """
    class Meta:
        model = Project
        # Excluimos el campo 'user', ya que se asignará automáticamente
        # desde el `request` en la vista.
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre del Proyecto',
            'description': 'Descripción (opcional)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Análisis de Calidad de Agua 2024'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class DataSourceUploadForm(forms.ModelForm):
    """
    Formulario para subir un nuevo archivo (DataSource).
    Es un subconjunto del modelo DataSource.
    """
    class Meta:
        model = DataSource
        # Solo necesitamos que el usuario proporcione estos campos.
        # El 'project' y 'data_type' se asignarán en la vista.
        fields = ['name', 'description', 'file']
        labels = {
            'name': 'Nombre del Dataset',
            'description': 'Descripción (opcional)',
            'file': 'Selecciona el archivo',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Datos Crudos - Estación Norte'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }