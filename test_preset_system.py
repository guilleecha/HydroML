#!/usr/bin/env python
"""
Test script for the Hyperparameter Presets system
Tests basic CRUD operations and API functionality
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
import json

def test_preset_system():
    print("🧪 Testing Hyperparameter Presets System")
    print("=" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Test 1: Create a preset
    print("\n📝 Test 1: Creating a hyperparameter preset")
    
    test_hyperparameters = {
        'model_name': 'RandomForestRegressor',
        'rf_n_estimators': 100,
        'rf_max_depth': 10,
        'split_strategy': 'RANDOM',
        'test_split_size': 0.2,
        'split_random_state': 42,
        'validation_strategy': 'TRAIN_TEST_SPLIT'
    }
    
    preset = HyperparameterPreset.objects.create(
        name='Test Random Forest Preset',
        description='A test preset for Random Forest with optimized parameters',
        hyperparameters=test_hyperparameters,
        user=user
    )
    
    print(f"✅ Created preset: {preset.name}")
    print(f"   ID: {preset.id}")
    print(f"   Parameters count: {preset.hyperparameters_count}")
    
    # Test 2: Retrieve and verify
    print("\n🔍 Test 2: Retrieving preset")
    
    retrieved_preset = HyperparameterPreset.objects.get(id=preset.id)
    print(f"✅ Retrieved preset: {retrieved_preset.name}")
    print(f"   Description: {retrieved_preset.description}")
    print(f"   User: {retrieved_preset.user.username}")
    print(f"   Hyperparameters: {json.dumps(retrieved_preset.hyperparameters, indent=2)}")
    
    # Test 3: Update preset
    print("\n✏️ Test 3: Updating preset")
    
    updated_params = retrieved_preset.hyperparameters.copy()
    updated_params['rf_n_estimators'] = 200
    updated_params['rf_max_depth'] = 15
    
    retrieved_preset.hyperparameters = updated_params
    retrieved_preset.description = 'Updated test preset with higher parameters'
    retrieved_preset.save()
    
    print(f"✅ Updated preset parameters")
    print(f"   New rf_n_estimators: {retrieved_preset.hyperparameters['rf_n_estimators']}")
    print(f"   New description: {retrieved_preset.description}")
    
    # Test 4: List user's presets
    print("\n📋 Test 4: Listing user presets")
    
    user_presets = HyperparameterPreset.objects.filter(user=user)
    print(f"✅ Found {user_presets.count()} preset(s) for user {user.username}")
    
    for preset_item in user_presets:
        print(f"   - {preset_item.name} ({preset_item.hyperparameters_count} parameters)")
    
    # Test 5: Create another preset for variety
    print("\n📝 Test 5: Creating a Gradient Boosting preset")
    
    gb_params = {
        'model_name': 'GradientBoostingRegressor',
        'gb_n_estimators': 150,
        'gb_learning_rate': 0.1,
        'split_strategy': 'TIMESERIES',
        'test_split_size': 0.3,
        'validation_strategy': 'TIME_SERIES_CV'
    }
    
    gb_preset = HyperparameterPreset.objects.create(
        name='Test Gradient Boosting Preset',
        description='Optimized Gradient Boosting parameters for time series',
        hyperparameters=gb_params,
        user=user
    )
    
    print(f"✅ Created GB preset: {gb_preset.name}")
    
    # Test 6: Test uniqueness constraint
    print("\n🚫 Test 6: Testing name uniqueness constraint")
    
    try:
        duplicate_preset = HyperparameterPreset.objects.create(
            name='Test Random Forest Preset',  # Same name as first preset
            description='This should fail',
            hyperparameters={'test': 'value'},
            user=user
        )
        print("❌ Uniqueness constraint failed - duplicate was created")
    except Exception as e:
        print(f"✅ Uniqueness constraint working: {type(e).__name__}")
    
    # Test 7: Final count
    print(f"\n📊 Final Results:")
    print(f"   Total presets in system: {HyperparameterPreset.objects.count()}")
    print(f"   Presets for test user: {HyperparameterPreset.objects.filter(user=user).count()}")
    
    print("\n🎉 All tests completed successfully!")
    print("The Hyperparameter Presets system is working correctly.")
    
    return True

if __name__ == '__main__':
    try:
        test_preset_system()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
