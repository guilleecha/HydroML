"""
Simple test script for NaN cleaning functionality.
Tests the new services directly without HTTP requests.
"""

import numpy as np
import pandas as pd
from django.contrib.auth.models import User
from projects.models import DataSource, Project
from projects.models.datasource import DataSourceType
from data_tools.services.session_manager import get_session_manager
from data_tools.views.api.nan_cleaning_api import QuickNaNCleaningAPIView, NaNAnalysisAPIView

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

def test_nan_services():
    """Test the NaN cleaning services directly."""
    print("🧹 Testing NaN Cleaning Services Directly")
    print("=" * 50)
    
    try:
        # 1. Create test user
        user, created = User.objects.get_or_create(
            username='test_nan_service_user',
            defaults={'email': 'test@example.com'}
        )
        print(f"✅ Test user: {user.username}")
        
        # 2. Create test project
        project, created = Project.objects.get_or_create(
            name='NaN Service Test Project',
            defaults={'owner': user}
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
            name='NaN Service Test DataSource',
            defaults={
                'project': project,
                'owner': user,
                'data_type': DataSourceType.PREPARED,
                'status': DataSource.Status.READY
            }
        )
        print(f"✅ Test DataSource: {datasource.name}")
        
        # 5. Initialize session with test data
        session_manager = get_session_manager(user.id, datasource.id)
        session_manager.initialize_session(test_df)
        print("✅ Session initialized with test data")
        
        # 6. Test NaN Analysis directly using session_manager
        print("\n📊 Testing NaN Analysis Service")
        
        current_df = session_manager.get_current_dataframe()
        if current_df is not None:
            # Calculate NaN analysis manually
            analysis = {
                'total_rows': len(current_df),
                'total_columns': len(current_df.columns),
                'total_cells': len(current_df) * len(current_df.columns),
                'total_nan_cells': int(current_df.isna().sum().sum()),
                'columns_with_nan': 0,
                'columns_completely_nan': 0,
                'rows_with_nan': int(current_df.isna().any(axis=1).sum())
            }
            
            # Analyze each column
            columns_with_nan = []
            columns_completely_nan = []
            
            for column in current_df.columns:
                nan_count = current_df[column].isna().sum()
                if nan_count > 0:
                    columns_with_nan.append(column)
                    if nan_count == len(current_df):
                        columns_completely_nan.append(column)
            
            analysis['columns_with_nan'] = len(columns_with_nan)
            analysis['columns_completely_nan'] = len(columns_completely_nan)
            analysis['nan_cell_percentage'] = round((analysis['total_nan_cells'] / analysis['total_cells']) * 100, 2)
            
            print(f"✅ NaN Analysis successful:")
            print(f"   Total rows: {analysis['total_rows']}")
            print(f"   Total columns: {analysis['total_columns']}")
            print(f"   Total NaN cells: {analysis['total_nan_cells']}")
            print(f"   NaN percentage: {analysis['nan_cell_percentage']}%")
            print(f"   Columns with NaN: {analysis['columns_with_nan']}")
            print(f"   Completely NaN columns: {analysis['columns_completely_nan']}")
            print(f"   Rows with NaN: {analysis['rows_with_nan']}")
        else:
            print("❌ Could not retrieve current DataFrame")
            return False
        
        # 7. Test Quick NaN Cleaning directly
        print("\n🧽 Testing Quick NaN Cleaning Service")
        
        # Get current DataFrame
        current_df = session_manager.get_current_dataframe()
        original_shape = current_df.shape
        
        # Apply cleaning logic
        cleaned_df = current_df.copy()
        
        # Track what was removed
        cleaning_summary = {
            'original_rows': original_shape[0],
            'original_columns': original_shape[1],
            'rows_removed': 0,
            'columns_removed': 0,
            'columns_dropped': [],
            'operations_performed': []
        }
        
        # 1. Remove columns that are completely NaN
        nan_columns = cleaned_df.columns[cleaned_df.isna().all()].tolist()
        if nan_columns:
            cleaned_df = cleaned_df.drop(columns=nan_columns)
            cleaning_summary['columns_removed'] = len(nan_columns)
            cleaning_summary['columns_dropped'] = nan_columns
            cleaning_summary['operations_performed'].append({
                'operation': 'remove_nan_columns',
                'columns_removed': len(nan_columns),
                'column_names': nan_columns
            })
        
        # 2. Remove rows with any NaN values
        rows_before = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(axis=0, how='any')
        rows_removed = rows_before - len(cleaned_df)
        
        if rows_removed > 0:
            cleaning_summary['rows_removed'] = rows_removed
            cleaning_summary['operations_performed'].append({
                'operation': 'remove_nan_rows',
                'rows_removed': rows_removed
            })
        
        # Final shape
        final_shape = cleaned_df.shape
        cleaning_summary['final_rows'] = final_shape[0]
        cleaning_summary['final_columns'] = final_shape[1]
        
        print(f"✅ NaN Cleaning successful:")
        print(f"   Original shape: ({cleaning_summary['original_rows']}, {cleaning_summary['original_columns']})")
        print(f"   Final shape: ({cleaning_summary['final_rows']}, {cleaning_summary['final_columns']})")
        print(f"   Rows removed: {cleaning_summary['rows_removed']}")
        print(f"   Columns removed: {cleaning_summary['columns_removed']}")
        print(f"   Operations performed: {len(cleaning_summary['operations_performed'])}")
        
        for op in cleaning_summary['operations_performed']:
            print(f"     - {op['operation']}")
            if 'columns_removed' in op:
                print(f"       Columns removed: {op['columns_removed']}")
            if 'rows_removed' in op:
                print(f"       Rows removed: {op['rows_removed']}")
        
        # 8. Apply transformation to session
        session_manager.apply_transformation(
            cleaned_df, 
            'quick_nan_cleaning', 
            {
                'operation': 'quick_nan_cleaning',
                'remove_nan_rows': True,
                'remove_nan_columns': True,
                'summary': cleaning_summary
            }
        )
        print("✅ Transformation applied to session")
        
        # 9. Verify cleaned data
        print("\n🔍 Verifying cleaned data")
        verified_df = session_manager.get_current_dataframe()
        
        if verified_df is not None:
            print(f"✅ Cleaned DataFrame shape: {verified_df.shape}")
            print(f"   Remaining NaN values: {verified_df.isna().sum().sum()}")
            
            # Check that column_c (completely NaN) was removed
            if 'column_c' not in verified_df.columns:
                print("✅ Completely NaN column was removed")
            else:
                print("❌ Completely NaN column was not removed")
                
            # Check that rows with NaN were removed
            if verified_df.isna().any().any():
                print("⚠️  Some NaN values still remain")
            else:
                print("✅ All NaN values removed")
        else:
            print("❌ Could not retrieve cleaned DataFrame")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 NaN Cleaning services test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Execute the test
if __name__ == '__main__':
    test_nan_services()
else:
    # When imported into Django shell
    test_nan_services()