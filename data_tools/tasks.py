import os
import pandas as pd
import numpy as np
from celery import shared_task
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from itertools import combinations
from .services import process_datasource_to_df
from .services.data_quality_service import run_data_quality_pipeline
from projects.models import DataSource
import logging
from django.conf import settings
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

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


@shared_task
def deep_missing_data_analysis_task(datasource_id, target_column, required_variables):
    """
    Comprehensive missing data analysis task for the Missing Data Toolkit.
    
    Performs:
    1. Missing data heatmap generation using missingno.matrix()
    2. Feature importance estimation using RandomForestRegressor
    3. Complete case analysis for all relevant variable combinations
    4. Saves results to DataSource.missing_data_report
    
    Args:
        datasource_id (str): DataSource UUID
        target_column (str): Target variable for feature importance analysis
        required_variables (list): List of required variables for analysis
        
    Returns:
        dict: Task execution summary
    """
    try:
        # Fetch the DataSource object
        datasource = DataSource.objects.get(id=datasource_id)
        
        logger.info(f"Starting deep missing data analysis for DataSource {datasource_id}")
        logger.info(f"Target column: {target_column}")
        logger.info(f"Required variables: {required_variables}")
        
        # Load the dataframe
        df = _load_dataframe_from_datasource(datasource)
        
        if df is None or df.empty:
            raise ValueError("Failed to load data or file is empty")
        
        logger.info(f"Loaded dataframe with shape: {df.shape}")
        
        # Step 1: Generate Missing Data Heatmap
        logger.info("Step 1: Generating missing data heatmap")
        heatmap_html = _generate_missing_data_heatmap(df, datasource_id, required_variables)
        
        # Step 2: Feature Importance Estimation
        logger.info("Step 2: Running feature importance estimation")
        feature_importances = _calculate_feature_importance(df, target_column, required_variables)
        
        # Step 3: Complete Case Analysis (Combinations)
        logger.info("Step 3: Running complete case analysis")
        combination_counts = _calculate_complete_case_combinations(df, required_variables)
        
        # Step 4: Additional missing data statistics
        logger.info("Step 4: Calculating additional missing data statistics")
        missing_stats = _calculate_missing_data_statistics(df, required_variables)
        
        # Step 5: Save the comprehensive report
        missing_data_report = {
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'target_column': target_column,
            'required_variables': required_variables,
            'heatmap_html': heatmap_html,
            'feature_importance': feature_importances,
            'combination_analysis': combination_counts,
            'missing_statistics': missing_stats,
            'analysis_metadata': {
                'original_shape': df.shape,
                'total_complete_rows': int(df.dropna().shape[0]),
                'total_rows_with_target': int(df[target_column].dropna().shape[0]) if target_column in df.columns else 0,
                'analysis_successful': True,
                'heatmap_generated': bool(heatmap_html)
            }
        }
        
        # Save to database
        datasource.missing_data_report = missing_data_report
        datasource.save()
        
        logger.info(f"Successfully completed deep missing data analysis for DataSource {datasource_id}")
        
        return {
            'status': 'success',
            'message': f"Deep missing data analysis completed for DataSource {datasource_id}",
            'feature_importance_variables': len(feature_importances),
            'combination_analysis_count': len(combination_counts),
            'total_complete_rows': missing_data_report['analysis_metadata']['total_complete_rows'],
            'heatmap_generated': bool(heatmap_html)
        }
        
    except Exception as e:
        logger.error(f"Deep missing data analysis failed for datasource {datasource_id}: {e}", exc_info=True)
        
        # Save error report
        try:
            datasource = DataSource.objects.get(id=datasource_id)
            datasource.missing_data_report = {
                'analysis_timestamp': pd.Timestamp.now().isoformat(),
                'error': str(e),
                'analysis_successful': False,
                'target_column': target_column,
                'required_variables': required_variables,
                'heatmap_generated': False
            }
            datasource.save()
        except Exception:
            logger.exception("Failed to update DataSource with error report")
        
        return {
            'status': 'error',
            'message': f"Deep missing data analysis failed: {str(e)}",
            'datasource_id': str(datasource_id)
        }


def _load_dataframe_from_datasource(datasource):
    """Load dataframe from DataSource file."""
    try:
        file_path = datasource.file.path
        
        if file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            # Try different encodings and separators
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            # Final fallback
            return pd.read_csv(file_path, encoding='latin-1')
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            # Try parquet as fallback
            return pd.read_parquet(file_path)
            
    except Exception as e:
        logger.error(f"Failed to load dataframe from datasource: {e}")
        return None


def _calculate_feature_importance(df, target_column, required_variables):
    """Calculate feature importance using RandomForestRegressor after imputation."""
    try:
        # Check if target column exists
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataframe")
        
        # Select features (required variables + target)
        all_variables = required_variables + [target_column]
        available_variables = [var for var in all_variables if var in df.columns]
        
        if len(available_variables) < 2:
            raise ValueError(f"Insufficient variables for analysis. Available: {available_variables}")
        
        # Create feature matrix and target vector
        feature_vars = [var for var in available_variables if var != target_column]
        X = df[feature_vars].copy()
        y = df[target_column].copy()
        
        # Keep only rows where target is not null
        mask = y.notna()
        X = X[mask]
        y = y[mask]
        
        if len(y) == 0:
            raise ValueError(f"No non-null values found in target column '{target_column}'")
        
        # Prepare features for ML
        X_processed = X.copy()
        
        # Handle categorical variables with label encoding
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns
        for col in categorical_columns:
            le = LabelEncoder()
            X_processed[col] = le.fit_transform(X_processed[col].astype(str))
        
        # Impute missing values in features
        imputer = SimpleImputer(strategy='median')
        X_imputed = pd.DataFrame(
            imputer.fit_transform(X_processed),
            columns=X_processed.columns,
            index=X_processed.index
        )
        
        # Handle target variable (ensure it's numeric)
        if y.dtype == 'object':
            le_target = LabelEncoder()
            y = pd.Series(le_target.fit_transform(y.astype(str)), index=y.index)
        
        # Train RandomForestRegressor
        rf = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            n_jobs=-1
        )
        
        rf.fit(X_imputed, y)
        
        # Extract feature importances
        feature_importances = {}
        for feature, importance in zip(feature_vars, rf.feature_importances_):
            feature_importances[feature] = float(importance)
        
        logger.info(f"Feature importance calculated for {len(feature_importances)} features")
        return feature_importances
        
    except Exception as e:
        logger.error(f"Feature importance calculation failed: {e}")
        return {}


def _calculate_complete_case_combinations(df, required_variables):
    """Calculate complete rows for all combinations of required variables."""
    try:
        # Filter to only include variables that exist in the dataframe
        available_variables = [var for var in required_variables if var in df.columns]
        
        if len(available_variables) == 0:
            return {}
        
        combination_counts = {}
        
        # Single variables
        for var in available_variables:
            complete_count = int(df[var].notna().sum())
            combination_counts[var] = {
                'variables': [var],
                'complete_rows': complete_count,
                'completion_rate': float(complete_count / len(df)) if len(df) > 0 else 0.0
            }
        
        # Combinations of 2 or more variables (up to 5 for performance)
        max_combination_size = min(5, len(available_variables))
        
        for r in range(2, max_combination_size + 1):
            for combination in combinations(available_variables, r):
                combination_key = " + ".join(sorted(combination))
                
                # Count rows where all variables in combination are not null
                mask = pd.Series(True, index=df.index)
                for var in combination:
                    mask &= df[var].notna()
                
                complete_count = int(mask.sum())
                combination_counts[combination_key] = {
                    'variables': list(combination),
                    'complete_rows': complete_count,
                    'completion_rate': float(complete_count / len(df)) if len(df) > 0 else 0.0
                }
        
        logger.info(f"Calculated complete case combinations for {len(combination_counts)} scenarios")
        return combination_counts
        
    except Exception as e:
        logger.error(f"Complete case combination calculation failed: {e}")
        return {}


def _calculate_missing_data_statistics(df, required_variables):
    """Calculate comprehensive missing data statistics."""
    try:
        available_variables = [var for var in required_variables if var in df.columns]
        
        missing_stats = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'required_variables_count': len(available_variables),
            'column_missing_percentages': {},
            'missing_patterns': {},
            'completely_missing_variables': []
        }
        
        # Calculate missing percentages for each variable
        for var in available_variables:
            missing_count = int(df[var].isna().sum())
            missing_percentage = float(missing_count / len(df) * 100) if len(df) > 0 else 0.0
            
            missing_stats['column_missing_percentages'][var] = {
                'missing_count': missing_count,
                'missing_percentage': missing_percentage,
                'complete_count': int(len(df) - missing_count)
            }
            
            # Track completely missing variables
            if missing_count == len(df):
                missing_stats['completely_missing_variables'].append(var)
        
        # Calculate missing patterns (simplified)
        missing_pattern_df = df[available_variables].isna()
        pattern_counts = missing_pattern_df.value_counts().head(10)  # Top 10 patterns
        
        for pattern, count in pattern_counts.items():
            pattern_key = "Missing: " + ", ".join([var for var, is_missing in zip(available_variables, pattern) if is_missing])
            if not pattern_key.endswith(": "):
                missing_stats['missing_patterns'][pattern_key or "Complete"] = int(count)
        
        logger.info(f"Calculated missing data statistics for {len(available_variables)} variables")
        return missing_stats
        
    except Exception as e:
        logger.error(f"Missing data statistics calculation failed: {e}")
        return {}


def _generate_missing_data_heatmap(df, datasource_id, required_variables):
    """
    Generate an interactive missing data heatmap using Plotly.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        datasource_id (str): DataSource identifier for file naming
        required_variables (list): List of required variables to focus on
        
    Returns:
        str or None: HTML string of interactive Plotly heatmap, or None if failed
    """
    try:
        # Filter dataframe to focus on required variables that exist
        available_variables = [var for var in required_variables if var in df.columns]
        
        if not available_variables:
            logger.warning("No available variables for heatmap generation")
            return None
        
        # Create focused dataframe for heatmap (limit to reasonable size for performance)
        heatmap_df = df[available_variables].copy()
        
        # If dataset is very large, sample for visualization
        if len(heatmap_df) > 1000:
            heatmap_df = heatmap_df.sample(n=1000, random_state=42)
            logger.info(f"Sampled 1000 rows from {len(df)} for heatmap visualization")
        
        # Create nullity matrix (1 for missing, 0 for present)
        nullity_matrix = heatmap_df.isnull().astype(int)
        
        # Create interactive heatmap with Plotly
        fig = px.imshow(
            nullity_matrix.values,
            x=nullity_matrix.columns,
            y=list(range(len(nullity_matrix))),
            color_continuous_scale=[
                [0, '#61AFEF'],    # Present data - One Dark blue
                [1, '#E06C75']     # Missing data - One Dark red
            ],
            aspect="auto",
            title=f"Missing Data Pattern Matrix - {len(available_variables)} Variables",
            labels=dict(
                x="Variables", 
                y="Records", 
                color="Status"
            )
        )
        
        # Apply One Dark theme styling
        fig.update_layout(
            # Dark background matching One Dark theme
            plot_bgcolor='#282C34',
            paper_bgcolor='#282C34',
            
            # Title styling
            title=dict(
                font=dict(color='#ABB2BF', size=16, family='monospace'),
                x=0.5,
                xanchor='center',
                pad=dict(t=20)
            ),
            
            # X-axis styling
            xaxis=dict(
                title=dict(
                    text="Variables",
                    font=dict(color='#ABB2BF', size=12)
                ),
                tickfont=dict(color='#ABB2BF', size=10),
                tickangle=-45,
                gridcolor='#3E4451',
                showgrid=True,
                zeroline=False,
                side='bottom'
            ),
            
            # Y-axis styling
            yaxis=dict(
                title=dict(
                    text="Records",
                    font=dict(color='#ABB2BF', size=12)
                ),
                tickfont=dict(color='#ABB2BF', size=10),
                gridcolor='#3E4451',
                showgrid=True,
                zeroline=False,
                autorange='reversed'  # Show first rows at top
            ),
            
            # Colorbar styling
            coloraxis_colorbar=dict(
                title=dict(
                    text="Data Status", 
                    font=dict(color='#ABB2BF', size=12)
                ),
                tickfont=dict(color='#ABB2BF', size=10),
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Present', 'Missing'],
                thickness=20,
                len=0.7
            ),
            
            # Layout dimensions
            width=900,
            height=max(400, min(800, len(nullity_matrix) * 2 + 200)),
            margin=dict(t=80, r=80, b=100, l=80),
            
            # Hover styling
            hoverlabel=dict(
                bgcolor='#3E4451',
                bordercolor='#ABB2BF',
                font=dict(color='#ABB2BF', family='monospace')
            )
        )
        
        # Enhanced hover template for better interactivity
        fig.update_traces(
            hovertemplate="<b>Variable:</b> %{x}<br>" +
                         "<b>Record:</b> %{y}<br>" +
                         "<b>Status:</b> %{customdata}<br>" +
                         "<extra></extra>",
            customdata=[["Missing" if val else "Present" for val in row] 
                       for row in nullity_matrix.values]
        )
        
        # Convert to HTML string for embedding in Django template
        html_string = fig.to_html(
            include_plotlyjs='cdn',
            div_id=f"missing-data-heatmap-{datasource_id}",
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'missing_data_heatmap_{datasource_id}',
                    'height': max(400, min(800, len(nullity_matrix) * 2 + 200)),
                    'width': 900,
                    'scale': 2
                }
            }
        )
        
        logger.info(f"Generated interactive missing data heatmap with {len(available_variables)} variables")
        return html_string
        
    except Exception as e:
        logger.error(f"Heatmap generation failed: {e}", exc_info=True)
        return None