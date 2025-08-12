# data_tools/services.py
import pandas as pd
import io
from django.core.files.base import ContentFile
from projects.models import DataSource, DataSourceType


def perform_data_fusion(project, datasources, merge_col, output_name):
    """
    Toma una lista de DataSources, los fusiona y devuelve el nuevo DataSource creado.
    Si algo falla, devuelve None.
    Esta función NO sabe nada sobre 'request' o 'messages'. Es lógica pura.
    """
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