from django import forms

class FeatureEngineeringForm(forms.Form):
    new_column_name = forms.CharField(
        label="Nombre de la Nueva Columna",
        max_length=255
    )
    formula_string = forms.CharField(
        label="Fórmula (ej. 'columna_A * 2')",
        widget=forms.Textarea
    )
