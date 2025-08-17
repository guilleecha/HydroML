# connectors/services/database_connection_service.py

import logging
import pandas as pd
from typing import Tuple, Optional, Dict, Any
from django.conf import settings
from django.contrib.auth.models import User

from ..models import DatabaseConnection
from projects.models import DataSource

logger = logging.getLogger(__name__)


class DatabaseConnectionService:
    """Service for managing database connections and data import operations."""
    
    @staticmethod
    def test_connection(connection: DatabaseConnection) -> Tuple[bool, str]:
        """
        Test a database connection.
        
        Args:
            connection: DatabaseConnection instance to test
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Import here to avoid dependency issues if SQLAlchemy is not installed
            import sqlalchemy
            from sqlalchemy import create_engine, text
            
            # Create engine with connection string
            engine = create_engine(connection.connection_string)
            
            # Test connection with a simple query
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            logger.info(f"Database connection test successful for {connection.name}")
            return True, "Connection successful"
            
        except ImportError:
            error_msg = "SQLAlchemy is required for database connections. Please install it."
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(f"Database connection test failed for {connection.name}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def get_table_list(connection: DatabaseConnection) -> Tuple[bool, Any]:
        """
        Get list of tables from a database connection.
        
        Args:
            connection: DatabaseConnection instance
            
        Returns:
            Tuple of (success: bool, tables: list or error_message: str)
        """
        try:
            import sqlalchemy
            from sqlalchemy import create_engine, inspect
            
            engine = create_engine(connection.connection_string)
            inspector = inspect(engine)
            
            # Get table names
            tables = inspector.get_table_names()
            
            logger.info(f"Retrieved {len(tables)} tables from {connection.name}")
            return True, tables
            
        except ImportError:
            error_msg = "SQLAlchemy is required for database connections."
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Failed to retrieve tables: {str(e)}"
            logger.error(f"Failed to get tables from {connection.name}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def get_table_columns(connection: DatabaseConnection, table_name: str) -> Tuple[bool, Any]:
        """
        Get column information for a specific table.
        
        Args:
            connection: DatabaseConnection instance
            table_name: Name of the table
            
        Returns:
            Tuple of (success: bool, columns: list or error_message: str)
        """
        try:
            import sqlalchemy
            from sqlalchemy import create_engine, inspect
            
            engine = create_engine(connection.connection_string)
            inspector = inspect(engine)
            
            # Get column information
            columns = inspector.get_columns(table_name)
            
            # Format column information
            column_info = [
                {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col.get('nullable', True),
                    'default': col.get('default'),
                    'primary_key': col.get('primary_key', False)
                }
                for col in columns
            ]
            
            logger.info(f"Retrieved {len(column_info)} columns from table {table_name} in {connection.name}")
            return True, column_info
            
        except ImportError:
            error_msg = "SQLAlchemy is required for database connections."
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Failed to retrieve columns: {str(e)}"
            logger.error(f"Failed to get columns from table {table_name} in {connection.name}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def execute_query(
        connection: DatabaseConnection, 
        query: str, 
        limit: Optional[int] = None
    ) -> Tuple[bool, Any]:
        """
        Execute a SQL query and return results as a DataFrame.
        
        Args:
            connection: DatabaseConnection instance
            query: SQL query to execute
            limit: Optional limit for number of rows to return
            
        Returns:
            Tuple of (success: bool, dataframe: pd.DataFrame or error_message: str)
        """
        try:
            import sqlalchemy
            from sqlalchemy import create_engine
            
            engine = create_engine(connection.connection_string)
            
            # Add LIMIT clause if specified and not already present
            if limit and 'LIMIT' not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {limit}"
            
            # Execute query and read into DataFrame
            df = pd.read_sql_query(query, engine)
            
            logger.info(f"Query executed successfully from {connection.name}, returned {len(df)} rows")
            return True, df
            
        except ImportError:
            error_msg = "SQLAlchemy and pandas are required for database connections."
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(f"Query execution failed for {connection.name}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def create_datasource_from_query(
        connection: DatabaseConnection,
        query: str,
        datasource_name: str,
        project,
        description: Optional[str] = None
    ) -> Tuple[bool, Any]:
        """
        Execute a query and create a DataSource from the results.
        
        Args:
            connection: DatabaseConnection instance
            query: SQL query to execute
            datasource_name: Name for the new DataSource
            project: Project instance to create the DataSource in
            description: Optional description for the DataSource
            
        Returns:
            Tuple of (success: bool, datasource: DataSource or error_message: str)
        """
        try:
            # Execute the query
            success, result = DatabaseConnectionService.execute_query(connection, query)
            
            if not success:
                return False, result
            
            df = result
            
            # Validate DataFrame
            if df.empty:
                return False, "Query returned no data"
            
            # Create temporary file for the data
            import tempfile
            import os
            from django.core.files.base import ContentFile
            
            # Convert DataFrame to CSV
            csv_content = df.to_csv(index=False)
            csv_file = ContentFile(csv_content.encode('utf-8'), name=f"{datasource_name}.csv")
            
            # Create DataSource
            datasource = DataSource.objects.create(
                name=datasource_name,
                description=description or f"Data imported from {connection.name}",
                project=project,
                data_type='ORIGINAL',
                status='READY',
                file=csv_file
            )
            
            # Update metadata in quality_report field
            datasource.quality_report = {
                'connection_name': connection.name,
                'connection_type': connection.database_type,
                'query': query,
                'rows': len(df),
                'columns': list(df.columns),
                'import_source': 'database_connection'
            }
            datasource.save()
            
            logger.info(f"DataSource {datasource_name} created successfully from {connection.name}")
            return True, datasource
            
        except Exception as e:
            error_msg = f"Failed to create DataSource: {str(e)}"
            logger.error(f"Failed to create DataSource from {connection.name}: {error_msg}")
            return False, error_msg
