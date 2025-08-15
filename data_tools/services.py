# data_tools/services.py
import pandas as pd
from projects.models.datasource import DataSource, DataSourceType
from django.core.files.base import ContentFile
import io
from projects.models.transformation import Transformation


def perform_data_fusion(project, datasources, merge_col, output_name):
    """
    Toma una lista de DataSources, los fusiona y devuelve el nuevo DataSource creado.
    Si algo falla, devuelve None.
    Esta función NO sabe nada sobre 'request' o 'messages'. Es lógica pura.
    """
    if len(datasources) < 2:
        raise ValueError("Se requieren al menos dos DataSources para la fusión.")
    try:
        df_list = []
        for ds in datasources:
            temp_df = pd.read_csv(ds.file.path, encoding='latin-1')
            if merge_col not in temp_df.columns:
                # En lugar de mostrar un mensaje, devolvemos un error.
                # La vista se encargará de comunicárselo al usuario.
                raise ValueError(f"La columna '{merge_col}' no se encontró en el archivo '{ds.name}'.")
            df_list.append(temp_df)

        merged_df = df_list[0]
        for df_to_merge in df_list[1:]:
            merged_df = pd.merge(merged_df, df_to_merge, on=merge_col, how='outer')

        parquet_buffer = io.BytesIO()
        merged_df.to_parquet(parquet_buffer, index=False)

        new_datasource = DataSource(
            project=project,
            name=output_name,
            description=f"Fusión de {len(datasources)} datasets basada en la columna '{merge_col}'.",
            data_type=DataSourceType.FUSED
        )
        new_file = ContentFile(parquet_buffer.getvalue())
        new_datasource.file.save(f'fused_{project.id}_{pd.Timestamp.now().strftime("%Y%m%d%H%M")}.parquet', new_file)
        new_datasource.parents.add(*datasources)
        new_datasource.save()

        return new_datasource, None  # Devuelve el objeto creado y ningún error

    except Exception as e:
        return None, str(e)  # Devuelve None y el mensaje de error como un string


def perform_feature_engineering(datasource_id, new_column_name, formula_string):
    try:
        # 1. Cargar el DataSource original
        ds = DataSource.objects.get(id=datasource_id)
        df = pd.read_csv(ds.file.path)

        # 2. Crear la nueva columna usando df.eval()
        df[new_column_name] = df.eval(formula_string)

        # 3. Guardar el DataFrame modificado como nuevo DataSource PREPARED
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        new_ds = DataSource.objects.create(
            name=f"{ds.name} + {new_column_name}",
            type=DataSourceType.PREPARED,
            parent=ds,
        )
        new_ds.file.save(f"{new_ds.id}.csv", ContentFile(buffer.getvalue()))
        new_ds.save()

        # 4. Devolver el nuevo DataSource
        return new_ds
    except Exception as e:
        return {"error": str(e)}


def process_datasource_to_df(datasource_id):
    """
    Processes a DataSource into a pandas DataFrame, applying transformations if necessary.

    Args:
        datasource_id (UUID): The ID of the DataSource to process.

    Returns:
        pd.DataFrame: The resulting DataFrame after applying transformations.

    Raises:
        DataSource.DoesNotExist: If no DataSource is found for the given ID.
    """
    # Fetch the DataSource instance
    datasource = DataSource.objects.get(id=datasource_id)

    # Base Case: If the DataSource is not derived, read the file directly
    if not datasource.is_derived:
        if not datasource.file:
            raise ValueError(f"DataSource {datasource_id} does not have an associated file.")
        return pd.read_csv(datasource.file.path)

    # Recursive Case: Process parent DataSources
    parents = datasource.parents.all()
    if not parents.exists():
        raise ValueError(f"Derived DataSource {datasource_id} has no parents.")

    # Process all parents into a list of DataFrames
    df_list = [process_datasource_to_df(parent.id) for parent in parents]

    # Apply transformations in order
    transformations = datasource.transformations.order_by('order')
    df = None
    for transformation in transformations:
        if transformation.operation_type == 'select_columns':
            # Select specific columns
            columns_list = transformation.parameters.get('columns', [])
            df = df[columns_list]
        elif transformation.operation_type == 'filter_rows':
            # Filter rows based on a condition
            column = transformation.parameters.get('column')
            operator = transformation.parameters.get('operator')
            value = transformation.parameters.get('value')

            if operator == '>':
                df = df[df[column] > value]
            else:
                raise NotImplementedError(f"Operator '{operator}' is not implemented.")
        elif transformation.operation_type == 'merge':
            # Merge two DataFrames
            if len(df_list) < 2:
                raise ValueError("Merge operation requires at least two parent DataFrames.")
            
            left_df = df_list[0]
            right_df = df_list[1]
            left_on = transformation.parameters.get('left_on')
            right_on = transformation.parameters.get('right_on')
            how = transformation.parameters.get('how', 'outer')

            # Perform the merge
            merged_df = pd.merge(left_df, right_df, left_on=left_on, right_on=right_on, how=how)
            df = merged_df

    # Return the final DataFrame
    return df


def create_fusion_recipe(project, left_datasource, right_datasource, left_on_col, right_on_col, output_name):
    """
    Creates a new recipe-based fusion DataSource.

    Args:
        project (Project): The project to which the new DataSource belongs.
        left_datasource (DataSource): The left parent DataSource.
        right_datasource (DataSource): The right parent DataSource.
        left_on_col (str): The column to join on from the left DataSource.
        right_on_col (str): The column to join on from the right DataSource.
        output_name (str): The name of the resulting DataSource.

    Returns:
        DataSource: The newly created DataSource.
    """
    try:
        # Step 1: Create a new derived DataSource
        new_datasource = DataSource.objects.create(
            project=project,
            name=output_name,
            description=f"Fusion of {left_datasource.name} and {right_datasource.name}",
            is_derived=True
        )

        # Step 2: Set the parents of the new DataSource
        new_datasource.parents.set([left_datasource, right_datasource])

        # Step 3: Create a 'merge' Transformation for the new DataSource
        Transformation.objects.create(
            derived_datasource=new_datasource,
            order=1,
            operation_type='merge',
            parameters={
                'left_on': left_on_col,
                'right_on': right_on_col,
                'how': 'outer'
            }
        )

        # Step 4: Return the new DataSource
        return new_datasource
    except Exception as e:
        raise ValueError(f"Error creating fusion recipe: {str(e)}")