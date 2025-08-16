from django import forms
from django.core.exceptions import ValidationError
from .models import HyperparameterPreset
from .constants import ML_MODEL_CHOICES
import json


class HyperparameterPresetForm(forms.ModelForm):
    """
    Form for creating and editing hyperparameter presets.
    """
    hyperparameters_json = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'class': 'w-full px-3 py-2 bg-background-primary border border-border-default rounded-lg font-mono text-sm',
            'placeholder': '{\n  "learning_rate": 0.001,\n  "batch_size": 32,\n  "epochs": 100\n}'
        }),
        help_text="Enter hyperparameters as JSON. Example: {\"learning_rate\": 0.001, \"batch_size\": 32}",
        label="Hyperparameters (JSON)"
    )
    
    class Meta:
        model = HyperparameterPreset
        fields = ['name', 'description', 'model_type', 'hyperparameters_json']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 bg-background-primary border border-border-default rounded-lg',
                'placeholder': 'Enter preset name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 bg-background-primary border border-border-default rounded-lg',
                'placeholder': 'Describe what this preset is for (optional)'
            }),
            'model_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 bg-background-primary border border-border-default rounded-lg'
            }),
        }
        help_texts = {
            'name': 'A unique name for this preset',
            'description': 'Optional description of when to use this preset',
            'model_type': 'Select the ML model this preset is designed for',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate JSON field if editing existing preset
        if self.instance and self.instance.pk:
            self.fields['hyperparameters_json'].initial = json.dumps(
                self.instance.hyperparameters, indent=2
            )
    
    def clean_hyperparameters_json(self):
        """
        Validate that the JSON is valid and is a dictionary.
        """
        json_str = self.cleaned_data['hyperparameters_json'].strip()
        
        if not json_str:
            raise ValidationError("Hyperparameters JSON cannot be empty.")
        
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {e}")
        
        if not isinstance(parsed, dict):
            raise ValidationError("Hyperparameters must be a JSON object (dictionary), not a list or other type.")
        
        return parsed
    
    def clean_name(self):
        """
        Ensure preset name is unique for this user and model type.
        """
        name = self.cleaned_data['name']
        
        if self.user:
            # Get model_type from cleaned_data or instance
            model_type = self.cleaned_data.get('model_type')
            if not model_type and self.instance:
                model_type = self.instance.model_type
            
            if model_type:
                existing = HyperparameterPreset.objects.filter(
                    user=self.user,
                    name=name,
                    model_type=model_type
                )
                
                # If editing, exclude the current instance
                if self.instance and self.instance.pk:
                    existing = existing.exclude(pk=self.instance.pk)
                
                if existing.exists():
                    raise ValidationError(f"You already have a preset named '{name}' for {model_type}.")
        
        return name
    
    def save(self, commit=True):
        """
        Save the preset with the user and convert JSON string to dict.
        """
        preset = super().save(commit=False)
        preset.hyperparameters = self.cleaned_data['hyperparameters_json']
        
        if self.user:
            preset.user = self.user
        
        if commit:
            preset.save()
        
        return preset