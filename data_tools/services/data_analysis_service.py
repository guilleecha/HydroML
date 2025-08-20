"""
Data Analysis Service for Data Studio.
Handles nullity analysis and visualization generation.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json
import logging
import sentry_sdk

logger = logging.getLogger(__name__)


def calculate_nullity_report(df, include_visualizations=False):
    """
    Calculate comprehensive nullity report for the Missing Data Toolkit.
    
    Args:
        df (pd.DataFrame): Input dataframe
        include_visualizations (bool): Whether to generate expensive visualizations
        
    Returns:
        dict: Nullity report with statistics and optional visualizations
    """
    try:
        # Calculate basic nullity statistics (fast)
        total_values = df.size
        missing_values = df.isnull().sum().sum()
        missing_percentage = (missing_values / total_values) * 100
        
        # Column-level nullity statistics (fast)
        column_nullity = []
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            column_nullity.append({
                'column': col,
                'null_count': null_count,
                'null_percentage': round(null_percentage, 2),
                'dtype': str(df[col].dtype)
            })
        
        # Sort by null percentage descending
        column_nullity = sorted(column_nullity, key=lambda x: x['null_percentage'], reverse=True)
        
        result = {
            'total_values': total_values,
            'missing_values': missing_values,
            'missing_percentage': round(missing_percentage, 2),
            'complete_percentage': round(100 - missing_percentage, 2),
            'column_nullity': column_nullity,
        }
        
        # Only generate expensive visualizations when explicitly requested
        if include_visualizations:
            result['visualizations'] = generate_nullity_visualizations(df)
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating nullity report: {e}")
        sentry_sdk.capture_exception(e)
        return {
            'error': f'Failed to calculate nullity report: {str(e)}'
        }


def generate_nullity_visualizations(df):
    """
    Generate interactive Plotly visualizations for nullity patterns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        dict: Interactive Plotly visualizations as JSON
    """
    try:
        visualizations = {}
        
        # 1. Missing Data Bar Chart
        null_counts = df.isnull().sum()
        null_percentages = (null_counts / len(df)) * 100
        
        # Filter columns with missing data
        missing_cols = null_counts[null_counts > 0]
        
        if len(missing_cols) > 0:
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=missing_cols.index,
                    y=missing_cols.values,
                    text=[f'{pct:.1f}%' for pct in null_percentages[missing_cols.index]],
                    textposition='auto',
                    marker=dict(color='rgb(158,202,225)', line=dict(color='rgb(8,48,107)', width=1.5))
                )
            ])
            
            fig_bar.update_layout(
                title='Missing Data Count by Column',
                xaxis_title='Columns',
                yaxis_title='Missing Count',
                xaxis_tickangle=-45,
                height=400,
                template='plotly_white'
            )
            
            visualizations['bar'] = json.loads(pio.to_json(fig_bar))
        
        # 2. Missing Data Matrix (Heatmap)
        if len(df.columns) <= 30:  # Only for manageable number of columns
            # Create binary matrix for missing data
            missing_matrix = df.isnull().astype(int)
            
            fig_matrix = go.Figure(data=go.Heatmap(
                z=missing_matrix.values.T,
                x=missing_matrix.index,
                y=missing_matrix.columns,
                colorscale=[[0, 'lightblue'], [1, 'darkred']],
                showscale=True,
                colorbar=dict(title="Missing", tickvals=[0, 1], ticktext=["Present", "Missing"])
            ))
            
            fig_matrix.update_layout(
                title='Missing Data Matrix',
                xaxis_title='Row Index',
                yaxis_title='Columns',
                height=max(400, len(df.columns) * 20),
                template='plotly_white'
            )
            
            visualizations['matrix'] = json.loads(pio.to_json(fig_matrix))
        
        # 3. Missing Data Percentage Pie Chart
        if len(missing_cols) > 0:
            complete_pct = 100 - null_percentages.sum() / len(df.columns)
            missing_pct = null_percentages.sum() / len(df.columns)
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Complete Data', 'Missing Data'],
                values=[complete_pct, missing_pct],
                hole=0.3,
                marker_colors=['lightgreen', 'lightcoral']
            )])
            
            fig_pie.update_layout(
                title='Overall Data Completeness',
                height=400,
                template='plotly_white'
            )
            
            visualizations['pie'] = json.loads(pio.to_json(fig_pie))
        
        # 4. Column-wise Missing Data Distribution
        col_missing_data = []
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                col_missing_data.append({
                    'column': col,
                    'missing_count': missing_count,
                    'missing_percentage': (missing_count / len(df)) * 100
                })
        
        if col_missing_data:
            col_df = pd.DataFrame(col_missing_data)
            
            fig_scatter = px.scatter(
                col_df, 
                x='missing_count', 
                y='missing_percentage',
                hover_data=['column'],
                title='Missing Data Distribution',
                labels={'missing_count': 'Missing Count', 'missing_percentage': 'Missing Percentage (%)'}
            )
            
            fig_scatter.update_layout(height=400, template='plotly_white')
            visualizations['scatter'] = json.loads(pio.to_json(fig_scatter))
        
        return visualizations
        
    except Exception as e:
        logger.error(f"Error generating nullity visualizations: {e}")
        sentry_sdk.capture_exception(e)
        return {'error': f'Failed to generate visualizations: {str(e)}'}