"""
Data Studio Transformation API Views for stateful data transformations.
These endpoints apply transformations to cached DataFrames in the session.
"""

import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from projects.models import DataSource
from data_tools.services.session_manager import get_session_manager

# Feature-engine imports (compatible with version 1.6.2)
from feature_engine.imputation import MeanMedianImputer, CategoricalImputer, ArbitraryNumberImputer
from feature_engine.encoding import OrdinalEncoder, OneHotEncoder, RareLabelEncoder
from feature_engine.wrappers import SklearnTransformerWrapper
from feature_engine.outliers import OutlierTrimmer, Winsorizer
from feature_engine.creation import MathFeatures, RelativeFeatures

# Scikit-learn imports (compatible with version 1.7.1)
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def apply_missing_data_imputation(request, datasource_id):
    """
    Apply missing data imputation to the current session DataFrame.
    """
    try:
        # Get session manager and current DataFrame
        session_manager = get_session_manager(request.session.session_key)
        df = session_manager.get_dataframe()
        
        if df is None:
            return JsonResponse({
                'success': False, 
                'error': 'No data loaded in session'
            })

        # Parse request data
        data = json.loads(request.body)
        method = data.get('method', 'mean')  # mean, median, mode, constant
        columns = data.get('columns', [])
        constant_value = data.get('constant_value', 0)
        
        # Validate columns exist
        invalid_columns = [col for col in columns if col not in df.columns]
        if invalid_columns:
            return JsonResponse({
                'success': False,
                'error': f'Columns not found: {invalid_columns}'
            })
        
        # Apply imputation using feature-engine
        df_transformed = df.copy()
        
        if method in ['mean', 'median']:
            # Use feature-engine for numerical imputation
            imputer = MeanMedianImputer(
                imputation_method=method,
                variables=columns if columns else None
            )
            df_transformed = imputer.fit_transform(df_transformed)
            
        elif method == 'mode':
            # Use feature-engine for categorical imputation
            imputer = CategoricalImputer(
                imputation_method='frequent',
                variables=columns if columns else None
            )
            df_transformed = imputer.fit_transform(df_transformed)
            
        elif method == 'constant':
            # Use feature-engine for arbitrary value imputation
            imputer = ArbitraryNumberImputer(
                arbitrary_number=constant_value,
                variables=columns if columns else None
            )
            df_transformed = imputer.fit_transform(df_transformed)
        
        # Store transformed DataFrame
        session_manager.store_dataframe(df_transformed)
        
        return JsonResponse({
            'success': True,
            'message': f'Imputation applied successfully using {method} method',
            'affected_columns': columns,
            'shape': df_transformed.shape
        })
        
    except Exception as e:
        logger.error(f"Error in apply_missing_data_imputation: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def apply_feature_encoding(request, datasource_id):
    """
    Apply feature encoding to categorical variables.
    """
    try:
        # Get session manager and current DataFrame
        session_manager = get_session_manager(request.session.session_key)
        df = session_manager.get_dataframe()
        
        if df is None:
            return JsonResponse({
                'success': False, 
                'error': 'No data loaded in session'
            })

        # Parse request data
        data = json.loads(request.body)
        method = data.get('method', 'ordinal')  # ordinal, onehot, rare_label
        columns = data.get('columns', [])
        rare_threshold = data.get('rare_threshold', 0.05)
        
        # Validate columns exist
        invalid_columns = [col for col in columns if col not in df.columns]
        if invalid_columns:
            return JsonResponse({
                'success': False,
                'error': f'Columns not found: {invalid_columns}'
            })
        
        # Apply encoding using feature-engine
        df_transformed = df.copy()
        
        if method == 'ordinal':
            # Use feature-engine OrdinalEncoder
            encoder = OrdinalEncoder(
                encoding_method='arbitrary',
                variables=columns if columns else None
            )
            df_transformed = encoder.fit_transform(df_transformed)
            
        elif method == 'onehot':
            # Use feature-engine OneHotEncoder
            encoder = OneHotEncoder(
                variables=columns if columns else None,
                drop_last=True
            )
            df_transformed = encoder.fit_transform(df_transformed)
            
        elif method == 'rare_label':
            # Use feature-engine RareLabelEncoder
            encoder = RareLabelEncoder(
                tol=rare_threshold,
                variables=columns if columns else None
            )
            df_transformed = encoder.fit_transform(df_transformed)
        
        # Store transformed DataFrame
        session_manager.store_dataframe(df_transformed)
        
        return JsonResponse({
            'success': True,
            'message': f'Encoding applied successfully using {method} method',
            'affected_columns': columns,
            'shape': df_transformed.shape
        })
        
    except Exception as e:
        logger.error(f"Error in apply_feature_encoding: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def apply_feature_scaling(request, datasource_id):
    """
    Apply feature scaling to numerical variables using sklearn transformers via feature-engine wrapper.
    """
    try:
        # Get session manager and current DataFrame
        session_manager = get_session_manager(request.session.session_key)
        df = session_manager.get_dataframe()
        
        if df is None:
            return JsonResponse({
                'success': False, 
                'error': 'No data loaded in session'
            })

        # Parse request data
        data = json.loads(request.body)
        method = data.get('method', 'standard')  # standard, minmax, robust
        columns = data.get('columns', [])
        
        # Validate columns exist
        invalid_columns = [col for col in columns if col not in df.columns]
        if invalid_columns:
            return JsonResponse({
                'success': False,
                'error': f'Columns not found: {invalid_columns}'
            })
        
        # Apply scaling using feature-engine wrapper with scikit-learn scalers
        df_transformed = df.copy()
        
        if method == 'standard':
            # Use StandardScaler via SklearnTransformerWrapper
            scaler = SklearnTransformerWrapper(
                transformer=StandardScaler(),
                variables=columns if columns else None
            )
            
        elif method == 'minmax':
            # Use MinMaxScaler via SklearnTransformerWrapper
            scaler = SklearnTransformerWrapper(
                transformer=MinMaxScaler(),
                variables=columns if columns else None
            )
            
        elif method == 'robust':
            # Use RobustScaler via SklearnTransformerWrapper
            scaler = SklearnTransformerWrapper(
                transformer=RobustScaler(),
                variables=columns if columns else None
            )
        
        df_transformed = scaler.fit_transform(df_transformed)
        
        # Store transformed DataFrame
        session_manager.store_dataframe(df_transformed)
        
        return JsonResponse({
            'success': True,
            'message': f'Scaling applied successfully using {method} method',
            'affected_columns': columns,
            'shape': df_transformed.shape
        })
        
    except Exception as e:
        logger.error(f"Error in apply_feature_scaling: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def apply_outlier_treatment(request, datasource_id):
    """
    Apply outlier treatment to numerical variables.
    """
    try:
        # Get session manager and current DataFrame
        session_manager = get_session_manager(request.session.session_key)
        df = session_manager.get_dataframe()
        
        if df is None:
            return JsonResponse({
                'success': False, 
                'error': 'No data loaded in session'
            })

        # Parse request data
        data = json.loads(request.body)
        method = data.get('method', 'winsorize')  # winsorize, trim
        columns = data.get('columns', [])
        capping_method = data.get('capping_method', 'iqr')  # iqr, quantiles
        fold = data.get('fold', 1.5)
        
        # Validate columns exist
        invalid_columns = [col for col in columns if col not in df.columns]
        if invalid_columns:
            return JsonResponse({
                'success': False,
                'error': f'Columns not found: {invalid_columns}'
            })
        
        # Apply outlier treatment using feature-engine
        df_transformed = df.copy()
        
        if method == 'winsorize':
            # Use feature-engine Winsorizer
            outlier_handler = Winsorizer(
                capping_method=capping_method,
                fold=fold,
                variables=columns if columns else None
            )
            
        elif method == 'trim':
            # Use feature-engine OutlierTrimmer
            outlier_handler = OutlierTrimmer(
                capping_method=capping_method,
                fold=fold,
                variables=columns if columns else None
            )
        
        df_transformed = outlier_handler.fit_transform(df_transformed)
        
        # Store transformed DataFrame
        session_manager.store_dataframe(df_transformed)
        
        return JsonResponse({
            'success': True,
            'message': f'Outlier treatment applied successfully using {method} method',
            'affected_columns': columns,
            'shape': df_transformed.shape
        })
        
    except Exception as e:
        logger.error(f"Error in apply_outlier_treatment: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def apply_feature_engineering(request, datasource_id):
    """
    Apply feature engineering transformations.
    """
    try:
        # Get session manager and current DataFrame
        session_manager = get_session_manager(request.session.session_key)
        df = session_manager.get_dataframe()
        
        if df is None:
            return JsonResponse({
                'success': False, 
                'error': 'No data loaded in session'
            })

        # Parse request data
        data = json.loads(request.body)
        method = data.get('method', 'math')  # math, relative
        columns = data.get('columns', [])
        operation = data.get('operation', 'add')  # add, subtract, multiply, divide, etc.
        reference_columns = data.get('reference_columns', [])
        
        # Validate columns exist
        invalid_columns = [col for col in columns if col not in df.columns]
        if invalid_columns:
            return JsonResponse({
                'success': False,
                'error': f'Columns not found: {invalid_columns}'
            })
        
        # Apply feature engineering using feature-engine
        df_transformed = df.copy()
        
        if method == 'math':
            # Use feature-engine MathFeatures
            feature_creator = MathFeatures(
                variables=columns if columns else None,
                func=[operation]
            )
            
        elif method == 'relative':
            # Use feature-engine RelativeFeatures
            if not reference_columns:
                return JsonResponse({
                    'success': False,
                    'error': 'Reference columns required for relative features'
                })
            
            feature_creator = RelativeFeatures(
                variables=columns if columns else None,
                reference=reference_columns,
                func=[operation]
            )
        
        df_transformed = feature_creator.fit_transform(df_transformed)
        
        # Store transformed DataFrame
        session_manager.store_dataframe(df_transformed)
        
        return JsonResponse({
            'success': True,
            'message': f'Feature engineering applied successfully using {method} method',
            'affected_columns': columns,
            'shape': df_transformed.shape
        })
        
    except Exception as e:
        logger.error(f"Error in apply_feature_engineering: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def apply_column_operations(request, datasource_id):
    """
    Apply column operations like rename, drop, etc.
    """
    try:
        # Get session manager and current DataFrame
        session_manager = get_session_manager(request.session.session_key)
        df = session_manager.get_dataframe()
        
        if df is None:
            return JsonResponse({
                'success': False, 
                'error': 'No data loaded in session'
            })

        # Parse request data
        data = json.loads(request.body)
        operation = data.get('operation', 'rename')  # rename, drop, duplicate
        columns = data.get('columns', [])
        new_names = data.get('new_names', {})  # For rename operation
        
        # Validate columns exist
        if operation in ['rename', 'drop', 'duplicate']:
            invalid_columns = [col for col in columns if col not in df.columns]
            if invalid_columns:
                return JsonResponse({
                    'success': False,
                    'error': f'Columns not found: {invalid_columns}'
                })
        
        # Apply column operations
        df_transformed = df.copy()
        
        if operation == 'rename':
            # Rename columns
            if new_names:
                df_transformed = df_transformed.rename(columns=new_names)
            
        elif operation == 'drop':
            # Drop columns
            df_transformed = df_transformed.drop(columns=columns)
            
        elif operation == 'duplicate':
            # Duplicate columns
            for col in columns:
                new_col_name = f"{col}_copy"
                df_transformed[new_col_name] = df_transformed[col]
        
        # Store transformed DataFrame
        session_manager.store_dataframe(df_transformed)
        
        return JsonResponse({
            'success': True,
            'message': f'Column operation "{operation}" applied successfully',
            'affected_columns': columns,
            'shape': df_transformed.shape
        })
        
    except Exception as e:
        logger.error(f"Error in apply_column_operations: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
