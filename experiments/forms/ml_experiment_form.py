# experiments/forms/ml_experiment_form.py
from django import forms
from crispy_forms.helper import FormHelper
from ..models import MLExperiment
from core.models import HyperparameterPreset
from core.constants import ML_MODEL_FORM_CHOICES

class MLExperimentForm(forms.ModelForm):
    # Load Preset field for hyperparameters
    load_preset = forms.ModelChoiceField(
        queryset=HyperparameterPreset.objects.none(),
        required=False,
        empty_label="Select a model first...",
        label="Load Hyperparameter Preset",
        help_text="Choose a saved preset to automatically populate hyperparameter fields",
        widget=forms.Select(attrs={
            'class': 'preset-selector',
            'data-api-url': '/api/presets/',
            'disabled': True  # Disabled by default until model is selected
        })
    )
    
    # Campos para hiperparámetros dinámicos
    rf_n_estimators = forms.IntegerField(label="N° de árboles (Random Forest)", required=False)
    rf_max_depth = forms.IntegerField(label="Profundidad máxima (Random Forest)", required=False)
    gb_n_estimators = forms.IntegerField(label="N° de árboles (Gradient Boosting)", required=False)
    gb_learning_rate = forms.FloatField(label="Tasa de Aprendizaje (Gradient Boosting)", required=False)

    model_name = forms.ChoiceField(choices=ML_MODEL_FORM_CHOICES, label="Modelo de Machine Learning a Utilizar")

    SPLIT_CHOICES = [
        ('RANDOM', 'Aleatorio'),
        ('TIMESERIES', 'Serie Temporal'),
    ]
    split_strategy = forms.ChoiceField(choices=SPLIT_CHOICES, label="Estrategia de División")

    VALIDATION_CHOICES = [
        ('TRAIN_TEST_SPLIT', 'Simple Train/Test Split'),
        ('TIME_SERIES_CV', 'Time Series Cross-Validation'),
    ]
    validation_strategy = forms.ChoiceField(
        choices=VALIDATION_CHOICES, 
        label="Estrategia de Validación",
        help_text="Selecciona la estrategia de validación para evaluar el modelo"
    )

    class Meta:
        model = MLExperiment
        fields = [
            'name', 'description', 'model_name', 'input_datasource', 
            'target_column', 'feature_set', 'split_strategy', 'validation_strategy', 
            'test_split_size', 'split_random_state', 'tags'
        ]
        widgets = {
            'target_column': forms.HiddenInput(),
            'feature_set': forms.HiddenInput(),
        }

    def __init__(self, project, *args, **kwargs):
        # Extract user from kwargs if passed
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['input_datasource'].queryset = project.datasources.all()
        
        # Set queryset for load_preset field to current user's presets
        if self.user:
            self.fields['load_preset'].queryset = HyperparameterPreset.objects.filter(user=self.user)
        
        # El FormHelper ahora es súper simple y no define ningún layout
        self.helper = FormHelper()
        self.helper.form_tag = False 
        self.helper.disable_csrf = True