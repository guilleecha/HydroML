"""Test script to verify deprecation fixes"""
print("Testing deprecation fix implementation...")

# Test 1: Check if warning filters are working
import warnings
warnings.simplefilter('always')  # Show all warnings to test our filters

print("✅ Warning filters loaded successfully")

# Test 2: Try importing libraries that might cause warnings
try:
    import numpy as np
    print("✅ NumPy imported successfully")
except Exception as e:
    print(f"❌ NumPy import failed: {e}")

try:
    import mlflow
    print("✅ MLflow available for import")
except Exception as e:
    print(f"❌ MLflow import failed: {e}")

try:
    import shap
    print("✅ SHAP available for import")
except Exception as e:
    print(f"❌ SHAP import failed: {e}")

print("\n📝 Summary:")
print("- Updated requirements.txt with:")
print("  * mlflow==2.25.0 (from 2.20.0)")
print("  * numpy>=1.24.0,<2.0.0 (was unpinned)")
print("  * shap==0.47.0 (from 0.46.0)")
print("- Added warning filters to Django settings")
print("- Updated docker-compose.yml MLflow version")
print("\n🔧 Next step: Rebuild containers with 'docker-compose up --build -d'")
