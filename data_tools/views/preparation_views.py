# data_tools/views/preparation_views.py
import json
import io
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from projects.models import DataSource, DataSourceType  # Importamos desde 'projects'
from core.utils.breadcrumbs import create_basic_breadcrumbs

# Feature-engine imports
from feature_engine.imputation import MeanMedianImputer
from feature_engine.encoding import OneHotEncoder
from feature_engine.discretisation import EqualFrequencyDiscretiser


@login_required
def data_preparer_page(request, pk):
    """
    Vista para Data Studio (anteriormente Data Preparer).
    Página unificada para visualizar y preparar datos.
    Maneja la carga inicial (GET) y el procesamiento y guardado (POST).
    """
    datasource = get_object_or_404(DataSource, pk=pk, project__owner=request.user)

    # Construir breadcrumbs usando la utilidad breadcrumbs
    breadcrumbs = create_basic_breadcrumbs(
        ('Workspace', reverse('projects:project_list')),
        (datasource.project.name, reverse('projects:project_detail', kwargs={'pk': datasource.project.pk})),
        (datasource.name, None),  # DataSource name without link
        'Data Studio'  # Current page - no link
    )

    # --- LÓGICA POST: Procesar y guardar un nuevo DataSource preparado ---
    if request.method == 'POST':
        try:
            # Check if this is an AJAX request for feature engineering transformation
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.POST.get('action') == 'apply_transformation':
                return handle_feature_engineering_transformation(request, datasource)
            
            # 1. Leer el dataframe original completo
            file_path = datasource.file.path
            if file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            elif file_path.endswith('.csv'):
                try:
                    df = pd.read_csv(file_path, delimiter=',', encoding='latin-1')
                except pd.errors.ParserError as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'Error parsing CSV file: {str(e)}. Please check the file format and delimiter.'
                    })
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:  # Try Parquet as fallback for other extensions
                try:
                    df = pd.read_parquet(file_path)
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'Unsupported file format. Error: {str(e)}'
                    })

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
        # 1. Read the file correctly based on its extension
        file_path = datasource.file.path
        
        if file_path.endswith('.parquet'):
            # Read Parquet file - get first 50 rows for preview
            df_full = pd.read_parquet(file_path)
            df_head = df_full.head(50)
        elif file_path.endswith('.csv'):
            # Try reading CSV with different delimiters
            try:
                df_head = pd.read_csv(file_path, nrows=50, delimiter=',', encoding='latin-1')
            except pd.errors.ParserError as e:
                # Try with different delimiters if comma fails
                try:
                    df_head = pd.read_csv(file_path, nrows=50, delimiter=';', encoding='latin-1')
                except pd.errors.ParserError:
                    try:
                        df_head = pd.read_csv(file_path, nrows=50, delimiter='\t', encoding='latin-1')
                    except pd.errors.ParserError:
                        raise pd.errors.ParserError(f"Unable to parse CSV file with common delimiters. Original error: {str(e)}")
        elif file_path.endswith(('.xls', '.xlsx')):
            # Read Excel file - get first 50 rows for preview
            df_full = pd.read_excel(file_path)
            df_head = df_full.head(50)
        else:
            # Try to read as Parquet as fallback for other extensions
            try:
                df_full = pd.read_parquet(file_path)
                df_head = df_full.head(50)
            except Exception:
                raise ValueError(f"Unsupported file format: {file_path}")
        
        # 2. Generate column information
        column_info = {}
        for col in df_head.columns:
            column_info[col] = {'pandas_dtype': str(df_head[col].dtype)}

        # 3. Prepare data for AG Grid
        # Convert DataFrame to list of dictionaries for JavaScript
        grid_data = df_head.to_dict('records')
        
        # Convert DataFrame to JSON string for template
        grid_data_json = json.dumps(grid_data, default=str)
        
        # Generate column definitions for AG Grid
        column_defs = []
        for col in df_head.columns:
            col_def = {
                'headerName': col,
                'field': col,
                'sortable': True,
                'filter': True,
                'resizable': True
            }
            
            # Set appropriate cell data type for AG Grid
            dtype = str(df_head[col].dtype)
            if 'int' in dtype or 'float' in dtype:
                col_def['type'] = 'numericColumn'
            elif 'datetime' in dtype:
                col_def['type'] = 'dateColumn'
            else:
                col_def['type'] = 'textColumn'
                
            column_defs.append(col_def)
        
        column_defs_json = json.dumps(column_defs)

        # 4. Generate HTML table from DataFrame (keeping for fallback)
        preview_html = df_head.to_html(
            classes='w-full text-sm',
            table_id='data-preview-table',
            index=False, 
            border=0,
            escape=False
        )
    except Exception as e:
        column_info = {}
        grid_data_json = '[]'
        column_defs_json = '[]'
        preview_html = f"<div class='alert alert-danger'>Error al leer el archivo: {e}</div>"

    context = {
        'datasource': datasource,
        'column_info': column_info,
        'preview_html': preview_html,
        'grid_data_json': grid_data_json,
        'column_defs_json': column_defs_json,
        'breadcrumbs': breadcrumbs
    }
    return render(request, 'data_tools/data_preparer.html', context)


def handle_feature_engineering_transformation(request, datasource):
    """
    Handle feature engineering transformations via AJAX.
    """
    try:
        # 1. Load the original dataframe
        file_path = datasource.file.path
        if file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, delimiter=',', encoding='latin-1')
            except pd.errors.ParserError as e:
                # Try with different delimiters if comma fails
                try:
                    df = pd.read_csv(file_path, delimiter=';', encoding='latin-1')
                except pd.errors.ParserError:
                    try:
                        df = pd.read_csv(file_path, delimiter='\t', encoding='latin-1')
                    except pd.errors.ParserError:
                        return JsonResponse({'success': False, 'error': f'Error al analizar el archivo CSV: {str(e)}'})
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            # Try Parquet as fallback for other extensions
            try:
                df = pd.read_parquet(file_path)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Error reading file: {str(e)}'})
        
        # 2. Get transformation parameters
        transformation_type = request.POST.get('transformation_type')
        
        # 3. Apply the selected transformation
        if transformation_type == 'mean_median_imputer':
            strategy = request.POST.get('strategy', 'mean')
            variables = request.POST.get('variables', '').strip()
            
            # If variables specified, use them; otherwise use all numeric columns
            if variables:
                var_list = [v.strip() for v in variables.split(',') if v.strip()]
                # Filter to only include columns that exist and are numeric
                numeric_cols = df.select_dtypes(include=['number']).columns
                var_list = [v for v in var_list if v in numeric_cols]
            else:
                var_list = None  # Use all numeric columns
            
            # Apply transformation
            imputer = MeanMedianImputer(imputation_method=strategy, variables=var_list)
            df_transformed = imputer.fit_transform(df)
            
            message = f"Applied {strategy} imputation to {len(imputer.variables_)} numeric columns"
            
        elif transformation_type == 'onehot_encoder':
            top_categories = request.POST.get('top_categories')
            drop_last = request.POST.get('drop_last', 'false') == 'true'
            
            # Get categorical columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not categorical_cols:
                return JsonResponse({
                    'success': False,
                    'error': 'No categorical columns found for encoding'
                })
            
            # Configure encoder
            encoder_params = {'drop_last': drop_last}
            if top_categories and top_categories.isdigit():
                encoder_params['top_categories'] = int(top_categories)
            
            encoder = OneHotEncoder(variables=categorical_cols, **encoder_params)
            df_transformed = encoder.fit_transform(df)
            
            message = f"Applied one-hot encoding to {len(categorical_cols)} categorical columns"
            
        elif transformation_type == 'equal_frequency_discretiser':
            bins = int(request.POST.get('bins', 5))
            return_boundaries = request.POST.get('return_boundaries', 'false') == 'true'
            
            # Get numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_cols:
                return JsonResponse({
                    'success': False,
                    'error': 'No numeric columns found for discretization'
                })
            
            discretiser = EqualFrequencyDiscretiser(
                variables=numeric_cols,
                q=bins,
                return_boundaries=return_boundaries
            )
            df_transformed = discretiser.fit_transform(df)
            
            message = f"Applied equal frequency discretization to {len(numeric_cols)} numeric columns with {bins} bins"
            
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown transformation type: {transformation_type}'
            })
        
        # 4. Save the transformed dataframe as a new DataSource
        parquet_buffer = io.BytesIO()
        df_transformed.to_parquet(parquet_buffer, index=False)
        
        # Create transformation description
        transformation_names = {
            'mean_median_imputer': 'Mean/Median Imputation',
            'onehot_encoder': 'One-Hot Encoding',
            'equal_frequency_discretiser': 'Equal Frequency Discretization'
        }
        
        transformation_name = transformation_names.get(transformation_type, transformation_type)
        new_dataset_name = f"{datasource.name} ({transformation_name})"
        
        # 5. Create new DataSource object
        new_datasource = DataSource(
            project=datasource.project,
            name=new_dataset_name,
            description=f"Applied {transformation_name} to '{datasource.name}'. {message}",
            data_type=DataSourceType.PREPARED
        )
        
        new_file = ContentFile(parquet_buffer.getvalue())
        timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        filename = f'fe_{transformation_type}_{datasource.pk}_{timestamp}.parquet'
        new_datasource.file.save(filename, new_file)
        
        # 6. Set lineage
        new_datasource.parents.add(datasource)
        new_datasource.save()
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_datasource_id': str(new_datasource.pk),
            'new_datasource_name': new_datasource.name
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })