#!/usr/bin/env python3

import os
import re

def revert_datasource_filters():
    """
    Revert owner=request.user back to project__user=request.user temporarily for migration
    """
    files_to_fix = [
        'data_tools/views/api/session_api_views.py',
        'data_tools/views/api/transformation_api_views.py'
    ]
    
    pattern = r'owner=request\.user'
    replacement = 'project__owner=request.user'
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"Reverting {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count matches
            matches = len(re.findall(pattern, content))
            print(f"  Found {matches} matches")
            
            # Replace all occurrences
            new_content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"  Reverted {matches} occurrences")
        else:
            print(f"File not found: {file_path}")

if __name__ == '__main__':
    revert_datasource_filters()
    print("Done!")
