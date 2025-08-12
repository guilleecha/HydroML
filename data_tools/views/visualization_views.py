# data_tools/views/visualization_views.py
import json
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from projects.models import DataSource


@login_required
def data_viewer_page(request, pk):
    """
    Renderiza la página principal del visor de datos.
    """
    # CAMBIO AQUÍ: de 'project__user' a 'project__owner'
    datasource = get_object_or_404(DataSource, pk=pk, project__owner=request.user)
    context = {
        'datasource': datasource,
    }
    return render(request, 'data_tools/data_viewer.html', context)


@login_required
def get_datasource_json(request, pk):
    """
    Vista de API que devuelve los datos de un DataSource en formato JSON.
    """
    # CAMBIO AQUÍ: de 'project__user' a 'project__owner'
    datasource = get_object_or_404(DataSource, pk=pk, project__owner=request.user)
    try:
        file_path = datasource.file.path

        # ... (resto del código de la vista que ya funcionaba) ...
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=100, encoding='latin-1', engine='python')
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path, nrows=100)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
            if len(df) > 100:
                df = df.head(100)
        else:
            return JsonResponse({'error': 'Formato de archivo no soportado.'}, status=400)

        df = df.fillna('')
        data_json = json.loads(df.to_json(orient='split', index=False))
        return JsonResponse(data_json)

    except Exception as e:
        return JsonResponse({'error': f"Error al leer el archivo: {str(e)}"}, status=500)