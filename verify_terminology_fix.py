#!/usr/bin/env python3
"""
Verification script for terminology fix and button functionality
This script checks that all terminology has been updated and the button structure is correct
"""
import os
import re
from pathlib import Path

def find_template_files():
    """Find all HTML template files in the project"""
    template_files = []
    for root, dirs, files in os.walk("."):
        if "templates" in root:
            for file in files:
                if file.endswith(".html"):
                    template_files.append(os.path.join(root, file))
    return template_files

def check_terminology(files):
    """Check for any remaining Spanish 'Proyecto' terms"""
    issues = []
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for remaining Spanish terms
            if re.search(r'\bProyecto\b', content) or re.search(r'\bproyecto\b', content):
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if re.search(r'\bProyecto\b|\bproyecto\b', line):
                        issues.append(f"{file_path}:{i}: {line.strip()}")
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return issues

def check_button_structure():
    """Check the specific dashboard button for proper HTML structure"""
    dashboard_path = "core/templates/core/dashboard.html"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper button structure around the new project button
        if '@click="openNewProjectPanel()"' in content:
            # Find the line with the click handler
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '@click="openNewProjectPanel()"' in line:
                    # Check if it's properly structured as a button
                    if '<button' in line and 'Nuevo Workspace' in content[content.find(line):content.find(line) + 500]:
                        return True, f"Button correctly structured at line {i+1}"
                    else:
                        return False, f"Button structure issue at line {i+1}: {line.strip()}"
        
        return False, "No button with openNewProjectPanel() found"
        
    except Exception as e:
        return False, f"Error checking button structure: {e}"

def main():
    print("=== HydroML Terminology and Button Fix Verification ===\n")
    
    # Find all template files
    template_files = find_template_files()
    print(f"Found {len(template_files)} HTML template files\n")
    
    # Check terminology
    print("1. Checking for remaining Spanish 'Proyecto' terms...")
    terminology_issues = check_terminology(template_files)
    
    if terminology_issues:
        print(f"❌ Found {len(terminology_issues)} terminology issues:")
        for issue in terminology_issues:
            print(f"   {issue}")
    else:
        print("✅ No remaining Spanish 'Proyecto' terms found!")
    
    print()
    
    # Check button structure
    print("2. Checking dashboard button structure...")
    button_ok, button_msg = check_button_structure()
    
    if button_ok:
        print(f"✅ {button_msg}")
    else:
        print(f"❌ {button_msg}")
    
    print()
    
    # Summary
    if not terminology_issues and button_ok:
        print("🎉 All checks passed! The terminology fix and button repair are complete.")
    else:
        print("⚠️  Some issues found. Please review the output above.")
    
    return len(terminology_issues) == 0 and button_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
