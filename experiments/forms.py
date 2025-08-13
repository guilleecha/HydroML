from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, HTML, Submit, Div
from .models import MLExperiment
from projects.models import DataSource

class MLExperimentForm(forms.ModelForm):
    # Campos para hiperparámetros dinámicos (opcionales)
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

    class Meta:
        model = MLExperiment
        fields = [
            'name', 'description', 'model_name', 'input_datasource', 
            'target_column', 'feature_set'
        ]
        widgets = {
            'target_column': forms.HiddenInput(),
            'feature_set': forms.HiddenInput(),
        }
        labels = {
            'name': 'Nombre del Experimento',
            'description': 'Describe el objetivo de este experimento',
            'input_datasource': 'Fuente de Datos de Entrada',
        }

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_datasource'].queryset = project.datasources.all()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'experiment-form'
        self.helper.attrs['data-get-columns-url'] = f"/tools/api/get-columns/{'00000000-0000-0000-0000-000000000000'}/"

        self.helper.layout = Layout(
            Fieldset(
                'Información General',
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    Column('description', css_class='form-group col-md-6 mb-0'),
                )
            ),
            Fieldset(
                'Configuración del Modelo',
                'model_name',
                # Usamos Div() de Crispy en lugar de HTML() para los campos dinámicos
                Div(
                    HTML('<p class="text-sm font-medium text-gray-600">Hiperparámetros (Random Forest)</p>'),
                    Row(Column('rf_n_estimators'), Column('rf_max_depth')),
                    id="rf-fields", 
                    css_class="hidden space-y-4 mt-4 border-l-4 p-4 rounded-r-md border-gray-200"
                ),
                Div(
                    HTML('<p class="text-sm font-medium text-gray-600">Hiperparámetros (Gradient Boosting)</p>'),
                    Row(Column('gb_n_estimators'), Column('gb_learning_rate')),
                    id="gb-fields", 
                    css_class="hidden space-y-4 mt-4 border-l-4 p-4 rounded-r-md border-gray-200"
                ),
            ),
            Fieldset(
                'Selección de Datos y Variables',
                'input_datasource',
                # Mantenemos HTML() para los elementos que NO son campos del formulario
                HTML("""
                    <div class="mt-4">
                        <label for="id_target_column_select" class="block text-sm font-medium text-gray-700">Variable Objetivo</label>
                        <select id="id_target_column_select" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" disabled>
                            <option value="">Primero selecciona una Fuente de Datos</option>
                        </select>
                    </div>
                """),
                HTML("""
                    <div class="mt-6">
                        <label class="block text-sm font-medium text-gray-700">Variables Predictoras</label>
                        <div class="flex space-x-4 items-center mt-2">
                            <div class="flex-1"><label for="features-available" class="text-xs text-gray-500 mb-1 block">Disponibles</label><select id="features-available" class="block w-full h-48 border rounded-md border-gray-300" multiple></select></div>
                            <div class="flex flex-col space-y-2"><button type="button" id="btn-add-feature" class="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">&gt;&gt;</button><button type="button" id="btn-remove-feature" class="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">&lt;&lt;</button></div>
                            <div class="flex-1"><label for="features-selected" class="text-xs text-gray-500 mb-1 block">Seleccionadas</label><select id="features-selected" class="block w-full h-48 border rounded-md border-gray-300" multiple></select></div>
                        </div>
                    </div>
                """),
            ),
            # Incluimos los campos ocultos para que se rendericen
            'target_column',
            'feature_set',
        )