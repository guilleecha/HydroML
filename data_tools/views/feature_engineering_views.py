from django.shortcuts import render, redirect
from django.contrib import messages
from projects.models.datasource import DataSource
from data_tools.services import perform_feature_engineering
import pandas as pd

def feature_engineering_page(request, datasource_id):
    ds = DataSource.objects.get(id=datasource_id)
    df = pd.read_csv(ds.file.path)
    columns = df.columns.tolist()

    if request.method == "POST":
        new_column_name = request.POST.get("new_column_name")
        formula_string = request.POST.get("formula_string")
        result = perform_feature_engineering(datasource_id, new_column_name, formula_string)
        if isinstance(result, dict) and "error" in result:
            messages.error(request, f"Error: {result['error']}")
        else:
            messages.success(request, f"Columna '{new_column_name}' creada exitosamente.")
            return redirect("data_tools:feature_engineering_page", datasource_id=datasource_id)
    return render(request, "data_tools/feature_engineering_page.html", {
        "datasource": ds,
        "columns": columns,
    })