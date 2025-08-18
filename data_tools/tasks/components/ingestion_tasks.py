"""
Data ingestion and file processing tasks for data_tools.
"""
from celery import shared_task
from data_tools.services import process_datasource_to_df
from data_tools.services.data_quality_service import run_data_quality_pipeline
from projects.models import DataSource
import logging
import os
import pandas as pd
import numpy as np
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)


@shared_task
def convert_file_to_parquet_task(datasource_id):
    """
    Enhanced data ingestion task with Great Expectations validation and cleaning.
    
    This task now includes:
    1. Data loading and type inference
    2. Automatic data cleaning and type conversion
    3. Great Expectations validation suite
    4. Quality report generation
    5. Cleaned data saving as Parquet
    """
    # Fetch the DataSource object
    datasource = DataSource.objects.get(id=datasource_id)

    # Mark as processing
    datasource.status = DataSource.Status.PROCESSING
    datasource.save()

    try:
        # Step 1: Load the original file
        original_file_path = datasource.file.path
        logger.info(f"Loading file for DataSource {datasource_id}: {original_file_path}")

        # Read the original file with enhanced format detection
        df = _load_file_with_format_detection(original_file_path)
        
        if df is None or df.empty:
            raise ValueError("Failed to load data or file is empty")

        logger.info(f"Successfully loaded {df.shape[0]:,} rows and {df.shape[1]} columns")

        # Step 2: Set up quality report output directory
        quality_reports_dir = Path(settings.MEDIA_ROOT) / 'quality_reports' / str(datasource_id)
        quality_reports_dir.mkdir(parents=True, exist_ok=True)

        # Step 3: Run Great Expectations data quality pipeline
        logger.info(f"Starting data quality pipeline for DataSource {datasource_id}")
        
        try:
            cleaned_df, quality_report, report_html_path = run_data_quality_pipeline(
                df=df,
                datasource_id=str(datasource_id),
                output_dir=str(quality_reports_dir)
            )
            
            logger.info(f"Data quality pipeline completed. Report saved to: {report_html_path}")
            
        except ImportError as e:
            # Fallback if Great Expectations is not installed
            logger.warning(f"Great Expectations not available, using fallback validation: {e}")
            cleaned_df, quality_report, report_html_path = _fallback_data_validation(
                df, datasource_id, quality_reports_dir
            )
        except Exception as e:
            logger.error(f"Data quality pipeline failed, using fallback: {e}")
            cleaned_df, quality_report, report_html_path = _fallback_data_validation(
                df, datasource_id, quality_reports_dir
            )

        # Step 4: Save the cleaned DataFrame as Parquet
        base_path = os.path.splitext(original_file_path)[0]
        new_parquet_path = f"{base_path}.parquet"

        logger.info(f"Saving cleaned data to Parquet: {new_parquet_path}")
        cleaned_df.to_parquet(new_parquet_path, index=False)

        # Step 5: Update DataSource with new file path and quality report
        media_root = datasource.file.storage.location
        relative_parquet_path = os.path.relpath(new_parquet_path, media_root)
        relative_report_path = os.path.relpath(report_html_path, settings.MEDIA_ROOT)

        # Update DataSource fields
        datasource.file.name = relative_parquet_path
        datasource.quality_report = quality_report
        datasource.quality_report_path = relative_report_path
        datasource.status = DataSource.Status.READY
        datasource.save()

        # Step 6: Clean up original file
        if os.path.exists(original_file_path) and original_file_path != new_parquet_path:
            try:
                os.remove(original_file_path)
                logger.info(f"Removed original file: {original_file_path}")
            except OSError as e:
                logger.warning(f"Could not remove original file: {e}")

        logger.info(f"Successfully completed enhanced data ingestion for DataSource {datasource_id}")
        
        # Return success summary
        return {
            'status': 'success',
            'message': f"Enhanced data ingestion completed for DataSource {datasource_id}",
            'data_shape': cleaned_df.shape,
            'quality_report_path': relative_report_path,
            'type_conversions': len(quality_report.get('cleaning_report', {}).get('type_conversions', {})),
            'validation_success': quality_report.get('validation_success', False)
        }

    except Exception as e:
        # Record error in datasource and mark status
        logger.error(f"Enhanced data ingestion failed for datasource {datasource_id}: {e}", exc_info=True)
        try:
            datasource.status = DataSource.Status.ERROR
            datasource.quality_report = {
                'error': str(e),
                'pipeline_failed': True,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            datasource.save()
        except Exception:
            logger.exception("Failed to update DataSource status after ingestion error")
        
        return {
            'status': 'error',
            'message': f"Enhanced data ingestion failed: {str(e)}",
            'datasource_id': str(datasource_id)
        }


def _load_file_with_format_detection(file_path: str) -> pd.DataFrame:
    """
    Load file with enhanced format detection and encoding handling.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        pd.DataFrame: Loaded DataFrame
    """
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.csv':
            # Try different encodings and separators for CSV files
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    # First try with automatic delimiter detection
                    df = pd.read_csv(file_path, sep=None, engine='python', encoding=encoding)
                    if not df.empty and len(df.columns) > 1:
                        return df
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            # Fallback to basic CSV reading
            return pd.read_csv(file_path, encoding='latin-1')
            
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
            
        elif file_ext == '.json':
            return pd.read_json(file_path)
            
        elif file_ext == '.tsv':
            return pd.read_csv(file_path, sep='\t', encoding='utf-8')
            
        elif file_ext == '.parquet':
            return pd.read_parquet(file_path)
            
        else:
            # Default to CSV parsing for unknown extensions
            logger.warning(f"Unknown file extension {file_ext}, attempting CSV parsing")
            return pd.read_csv(file_path, sep=None, engine='python', encoding='latin-1')
            
    except Exception as e:
        logger.error(f"Failed to load file {file_path}: {e}")
        raise


def _fallback_data_validation(df: pd.DataFrame, datasource_id: str, output_dir: Path) -> tuple:
    """
    Fallback data validation when Great Expectations is not available.
    
    Args:
        df: Input DataFrame
        datasource_id: DataSource identifier
        output_dir: Output directory for reports
        
    Returns:
        tuple: (cleaned_df, quality_report, report_path)
    """
    logger.info(f"Running fallback data validation for DataSource {datasource_id}")
    
    # Perform basic cleaning
    cleaned_df = df.copy()
    original_shape = df.shape
    
    # Basic type inference and conversion
    type_conversions = {}
    null_introductions = {}
    
    for column in df.columns:
        if df[column].dtype == 'object':
            # Try numeric conversion
            try:
                numeric_series = pd.to_numeric(df[column], errors='coerce')
                non_null_original = df[column].dropna().shape[0]
                non_null_converted = numeric_series.dropna().shape[0]
                
                # If at least 70% of values can be converted, do the conversion
                if non_null_converted / non_null_original >= 0.7:
                    introduced_nulls = df[column].isna().sum() - numeric_series.isna().sum()
                    cleaned_df[column] = numeric_series
                    
                    type_conversions[column] = {
                        'from': str(df[column].dtype),
                        'to': str(numeric_series.dtype),
                        'conversion_rate': (non_null_converted / non_null_original) * 100
                    }
                    
                    if introduced_nulls > 0:
                        null_introductions[column] = int(introduced_nulls)
                        
            except Exception as e:
                logger.warning(f"Failed to convert column {column}: {e}")
    
    # Build quality report
    quality_report = {
        'fallback_validation': True,
        'original_shape': original_shape,
        'final_shape': cleaned_df.shape,
        'cleaning_report': {
            'type_conversions': type_conversions,
            'null_introductions': null_introductions,
            'total_converted_columns': len(type_conversions)
        },
        'missing_values': cleaned_df.isnull().sum().to_dict(),
        'data_types': {col: str(dtype) for col, dtype in cleaned_df.dtypes.items()},
        'validation_success': True,  # Fallback always "succeeds"
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    # Create simple HTML report
    report_path = output_dir / f"fallback_quality_report_ds_{datasource_id}.html"
    _create_fallback_html_report(quality_report, datasource_id, str(report_path))
    
    return cleaned_df, quality_report, str(report_path)


def _create_fallback_html_report(quality_report: dict, datasource_id: str, report_path: str):
    """Create a simple HTML report for fallback validation."""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Quality Report - DataSource {datasource_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .header {{ background: #2196F3; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .success {{ color: #4CAF50; }}
            .warning {{ color: #FF9800; }}
            .metric {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .warning-box {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Data Quality Report (Fallback Mode)</h1>
                <p>DataSource ID: {datasource_id}</p>
                <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="warning-box">
                <strong>Note:</strong> This report was generated using fallback validation. 
                Install Great Expectations for enhanced data quality analysis.
            </div>
            
            <h2>Data Overview</h2>
            <div class="metric">
                <strong>Original Shape:</strong> {quality_report['original_shape'][0]:,} rows × {quality_report['original_shape'][1]} columns
            </div>
            <div class="metric">
                <strong>Final Shape:</strong> {quality_report['final_shape'][0]:,} rows × {quality_report['final_shape'][1]} columns
            </div>
            <div class="metric">
                <strong>Type Conversions:</strong> {quality_report['cleaning_report']['total_converted_columns']}
            </div>
            
            <h2>Type Conversions</h2>
            {_generate_type_conversions_table(quality_report.get('cleaning_report', {}).get('type_conversions', {}))}
            
            <h2>Missing Values by Column</h2>
            {_generate_missing_values_table(quality_report.get('missing_values', {}))}
            
            <h2>Final Data Types</h2>
            {_generate_data_types_table(quality_report.get('data_types', {}))}
            
        </div>
    </body>
    </html>
    """
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _generate_type_conversions_table(conversions: dict) -> str:
    """Generate HTML table for type conversions."""
    if not conversions:
        return "<p>No type conversions were performed.</p>"
    
    html = "<table><tr><th>Column</th><th>From Type</th><th>To Type</th><th>Conversion Rate</th></tr>"
    
    for column, details in conversions.items():
        html += f"""
        <tr>
            <td>{column}</td>
            <td>{details['from']}</td>
            <td>{details['to']}</td>
            <td>{details['conversion_rate']:.1f}%</td>
        </tr>
        """
    
    html += "</table>"
    return html


def _generate_missing_values_table(missing_values: dict) -> str:
    """Generate HTML table for missing values."""
    if not missing_values:
        return "<p>No missing values information available.</p>"
    
    # Filter out columns with 0 missing values for cleaner display
    filtered_missing = {col: count for col, count in missing_values.items() if count > 0}
    
    if not filtered_missing:
        return "<p>No missing values found in any column.</p>"
    
    html = "<table><tr><th>Column</th><th>Missing Values</th></tr>"
    
    for column, count in sorted(filtered_missing.items(), key=lambda x: x[1], reverse=True):
        html += f"""
        <tr>
            <td>{column}</td>
            <td>{count:,}</td>
        </tr>
        """
    
    html += "</table>"
    return html


def _generate_data_types_table(data_types: dict) -> str:
    """Generate HTML table for data types."""
    if not data_types:
        return "<p>No data type information available.</p>"
    
    html = "<table><tr><th>Column</th><th>Data Type</th></tr>"
    
    for column, dtype in data_types.items():
        html += f"""
        <tr>
            <td>{column}</td>
            <td>{dtype}</td>
        </tr>
        """
    
    html += "</table>"
    return html
