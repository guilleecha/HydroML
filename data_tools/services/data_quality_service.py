"""
Data Quality Service - Modernized Interface.
This is the new entry point that uses the refactored modular services.
Maintains backward compatibility while providing enhanced functionality.
"""
import logging
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from .quality_pipeline import DataQualityPipeline, QualityPipelineConfig
import sentry_sdk

logger = logging.getLogger(__name__)

# For backward compatibility - maintain the original function signature
def run_data_quality_pipeline(df: pd.DataFrame, datasource_id: str, output_dir: str) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    """
    Run the complete data quality pipeline - Enhanced version.
    
    This function now uses the new modular architecture while maintaining
    backward compatibility with the original interface.
    
    Args:
        df: Input pandas DataFrame
        datasource_id: Unique identifier for the DataSource
        output_dir: Directory to save quality reports
        
    Returns:
        Tuple containing:
        - Cleaned DataFrame
        - Quality report dictionary
        - Path to HTML report file
        
    Enhancements in new version:
    - Advanced type conversion algorithms
    - ML readiness assessment
    - Modern responsive HTML reports
    - Better anomaly detection
    - Privacy scanning capabilities
    - Comprehensive data profiling
    """
    try:
        # Create enhanced configuration
        config = QualityPipelineConfig()
        
        # Create and run pipeline
        pipeline = DataQualityPipeline(datasource_id, config)
        return pipeline.run_pipeline(df, output_dir)
        
    except Exception as e:
        logger.error(f"Enhanced data quality pipeline failed for DataSource {datasource_id}: {e}")
        sentry_sdk.capture_exception(e)
        
        # Fallback to legacy implementation if available
        try:
            from .data_quality_service_legacy import run_data_quality_pipeline as legacy_pipeline
            logger.warning("Falling back to legacy quality pipeline")
            return legacy_pipeline(df, datasource_id, output_dir)
        except ImportError:
            logger.error("Legacy pipeline also unavailable")
            return df, {'error': str(e), 'pipeline_status': 'failed'}, ""


# Export the enhanced service classes for direct use
from .data_validation_service import DataValidationService
from .data_cleaning_service import DataCleaningService  
from .html_report_generator import HtmlReportGenerator

__all__ = [
    'run_data_quality_pipeline',
    'DataValidationService', 
    'DataCleaningService',
    'HtmlReportGenerator',
    'DataQualityPipeline',
    'QualityPipelineConfig'
]