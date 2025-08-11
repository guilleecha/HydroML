# hydro_app/forms.py

from django import forms
from .models import Experiment, MLExperiment
from projects.models import DataSource

class ExperimentForm(forms.ModelForm):
    # Campo para seleccionar múltiples fuentes de datos. Se mostrará como una lista de checkboxes.
    datasources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.none(), # El queryset se define en la vista
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selecciona las Fuentes de Datos a fusionar"
    )

    def __init__(self, datasources_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if datasources_queryset:
            self.fields['datasources'].queryset = datasources_queryset

    class Meta:
        model = Experiment
        fields = ['name', 'description', 'datasources']
        labels = {
            'name': 'Nombre del Experimento',
            'description': 'Describe el objetivo de este experimento'
        }



class ExperimentUpdateForm(forms.ModelForm):
    """
    Un formulario para actualizar los metadatos de un Experimento existente.
    """
    class Meta:
        model = Experiment
        # Solo permitimos editar el nombre y la descripción
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre del Experimento',
            'description': 'Descripción'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class MLExperimentForm(forms.ModelForm):
    # Campo para seleccionar el dataset de entrada. Lo filtraremos en la vista.
    source_dataset = forms.ModelChoiceField(
        queryset=DataSource.objects.all(),
        label="Dataset de Origen",
        help_text="Seleccioná un dataset preparado para usar como entrada."
    )
    # Usamos un área de texto para las features. El usuario las separará por comas.
    feature_set = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label="Variables Predictoras (Features)",
        help_text="Escribí los nombres de las columnas separados por comas."
    )

    class Meta:
        model = MLExperiment
        fields = [
            'name', 'description', 'source_dataset', 'target_column',
            'model_name', 'feature_set', 'hyperparameters', 'validation_strategy'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'source_dataset': forms.Select(attrs={'class': 'form-select'}),
            'target_column': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.Select(attrs={'class': 'form-select'}),
            'hyperparameters': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'validation_strategy': forms.Select(attrs={'class': 'form-select'}),
        }