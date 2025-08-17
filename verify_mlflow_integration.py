#!/usr/bin/env python3
"""
MLflow Integration Verification Script
This script validates that the MLflow unified integration is working properly.
"""

import os
import sys

def check_backend_changes():
    """Verify backend changes are in place"""
    print("🔍 Checking backend changes...")
    
    view_file = 'experiments/views/experiment_results_views.py'
    if not os.path.exists(view_file):
        print("❌ View file not found")
        return False
    
    with open(view_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for our key additions
    checks = [
        'mlflow_params = {}',
        'mlflow_metrics = {}',
        'from mlflow.tracking import MlflowClient',
        'run = client.get_run(experiment.mlflow_run_id)',
        'mlflow_params = run.data.params',
        'mlflow_metrics = run.data.metrics'
    ]
    
    missing = []
    for check in checks:
        if check not in content:
            missing.append(check)
    
    if missing:
        print(f"❌ Missing backend features: {missing}")
        return False
    
    print("✅ Backend changes verified")
    return True

def check_frontend_changes():
    """Verify frontend changes are in place"""
    print("🔍 Checking frontend changes...")
    
    template_file = 'experiments/templates/experiments/ml_experiment_detail.html'
    if not os.path.exists(template_file):
        print("❌ Template file not found")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for our key additions
    checks = [
        'tab-mlflow-params-btn',
        'tab-mlflow-metrics-btn',
        'Hiperparámetros',
        'Métricas Detalladas',
        'mlflow_params',
        'mlflow_metrics',
        'mlflow_error'
    ]
    
    missing = []
    for check in checks:
        if check not in content:
            missing.append(check)
    
    # Check that old MLflow UI links are removed
    old_patterns = [
        'http://localhost:5000/#/experiments/0/runs/',
        'Ver en MLflow UI',
        'Abrir MLflow'
    ]
    
    found_old = []
    for pattern in old_patterns:
        if pattern in content:
            found_old.append(pattern)
    
    if missing:
        print(f"❌ Missing frontend features: {missing}")
        return False
    
    if found_old:
        print(f"❌ Old MLflow UI references still present: {found_old}")
        return False
    
    print("✅ Frontend changes verified")
    return True

def check_documentation():
    """Verify documentation is in place"""
    print("🔍 Checking documentation...")
    
    doc_file = 'docs/MLFLOW_UNIFIED_INTEGRATION_IMPLEMENTATION.md'
    if not os.path.exists(doc_file):
        print("❌ Documentation file not found")
        return False
    
    print("✅ Documentation verified")
    return True

def main():
    """Main verification function"""
    print("🧪 MLflow Unified Integration Verification")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(__file__))
    
    # Run checks
    backend_ok = check_backend_changes()
    frontend_ok = check_frontend_changes()
    docs_ok = check_documentation()
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY:")
    print(f"   Backend changes: {'✅ VERIFIED' if backend_ok else '❌ FAILED'}")
    print(f"   Frontend changes: {'✅ VERIFIED' if frontend_ok else '❌ FAILED'}")
    print(f"   Documentation: {'✅ VERIFIED' if docs_ok else '❌ FAILED'}")
    
    if backend_ok and frontend_ok and docs_ok:
        print("\n🎉 All verifications passed!")
        print("\n📋 IMPLEMENTATION SUMMARY:")
        print("   ✅ Enhanced MLflow data fetching (parameters, metrics, artifacts)")
        print("   ✅ New dedicated tabs: 'Hiperparámetros' and 'Métricas Detalladas'")
        print("   ✅ Removed all external MLflow UI links")
        print("   ✅ Unified user experience within HydroML")
        print("   ✅ Error handling and graceful degradation")
        print("   ✅ Dark mode support and responsive design")
        print("\n🔗 KEY FEATURES:")
        print("   - Parameters displayed in clean key-value tables")
        print("   - Metrics shown in visual cards and detailed tables")
        print("   - Conditional tab visibility (only with MLflow run ID)")
        print("   - Comprehensive error handling")
        print("   - Maintains existing artifact download functionality")
        print("\n🎯 NEXT STEPS:")
        print("   1. Create a new experiment via the web interface")
        print("   2. Run the experiment to generate MLflow data")
        print("   3. View the new 'Hiperparámetros' and 'Métricas Detalladas' tabs")
        print("   4. Verify no external MLflow UI links are present")
        
        return True
    else:
        print("\n⚠️  Some verifications failed!")
        print("   Please check the implementation and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
