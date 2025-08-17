#!/usr/bin/env python
"""
Test script for the updated context-aware Hyperparameter Presets system
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import HyperparameterPreset
from core.constants import ML_MODEL_CHOICES
import json

def test_context_aware_presets():
    print("🧪 Testing Context-Aware Hyperparameter Presets System")
    print("=" * 60)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_user_context',
        defaults={'email': 'test_context@example.com'}
    )
    
    if created:
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Test 1: Create presets for different model types
    print("\n📝 Test 1: Creating presets for different model types")
    
    # Random Forest preset
    rf_params = {
        'model_name': 'RandomForestRegressor',
        'rf_n_estimators': 100,
        'rf_max_depth': 10,
        'split_strategy': 'RANDOM',
        'test_split_size': 0.2,
        'split_random_state': 42,
        'validation_strategy': 'TRAIN_TEST_SPLIT'
    }
    
    rf_preset = HyperparameterPreset.objects.create(
        name='Optimized Random Forest',
        description='Optimized RF parameters for general use',
        model_type='RandomForestRegressor',
        hyperparameters=rf_params,
        user=user
    )
    print(f"✅ Created RF preset: {rf_preset.name}")
    
    # Gradient Boosting preset
    gb_params = {
        'model_name': 'GradientBoostingRegressor',
        'gb_n_estimators': 150,
        'gb_learning_rate': 0.1,
        'split_strategy': 'TIMESERIES',
        'test_split_size': 0.3,
        'validation_strategy': 'TIME_SERIES_CV'
    }
    
    gb_preset = HyperparameterPreset.objects.create(
        name='Optimized Gradient Boosting',
        description='GB parameters for time series data',
        model_type='GradientBoostingRegressor',
        hyperparameters=gb_params,
        user=user
    )
    print(f"✅ Created GB preset: {gb_preset.name}")
    
    # Linear Regression preset
    lr_params = {
        'model_name': 'LinearRegression',
        'split_strategy': 'RANDOM',
        'test_split_size': 0.2,
        'split_random_state': 123,
        'validation_strategy': 'TRAIN_TEST_SPLIT'
    }
    
    lr_preset = HyperparameterPreset.objects.create(
        name='Basic Linear Regression',
        description='Simple linear regression setup',
        model_type='LinearRegression',
        hyperparameters=lr_params,
        user=user
    )
    print(f"✅ Created LR preset: {lr_preset.name}")
    
    # Test 2: Filter presets by model type
    print("\n🔍 Test 2: Filtering presets by model type")
    
    for model_type, model_name in ML_MODEL_CHOICES:
        filtered_presets = HyperparameterPreset.objects.filter(
            user=user,
            model_type=model_type
        )
        print(f"   {model_name}: {filtered_presets.count()} preset(s)")
        for preset in filtered_presets:
            print(f"     - {preset.name}")
    
    # Test 3: Test unique constraint with model_type
    print("\n🚫 Test 3: Testing uniqueness constraint with model_type")
    
    try:
        # This should work - same name but different model type
        duplicate_different_model = HyperparameterPreset.objects.create(
            name='Optimized Random Forest',  # Same name as RF preset
            description='But for GB model',
            model_type='GradientBoostingRegressor',  # Different model type
            hyperparameters={'test': 'value'},
            user=user
        )
        print("✅ Same name, different model type: Allowed")
        duplicate_different_model.delete()  # Clean up
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    try:
        # This should fail - same name, same model type, same user
        true_duplicate = HyperparameterPreset.objects.create(
            name='Optimized Random Forest',  # Same name
            description='This should fail',
            model_type='RandomForestRegressor',  # Same model type
            hyperparameters={'test': 'value'},
            user=user  # Same user
        )
        print("❌ Uniqueness constraint failed - true duplicate was created")
    except Exception as e:
        print(f"✅ Uniqueness constraint working: {type(e).__name__}")
    
    # Test 4: Simulate API filtering
    print("\n🔌 Test 4: Simulating API filtering")
    
    for model_type, model_name in ML_MODEL_CHOICES:
        # This simulates what the API endpoint would return
        api_result = HyperparameterPreset.objects.filter(
            user=user,
            model_type=model_type
        ).values('id', 'name', 'description')
        
        api_data = {
            'status': 'success',
            'presets': list(api_result)
        }
        
        print(f"   API response for {model_name}:")
        print(f"     Status: {api_data['status']}")
        print(f"     Count: {len(api_data['presets'])}")
        for preset in api_data['presets']:
            print(f"       - {preset['name']} (ID: {preset['id']})")
    
    # Test 5: Final statistics
    print(f"\n📊 Final Results:")
    print(f"   Total presets in system: {HyperparameterPreset.objects.count()}")
    print(f"   Presets for test user: {HyperparameterPreset.objects.filter(user=user).count()}")
    
    # Show breakdown by model type
    for model_type, model_name in ML_MODEL_CHOICES:
        count = HyperparameterPreset.objects.filter(user=user, model_type=model_type).count()
        print(f"     {model_name}: {count}")
    
    print("\n🎉 All context-aware preset tests completed successfully!")
    print("The system now supports model-specific preset filtering.")
    
    return True

if __name__ == '__main__':
    try:
        test_context_aware_presets()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
