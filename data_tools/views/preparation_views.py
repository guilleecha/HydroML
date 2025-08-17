# data_tools/views/preparation_views.py
import json
import io
import pandas as pd
import numpy as np
import missingno as msno
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import base64
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

            # 4. Preparar el paso de la receta para guardar
            recipe_step = {
                'action_type': 'data_preparation',
                'action_name': 'Data Type Conversion & Column Removal',
                'timestamp': pd.Timestamp.now().isoformat(),
                'details': {
                    'type_conversions': {key.replace('type-', ''): new_type 
                                       for key, new_type in request.POST.items() 
                                       if key.startswith('type-') and new_type},
                    'removed_columns': removed_columns
                }
            }

            # 5. Guardar el nuevo dataframe en formato Parquet (eficiente)
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, index=False)

            new_dataset_name = request.POST.get('new_dataset_name', f"{datasource.name} (Preparado)")

            # 6. Crear el nuevo objeto DataSource en la base de datos
            new_datasource = DataSource(
                project=datasource.project,
                name=new_dataset_name,
                description=f"Versión preparada de '{datasource.name}'.",
                data_type=DataSourceType.PREPARED  # Marcamos el tipo de dato
            )
            
            # 7. Copiar recipe_steps del padre y agregar el nuevo paso
            new_recipe_steps = list(datasource.recipe_steps or [])  # Copiar pasos existentes
            new_recipe_steps.append(recipe_step)  # Agregar el nuevo paso
            new_datasource.recipe_steps = new_recipe_steps
            
            new_file = ContentFile(parquet_buffer.getvalue())
            # Guardamos con un nombre único para evitar colisiones
            new_datasource.file.save(f'prepared_{datasource.pk}_{pd.Timestamp.now().strftime("%Y%m%d%H%M%S")}.parquet',
                                     new_file)

            # 8. Establecer el linaje: el original es el padre del nuevo
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
        
        # 5. Calculate nullity report for Missing Data Toolkit
        nullity_report = calculate_nullity_report(df_full if 'df_full' in locals() else df_head)
        
    except Exception as e:
        column_info = {}
        grid_data_json = '[]'
        column_defs_json = '[]'
        preview_html = f"<div class='alert alert-danger'>Error al leer el archivo: {e}</div>"
        nullity_report = None

    context = {
        'datasource': datasource,
        'column_info': column_info,
        'preview_html': preview_html,
        'grid_data_json': grid_data_json,
        'column_defs_json': column_defs_json,
        'breadcrumbs': breadcrumbs,
        'recipe_steps': datasource.recipe_steps,  # Pass recipe steps to template
        'nullity_report': nullity_report,  # Pass nullity report for Missing Data Toolkit
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
        
        # Create recipe step for this transformation
        recipe_step = {
            'action_type': 'feature_engineering',
            'action_name': transformation_name,
            'timestamp': pd.Timestamp.now().isoformat(),
            'details': {
                'transformation_type': transformation_type,
                'parameters': dict(request.POST),
                'description': message
            }
        }

        # 5. Create new DataSource object
        new_datasource = DataSource(
            project=datasource.project,
            name=new_dataset_name,
            description=f"Applied {transformation_name} to '{datasource.name}'. {message}",
            data_type=DataSourceType.PREPARED
        )
        
        # Copy recipe_steps from parent and add new step
        new_recipe_steps = list(datasource.recipe_steps or [])  # Copy existing steps
        new_recipe_steps.append(recipe_step)  # Add the new step
        new_datasource.recipe_steps = new_recipe_steps
        
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


def calculate_nullity_report(df):
    """
    Calculate comprehensive nullity report for the Missing Data Toolkit.
    
    Returns:
        dict: Nullity report with statistics and visualizations
    """
    try:
        if df is None or df.empty:
            return None
        
        # Basic missing data statistics
        total_rows = len(df)
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Per-column missing data
        column_nullity = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            column_nullity[col] = {
                'missing_count': int(missing_count),
                'missing_percentage': float(missing_count / total_rows * 100) if total_rows > 0 else 0,
                'complete_count': int(total_rows - missing_count),
                'data_type': str(df[col].dtype)
            }
        
        # Missing patterns (simplified)
        missing_pattern_counts = {}
        missing_df = df.isnull()
        
        # Get most common missing patterns (top 10)
        pattern_counts = missing_df.value_counts().head(10)
        for pattern, count in pattern_counts.items():
            # Create pattern description
            missing_cols = [col for col, is_missing in zip(df.columns, pattern) if is_missing]
            pattern_key = f"Missing: {', '.join(missing_cols)}" if missing_cols else "Complete"
            missing_pattern_counts[pattern_key] = int(count)
        
        # Complete rows count
        complete_rows = df.dropna().shape[0]
        
        # Data quality summary
        data_quality = {
            'completeness_score': float((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0,
            'columns_with_missing': int(sum(1 for col in df.columns if df[col].isnull().any())),
            'columns_completely_missing': int(sum(1 for col in df.columns if df[col].isnull().all())),
            'rows_with_missing': int(df.isnull().any(axis=1).sum()),
            'rows_completely_missing': int(df.isnull().all(axis=1).sum())
        }
        
        # Generate visualization data for charts
        visualization_data = generate_nullity_visualizations(df)
        
        nullity_report = {
            'summary': {
                'total_rows': total_rows,
                'total_columns': len(df.columns),
                'total_cells': total_cells,
                'missing_cells': int(missing_cells),
                'missing_percentage': round(missing_percentage, 2),
                'complete_rows': int(complete_rows),
                'complete_rows_percentage': round((complete_rows / total_rows * 100) if total_rows > 0 else 0, 2)
            },
            'column_analysis': column_nullity,
            'missing_patterns': missing_pattern_counts,
            'data_quality': data_quality,
            'visualizations': visualization_data,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return nullity_report
        
    except Exception as e:
        # Return minimal report on error
        return {
            'summary': {
                'total_rows': len(df) if df is not None else 0,
                'total_columns': len(df.columns) if df is not None else 0,
                'error': str(e)
            },
            'timestamp': pd.Timestamp.now().isoformat()
        }


def generate_nullity_visualizations(df):
    """
    Generate visualization data for nullity patterns.
    
    Returns:
        dict: Visualization data for charts
    """
    try:
        # Prepare data for missing data bar chart
        missing_counts = df.isnull().sum().sort_values(ascending=False)
        
        # Top 20 columns with missing data
        top_missing = missing_counts[missing_counts > 0].head(20)
        
        bar_chart_data = {
            'labels': list(top_missing.index),
            'values': [int(x) for x in top_missing.values],
            'percentages': [round(x / len(df) * 100, 1) for x in top_missing.values]
        }
        
        # Data completeness matrix (for heatmap-style visualization)
        # Sample a subset for performance
        sample_size = min(1000, len(df))
        df_sample = df.sample(n=sample_size, random_state=42) if len(df) > sample_size else df
        
        # Create matrix data (rows are samples, columns are variables)
        matrix_data = []
        for idx, row in df_sample.iterrows():
            row_data = []
            for col in df.columns:
                row_data.append(0 if pd.isnull(row[col]) else 1)  # 0 = missing, 1 = present
            matrix_data.append(row_data)
        
        heatmap_data = {
            'columns': list(df.columns),
            'matrix': matrix_data,
            'sample_size': sample_size,
            'total_rows': len(df)
        }
        
        # Missing data correlation (which variables tend to be missing together)
        missing_corr = df.isnull().corr()
        
        # Convert correlation matrix to format suitable for frontend
        correlation_data = []
        for i, col1 in enumerate(missing_corr.columns):
            for j, col2 in enumerate(missing_corr.columns):
                if i <= j:  # Only upper triangle to avoid duplicates
                    corr_value = missing_corr.iloc[i, j]
                    if not pd.isna(corr_value) and corr_value != 1.0:  # Exclude self-correlation
                        correlation_data.append({
                            'variable1': col1,
                            'variable2': col2,
                            'correlation': round(float(corr_value), 3)
                        })
        
        # Sort by correlation strength
        correlation_data.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            'bar_chart': bar_chart_data,
            'heatmap': heatmap_data,
            'correlations': correlation_data[:50]  # Top 50 correlations
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'bar_chart': {'labels': [], 'values': [], 'percentages': []},
            'heatmap': {'columns': [], 'matrix': [], 'sample_size': 0},
            'correlations': []
        }