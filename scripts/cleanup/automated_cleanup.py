#!/usr/bin/env python3
"""
Automated Cleanup Script for HydroML Project
Part of CCMP (Claude Code Management Protocol) system

This script automatically identifies and optionally removes obsolete files,
temporary artifacts, and maintains project structure integrity.
"""

import os
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
import fnmatch


class HydroMLCleanupManager:
    """Manages automated cleanup operations for HydroML project"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.backup_dir = self.project_root / ".cleanup_backups"
        self.config_file = self.project_root / "scripts" / "cleanup" / "cleanup_config.json"
        
        # Files that should NEVER be in project root (except allowed ones)
        self.allowed_root_files = {
            'manage.py', 'requirements.txt', 'README.md', 'package.json', 
            'package-lock.json', 'tailwind.config.js', 'postcss.config.js',
            'docker-compose.yml', 'Dockerfile', '.gitignore', 'db.sqlite3'
        }
        
        # Patterns for files that are typically temporary/obsolete
        self.cleanup_patterns = {
            'temp_tests': {
                'patterns': ['test_*.py', '*_test.py'],
                'exclude_dirs': ['tests/', '*/tests/', '*/test/'],
                'target_location': 'tests/temp_files/',
                'action': 'move'
            },
            'temp_docs': {
                'patterns': ['*_SUMMARY.md', '*_backup.md', 'test_*.md'],
                'exclude_dirs': ['docs/'],
                'target_location': 'docs/archived/',
                'action': 'move'
            },
            'config_duplicates': {
                'patterns': ['pytest.ini', '.pytest_cache/'],
                'exclude_dirs': ['data_tools/tests/', 'tests/'],
                'target_location': None,
                'action': 'consolidate'
            },
            'scripts_misplaced': {
                'patterns': ['run_*.py', '*.sh'],
                'exclude_dirs': ['scripts/'],
                'target_location': 'scripts/',
                'action': 'move'
            },
            'cache_files': {
                'patterns': ['__pycache__/', '*.pyc', '.pytest_cache/', 'node_modules/.cache/'],
                'exclude_dirs': [],
                'target_location': None,
                'action': 'delete'
            }
        }
    
    def create_backup(self, file_path: Path) -> bool:
        """Create backup of file before cleanup operations"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / timestamp / file_path.relative_to(self.project_root)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            if file_path.is_file():
                shutil.copy2(file_path, backup_path)
            elif file_path.is_dir():
                shutil.copytree(file_path, backup_path, dirs_exist_ok=True)
            
            return True
        except Exception as e:
            print(f"❌ Failed to backup {file_path}: {e}")
            return False
    
    def scan_root_violations(self) -> List[Tuple[Path, str]]:
        """Scan for files in project root that shouldn't be there"""
        violations = []
        
        for item in self.project_root.iterdir():
            if item.name.startswith('.'):
                continue
                
            if item.is_file() and item.name not in self.allowed_root_files:
                violations.append((item, f"File shouldn't be in root: {item.name}"))
            elif item.is_dir() and item.name in ['temp', 'tmp', 'cache']:
                violations.append((item, f"Temporary directory in root: {item.name}"))
        
        return violations
    
    def find_cleanup_candidates(self) -> Dict[str, List[Path]]:
        """Find files matching cleanup patterns"""
        candidates = {category: [] for category in self.cleanup_patterns}
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            relative_root = root_path.relative_to(self.project_root)
            
            for category, config in self.cleanup_patterns.items():
                # Check if we should exclude this directory
                if any(fnmatch.fnmatch(str(relative_root), exclude) for exclude in config['exclude_dirs']):
                    continue
                
                # Check files against patterns
                for pattern in config['patterns']:
                    for file in files:
                        if fnmatch.fnmatch(file, pattern):
                            candidates[category].append(root_path / file)
                    
                    # Check directories against patterns
                    for dir_name in dirs[:]:  # Use slice to allow modification
                        if fnmatch.fnmatch(dir_name + '/', pattern):
                            candidates[category].append(root_path / dir_name)
        
        return candidates
    
    def consolidate_config_files(self, duplicates: List[Path]) -> bool:
        """Consolidate duplicate configuration files"""
        if not duplicates:
            return True
        
        # Find the canonical location (prefer tests/ over root)
        canonical = None
        for dup in duplicates:
            if 'tests' in str(dup).lower():
                canonical = dup
                break
        
        if not canonical:
            canonical = duplicates[0]
        
        print(f"📋 Consolidating config files, keeping: {canonical}")
        
        # Remove other duplicates
        for dup in duplicates:
            if dup != canonical:
                try:
                    if self.create_backup(dup):
                        if dup.is_file():
                            dup.unlink()
                        else:
                            shutil.rmtree(dup)
                        print(f"  ✅ Removed duplicate: {dup}")
                except Exception as e:
                    print(f"  ❌ Failed to remove {dup}: {e}")
                    return False
        
        return True
    
    def move_files(self, files: List[Path], target_dir: str) -> bool:
        """Move files to target directory"""
        target_path = self.project_root / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        
        success = True
        for file_path in files:
            try:
                if self.create_backup(file_path):
                    new_location = target_path / file_path.name
                    
                    if file_path.is_file():
                        shutil.move(str(file_path), str(new_location))
                    else:
                        shutil.move(str(file_path), str(new_location))
                    
                    print(f"  ✅ Moved {file_path.name} → {target_dir}")
                else:
                    success = False
            except Exception as e:
                print(f"  ❌ Failed to move {file_path}: {e}")
                success = False
        
        return success
    
    def delete_files(self, files: List[Path]) -> bool:
        """Delete temporary/cache files"""
        success = True
        for file_path in files:
            try:
                # Create backup before deletion (for safety)
                if self.create_backup(file_path):
                    if file_path.is_file():
                        file_path.unlink()
                    else:
                        shutil.rmtree(file_path)
                    print(f"  ✅ Deleted: {file_path}")
                else:
                    success = False
            except Exception as e:
                print(f"  ❌ Failed to delete {file_path}: {e}")
                success = False
        
        return success
    
    def run_cleanup(self, dry_run: bool = True, categories: Set[str] = None) -> Dict[str, bool]:
        """Run cleanup operations"""
        print("🧹 HydroML Project Cleanup")
        print("=" * 50)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        
        results = {}
        
        # Check root violations
        print("\n📁 Scanning root directory violations...")
        root_violations = self.scan_root_violations()
        if root_violations:
            print(f"Found {len(root_violations)} root violations:")
            for violation, reason in root_violations:
                print(f"  ❌ {violation.name}: {reason}")
        else:
            print("  ✅ No root directory violations found")
        
        # Find cleanup candidates
        print("\n🔍 Scanning for cleanup candidates...")
        candidates = self.find_cleanup_candidates()
        
        total_candidates = sum(len(files) for files in candidates.values())
        print(f"Found {total_candidates} files/directories for potential cleanup")
        
        # Process each category
        for category, files in candidates.items():
            if not files or (categories and category not in categories):
                continue
            
            config = self.cleanup_patterns[category]
            print(f"\n📋 Processing {category}: {len(files)} items")
            
            if dry_run:
                for file_path in files[:5]:  # Show first 5 items
                    print(f"  🔍 Would {config['action']}: {file_path}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more items")
                results[category] = True
                continue
            
            # Execute cleanup action
            if config['action'] == 'move' and config['target_location']:
                results[category] = self.move_files(files, config['target_location'])
            elif config['action'] == 'consolidate':
                results[category] = self.consolidate_config_files(files)
            elif config['action'] == 'delete':
                results[category] = self.delete_files(files)
            else:
                print(f"  ⚠️ Unknown action: {config['action']}")
                results[category] = False
        
        return results
    
    def generate_report(self, results: Dict[str, bool]) -> str:
        """Generate cleanup report"""
        timestamp = datetime.now().isoformat()
        
        report = {
            'timestamp': timestamp,
            'project_root': str(self.project_root),
            'cleanup_results': results,
            'success_rate': sum(results.values()) / len(results) if results else 0,
            'backup_location': str(self.backup_dir)
        }
        
        # Save report
        reports_dir = self.project_root / "scripts" / "cleanup" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)
    
    def restore_from_backup(self, backup_timestamp: str = None) -> bool:
        """Restore files from backup"""
        if not backup_timestamp:
            # Find latest backup
            backups = list(self.backup_dir.glob('*'))
            if not backups:
                print("❌ No backups found")
                return False
            backup_timestamp = max(backups, key=lambda x: x.stat().st_mtime).name
        
        backup_path = self.backup_dir / backup_timestamp
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_timestamp}")
            return False
        
        print(f"🔄 Restoring from backup: {backup_timestamp}")
        
        try:
            # Restore files
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    src = Path(root) / file
                    rel_path = src.relative_to(backup_path)
                    dst = self.project_root / rel_path
                    
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    
            print("✅ Restoration completed")
            return True
        except Exception as e:
            print(f"❌ Restoration failed: {e}")
            return False


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='HydroML Project Cleanup Tool')
    parser.add_argument('--execute', action='store_true', help='Execute cleanup (default is dry-run)')
    parser.add_argument('--categories', nargs='+', help='Specific categories to clean')
    parser.add_argument('--restore', type=str, help='Restore from backup (timestamp)')
    parser.add_argument('--root', type=str, help='Project root directory', default='.')
    
    args = parser.parse_args()
    
    cleanup_manager = HydroMLCleanupManager(args.root)
    
    if args.restore:
        success = cleanup_manager.restore_from_backup(args.restore)
        exit(0 if success else 1)
    
    # Run cleanup
    categories = set(args.categories) if args.categories else None
    results = cleanup_manager.run_cleanup(dry_run=not args.execute, categories=categories)
    
    # Generate report
    report_file = cleanup_manager.generate_report(results)
    
    print(f"\n📊 Cleanup completed")
    print(f"📄 Report saved to: {report_file}")
    print(f"💾 Backups available in: {cleanup_manager.backup_dir}")
    
    # Exit with success/failure code
    success_rate = sum(results.values()) / len(results) if results else 1
    exit(0 if success_rate == 1.0 else 1)


if __name__ == "__main__":
    main()