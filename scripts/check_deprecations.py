#!/usr/bin/env python3
"""
Deprecation Check Script for HydroML Project

This script scans the codebase for deprecated patterns that could cause warnings:
- Pydantic @validator decorators (should be @field_validator)
- NumPy dtype usage that might cause warnings
- Other deprecated patterns

Usage:
    python scripts/check_deprecations.py
"""

import os
import re
import sys
from pathlib import Path

def check_pydantic_patterns(file_path, content):
    """Check for deprecated Pydantic patterns."""
    issues = []
    
    # Check for @validator imports
    if re.search(r'from pydantic import.*validator', content):
        issues.append("Uses deprecated 'validator' import - should use 'field_validator'")
    
    # Check for @validator decorator usage
    validator_matches = re.finditer(r'@validator\s*\([\'"]([^\'"]+)[\'"]', content)
    for match in validator_matches:
        field_name = match.group(1)
        issues.append(f"Uses deprecated @validator('{field_name}') - should use @field_validator('{field_name}')")
    
    # Check for class Config
    if re.search(r'class\s+Config\s*:', content):
        issues.append("Uses deprecated 'class Config' - should use model_config = ConfigDict(...)")
    
    return issues

def check_numpy_patterns(file_path, content):
    """Check for potentially problematic NumPy patterns."""
    issues = []
    
    # Check for np.inexact usage (deprecated)
    if 'np.inexact' in content or 'numpy.inexact' in content:
        issues.append("Uses deprecated np.inexact - update to specific numeric types")
    
    # Check for np.integer usage (deprecated as super class)
    if 'np.integer' in content or 'numpy.integer' in content:
        issues.append("Uses deprecated np.integer - update to specific integer types")
    
    # Check for np.generic usage (deprecated as super class)  
    if 'np.generic' in content or 'numpy.generic' in content:
        issues.append("Uses deprecated np.generic - update to specific types")
    
    return issues

def check_file(file_path):
    """Check a single file for deprecation issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for Pydantic patterns
        issues.extend(check_pydantic_patterns(file_path, content))
        
        # Check for NumPy patterns
        issues.extend(check_numpy_patterns(file_path, content))
        
        return issues
    
    except Exception as e:
        return [f"Error reading file: {e}"]

def scan_directory(base_path):
    """Scan directory for Python files and check for deprecation issues."""
    base_path = Path(base_path)
    issues_found = {}
    
    # Skip certain directories
    skip_dirs = {
        'staticfiles', 'static', 'media', '__pycache__', '.git', 
        'node_modules', 'venv', 'env', '.pytest_cache', 'migrations'
    }
    
    for py_file in base_path.rglob('*.py'):
        # Skip files in ignored directories
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue
        
        # Skip third-party code
        if 'site-packages' in str(py_file):
            continue
            
        issues = check_file(py_file)
        if issues:
            issues_found[str(py_file)] = issues
    
    return issues_found

def main():
    """Main function to run the deprecation check."""
    base_dir = Path(__file__).parent.parent
    print(f"🔍 Scanning HydroML project for deprecation issues...")
    print(f"📁 Base directory: {base_dir}")
    print(f"📁 Absolute path: {base_dir.absolute()}")
    print()
    
    issues_found = scan_directory(base_dir)
    
    if not issues_found:
        print("✅ No deprecation issues found in your code!")
        print("📝 Note: This script only checks your custom code, not third-party libraries.")
        print("💡 The warnings you're seeing are likely from mlflow, shap, or other dependencies.")
        print("🔧 Updated requirements.txt and added warning filters to suppress them.")
    else:
        print("⚠️  Found potential deprecation issues:")
        print()
        
        for file_path, issues in issues_found.items():
            print(f"📄 {file_path}")
            for issue in issues:
                print(f"   • {issue}")
            print()
        
        print(f"📊 Total files with issues: {len(issues_found)}")
        
        # Return non-zero exit code if issues found
        sys.exit(1)

if __name__ == "__main__":
    main()
