"""
Export Format Handlers - Utilities for converting DataFrames to different export formats.

This module provides format-specific conversion utilities that handle the nuances
of each export format while maintaining data integrity and performance.
"""

import os
import logging
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportFormatHandler:
    """
    Handler for different export formats with format-specific optimizations.
    
    This class provides static methods for converting pandas DataFrames to
    various export formats with customizable options for each format.
    """
    
    @staticmethod
    def to_csv(dataframe: pd.DataFrame, file_path: str, options: Optional[Dict[str, Any]] = None) -> None:
        """
        Convert DataFrame to CSV format.
        
        Args:
            dataframe: Pandas DataFrame to convert
            file_path: Output file path
            options: CSV-specific options
                - delimiter: Field delimiter (default: ',')
                - encoding: File encoding (default: 'utf-8')
                - include_header: Include column headers (default: True)
                - quote_char: Quote character (default: '"')
                - index: Include row index (default: False)
                - na_rep: String representation of NaN (default: '')
        
        Raises:
            Exception: If conversion fails
        """
        try:
            # Default options
            csv_options = {
                'sep': ',',
                'encoding': 'utf-8',
                'header': True,
                'quotechar': '"',
                'index': False,
                'na_rep': ''
            }
            
            # Override with user options
            if options:
                # Map user-friendly names to pandas parameters
                option_mapping = {
                    'delimiter': 'sep',
                    'include_header': 'header',
                    'quote_char': 'quotechar'
                }
                
                for key, value in options.items():
                    pandas_key = option_mapping.get(key, key)
                    if pandas_key in csv_options:
                        csv_options[pandas_key] = value
            
            # Handle large datasets efficiently
            if len(dataframe) > 100000:
                logger.info(f"Large dataset detected ({len(dataframe)} rows). Using chunked CSV writing.")
                # For very large datasets, we might want to implement chunked writing
                # For now, just use standard pandas to_csv with optimizations
                csv_options['chunksize'] = 10000
            
            # Convert and save
            dataframe.to_csv(file_path, **csv_options)
            
            logger.info(f"DataFrame converted to CSV: {file_path} ({len(dataframe)} rows)")
            
        except Exception as e:
            logger.error(f"Error converting DataFrame to CSV: {str(e)}")
            raise Exception(f"CSV conversion failed: {str(e)}")
    
    @staticmethod
    def to_json(dataframe: pd.DataFrame, file_path: str, options: Optional[Dict[str, Any]] = None) -> None:
        """
        Convert DataFrame to JSON format.
        
        Args:
            dataframe: Pandas DataFrame to convert
            file_path: Output file path
            options: JSON-specific options
                - orient: JSON orientation ('records', 'index', 'values', 'split', 'table')
                - date_format: Date format ('iso', 'epoch')
                - indent: JSON indentation (int or None)
                - force_ascii: Ensure ASCII output (default: False)
        
        Raises:
            Exception: If conversion fails
        """
        try:
            # Default options
            json_options = {
                'orient': 'records',
                'date_format': 'iso',
                'indent': 2,
                'force_ascii': False
            }
            
            # Override with user options
            if options:
                for key, value in options.items():
                    if key in json_options:
                        json_options[key] = value
            
            # Handle large datasets
            if len(dataframe) > 50000:
                logger.warning(
                    f"Large dataset for JSON export ({len(dataframe)} rows). "
                    "Consider using a different format for better performance."
                )
            
            # Handle datetime columns
            dataframe = ExportFormatHandler._prepare_datetime_columns(dataframe)
            
            # Convert and save
            with open(file_path, 'w', encoding='utf-8') as f:
                dataframe.to_json(f, **json_options)
            
            logger.info(f"DataFrame converted to JSON: {file_path} ({len(dataframe)} rows)")
            
        except Exception as e:
            logger.error(f"Error converting DataFrame to JSON: {str(e)}")
            raise Exception(f"JSON conversion failed: {str(e)}")
    
    @staticmethod
    def to_parquet(dataframe: pd.DataFrame, file_path: str, options: Optional[Dict[str, Any]] = None) -> None:
        """
        Convert DataFrame to Parquet format.
        
        Args:
            dataframe: Pandas DataFrame to convert
            file_path: Output file path
            options: Parquet-specific options
                - compression: Compression algorithm ('snappy', 'gzip', 'brotli', 'lz4')
                - engine: Parquet engine ('auto', 'pyarrow', 'fastparquet')
                - index: Include row index (default: False)
        
        Raises:
            Exception: If conversion fails
        """
        try:
            # Default options
            parquet_options = {
                'compression': 'snappy',
                'engine': 'auto',
                'index': False
            }
            
            # Override with user options
            if options:
                for key, value in options.items():
                    if key in parquet_options:
                        parquet_options[key] = value
            
            # Validate compression option
            valid_compressions = ['snappy', 'gzip', 'brotli', 'lz4', None]
            if parquet_options['compression'] not in valid_compressions:
                logger.warning(
                    f"Invalid compression '{parquet_options['compression']}'. "
                    "Using 'snappy' instead."
                )
                parquet_options['compression'] = 'snappy'
            
            # Prepare DataFrame for Parquet
            dataframe = ExportFormatHandler._prepare_parquet_dataframe(dataframe)
            
            # Convert and save
            dataframe.to_parquet(file_path, **parquet_options)
            
            logger.info(f"DataFrame converted to Parquet: {file_path} ({len(dataframe)} rows)")
            
        except Exception as e:
            logger.error(f"Error converting DataFrame to Parquet: {str(e)}")
            raise Exception(f"Parquet conversion failed: {str(e)}")
    
    @staticmethod
    def to_excel(dataframe: pd.DataFrame, file_path: str, options: Optional[Dict[str, Any]] = None) -> None:
        """
        Convert DataFrame to Excel format.
        
        Args:
            dataframe: Pandas DataFrame to convert
            file_path: Output file path
            options: Excel-specific options
                - sheet_name: Name of the Excel sheet (default: 'Sheet1')
                - index: Include row index (default: False)
                - freeze_panes: Tuple for freeze panes (row, col)
                - startrow: Upper left cell row to dump data frame (default: 0)
                - startcol: Upper left cell column to dump data frame (default: 0)
        
        Raises:
            Exception: If conversion fails
        """
        try:
            # Default options
            excel_options = {
                'sheet_name': 'Sheet1',
                'index': False,
                'startrow': 0,
                'startcol': 0
            }
            
            # Override with user options
            if options:
                for key, value in options.items():
                    if key in excel_options:
                        excel_options[key] = value
            
            # Check dataset size for Excel limits
            max_rows = 1048576  # Excel row limit
            max_cols = 16384    # Excel column limit
            
            if len(dataframe) > max_rows:
                logger.error(
                    f"Dataset too large for Excel ({len(dataframe)} rows). "
                    f"Excel supports maximum {max_rows} rows."
                )
                raise Exception("Dataset exceeds Excel row limit")
            
            if len(dataframe.columns) > max_cols:
                logger.error(
                    f"Dataset has too many columns ({len(dataframe.columns)}). "
                    f"Excel supports maximum {max_cols} columns."
                )
                raise Exception("Dataset exceeds Excel column limit")
            
            # Prepare DataFrame for Excel
            dataframe = ExportFormatHandler._prepare_excel_dataframe(dataframe)
            
            # Create Excel writer with openpyxl engine
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Write DataFrame
                dataframe.to_excel(writer, **excel_options)
                
                # Apply freeze panes if specified
                if 'freeze_panes' in options and options['freeze_panes']:
                    try:
                        worksheet = writer.sheets[excel_options['sheet_name']]
                        worksheet.freeze_panes = options['freeze_panes']
                    except Exception as e:
                        logger.warning(f"Could not apply freeze panes: {str(e)}")
            
            logger.info(f"DataFrame converted to Excel: {file_path} ({len(dataframe)} rows)")
            
        except Exception as e:
            logger.error(f"Error converting DataFrame to Excel: {str(e)}")
            raise Exception(f"Excel conversion failed: {str(e)}")
    
    # Helper methods
    
    @staticmethod
    def _prepare_datetime_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Prepare datetime columns for better JSON serialization."""
        df = dataframe.copy()
        
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                # Convert to string to ensure proper JSON serialization
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            elif pd.api.types.is_period_dtype(df[col]):
                df[col] = df[col].astype(str)
        
        return df
    
    @staticmethod
    def _prepare_parquet_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for Parquet format compatibility."""
        df = dataframe.copy()
        
        # Handle mixed-type columns that might cause issues with Parquet
        for col in df.columns:
            # Convert object columns with mixed types to string
            if df[col].dtype == 'object':
                # Check if column has mixed numeric and non-numeric data
                try:
                    pd.to_numeric(df[col], errors='raise')
                except (ValueError, TypeError):
                    # Mixed types detected, convert to string
                    df[col] = df[col].astype(str)
            
            # Handle complex data types
            elif pd.api.types.is_complex_dtype(df[col]):
                df[col] = df[col].astype(str)
        
        return df
    
    @staticmethod
    def _prepare_excel_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for Excel format compatibility."""
        df = dataframe.copy()
        
        # Handle very long strings that might cause Excel issues
        max_cell_length = 32767  # Excel cell character limit
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Truncate strings that are too long
                mask = df[col].astype(str).str.len() > max_cell_length
                if mask.any():
                    logger.warning(
                        f"Truncating {mask.sum()} cells in column '{col}' "
                        f"to fit Excel cell limit ({max_cell_length} characters)"
                    )
                    df.loc[mask, col] = df.loc[mask, col].astype(str).str[:max_cell_length]
            
            # Handle timezone-aware datetime columns
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                    # Convert to timezone-naive datetime for Excel compatibility
                    df[col] = df[col].dt.tz_localize(None)
        
        return df
    
    @staticmethod
    def get_supported_formats() -> Dict[str, Dict[str, Any]]:
        """
        Get information about supported export formats.
        
        Returns:
            Dict with format information including options and limitations
        """
        return {
            'csv': {
                'name': 'Comma-Separated Values',
                'extension': '.csv',
                'mime_type': 'text/csv',
                'supports_large_datasets': True,
                'max_size_recommendation': 'No limit (streaming supported)',
                'options': {
                    'delimiter': 'Field delimiter (default: ",")',
                    'encoding': 'File encoding (default: "utf-8")',
                    'include_header': 'Include column headers (default: true)',
                    'quote_char': 'Quote character (default: "\"")'
                }
            },
            'json': {
                'name': 'JavaScript Object Notation',
                'extension': '.json',
                'mime_type': 'application/json',
                'supports_large_datasets': False,
                'max_size_recommendation': '50,000 rows (memory intensive)',
                'options': {
                    'orient': 'JSON structure (records, index, values, split, table)',
                    'date_format': 'Date format (iso, epoch)',
                    'indent': 'JSON indentation (number of spaces)'
                }
            },
            'parquet': {
                'name': 'Apache Parquet',
                'extension': '.parquet',
                'mime_type': 'application/octet-stream',
                'supports_large_datasets': True,
                'max_size_recommendation': 'Excellent for large datasets',
                'options': {
                    'compression': 'Compression algorithm (snappy, gzip, brotli, lz4)',
                    'engine': 'Parquet engine (auto, pyarrow, fastparquet)'
                }
            },
            'excel': {
                'name': 'Microsoft Excel',
                'extension': '.xlsx',
                'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'supports_large_datasets': False,
                'max_size_recommendation': '1,048,576 rows × 16,384 columns (Excel limits)',
                'options': {
                    'sheet_name': 'Name of the Excel sheet',
                    'freeze_panes': 'Freeze panes position (row, column)',
                    'startrow': 'Starting row for data',
                    'startcol': 'Starting column for data'
                }
            }
        }