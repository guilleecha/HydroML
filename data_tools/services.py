# data_tools/services.py
import pandas as pd
from projects.models.datasource import DataSource, DataSourceType
from django.core.files.base import ContentFile
import io


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