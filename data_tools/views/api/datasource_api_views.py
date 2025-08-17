"""
DataSource-related API views.
Handles operations related to DataSource columns and metadata.
"""
import pandas as pd
from django.views import View

from .mixins import BaseAPIView


class DataSourceColumnsAPIView(BaseAPIView, View):
    """
    API view for retrieving DataSource column information.
    Supports multiple file formats: CSV, Parquet, Excel.
    """
    
    def get(self, request, datasource_id):
        """
        Get columns and basic metadata for a DataSource.
        
        Args:
            request: HTTP request object
            datasource_id: UUID of the DataSource
            
        Returns:
            JsonResponse: List of columns with types and sample data
        """
        # Get and validate DataSource
        datasource = self.get_datasource(datasource_id)
        
        validation_error = self.validate_datasource_status(datasource)
        if validation_error:
            return self.error_response(validation_error['error'])
        
        try:
            # Read file based on format
            df = self._read_dataframe(datasource.file.path)
            
            # Generate column information
            columns_info = self._generate_columns_info(df)
            
            return self.success_response({
                'columns': columns_info,
                'total_rows': len(df),
                'total_columns': len(df.columns)
            })
            
        except Exception as e:
            return self.error_response(f'Error procesando archivo: {str(e)}')
    
    def _read_dataframe(self, file_path):
        """
        Read DataFrame from file with format detection and error handling.
        
        Args:
            file_path: Path to the file
            
        Returns:
            pandas.DataFrame: Loaded DataFrame
            
        Raises:
            Exception: If file cannot be read with any supported format
        """
        if file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        
        elif file_path.endswith('.csv'):
            # Try different CSV configurations
            for delimiter in [',', ';', '\t']:
                for encoding in ['latin-1', 'utf-8', 'cp1252']:
                    try:
                        return pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
                    except (pd.errors.ParserError, UnicodeDecodeError):
                        continue
            
            raise Exception("No se pudo leer el archivo CSV con ningún formato soportado")
        
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        
        else:
            raise Exception(f"Formato de archivo no soportado: {file_path}")
    
    def _generate_columns_info(self, df):
        """
        Generate detailed column information from DataFrame.
        
        Args:
            df: pandas.DataFrame to analyze
            
        Returns:
            list: List of column dictionaries with metadata
        """
        columns_info = []
        
        for column in df.columns:
            col_series = df[column]
            
            # Basic column info
            column_info = {
                'name': column,
                'dtype': str(col_series.dtype),
                'non_null_count': int(col_series.count()),
                'null_count': int(col_series.isnull().sum()),
                'null_percentage': round((col_series.isnull().sum() / len(df)) * 100, 2)
            }
            
            # Add sample values (non-null)
            non_null_values = col_series.dropna()
            if len(non_null_values) > 0:
                sample_size = min(5, len(non_null_values))
                column_info['sample_values'] = non_null_values.head(sample_size).tolist()
            
            # Add statistics for numeric columns
            if pd.api.types.is_numeric_dtype(col_series):
                column_info.update({
                    'min': float(col_series.min()) if not col_series.empty else None,
                    'max': float(col_series.max()) if not col_series.empty else None,
                    'mean': float(col_series.mean()) if not col_series.empty else None,
                    'std': float(col_series.std()) if not col_series.empty else None
                })
            
            columns_info.append(column_info)
        
        return columns_info


class FusionColumnsAPIView(BaseAPIView, View):
    """
    API view for handling data fusion column operations.
    """
    
    def post(self, request):
        """
        Get columns for data fusion from selected DataSources.
        
        Args:
            request: HTTP request with datasource_ids in POST data
            
        Returns:
            JsonResponse: Combined column information from all DataSources
        """
        try:
            # Get DataSource IDs from POST data
            datasource_ids = request.POST.getlist('datasource_ids')
            
            if not datasource_ids:
                return self.error_response('No se proporcionaron IDs de DataSource')
            
            fusion_columns = []
            datasource_info = []
            
            for ds_id in datasource_ids:
                try:
                    # Get and validate DataSource
                    datasource = self.get_datasource(ds_id)
                    
                    validation_error = self.validate_datasource_status(datasource)
                    if validation_error:
                        continue  # Skip invalid DataSources but don't fail entirely
                    
                    # Read DataFrame and get columns
                    df = DataSourceColumnsAPIView()._read_dataframe(datasource.file.path)
                    
                    # Add DataSource info
                    datasource_info.append({
                        'id': str(datasource.id),
                        'name': datasource.name,
                        'columns': list(df.columns),
                        'total_rows': len(df)
                    })
                    
                    # Add columns to fusion list with source info
                    for column in df.columns:
                        fusion_columns.append({
                            'datasource_id': str(datasource.id),
                            'datasource_name': datasource.name,
                            'column': column,
                            'dtype': str(df[column].dtype)
                        })
                
                except Exception as e:
                    # Log error but continue with other DataSources
                    print(f"Error processing DataSource {ds_id}: {str(e)}")
                    continue
            
            return self.success_response({
                'fusion_columns': fusion_columns,
                'datasources': datasource_info,
                'total_datasources': len(datasource_info)
            })
            
        except Exception as e:
            return self.error_response(f'Error en la fusión: {str(e)}')


# Legacy function wrapper for backward compatibility
def get_datasource_columns(request, datasource_id):
    """
    Legacy function wrapper for DataSourceColumnsAPIView.
    Maintains backward compatibility with existing URL patterns.
    """
    view = DataSourceColumnsAPIView.as_view()
    return view(request, datasource_id=datasource_id)
