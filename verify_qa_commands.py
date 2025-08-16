#!/usr/bin/env python3
"""
QA Commands Verification Script
This script verifies that the cleandb and seeddb management commands have been created correctly.
"""

import os

def check_file_exists(filepath):
    """Check if a file exists and show its basic info"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {filepath} exists ({size} bytes)")
        return True
    else:
        print(f"❌ {filepath} not found")
        return False

def show_file_summary(filepath, description):
    """Show a summary of the file contents"""
    if check_file_exists(filepath):
        print(f"📄 {description}:")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"   - Total lines: {len(lines)}")
                
                # Find the command class
                for i, line in enumerate(lines):
                    if 'class Command' in line:
                        print(f"   - Command class found at line {i+1}")
                        break
                
                # Find the help text
                for line in lines:
                    if 'help =' in line:
                        help_text = line.strip().split('=', 1)[1].strip().strip("'\"")
                        print(f"   - Help text: {help_text}")
                        break
                        
        except Exception as e:
            print(f"   - Error reading file: {e}")
        print()

def main():
    print("🔍 QA Commands Verification")
    print("="*50)
    
    # Check if command files exist
    cleandb_path = "core/management/commands/cleandb.py"
    seeddb_path = "core/management/commands/seeddb.py"
    
    show_file_summary(cleandb_path, "Clean Database Command")
    show_file_summary(seeddb_path, "Seed Database Command")
    
    print("📋 Manual Testing Instructions:")
    print("="*50)
    print()
    print("1. Test cleandb command:")
    print("   docker-compose exec web python manage.py cleandb --help")
    print("   docker-compose exec web python manage.py cleandb --confirm")
    print()
    print("2. Test seeddb command:")
    print("   docker-compose exec web python manage.py seeddb --help")
    print("   docker-compose exec web python manage.py seeddb")
    print()
    print("3. Verify database state:")
    print("   docker-compose exec web python manage.py shell -c \"")
    print("   from projects.models import Project, DataSource;")
    print("   print(f'Projects: {Project.objects.count()}');")
    print("   print(f'DataSources: {DataSource.objects.count()}')\"")
    print()
    print("4. Check created projects:")
    print("   docker-compose exec web python manage.py shell -c \"")
    print("   from projects.models import Project;")
    print("   for p in Project.objects.all():") 
    print("       print(f'{p.name}: {p.datasources.count()} datasources')\"")
    print()
    print("🎯 Expected Results:")
    print("- cleandb should delete all Projects, DataSources, MLExperiments, ExperimentSuites")
    print("- seeddb should create 4 projects with realistic datasets")
    print("- 'Análisis de Ventas de Supermercado' should have 2 datasets for fusion testing")
    print("- All datasets should be saved as .parquet files")

if __name__ == "__main__":
    main()
