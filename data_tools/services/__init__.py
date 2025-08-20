from .engine import process_datasource_to_df
from .recipes import create_fusion_recipe
# Import from main services module (legacy functions moved there)
# Import functions from main services file (using lazy imports in views to avoid circular dependencies)
try:
    from ..services import perform_data_fusion, perform_feature_engineering
except ImportError:
    # Graceful degradation if circular import still occurs
    perform_data_fusion = None
    perform_feature_engineering = None
from .data_analysis_service import *
from .session_service import *

# New modular quality services
from .data_validation_service import DataValidationService
from .data_cleaning_service import DataCleaningService
from .html_report_generator import HtmlReportGenerator
from .quality_pipeline import DataQualityPipeline, QualityPipelineConfig, run_data_quality_pipeline

# Export services
from .export_service import ExportService
from .export_formats import ExportFormatHandler
from .file_manager import ExportFileManager

# Legacy compatibility - import original function
try:
    from .data_quality_service_legacy import run_data_quality_pipeline as legacy_quality_pipeline
    LEGACY_QUALITY_AVAILABLE = True
except ImportError:
    LEGACY_QUALITY_AVAILABLE = False

__all__ = [
    "process_datasource_to_df",
    "create_fusion_recipe",
    "perform_data_fusion",
    "perform_feature_engineering",
    # Data analysis services
    "calculate_nullity_report",
    "generate_nullity_visualizations",
    # Session services
    "initialize_session",
    "load_current_dataframe",
    "save_current_dataframe",
    "session_exists",
    # New quality services
    "DataValidationService",
    "DataCleaningService", 
    "HtmlReportGenerator",
    "DataQualityPipeline",
    "QualityPipelineConfig",
    "run_data_quality_pipeline",
    # Export services
    "ExportService",
    "ExportFormatHandler",
    "ExportFileManager",
]