from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from projects.models.datasource import DataSource
# Import moved inside function to avoid circular import (Django best practice)
from ..forms import FeatureEngineeringForm
import pandas as pd

@login_required
def feature_engineering_page(request, datasource_id):
    parent_datasource = get_object_or_404(DataSource, id=datasource_id)

    if request.method == 'POST':
        form = FeatureEngineeringForm(request.POST)
        if form.is_valid():
            # Import inside function to avoid circular import (Django best practice)
            try:
                from data_tools.services import perform_feature_engineering
            except ImportError:
                # Fallback if services module has issues
                messages.error(request, "Feature engineering service is temporarily unavailable.")
                return render(request, 'data_tools/feature_engineering.html', {
                    'form': form,
                    'datasource': parent_datasource,
                    "columns": [],
                })
            
            new_column_name = form.cleaned_data['new_column_name']
            formula_string = form.cleaned_data['formula_string']
            result = perform_feature_engineering(datasource_id, new_column_name, formula_string)
            if isinstance(result, dict) and "error" in result:
                messages.error(request, f"Error: {result['error']}")
            else:
                messages.success(request, f"Columna '{new_column_name}' creada exitosamente.")
                return redirect('project_detail', project_id=parent_datasource.project.id)
    else:
        form = FeatureEngineeringForm()

    df = pd.read_csv(parent_datasource.file.path)
    columns = df.columns.tolist()

    return render(request, 'data_tools/feature_engineering.html', {
        'form': form,
        'datasource': parent_datasource,
        "columns": columns,
    })