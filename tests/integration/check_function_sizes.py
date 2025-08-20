#!/usr/bin/env python
"""
Check function sizes in the codebase to ensure CLAUDE.md compliance.
"""
import ast
import os
from pathlib import Path

def check_function_sizes(directory="."):
    """Check all Python files for functions exceeding 50 lines."""
    large_functions = []
    
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment and migrations
        if '.venv' in root or 'migrations' in root or '__pycache__' in root or 'node_modules' in root:
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
                                    'file': file_path.replace('.\\', ''),
                                    'function': node.name,
                                    'lines': func_lines,
                                    'start_line': node.lineno
                                })
                except (SyntaxError, UnicodeDecodeError, AttributeError):
                    pass
    
    return large_functions

def check_class_sizes(directory="."):
    """Check all Python files for classes exceeding 100 lines."""
    large_classes = []
    
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment and migrations
        if '.venv' in root or 'migrations' in root or '__pycache__' in root or 'node_modules' in root:
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
                                    'file': file_path.replace('.\\', ''),
                                    'class': node.name,
                                    'lines': class_lines,
                                    'start_line': node.lineno
                                })
                except (SyntaxError, UnicodeDecodeError, AttributeError):
                    pass
    
    return large_classes

def main():
    print("📏 CHECKING CLAUDE.MD COMPLIANCE")
    print("=" * 50)
    
    print("🔍 Checking for functions > 50 lines...")
    large_functions = check_function_sizes()
    
    if large_functions:
        print(f"  ⚠️  Found {len(large_functions)} large functions:")
        for func in sorted(large_functions, key=lambda x: x['lines'], reverse=True):
            print(f"    📏 {func['function']} ({func['lines']} lines) in {func['file']}:{func['start_line']}")
    else:
        print("  ✅ All functions are ≤ 50 lines")
    
    print("\n🔍 Checking for classes > 100 lines...")
    large_classes = check_class_sizes()
    
    if large_classes:
        print(f"  ⚠️  Found {len(large_classes)} large classes:")
        for cls in sorted(large_classes, key=lambda x: x['lines'], reverse=True):
            print(f"    📦 {cls['class']} ({cls['lines']} lines) in {cls['file']}:{cls['start_line']}")
    else:
        print("  ✅ All classes are ≤ 100 lines")
    
    print(f"\n📊 Summary:")
    print(f"  Functions > 50 lines: {len(large_functions)}")
    print(f"  Classes > 100 lines: {len(large_classes)}")
    
    if len(large_functions) == 0 and len(large_classes) == 0:
        print("🎉 All code complies with CLAUDE.md limits!")
    else:
        print("📝 Some refactoring may be needed for full compliance.")

if __name__ == "__main__":
    main()