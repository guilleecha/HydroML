# data_tools/forms/fusion_forms.py
from django import forms
from projects.models import DataSource

class DataFusionForm(forms.Form):
    """
    Formulario para configurar una tarea de fusión de datos.
    """
    datasources_to_merge = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Selecciona los Datasets que deseas fusionar (2 o más)",
    )
    merge_column = forms.CharField(
        label="Columna de Unión (Merge Column)",
        help_text="Escribe el nombre exacto de la columna común (ej: 'Fecha').",
        widget=forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700'})
    )
    output_name = forms.CharField(
        label="Nombre del Nuevo Dataset Fusionado",
        widget=forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700'})
    )

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['datasources_to_merge'].queryset = DataSource.objects.filter(project=project)

    def clean_datasources_to_merge(self):
        selected_datasources = self.cleaned_data.get('datasources_to_merge')
        if selected_datasources and len(selected_datasources) < 2:
            raise forms.ValidationError("Debes seleccionar al menos dos datasets para fusionar.")
        return selected_datasources