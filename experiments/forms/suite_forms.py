from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field
from ..models import ExperimentSuite, MLExperiment
from projects.models import FeatureSet, Project


class ExperimentSuiteForm(forms.ModelForm):
    """
    Form for creating a general ExperimentSuite.
    """
    base_experiment = forms.ModelChoiceField(
        queryset=MLExperiment.objects.none(),  # Will be filtered in __init__
        label="Experimento Base",
        help_text="Selecciona el experimento que servirá como plantilla de configuración.",
        required=False
    )
    
    class Meta:
        model = ExperimentSuite
        fields = ['name', 'description', 'study_type', 'base_experiment', 'search_space', 'optimization_metric']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'search_space': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': '{\n  "learning_rate": [0.01, 0.1, 0.2],\n  "n_estimators": [50, 100, 200]\n}'
            }),
        }
        labels = {
            'name': 'Nombre del Suite',
            'description': 'Descripción',
            'study_type': 'Tipo de Estudio',
            'search_space': 'Espacio de Búsqueda (JSON)',
            'optimization_metric': 'Métrica de Optimización'
        }
        help_texts = {
            'name': 'Nombre descriptivo para el suite de experimentos.',
            'description': 'Descripción detallada del objetivo del estudio.',
            'study_type': 'Tipo de estudio que realizará este suite.',
            'search_space': 'Definición JSON de los parámetros a explorar.',
            'optimization_metric': 'Métrica objetivo para optimizar (ej: r2_score, accuracy, f1_score).'
        }

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if project:
            # Filter base_experiment queryset to only show experiments from the current project
            self.fields['base_experiment'].queryset = MLExperiment.objects.filter(
                project=project,
                status__in=['FINISHED', 'RUNNING']  # Only completed or running experiments
            )

        # Configure Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Información General',
                Field('name', css_class='form-control'),
                Field('description', css_class='form-control'),
                css_class='mb-4'
            ),
            Fieldset(
                'Configuración del Estudio',
                Field('study_type', css_class='form-control'),
                Field('base_experiment', css_class='form-control'),
                Field('optimization_metric', css_class='form-control'),
                css_class='mb-4'
            ),
            Fieldset(
                'Parámetros de Búsqueda',
                Field('search_space', css_class='form-control font-monospace'),
                css_class='mb-4'
            ),
            Div(
                Submit('submit', 'Crear Suite de Experimentos', css_class='btn btn-primary'),
                css_class='d-grid gap-2'
            )
        )


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