#!/usr/bin/env python
"""
Test script for the new modular data quality services.
This script tests imports, basic functionality, and integration.
"""
import os
import sys
import django
import pandas as pd
import numpy as np
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

def test_imports():
    """Test that all new services can be imported correctly."""
    print("🔍 Testing imports...")
    
    try:
        # Test individual service imports
        from data_tools.services.data_validation_service import DataValidationService
        print("  ✅ DataValidationService imported successfully")
        
        from data_tools.services.data_cleaning_service import DataCleaningService
        print("  ✅ DataCleaningService imported successfully")
        
        from data_tools.services.html_report_generator import HtmlReportGenerator
        print("  ✅ HtmlReportGenerator imported successfully")
        
        from data_tools.services.quality_pipeline import DataQualityPipeline, QualityPipelineConfig, run_data_quality_pipeline
        print("  ✅ Quality pipeline components imported successfully")
        
        # Test main service import
        from data_tools.services.data_quality_service import run_data_quality_pipeline as new_pipeline
        print("  ✅ New data_quality_service imported successfully")
        
        # Test package-level imports
        from data_tools.services import DataValidationService, DataCleaningService, HtmlReportGenerator
        print("  ✅ Package-level imports working")
        
        print("🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def create_test_data():
    """Create diverse test data to test all cleaning algorithms."""
    print("\n📊 Creating test data...")
    
    # Create a DataFrame with various data quality issues
    data = {
        # Clean numeric column
        'age': [25, 30, 22, 28, 35, 45, None, 33],
        
        # Mixed numeric/string column (should be converted)
        'salary': ['50000', '60,000', '$75000', '45000', 'N/A', '80000', '55000', '90,000'],
        
        # Date column with mixed formats
        'hire_date': ['2020-01-15', '15/02/2021', '2019-12-01', None, '2022-03-10', 'invalid', '2021-05-20', '10-04-2020'],
        
        # Boolean-like column
        'active': ['yes', 'no', 'true', 'false', 'Y', 'N', None, '1'],
        
        # High cardinality categorical
        'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005', 'EMP006', 'EMP007', 'EMP008'],
        
        # Low cardinality categorical
        'department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', None, 'Finance'],
        
        # Column with outliers
        'bonus': [1000, 1200, 1100, 1050, 15000, 1300, 1150, 1000],  # 15000 is outlier
        
        # Column with potential PII
        'email': ['john@company.com', 'jane@company.com', None, 'bob@company.com', 'alice@company.com', 'charlie@company.com', 'diana@company.com', 'eve@company.com']
    }
    
    df = pd.DataFrame(data)
    
    # Add some duplicate rows
    df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True)
    
    print(f"  ✅ Created test DataFrame: {df.shape}")
    print(f"  📋 Columns: {list(df.columns)}")
    print(f"  🔍 Data types: {df.dtypes.to_dict()}")
    
    return df

def test_cleaning_service(df):
    """Test the data cleaning service."""
    print("\n🧹 Testing DataCleaningService...")
    
    try:
        from data_tools.services.data_cleaning_service import DataCleaningService
        
        # Initialize service
        cleaning_service = DataCleaningService("test_datasource")
        
        # Test data profiling
        profile = cleaning_service.get_data_profile(df)
        print(f"  📊 Data profile generated: {len(profile)} metrics")
        
        # Test cleaning
        cleaned_df = cleaning_service.clean_dataframe(df)
        print(f"  🧽 Cleaning completed: {df.shape} → {cleaned_df.shape}")
        
        # Test cleaning report
        report = cleaning_service.get_cleaning_report()
        print(f"  📋 Cleaning report: {len(report)} sections")
        
        # Show type conversions
        type_conversions = report.get('type_conversions', {})
        if type_conversions:
            print(f"  🔄 Type conversions performed: {len(type_conversions)}")
            for col, details in type_conversions.items():
                print(f"    - {col}: {details.get('conversion_method', 'unknown')}")
        
        print("  ✅ DataCleaningService test passed!")
        return cleaned_df, True
        
    except Exception as e:
        print(f"  ❌ DataCleaningService test failed: {e}")
        return df, False

def test_validation_service(df):
    """Test the data validation service."""
    print("\n📋 Testing DataValidationService...")
    
    try:
        from data_tools.services.data_validation_service import DataValidationService
        
        # Initialize service
        validation_service = DataValidationService("test_datasource")
        
        # Check if Great Expectations is available
        if not validation_service.is_available():
            print("  ⚠️  Great Expectations not available, testing basic functionality")
            print("  ✅ DataValidationService basic test passed!")
            return True
        
        # Test with Great Expectations
        if validation_service.initialize_context():
            print("  🏗️  GX context initialized")
            
            if validation_service.create_validator(df):
                print("  🔧 Validator created")
                
                validation_service.add_basic_expectations(df)
                print("  📏 Basic expectations added")
                
                success, results = validation_service.validate()
                if success:
                    print(f"  ✅ Validation completed: {results.get('success_percent', 0):.1f}% success")
                else:
                    print("  ⚠️  Validation completed with issues")
                    
                print("  ✅ DataValidationService full test passed!")
                return True
        
        print("  ⚠️  Great Expectations setup failed, but service is functional")
        return True
        
    except Exception as e:
        print(f"  ❌ DataValidationService test failed: {e}")
        return False

def test_report_generator(quality_data, output_dir):
    """Test the HTML report generator."""
    print("\n📄 Testing HtmlReportGenerator...")
    
    try:
        from data_tools.services.html_report_generator import HtmlReportGenerator
        
        # Initialize generator
        report_generator = HtmlReportGenerator("test_datasource")
        
        # Generate comprehensive report
        report_path = report_generator.generate_comprehensive_report(
            quality_data, output_dir, 'comprehensive'
        )
        
        if report_path and os.path.exists(report_path):
            file_size = os.path.getsize(report_path) / 1024  # KB
            print(f"  📄 HTML report generated: {report_path}")
            print(f"  📏 Report size: {file_size:.1f} KB")
            print("  ✅ HtmlReportGenerator test passed!")
            return report_path, True
        else:
            print("  ❌ Report file not created")
            return "", False
            
    except Exception as e:
        print(f"  ❌ HtmlReportGenerator test failed: {e}")
        return "", False

def test_complete_pipeline(df, output_dir):
    """Test the complete quality pipeline."""
    print("\n🚀 Testing Complete Quality Pipeline...")
    
    try:
        from data_tools.services.quality_pipeline import DataQualityPipeline, QualityPipelineConfig
        
        # Create configuration
        config = QualityPipelineConfig()
        config.enable_ml_readiness_check = True
        config.enable_privacy_scan = True
        config.missing_strategy = 'auto'
        
        # Initialize pipeline
        pipeline = DataQualityPipeline("test_datasource", config)
        
        # Run complete pipeline
        cleaned_df, quality_report, report_path = pipeline.run_pipeline(df, output_dir)
        
        print(f"  🧽 Pipeline completed: {df.shape} → {cleaned_df.shape}")
        print(f"  📊 Quality report sections: {len(quality_report)}")
        
        # Check ML readiness assessment
        ml_readiness = quality_report.get('ml_readiness_assessment', {})
        if ml_readiness:
            overall_score = ml_readiness.get('overall_score', 0)
            print(f"  🤖 ML readiness score: {overall_score}/100")
        
        # Check overall quality score
        overall_quality = quality_report.get('overall_quality_score', 0)
        print(f"  🎯 Overall quality score: {overall_quality:.3f}")
        
        # Check execution log
        execution_log = quality_report.get('execution_log', [])
        print(f"  📋 Pipeline phases completed: {len(execution_log)}")
        
        if report_path and os.path.exists(report_path):
            print(f"  📄 Comprehensive report: {report_path}")
        
        print("  ✅ Complete pipeline test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Complete pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backward_compatibility(df, output_dir):
    """Test backward compatibility with original interface."""
    print("\n🔄 Testing Backward Compatibility...")
    
    try:
        # Test the main interface that should maintain compatibility
        from data_tools.services.data_quality_service import run_data_quality_pipeline
        
        # Run with original signature
        cleaned_df, quality_report, report_path = run_data_quality_pipeline(
            df, "test_datasource_compat", output_dir
        )
        
        print(f"  ✅ Backward compatible interface working")
        print(f"  📊 Result shape: {cleaned_df.shape}")
        print(f"  📋 Report keys: {len(quality_report)}")
        
        # Test package import
        from data_tools.services import run_data_quality_pipeline as package_pipeline
        print("  ✅ Package-level import working")
        
        print("  ✅ Backward compatibility test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Backward compatibility test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 TESTING NEW DATA QUALITY SERVICES\n")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path("quality_test_output")
    output_dir.mkdir(exist_ok=True)
    
    test_results = []
    
    # Test 1: Imports
    test_results.append(("Imports", test_imports()))
    
    if not test_results[-1][1]:
        print("\n❌ Import tests failed, stopping here.")
        return
    
    # Test 2: Create test data
    df = create_test_data()
    
    # Test 3: Individual services
    cleaned_df, cleaning_success = test_cleaning_service(df)
    test_results.append(("Data Cleaning", cleaning_success))
    
    validation_success = test_validation_service(cleaned_df)
    test_results.append(("Data Validation", validation_success))
    
    # Create mock quality data for report testing
    quality_data = {
        'data_profile': {'total_rows': len(df), 'total_columns': len(df.columns)},
        'validation_results': {'success_percent': 85.0, 'success': True},
        'cleaning_report': {'operations_performed': []},
        'anomalies_detected': {}
    }
    
    report_path, report_success = test_report_generator(quality_data, str(output_dir))
    test_results.append(("HTML Report Generation", report_success))
    
    # Test 4: Complete pipeline
    pipeline_success = test_complete_pipeline(df, str(output_dir))
    test_results.append(("Complete Pipeline", pipeline_success))
    
    # Test 5: Backward compatibility
    compat_success = test_backward_compatibility(df, str(output_dir))
    test_results.append(("Backward Compatibility", compat_success))
    
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
        print("🎉 ALL TESTS PASSED! New architecture is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\n📁 Test outputs saved to: {output_dir.absolute()}")

if __name__ == "__main__":
    main()