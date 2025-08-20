"""
Data Cleaning Service.
Advanced data cleaning with improved algorithms and ML-ready preprocessing.
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from sklearn.preprocessing import LabelEncoder
from django.utils import timezone
import sentry_sdk

logger = logging.getLogger(__name__)


class DataCleaningService:
    """
    Advanced data cleaning service with ML-ready preprocessing capabilities.
    """
    
    def __init__(self, datasource_id: str):
        self.datasource_id = datasource_id
        self.cleaning_report = {}
        self.type_conversions = {}
        self.anomalies_detected = {}
        
    def clean_dataframe(self, df: pd.DataFrame, 
                       remove_duplicates: bool = True,
                       handle_missing: str = 'auto',
                       convert_types: bool = True) -> pd.DataFrame:
        """
        Comprehensive data cleaning pipeline.
        
        Args:
            df: Input DataFrame
            remove_duplicates: Whether to remove duplicate rows
            handle_missing: Strategy for missing values ('auto', 'drop', 'fill')
            convert_types: Whether to perform type conversions
            
        Returns:
            Cleaned DataFrame
        """
        try:
            original_shape = df.shape
            cleaned_df = df.copy()
            
            # Initialize cleaning report
            self.cleaning_report = {
                'original_shape': original_shape,
                'timestamp': timezone.now().isoformat(),
                'operations_performed': []
            }
            
            # 1. Remove completely empty rows/columns
            cleaned_df = self._remove_empty_data(cleaned_df)
            
            # 2. Handle duplicates
            if remove_duplicates:
                cleaned_df = self._remove_duplicates(cleaned_df)
            
            # 3. Type conversions with improved detection
            if convert_types:
                cleaned_df = self._smart_type_conversion(cleaned_df)
            
            # 4. Handle missing values
            if handle_missing != 'none':
                cleaned_df = self._handle_missing_values(cleaned_df, handle_missing)
            
            # 5. Detect and handle anomalies
            cleaned_df = self._detect_anomalies(cleaned_df)
            
            # 6. Standardize string values
            cleaned_df = self._standardize_strings(cleaned_df)
            
            # Final report
            self.cleaning_report['final_shape'] = cleaned_df.shape
            self.cleaning_report['rows_removed'] = original_shape[0] - cleaned_df.shape[0]
            self.cleaning_report['columns_removed'] = original_shape[1] - cleaned_df.shape[1]
            
            logger.info(f"Data cleaning completed for DataSource {self.datasource_id}")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            sentry_sdk.capture_exception(e)
            return df
    
    def _remove_empty_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove completely empty rows and columns."""
        try:
            original_shape = df.shape
            
            # Remove empty rows and columns
            df_clean = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            
            removed_rows = original_shape[0] - df_clean.shape[0]
            removed_cols = original_shape[1] - df_clean.shape[1]
            
            if removed_rows > 0 or removed_cols > 0:
                self.cleaning_report['operations_performed'].append({
                    'operation': 'remove_empty_data',
                    'rows_removed': removed_rows,
                    'columns_removed': removed_cols
                })
            
            return df_clean
            
        except Exception as e:
            logger.warning(f"Failed to remove empty data: {e}")
            return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows with detailed reporting."""
        try:
            original_count = len(df)
            df_clean = df.drop_duplicates()
            duplicates_removed = original_count - len(df_clean)
            
            if duplicates_removed > 0:
                self.cleaning_report['operations_performed'].append({
                    'operation': 'remove_duplicates',
                    'duplicates_removed': duplicates_removed,
                    'percentage': round((duplicates_removed / original_count) * 100, 2)
                })
            
            return df_clean
            
        except Exception as e:
            logger.warning(f"Failed to remove duplicates: {e}")
            return df
    
    def _smart_type_conversion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced type conversion with improved detection algorithms."""
        try:
            conversions_made = []
            
            for column in df.columns:
                original_type = str(df[column].dtype)
                
                # Skip if already numeric or datetime
                if pd.api.types.is_numeric_dtype(df[column]) or pd.api.types.is_datetime64_any_dtype(df[column]):
                    continue
                
                # Try different conversions
                new_series, conversion_type = self._attempt_conversions(df[column])
                
                if conversion_type != 'no_conversion':
                    df[column] = new_series
                    conversions_made.append({
                        'column': column,
                        'from_type': original_type,
                        'to_type': str(new_series.dtype),
                        'conversion_method': conversion_type
                    })
            
            if conversions_made:
                self.cleaning_report['operations_performed'].append({
                    'operation': 'type_conversions',
                    'conversions': conversions_made
                })
                self.type_conversions = {conv['column']: conv for conv in conversions_made}
            
            return df
            
        except Exception as e:
            logger.warning(f"Type conversion failed: {e}")
            return df
    
    def _attempt_conversions(self, series: pd.Series) -> Tuple[pd.Series, str]:
        """Attempt various type conversions on a series."""
        # 1. Try datetime conversion
        datetime_series, is_datetime = self._try_datetime_conversion(series)
        if is_datetime:
            return datetime_series, 'datetime'
        
        # 2. Try numeric conversion
        numeric_series, is_numeric = self._try_numeric_conversion(series)
        if is_numeric:
            return numeric_series, 'numeric'
        
        # 3. Try boolean conversion
        bool_series, is_bool = self._try_boolean_conversion(series)
        if is_bool:
            return bool_series, 'boolean'
        
        # 4. Try categorical conversion
        cat_series, is_categorical = self._try_categorical_conversion(series)
        if is_categorical:
            return cat_series, 'categorical'
        
        return series, 'no_conversion'
    
    def _try_datetime_conversion(self, series: pd.Series) -> Tuple[pd.Series, bool]:
        """Try to convert series to datetime."""
        try:
            # Common datetime patterns
            datetime_patterns = [
                '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S',
                '%d-%m-%Y', '%Y/%m/%d'
            ]
            
            # Check if values look like dates
            sample_values = series.dropna().astype(str).head(10)
            
            for pattern in datetime_patterns:
                try:
                    pd.to_datetime(sample_values, format=pattern)
                    # If successful, convert entire series
                    converted = pd.to_datetime(series, format=pattern, errors='coerce')
                    success_rate = converted.notna().sum() / len(series.dropna())
                    
                    if success_rate > 0.8:  # 80% success rate
                        return converted, True
                except:
                    continue
            
            # Try infer_datetime_format
            converted = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            success_rate = converted.notna().sum() / len(series.dropna())
            
            if success_rate > 0.8:
                return converted, True
                
        except Exception as e:
            logger.debug(f"Datetime conversion failed: {e}")
        
        return series, False
    
    def _try_numeric_conversion(self, series: pd.Series) -> Tuple[pd.Series, bool]:
        """Improved numeric conversion with better detection."""
        try:
            # Clean common numeric patterns
            cleaned_series = series.astype(str).str.replace(',', '')  # Remove commas
            cleaned_series = cleaned_series.str.replace('$', '')      # Remove currency
            cleaned_series = cleaned_series.str.replace('%', '')      # Remove percentages
            cleaned_series = cleaned_series.str.strip()               # Remove whitespace
            
            # Try conversion
            numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
            
            # Calculate success rate
            non_null_original = series.dropna()
            non_null_converted = numeric_series.dropna()
            
            if len(non_null_original) > 0:
                success_rate = len(non_null_converted) / len(non_null_original)
                
                # Convert if 85% or more values are numeric
                if success_rate >= 0.85:
                    return numeric_series, True
                    
        except Exception as e:
            logger.debug(f"Numeric conversion failed: {e}")
        
        return series, False
    
    def _try_boolean_conversion(self, series: pd.Series) -> Tuple[pd.Series, bool]:
        """Try to convert series to boolean."""
        try:
            # Common boolean patterns
            true_values = {'true', 'yes', 'y', '1', 'on', 'si', 'sí'}
            false_values = {'false', 'no', 'n', '0', 'off'}
            
            lowercase_series = series.astype(str).str.lower().str.strip()
            unique_values = set(lowercase_series.dropna().unique())
            
            # Check if all values are boolean-like
            if unique_values.issubset(true_values.union(false_values)):
                bool_series = lowercase_series.map(
                    lambda x: True if x in true_values else (False if x in false_values else None)
                )
                return bool_series, True
                
        except Exception as e:
            logger.debug(f"Boolean conversion failed: {e}")
        
        return series, False
    
    def _try_categorical_conversion(self, series: pd.Series) -> Tuple[pd.Series, bool]:
        """Try to convert series to categorical if low cardinality."""
        try:
            unique_count = series.nunique()
            total_count = len(series.dropna())
            
            # Convert to categorical if cardinality is low relative to size
            if total_count > 50 and unique_count / total_count < 0.1:  # Less than 10% unique
                return series.astype('category'), True
                
        except Exception as e:
            logger.debug(f"Categorical conversion failed: {e}")
        
        return series, False
    
    def _handle_missing_values(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """Handle missing values with various strategies."""
        try:
            missing_info = []
            
            for column in df.columns:
                missing_count = df[column].isna().sum()
                if missing_count == 0:
                    continue
                
                missing_pct = (missing_count / len(df)) * 100
                
                if strategy == 'auto':
                    # Smart missing value handling
                    if missing_pct > 70:
                        # Drop column if >70% missing
                        df = df.drop(columns=[column])
                        missing_info.append({
                            'column': column,
                            'action': 'dropped_column',
                            'missing_percentage': missing_pct
                        })
                    elif pd.api.types.is_numeric_dtype(df[column]):
                        # Fill numeric with median
                        df[column] = df[column].fillna(df[column].median())
                        missing_info.append({
                            'column': column,
                            'action': 'filled_median',
                            'missing_percentage': missing_pct
                        })
                    else:
                        # Fill categorical with mode
                        mode_value = df[column].mode()
                        if len(mode_value) > 0:
                            df[column] = df[column].fillna(mode_value[0])
                        missing_info.append({
                            'column': column,
                            'action': 'filled_mode',
                            'missing_percentage': missing_pct
                        })
                
                elif strategy == 'drop':
                    df = df.dropna(subset=[column])
            
            if missing_info:
                self.cleaning_report['operations_performed'].append({
                    'operation': 'handle_missing_values',
                    'strategy': strategy,
                    'actions': missing_info
                })
            
            return df
            
        except Exception as e:
            logger.warning(f"Missing value handling failed: {e}")
            return df
    
    def _detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and handle statistical anomalies."""
        try:
            anomalies_detected = []
            
            for column in df.select_dtypes(include=[np.number]).columns:
                # IQR method for outlier detection
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                
                if len(outliers) > 0:
                    anomalies_detected.append({
                        'column': column,
                        'outlier_count': len(outliers),
                        'outlier_percentage': (len(outliers) / len(df)) * 100,
                        'bounds': {'lower': lower_bound, 'upper': upper_bound}
                    })
            
            if anomalies_detected:
                self.anomalies_detected = {item['column']: item for item in anomalies_detected}
                self.cleaning_report['operations_performed'].append({
                    'operation': 'anomaly_detection',
                    'anomalies': anomalies_detected
                })
            
            return df
            
        except Exception as e:
            logger.warning(f"Anomaly detection failed: {e}")
            return df
    
    def _standardize_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize string columns."""
        try:
            standardized_columns = []
            
            for column in df.select_dtypes(include=['object']).columns:
                if df[column].dtype == 'object':
                    # Basic string cleaning
                    original_unique = df[column].nunique()
                    
                    # Clean strings
                    df[column] = df[column].astype(str).str.strip()
                    df[column] = df[column].str.replace(r'\s+', ' ', regex=True)  # Multiple spaces
                    
                    new_unique = df[column].nunique()
                    
                    if original_unique != new_unique:
                        standardized_columns.append({
                            'column': column,
                            'unique_before': original_unique,
                            'unique_after': new_unique
                        })
            
            if standardized_columns:
                self.cleaning_report['operations_performed'].append({
                    'operation': 'string_standardization',
                    'columns': standardized_columns
                })
            
            return df
            
        except Exception as e:
            logger.warning(f"String standardization failed: {e}")
            return df
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Get comprehensive cleaning report."""
        return {
            'cleaning_report': self.cleaning_report,
            'type_conversions': self.type_conversions,
            'anomalies_detected': self.anomalies_detected
        }
    
    def get_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate enhanced data profile."""
        try:
            return {
                'total_rows': int(len(df)),
                'total_columns': int(len(df.columns)),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                'missing_values': {str(col): int(val) for col, val in df.isnull().sum().items()},
                'data_types': {str(col): str(dtype) for col, dtype in df.dtypes.items()},
                'duplicate_rows': int(df.duplicated().sum()),
                'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
                'datetime_columns': len(df.select_dtypes(include=['datetime']).columns),
                'unique_counts': {str(col): int(df[col].nunique()) for col in df.columns}
            }
        except Exception as e:
            logger.error(f"Data profiling failed: {e}")
            sentry_sdk.capture_exception(e)
            return {}