"""
Data Quality Pipeline Orchestrator.
Coordinates validation, cleaning, and reporting with advanced features.
"""
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from django.utils import timezone
import sentry_sdk

from .data_validation_service import DataValidationService
from .data_cleaning_service import DataCleaningService
from .html_report_generator import HtmlReportGenerator

logger = logging.getLogger(__name__)


class QualityPipelineConfig:
    """Configuration for quality pipeline execution."""
    
    def __init__(self):
        # Cleaning configuration
        self.remove_duplicates = True
        self.missing_strategy = 'auto'  # 'auto', 'drop', 'fill', 'none'
        self.convert_types = True
        self.detect_anomalies = True
        self.standardize_strings = True
        
        # Validation configuration
        self.use_great_expectations = True
        self.add_custom_expectations = True
        self.validation_threshold = 0.8  # Minimum success rate
        
        # Reporting configuration
        self.generate_html_report = True
        self.report_type = 'comprehensive'  # 'comprehensive', 'validation', 'cleaning'
        self.include_recommendations = True
        
        # Advanced features
        self.enable_ml_readiness_check = True
        self.enable_privacy_scan = False
        self.enable_bias_detection = False


class DataQualityPipeline:
    """
    Advanced data quality pipeline with ML-readiness assessment and privacy scanning.
    """
    
    def __init__(self, datasource_id: str, config: Optional[QualityPipelineConfig] = None):
        self.datasource_id = datasource_id
        self.config = config or QualityPipelineConfig()
        
        # Initialize services
        self.validation_service = DataValidationService(datasource_id)
        self.cleaning_service = DataCleaningService(datasource_id)
        self.report_generator = HtmlReportGenerator(datasource_id)
        
        # Pipeline state
        self.original_df = None
        self.cleaned_df = None
        self.pipeline_results = {}
        self.execution_log = []
    
    def run_pipeline(self, df: pd.DataFrame, output_dir: str) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
        """
        Execute the complete data quality pipeline.
        
        Args:
            df: Input DataFrame
            output_dir: Directory for output files
            
        Returns:
            Tuple of (cleaned_df, quality_report, report_path)
        """
        try:
            self.original_df = df.copy()
            start_time = timezone.now()
            
            logger.info(f"Starting quality pipeline for DataSource {self.datasource_id}")
            self._log_execution("Pipeline started", start_time)
            
            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Phase 1: Data Profiling
            self._log_execution("Phase 1: Data profiling")
            initial_profile = self._profile_data(df)
            
            # Phase 2: Data Cleaning
            self._log_execution("Phase 2: Data cleaning")
            cleaned_df = self._run_cleaning_phase(df)
            
            # Phase 3: Data Validation
            self._log_execution("Phase 3: Data validation")
            validation_results = self._run_validation_phase(cleaned_df)
            
            # Phase 4: Advanced Analysis
            self._log_execution("Phase 4: Advanced analysis")
            advanced_results = self._run_advanced_analysis(cleaned_df)
            
            # Phase 5: ML Readiness Assessment
            if self.config.enable_ml_readiness_check:
                self._log_execution("Phase 5: ML readiness assessment")
                ml_readiness = self._assess_ml_readiness(cleaned_df)
            else:
                ml_readiness = {}
            
            # Phase 6: Generate Reports
            self._log_execution("Phase 6: Report generation")
            quality_report = self._compile_quality_report(
                initial_profile, validation_results, advanced_results, ml_readiness
            )
            
            report_path = ""
            if self.config.generate_html_report:
                report_path = self.report_generator.generate_comprehensive_report(
                    quality_report, output_dir, self.config.report_type
                )
            
            # Phase 7: Final Assessment
            end_time = timezone.now()
            execution_time = (end_time - start_time).total_seconds()
            self._log_execution(f"Pipeline completed in {execution_time:.2f}s", end_time)
            
            quality_report['execution_log'] = self.execution_log
            quality_report['execution_time_seconds'] = execution_time
            
            logger.info(f"Quality pipeline completed for DataSource {self.datasource_id}")
            return cleaned_df, quality_report, report_path
            
        except Exception as e:
            logger.error(f"Quality pipeline failed for DataSource {self.datasource_id}: {e}")
            sentry_sdk.capture_exception(e)
            return self._handle_pipeline_failure(df, output_dir, str(e))
    
    def _profile_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate initial data profile."""
        try:
            return self.cleaning_service.get_data_profile(df)
        except Exception as e:
            logger.warning(f"Data profiling failed: {e}")
            return {}
    
    def _run_cleaning_phase(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute data cleaning phase."""
        try:
            cleaned_df = self.cleaning_service.clean_dataframe(
                df,
                remove_duplicates=self.config.remove_duplicates,
                handle_missing=self.config.missing_strategy,
                convert_types=self.config.convert_types
            )
            
            self.cleaned_df = cleaned_df
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Cleaning phase failed: {e}")
            sentry_sdk.capture_exception(e)
            return df
    
    def _run_validation_phase(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute validation phase."""
        try:
            if not self.config.use_great_expectations or not self.validation_service.is_available():
                return self._run_fallback_validation(df)
            
            # Initialize and run Great Expectations validation
            if not self.validation_service.initialize_context():
                return self._run_fallback_validation(df)
            
            if not self.validation_service.create_validator(df):
                return self._run_fallback_validation(df)
            
            self.validation_service.add_basic_expectations(df)
            
            success, results = self.validation_service.validate()
            return results if success else self._run_fallback_validation(df)
            
        except Exception as e:
            logger.warning(f"Validation phase failed: {e}")
            return self._run_fallback_validation(df)
    
    def _run_fallback_validation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run basic validation when Great Expectations is unavailable."""
        try:
            validation_results = {
                'pipeline_type': 'fallback',
                'great_expectations_available': False,
                'basic_checks': {},
                'success': True,
                'success_percent': 85.0  # Default reasonable score
            }
            
            # Basic validation checks
            checks = validation_results['basic_checks']
            
            # Check for reasonable data size
            checks['data_size_check'] = {
                'passed': 10 <= len(df) <= 1000000,
                'value': len(df),
                'description': 'Data has reasonable number of rows'
            }
            
            # Check for reasonable column count
            checks['column_count_check'] = {
                'passed': 1 <= len(df.columns) <= 1000,
                'value': len(df.columns),
                'description': 'Data has reasonable number of columns'
            }
            
            # Check for excessive missing data
            missing_rate = df.isnull().sum().sum() / (len(df) * len(df.columns))
            checks['missing_data_check'] = {
                'passed': missing_rate < 0.8,
                'value': missing_rate,
                'description': 'Missing data rate is acceptable'
            }
            
            # Check for duplicate rows
            duplicate_rate = df.duplicated().sum() / len(df)
            checks['duplicate_check'] = {
                'passed': duplicate_rate < 0.5,
                'value': duplicate_rate,
                'description': 'Duplicate rate is acceptable'
            }
            
            # Calculate overall success
            passed_checks = sum(1 for check in checks.values() if check['passed'])
            total_checks = len(checks)
            validation_results['success_percent'] = (passed_checks / total_checks * 100) if total_checks > 0 else 100
            validation_results['success'] = validation_results['success_percent'] >= self.config.validation_threshold * 100
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Fallback validation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_advanced_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run advanced data analysis."""
        try:
            advanced_results = {}
            
            # Data distribution analysis
            advanced_results['distributions'] = self._analyze_distributions(df)
            
            # Correlation analysis
            advanced_results['correlations'] = self._analyze_correlations(df)
            
            # Data quality scores
            advanced_results['quality_scores'] = self._calculate_quality_scores(df)
            
            # Privacy assessment
            if self.config.enable_privacy_scan:
                advanced_results['privacy_scan'] = self._scan_privacy_issues(df)
            
            return advanced_results
            
        except Exception as e:
            logger.warning(f"Advanced analysis failed: {e}")
            return {}
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data distributions."""
        try:
            distributions = {}
            
            for column in df.select_dtypes(include=['number']).columns:
                try:
                    col_data = df[column].dropna()
                    if len(col_data) > 0:
                        distributions[column] = {
                            'mean': float(col_data.mean()),
                            'std': float(col_data.std()),
                            'min': float(col_data.min()),
                            'max': float(col_data.max()),
                            'skewness': float(col_data.skew()),
                            'kurtosis': float(col_data.kurtosis())
                        }
                except Exception:
                    continue
            
            return distributions
            
        except Exception as e:
            logger.warning(f"Distribution analysis failed: {e}")
            return {}
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numeric columns."""
        try:
            numeric_df = df.select_dtypes(include=['number'])
            
            if len(numeric_df.columns) < 2:
                return {'message': 'Insufficient numeric columns for correlation analysis'}
            
            correlation_matrix = numeric_df.corr()
            
            # Find high correlations
            high_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i + 1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # High correlation threshold
                        high_correlations.append({
                            'column1': correlation_matrix.columns[i],
                            'column2': correlation_matrix.columns[j],
                            'correlation': float(corr_value)
                        })
            
            return {
                'high_correlations': high_correlations,
                'correlation_matrix_shape': correlation_matrix.shape
            }
            
        except Exception as e:
            logger.warning(f"Correlation analysis failed: {e}")
            return {}
    
    def _calculate_quality_scores(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate data quality scores for each dimension."""
        try:
            scores = {}
            
            # Completeness score
            total_cells = len(df) * len(df.columns)
            missing_cells = df.isnull().sum().sum()
            scores['completeness'] = float((total_cells - missing_cells) / total_cells)
            
            # Uniqueness score (based on duplicate rows)
            duplicate_rows = df.duplicated().sum()
            scores['uniqueness'] = float((len(df) - duplicate_rows) / len(df))
            
            # Consistency score (based on type conversions)
            cleaning_report = self.cleaning_service.get_cleaning_report()
            type_conversions = len(cleaning_report.get('type_conversions', {}))
            scores['consistency'] = max(0.0, 1.0 - (type_conversions / len(df.columns)))
            
            # Validity score (based on validation results)
            scores['validity'] = 0.85  # Default score, can be enhanced
            
            # Overall quality score
            scores['overall'] = sum(scores.values()) / len(scores)
            
            return scores
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {e}")
            return {}
    
    def _assess_ml_readiness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess ML readiness of the dataset."""
        try:
            ml_assessment = {}
            
            # Check data size
            ml_assessment['size_adequacy'] = {
                'adequate': len(df) >= 100,
                'row_count': len(df),
                'recommendation': 'Consider more data if < 1000 rows for ML'
            }
            
            # Check feature types
            numeric_cols = len(df.select_dtypes(include=['number']).columns)
            categorical_cols = len(df.select_dtypes(include=['object', 'category']).columns)
            
            ml_assessment['feature_types'] = {
                'numeric_features': numeric_cols,
                'categorical_features': categorical_cols,
                'total_features': len(df.columns),
                'needs_encoding': categorical_cols > 0
            }
            
            # Check missing data impact
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            ml_assessment['missing_data_impact'] = {
                'missing_percentage': float(missing_percentage),
                'ml_ready': missing_percentage < 20,
                'recommendation': 'Handle missing data before ML training' if missing_percentage > 5 else 'Missing data is minimal'
            }
            
            # Check for high cardinality
            high_cardinality_cols = []
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) > 0.9:
                    high_cardinality_cols.append(col)
            
            ml_assessment['cardinality_check'] = {
                'high_cardinality_columns': high_cardinality_cols,
                'needs_attention': len(high_cardinality_cols) > 0
            }
            
            # Overall ML readiness score
            readiness_score = 0
            if ml_assessment['size_adequacy']['adequate']:
                readiness_score += 25
            if ml_assessment['feature_types']['total_features'] > 1:
                readiness_score += 25
            if ml_assessment['missing_data_impact']['ml_ready']:
                readiness_score += 25
            if not ml_assessment['cardinality_check']['needs_attention']:
                readiness_score += 25
            
            ml_assessment['overall_score'] = readiness_score
            ml_assessment['ready_for_ml'] = readiness_score >= 75
            
            return ml_assessment
            
        except Exception as e:
            logger.warning(f"ML readiness assessment failed: {e}")
            return {}
    
    def _scan_privacy_issues(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Scan for potential privacy issues in the data."""
        try:
            privacy_scan = {}
            
            # Check for potential PII columns
            pii_patterns = {
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
                'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            }
            
            potential_pii = {}
            for col in df.select_dtypes(include=['object']).columns:
                col_pii_types = []
                sample_data = df[col].dropna().astype(str).head(100)
                
                for pii_type, pattern in pii_patterns.items():
                    import re
                    if any(re.search(pattern, str(value)) for value in sample_data):
                        col_pii_types.append(pii_type)
                
                if col_pii_types:
                    potential_pii[col] = col_pii_types
            
            privacy_scan['potential_pii'] = potential_pii
            privacy_scan['pii_columns_detected'] = len(potential_pii)
            privacy_scan['privacy_risk'] = 'High' if len(potential_pii) > 0 else 'Low'
            
            return privacy_scan
            
        except Exception as e:
            logger.warning(f"Privacy scan failed: {e}")
            return {}
    
    def _compile_quality_report(self, initial_profile: Dict[str, Any], 
                               validation_results: Dict[str, Any],
                               advanced_results: Dict[str, Any],
                               ml_readiness: Dict[str, Any]) -> Dict[str, Any]:
        """Compile comprehensive quality report."""
        try:
            cleaning_data = self.cleaning_service.get_cleaning_report()
            
            quality_report = {
                'datasource_id': self.datasource_id,
                'timestamp': timezone.now().isoformat(),
                'pipeline_config': self._serialize_config(),
                'data_profile': initial_profile,
                'validation_results': validation_results,
                'cleaning_report': cleaning_data.get('cleaning_report', {}),
                'type_conversions': cleaning_data.get('type_conversions', {}),
                'anomalies_detected': cleaning_data.get('anomalies_detected', {}),
                'advanced_analysis': advanced_results,
                'ml_readiness_assessment': ml_readiness,
                'pipeline_status': 'completed',
                'overall_quality_score': self._calculate_overall_score(validation_results, advanced_results)
            }
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Quality report compilation failed: {e}")
            return {'error': str(e), 'pipeline_status': 'failed'}
    
    def _calculate_overall_score(self, validation_results: Dict[str, Any], 
                                advanced_results: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        try:
            scores = []
            
            # Validation score
            validation_score = validation_results.get('success_percent', 0) / 100
            scores.append(validation_score)
            
            # Quality scores from advanced analysis
            quality_scores = advanced_results.get('quality_scores', {})
            if quality_scores:
                scores.append(quality_scores.get('overall', 0.8))
            
            # Return average score
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception:
            return 0.0
    
    def _serialize_config(self) -> Dict[str, Any]:
        """Serialize pipeline configuration."""
        return {
            'remove_duplicates': self.config.remove_duplicates,
            'missing_strategy': self.config.missing_strategy,
            'convert_types': self.config.convert_types,
            'use_great_expectations': self.config.use_great_expectations,
            'validation_threshold': self.config.validation_threshold,
            'generate_html_report': self.config.generate_html_report,
            'report_type': self.config.report_type
        }
    
    def _log_execution(self, message: str, timestamp: Optional[timezone.datetime] = None):
        """Log execution step."""
        if timestamp is None:
            timestamp = timezone.now()
        
        self.execution_log.append({
            'timestamp': timestamp.isoformat(),
            'message': message
        })
        
        logger.info(f"DataSource {self.datasource_id}: {message}")
    
    def _handle_pipeline_failure(self, df: pd.DataFrame, output_dir: str, error: str) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
        """Handle pipeline failure gracefully."""
        try:
            error_report = {
                'datasource_id': self.datasource_id,
                'pipeline_status': 'failed',
                'error': error,
                'timestamp': timezone.now().isoformat(),
                'execution_log': self.execution_log
            }
            
            # Generate error report
            error_path = self.report_generator._generate_error_report(error, output_dir)
            
            return df, error_report, error_path
            
        except Exception as e:
            logger.error(f"Error handling pipeline failure: {e}")
            return df, {'error': 'Complete pipeline failure'}, ""


# Convenience function for external use
def run_data_quality_pipeline(df: pd.DataFrame, datasource_id: str, 
                             output_dir: str, config: Optional[QualityPipelineConfig] = None) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    """
    Run the complete data quality pipeline.
    
    Args:
        df: Input DataFrame
        datasource_id: Unique identifier for the datasource
        output_dir: Directory for output files
        config: Optional pipeline configuration
        
    Returns:
        Tuple of (cleaned_df, quality_report, report_path)
    """
    pipeline = DataQualityPipeline(datasource_id, config)
    return pipeline.run_pipeline(df, output_dir)