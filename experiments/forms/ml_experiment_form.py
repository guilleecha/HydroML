# experiments/forms/ml_experiment_form.py
from django import forms
from crispy_forms.helper import FormHelper
from ..models import MLExperiment

class MLExperimentForm(forms.ModelForm):
    # Campos para hiperparámetros dinámicos
    rf_n_estimators = forms.IntegerField(label="N° de árboles (Random Forest)", required=False)
    rf_max_depth = forms.IntegerField(label="Profundidad máxima (Random Forest)", required=False)
    gb_n_estimators = forms.IntegerField(label="N° de árboles (Gradient Boosting)", required=False)
    gb_learning_rate = forms.FloatField(label="Tasa de Aprendizaje (Gradient Boosting)", required=False)

    MODEL_CHOICES = [
        ('', 'Selecciona un modelo...'),
        ('RandomForestRegressor', 'Random Forest'),
        ('GradientBoostingRegressor', 'Gradient Boosting'),
        ('LinearRegression', 'Regresión Lineal'),
    ]
    model_name = forms.ChoiceField(choices=MODEL_CHOICES, label="Modelo de Machine Learning a Utilizar")

    SPLIT_CHOICES = [
        ('RANDOM', 'Aleatorio'),
        ('TIMESERIES', 'Serie Temporal'),
    ]
    split_strategy = forms.ChoiceField(choices=SPLIT_CHOICES, label="Estrategia de División")

    class Meta:
        model = MLExperiment
        fields = [
            'name', 'description', 'model_name', 'input_datasource', 
            'target_column', 'feature_set', 'split_strategy', 'test_split_size', 'split_random_state'
        ]
        widgets = {
            'target_column': forms.HiddenInput(),
            'feature_set': forms.HiddenInput(),
        }

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_datasource'].queryset = project.datasources.all()
        
        # El FormHelper ahora es súper simple y no define ningún layout
        self.helper = FormHelper()
        self.helper.form_tag = False 
        self.helper.disable_csrf = True