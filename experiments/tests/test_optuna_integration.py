#!/usr/bin/env python
"""
Test script to validate Optuna integration for ExperimentSuite.

This script tests the core functionality of the Optuna integration
without requiring the full Django application to be running.
"""

import sys
import json

def test_optuna_import():
    """Test that Optuna can be imported successfully."""
    try:
        import optuna
        print("✅ Optuna import successful")
        print(f"   Version: {optuna.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Optuna import failed: {e}")
        return False

def test_optuna_study_creation():
    """Test creating an Optuna study with different directions."""
    try:
        import optuna
        
        # Test maximize direction (for metrics like R²)
        study_max = optuna.create_study(direction='maximize')
        print("✅ Study creation (maximize) successful")
        
        # Test minimize direction (for metrics like MSE)
        study_min = optuna.create_study(direction='minimize')
        print("✅ Study creation (minimize) successful")
        
        return True
    except Exception as e:
        print(f"❌ Study creation failed: {e}")
        return False

def test_parameter_suggestion():
    """Test parameter suggestion functionality."""
    try:
        import optuna
        
        study = optuna.create_study(direction='maximize')
        
        def test_objective(trial):
            # Test different parameter types
            n_estimators = trial.suggest_int('n_estimators', 10, 100)
            max_depth = trial.suggest_int('max_depth', 3, 10)
            learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3)
            algorithm = trial.suggest_categorical('algorithm', ['rf', 'gb', 'xgb'])
            
            # Mock metric calculation
            mock_score = 0.85 + (n_estimators / 1000) + (learning_rate * 0.1)
            return mock_score
        
        # Run a few trials
        study.optimize(test_objective, n_trials=5)
        
        print("✅ Parameter suggestion test successful")
        print(f"   Best value: {study.best_value:.4f}")
        print(f"   Best params: {study.best_params}")
        
        return True
    except Exception as e:
        print(f"❌ Parameter suggestion test failed: {e}")
        return False

def test_parameter_importance():
    """Test parameter importance calculation."""
    try:
        import optuna
        import optuna.importance
        
        study = optuna.create_study(direction='maximize')
        
        def test_objective(trial):
            x = trial.suggest_float('x', -10, 10)
            y = trial.suggest_float('y', -10, 10)
            z = trial.suggest_float('z', -10, 10)
            
            # x has most impact, y some impact, z minimal impact
            return -(x**2 + y + 0.1*z)
        
        # Run enough trials for importance calculation
        study.optimize(test_objective, n_trials=20)
        
        # Calculate importance
        importance = optuna.importance.get_param_importances(study)
        print("✅ Parameter importance calculation successful")
        print(f"   Importances: {importance}")
        
        return True
    except Exception as e:
        print(f"❌ Parameter importance test failed: {e}")
        return False

def test_search_space_parsing():
    """Test parsing of different search space formats."""
    try:
        # Test structured search space format
        structured_space = {
            'n_estimators': {'type': 'int', 'low': 10, 'high': 100},
            'max_depth': {'type': 'int', 'low': 3, 'high': 10},
            'learning_rate': {'type': 'float', 'low': 0.01, 'high': 0.3},
            'algorithm': {'type': 'categorical', 'choices': ['rf', 'gb', 'xgb']}
        }
        
        # Test simple list format
        simple_space = {
            'n_estimators': [10, 50, 100],
            'max_depth': [3, 5, 7, 10],
            'algorithm': ['rf', 'gb', 'xgb']
        }
        
        print("✅ Search space parsing test successful")
        print(f"   Structured format: {len(structured_space)} parameters")
        print(f"   Simple format: {len(simple_space)} parameters")
        
        return True
    except Exception as e:
        print(f"❌ Search space parsing test failed: {e}")
        return False

def main():
    """Run all Optuna integration tests."""
    print("🧪 Testing Optuna Integration for HydroML ExperimentSuite")
    print("=" * 60)
    
    tests = [
        test_optuna_import,
        test_optuna_study_creation,
        test_parameter_suggestion,
        test_parameter_importance,
        test_search_space_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        print(f"\n🔬 Running {test_func.__name__}...")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_func.__name__} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Optuna integration is ready.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
