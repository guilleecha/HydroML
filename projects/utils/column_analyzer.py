# projects/utils/column_analyzer.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ColumnAnalyzer:
    """Analyzes columns and generates ML suitability flags"""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.flags = {}
    
    def analyze_all_columns(self) -> Dict[str, Any]:
        """Analyze all columns and return flags dictionary"""
        try:
            for column in self.df.columns:
                self.flags[column] = self._analyze_column(column)
            
            self.flags['_metadata'] = {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns)
            }
            
            return self.flags
        except Exception as e:
            logger.error(f"Error analyzing columns: {str(e)}")
            return {}
    
    def _analyze_column(self, column: str) -> Dict[str, Any]:
        """Analyze a single column"""
        series = self.df[column]
        flags = {
            'data_type': str(series.dtype),
            'non_null_count': int(series.count()),
            'null_count': int(series.isnull().sum()),
            'has_nan': bool(series.isnull().any()),
            'nan_percentage': float(series.isnull().sum() / len(series) * 100),
            'unique_values': int(series.nunique()),
            'warnings': [],
            'suitable_for_target': True,
            'suitable_for_features': True
        }
        
        # Analyze based on data type
        if pd.api.types.is_numeric_dtype(series):
            flags.update(self._analyze_numeric_column(series))
        elif isinstance(series.dtype, pd.CategoricalDtype) or series.dtype == 'object':
            flags.update(self._analyze_categorical_column(series))
        elif pd.api.types.is_datetime64_any_dtype(series):
            flags.update(self._analyze_datetime_column(series))
        
        # General ML suitability checks
        try:
            self._check_ml_suitability(flags, series)
        except Exception as e:
            logger.warning(f"Error in ML suitability check for column {column}: {str(e)}")
            flags['warnings'].append(f"Error en análisis: {str(e)}")
        
        return flags
    
    def _analyze_numeric_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze numeric column"""
        non_null_series = series.dropna()
        
        flags = {
            'is_numeric': True,
            'min_value': float(non_null_series.min()) if len(non_null_series) > 0 else None,
            'max_value': float(non_null_series.max()) if len(non_null_series) > 0 else None,
            'mean_value': float(non_null_series.mean()) if len(non_null_series) > 0 else None,
            'std_value': float(non_null_series.std()) if len(non_null_series) > 0 else None,
            'zero_variance': False,
            'outliers_count': 0,
            'outliers_percentage': 0.0,
            'warnings': []
        }
        
        if len(non_null_series) > 0:
            # Check for zero variance
            if non_null_series.var() == 0:
                flags['zero_variance'] = True
                flags['warnings'].append("Columna constante (varianza cero)")
                flags['suitable_for_features'] = False
            
            # Detect outliers using IQR method
            if len(non_null_series) > 4:  # Need at least 4 values for quartiles
                Q1 = non_null_series.quantile(0.25)
                Q3 = non_null_series.quantile(0.75)
                IQR = Q3 - Q1
                
                if IQR > 0:  # Avoid division by zero
                    outlier_mask = (non_null_series < (Q1 - 1.5 * IQR)) | (non_null_series > (Q3 + 1.5 * IQR))
                    outliers_count = outlier_mask.sum()
                    flags['outliers_count'] = int(outliers_count)
                    flags['outliers_percentage'] = float(outliers_count / len(non_null_series) * 100)
                    
                    if flags['outliers_percentage'] > 10:
                        flags['warnings'].append(f"Alto porcentaje de outliers ({flags['outliers_percentage']:.1f}%)")
        
        return flags
    
    def _analyze_categorical_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze categorical column"""
        non_null_series = series.dropna()
        value_counts = non_null_series.value_counts()
        
        flags = {
            'is_categorical': True,
            'category_count': len(value_counts),
            'most_frequent_value': str(value_counts.index[0]) if len(value_counts) > 0 else None,
            'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            'least_frequent_count': int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
            'high_cardinality': False,
            'needs_encoding': True,
            'warnings': []
        }
        
        # Check for high cardinality
        if flags['category_count'] > len(series) * 0.5:  # More than 50% unique values
            flags['high_cardinality'] = True
            flags['warnings'].append("Alta cardinalidad - muchas categorías únicas")
            flags['suitable_for_features'] = False
        
        # Check for class imbalance (if few categories)
        if flags['category_count'] <= 10 and len(value_counts) > 1:
            min_class_pct = flags['least_frequent_count'] / len(non_null_series) * 100
            if min_class_pct < 1:
                flags['warnings'].append(f"Clases muy desbalanceadas - clase minoritaria: {min_class_pct:.2f}%")
        
        return flags
    
    def _analyze_datetime_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze datetime column"""
        non_null_series = series.dropna()
        
        flags = {
            'is_datetime': True,
            'min_date': str(non_null_series.min()) if len(non_null_series) > 0 else None,
            'max_date': str(non_null_series.max()) if len(non_null_series) > 0 else None,
            'needs_feature_engineering': True,
            'warnings': []
        }
        
        flags['warnings'].append("Columna de fecha - requiere ingeniería de características para ML")
        flags['suitable_for_features'] = False  # Needs preprocessing
        flags['suitable_for_target'] = False    # Usually not suitable as target
        
        return flags
    
    def _check_ml_suitability(self, flags: Dict[str, Any], series: pd.Series):
        """Check general ML suitability and add warnings"""
        
        # Ensure warnings list exists
        if 'warnings' not in flags:
            flags['warnings'] = []
        
        # High percentage of missing values
        if flags['nan_percentage'] > 50:
            flags['warnings'].append(f"Demasiados valores faltantes ({flags['nan_percentage']:.1f}%)")
            flags['suitable_for_target'] = False
            flags['suitable_for_features'] = False
        elif flags['nan_percentage'] > 20:
            flags['warnings'].append(f"Alto porcentaje de valores faltantes ({flags['nan_percentage']:.1f}%)")
        
        # Single unique value (constant column)
        if flags['unique_values'] == 1:
            flags['warnings'].append("Columna constante - un solo valor único")
            flags['suitable_for_target'] = False
            flags['suitable_for_features'] = False
        
        # Too few non-null values
        if flags['non_null_count'] < 10:
            flags['warnings'].append("Muy pocos valores válidos para ML")
            flags['suitable_for_target'] = False
            flags['suitable_for_features'] = False
        
        # Target-specific checks
        if flags['unique_values'] == 2:
            flags['ml_problem_type'] = 'binary_classification'
        elif flags['unique_values'] < 20 and not flags.get('is_numeric', False):
            flags['ml_problem_type'] = 'multiclass_classification'
        elif flags.get('is_numeric', False):
            flags['ml_problem_type'] = 'regression'
        else:
            flags['ml_problem_type'] = 'unknown'
    
    @staticmethod
    def update_datasource_flags(datasource, force_update=False):
        """Update column flags for a datasource"""
        try:
            # Check if flags need updating
            if datasource.column_flags and not force_update:
                metadata = datasource.column_flags.get('_metadata', {})
                if metadata.get('analysis_timestamp'):
                    logger.info(f"Column flags already exist for {datasource.name}, skipping analysis")
                    return datasource.column_flags
            
            # Load dataframe
            if hasattr(datasource, 'get_dataframe'):
                df = datasource.get_dataframe()
            elif datasource.file:
                file_path = datasource.file.path
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path, nrows=10000)  # Sample for large files
                elif file_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path, nrows=10000)
                elif file_path.endswith('.parquet'):
                    df = pd.read_parquet(file_path)
                else:
                    raise ValueError(f"Unsupported file format: {file_path}")
            else:
                raise ValueError("Cannot access datasource data")
            
            # Analyze columns
            analyzer = ColumnAnalyzer(df)
            flags = analyzer.analyze_all_columns()
            
            # Update datasource
            datasource.column_flags = flags
            datasource.save(update_fields=['column_flags'])
            
            logger.info(f"Updated column flags for datasource {datasource.name}")
            return flags
            
        except Exception as e:
            logger.error(f"Error updating column flags for {datasource.name}: {str(e)}")
            return {}