import json
from django import forms
from .models import MLExperiment
from projects.models import DataSource


class MLExperimentForm(forms.ModelForm):
    """
    Formulario para crear y actualizar un Experimento de Machine Learning.
    Está directamente vinculado al modelo MLExperiment.
    """

    # Sobrescribimos el campo para tener control total sobre el widget y el queryset.
    feature_set = forms.CharField(
        label="Variables Predictoras (Features)",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        help_text="Escribe los nombres de las columnas separados por comas. Ej: temp_max, temp_min, precipitacion"
    )

    hyperparameters = forms.CharField(
        label="Hiperparámetros (formato JSON)",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        help_text='Introduce un diccionario JSON. Ejemplo: {"n_estimators": 150, "max_depth": 10}'
    )

    # Paso 1: Cambiar a un ChoiceField para seleccionar el modelo.
    MODEL_CHOICES = [
        ('RandomForestRegressor', 'Random Forest'),
        ('GradientBoostingRegressor', 'Gradient Boosting'),
        ('LinearRegression', 'Regresión Lineal'),
    ]
    model_name = forms.ChoiceField(choices=MODEL_CHOICES, label="Modelo de Machine Learning a Utilizar", widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, project, *args, **kwargs):
        """
        El 'truco' para este formulario: requiere que se le pase el proyecto actual
        para poder filtrar los DataSources y mostrar solo los relevantes.
        """
        super().__init__(*args, **kwargs)

        # Filtramos el queryset del campo 'input_datasource' para mostrar solo
        # los datasets que pertenecen al proyecto actual.
        self.fields['input_datasource'].queryset = DataSource.objects.filter(project=project)

    def clean_feature_set(self):
        """
        Toma el string del campo 'feature_set' y lo convierte en una lista
        de strings limpios, que es lo que el modelo JSONField espera.
        """
        features_string = self.cleaned_data.get('feature_set', '')
        # Divide por comas, elimina espacios en blanco y quita cualquier entrada vacía.
        return [feature.strip() for feature in features_string.split(',') if feature.strip()]

    def clean_hyperparameters(self):
        """
        Valida que el string de hiperparámetros sea un JSON válido.
        Devuelve un diccionario Python.
        """
        params_string = self.cleaned_data.get('hyperparameters', '')
        if not params_string:
            return {}  # Si está vacío, devuelve un diccionario vacío
        try:
            return json.loads(params_string)
        except json.JSONDecodeError:
            raise forms.ValidationError("El formato JSON de los hiperparámetros no es válido.")

    class Meta:
        model = MLExperiment

        # Campos que se mostrarán en el formulario.
        # Coinciden con el modelo MLExperiment que definimos.
        fields = [
            'name',
            'description',
            'input_datasource',
            'target_column',
            'model_name',
            'feature_set',
            'hyperparameters'
        ]

        labels = {
            'name': "Nombre del Experimento",
            'description': "Describe el objetivo de este experimento",
            'input_datasource': "Fuente de Datos de Entrada",
            'target_column': "Variable Objetivo (Target)",
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'input_datasource': forms.Select(attrs={'class': 'form-select'}),
            'target_column': forms.TextInput(attrs={'class': 'form-control'}),
        }