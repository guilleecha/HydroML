#!/usr/bin/env python
"""
Test the ML experiment validation system
"""
import os
import django
import pandas as pd
import numpy as np
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from experiments.validators import MLExperimentValidator
from projects.models import DataSource, Project
from django.contrib.auth import get_user_model

def create_test_datasource(data_content, filename="test.csv"):
    """Create a mock datasource for testing"""
    class MockDataSource:
        def __init__(self, data):
            self.data = data
            self.name = filename
        
        def get_dataframe(self):
            return self.data
    
    return MockDataSource(data_content)

def test_validation_scenarios():
    print("🧪 Testing ML Experiment Validation System...")
    
    # Scenario 1: Perfect data
    print("\n📊 Test 1: Perfect dataset")
    np.random.seed(42)
    good_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 1000),
        'feature2': np.random.normal(0, 1, 1000),
        'feature3': np.random.choice(['A', 'B', 'C'], 1000),
        'target': np.random.normal(0, 1, 1000)
    })
    
    validator1 = MLExperimentValidator(
        datasource=create_test_datasource(good_data),
        target_column='target',
        feature_columns=['feature1', 'feature2', 'feature3'],
        model_name='RandomForestRegressor'
    )
    result1 = validator1.validate_all()
    
    print(f"✅ Valid: {result1['valid']}")
    print(f"⚠️  Warnings: {len(result1['warnings'])}")
    for warning in result1['warnings']:
        print(f"   - {warning}")
    
    # Scenario 2: Data with problems
    print("\n📊 Test 2: Problematic dataset")
    bad_data = pd.DataFrame({
        'feature1': [1, 1, 1, 1, 1],  # Zero variance
        'feature2': [1, 2, np.nan, 4, np.nan],  # Many NaN
        'target': [1, 1, 1, 1, 1]  # No variance
    })
    
    validator2 = MLExperimentValidator(
        datasource=create_test_datasource(bad_data),
        target_column='target',
        feature_columns=['feature1', 'feature2'],
        model_name='GradientBoostingRegressor'
    )
    result2 = validator2.validate_all()
    
    print(f"❌ Valid: {result2['valid']}")
    print(f"🚨 Errors: {len(result2['errors'])}")
    for error in result2['errors']:
        print(f"   - {error}")
    print(f"⚠️  Warnings: {len(result2['warnings'])}")
    for warning in result2['warnings']:
        print(f"   - {warning}")
    
    # Scenario 3: Small dataset
    print("\n📊 Test 3: Small dataset")
    small_data = pd.DataFrame({
        'x1': [1, 2, 3, 4, 5],
        'x2': [2, 4, 6, 8, 10],
        'y': [1.1, 2.1, 3.1, 4.1, 5.1]
    })
    
    validator3 = MLExperimentValidator(
        datasource=create_test_datasource(small_data),
        target_column='y',
        feature_columns=['x1', 'x2'],
        model_name='RandomForestRegressor'
    )
    result3 = validator3.validate_all()
    
    print(f"❌ Valid: {result3['valid']}")
    print(f"🚨 Errors: {len(result3['errors'])}")
    for error in result3['errors']:
        print(f"   - {error}")
    print(f"⚠️  Warnings: {len(result3['warnings'])}")
    for warning in result3['warnings']:
        print(f"   - {warning}")
    
    print("\n🎯 Validation testing completed!")

if __name__ == '__main__':
    test_validation_scenarios()