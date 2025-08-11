# data_tools/views/visualization_views.py
import json
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from projects.models import DataSource  # Importamos el modelo desde la app 'projects'


@login_required
def data_viewer_page(request, pk):
    """
    Renderiza la página principal del visor de datos, que luego
    hará una llamada a la API para cargar los datos de forma asíncrona.
    """
    # Se asegura de que el datasource exista y pertenezca al usuario logueado
    datasource = get_object_or_404(DataSource, pk=pk, project__user=request.user)
    context = {
        'datasource': datasource,
    }
    return render(request, 'data_tools/data_viewer.html', context)


@login_required
def get_datasource_json(request, pk):
    """
    Vista de API: Lee una muestra de un archivo DataSource (las primeras 100 filas)
    y la devuelve en formato JSON para que sea consumida por el frontend.
    """
    datasource = get_object_or_404(DataSource, pk=pk, project__user=request.user)
    try:
        file_path = datasource.file.path

        # Leemos solo las primeras 100 filas para una carga rápida
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=100, encoding='latin-1', engine='python')
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path, nrows=100)
        elif file_path.endswith('.parquet'):
            # Para parquet, leemos todo y luego tomamos la cabecera
            df = pd.read_parquet(file_path)
            if len(df) > 100:
                df = df.head(100)
        else:
            return JsonResponse({'error': 'Formato de archivo no soportado.'}, status=400)

        # Reemplazamos valores NaN (Not a Number) por strings vacíos para evitar errores en JSON
        df = df.fillna('')

        # Convertimos el DataFrame a un formato JSON que es fácil de usar en JavaScript
        data_json = json.loads(df.to_json(orient='split', index=False))
        return JsonResponse(data_json)

    except Exception as e:
        # Devolvemos un error claro al frontend si algo sale mal
        return JsonResponse({'error': f"Error al leer el archivo: {str(e)}"}, status=500)