"""
SQL execution and query history API views.
Handles SQL queries against DataSources and maintains execution history.
"""
import time
import pandas as pd
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .mixins import BaseAPIView
from data_tools.models import QueryHistory


class SQLExecutionAPIView(BaseAPIView, View):
    """
    API view for executing SQL queries against DataSources.
    Automatically saves execution history for logged-in users.
    """
    
    def post(self, request):
        """
        Execute SQL query against a DataSource.
        
        Args:
            request: HTTP request with SQL query and datasource_id
            
        Returns:
            JsonResponse: Query results with execution metadata
        """
        try:
            # Extract parameters
            sql_query = request.POST.get('sql_query', '').strip()
            datasource_id = request.POST.get('datasource_id')
            
            if not sql_query:
                return self.error_response('Query SQL es requerido')
            
            if not datasource_id:
                return self.error_response('ID del DataSource es requerido')
            
            # Get and validate DataSource
            datasource = self.get_datasource(datasource_id)
            
            validation_error = self.validate_datasource_status(datasource)
            if validation_error:
                return self.error_response(validation_error['error'])
            
            # Execute query and measure time
            start_time = time.time()
            result = self._execute_sql_query(datasource, sql_query)
            execution_time = time.time() - start_time
            
            # Save to query history
            self._save_query_history(
                user=request.user,
                datasource=datasource,
                query=sql_query,
                success=True,
                execution_time=execution_time,
                rows_returned=len(result['data']) if result['data'] else 0
            )
            
            # Add execution metadata
            result.update({
                'execution_time': round(execution_time, 3),
                'timestamp': time.time()
            })
            
            return self.success_response(result)
            
        except Exception as e:
            # Save failed query to history
            try:
                self._save_query_history(
                    user=request.user,
                    datasource=datasource if 'datasource' in locals() else None,
                    query=sql_query if 'sql_query' in locals() else '',
                    success=False,
                    error_message=str(e)
                )
            except:
                pass  # Don't fail on history save error
            
            return self.error_response(f'Error ejecutando SQL: {str(e)}')
    
    def _execute_sql_query(self, datasource, sql_query):
        """
        Execute SQL query against DataSource using pandas.
        
        Args:
            datasource: DataSource object to query
            sql_query: SQL query string
            
        Returns:
            dict: Query results with data and metadata
        """
        # Basic SQL injection protection
        if self._is_unsafe_query(sql_query):
            raise ValueError("Query contiene operaciones no permitidas")
        
        # Read DataFrame
        from .datasource_api_views import DataSourceColumnsAPIView
        df = DataSourceColumnsAPIView()._read_dataframe(datasource.file.path)
        
        # Set up pandas SQL environment
        import sqlite3
        import io
        
        # Create in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        
        # Load DataFrame into SQLite
        df.to_sql('data', conn, index=False, if_exists='replace')
        
        try:
            # Execute query
            result_df = pd.read_sql_query(sql_query, conn)
            
            # Convert to JSON-serializable format
            data = []
            for _, row in result_df.iterrows():
                row_dict = {}
                for col in result_df.columns:
                    value = row[col]
                    # Handle pandas/numpy types
                    if pd.isna(value):
                        row_dict[col] = None
                    elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                        row_dict[col] = str(value)
                    else:
                        row_dict[col] = value
                data.append(row_dict)
            
            return {
                'data': data,
                'columns': list(result_df.columns),
                'row_count': len(result_df),
                'column_count': len(result_df.columns)
            }
            
        finally:
            conn.close()
    
    def _is_unsafe_query(self, query):
        """
        Basic security check for SQL queries.
        
        Args:
            query: SQL query string
            
        Returns:
            bool: True if query contains unsafe operations
        """
        query_upper = query.upper()
        unsafe_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
            'TRUNCATE', 'REPLACE', 'MERGE', 'EXEC', 'EXECUTE'
        ]
        
        return any(keyword in query_upper for keyword in unsafe_keywords)
    
    def _save_query_history(self, user, datasource, query, success, 
                          execution_time=None, rows_returned=None, error_message=None):
        """
        Save query execution to history.
        
        Args:
            user: User who executed the query
            datasource: DataSource that was queried
            query: SQL query string
            success: Whether query executed successfully
            execution_time: Execution time in seconds
            rows_returned: Number of rows returned
            error_message: Error message if query failed
        """
        QueryHistory.objects.create(
            user=user,
            datasource=datasource,
            sql_query=query,
            was_successful=success,
            execution_time_ms=int(execution_time * 1000) if execution_time else None,
            rows_returned=rows_returned
        )


class QueryHistoryAPIView(BaseAPIView, View):
    """
    API view for retrieving SQL query execution history.
    """
    
    def get(self, request):
        """
        Get paginated query history for the current user.
        
        Args:
            request: HTTP request with optional filtering parameters
            
        Returns:
            JsonResponse: Paginated list of query history entries
        """
        try:
            # Get filtering parameters
            datasource_id = request.GET.get('datasource_id')
            success_filter = request.GET.get('success')
            page = request.GET.get('page', 1)
            limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 per page
            
            # Build query
            queryset = QueryHistory.objects.filter(user=request.user)
            
            if datasource_id:
                queryset = queryset.filter(datasource_id=datasource_id)
            
            if success_filter is not None:
                success_bool = success_filter.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(was_successful=success_bool)
            
            # Order by most recent first
            queryset = queryset.order_by('-timestamp')
            
            # Paginate
            paginator = Paginator(queryset, limit)
            
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            
            # Serialize history entries
            history_data = []
            for entry in page_obj:
                history_data.append({
                    'id': str(entry.id),
                    'query': entry.sql_query,
                    'query_preview': entry.query_preview,
                    'datasource_name': entry.datasource.name if entry.datasource else 'N/A',
                    'datasource_id': str(entry.datasource.id) if entry.datasource else None,
                    'success': entry.was_successful,
                    'execution_time': entry.execution_time_ms / 1000 if entry.execution_time_ms else None,
                    'rows_returned': entry.rows_returned,
                    'created_at': entry.timestamp.isoformat(),
                    'updated_at': entry.timestamp.isoformat()  # Using timestamp for both
                })
            
            return self.success_response({
                'history': history_data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'items_per_page': limit
                }
            })
            
        except Exception as e:
            return self.error_response(f'Error obteniendo historial: {str(e)}')
