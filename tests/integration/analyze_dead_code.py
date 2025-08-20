#!/usr/bin/env python
"""
Analyze dead code and duplications in the HydroML project.
This script identifies unused functions, duplicated code, and legacy files.
"""
import os
import sys
import ast
import re
from pathlib import Path
from collections import defaultdict, Counter

def find_function_definitions(file_path):
    """Find all function definitions in a Python file."""
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
    except (SyntaxError, UnicodeDecodeError):
        pass
    
    return functions

def find_function_calls(file_path):
    """Find all function calls in a Python file."""
    calls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple regex to find function calls
        pattern = r'(\w+)\s*\('
        calls = re.findall(pattern, content)
    except UnicodeDecodeError:
        pass
    
    return calls

def find_duplicate_functions():
    """Find duplicate function definitions across the project."""
    print("🔍 Analyzing duplicate functions...")
    
    function_locations = defaultdict(list)
    
    # Scan all Python files
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and migrations
        if '.venv' in root or 'migrations' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                functions = find_function_definitions(file_path)
                
                for func in functions:
                    function_locations[func].append(file_path)
    
    # Find duplicates
    duplicates = {func: locations for func, locations in function_locations.items() 
                 if len(locations) > 1 and not func.startswith('_')}
    
    if duplicates:
        print(f"  ⚠️  Found {len(duplicates)} potentially duplicate functions:")
        for func, locations in duplicates.items():
            print(f"    🔄 {func}:")
            for loc in locations:
                print(f"      - {loc}")
    else:
        print("  ✅ No duplicate functions found")
    
    return duplicates

def find_unused_functions():
    """Find functions that are defined but never called."""
    print("\n🔍 Analyzing unused functions...")
    
    all_definitions = set()
    all_calls = set()
    
    # Collect all function definitions and calls
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and migrations
        if '.venv' in root or 'migrations' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Collect definitions
                functions = find_function_definitions(file_path)
                all_definitions.update(functions)
                
                # Collect calls
                calls = find_function_calls(file_path)
                all_calls.update(calls)
    
    # Find unused functions (excluding common patterns)
    unused = all_definitions - all_calls
    
    # Filter out Django patterns, magic methods, etc.
    filtered_unused = {func for func in unused 
                      if not func.startswith('_') 
                      and func not in ['get', 'post', 'put', 'delete', 'dispatch']
                      and not func.endswith('_view')
                      and func not in ['main', 'setUp', 'tearDown']}
    
    if filtered_unused:
        print(f"  ⚠️  Found {len(filtered_unused)} potentially unused functions:")
        for func in sorted(filtered_unused):
            print(f"    🗑️  {func}")
    else:
        print("  ✅ No obviously unused functions found")
    
    return filtered_unused

def find_legacy_files():
    """Find legacy and backup files that can be removed."""
    print("\n🔍 Analyzing legacy files...")
    
    legacy_patterns = ['_legacy', '_backup', '.backup', '_old', '_bak']
    legacy_files = []
    
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or '__pycache__' in root:
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            if any(pattern in file for pattern in legacy_patterns):
                legacy_files.append(file_path)
    
    if legacy_files:
        print(f"  📁 Found {len(legacy_files)} legacy files:")
        total_size = 0
        for file_path in legacy_files:
            try:
                size = os.path.getsize(file_path)
                total_size += size
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                print(f"    🗂️  {file_path} ({lines} lines, {size/1024:.1f} KB)")
            except:
                print(f"    🗂️  {file_path} (unreadable)")
        
        print(f"    💾 Total legacy file size: {total_size/1024:.1f} KB")
    else:
        print("  ✅ No legacy files found")
    
    return legacy_files

def find_large_functions():
    """Find functions that exceed 50 lines (CLAUDE.md limit)."""
    print("\n🔍 Analyzing large functions...")
    
    large_functions = []
    
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or 'migrations' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Calculate function length
                            func_lines = node.end_lineno - node.lineno + 1
                            if func_lines > 50:
                                large_functions.append({
                                    'file': file_path,
                                    'function': node.name,
                                    'lines': func_lines,
                                    'start_line': node.lineno
                                })
                except (SyntaxError, UnicodeDecodeError):
                    pass
    
    if large_functions:
        print(f"  ⚠️  Found {len(large_functions)} functions exceeding 50 lines:")
        for func_info in sorted(large_functions, key=lambda x: x['lines'], reverse=True):
            print(f"    📏 {func_info['function']} in {func_info['file']}:{func_info['start_line']} ({func_info['lines']} lines)")
    else:
        print("  ✅ All functions are within 50-line limit")
    
    return large_functions

def find_large_classes():
    """Find classes that exceed 100 lines (CLAUDE.md limit)."""
    print("\n🔍 Analyzing large classes...")
    
    large_classes = []
    
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or 'migrations' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Calculate class length
                            class_lines = node.end_lineno - node.lineno + 1
                            if class_lines > 100:
                                large_classes.append({
                                    'file': file_path,
                                    'class': node.name,
                                    'lines': class_lines,
                                    'start_line': node.lineno
                                })
                except (SyntaxError, UnicodeDecodeError):
                    pass
    
    if large_classes:
        print(f"  ⚠️  Found {len(large_classes)} classes exceeding 100 lines:")
        for class_info in sorted(large_classes, key=lambda x: x['lines'], reverse=True):
            print(f"    📦 {class_info['class']} in {class_info['file']}:{class_info['start_line']} ({class_info['lines']} lines)")
    else:
        print("  ✅ All classes are within 100-line limit")
    
    return large_classes

def analyze_imports():
    """Analyze unused imports."""
    print("\n🔍 Analyzing imports...")
    
    # This is a simplified analysis - real import analysis is complex
    unused_imports = []
    
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or 'migrations' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py') and 'legacy' in file:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                    unused_imports.append({'file': file_path, 'lines': lines})
                except:
                    pass
    
    if unused_imports:
        print(f"  📦 Found {len(unused_imports)} legacy files with potential unused imports:")
        for imp in unused_imports:
            print(f"    📋 {imp['file']} ({imp['lines']} lines)")
    
    return unused_imports

def main():
    """Run all dead code analysis."""
    print("🧹 DEAD CODE ANALYSIS")
    print("=" * 60)
    
    # Change to project directory
    os.chdir('.')
    
    # Run analyses
    duplicates = find_duplicate_functions()
    unused = find_unused_functions()
    legacy_files = find_legacy_files()
    large_functions = find_large_functions()
    large_classes = find_large_classes()
    unused_imports = analyze_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEAD CODE ANALYSIS SUMMARY")
    print("=" * 60)
    
    total_issues = len(duplicates) + len(unused) + len(legacy_files) + len(large_functions) + len(large_classes)
    
    print(f"Duplicate functions: {len(duplicates)}")
    print(f"Unused functions: {len(unused)}")
    print(f"Legacy files: {len(legacy_files)}")
    print(f"Large functions (>50 lines): {len(large_functions)}")
    print(f"Large classes (>100 lines): {len(large_classes)}")
    
    print(f"\nTotal issues found: {total_issues}")
    
    if total_issues == 0:
        print("🎉 No dead code issues found!")
    else:
        print("📝 Recommendations for cleanup available above.")

if __name__ == "__main__":
    main()