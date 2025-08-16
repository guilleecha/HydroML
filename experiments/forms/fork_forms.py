# experiments/forms/fork_forms.py
"""
Forms for experiment forking functionality.
"""

from django import forms
from projects.models import Project


class ForkExperimentForm(forms.Form):
    """
    Form for selecting a project when forking an experiment.
    """
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={
            'class': 'form-select bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        }),
        help_text="Select the project where you want to save the forked experiment."
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show projects owned by the current user
        self.fields['project'].queryset = Project.objects.filter(owner=user).order_by('name')
