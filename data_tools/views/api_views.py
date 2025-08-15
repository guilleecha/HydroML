# data_tools/views/api_views.py
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from projects.models.datasource import DataSource

@login_required
def get_columns_api(request, datasource_id):
    """
    API endpoint que devuelve las columnas de un DataSource específico.
    """
    try:
        # Asegurarse de que el datasource pertenece al proyecto del usuario
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        
        # Leer solo la cabecera del archivo para obtener las columnas rápidamente
        file_path = datasource.file.path
        
        # All files are now converted to Parquet format
        df = pd.read_parquet(file_path)
        columns = df.columns.tolist()
        
        return JsonResponse({'columns': columns})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_datasource_columns(request, datasource_id):
    try:
        ds = DataSource.objects.get(id=datasource_id)
        df = pd.read_csv(ds.file.path)
        columns = df.columns.tolist()
        return JsonResponse({"columns": columns})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
