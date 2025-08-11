
from django import forms
from .models import DataSource, Project

class DataSourceForm(forms.ModelForm):
    """
    Un formulario para crear nuevas instancias de DataSource.
    Permite al usuario subir un archivo y darle un nombre y descripción.
    """
    class Meta:
        model = DataSource
        # Incluimos los campos que el usuario debe rellenar.
        # 'project' se asignará automáticamente en la vista.
        fields = ['name', 'description', 'file']
        labels = {
            'name': 'Nombre de la Fuente de Datos',
            'description': 'Descripción (ej: Estación, período de datos)',
            'file': 'Seleccionar Archivo (CSV o Excel)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


# Formulario para crear Proyectos
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre del Proyecto',
            'description': 'Descripción Corta del Proyecto',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }