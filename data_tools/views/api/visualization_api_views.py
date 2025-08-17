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
    
    def post(self, request):
        """
        Generate a chart based on the provided configuration.
        
        Args:
            request: HTTP request with chart configuration
            
        Returns:
            JsonResponse: Chart data in Plotly format
        """
        try:
            # Extract parameters
            datasource_id = request.POST.get('datasource_id')
            chart_type = request.POST.get('chart_type', '').lower()
            
            if not datasource_id:
                return self.error_response('ID del DataSource es requerido')
            
            if chart_type not in self.SUPPORTED_CHART_TYPES:
                return self.error_response(
                    f'Tipo de gráfico no soportado: {chart_type}. '
                    f'Tipos disponibles: {", ".join(self.SUPPORTED_CHART_TYPES.keys())}'
                )
            
            # Get and validate DataSource
            datasource = self.get_datasource(datasource_id)
            
            validation_error = self.validate_datasource_status(datasource)
            if validation_error:
                return self.error_response(validation_error['error'])
            
            # Load data
            df = self._load_dataframe(datasource)
            
            # Validate chart parameters
            chart_config = self._validate_chart_parameters(request.POST, chart_type)
            
            # Generate chart
            chart_data = self._generate_chart(df, chart_type, chart_config)
            
            return self.success_response({
                'chart': chart_data,
                'chart_type': chart_type,
                'datasource_name': datasource.name,
                'data_points': len(df)
            })
            
        except Exception as e:
            return self.error_response(f'Error generando gráfico: {str(e)}')
    
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
    
    def _apply_common_styling(self, fig, config):
        """
        Apply common styling to all chart types.
        
        Args:
            fig: Plotly figure object
            config: Chart configuration
        """
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Update axes
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='black'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='black'
        )
