#!/usr/bin/env python
"""
Test script for NaN cleaning functionality in Data Studio.
Tests the new QuickNaNCleaningAPIView and NaNAnalysisAPIView endpoints.
"""

import os
import sys
import django
import numpy as np
import pandas as pd
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from projects.models import DataSource, Project
from data_tools.services.session_manager import get_session_manager

def create_test_data_with_nan():
    """Create a test DataFrame with various NaN patterns."""
    np.random.seed(42)
    
    # Create test data with NaN values
    data = {
        'column_a': [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
        'column_b': [np.nan, 2, 3, np.nan, 5, 6, np.nan, 8, 9, np.nan],
        'column_c': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],  # Completely NaN
        'column_d': ['A', 'B', np.nan, 'D', 'E', 'F', 'G', np.nan, 'I', 'J'],
        'column_e': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.0]  # No NaN
    }
    
    return pd.DataFrame(data)

def test_nan_cleaning_functionality():
    """Test the complete NaN cleaning functionality."""
    print("🧹 Testing NaN Cleaning Functionality")
    print("=" * 50)
    
    try:
        # 1. Create test user
        user, created = User.objects.get_or_create(
            username='test_nan_user',
            defaults={'email': 'test@example.com'}
        )
        print(f"✅ Test user: {user.username}")
        
        # 2. Create test project
        project, created = Project.objects.get_or_create(
            name='NaN Test Project',
            defaults={'created_by': user}
        )
        print(f"✅ Test project: {project.name}")
        
        # 3. Create test DataFrame with NaN values
        test_df = create_test_data_with_nan()
        print(f"✅ Test DataFrame created: {test_df.shape}")
        print(f"   NaN counts per column:")
        for col in test_df.columns:
            nan_count = test_df[col].isna().sum()
            print(f"     {col}: {nan_count} NaN values")
        
        # 4. Create test DataSource
        datasource, created = DataSource.objects.get_or_create(
            name='NaN Test DataSource',
            defaults={
                'project': project,
                'created_by': user,
                'data_type': DataSource.DataSourceType.PREPARED,
                'status': DataSource.Status.READY,
                'file_size': 1000,
                'row_count': len(test_df),
                'column_count': len(test_df.columns)
            }
        )
        print(f"✅ Test DataSource: {datasource.name}")
        
        # 5. Initialize session with test data
        session_manager = get_session_manager(user.id, datasource.id)
        session_manager.initialize_session(test_df)
        print("✅ Session initialized with test data")
        
        # 6. Test NaN Analysis API
        print("\n📊 Testing NaN Analysis API")
        client = Client()
        client.force_login(user)
        
        analysis_url = reverse('data_tools:nan_analysis', kwargs={'datasource_id': datasource.id})
        response = client.get(analysis_url)
        
        if response.status_code == 200:
            analysis_data = response.json()
            if analysis_data.get('success'):
                analysis = analysis_data['data']
                print(f"✅ NaN Analysis successful:")
                print(f"   Total rows: {analysis['total_rows']}")
                print(f"   Total columns: {analysis['total_columns']}")
                print(f"   Total NaN cells: {analysis['total_nan_cells']}")
                print(f"   NaN percentage: {analysis['nan_cell_percentage']}%")
                print(f"   Columns with NaN: {analysis['columns_with_nan']}")
                print(f"   Completely NaN columns: {analysis['columns_completely_nan']}")
                print(f"   Rows with NaN: {analysis['rows_with_nan']}")
            else:
                print(f"❌ Analysis failed: {analysis_data.get('error')}")
                return False
        else:
            print(f"❌ Analysis API failed with status {response.status_code}")
            return False
        
        # 7. Test Quick NaN Cleaning API
        print("\n🧽 Testing Quick NaN Cleaning API")
        
        cleaning_url = reverse('data_tools:quick_nan_cleaning', kwargs={'datasource_id': datasource.id})
        cleaning_data = {
            'remove_nan_rows': 'true',
            'remove_nan_columns': 'true'
        }
        
        response = client.post(cleaning_url, cleaning_data)
        
        if response.status_code == 200:
            cleaning_result = response.json()
            if cleaning_result.get('success'):
                summary = cleaning_result['summary']
                print(f"✅ NaN Cleaning successful:")
                print(f"   Original shape: ({summary['original_rows']}, {summary['original_columns']})")
                print(f"   Final shape: ({summary['final_rows']}, {summary['final_columns']})")
                print(f"   Rows removed: {summary['rows_removed']}")
                print(f"   Columns removed: {summary['columns_removed']}")
                print(f"   Operations performed: {len(summary['operations_performed'])}")
                
                for op in summary['operations_performed']:
                    print(f"     - {op['operation']}")
                    if 'columns_removed' in op:
                        print(f"       Columns removed: {op['columns_removed']}")
                    if 'rows_removed' in op:
                        print(f"       Rows removed: {op['rows_removed']}")
            else:
                print(f"❌ Cleaning failed: {cleaning_result.get('error')}")
                return False
        else:
            print(f"❌ Cleaning API failed with status {response.status_code}")
            return False
        
        # 8. Verify cleaned data
        print("\n🔍 Verifying cleaned data")
        cleaned_df = session_manager.get_current_dataframe()
        
        if cleaned_df is not None:
            print(f"✅ Cleaned DataFrame shape: {cleaned_df.shape}")
            print(f"   Remaining NaN values: {cleaned_df.isna().sum().sum()}")
            
            # Check that column_c (completely NaN) was removed
            if 'column_c' not in cleaned_df.columns:
                print("✅ Completely NaN column was removed")
            else:
                print("❌ Completely NaN column was not removed")
                
            # Check that rows with NaN were removed
            if cleaned_df.isna().any().any():
                print("⚠️  Some NaN values still remain")
            else:
                print("✅ All NaN values removed")
        else:
            print("❌ Could not retrieve cleaned DataFrame")
            return False
        
        # 9. Test analysis after cleaning
        print("\n📊 Testing NaN Analysis after cleaning")
        response = client.get(analysis_url)
        
        if response.status_code == 200:
            analysis_data = response.json()
            if analysis_data.get('success'):
                analysis = analysis_data['data']
                print(f"✅ Post-cleaning analysis:")
                print(f"   Total NaN cells: {analysis['total_nan_cells']}")
                print(f"   Columns with NaN: {analysis['columns_with_nan']}")
                
                if analysis['total_nan_cells'] == 0:
                    print("✅ Perfect! No NaN values remaining")
                else:
                    print(f"⚠️  Still {analysis['total_nan_cells']} NaN values remaining")
        
        print("\n" + "=" * 50)
        print("🎉 NaN Cleaning functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_nan_cleaning_functionality()
    sys.exit(0 if success else 1)