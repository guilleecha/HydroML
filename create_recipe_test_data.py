#!/usr/bin/env python
"""
Script to create test data for Recipe Builder functionality
"""
import os
import django
import pandas as pd
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project
from projects.models.datasource import DataSource

def create_test_data():
    """Create test data for Recipe Builder"""
    
    # Get or create user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    print(f"User {'created' if created else 'found'}: {user.username}")
    
    # Get or create project
    project, created = Project.objects.get_or_create(
        name='Recipe Builder Test Project',
        defaults={
            'description': 'Test project for Recipe Builder functionality',
            'owner': user
        }
    )
    print(f"Project {'created' if created else 'found'}: {project.name}")
    
    # Create sample hydrological data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=200, freq='D')
    
    # Generate realistic hydrological data
    flow_rate = np.random.lognormal(2, 0.8, 200)  # River flow rates (m³/s)
    precipitation = np.random.exponential(3, 200)  # Daily precipitation (mm)
    temperature = 15 + 10 * np.sin(2 * np.pi * np.arange(200) / 365) + np.random.normal(0, 3, 200)  # Temperature (°C)
    water_level = flow_rate * 0.05 + np.random.normal(2, 0.3, 200)  # Water level (m)
    ph_level = 7 + np.random.normal(0, 0.5, 200)  # pH level
    
    # Add some missing values for testing imputation
    missing_indices = np.random.choice(200, 20, replace=False)
    flow_rate[missing_indices] = np.nan
    
    # Add some missing values to other columns too
    temp_missing = np.random.choice(200, 10, replace=False)
    temperature[temp_missing] = np.nan
    
    # Create DataFrame
    data = pd.DataFrame({
        'date': dates,
        'station_code': ['ST' + str(i//20 + 1).zfill(3) for i in range(200)],  # Multiple stations
        'flow_rate': flow_rate,
        'precipitation': precipitation,
        'temperature': temperature,
        'water_level': water_level,
        'ph_level': ph_level,
        'data_quality': np.random.choice(['excellent', 'good', 'fair', 'poor'], 200, p=[0.4, 0.3, 0.2, 0.1])
    })
    
    # Convert to CSV string
    csv_data = data.to_csv(index=False)
    
    # Create DataSource
    datasource, created = DataSource.objects.get_or_create(
        name='Recipe Builder Test Data',
        defaults={
            'description': 'Hydrological test dataset with missing values for Recipe Builder testing',
            'project': project,
            'data_type': 'time_series',
            'file_data': csv_data
        }
    )
    
    print(f"DataSource {'created' if created else 'found'}: {datasource.name} (ID: {datasource.id})")
    print(f"Data shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")
    print(f"Missing values in flow_rate: {data.flow_rate.isna().sum()}")
    print(f"Missing values in temperature: {data.temperature.isna().sum()}")
    print(f"Unique stations: {data.station_code.nunique()}")
    
    # Print the Data Studio URL
    print(f"\n🎯 Test the Recipe Builder at:")
    print(f"http://localhost:8000/data_tools/data-studio/{datasource.id}/")
    
    return datasource

if __name__ == '__main__':
    create_test_data()
