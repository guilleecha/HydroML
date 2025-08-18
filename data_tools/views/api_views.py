# data_tools/views/api_views.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from projects.models.datasource import DataSource
from data_tools.models import QueryHistory

@login_required
def get_columns_api(request, datasource_id):
    """
    API endpoint que devuelve las columnas de un DataSource específico.
    Soporta múltiples formatos de archivo: CSV, Parquet, Excel.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔧 [BACKEND DEBUG] get_columns_api called with datasource_id: {datasource_id}")
    logger.info(f"👤 [BACKEND DEBUG] Request user: {request.user}")
    logger.info(f"🌐 [BACKEND DEBUG] Request method: {request.method}")
    logger.info(f"📋 [BACKEND DEBUG] Request META: {dict(request.META)}")
    
    try:
        logger.info(f"🔍 [BACKEND DEBUG] Searching for DataSource with ID: {datasource_id}")
        logger.info(f"🔍 [BACKEND DEBUG] DataSource ID type: {type(datasource_id)}")
        
        # Asegurarse de que el datasource pertenece al proyecto del usuario
        datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
        logger.info(f"✅ [BACKEND DEBUG] DataSource found: {datasource}")
        logger.info(f"📋 [BACKEND DEBUG] DataSource name: {datasource.name}")
        logger.info(f"📋 [BACKEND DEBUG] DataSource status: {datasource.status}")
        logger.info(f"📋 [BACKEND DEBUG] DataSource project: {datasource.project}")
        logger.info(f"📋 [BACKEND DEBUG] DataSource file: {datasource.file}")
        
        # Verificar que el DataSource esté listo
        logger.info(f"🔍 [BACKEND DEBUG] Checking DataSource status...")
        if datasource.status != DataSource.Status.READY:
            error_msg = f'DataSource "{datasource.name}" no está listo (estado: {datasource.status})'
            logger.error(f"❌ [BACKEND DEBUG] Status check failed: {error_msg}")
            return JsonResponse({
                'error': error_msg
            }, status=400)
        logger.info(f"✅ [BACKEND DEBUG] DataSource status is READY")
        
        # Verificar que el DataSource tiene un archivo asociado
        logger.info(f"🔍 [BACKEND DEBUG] Checking if DataSource has file...")
        if not datasource.file:
            error_msg = f'DataSource "{datasource.name}" no tiene archivo asociado'
            logger.error(f"❌ [BACKEND DEBUG] File check failed: {error_msg}")
            return JsonResponse({
                'error': error_msg
            }, status=400)
        logger.info(f"✅ [BACKEND DEBUG] DataSource has file: {datasource.file}")
        
    # Leer el archivo con soporte para múltiples formatos
    import os
    file_path = datasource.file.path
    logger.info(f"📁 [BACKEND DEBUG] File path: {file_path}")
        logger.info(f"📁 [BACKEND DEBUG] File exists: {os.path.exists(file_path)}")
        logger.info(f"📁 [BACKEND DEBUG] File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")
        
        # Detectar formato de archivo y leer apropiadamente
        logger.info(f"📁 [BACKEND DEBUG] Detecting file format...")
        df = None
        
        if file_path.endswith('.parquet'):
            logger.info(f"📁 [BACKEND DEBUG] Reading as Parquet file...")
            df = pd.read_parquet(file_path)
            logger.info(f"✅ [BACKEND DEBUG] Parquet file read successfully")
        elif file_path.endswith('.csv'):
            logger.info(f"📁 [BACKEND DEBUG] Reading as CSV file...")
            try:
                logger.info(f"📁 [BACKEND DEBUG] Trying comma delimiter with latin-1 encoding...")
                df = pd.read_csv(file_path, delimiter=',', encoding='latin-1')
                logger.info(f"✅ [BACKEND DEBUG] CSV read with comma delimiter")
            except pd.errors.ParserError as e:
                logger.warning(f"⚠️ [BACKEND DEBUG] Comma delimiter failed: {e}")
                try:
                    logger.info(f"📁 [BACKEND DEBUG] Trying semicolon delimiter...")
                    df = pd.read_csv(file_path, delimiter=';', encoding='latin-1')
                    logger.info(f"✅ [BACKEND DEBUG] CSV read with semicolon delimiter")
                except pd.errors.ParserError as e:
                    logger.warning(f"⚠️ [BACKEND DEBUG] Semicolon delimiter failed: {e}")
                    try:
                        logger.info(f"📁 [BACKEND DEBUG] Trying tab delimiter...")
                        df = pd.read_csv(file_path, delimiter='\t', encoding='latin-1')
                        logger.info(f"✅ [BACKEND DEBUG] CSV read with tab delimiter")
                    except pd.errors.ParserError as e:
                        logger.error(f"❌ [BACKEND DEBUG] All CSV delimiter attempts failed: {e}")
                        return JsonResponse({'error': f'Error al analizar el archivo CSV: {str(e)}'}, status=400)
        elif file_path.endswith(('.xls', '.xlsx')):
            logger.info(f"📁 [BACKEND DEBUG] Reading as Excel file...")
            df = pd.read_excel(file_path)
            logger.info(f"✅ [BACKEND DEBUG] Excel file read successfully")
        else:
            logger.info(f"📁 [BACKEND DEBUG] Unknown format, trying Parquet as fallback...")
            try:
                df = pd.read_parquet(file_path)
                logger.info(f"✅ [BACKEND DEBUG] Fallback Parquet read successful")
            except Exception as e:
                logger.error(f"❌ [BACKEND DEBUG] Fallback Parquet read failed: {e}")
                return JsonResponse({'error': f'Formato de archivo no soportado: {file_path}'}, status=400)
        
        logger.info(f"📊 [BACKEND DEBUG] DataFrame loaded successfully")
        logger.info(f"📊 [BACKEND DEBUG] DataFrame shape: {df.shape}")
        logger.info(f"📊 [BACKEND DEBUG] DataFrame columns count: {len(df.columns)}")
        
        columns = df.columns.tolist()
        logger.info(f"📋 [BACKEND DEBUG] Extracted columns: {columns}")
        logger.info(f"📋 [BACKEND DEBUG] Columns type: {type(columns)}")
        logger.info(f"📋 [BACKEND DEBUG] First 5 columns: {columns[:5] if len(columns) > 5 else columns}")
        
        response_data = {'columns': columns}
        logger.info(f"📤 [BACKEND DEBUG] Preparing response: {response_data}")
        logger.info(f"✅ [BACKEND DEBUG] API call completed successfully")
        
        return JsonResponse(response_data)
        
    except DataSource.DoesNotExist:
        error_msg = f"DataSource with ID {datasource_id} not found or access denied"
        logger.error(f"❌ [BACKEND DEBUG] DataSource.DoesNotExist: {error_msg}")
        return JsonResponse({'error': error_msg}, status=404)
    except Exception as e:
        logger.error(f"❌ [BACKEND DEBUG] Unexpected error: {str(e)}")
        logger.error(f"❌ [BACKEND DEBUG] Error type: {type(e)}")
        logger.error(f"❌ [BACKEND DEBUG] Error args: {e.args}")
        import traceback
        logger.error(f"❌ [BACKEND DEBUG] Full traceback: {traceback.format_exc()}")
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
    - column_name: Name of the column to chart (for single-column charts)
    - x_column: Name of X-axis column (for scatter plots)
    - y_column: Name of Y-axis column (for scatter plots)
    - chart_type: Type of chart ('histogram', 'boxplot', or 'scatter')
    
    Returns:
    JSON with the chart HTML or error message.
    """
    try:
        # Get parameters
        datasource_id = request.GET.get('datasource_id')
        column_name = request.GET.get('column_name')
        x_column = request.GET.get('x_column')
        y_column = request.GET.get('y_column')
        chart_type = request.GET.get('chart_type', 'histogram')
        
        # Validate parameters based on chart type
        if chart_type == 'scatter':
            if not datasource_id or not x_column or not y_column:
                return JsonResponse({
                    'error': 'Para gráficos de dispersión se requieren: datasource_id, x_column y y_column'
                }, status=400)
        else:
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
        
        # Handle column validation based on chart type
        if chart_type == 'scatter':
            # Validate both X and Y columns for scatter plots
            if x_column not in df.columns:
                return JsonResponse({
                    'error': f'La columna X "{x_column}" no existe en el dataset'
                }, status=400)
            
            if y_column not in df.columns:
                return JsonResponse({
                    'error': f'La columna Y "{y_column}" no existe en el dataset'
                }, status=400)
            
            # Check if both columns are numeric
            if not pd.api.types.is_numeric_dtype(df[x_column]):
                return JsonResponse({
                    'error': f'La columna X "{x_column}" no es numérica'
                }, status=400)
            
            if not pd.api.types.is_numeric_dtype(df[y_column]):
                return JsonResponse({
                    'error': f'La columna Y "{y_column}" no es numérica'
                }, status=400)
            
            # Remove rows with null values in either column
            plot_data = df[[x_column, y_column]].dropna()
            
            if len(plot_data) == 0:
                return JsonResponse({
                    'error': f'No hay datos válidos para las columnas "{x_column}" y "{y_column}"'
                }, status=400)
                
        else:
            # Single column validation for histogram and boxplot
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
        elif chart_type == 'scatter':
            fig = px.scatter(
                x=plot_data[x_column],
                y=plot_data[y_column],
                title=f'Diagrama de Dispersión: {x_column} vs {y_column}',
                labels={'x': x_column, 'y': y_column}
            )
            fig.update_layout(
                xaxis_title=x_column,
                yaxis_title=y_column,
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
        
        # Prepare response data
        response_data = {
            'success': True,
            'chart_html': chart_html,
            'chart_type': chart_type,
        }
        
        # Add appropriate metadata based on chart type
        if chart_type == 'scatter':
            response_data.update({
                'x_column': x_column,
                'y_column': y_column,
                'data_points': len(plot_data)
            })
        else:
            response_data.update({
                'column_name': column_name,
                'data_points': len(column_data)
            })
        
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}'
        }, status=500)


@login_required
def execute_sql_api(request):
    """
    API endpoint para ejecutar consultas SQL sobre pandas DataFrames usando pandasql.
    
    Expected POST parameters:
    - datasource_id: UUID of the DataSource
    - sql_query: SQL query string to execute
    
    Returns:
    JSON with the query results or error message.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo se permiten peticiones POST'}, status=405)
    
    try:
        import json
        from pandasql import sqldf
        
        # Parse request body
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
        
        # Get parameters
        datasource_id = body.get('datasource_id')
        sql_query = body.get('sql_query')
        
        if not datasource_id or not sql_query:
            return JsonResponse({
                'error': 'Se requieren los parámetros: datasource_id y sql_query'
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
        
        # Verify DataSource has an associated file
        if not datasource.file:
            return JsonResponse({
                'error': f'DataSource "{datasource.name}" no tiene archivo asociado'
            }, status=400)
        
        # Load the data
        file_path = datasource.file.path
        
        # Read file based on format
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
        
        # Basic validation for SQL query
        sql_query_clean = sql_query.strip()
        if not sql_query_clean:
            return JsonResponse({'error': 'La consulta SQL no puede estar vacía'}, status=400)
        
        # Security check: prevent dangerous SQL operations
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'TRUNCATE']
        sql_upper = sql_query_clean.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return JsonResponse({
                    'error': f'Operación SQL no permitida: {keyword}. Solo se permiten consultas SELECT.'
                }, status=400)
        
        # Execute SQL query using pandasql
        start_time = time.time()
        try:
            # Make the DataFrame available as 'df' in the local scope for sqldf
            result_df = sqldf(sql_query_clean, locals())
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            if result_df is None or result_df.empty:
                # Save successful query to history (even if no results)
                QueryHistory.objects.create(
                    user=request.user,
                    datasource=datasource,
                    sql_query=sql_query_clean,
                    rows_returned=0,
                    execution_time_ms=execution_time_ms,
                    was_successful=True
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Consulta ejecutada exitosamente, pero no retornó resultados',
                    'data': [],
                    'rows_returned': 0,
                    'columns': []
                })
            
            # Convert result to JSON format
            result_json = result_df.to_dict(orient='records')
            
            # Get column names and basic statistics
            columns = result_df.columns.tolist()
            rows_returned = len(result_df)
            
            # Basic data type info for columns
            column_info = []
            for col in columns:
                dtype_str = str(result_df[col].dtype)
                null_count = result_df[col].isnull().sum()
                column_info.append({
                    'name': col,
                    'dtype': dtype_str,
                    'null_count': int(null_count)
                })
            
            # Save successful query to history
            QueryHistory.objects.create(
                user=request.user,
                datasource=datasource,
                sql_query=sql_query_clean,
                rows_returned=rows_returned,
                execution_time_ms=execution_time_ms,
                was_successful=True
            )
            
            return JsonResponse({
                'success': True,
                'data': result_json,
                'rows_returned': rows_returned,
                'columns': columns,
                'column_info': column_info,
                'message': f'Consulta ejecutada exitosamente. {rows_returned} filas retornadas.'
            })
            
        except Exception as sql_error:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Save failed query to history
            QueryHistory.objects.create(
                user=request.user,
                datasource=datasource,
                sql_query=sql_query_clean,
                rows_returned=None,
                execution_time_ms=execution_time_ms,
                was_successful=False
            )
            
            # Handle SQL execution errors gracefully
            error_message = str(sql_error)
            
            # Provide more user-friendly error messages for common issues
            if 'no such table' in error_message.lower():
                return JsonResponse({
                    'error': f'Tabla no encontrada. Use "df" como nombre de la tabla en su consulta SQL. Error: {error_message}'
                }, status=400)
            elif 'syntax error' in error_message.lower():
                return JsonResponse({
                    'error': f'Error de sintaxis en la consulta SQL: {error_message}'
                }, status=400)
            elif 'no such column' in error_message.lower():
                available_columns = df.columns.tolist()
                return JsonResponse({
                    'error': f'Columna no encontrada. Columnas disponibles: {", ".join(available_columns)}. Error: {error_message}'
                }, status=400)
            else:
                return JsonResponse({
                    'error': f'Error al ejecutar la consulta SQL: {error_message}'
                }, status=400)
        
    except ImportError:
        return JsonResponse({
            'error': 'La librería pandasql no está instalada. Contacte al administrador del sistema.'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}'
        }, status=500)


@login_required
def get_query_history_api(request):
    """
    API endpoint para obtener el historial de consultas SQL del usuario.
    
    Expected GET parameters:
    - datasource_id: (Optional) UUID of the DataSource to filter by
    - limit: (Optional) Maximum number of queries to return (default: 20)
    - successful_only: (Optional) If true, only return successful queries (default: false)
    
    Returns:
    JSON with the query history data.
    """
    try:
        # Get parameters
        datasource_id = request.GET.get('datasource_id')
        limit = int(request.GET.get('limit', 20))
        successful_only = request.GET.get('successful_only', 'false').lower() == 'true'
        
        # Validate limit
        if limit < 1 or limit > 100:
            return JsonResponse({
                'error': 'El parámetro limit debe estar entre 1 y 100'
            }, status=400)
        
        # Start with user's queries
        queryset = QueryHistory.objects.filter(user=request.user)
        
        # Filter by datasource if provided
        if datasource_id:
            from uuid import UUID
            try:
                UUID(datasource_id)
                # Verify the user has access to this datasource
                try:
                    datasource = DataSource.objects.get(id=datasource_id, project__owner=request.user)
                    queryset = queryset.filter(datasource=datasource)
                except DataSource.DoesNotExist:
                    return JsonResponse({
                        'error': f'DataSource con ID {datasource_id} no existe o no tienes acceso'
                    }, status=404)
            except ValueError:
                return JsonResponse({
                    'error': 'datasource_id debe ser un UUID válido'
                }, status=400)
        
        # Filter by success status if requested
        if successful_only:
            queryset = queryset.filter(was_successful=True)
        
        # Order by most recent first and apply limit
        queryset = queryset.order_by('-timestamp')[:limit]
        
        # Convert to list of dictionaries
        history_data = []
        for query in queryset:
            history_data.append({
                'id': str(query.id),
                'sql_query': query.sql_query,
                'query_preview': query.query_preview,
                'datasource_id': str(query.datasource.id),
                'datasource_name': query.datasource.name,
                'timestamp': query.timestamp.isoformat(),
                'rows_returned': query.rows_returned,
                'execution_time_ms': query.execution_time_ms,
                'was_successful': query.was_successful
            })
        
        return JsonResponse({
            'success': True,
            'history': history_data,
            'total_queries': len(history_data),
            'filtered_by_datasource': datasource_id is not None,
            'successful_only': successful_only
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}'
        }, status=500)
