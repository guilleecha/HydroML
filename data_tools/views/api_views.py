# data_tools/views/api_views.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

@login_required
def get_fusion_columns_api(request):
    """
    API endpoint que devuelve las columnas de dos DataSources para fusión de datos.
    
    Parámetros GET esperados:
    - ds_a: UUID del primer DataSource
    - ds_b: UUID del segundo DataSource
    
    Retorna:
    JSON con la estructura de columnas para ambos datasources.
    """
    try:
        # Obtener los UUIDs de los parámetros GET
        ds_a_id = request.GET.get('ds_a')
        ds_b_id = request.GET.get('ds_b')
        
        if not ds_a_id or not ds_b_id:
            return JsonResponse({
                'error': 'Se requieren ambos parámetros: ds_a y ds_b'
            }, status=400)
        
        # Validate UUID format
        from uuid import UUID
        try:
            UUID(ds_a_id)
            UUID(ds_b_id)
        except ValueError:
            return JsonResponse({
                'error': 'Los parámetros ds_a y ds_b deben ser UUIDs válidos'
            }, status=400)
        
        # Verificar que ambos datasources existan y pertenezcan al usuario
        try:
            datasource_a = DataSource.objects.get(id=ds_a_id, project__owner=request.user)
        except DataSource.DoesNotExist:
            return JsonResponse({
                'error': f'DataSource A con ID {ds_a_id} no existe o no tienes acceso'
            }, status=404)
            
        try:
            datasource_b = DataSource.objects.get(id=ds_b_id, project__owner=request.user)
        except DataSource.DoesNotExist:
            return JsonResponse({
                'error': f'DataSource B con ID {ds_b_id} no existe o no tienes acceso'
            }, status=404)
        
        # Verificar que ambos datasources estén en estado READY
        if datasource_a.status != DataSource.Status.READY:
            return JsonResponse({
                'error': f'DataSource A "{datasource_a.name}" no está listo (estado: {datasource_a.status})'
            }, status=400)
            
        if datasource_b.status != DataSource.Status.READY:
            return JsonResponse({
                'error': f'DataSource B "{datasource_b.name}" no está listo (estado: {datasource_b.status})'
            }, status=400)
        
        # Leer las columnas de ambos datasources
        df_a = pd.read_parquet(datasource_a.file.path)
        df_b = pd.read_parquet(datasource_b.file.path)
        
        columns_a = df_a.columns.tolist()
        columns_b = df_b.columns.tolist()
        
        # Estructura de respuesta según especificación
        response_data = {
            "datasource_a": {
                "id": str(datasource_a.id),
                "name": datasource_a.name,
                "columns": columns_a
            },
            "datasource_b": {
                "id": str(datasource_b.id),
                "name": datasource_b.name,
                "columns": columns_b
            }
        }
        
        return JsonResponse(response_data)
        
    except DataSource.DoesNotExist:
        return JsonResponse({
            'error': 'Uno o ambos DataSources no existen o no pertenecen a tus proyectos'
        }, status=404)
    except FileNotFoundError:
        return JsonResponse({
            'error': 'Archivo de datos no encontrado para uno de los DataSources'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}'
        }, status=500)

def get_datasource_columns(request, datasource_id):
    try:
        ds = DataSource.objects.get(id=datasource_id)
        df = pd.read_csv(ds.file.path)
        columns = df.columns.tolist()
        return JsonResponse({"columns": columns})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def generate_chart_api(request):
    """
    API endpoint to generate Plotly charts for specific columns.
    
    Expected GET parameters:
    - datasource_id: UUID of the DataSource
    - column_name: Name of the column to chart
    - chart_type: Type of chart ('histogram' or 'boxplot')
    
    Returns:
    JSON with the chart HTML or error message.
    """
    try:
        # Get parameters
        datasource_id = request.GET.get('datasource_id')
        column_name = request.GET.get('column_name')
        chart_type = request.GET.get('chart_type', 'histogram')
        
        if not datasource_id or not column_name:
            return JsonResponse({
                'error': 'Se requieren los parámetros: datasource_id y column_name'
            }, status=400)
        
        # Validate UUID format
        from uuid import UUID
        try:
            UUID(datasource_id)
        except ValueError:
            return JsonResponse({
                'error': 'datasource_id debe ser un UUID válido'
            }, status=400)
        
        # Get DataSource
        try:
            datasource = DataSource.objects.get(id=datasource_id, project__owner=request.user)
        except DataSource.DoesNotExist:
            return JsonResponse({
                'error': f'DataSource con ID {datasource_id} no existe o no tienes acceso'
            }, status=404)
        
        # Verify DataSource is ready
        if datasource.status != DataSource.Status.READY:
            return JsonResponse({
                'error': f'DataSource "{datasource.name}" no está listo (estado: {datasource.status})'
            }, status=400)
        
        # Load the data
        file_path = datasource.file.path
        
        if file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, delimiter=',', encoding='latin-1')
            except pd.errors.ParserError:
                try:
                    df = pd.read_csv(file_path, delimiter=';', encoding='latin-1')
                except pd.errors.ParserError:
                    try:
                        df = pd.read_csv(file_path, delimiter='\t', encoding='latin-1')
                    except pd.errors.ParserError as e:
                        return JsonResponse({'error': f'Error al analizar el archivo CSV: {str(e)}'}, status=400)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            try:
                df = pd.read_parquet(file_path)
            except Exception as e:
                return JsonResponse({'error': f'Error reading file: {str(e)}'}, status=400)
        
        # Check if column exists
        if column_name not in df.columns:
            return JsonResponse({
                'error': f'La columna "{column_name}" no existe en el dataset'
            }, status=400)
        
        # Check if column is numeric
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            return JsonResponse({
                'error': f'La columna "{column_name}" no es numérica'
            }, status=400)
        
        # Remove null values for plotting
        column_data = df[column_name].dropna()
        
        if len(column_data) == 0:
            return JsonResponse({
                'error': f'La columna "{column_name}" no tiene datos válidos'
            }, status=400)
        
        # Generate chart based on type
        if chart_type == 'histogram':
            fig = px.histogram(
                x=column_data,
                nbins=30,
                title=f'Distribución de {column_name}',
                labels={'x': column_name, 'y': 'Frecuencia'}
            )
            fig.update_layout(
                xaxis_title=column_name,
                yaxis_title='Frecuencia',
                template='plotly_white',
                height=400
            )
        elif chart_type == 'boxplot':
            fig = px.box(
                y=column_data,
                title=f'Diagrama de Caja de {column_name}',
                labels={'y': column_name}
            )
            fig.update_layout(
                yaxis_title=column_name,
                template='plotly_white',
                height=400
            )
        else:
            return JsonResponse({
                'error': f'Tipo de gráfico no soportado: {chart_type}'
            }, status=400)
        
        # Convert to HTML
        chart_html = fig.to_html(
            include_plotlyjs=False,  # Don't include plotly.js since it's already loaded
            div_id="plotly-chart",
            config={'responsive': True, 'displayModeBar': True}
        )
        
        return JsonResponse({
            'success': True,
            'chart_html': chart_html,
            'column_name': column_name,
            'chart_type': chart_type,
            'data_points': len(column_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}'
        }, status=500)
