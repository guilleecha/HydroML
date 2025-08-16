"""
Great Expectations Data Validation and Cleaning Service

This module provides comprehensive data validation, cleaning, and reporting
capabilities using the Great Expectations library.
"""
import os
import pandas as pd
from pathlib import Path
import logging
from typing import Tuple, Dict, Any
from django.conf import settings
from django.utils import timezone
import json

# Try to import Great Expectations, fallback if not available
try:
    import great_expectations as gx
    from great_expectations.core.expectation_suite import ExpectationSuite
    from great_expectations.validator.validator import Validator
    GX_AVAILABLE = True
except ImportError:
    GX_AVAILABLE = False
    gx = None
    ExpectationSuite = None
    Validator = None

logger = logging.getLogger(__name__)


class DataQualityService:
    """
    Service class for data validation, cleaning, and quality reporting using Great Expectations.
    """
    
    def __init__(self, datasource_id: str):
        self.datasource_id = datasource_id
        self.context = None
        self.validator = None
        self.cleaned_df = None
        self.quality_report = {}
        
    def initialize_gx_context(self):
        """Initialize Great Expectations context with custom configuration."""
        if not GX_AVAILABLE:
            logger.warning("Great Expectations not available, skipping GX context initialization")
            return False
            
        try:
            # Create GX context with ephemeral configuration for simplicity
            self.context = gx.get_context(mode="ephemeral")
            logger.info(f"Great Expectations context initialized for DataSource {self.datasource_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize GX context: {e}")
            return False
    
    def load_and_profile_data(self, df: pd.DataFrame) -> bool:
        """
        Load DataFrame into Great Expectations and perform initial profiling.
        
        Args:
            df: Input pandas DataFrame
            
        Returns:
            bool: Success status
        """
        try:
            # Create a data asset from the DataFrame
            data_asset = self.context.data_sources.add_pandas("pandas_datasource").add_dataframe_asset(
                name=f"datasource_{self.datasource_id}",
                dataframe=df
            )
            
            # Create batch request
            batch_request = data_asset.build_batch_request()
            
            # Create expectation suite
            suite_name = f"quality_suite_{self.datasource_id}"
            suite = self.context.suites.add(ExpectationSuite(name=suite_name))
            
            # Create validator
            self.validator = self.context.get_validator(
                batch_request=batch_request,
                expectation_suite=suite
            )
            
            logger.info(f"Data loaded and profiled successfully for DataSource {self.datasource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load and profile data: {e}")
            return False
    
    def infer_and_validate_data_types(self) -> pd.DataFrame:
        """
        Infer data types and handle mixed-type columns with validation expectations.
        
        Returns:
            pd.DataFrame: Cleaned DataFrame with corrected types
        """
        try:
            # Get the current DataFrame
            df = self.validator.active_batch.data.dataframe.copy()
            original_shape = df.shape
            
            # Store original data types for comparison
            original_dtypes = df.dtypes.to_dict()
            
            # Initialize cleaning report
            cleaning_report = {
                'original_shape': original_shape,
                'original_dtypes': {col: str(dtype) for col, dtype in original_dtypes.items()},
                'type_conversions': {},
                'conversion_failures': {},
                'null_introductions': {}
            }
            
            # Process each column for type inference and conversion
            for column in df.columns:
                try:
                    self._process_column_type_conversion(df, column, cleaning_report)
                except Exception as e:
                    logger.warning(f"Failed to process column {column}: {e}")
                    cleaning_report['conversion_failures'][column] = str(e)
            
            # Store cleaned DataFrame and report
            self.cleaned_df = df
            self.quality_report['cleaning_report'] = cleaning_report
            self.quality_report['final_shape'] = df.shape
            self.quality_report['final_dtypes'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
            
            logger.info(f"Data type inference and conversion completed for DataSource {self.datasource_id}")
            return df
            
        except Exception as e:
            logger.error(f"Failed during data type inference: {e}")
            # Return original DataFrame if conversion fails
            return self.validator.active_batch.data.dataframe.copy()
    
    def _process_column_type_conversion(self, df: pd.DataFrame, column: str, cleaning_report: dict):
        """
        Process a single column for type conversion and validation.
        
        Args:
            df: DataFrame to modify
            column: Column name to process
            cleaning_report: Report dictionary to update
        """
        original_series = df[column].copy()
        original_type = str(original_series.dtype)
        
        # Skip if already numeric
        if pd.api.types.is_numeric_dtype(original_series):
            return
        
        # Try to convert to numeric if the column contains mostly numbers
        non_null_values = original_series.dropna()
        if len(non_null_values) == 0:
            return
        
        # Test numeric conversion potential
        numeric_convertible = 0
        for value in non_null_values.astype(str):
            try:
                float(value)
                numeric_convertible += 1
            except (ValueError, TypeError):
                continue
        
        numeric_percentage = numeric_convertible / len(non_null_values)
        
        # If 70% or more values can be converted to numeric, attempt conversion
        if numeric_percentage >= 0.7:
            try:
                # Convert with errors='coerce' to turn non-convertible values to NaN
                converted_series = pd.to_numeric(original_series, errors='coerce')
                
                # Count how many values became NaN due to conversion
                original_nulls = original_series.isna().sum()
                new_nulls = converted_series.isna().sum()
                introduced_nulls = new_nulls - original_nulls
                
                # Update DataFrame
                df[column] = converted_series
                
                # Record conversion details
                cleaning_report['type_conversions'][column] = {
                    'from': original_type,
                    'to': str(converted_series.dtype),
                    'numeric_percentage': round(numeric_percentage * 100, 2),
                    'introduced_nulls': int(introduced_nulls),
                    'total_nulls_after': int(new_nulls)
                }
                
                if introduced_nulls > 0:
                    cleaning_report['null_introductions'][column] = int(introduced_nulls)
                
                # Add Great Expectations validation
                self._add_type_validation_expectations(column, converted_series.dtype)
                
            except Exception as e:
                logger.warning(f"Failed to convert column {column} to numeric: {e}")
    
    def _add_type_validation_expectations(self, column: str, expected_type):
        """Add type validation expectations for converted columns."""
        try:
            # Add expectation for column type
            if pd.api.types.is_numeric_dtype(expected_type):
                self.validator.expect_column_values_to_be_of_type(
                    column=column,
                    type_="float64"
                )
            
            # Add expectation to monitor null values
            self.validator.expect_column_values_to_not_be_null(
                column=column,
                mostly=0.1  # Allow up to 90% null values after conversion
            )
            
        except Exception as e:
            logger.warning(f"Failed to add expectations for column {column}: {e}")
    
    def add_comprehensive_expectations(self):
        """Add comprehensive data quality expectations."""
        try:
            df = self.cleaned_df if self.cleaned_df is not None else self.validator.active_batch.data.dataframe
            
            # Add table-level expectations
            self.validator.expect_table_row_count_to_be_between(
                min_value=1,
                max_value=1000000  # Reasonable upper limit
            )
            
            self.validator.expect_table_column_count_to_be_between(
                min_value=1,
                max_value=1000  # Reasonable upper limit for columns
            )
            
            # Add column-level expectations
            for column in df.columns:
                try:
                    # Check for high percentage of missing values
                    null_percentage = df[column].isna().sum() / len(df)
                    
                    if null_percentage > 0.5:  # More than 50% null
                        # Add expectation that documents high null rate
                        self.validator.expect_column_values_to_not_be_null(
                            column=column,
                            mostly=0.1  # Allow high null rate but document it
                        )
                    
                    # Add uniqueness check for potential ID columns
                    if 'id' in column.lower() or column.lower() in ['index', 'key']:
                        self.validator.expect_column_values_to_be_unique(column=column)
                    
                    # Add range checks for numeric columns
                    if pd.api.types.is_numeric_dtype(df[column]):
                        self.validator.expect_column_values_to_be_between(
                            column=column,
                            min_value=df[column].min(),
                            max_value=df[column].max()
                        )
                        
                except Exception as e:
                    logger.warning(f"Failed to add expectations for column {column}: {e}")
            
            logger.info(f"Comprehensive expectations added for DataSource {self.datasource_id}")
            
        except Exception as e:
            logger.error(f"Failed to add comprehensive expectations: {e}")
    
    def validate_and_generate_report(self, output_path: str) -> Tuple[bool, str]:
        """
        Run validation and generate HTML quality report.
        
        Args:
            output_path: Directory path where to save the HTML report
            
        Returns:
            Tuple[bool, str]: (Success status, Report file path)
        """
        try:
            # Run validation
            validation_result = self.validator.validate()
            
            # Update quality report with validation results
            self.quality_report.update({
                'validation_success': validation_result.success,
                'evaluated_expectations': validation_result.statistics.get('evaluated_expectations', 0),
                'successful_expectations': validation_result.statistics.get('successful_expectations', 0),
                'unsuccessful_expectations': validation_result.statistics.get('unsuccessful_expectations', 0),
                'success_percent': validation_result.statistics.get('success_percent', 0)
            })
            
            # Generate Data Docs
            report_filename = f"quality_report_ds_{self.datasource_id}.html"
            report_path = Path(output_path) / report_filename
            
            # Ensure output directory exists
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Build and save data docs
            self.context.build_data_docs()
            
            # Get the generated HTML and save it to our custom location
            docs_sites = self.context.get_docs_sites_urls()
            if docs_sites:
                # Copy the generated docs to our desired location
                self._save_custom_report(validation_result, str(report_path))
            else:
                # Fallback: create a simple HTML report
                self._create_fallback_html_report(validation_result, str(report_path))
            
            logger.info(f"Quality report generated: {report_path}")
            return True, str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to generate quality report: {e}")
            # Create error report
            error_report_path = Path(output_path) / f"error_report_ds_{self.datasource_id}.html"
            self._create_error_html_report(str(e), str(error_report_path))
            return False, str(error_report_path)
    
    def _save_custom_report(self, validation_result, report_path: str):
        """Save a custom HTML report with validation results."""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Quality Report - DataSource {self.datasource_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background: #4CAF50; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .success {{ color: #4CAF50; }}
                .warning {{ color: #FF9800; }}
                .error {{ color: #F44336; }}
                .metric {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }}
                .expectation {{ background: #fff; border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .expectation.success {{ border-left: 4px solid #4CAF50; }}
                .expectation.failed {{ border-left: 4px solid #F44336; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Data Quality Report</h1>
                    <p>DataSource ID: {self.datasource_id}</p>
                    <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h2>Validation Summary</h2>
                <div class="metric">
                    <strong>Overall Success:</strong> 
                    <span class="{'success' if validation_result.success else 'error'}">
                        {'✓ PASSED' if validation_result.success else '✗ FAILED'}
                    </span>
                </div>
                <div class="metric">
                    <strong>Success Rate:</strong> {validation_result.statistics.get('success_percent', 0):.1f}%
                </div>
                <div class="metric">
                    <strong>Expectations Evaluated:</strong> {validation_result.statistics.get('evaluated_expectations', 0)}
                </div>
                <div class="metric">
                    <strong>Successful:</strong> <span class="success">{validation_result.statistics.get('successful_expectations', 0)}</span>
                </div>
                <div class="metric">
                    <strong>Failed:</strong> <span class="error">{validation_result.statistics.get('unsuccessful_expectations', 0)}</span>
                </div>
                
                <h2>Data Overview</h2>
                {self._generate_data_overview_html()}
                
                <h2>Type Conversions</h2>
                {self._generate_type_conversions_html()}
                
                <h2>Expectation Results</h2>
                {self._generate_expectations_html(validation_result)}
                
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_data_overview_html(self) -> str:
        """Generate HTML for data overview section."""
        if 'cleaning_report' not in self.quality_report:
            return "<p>No data overview available.</p>"
        
        report = self.quality_report['cleaning_report']
        
        return f"""
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Original Shape</td><td>{report['original_shape'][0]:,} rows × {report['original_shape'][1]} columns</td></tr>
            <tr><td>Final Shape</td><td>{self.quality_report.get('final_shape', ['Unknown', 'Unknown'])[0]:,} rows × {self.quality_report.get('final_shape', ['Unknown', 'Unknown'])[1]} columns</td></tr>
            <tr><td>Type Conversions</td><td>{len(report.get('type_conversions', {}))}</td></tr>
            <tr><td>Null Values Introduced</td><td>{sum(report.get('null_introductions', {}).values())}</td></tr>
        </table>
        """
    
    def _generate_type_conversions_html(self) -> str:
        """Generate HTML for type conversions section."""
        if 'cleaning_report' not in self.quality_report:
            return "<p>No type conversion data available.</p>"
        
        conversions = self.quality_report['cleaning_report'].get('type_conversions', {})
        
        if not conversions:
            return "<p>No type conversions were performed.</p>"
        
        html = "<table><tr><th>Column</th><th>From Type</th><th>To Type</th><th>Numeric %</th><th>Nulls Introduced</th></tr>"
        
        for column, details in conversions.items():
            html += f"""
            <tr>
                <td>{column}</td>
                <td>{details['from']}</td>
                <td>{details['to']}</td>
                <td>{details['numeric_percentage']}%</td>
                <td>{details['introduced_nulls']}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_expectations_html(self, validation_result) -> str:
        """Generate HTML for expectations results."""
        html = ""
        
        for result in validation_result.results:
            expectation_type = result.expectation_config.expectation_type
            success = result.success
            
            html += f"""
            <div class="expectation {'success' if success else 'failed'}">
                <strong>{expectation_type}</strong>
                <span class="{'success' if success else 'error'}">
                    {'✓ PASSED' if success else '✗ FAILED'}
                </span>
                <br>
                <small>{result.expectation_config.kwargs}</small>
            </div>
            """
        
        return html if html else "<p>No expectation results available.</p>"
    
    def _create_fallback_html_report(self, validation_result, report_path: str):
        """Create a fallback HTML report when docs generation fails."""
        self._save_custom_report(validation_result, report_path)
    
    def _create_error_html_report(self, error_message: str, report_path: str):
        """Create an error HTML report when validation fails."""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Data Quality Error Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .error {{ color: #F44336; background: #ffebee; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Data Quality Report - Error</h1>
            <div class="error">
                <h2>Validation Failed</h2>
                <p><strong>DataSource ID:</strong> {self.datasource_id}</p>
                <p><strong>Error:</strong> {error_message}</p>
                <p><strong>Time:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get the comprehensive quality report."""
        return self.quality_report
    
    def _run_fallback_pipeline(self, df: pd.DataFrame, output_dir: str) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
        """
        Run a fallback data quality pipeline when Great Expectations is not available.
        
        This provides basic data validation and cleaning using pandas only.
        """
        logger.info(f"Running fallback data quality pipeline for DataSource {self.datasource_id}")
        
        try:
            # Basic data profiling with JSON serializable types
            profile = {
                'total_rows': int(len(df)),
                'total_columns': int(len(df.columns)),
                'missing_values': {str(col): int(val) for col, val in df.isnull().sum().items()},
                'data_types': {str(col): str(dtype) for col, dtype in df.dtypes.items()},
                'memory_usage': int(df.memory_usage(deep=True).sum()),
                'duplicate_rows': int(df.duplicated().sum())
            }
            
            # Basic data cleaning
            cleaned_df = df.copy()
            
            # Remove completely empty rows and columns
            cleaned_df = cleaned_df.dropna(how='all', axis=0)  # Remove empty rows
            cleaned_df = cleaned_df.dropna(how='all', axis=1)  # Remove empty columns
            
            # Convert numeric columns with better type inference
            for col in cleaned_df.columns:
                # Try to convert to numeric if it looks numeric
                if cleaned_df[col].dtype == 'object':
                    try:
                        # Check if column contains mostly numeric values
                        numeric_series = pd.to_numeric(cleaned_df[col], errors='coerce')
                        non_null_count = numeric_series.count()
                        total_count = len(cleaned_df[col])
                        
                        # If more than 80% of values are numeric, convert the column
                        if non_null_count / total_count > 0.8:
                            cleaned_df[col] = numeric_series
                    except:
                        pass
            
            # Generate fallback report
            cleaning_summary = {
                'original_rows': int(len(df)),
                'cleaned_rows': int(len(cleaned_df)),
                'rows_removed': int(len(df) - len(cleaned_df)),
                'original_columns': int(len(df.columns)),
                'cleaned_columns': int(len(cleaned_df.columns)),
                'columns_removed': int(len(df.columns) - len(cleaned_df.columns)),
                'type_conversions': []
            }
            
            # Track type conversions
            for col in cleaned_df.columns:
                if col in df.columns and str(df[col].dtype) != str(cleaned_df[col].dtype):
                    cleaning_summary['type_conversions'].append({
                        'column': col,
                        'from_type': str(df[col].dtype),
                        'to_type': str(cleaned_df[col].dtype)
                    })
            
            # Quality report
            quality_report = {
                'pipeline_type': 'fallback',
                'great_expectations_available': False,
                'data_profile': profile,
                'cleaning_summary': cleaning_summary,
                'validation_timestamp': timezone.now().isoformat(),
                'status': 'completed_with_fallback'
            }
            
            # Generate HTML report
            report_path = os.path.join(output_dir, f"fallback_quality_report_ds_{self.datasource_id}.html")
            self._create_fallback_html_report(quality_report, report_path)
            
            return cleaned_df, quality_report, report_path
            
        except Exception as e:
            logger.error(f"Fallback pipeline failed for DataSource {self.datasource_id}: {e}")
            # Return original data with minimal error report
            error_report = {
                'pipeline_type': 'fallback',
                'error': str(e),
                'pipeline_failed': True,
                'status': 'failed'
            }
            error_path = os.path.join(output_dir, f"fallback_error_report_ds_{self.datasource_id}.html")
            self._create_error_html_report(str(e), error_path)
            return df, error_report, error_path
    
    def _create_fallback_html_report(self, quality_report: Dict[str, Any], report_path: str):
        """Create an HTML report for the fallback pipeline."""
        profile = quality_report.get('data_profile', {})
        cleaning = quality_report.get('cleaning_summary', {})
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Fallback Data Quality Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .warning {{ background: #FFF3CD; border: 1px solid #FFEAA7; color: #856404; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                .section h2 {{ color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }}
                .metric {{ display: inline-block; margin: 10px 15px 10px 0; padding: 10px; background: #E3F2FD; border-radius: 4px; }}
                .metric strong {{ color: #1976D2; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .type-change {{ background-color: #E8F5E8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Data Quality Report (Fallback Mode)</h1>
                    <p>DataSource ID: {self.datasource_id}</p>
                    <p>Generated: {quality_report.get('validation_timestamp', 'Unknown')}</p>
                </div>
                
                <div class="warning">
                    <strong>Note:</strong> This report was generated using fallback validation because Great Expectations is not available.
                    For comprehensive data validation, please install Great Expectations.
                </div>
                
                <div class="section">
                    <h2>Data Profile</h2>
                    <div class="metric"><strong>Total Rows:</strong> {profile.get('total_rows', 'N/A')}</div>
                    <div class="metric"><strong>Total Columns:</strong> {profile.get('total_columns', 'N/A')}</div>
                    <div class="metric"><strong>Duplicate Rows:</strong> {profile.get('duplicate_rows', 'N/A')}</div>
                    <div class="metric"><strong>Memory Usage:</strong> {profile.get('memory_usage', 'N/A')} bytes</div>
                </div>
                
                <div class="section">
                    <h2>Data Cleaning Summary</h2>
                    <div class="metric"><strong>Rows Removed:</strong> {cleaning.get('rows_removed', 'N/A')}</div>
                    <div class="metric"><strong>Columns Removed:</strong> {cleaning.get('columns_removed', 'N/A')}</div>
                    <div class="metric"><strong>Type Conversions:</strong> {len(cleaning.get('type_conversions', []))}</div>
                </div>
                
                <div class="section">
                    <h2>Missing Values by Column</h2>
                    <table>
                        <tr><th>Column</th><th>Missing Values</th></tr>
        """
        
        # Add missing values table
        for col, missing in profile.get('missing_values', {}).items():
            html_content += f"<tr><td>{col}</td><td>{missing}</td></tr>"
        
        html_content += """
                    </table>
                </div>
                
                <div class="section">
                    <h2>Data Types</h2>
                    <table>
                        <tr><th>Column</th><th>Data Type</th></tr>
        """
        
        # Add data types table
        for col, dtype in profile.get('data_types', {}).items():
            html_content += f"<tr><td>{col}</td><td>{dtype}</td></tr>"
        
        html_content += """
                    </table>
                </div>
        """
        
        # Add type conversions if any
        if cleaning.get('type_conversions'):
            html_content += """
                <div class="section">
                    <h2>Type Conversions Applied</h2>
                    <table>
                        <tr><th>Column</th><th>From Type</th><th>To Type</th></tr>
            """
            for conversion in cleaning['type_conversions']:
                html_content += f"""
                    <tr class="type-change">
                        <td>{conversion['column']}</td>
                        <td>{conversion['from_type']}</td>
                        <td>{conversion['to_type']}</td>
                    </tr>
                """
            html_content += "</table></div>"
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


def run_data_quality_pipeline(df: pd.DataFrame, datasource_id: str, output_dir: str) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    """
    Run the complete data quality pipeline for a DataFrame.
    
    Args:
        df: Input pandas DataFrame
        datasource_id: Unique identifier for the DataSource
        output_dir: Directory to save quality reports
        
    Returns:
        Tuple containing:
        - Cleaned DataFrame
        - Quality report dictionary
        - Path to HTML report file
    """
    service = DataQualityService(datasource_id)
    
    # Check if Great Expectations is available
    if not GX_AVAILABLE:
        logger.warning("Great Expectations not available, using fallback validation")
        return service._run_fallback_pipeline(df, output_dir)
    
    try:
        # Initialize Great Expectations
        if not service.initialize_gx_context():
            logger.warning("GX context initialization failed, falling back to basic validation")
            return service._run_fallback_pipeline(df, output_dir)
        
        # Load and profile data
        if not service.load_and_profile_data(df):
            logger.warning("Failed to load and profile data, falling back to basic validation")
            return service._run_fallback_pipeline(df, output_dir)
        
        # Infer and validate data types
        cleaned_df = service.infer_and_validate_data_types()
        
        # Add comprehensive expectations
        service.add_comprehensive_expectations()
        
        # Generate quality report
        success, report_path = service.validate_and_generate_report(output_dir)
        
        if not success:
            logger.warning(f"Quality validation failed for DataSource {datasource_id}")
        
        return cleaned_df, service.get_quality_report(), report_path
        
    except Exception as e:
        logger.error(f"Data quality pipeline failed for DataSource {datasource_id}: {e}")
        logger.info("Falling back to basic validation")
        return service._run_fallback_pipeline(df, output_dir)
