"""
Visualization and chart generation API views.
Handles creation of charts and data visualizations using Plotly.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.views import View

from .mixins import BaseAPIView


class ChartGenerationAPIView(BaseAPIView, View):
    """
    API view for generating charts and visualizations from DataSource data.
    Supports multiple chart types using Plotly.
    """
    
    # Supported chart types and their configurations
    SUPPORTED_CHART_TYPES = {
        'scatter': {
            'required_params': ['x_axis', 'y_axis'],
            'optional_params': ['color_by', 'size_by', 'title']
        },
        'line': {
            'required_params': ['x_axis', 'y_axis'],
            'optional_params': ['color_by', 'title']
        },
        'bar': {
            'required_params': ['x_axis', 'y_axis'],
            'optional_params': ['color_by', 'title']
        },
        'histogram': {
            'required_params': ['column'],
            'optional_params': ['bins', 'color_by', 'title']
        },
        'box': {
            'required_params': ['y_axis'],
            'optional_params': ['x_axis', 'color_by', 'title']
        },
        'heatmap': {
            'required_params': ['x_axis', 'y_axis', 'values'],
            'optional_params': ['title']
        }
    }
    
    def get(self, request):
        """
        Generate a chart based on the provided configuration (GET method for backward compatibility).
        
        Args:
            request: HTTP request with chart configuration
            
        Returns:
            JsonResponse: Chart HTML or error message
        """
        return self._handle_chart_request(request, request.GET)
        
    def post(self, request):
        """
        Generate a chart based on the provided configuration (POST method).
        
        Args:
            request: HTTP request with chart configuration
            
        Returns:
            JsonResponse: Chart data in Plotly format
        """
        return self._handle_chart_request(request, request.POST)
        
    def _handle_chart_request(self, request, params):
        """
        Handle chart generation request with parameters from GET or POST.
        
        Args:
            request: HTTP request object
            params: GET or POST parameters
            
        Returns:
            JsonResponse: Chart response
        """
        try:
            # Extract parameters
            datasource_id = params.get('datasource_id')
            chart_type = params.get('chart_type', 'histogram').lower()
            column_name = params.get('column_name')
            x_column = params.get('x_column')
            y_column = params.get('y_column')
            
            # Parameter validation based on chart type
            if chart_type == 'scatter':
                if not datasource_id or not x_column or not y_column:
                    return JsonResponse({
                        'error': 'Para gráficos de dispersión se requieren: datasource_id, x_column y y_column'
                    }, status=400)
            else:
                if not datasource_id or not column_name:
                    return JsonResponse({
                        'error': 'Se requieren los parámetros: datasource_id y column_name'
                    }, status=400)
            
            # Validate UUID format
            from uuid import UUID
            try:
                UUID(datasource_id)
            except ValueError:
                return JsonResponse({
                    'error': 'datasource_id debe ser un UUID válido'
                }, status=400)
            
            # Get and validate DataSource with user permission check
            try:
                from projects.models.datasource import DataSource
                datasource = DataSource.objects.get(id=datasource_id, project__owner=request.user)
            except DataSource.DoesNotExist:
                return JsonResponse({
                    'error': f'DataSource con ID {datasource_id} no existe o no tienes acceso'
                }, status=404)
            
            # Verify DataSource is ready
            if datasource.status != DataSource.Status.READY:
                return JsonResponse({
                    'error': f'DataSource "{datasource.name}" no está listo (estado: {datasource.status})'
                }, status=400)
            
            # Load data with multiple format support
            df = self._read_dataframe_multi_format(datasource.file.path)
            
            # Generate chart based on type (simplified approach for backward compatibility)
            chart_html = self._generate_simple_chart(df, chart_type, column_name, x_column, y_column)
            
            # Prepare response data
            response_data = {
                'success': True,
                'chart_html': chart_html,
                'chart_type': chart_type,
            }
            
            # Add appropriate metadata based on chart type
            if chart_type == 'scatter':
                response_data.update({
                    'x_column': x_column,
                    'y_column': y_column,
                    'data_points': len(df)
                })
            else:
                response_data.update({
                    'column_name': column_name,
                    'data_points': len(df)
                })
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'error': f'Error inesperado: {str(e)}'
            }, status=500)
    
    def _load_dataframe(self, datasource):
        """
        Load DataFrame from DataSource file.
        
        Args:
            datasource: DataSource object
            
        Returns:
            pandas.DataFrame: Loaded data
        """
        from .datasource_api_views import DataSourceColumnsAPIView
        return DataSourceColumnsAPIView()._read_dataframe(datasource.file.path)
    
    def _validate_chart_parameters(self, post_data, chart_type):
        """
        Validate chart parameters based on chart type requirements.
        
        Args:
            post_data: POST data from request
            chart_type: Type of chart to generate
            
        Returns:
            dict: Validated chart configuration
            
        Raises:
            ValueError: If required parameters are missing
        """
        chart_spec = self.SUPPORTED_CHART_TYPES[chart_type]
        config = {}
        
        # Validate required parameters
        for param in chart_spec['required_params']:
            value = post_data.get(param)
            if not value:
                raise ValueError(f'Parámetro requerido faltante: {param}')
            config[param] = value
        
        # Add optional parameters
        for param in chart_spec['optional_params']:
            value = post_data.get(param)
            if value:
                config[param] = value
        
        return config
    
    def _generate_chart(self, df, chart_type, config):
        """
        Generate chart using Plotly based on type and configuration.
        
        Args:
            df: pandas.DataFrame with data
            chart_type: Type of chart to generate
            config: Chart configuration parameters
            
        Returns:
            dict: Plotly chart data
        """
        # Validate columns exist in DataFrame
        self._validate_columns_exist(df, config)
        
        # Generate chart based on type
        if chart_type == 'scatter':
            fig = self._create_scatter_plot(df, config)
        elif chart_type == 'line':
            fig = self._create_line_plot(df, config)
        elif chart_type == 'bar':
            fig = self._create_bar_plot(df, config)
        elif chart_type == 'histogram':
            fig = self._create_histogram(df, config)
        elif chart_type == 'box':
            fig = self._create_box_plot(df, config)
        elif chart_type == 'heatmap':
            fig = self._create_heatmap(df, config)
        else:
            raise ValueError(f'Tipo de gráfico no implementado: {chart_type}')
        
        # Apply common styling
        self._apply_common_styling(fig, config)
        
        # Convert to JSON
        return fig.to_dict()
    
    def _validate_columns_exist(self, df, config):
        """
        Validate that all specified columns exist in the DataFrame.
        
        Args:
            df: pandas.DataFrame to validate against
            config: Chart configuration with column names
            
        Raises:
            ValueError: If any column doesn't exist
        """
        available_columns = set(df.columns)
        
        for key, value in config.items():
            if key.endswith(('_axis', '_by')) or key in ['column', 'values']:
                if value not in available_columns:
                    raise ValueError(
                        f'Columna "{value}" no existe en el dataset. '
                        f'Columnas disponibles: {", ".join(available_columns)}'
                    )
    
    def _create_scatter_plot(self, df, config):
        """Create scatter plot."""
        return px.scatter(
            df,
            x=config['x_axis'],
            y=config['y_axis'],
            color=config.get('color_by'),
            size=config.get('size_by'),
            title=config.get('title', 'Scatter Plot')
        )
    
    def _create_line_plot(self, df, config):
        """Create line plot."""
        return px.line(
            df,
            x=config['x_axis'],
            y=config['y_axis'],
            color=config.get('color_by'),
            title=config.get('title', 'Line Plot')
        )
    
    def _create_bar_plot(self, df, config):
        """Create bar plot."""
        return px.bar(
            df,
            x=config['x_axis'],
            y=config['y_axis'],
            color=config.get('color_by'),
            title=config.get('title', 'Bar Plot')
        )
    
    def _create_histogram(self, df, config):
        """Create histogram."""
        return px.histogram(
            df,
            x=config['column'],
            nbins=int(config.get('bins', 30)),
            color=config.get('color_by'),
            title=config.get('title', 'Histogram')
        )
    
    def _create_box_plot(self, df, config):
        """Create box plot."""
        return px.box(
            df,
            x=config.get('x_axis'),
            y=config['y_axis'],
            color=config.get('color_by'),
            title=config.get('title', 'Box Plot')
        )
    
    def _create_heatmap(self, df, config):
        """Create heatmap."""
        # For heatmap, we need to pivot the data
        pivot_df = df.pivot_table(
            values=config['values'],
            index=config['y_axis'],
            columns=config['x_axis'],
            aggfunc='mean'
        )
        
        return px.imshow(
            pivot_df,
            title=config.get('title', 'Heatmap'),
            aspect='auto'
        )
    
    def _read_dataframe_multi_format(self, file_path):
        """
        Read DataFrame with multiple format support (backward compatibility).
        
        Args:
            file_path: Path to the file
            
        Returns:
            pandas.DataFrame: Loaded DataFrame
        """
        import pandas as pd
        
        if file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            # Try different CSV configurations like original
            try:
                return pd.read_csv(file_path, delimiter=',', encoding='latin-1')
            except pd.errors.ParserError:
                try:
                    return pd.read_csv(file_path, delimiter=';', encoding='latin-1')
                except pd.errors.ParserError:
                    try:
                        return pd.read_csv(file_path, delimiter='\t', encoding='latin-1')
                    except pd.errors.ParserError as e:
                        raise Exception(f'Error al analizar el archivo CSV: {str(e)}')
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            try:
                return pd.read_parquet(file_path)
            except Exception as e:
                raise Exception(f'Error reading file: {str(e)}')
    
    def _generate_simple_chart(self, df, chart_type, column_name, x_column, y_column):
        """
        Generate simple chart HTML (backward compatibility).
        
        Args:
            df: pandas.DataFrame with data
            chart_type: Type of chart
            column_name: Column for single-column charts
            x_column: X-axis column for scatter plots
            y_column: Y-axis column for scatter plots
            
        Returns:
            str: Chart HTML
        """
        import plotly.express as px
        
        # Handle column validation based on chart type
        if chart_type == 'scatter':
            # Validate both X and Y columns for scatter plots
            if x_column not in df.columns:
                raise Exception(f'La columna X "{x_column}" no existe en el dataset')
            
            if y_column not in df.columns:
                raise Exception(f'La columna Y "{y_column}" no existe en el dataset')
            
            # Check if both columns are numeric
            if not pd.api.types.is_numeric_dtype(df[x_column]):
                raise Exception(f'La columna X "{x_column}" no es numérica')
            
            if not pd.api.types.is_numeric_dtype(df[y_column]):
                raise Exception(f'La columna Y "{y_column}" no es numérica')
            
            # Remove rows with null values in either column
            plot_data = df[[x_column, y_column]].dropna()
            
            if len(plot_data) == 0:
                raise Exception(f'No hay datos válidos para las columnas "{x_column}" y "{y_column}"')
            
            fig = px.scatter(
                x=plot_data[x_column],
                y=plot_data[y_column],
                title=f'Diagrama de Dispersión: {x_column} vs {y_column}',
                labels={'x': x_column, 'y': y_column}
            )
            fig.update_layout(
                xaxis_title=x_column,
                yaxis_title=y_column,
                template='plotly_white',
                height=400
            )
                
        else:
            # Single column validation for histogram and boxplot
            if column_name not in df.columns:
                raise Exception(f'La columna "{column_name}" no existe en el dataset')
            
            # Check if column is numeric
            if not pd.api.types.is_numeric_dtype(df[column_name]):
                raise Exception(f'La columna "{column_name}" no es numérica')
            
            # Remove null values for plotting
            column_data = df[column_name].dropna()
            
            if len(column_data) == 0:
                raise Exception(f'La columna "{column_name}" no tiene datos válidos')

            # Generate chart based on type
            if chart_type == 'histogram':
                fig = px.histogram(
                    x=column_data,
                    nbins=30,
                    title=f'Distribución de {column_name}',
                    labels={'x': column_name, 'y': 'Frecuencia'}
                )
                fig.update_layout(
                    xaxis_title=column_name,
                    yaxis_title='Frecuencia',
                    template='plotly_white',
                    height=400
                )
            elif chart_type == 'boxplot':
                fig = px.box(
                    y=column_data,
                    title=f'Diagrama de Caja de {column_name}',
                    labels={'y': column_name}
                )
                fig.update_layout(
                    yaxis_title=column_name,
                    template='plotly_white',
                    height=400
                )
            else:
                raise Exception(f'Tipo de gráfico no soportado: {chart_type}')
        
        # Convert to HTML
        return fig.to_html(
            include_plotlyjs=False,  # Don't include plotly.js since it's already loaded
            div_id="plotly-chart",
            config={'responsive': True, 'displayModeBar': True}
        )
