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
        try:
            # All files are now converted to Parquet format
            df = pd.read_parquet(file_path)
            if len(df) > 100:
                df = df.head(100)
        except pd.errors.ParserError as e:
            return JsonResponse({'error': f"Error al analizar el archivo: {str(e)}"}, status=400)

        df = df.fillna('')
        data_json = json.loads(df.to_json(orient='split', index=False))
        return JsonResponse(data_json)

    except Exception as e:
        return JsonResponse({'error': f"Error al leer el archivo: {str(e)}"}, status=500)