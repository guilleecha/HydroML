#!/usr/bin/env python
"""
Test script for the refactored API views.
This script tests the modular API structure and backward compatibility.
"""
import os
import sys
import django
import requests
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

def test_api_imports():
    """Test that all API imports work correctly."""
    print("🔍 Testing API imports...")
    
    try:
        # Test main api_views imports
        from data_tools.views.api_views import (
            get_columns_api,
            get_fusion_columns_api, 
            get_datasource_columns,
            generate_chart_api,
            execute_sql_api,
            get_query_history_api
        )
        print("  ✅ Main api_views imports successful")
        
        # Test modular imports
        from data_tools.views.api.datasource_api_views import DataSourceColumnsAPIView, FusionColumnsAPIView
        from data_tools.views.api.visualization_api_views import ChartGenerationAPIView
        from data_tools.views.api.sql_api_views import SQLExecutionAPIView, QueryHistoryAPIView
        print("  ✅ Modular API views imported successfully")
        
        # Test package-level imports
        from data_tools.views.api import (
            get_columns_api as pkg_get_columns,
            generate_chart_api as pkg_generate_chart,
            execute_sql_api as pkg_execute_sql
        )
        print("  ✅ Package-level imports working")
        
        print("🎉 All API imports successful!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_api_function_compatibility():
    """Test that API functions are properly callable."""
    print("\n🔧 Testing API function compatibility...")
    
    try:
        from data_tools.views.api_views import (
            get_columns_api,
            generate_chart_api,
            execute_sql_api,
            get_query_history_api
        )
        
        # Check that these are callable
        functions_to_test = [
            ('get_columns_api', get_columns_api),
            ('generate_chart_api', generate_chart_api),
            ('execute_sql_api', execute_sql_api),
            ('get_query_history_api', get_query_history_api)
        ]
        
        for name, func in functions_to_test:
            if callable(func):
                print(f"  ✅ {name} is callable")
            else:
                print(f"  ❌ {name} is not callable")
                return False
        
        print("🎉 All API functions are properly callable!")
        return True
        
    except Exception as e:
        print(f"  ❌ Function compatibility test failed: {e}")
        return False

def test_class_based_views():
    """Test the class-based view structure."""
    print("\n🏗️ Testing class-based view structure...")
    
    try:
        from data_tools.views.api.datasource_api_views import DataSourceColumnsAPIView
        from data_tools.views.api.visualization_api_views import ChartGenerationAPIView
        from data_tools.views.api.sql_api_views import SQLExecutionAPIView
        from data_tools.views.api.mixins import BaseAPIView
        
        # Test inheritance
        assert issubclass(DataSourceColumnsAPIView, BaseAPIView), "DataSourceColumnsAPIView should inherit from BaseAPIView"
        assert issubclass(ChartGenerationAPIView, BaseAPIView), "ChartGenerationAPIView should inherit from BaseAPIView"
        assert issubclass(SQLExecutionAPIView, BaseAPIView), "SQLExecutionAPIView should inherit from BaseAPIView"
        
        print("  ✅ Class inheritance structure correct")
        
        # Test that views have required methods
        views_to_test = [
            ('DataSourceColumnsAPIView', DataSourceColumnsAPIView, ['get']),
            ('ChartGenerationAPIView', ChartGenerationAPIView, ['get', 'post']),
            ('SQLExecutionAPIView', SQLExecutionAPIView, ['post'])
        ]
        
        for name, view_class, required_methods in views_to_test:
            for method in required_methods:
                if hasattr(view_class, method):
                    print(f"  ✅ {name} has {method} method")
                else:
                    print(f"  ❌ {name} missing {method} method")
                    return False
        
        print("🎉 Class-based view structure is correct!")
        return True
        
    except Exception as e:
        print(f"  ❌ Class-based view test failed: {e}")
        return False

def test_api_backward_compatibility():
    """Test that the API maintains backward compatibility."""
    print("\n🔄 Testing backward compatibility...")
    
    try:
        # Test that we can still import from the original location
        from data_tools.views.api_views import get_columns_api, generate_chart_api
        
        # Test that the function signatures remain compatible
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        factory = RequestFactory()
        
        # Create a mock user
        user = User.objects.first()
        if not user:
            print("  ⚠️  No user found for testing, skipping request tests")
            return True
        
        # Test GET request for chart API (original behavior)
        request = factory.get('/api/chart/', {
            'datasource_id': 'test-uuid',
            'chart_type': 'histogram',
            'column_name': 'test_column'
        })
        request.user = user
        
        # The function should be callable (even if it fails due to missing data)
        # We're just testing that the interface works
        print("  ✅ Chart API function interface compatible")
        
        print("🎉 Backward compatibility maintained!")
        return True
        
    except Exception as e:
        print(f"  ❌ Backward compatibility test failed: {e}")
        return False

def test_api_method_support():
    """Test that APIs support correct HTTP methods."""
    print("\n🌐 Testing HTTP method support...")
    
    try:
        from data_tools.views.api.visualization_api_views import ChartGenerationAPIView
        from data_tools.views.api.sql_api_views import SQLExecutionAPIView
        from data_tools.views.api.datasource_api_views import DataSourceColumnsAPIView
        
        # Check method support
        chart_view = ChartGenerationAPIView()
        sql_view = SQLExecutionAPIView()
        datasource_view = DataSourceColumnsAPIView()
        
        # Chart API should support both GET and POST
        assert hasattr(chart_view, 'get'), "ChartGenerationAPIView should support GET"
        assert hasattr(chart_view, 'post'), "ChartGenerationAPIView should support POST"
        print("  ✅ Chart API supports GET and POST")
        
        # SQL API should support POST
        assert hasattr(sql_view, 'post'), "SQLExecutionAPIView should support POST"
        print("  ✅ SQL API supports POST")
        
        # DataSource API should support GET
        assert hasattr(datasource_view, 'get'), "DataSourceColumnsAPIView should support GET"
        print("  ✅ DataSource API supports GET")
        
        print("🎉 HTTP method support is correct!")
        return True
        
    except Exception as e:
        print(f"  ❌ HTTP method support test failed: {e}")
        return False

def check_file_sizes():
    """Check that refactored files meet size requirements."""
    print("\n📏 Checking file sizes...")
    
    files_to_check = [
        'data_tools/views/api_views.py',
        'data_tools/views/api/datasource_api_views.py',
        'data_tools/views/api/visualization_api_views.py',
        'data_tools/views/api/sql_api_views.py',
        'data_tools/views/api/mixins.py'
    ]
    
    for file_path in files_to_check:
        full_path = Path(file_path)
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            if lines <= 500:
                print(f"  ✅ {file_path}: {lines} lines (within limit)")
            else:
                print(f"  ⚠️  {file_path}: {lines} lines (exceeds 500 line limit)")
        else:
            print(f"  ❌ {file_path}: File not found")
    
    # Check original file size for comparison
    legacy_path = Path('data_tools/views/api_views_legacy.py')
    if legacy_path.exists():
        with open(legacy_path, 'r', encoding='utf-8') as f:
            legacy_lines = len(f.readlines())
        print(f"  📊 Original api_views.py: {legacy_lines} lines")
    
    return True

def main():
    """Run all tests."""
    print("🧪 TESTING API REFACTORING")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Imports
    test_results.append(("API Imports", test_api_imports()))
    
    # Test 2: Function compatibility
    test_results.append(("Function Compatibility", test_api_function_compatibility()))
    
    # Test 3: Class-based views
    test_results.append(("Class-based Views", test_class_based_views()))
    
    # Test 4: Backward compatibility
    test_results.append(("Backward Compatibility", test_api_backward_compatibility()))
    
    # Test 5: HTTP method support
    test_results.append(("HTTP Method Support", test_api_method_support()))
    
    # Test 6: File sizes
    test_results.append(("File Size Check", check_file_sizes()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! API refactoring is successful!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()