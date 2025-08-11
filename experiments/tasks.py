# experiments/tasks.py

import pandas as pd
import io
from celery import shared_task
from functools import reduce
from django.core.files.base import ContentFile
from .models import Experiment, FusedData
from projects.models import DataSource

@shared_task
def process_data_fusion_task(experiment_id):
    """
    Tarea de Celery para procesar la fusión de datos en segundo plano.
    Guarda el resultado en formato Parquet y calcula un resumen estadístico.
    """
    experiment = None
    try:
        experiment = Experiment.objects.get(id=experiment_id)
        experiment.status = Experiment.StatusChoices.PROCESSING
        experiment.save()

        datasources = experiment.datasources.all()
        merge_key = experiment.merge_key

        if not datasources:
            raise ValueError("No se seleccionaron fuentes de datos para el experimento.")

        dataframes = []
        for ds in datasources:
            file_path = ds.file.path
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                print(f"Formato de archivo no soportado y omitido: {file_path}")
                continue

            if merge_key not in df.columns:
                raise ValueError(f"La columna de fusión '{merge_key}' no se encontró en el archivo '{ds.name}'.")

            dataframes.append(df)

        if not dataframes:
            raise ValueError("No se pudieron cargar DataFrames desde las fuentes de datos.")

        merged_df = reduce(lambda left, right: pd.merge(left, right, on=merge_key, how='outer'), dataframes)

        # --- PASO 1: CALCULAR EL RESUMEN ESTADÍSTICO (Sin cambios) ---
        numeric_df = merged_df.select_dtypes(include=['number'])
        summary_df = numeric_df.describe()
        summary_json = summary_df.to_dict(orient="index")

        # --- PASO 2: GUARDAR EL ARCHIVO PARQUET Y EL RESUMEN ---
        # Usamos BytesIO para Parquet porque maneja datos binarios, no texto.
        parquet_buffer = io.BytesIO()
        # Guardamos el DataFrame en el buffer en formato Parquet.
        merged_df.to_parquet(parquet_buffer, index=False)

        # Creamos la instancia de FusedData y guardamos el resumen.
        fused_data = FusedData(
            experiment=experiment,
            summary=summary_json
        )

        # ContentFile puede manejar el buffer de bytes directamente.
        fused_file = ContentFile(parquet_buffer.getvalue())
        # Cambiamos la extensión del archivo a .parquet.
        fused_data.fused_file.save(f'fused_data_{experiment.id}.parquet', fused_file)
        fused_data.save()

        experiment.status = Experiment.StatusChoices.COMPLETE
        print(f"Experimento {experiment.id} completado exitosamente (Parquet).")



    except Exception as e:
        print(f"Error procesando el experimento {experiment_id}: {e}")
        if experiment:
            experiment.status = Experiment.StatusChoices.FAILED
            experiment.error_message = str(e)

    finally:
        if experiment:
            experiment.save()