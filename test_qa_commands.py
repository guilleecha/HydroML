#!/usr/bin/env python3
"""
Test script to verify the QA setup and teardown commands work correctly.
This script tests both cleandb and seeddb management commands.
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and capture its output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"Command: {command}")
    print("="*60)
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
        else:
            print(f"❌ FAILED: {description} (Exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description} took longer than 5 minutes")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def check_database_counts(description):
    """Check current database object counts"""
    command = (
        "docker-compose exec web python manage.py shell -c "
        "\"from projects.models import Project, DataSource; "
        "from experiments.models import MLExperiment, ExperimentSuite; "
        "print(f'Projects: {Project.objects.count()}'); "
        "print(f'DataSources: {DataSource.objects.count()}'); "
        "print(f'MLExperiments: {MLExperiment.objects.count()}'); "
        "print(f'ExperimentSuites: {ExperimentSuite.objects.count()}')\""
    )
    
    print(f"\n📊 {description}")
    run_command(command, f"Database counts - {description}")

def main():
    """Main test execution"""
    print("🧪 HydroML QA Commands Test Suite")
    print("Testing cleandb and seeddb management commands...")
    
    # Check initial state
    check_database_counts("Initial State")
    
    # Test cleandb command
    success = run_command(
        "docker-compose exec web python manage.py cleandb --confirm",
        "Testing cleandb command (clean database)"
    )
    
    if success:
        check_database_counts("After cleandb")
    
    # Test seeddb command
    success = run_command(
        "docker-compose exec web python manage.py seeddb",
        "Testing seeddb command (populate with sample data)"
    )
    
    if success:
        check_database_counts("After seeddb")
        
        # Verify specific projects exist
        print("\n🔍 Verifying specific seeded projects...")
        verify_command = (
            "docker-compose exec web python manage.py shell -c "
            "\"from projects.models import Project; "
            "projects = Project.objects.all(); "
            "print('Created projects:'); "
            "for p in projects: print(f'  - {p.name} (DataSources: {p.datasources.count()})')\""
        )
        run_command(verify_command, "Verify seeded projects and datasources")
    
    print("\n" + "="*60)
    print("🏁 Test Suite Complete!")
    print("Review the output above to ensure all commands executed successfully.")
    print("="*60)

if __name__ == "__main__":
    main()
