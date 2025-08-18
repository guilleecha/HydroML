"""
Data quality and analysis tasks for data_tools.
"""
from celery import shared_task
from projects.models import DataSource
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from itertools import combinations
import logging
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


@shared_task
def deep_missing_data_analysis_task(datasource_id, target_column, required_variables):
    """
    Comprehensive missing data analysis task for the Missing Data Toolkit.
    
    Performs:
    1. Missing data heatmap generation using missingno.matrix()
    2. Feature importance estimation using RandomForestRegressor
    3. Complete case analysis for all relevant variable combinations
    4. Saves results to DataSource.missing_data_report
    
    Args:
        datasource_id (str): DataSource UUID
        target_column (str): Target variable for feature importance analysis
        required_variables (list): List of required variables for analysis
        
    Returns:
        dict: Task execution summary
    """
    try:
        # Fetch the DataSource object
        datasource = DataSource.objects.get(id=datasource_id)
        
        logger.info(f"Starting deep missing data analysis for DataSource {datasource_id}")
        logger.info(f"Target column: {target_column}")
        logger.info(f"Required variables: {required_variables}")
        
        # Load the dataframe
        df = _load_dataframe_from_datasource(datasource)
        
        if df is None or df.empty:
            raise ValueError("Failed to load data or file is empty")
        
        logger.info(f"Loaded dataframe with shape: {df.shape}")
        
        # Step 1: Generate Missing Data Heatmap
        logger.info("Step 1: Generating missing data heatmap")
        heatmap_html = _generate_missing_data_heatmap(df, datasource_id, required_variables)
        
        # Step 2: Feature Importance Estimation
        logger.info("Step 2: Running feature importance estimation")
        feature_importances = _calculate_feature_importance(df, target_column, required_variables)
        
        # Step 3: Complete Case Analysis (Combinations)
        logger.info("Step 3: Running complete case analysis")
        combination_counts = _calculate_complete_case_combinations(df, required_variables)
        
        # Step 4: Additional missing data statistics
        logger.info("Step 4: Calculating additional missing data statistics")
        missing_stats = _calculate_missing_data_statistics(df, required_variables)
        
        # Step 5: Save the comprehensive report
        missing_data_report = {
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'target_column': target_column,
            'required_variables': required_variables,
            'heatmap_html': heatmap_html,
            'feature_importance': feature_importances,
            'combination_analysis': combination_counts,
            'missing_statistics': missing_stats,
            'analysis_metadata': {
                'original_shape': df.shape,
                'total_complete_rows': int(df.dropna().shape[0]),
                'total_rows_with_target': int(df[target_column].dropna().shape[0]) if target_column in df.columns else 0,
                'analysis_successful': True,
                'heatmap_generated': bool(heatmap_html)
            }
        }
        
        # Save to database
        datasource.missing_data_report = missing_data_report
        datasource.save()
        
        logger.info(f"Successfully completed deep missing data analysis for DataSource {datasource_id}")
        
        return {
            'status': 'success',
            'message': f"Deep missing data analysis completed for DataSource {datasource_id}",
            'feature_importance_variables': len(feature_importances),
            'combination_analysis_count': len(combination_counts),
            'total_complete_rows': missing_data_report['analysis_metadata']['total_complete_rows'],
            'heatmap_generated': bool(heatmap_html)
        }
        
    except Exception as e:
        logger.error(f"Deep missing data analysis failed for datasource {datasource_id}: {e}", exc_info=True)
        
        # Save error report
        try:
            datasource = DataSource.objects.get(id=datasource_id)
            datasource.missing_data_report = {
                'analysis_timestamp': pd.Timestamp.now().isoformat(),
                'error': str(e),
                'analysis_successful': False,
                'target_column': target_column,
                'required_variables': required_variables,
                'heatmap_generated': False
            }
            datasource.save()
        except Exception:
            logger.exception("Failed to update DataSource with error report")
        
        return {
            'status': 'error',
            'message': f"Deep missing data analysis failed: {str(e)}",
            'datasource_id': str(datasource_id)
        }


def _load_dataframe_from_datasource(datasource):
    """Load dataframe from DataSource file."""
    try:
        file_path = datasource.file.path
        
        if file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            # Try different encodings and separators
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            # Final fallback
            return pd.read_csv(file_path, encoding='latin-1')
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            # Try parquet as fallback
            return pd.read_parquet(file_path)
            
    except Exception as e:
        logger.error(f"Failed to load dataframe from datasource: {e}")
        return None


def _calculate_feature_importance(df, target_column, required_variables):
    """Calculate feature importance using RandomForestRegressor after imputation."""
    try:
        # Check if target column exists
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataframe")
        
        # Select features (required variables + target)
        all_variables = required_variables + [target_column]
        available_variables = [var for var in all_variables if var in df.columns]
        
        if len(available_variables) < 2:
            raise ValueError(f"Insufficient variables for analysis. Available: {available_variables}")
        
        # Create feature matrix and target vector
        feature_vars = [var for var in available_variables if var != target_column]
        X = df[feature_vars].copy()
        y = df[target_column].copy()
        
        # Keep only rows where target is not null
        mask = y.notna()
        X = X[mask]
        y = y[mask]
        
        if len(y) == 0:
            raise ValueError(f"No non-null values found in target column '{target_column}'")
        
        # Prepare features for ML
        X_processed = X.copy()
        
        # Handle categorical variables with label encoding
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns
        for col in categorical_columns:
            le = LabelEncoder()
            X_processed[col] = le.fit_transform(X_processed[col].astype(str))
        
        # Impute missing values in features
        imputer = SimpleImputer(strategy='median')
        X_imputed = pd.DataFrame(
            imputer.fit_transform(X_processed),
            columns=X_processed.columns,
            index=X_processed.index
        )
        
        # Handle target variable (ensure it's numeric)
        if y.dtype == 'object':
            le_target = LabelEncoder()
            y = pd.Series(le_target.fit_transform(y.astype(str)), index=y.index)
        
        # Train RandomForestRegressor
        rf = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            n_jobs=-1
        )
        
        rf.fit(X_imputed, y)
        
        # Extract feature importances
        feature_importances = {}
        for feature, importance in zip(feature_vars, rf.feature_importances_):
            feature_importances[feature] = float(importance)
        
        logger.info(f"Feature importance calculated for {len(feature_importances)} features")
        return feature_importances
        
    except Exception as e:
        logger.error(f"Feature importance calculation failed: {e}")
        return {}


def _calculate_complete_case_combinations(df, required_variables):
    """Calculate complete rows for all combinations of required variables."""
    try:
        # Filter to only include variables that exist in the dataframe
        available_variables = [var for var in required_variables if var in df.columns]
        
        if len(available_variables) == 0:
            return {}
        
        combination_counts = {}
        
        # Single variables
        for var in available_variables:
            complete_count = int(df[var].notna().sum())
            combination_counts[var] = {
                'variables': [var],
                'complete_rows': complete_count,
                'completion_rate': float(complete_count / len(df)) if len(df) > 0 else 0.0
            }
        
        # Combinations of 2 or more variables (up to 5 for performance)
        max_combination_size = min(5, len(available_variables))
        
        for r in range(2, max_combination_size + 1):
            for combination in combinations(available_variables, r):
                combination_key = " + ".join(sorted(combination))
                
                # Count rows where all variables in combination are not null
                mask = pd.Series(True, index=df.index)
                for var in combination:
                    mask &= df[var].notna()
                
                complete_count = int(mask.sum())
                combination_counts[combination_key] = {
                    'variables': list(combination),
                    'complete_rows': complete_count,
                    'completion_rate': float(complete_count / len(df)) if len(df) > 0 else 0.0
                }
        
        logger.info(f"Calculated complete case combinations for {len(combination_counts)} scenarios")
        return combination_counts
        
    except Exception as e:
        logger.error(f"Complete case combination calculation failed: {e}")
        return {}


def _calculate_missing_data_statistics(df, required_variables):
    """Calculate comprehensive missing data statistics."""
    try:
        available_variables = [var for var in required_variables if var in df.columns]
        
        missing_stats = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'required_variables_count': len(available_variables),
            'column_missing_percentages': {},
            'missing_patterns': {},
            'completely_missing_variables': []
        }
        
        # Calculate missing percentages for each variable
        for var in available_variables:
            missing_count = int(df[var].isna().sum())
            missing_percentage = float(missing_count / len(df) * 100) if len(df) > 0 else 0.0
            
            missing_stats['column_missing_percentages'][var] = {
                'missing_count': missing_count,
                'missing_percentage': missing_percentage,
                'complete_count': int(len(df) - missing_count)
            }
            
            # Track completely missing variables
            if missing_count == len(df):
                missing_stats['completely_missing_variables'].append(var)
        
        # Calculate missing patterns (simplified)
        missing_pattern_df = df[available_variables].isna()
        pattern_counts = missing_pattern_df.value_counts().head(10)  # Top 10 patterns
        
        for pattern, count in pattern_counts.items():
            pattern_key = "Missing: " + ", ".join([var for var, is_missing in zip(available_variables, pattern) if is_missing])
            if not pattern_key.endswith(": "):
                missing_stats['missing_patterns'][pattern_key or "Complete"] = int(count)
        
        logger.info(f"Calculated missing data statistics for {len(available_variables)} variables")
        return missing_stats
        
    except Exception as e:
        logger.error(f"Missing data statistics calculation failed: {e}")
        return {}


def _generate_missing_data_heatmap(df, datasource_id, required_variables):
    """
    Generate an interactive missing data heatmap using Plotly.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        datasource_id (str): DataSource identifier for file naming
        required_variables (list): List of required variables to focus on
        
    Returns:
        str or None: HTML string of interactive Plotly heatmap, or None if failed
    """
    try:
        # Filter dataframe to focus on required variables that exist
        available_variables = [var for var in required_variables if var in df.columns]
        
        if not available_variables:
            logger.warning("No available variables for heatmap generation")
            return None
        
        # Create focused dataframe for heatmap (limit to reasonable size for performance)
        heatmap_df = df[available_variables].copy()
        
        # If dataset is very large, sample for visualization
        if len(heatmap_df) > 1000:
            heatmap_df = heatmap_df.sample(n=1000, random_state=42)
            logger.info(f"Sampled 1000 rows from {len(df)} for heatmap visualization")
        
        # Create nullity matrix (1 for missing, 0 for present)
        nullity_matrix = heatmap_df.isnull().astype(int)
        
        # Create interactive heatmap with Plotly
        fig = px.imshow(
            nullity_matrix.values,
            x=nullity_matrix.columns,
            y=list(range(len(nullity_matrix))),
            color_continuous_scale=[
                [0, '#61AFEF'],    # Present data - One Dark blue
                [1, '#E06C75']     # Missing data - One Dark red
            ],
            aspect="auto",
            title=f"Missing Data Pattern Matrix - {len(available_variables)} Variables",
            labels=dict(
                x="Variables", 
                y="Records", 
                color="Status"
            )
        )
        
        # Apply One Dark theme styling
        fig.update_layout(
            # Dark background matching One Dark theme
            plot_bgcolor='#282C34',
            paper_bgcolor='#282C34',
            
            # Title styling
            title=dict(
                font=dict(color='#ABB2BF', size=16, family='monospace'),
                x=0.5,
                xanchor='center',
                pad=dict(t=20)
            ),
            
            # X-axis styling
            xaxis=dict(
                title=dict(
                    text="Variables",
                    font=dict(color='#ABB2BF', size=12)
                ),
                tickfont=dict(color='#ABB2BF', size=10),
                tickangle=-45,
                gridcolor='#3E4451',
                showgrid=True,
                zeroline=False,
                side='bottom'
            ),
            
            # Y-axis styling
            yaxis=dict(
                title=dict(
                    text="Records",
                    font=dict(color='#ABB2BF', size=12)
                ),
                tickfont=dict(color='#ABB2BF', size=10),
                gridcolor='#3E4451',
                showgrid=True,
                zeroline=False,
                autorange='reversed'  # Show first rows at top
            ),
            
            # Colorbar styling
            coloraxis_colorbar=dict(
                title=dict(
                    text="Data Status", 
                    font=dict(color='#ABB2BF', size=12)
                ),
                tickfont=dict(color='#ABB2BF', size=10),
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Present', 'Missing'],
                thickness=20,
                len=0.7
            ),
            
            # Layout dimensions
            width=900,
            height=max(400, min(800, len(nullity_matrix) * 2 + 200)),
            margin=dict(t=80, r=80, b=100, l=80),
            
            # Hover styling
            hoverlabel=dict(
                bgcolor='#3E4451',
                bordercolor='#ABB2BF',
                font=dict(color='#ABB2BF', family='monospace')
            )
        )
        
        # Enhanced hover template for better interactivity
        fig.update_traces(
            hovertemplate="<b>Variable:</b> %{x}<br>" +
                         "<b>Record:</b> %{y}<br>" +
                         "<b>Status:</b> %{customdata}<br>" +
                         "<extra></extra>",
            customdata=[["Missing" if val else "Present" for val in row] 
                       for row in nullity_matrix.values]
        )
        
        # Convert to HTML string for embedding in Django template
        html_string = fig.to_html(
            include_plotlyjs='cdn',
            div_id=f"missing-data-heatmap-{datasource_id}",
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'missing_data_heatmap_{datasource_id}',
                    'height': max(400, min(800, len(nullity_matrix) * 2 + 200)),
                    'width': 900,
                    'scale': 2
                }
            }
        )
        
        logger.info(f"Generated interactive missing data heatmap with {len(available_variables)} variables")
        return html_string
        
    except Exception as e:
        logger.error(f"Heatmap generation failed: {e}", exc_info=True)
        return None
