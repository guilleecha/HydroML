# data_tools/views/preparation_views.py
import json
import io
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required

from projects.models import DataSource, DataSourceType  # Importamos desde 'projects'


@login_required
def data_preparer_page(request, pk):
    """
    Vista para la Herramienta de Preparación de Datos.
    Maneja la carga inicial (GET) y el procesamiento y guardado (POST).
    """
    datasource = get_object_or_404(DataSource, pk=pk, project__user=request.user)

    # --- LÓGICA POST: Procesar y guardar un nuevo DataSource preparado ---
    if request.method == 'POST':
        try:
            # 1. Leer el dataframe original completo
            file_path = datasource.file.path
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='latin-1')
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:  # Asumimos parquet o un formato que pandas pueda leer
                df = pd.read_parquet(file_path)

            # 2. Iterar sobre los tipos de datos seleccionados en el formulario
            for key, new_type in request.POST.items():
                if key.startswith('type-'):
                    col_name = key.replace('type-', '')
                    if col_name in df.columns and new_type:
                        # Convertir a numérico de forma segura
                        if 'int' in new_type or 'float' in new_type:
                            df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                        # Convertir a fecha/hora de forma segura
                        elif 'datetime' in new_type:
                            df[col_name] = pd.to_datetime(df[col_name], errors='coerce')
                        # Convertir a otros tipos
                        df[col_name] = df[col_name].astype(new_type)

            # 3. Eliminar las columnas marcadas
            removed_columns_str = request.POST.get('removed_columns', '[]')
            removed_columns = json.loads(removed_columns_str)
            if removed_columns:
                df.drop(columns=removed_columns, inplace=True, errors='ignore')

            # 4. Guardar el nuevo dataframe en formato Parquet (eficiente)
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, index=False)

            new_dataset_name = request.POST.get('new_dataset_name', f"{datasource.name} (Preparado)")

            # 5. Crear el nuevo objeto DataSource en la base de datos
            new_datasource = DataSource(
                project=datasource.project,
                name=new_dataset_name,
                description=f"Versión preparada de '{datasource.name}'.",
                data_type=DataSourceType.PREPARED  # Marcamos el tipo de dato
            )
            new_file = ContentFile(parquet_buffer.getvalue())
            # Guardamos con un nombre único para evitar colisiones
            new_datasource.file.save(f'prepared_{datasource.pk}_{pd.Timestamp.now().strftime("%Y%m%d%H%M%S")}.parquet',
                                     new_file)

            # 6. Establecer el linaje: el original es el padre del nuevo
            new_datasource.parents.add(datasource)
            new_datasource.save()

            return redirect('projects:project_detail', pk=datasource.project.id)
        except Exception as e:
            # Manejar el error, quizás mostrando un mensaje al usuario
            # (Por ahora lo dejamos simple)
            pass

            # --- LÓGICA GET: Mostrar la página de preparación ---
    try:
        df_head = pd.read_csv(datasource.file.path, nrows=50, encoding='latin-1')
        column_info = {}
        for col in df_head.columns:
            column_info[col] = {'pandas_dtype': str(df_head[col].dtype)}

        # Pasamos las primeras 50 filas como HTML a la plantilla
        preview_html = df_head.to_html(classes='table table-bordered table-sm', index=False, border=0)
    except Exception as e:
        column_info = {}
        preview_html = f"<div class='alert alert-danger'>Error al leer el archivo: {e}</div>"

    context = {
        'datasource': datasource,
        'column_info': column_info,
        'preview_html': preview_html
    }
    return render(request, 'data_tools/data_preparer.html', context)