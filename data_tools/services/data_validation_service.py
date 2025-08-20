"""
Great Expectations Data Validation Service.
Specialized module for advanced data validation using Great Expectations.
"""
import logging
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import sentry_sdk

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


class DataValidationService:
    """
    Advanced data validation using Great Expectations.
    Focused solely on validation logic and expectation management.
    """
    
    def __init__(self, datasource_id: str):
        self.datasource_id = datasource_id
        self.context = None
        self.validator = None
        self.validation_results = {}
        
    def is_available(self) -> bool:
        """Check if Great Expectations is available."""
        return GX_AVAILABLE
        
    def initialize_context(self) -> bool:
        """Initialize Great Expectations context."""
        if not GX_AVAILABLE:
            logger.warning("Great Expectations not available")
            return False
            
        try:
            self.context = gx.get_context(mode="ephemeral")
            logger.info(f"GX context initialized for DataSource {self.datasource_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize GX context: {e}")
            sentry_sdk.capture_exception(e)
            return False
    
    def create_validator(self, df: pd.DataFrame) -> bool:
        """Create validator from DataFrame."""
        try:
            # Create data asset
            data_asset = self.context.data_sources.add_pandas(
                "pandas_datasource"
            ).add_dataframe_asset(
                name=f"datasource_{self.datasource_id}",
                dataframe=df
            )
            
            # Create batch request and expectation suite
            batch_request = data_asset.build_batch_request()
            suite_name = f"quality_suite_{self.datasource_id}"
            suite = self.context.suites.add(ExpectationSuite(name=suite_name))
            
            # Create validator
            self.validator = self.context.get_validator(
                batch_request=batch_request,
                expectation_suite=suite
            )
            
            logger.info(f"Validator created for DataSource {self.datasource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create validator: {e}")
            sentry_sdk.capture_exception(e)
            return False
    
    def add_basic_expectations(self, df: pd.DataFrame):
        """Add basic data quality expectations."""
        try:
            # Table-level expectations
            self.validator.expect_table_row_count_to_be_between(
                min_value=1, max_value=1000000
            )
            self.validator.expect_table_column_count_to_be_between(
                min_value=1, max_value=1000
            )
            
            # Column-level expectations
            for column in df.columns:
                self._add_column_expectations(df, column)
                
        except Exception as e:
            logger.error(f"Failed to add basic expectations: {e}")
            sentry_sdk.capture_exception(e)
    
    def _add_column_expectations(self, df: pd.DataFrame, column: str):
        """Add expectations for a specific column."""
        try:
            # Check null percentage
            null_percentage = df[column].isna().sum() / len(df)
            
            if null_percentage > 0.5:
                # High null rate - document it
                self.validator.expect_column_values_to_not_be_null(
                    column=column, mostly=0.1
                )
            
            # ID column uniqueness
            if 'id' in column.lower() or column.lower() in ['index', 'key']:
                self.validator.expect_column_values_to_be_unique(column=column)
            
            # Numeric column ranges
            if pd.api.types.is_numeric_dtype(df[column]):
                self.validator.expect_column_values_to_be_between(
                    column=column,
                    min_value=df[column].min(),
                    max_value=df[column].max()
                )
                
        except Exception as e:
            logger.warning(f"Failed to add expectations for column {column}: {e}")
    
    def add_type_expectations(self, column: str, expected_type):
        """Add type validation expectations for converted columns."""
        try:
            if pd.api.types.is_numeric_dtype(expected_type):
                self.validator.expect_column_values_to_be_of_type(
                    column=column, type_="float64"
                )
            
            self.validator.expect_column_values_to_not_be_null(
                column=column, mostly=0.1
            )
            
        except Exception as e:
            logger.warning(f"Failed to add type expectations for {column}: {e}")
    
    def validate(self) -> Tuple[bool, Dict[str, Any]]:
        """Run validation and return results."""
        try:
            validation_result = self.validator.validate()
            
            self.validation_results = {
                'success': validation_result.success,
                'evaluated_expectations': validation_result.statistics.get('evaluated_expectations', 0),
                'successful_expectations': validation_result.statistics.get('successful_expectations', 0),
                'unsuccessful_expectations': validation_result.statistics.get('unsuccessful_expectations', 0),
                'success_percent': validation_result.statistics.get('success_percent', 0),
                'raw_result': validation_result
            }
            
            return True, self.validation_results
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            sentry_sdk.capture_exception(e)
            return False, {'error': str(e)}
    
    def build_data_docs(self) -> Optional[str]:
        """Build and return data docs URL."""
        try:
            self.context.build_data_docs()
            docs_sites = self.context.get_docs_sites_urls()
            return docs_sites[0] if docs_sites else None
        except Exception as e:
            logger.error(f"Failed to build data docs: {e}")
            sentry_sdk.capture_exception(e)
            return None
    
    def get_results(self) -> Dict[str, Any]:
        """Get validation results."""
        return self.validation_results