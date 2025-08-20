"""
Plotly Configuration for HydroML Project.

This module provides standardized Plotly configuration, themes, and utility functions
for consistent visualization across the HydroML application.
"""

import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional
import json


# Default template configuration
DEFAULT_TEMPLATE = "plotly_white"

# HydroML color palette
HYDROML_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'info': '#17becf',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Color scales for different chart types
HYDROML_COLOR_SCALES = {
    'sequential': px.colors.sequential.Blues,
    'diverging': px.colors.diverging.RdBu,
    'qualitative': px.colors.qualitative.Set3,
    'water_quality': ['#e6f3ff', '#99d6ff', '#4db8ff', '#0080ff', '#0066cc', '#004d99']
}


def configure_plotly():
    """
    Configure Plotly with HydroML defaults.
    This should be called once during Django initialization.
    """
    # Set default template
    pio.templates.default = DEFAULT_TEMPLATE
    
    # Configure for web rendering
    pio.renderers.default = "browser"
    
    # Create custom HydroML theme
    hydroml_template = go.layout.Template(
        layout=go.Layout(
            colorway=list(HYDROML_COLORS.values()),
            font=dict(family="Inter, system-ui, sans-serif", size=12),
            title=dict(font=dict(size=16, color=HYDROML_COLORS['dark'])),
            paper_bgcolor='white',
            plot_bgcolor='white',
            hovermode='closest',
            showlegend=True,
            margin=dict(l=60, r=30, t=60, b=60)
        )
    )
    
    # Register the custom template
    pio.templates["hydroml"] = hydroml_template
    pio.templates.default = "hydroml"


def get_standard_layout(title: str, **kwargs) -> Dict[str, Any]:
    """
    Get standardized layout configuration for HydroML charts.
    
    Args:
        title: Chart title
        **kwargs: Additional layout parameters
        
    Returns:
        Layout configuration dict
    """
    layout = {
        'title': {
            'text': title,
            'font': {'size': 16, 'color': HYDROML_COLORS['dark']},
            'x': 0.5,
            'xanchor': 'center'
        },
        'template': 'hydroml',
        'height': 400,
        'margin': dict(l=60, r=30, t=60, b=60),
        'hovermode': 'closest'
    }
    
    # Merge with custom parameters
    layout.update(kwargs)
    return layout


def create_time_series_chart(df, x_col: str, y_col: str, title: str, **kwargs):
    """
    Create a standardized time series chart for hydrogeological data.
    
    Args:
        df: DataFrame with time series data
        x_col: Column name for x-axis (time)
        y_col: Column name for y-axis (values)
        title: Chart title
        **kwargs: Additional parameters for px.line
        
    Returns:
        Plotly figure
    """
    fig = px.line(
        df, 
        x=x_col, 
        y=y_col,
        title=title,
        template='hydroml',
        **kwargs
    )
    
    fig.update_layout(get_standard_layout(title))
    fig.update_traces(line=dict(width=2))
    
    return fig


def create_scatter_plot(df, x_col: str, y_col: str, title: str, color_col: Optional[str] = None, **kwargs):
    """
    Create a standardized scatter plot for data analysis.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis  
        title: Chart title
        color_col: Optional column for color coding
        **kwargs: Additional parameters for px.scatter
        
    Returns:
        Plotly figure
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        template='hydroml',
        **kwargs
    )
    
    fig.update_layout(get_standard_layout(title))
    return fig


def create_heatmap(z_data, x_labels, y_labels, title: str, **kwargs):
    """
    Create a standardized heatmap for correlation or missing data analysis.
    
    Args:
        z_data: 2D array or list for heatmap values
        x_labels: Labels for x-axis
        y_labels: Labels for y-axis
        title: Chart title
        **kwargs: Additional parameters for go.Heatmap
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=x_labels,
        y=y_labels,
        colorscale='Blues',
        **kwargs
    ))
    
    fig.update_layout(get_standard_layout(title))
    return fig


def save_chart_as_json(fig, filename: str = None) -> str:
    """
    Save Plotly figure as JSON for frontend rendering.
    
    Args:
        fig: Plotly figure
        filename: Optional filename for saving to file
        
    Returns:
        JSON string representation of the figure
    """
    json_str = pio.to_json(fig)
    
    if filename:
        with open(filename, 'w') as f:
            f.write(json_str)
    
    return json_str


def get_color_scale(scale_type: str = 'sequential') -> list:
    """
    Get predefined color scale for HydroML visualizations.
    
    Args:
        scale_type: Type of color scale ('sequential', 'diverging', 'qualitative', 'water_quality')
        
    Returns:
        List of colors
    """
    return HYDROML_COLOR_SCALES.get(scale_type, HYDROML_COLOR_SCALES['sequential'])


# Initialize Plotly configuration when module is imported
configure_plotly()