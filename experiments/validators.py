# experiments/validators.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from projects.models import DataSource
import sentry_sdk
import logging

logger = logging.getLogger(__name__)

class MLExperimentValidator:
    """Validates ML experiment configuration and data quality"""
    
    def __init__(self, datasource: DataSource, target_column: str, feature_columns: List[str], model_name: str):
        self.datasource = datasource
        self.target_column = target_column
        self.feature_columns = feature_columns
        self.model_name = model_name
        self.warnings = []
        self.errors = []
        self.data = None
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validations and return results"""
        try:
            # Set Sentry context for better error tracking
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("validation_type", "ml_experiment")
                scope.set_context("experiment_config", {
                    "datasource_id": str(self.datasource.id),
                    "model_name": self.model_name,
                    "target_column": self.target_column,
                    "n_features": len(self.feature_columns)
                })
            
            self._load_data()
            self._validate_using_column_flags()
            self._validate_data_quality()
            self._validate_target_column()
            self._validate_feature_columns()
            self._validate_model_requirements()
            self._validate_data_size()
            
            return {
                'valid': len(self.errors) == 0,
                'errors': self.errors,
                'warnings': self.warnings,
                'data_info': self._get_data_info() if self.data is not None else {}
            }
        except Exception as e:
            # Send detailed error to Sentry
            sentry_sdk.capture_exception(e)
            logger.error(f"Critical error during ML validation: {str(e)}", exc_info=True)
            self.errors.append(f"Error crítico durante validación: {str(e)}")
            return {
                'valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'data_info': {}
            }
    
    def _load_data(self):
        """Load data from datasource"""
        try:
            # Load data (implement based on your data loading logic)
            if hasattr(self.datasource, 'get_dataframe'):
                self.data = self.datasource.get_dataframe()
            elif hasattr(self.datasource, 'file') and self.datasource.file:
                file_path = self.datasource.file.path
                if file_path.endswith('.csv'):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith(('.xlsx', '.xls')):
                    self.data = pd.read_excel(file_path)
                elif file_path.endswith('.parquet'):
                    self.data = pd.read_parquet(file_path)
                else:
                    raise ValueError(f"Formato de archivo no soportado: {file_path}")
            else:
                raise ValueError("No se puede acceder a los datos del datasource")
                
        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.error(f"Error loading datasource {self.datasource.id}: {str(e)}", exc_info=True)
            self.errors.append(f"Error cargando datos: {str(e)}")
    
    def _validate_using_column_flags(self):
        """Use existing column_flags for validation"""
        if not self.datasource.column_flags:
            self.warnings.append("No hay análisis de calidad previo. Ejecutando validación básica.")
            return
            
        flags = self.datasource.column_flags
        
        # Validate target column using flags
        if self.target_column in flags:
            target_flags = flags[self.target_column]
            
            # Critical flags checks
            if not target_flags.get('suitable_for_target', True):
                self.errors.append(f"⚠️ Columna objetivo '{self.target_column}' no es adecuada para ML según análisis previo")
                
            if target_flags.get('zero_variance', False):
                self.errors.append(f"❌ Columna objetivo '{self.target_column}' tiene varianza cero (valores constantes)")
                
            if target_flags.get('nan_percentage', 0) > 10:
                self.errors.append(f"❌ Columna objetivo '{self.target_column}' tiene demasiados valores faltantes ({target_flags['nan_percentage']:.1f}%)")
                
            # Add warnings from flags
            target_warnings = target_flags.get('warnings', [])
            for warning in target_warnings:
                self.warnings.append(f"🎯 Objetivo: {warning}")
        
        # Validate feature columns using flags
        problematic_features = []
        high_missing_features = []
        
        for feature in self.feature_columns:
            if feature in flags:
                feature_flags = flags[feature]
                
                # Critical issues
                if not feature_flags.get('suitable_for_features', True):
                    problematic_features.append(feature)
                    
                if feature_flags.get('zero_variance', False):
                    self.errors.append(f"❌ Característica '{feature}' tiene varianza cero")
                    
                if feature_flags.get('nan_percentage', 0) > 25:
                    high_missing_features.append(f"{feature} ({feature_flags['nan_percentage']:.1f}%)")
                    
                # Model-specific validations using flags
                if feature_flags.get('high_cardinality', False) and self.model_name in ['RandomForestRegressor', 'GradientBoostingRegressor']:
                    self.warnings.append(f"🔧 Característica '{feature}' tiene alta cardinalidad - considera encoding")
                    
                # Add feature warnings
                feature_warnings = feature_flags.get('warnings', [])
                for warning in feature_warnings:
                    self.warnings.append(f"📊 {feature}: {warning}")
        
        if problematic_features:
            self.errors.append(f"❌ Características no aptas para ML: {', '.join(problematic_features)}")
            
        if high_missing_features:
            self.errors.append(f"❌ Características con demasiados valores faltantes: {', '.join(high_missing_features)}")
    
    def _validate_data_quality(self):
        """Validate overall data quality"""
        if self.data is None:
            return
            
        # Check for completely empty dataset
        if self.data.empty:
            self.errors.append("El dataset está vacío")
            return
        
        # Check minimum rows
        if len(self.data) < 10:
            self.errors.append(f"Dataset muy pequeño ({len(self.data)} filas). Mínimo recomendado: 10 filas")
        elif len(self.data) < 100:
            self.warnings.append(f"Dataset pequeño ({len(self.data)} filas). Recomendado: >100 filas para mejores resultados")
        
        # Check for duplicate rows
        duplicates = self.data.duplicated().sum()
        if duplicates > 0:
            if duplicates / len(self.data) > 0.5:
                self.warnings.append(f"Alto porcentaje de filas duplicadas ({duplicates}/{len(self.data)} - {duplicates/len(self.data)*100:.1f}%)")
            else:
                self.warnings.append(f"Se encontraron {duplicates} filas duplicadas")
    
    def _validate_target_column(self):
        """Validate target column"""
        if self.data is None or not self.target_column:
            return
        
        if self.target_column not in self.data.columns:
            self.errors.append(f"Columna objetivo '{self.target_column}' no existe en el dataset")
            return
        
        target_series = self.data[self.target_column]
        
        # Check for missing values
        missing_pct = target_series.isnull().sum() / len(target_series) * 100
        if missing_pct > 0:
            if missing_pct > 20:
                self.errors.append(f"Columna objetivo tiene demasiados valores faltantes ({missing_pct:.1f}%)")
            else:
                self.warnings.append(f"Columna objetivo tiene valores faltantes ({missing_pct:.1f}%)")
        
        # Check for single unique value
        unique_values = target_series.nunique()
        if unique_values == 1:
            self.errors.append("Columna objetivo tiene un solo valor único - no se puede entrenar el modelo")
        elif unique_values == 2:
            self.warnings.append("Problema de clasificación binaria detectado")
        elif unique_values < 10 and target_series.dtype == 'object':
            self.warnings.append(f"Problema de clasificación detectado ({unique_values} clases)")
        
        # Check for extreme class imbalance
        if target_series.dtype in ['object', 'category'] or unique_values < 20:
            value_counts = target_series.value_counts()
            min_class_pct = value_counts.min() / len(target_series) * 100
            if min_class_pct < 1:
                self.warnings.append(f"Clases muy desbalanceadas - clase minoritaria: {min_class_pct:.2f}%")
    
    def _validate_feature_columns(self):
        """Validate feature columns"""
        if self.data is None or not self.feature_columns:
            self.errors.append("No se han seleccionado columnas características")
            return
        
        missing_features = [col for col in self.feature_columns if col not in self.data.columns]
        if missing_features:
            self.errors.append(f"Columnas características no encontradas: {missing_features}")
            return
        
        features_df = self.data[self.feature_columns]
        
        # Check for features with too many missing values
        high_missing_features = []
        for col in self.feature_columns:
            missing_pct = features_df[col].isnull().sum() / len(features_df) * 100
            if missing_pct > 50:
                high_missing_features.append(f"{col} ({missing_pct:.1f}%)")
            elif missing_pct > 20:
                self.warnings.append(f"Característica '{col}' tiene muchos valores faltantes ({missing_pct:.1f}%)")
        
        if high_missing_features:
            self.errors.append(f"Características con demasiados valores faltantes: {', '.join(high_missing_features)}")
        
        # Check for zero variance features
        numeric_features = features_df.select_dtypes(include=[np.number])
        zero_var_features = []
        for col in numeric_features.columns:
            if numeric_features[col].var() == 0:
                zero_var_features.append(col)
        
        if zero_var_features:
            self.warnings.append(f"Características con varianza cero (constantes): {zero_var_features}")
        
        # Check for non-numeric features (may need encoding)
        categorical_features = features_df.select_dtypes(exclude=[np.number]).columns.tolist()
        if categorical_features and self.model_name in ['RandomForestRegressor', 'GradientBoostingRegressor']:
            self.warnings.append(f"Características categóricas detectadas: {categorical_features}. Necesitan codificación para {self.model_name}")
    
    def _validate_model_requirements(self):
        """Validate model-specific requirements"""
        if self.model_name == 'RandomForestRegressor':
            self._validate_random_forest()
        elif self.model_name == 'GradientBoostingRegressor':
            self._validate_gradient_boosting()
        # Add more model validations as needed
    
    def _validate_random_forest(self):
        """Validate Random Forest specific requirements"""
        if self.data is None:
            return
        
        # RF CANNOT handle NaN values - this is a critical error, not a warning
        selected_data = self.data[self.feature_columns + [self.target_column]]
        nan_columns = selected_data.columns[selected_data.isnull().any()].tolist()
        
        if nan_columns:
            self.errors.append(f"❌ Random Forest NO puede manejar valores NaN. Columnas problemáticas: {', '.join(nan_columns)}. Requiere imputación previa.")
            
            # Add specific NaN counts for user context
            for col in nan_columns:
                nan_count = selected_data[col].isnull().sum()
                nan_pct = nan_count / len(selected_data) * 100
                self.errors.append(f"   • {col}: {nan_count} valores NaN ({nan_pct:.1f}%)")
    
    def _validate_gradient_boosting(self):
        """Validate Gradient Boosting specific requirements"""
        if self.data is None:
            return
        
        # GB also struggles with NaN values - critical error
        selected_data = self.data[self.feature_columns + [self.target_column]]
        nan_columns = selected_data.columns[selected_data.isnull().any()].tolist()
        
        if nan_columns:
            self.errors.append(f"❌ Gradient Boosting NO maneja bien valores NaN. Columnas problemáticas: {', '.join(nan_columns)}. Requiere imputación previa.")
            
            for col in nan_columns:
                nan_count = selected_data[col].isnull().sum()
                nan_pct = nan_count / len(selected_data) * 100
                self.errors.append(f"   • {col}: {nan_count} valores NaN ({nan_pct:.1f}%)")
        
        # GB is sensitive to outliers - use flags if available
        if self.datasource.column_flags:
            high_outlier_features = []
            for col in self.feature_columns:
                if col in self.datasource.column_flags:
                    outlier_pct = self.datasource.column_flags[col].get('outliers_percentage', 0)
                    if outlier_pct > 15:  # More than 15% outliers
                        high_outlier_features.append(f"{col} ({outlier_pct:.1f}%)")
            
            if high_outlier_features:
                self.warnings.append(f"⚠️ Gradient Boosting es sensible a outliers. Características con muchos outliers: {', '.join(high_outlier_features)}")
        else:
            # Fallback to direct calculation if no flags
            numeric_cols = self.data[self.feature_columns].select_dtypes(include=[np.number]).columns
            outlier_features = []
            
            for col in numeric_cols:
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((self.data[col] < (Q1 - 1.5 * IQR)) | (self.data[col] > (Q3 + 1.5 * IQR))).sum()
                
                if outliers / len(self.data) > 0.15:  # More than 15% outliers
                    outlier_features.append(f"{col} ({outliers} outliers)")
            
            if outlier_features:
                self.warnings.append(f"⚠️ Gradient Boosting es sensible a outliers. Características con outliers: {', '.join(outlier_features)}")
    
    def _validate_data_size(self):
        """Validate data size for ML training"""
        if self.data is None:
            return
        
        n_samples = len(self.data)
        n_features = len(self.feature_columns)
        
        # Rule of thumb: at least 10 samples per feature
        min_samples = n_features * 10
        if n_samples < min_samples:
            self.warnings.append(f"Pocos datos para {n_features} características. Recomendado: >{min_samples} muestras, actual: {n_samples}")
        
        # Memory estimation for large datasets
        memory_usage_mb = self.data.memory_usage(deep=True).sum() / 1024 / 1024
        if memory_usage_mb > 500:  # > 500MB
            self.warnings.append(f"Dataset grande ({memory_usage_mb:.0f}MB). El entrenamiento puede ser lento.")
    
    def _get_data_info(self) -> Dict[str, Any]:
        """Get basic data information"""
        if self.data is None:
            return {}
        
        return {
            'n_samples': len(self.data),
            'n_features': len(self.feature_columns),
            'target_unique_values': self.data[self.target_column].nunique() if self.target_column in self.data.columns else 0,
            'missing_values_pct': self.data.isnull().sum().sum() / (len(self.data) * len(self.data.columns)) * 100,
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024 / 1024
        }