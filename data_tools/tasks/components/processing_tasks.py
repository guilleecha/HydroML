"""
Data processing tasks for data_tools.
"""
from celery import shared_task
from data_tools.services import process_datasource_to_df
import logging

logger = logging.getLogger(__name__)


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
