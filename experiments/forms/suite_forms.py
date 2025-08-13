from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from ..models import ExperimentSuite, MLExperiment
from projects.models import FeatureSet, Project

class AblationSuiteForm(forms.ModelForm):
    base_experiment = forms.ModelChoiceField(
        queryset=MLExperiment.objects.all(), # El queryset se filtrará en el __init__
        label="Experimento Base",
        help_text="Selecciona el experimento que servirá como plantilla de configuración."
    )
    
    ablation_feature_sets = forms.ModelMultipleChoiceField(
        queryset=FeatureSet.objects.all(), # El queryset se filtrará en el __init__
        widget=forms.CheckboxSelectMultiple,
        label="Grupos de Variables para Ablación",
        help_text="Selecciona los grupos de variables que se añadirán al conjunto base."
    )

    class Meta:
        model = ExperimentSuite
        fields = ['name', 'description', 'base_experiment'] # Se elimina 'ablation_feature_sets' de aquí

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar los querysets para que solo muestren los del proyecto actual
        self.fields['base_experiment'].queryset = MLExperiment.objects.filter(project=project)
        self.fields['ablation_feature_sets'].queryset = FeatureSet.objects.filter(project=project)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                '1. Información General', 'name', 'description'
            ),
            Fieldset(
                '2. Configuración de la Ablación', 'base_experiment', 'ablation_feature_sets'
            ),
            Submit('submit', 'Crear Suite de Ablación', css_class='btn-primary mt-4')
        )