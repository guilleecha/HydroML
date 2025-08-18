#!/usr/bin/env python
"""
Simple script to test data availability in Data Studio
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/app')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from projects.models import DataSource
from projects.models import Project

print("=== DEBUG TEST ===")

# List all projects
projects = Project.objects.all()
print(f"Total projects: {projects.count()}")
for p in projects:
    print(f"  Project: {p.id} - {p.name}")

# List all datasources
datasources = DataSource.objects.all()
print(f"Total datasources: {datasources.count()}")
for ds in datasources:
    print(f"  DataSource: {ds.id} - {ds.name} (Project: {ds.project.name})")
    print(f"    File: {ds.file.name if ds.file else 'No file'}")

# Test with the first datasource if it exists
if datasources.exists():
    ds = datasources.first()
    print(f"\n=== Testing with DataSource {ds.id}: {ds.name} ===")
    
    if ds.file:
        import pandas as pd
        import json
        
        try:
            file_path = ds.file.path
            print(f"File path: {file_path}")
            print(f"File exists: {os.path.exists(file_path)}")
            
            if file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
                print(f"DataFrame shape: {df.shape}")
                print(f"DataFrame columns: {list(df.columns)}")
                print(f"DataFrame dtypes: {df.dtypes}")
                
                # Prepare data as in the view
                df_head = df.head(50)
                grid_data = df_head.to_dict('records')
                print(f"Grid data rows: {len(grid_data)}")
                print(f"First row keys: {list(grid_data[0].keys()) if grid_data else 'No data'}")
                
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("No file attached to this datasource")
else:
    print("No datasources found!")

print("=== END DEBUG TEST ===")
