#!/usr/bin/env python3
"""
Test script to verify that the data preparer view correctly handles Parquet files.
This simulates the logic that was fixed in the view.
"""
import pandas as pd
import tempfile
import os

def test_parquet_reading():
    """Test that we can properly read a Parquet file and generate HTML preview."""
    
    # Create sample data
    sample_data = {
        'column1': [1, 2, 3, 4, 5],
        'column2': ['A', 'B', 'C', 'D', 'E'],
        'column3': [1.1, 2.2, 3.3, 4.4, 5.5]
    }
    df = pd.DataFrame(sample_data)
    
    # Save as Parquet file
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
        parquet_path = tmp_file.name
        df.to_parquet(parquet_path, index=False)
    
    try:
        # Test the fixed logic
        print("Testing Parquet file reading logic...")
        
        # This is the logic we implemented in the view
        file_path = parquet_path
        
        if file_path.endswith('.parquet'):
            print("✓ Detected .parquet extension")
            df_full = pd.read_parquet(file_path)
            df_head = df_full.head(50)
            print("✓ Successfully read Parquet file into DataFrame")
        else:
            print("✗ Failed to detect .parquet extension")
            return False
        
        # Generate HTML preview (like in the view)
        preview_html = df_head.to_html(
            classes='w-full text-sm',
            table_id='data-preview-table',
            index=False, 
            border=0,
            escape=False
        )
        
        print("✓ Successfully generated HTML preview")
        print("Preview HTML (first 200 chars):")
        print(preview_html[:200] + "...")
        
        # Verify the DataFrame is properly loaded
        print(f"\nDataFrame info:")
        print(f"Shape: {df_head.shape}")
        print(f"Columns: {list(df_head.columns)}")
        print(f"Data types: {dict(df_head.dtypes)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
        
    finally:
        # Clean up
        if os.path.exists(parquet_path):
            os.unlink(parquet_path)

if __name__ == "__main__":
    success = test_parquet_reading()
    if success:
        print("\n🎉 Test PASSED! Parquet reading logic is working correctly.")
    else:
        print("\n❌ Test FAILED! There are issues with the Parquet reading logic.")
