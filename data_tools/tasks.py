import os
import pandas as pd
from celery import shared_task
from .services import process_datasource_to_df
from projects.models import DataSource
import logging

logger = logging.getLogger(__name__)


@shared_task
def convert_file_to_parquet_task(datasource_id):
    """
    Convierte un archivo subido a formato Parquet en background.
    """
    # Fetch the DataSource object
    datasource = DataSource.objects.get(id=datasource_id)

    # mark as processing
    datasource.status = DataSource.Status.PROCESSING
    datasource.save()

    try:
        # Get the path to the originally uploaded file
        original_file_path = datasource.file.path

        # Read the original file into a pandas DataFrame with automatic delimiter detection
        df = pd.read_csv(original_file_path, sep=None, engine='python', encoding='latin-1')

        # Build a quality report
        quality_report = {
            'shape': df.shape,
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.apply(lambda dt: str(dt)).to_dict(),
        }

        # Save the quality report to the datasource
        datasource.quality_report = quality_report
        datasource.save()

        # Define a new file path for the Parquet file
        base_path = os.path.splitext(original_file_path)[0]
        new_parquet_path = f"{base_path}.parquet"

        # Save the DataFrame to the new path
        df.to_parquet(new_parquet_path)

        # Update the DataSource object's file field to point to the new Parquet file
        # Get the relative path from media root
        media_root = datasource.file.storage.location
        relative_path = os.path.relpath(new_parquet_path, media_root)
        datasource.file.name = relative_path

        # mark as ready
        datasource.status = DataSource.Status.READY
        datasource.save()

        # Delete the original uploaded file to save space (only on success)
        if os.path.exists(original_file_path):
            os.remove(original_file_path)

        logger.info(f"Successfully converted DataSource {datasource_id} to Parquet format")
        return f"Conversion completed for DataSource {datasource_id}"

    except Exception as e:
        # record error in datasource and mark status
        logger.error(f"Parquet conversion failed for datasource {datasource_id}: {e}", exc_info=True)
        try:
            datasource.status = DataSource.Status.ERROR
            datasource.quality_report = {'error': str(e)}
            datasource.save()
        except Exception:
            # if saving fails, at least log it
            logger.exception("Failed to update DataSource status after conversion error")
        return f"Error: {str(e)}"


@shared_task
def process_datasource_task(datasource_id):
    """
    Celery task to process a DataSource into a DataFrame in the background.

    This is a wrapper around the core service function to allow for
    asynchronous execution.
    """
    try:
        # The result of this (the DataFrame) won't be returned to the caller,
        # as this runs in the background. The purpose is to execute it.
        # In future steps, we might save the result somewhere.
        process_datasource_to_df(datasource_id)
        return f"Successfully processed DataSource {datasource_id}"
    except Exception as e:
        # It's good practice to catch exceptions and log them
        # You can add more robust logging here
        return f"Error processing DataSource {datasource_id}: {str(e)}"