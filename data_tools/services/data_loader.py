"""
Data loader service for loading data from various file formats.
"""

import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def load_data_from_parquet(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load data from a Parquet file.
    
    Args:
        file_path: Path to the Parquet file
        
    Returns:
        DataFrame if successful, None if failed
    """
    try:
        logger.info(f"Loading data from Parquet file: {file_path}")
        df = pd.read_parquet(file_path)
        logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Failed to load Parquet file {file_path}: {e}")
        return None


def load_data_from_csv(file_path: str, **kwargs) -> Optional[pd.DataFrame]:
    """
    Load data from a CSV file with automatic delimiter detection.
    
    Args:
        file_path: Path to the CSV file
        **kwargs: Additional arguments for pd.read_csv
        
    Returns:
        DataFrame if successful, None if failed
    """
    try:
        logger.info(f"Loading data from CSV file: {file_path}")
        
        # Try different delimiters and encodings
        delimiters = [',', ';', '\t']
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for delimiter in delimiters:
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, **kwargs)
                    logger.info(f"Successfully loaded CSV with delimiter '{delimiter}' and encoding '{encoding}': {len(df)} rows and {len(df.columns)} columns")
                    return df
                except Exception as e:
                    logger.debug(f"Failed with delimiter '{delimiter}' and encoding '{encoding}': {e}")
                    continue
        
        # If all attempts fail, try with default parameters
        df = pd.read_csv(file_path, **kwargs)
        logger.info(f"Successfully loaded CSV with default parameters: {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load CSV file {file_path}: {e}")
        return None


def load_data_from_excel(file_path: str, **kwargs) -> Optional[pd.DataFrame]:
    """
    Load data from an Excel file.
    
    Args:
        file_path: Path to the Excel file
        **kwargs: Additional arguments for pd.read_excel
        
    Returns:
        DataFrame if successful, None if failed
    """
    try:
        logger.info(f"Loading data from Excel file: {file_path}")
        df = pd.read_excel(file_path, **kwargs)
        logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Failed to load Excel file {file_path}: {e}")
        return None


def load_data_from_file(file_path: str, file_format: str = None, **kwargs) -> Optional[pd.DataFrame]:
    """
    Load data from a file, automatically detecting format if not specified.
    
    Args:
        file_path: Path to the file
        file_format: Explicit format ('csv', 'parquet', 'excel'), auto-detect if None
        **kwargs: Additional arguments for the specific loader
        
    Returns:
        DataFrame if successful, None if failed
    """
    try:
        # Auto-detect format from file extension if not specified
        if file_format is None:
            if file_path.endswith('.parquet'):
                file_format = 'parquet'
            elif file_path.endswith('.csv'):
                file_format = 'csv'
            elif file_path.endswith(('.xls', '.xlsx')):
                file_format = 'excel'
            else:
                logger.warning(f"Cannot auto-detect format for file: {file_path}")
                return None
        
        # Load using appropriate method
        if file_format == 'parquet':
            return load_data_from_parquet(file_path)
        elif file_format == 'csv':
            return load_data_from_csv(file_path, **kwargs)
        elif file_format == 'excel':
            return load_data_from_excel(file_path, **kwargs)
        else:
            logger.error(f"Unsupported file format: {file_format}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to load data from file {file_path}: {e}")
        return None


def get_data_info(df: pd.DataFrame) -> dict:
    """
    Get basic information about a DataFrame.
    
    Args:
        df: The DataFrame to analyze
        
    Returns:
        Dictionary with basic info about the DataFrame
    """
    try:
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'column_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum()
        }
    except Exception as e:
        logger.error(f"Failed to get data info: {e}")
        return {}
