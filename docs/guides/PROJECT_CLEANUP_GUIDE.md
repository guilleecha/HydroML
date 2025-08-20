# 🧹 HydroML Project Cleanup Guide

## 📋 Overview

This guide provides comprehensive instructions for maintaining a clean and organized HydroML project structure using the automated cleanup system implemented as part of the CCMP (Claude Code Management Protocol).

## 🎯 Cleanup Objectives

- **Maintain Clean Root Directory**: Only essential files should be in the project root
- **Proper File Organization**: Tests, documentation, and scripts in appropriate directories
- **Remove Obsolete Artifacts**: Clean up temporary files, backups, and cache
- **Prevent Future Clutter**: Automated prevention of common organizational issues

## 📁 Ideal Project Structure

```
hydroML/
├── 📄 manage.py                 # Django management
├── 📄 requirements.txt          # Python dependencies  
├── 📄 README.md                 # Main documentation
├── 📄 package.json              # Frontend dependencies
├── 📄 docker-compose.yml        # Container orchestration
├── 📄 .gitignore               # Git exclusions
├── 📁 accounts/                # Django auth app
├── 📁 core/                    # Core Django app
├── 📁 data_tools/              # Data processing app
├── 📁 experiments/             # ML experiments app
├── 📁 projects/                # Projects management app
├── 📁 docs/                    # All documentation
│   ├── 📁 guides/              # User guides
│   ├── 📁 implementation/      # Technical docs
│   ├── 📁 testing/            # Test documentation
│   └── 📁 archived/           # Archived/historical docs
├── 📁 scripts/                # Utility scripts
│   ├── 📁 cleanup/            # Cleanup automation
│   └── 📄 *.sh               # Shell scripts
├── 📁 tests/                  # All test files
│   ├── 📁 unit/              # Unit tests
│   ├── 📁 integration/       # Integration tests
│   ├── 📁 e2e/              # End-to-end tests
│   └── 📁 temp_files/       # Temporary test files
└── 📁 static/                # Static assets
```

## 🛠️ Using the Cleanup System

### Quick Start

```bash
# Dry run (recommended first)
python scripts/cleanup/automated_cleanup.py

# Execute cleanup
python scripts/cleanup/automated_cleanup.py --execute

# Clean specific categories only
python scripts/cleanup/automated_cleanup.py --execute --categories temp_tests temp_docs
```

### Available Cleanup Categories

#### 1. **temp_tests** - Misplaced Test Files
- **What it finds**: `test_*.py`, `*_test.py` files in wrong locations
- **Action**: Moves to `tests/temp_files/`
- **Example**: `test_enhanced_api_backend.py` in root → `tests/temp_files/`

#### 2. **temp_docs** - Temporary Documentation
- **What it finds**: `*_SUMMARY.md`, `*_backup.md`, `test_*.md` files
- **Action**: Moves to `docs/archived/`
- **Example**: `EXPORT_TESTING_SUITE_SUMMARY.md` → `docs/archived/`

#### 3. **config_duplicates** - Configuration File Duplicates  
- **What it finds**: Multiple `pytest.ini`, `.pytest_cache/` directories
- **Action**: Consolidates to canonical location
- **Example**: Keeps `data_tools/tests/pytest.ini`, removes root duplicate

#### 4. **scripts_misplaced** - Misplaced Scripts
- **What it finds**: `run_*.py`, `*.sh` files outside scripts/
- **Action**: Moves to `scripts/`
- **Example**: `run_export_coverage.py` → `scripts/run_export_coverage.py`

#### 5. **cache_files** - Cache and Temporary Files (⚠️ Disabled by default)
- **What it finds**: `__pycache__/`, `*.pyc`, `.pytest_cache/`, cache directories
- **Action**: Deletes permanently
- **Note**: Only run when explicitly requested

## 🔧 Manual Cleanup Commands

### Immediate Actions Needed

Current identified issues in HydroML:

```bash
# 1. Move misplaced test files
mkdir -p tests/temp_files
mv test_enhanced_api_backend.py tests/temp_files/
mv test_export_syntax.py tests/temp_files/

# 2. Move temporary documentation  
mkdir -p docs/archived
mv EXPORT_TESTING_SUITE_SUMMARY.md docs/archived/
mv README_backup.md docs/archived/
mv test_session_management.md docs/testing/

# 3. Move misplaced scripts
mkdir -p scripts
mv run_export_coverage.py scripts/
mv run_tests.sh scripts/

# 4. Remove duplicate config (keep the one in data_tools/tests/)
rm pytest.ini  # Root duplicate
```

### Verification Commands

```bash
# Check current root directory status
ls -la | grep -v "^d" | grep -v -E "(manage.py|requirements.txt|README.md|package.json|docker-compose.yml|Dockerfile|\.gitignore|db\.sqlite3)"

# Verify proper structure
find . -maxdepth 1 -type f -name "*.py" -not -name "manage.py"
find . -maxdepth 1 -type f -name "*.md" -not -name "README.md"
```

## 🔄 Automated Prevention

### Updated .gitignore

The enhanced `.gitignore` now prevents common cleanup issues:

```gitignore
# Temporary Development Files (should not be committed)
test_*.py  # Test files in root (should be moved to tests/)
*_SUMMARY.md  # Summary docs in root (should be in docs/)
*_backup.*  # Backup files in root
run_*.py  # Run scripts in root (should be in scripts/)
```

### Pre-commit Hooks (Recommended)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for files that shouldn't be in root
if ls *.py >/dev/null 2>&1; then
    if ! echo *.py | grep -q "^manage.py$"; then
        echo "❌ Python files found in root (other than manage.py)"
        echo "Run cleanup script: python scripts/cleanup/automated_cleanup.py"
        exit 1
    fi
fi
```

## 📊 Monitoring and Reporting

### Cleanup Reports

Every cleanup operation generates a detailed report:

```bash
# View latest cleanup report
ls -la scripts/cleanup/reports/ | tail -1

# View report contents
cat scripts/cleanup/reports/cleanup_report_*.json
```

### Backup and Recovery

```bash
# List available backups
ls -la .cleanup_backups/

# Restore from latest backup
python scripts/cleanup/automated_cleanup.py --restore

# Restore from specific backup
python scripts/cleanup/automated_cleanup.py --restore 20250820_143000
```

## 🚨 Safety Features

### Built-in Safeguards

1. **Dry Run by Default**: Never makes changes without `--execute` flag
2. **Automatic Backups**: All moved/deleted files are backed up
3. **Selective Categories**: Can target specific types of cleanup
4. **Configuration Validation**: Checks config before execution
5. **Rollback Capability**: Can restore from any backup

### Best Practices

1. **Always dry run first**: `python scripts/cleanup/automated_cleanup.py`
2. **Review the output**: Understand what will be changed
3. **Use categories**: Target specific issues with `--categories`
4. **Keep backups**: Don't immediately delete backup directories
5. **Test after cleanup**: Verify project still works correctly

## 🔧 Configuration

### Modifying Cleanup Rules

Edit `scripts/cleanup/cleanup_config.json`:

```json
{
  "cleanup_categories": {
    "custom_category": {
      "description": "Your custom cleanup rule",
      "patterns": ["*.custom"],
      "target_location": "custom/",
      "action": "move",
      "enabled": true
    }
  }
}
```

### Available Actions

- **move**: Relocate files to target directory
- **consolidate**: Merge duplicate config files
- **delete**: Permanently remove files (with backup)

## 📈 Integration with CCMP

### GitHub Issue Tracking

Cleanup operations can be tracked via GitHub issues:

```bash
# Create cleanup issue
gh issue create --title "[CLEANUP] Weekly maintenance" --body "Automated cleanup summary"
```

### Automation Schedule

Recommended cleanup schedule:

- **Daily**: Cache files cleanup (if enabled)
- **Weekly**: Full cleanup scan and dry run
- **Monthly**: Execute cleanup with review
- **Before releases**: Complete cleanup validation

## 🆘 Troubleshooting

### Common Issues

#### "Permission denied" errors
```bash
# Fix permissions
chmod +x scripts/cleanup/automated_cleanup.py
```

#### Backup directory full
```bash
# Clean old backups (older than 30 days)
find .cleanup_backups/ -type d -mtime +30 -exec rm -rf {} \;
```

#### Git conflicts after cleanup
```bash
# Reset to pre-cleanup state
python scripts/cleanup/automated_cleanup.py --restore
```

### Recovery Procedures

If cleanup goes wrong:

1. **Stop immediately**: Don't make more changes
2. **Check backup directory**: `.cleanup_backups/`
3. **Restore from backup**: Use `--restore` flag
4. **Report issue**: Create GitHub issue with error details

## 📞 Support

For cleanup issues:

1. Check this guide first
2. Review cleanup reports in `scripts/cleanup/reports/`
3. Try restore from backup
4. Create GitHub issue with:
   - Cleanup command used
   - Error message
   - Cleanup report file

---

*This guide is part of the HydroML CCMP system for maintaining code quality and project organization.*