#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

from django.db import connection

def check_table_structure():
    with connection.cursor() as cursor:
        # Check ExperimentSuite table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'experiments_experimentsuite' 
            ORDER BY ordinal_position;
        """)
        
        print('=== ExperimentSuite Table Structure ===')
        for row in cursor.fetchall():
            print(f'{row[0]:20} | {row[1]:15} | Nullable: {row[2]:3} | Default: {row[3] or "None"}')
        
        # Check if suite field exists in MLExperiment
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'experiments_mlexperiment' AND column_name = 'suite_id';
        """)
        
        suite_field = cursor.fetchone()
        print(f'\n=== MLExperiment suite_id field ===')
        if suite_field:
            print(f'suite_id field exists: {suite_field[0]} | {suite_field[1]} | Nullable: {suite_field[2]}')
        else:
            print('suite_id field does not exist in MLExperiment table')

        # Check indexes
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'experiments_experimentsuite';
        """)
        
        print(f'\n=== ExperimentSuite Indexes ===')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')

if __name__ == '__main__':
    check_table_structure()
