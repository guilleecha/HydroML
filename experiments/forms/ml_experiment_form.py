# experiments/forms/ml_experiment_form.py
from django import forms
from crispy_forms.helper import FormHelper
from ..models import MLExperiment
from core.models import HyperparameterPreset
from core.constants import ML_MODEL_FORM_CHOICES
from projects.models import Project, DataSource
from ..validators import MLExperimentValidator
import json
import sentry_sdk
import logging

logger = logging.getLogger(__name__)

class MLExperimentForm(forms.ModelForm):
    # Project selection field
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=True,
        empty_label="-- Selecciona un workspace --",
        label="Workspace de Destino",
        widget=forms.Select(attrs={'class': 'project-selector'})
    )
    
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
            'name', 'description', 'project', 'model_name', 'input_datasource', 
            'target_column', 'feature_set', 'split_strategy', 'validation_strategy', 
            'test_split_size', 'split_random_state', 'tags'
        ]
        widgets = {
            'target_column': forms.HiddenInput(),
            'feature_set': forms.HiddenInput(),
        }

    def __init__(self, project=None, *args, **kwargs):
        # Extract user from kwargs if passed
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up project queryset
        if self.user:
            self.fields['project'].queryset = Project.objects.filter(owner=self.user)
            # Pre-select project if provided
            if project:
                self.fields['project'].initial = project.id
        
        # Set up datasource queryset - show all user's datasources initially
        from projects.models import DataSource
        if self.user:
            self.fields['input_datasource'].queryset = DataSource.objects.filter(
                projects__owner=self.user
            ).distinct()
        else:
            self.fields['input_datasource'].queryset = DataSource.objects.none()
        
        # Set queryset for load_preset field to current user's presets
        if self.user:
            self.fields['load_preset'].queryset = HyperparameterPreset.objects.filter(user=self.user)
        
        # El FormHelper ahora es súper simple y no define ningún layout
        self.helper = FormHelper()
        self.helper.form_tag = False 
        self.helper.disable_csrf = True
    
    def clean(self):
        """Custom validation with ML-specific checks"""
        cleaned_data = super().clean()
        
        # Get form data
        datasource = cleaned_data.get('input_datasource')
        target_column = cleaned_data.get('target_column')
        feature_set = cleaned_data.get('feature_set')
        model_name = cleaned_data.get('model_name')
        
        # Only validate if we have the minimum required data
        if not datasource or not target_column or not feature_set or not model_name:
            return cleaned_data
        
        try:
            # Set Sentry context for form validation
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("form_validation", "ml_experiment")
                scope.set_context("form_data", {
                    "datasource_name": datasource.name if datasource else "None",
                    "model_name": model_name,
                    "target_column": target_column,
                    "user": self.user.username if self.user else "Anonymous"
                })
            
            # Parse feature set
            if isinstance(feature_set, str):
                feature_columns = json.loads(feature_set)
            elif isinstance(feature_set, list):
                feature_columns = feature_set
            else:
                error_msg = "Formato de características inválido"
                logger.warning(f"Invalid feature set format: {type(feature_set)}")
                raise forms.ValidationError(error_msg)
            
            # Generate column flags if missing
            if datasource and not datasource.column_flags:
                logger.info(f"Generating missing column flags for datasource {datasource.id}")
                from projects.utils.column_analyzer import ColumnAnalyzer
                try:
                    ColumnAnalyzer.update_datasource_flags(datasource)
                except Exception as flag_error:
                    logger.warning(f"Failed to generate column flags: {flag_error}")
                    sentry_sdk.capture_message(f"Column flags generation failed for datasource {datasource.id}")
            
            # Run ML validation
            validator = MLExperimentValidator(
                datasource=datasource,
                target_column=target_column,
                feature_columns=feature_columns,
                model_name=model_name
            )
            
            validation_result = validator.validate_all()
            logger.info(f"Validation completed - Valid: {validation_result['valid']}, Errors: {len(validation_result['errors'])}, Warnings: {len(validation_result['warnings'])}")
            
            # Add validation results to form for template access
            self.validation_result = validation_result
            
            # Raise errors if validation failed
            if not validation_result['valid']:
                error_messages = validation_result['errors']
                
                # Log validation failure with context
                logger.warning(f"ML experiment validation failed with {len(error_messages)} errors")
                sentry_sdk.capture_message(
                    f"ML experiment validation failed: {len(error_messages)} errors",
                    level="warning",
                    extras={
                        "errors": error_messages,
                        "warnings": validation_result.get('warnings', [])
                    }
                )
                
                raise forms.ValidationError({
                    '__all__': error_messages
                })
            
            # Store warnings for display (don't prevent form submission)
            if validation_result['warnings']:
                self.warnings = validation_result['warnings']
                logger.info(f"ML experiment validation passed with {len(validation_result['warnings'])} warnings")
            
        except forms.ValidationError:
            # Re-raise form validation errors without modification
            raise
        except json.JSONDecodeError as e:
            error_msg = f"Error parseando características: formato JSON inválido"
            logger.error(f"JSON decode error in feature set: {e}")
            sentry_sdk.capture_exception(e)
            raise forms.ValidationError(error_msg)
        except Exception as e:
            # Capture unexpected errors
            logger.error(f"Unexpected error during ML validation: {str(e)}", exc_info=True)
            sentry_sdk.capture_exception(e)
            raise forms.ValidationError(f"Error inesperado durante validación: {str(e)}")
        
        return cleaned_data