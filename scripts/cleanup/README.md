# 🧹 HydroML Cleanup System

## Quick Start

```bash
# Dry run (safe, shows what would be changed)
python automated_cleanup.py

# Execute cleanup
python automated_cleanup.py --execute

# Clean specific categories
python automated_cleanup.py --execute --categories temp_tests temp_docs
```

## Files in this Directory

- **`automated_cleanup.py`** - Main cleanup script with full automation
- **`cleanup_config.json`** - Configuration file defining cleanup rules
- **`reports/`** - Generated cleanup reports (created automatically)

## Current Project Issues Detected

Based on scan of project root, these files need cleanup:

### ❌ Misplaced Test Files
- `test_enhanced_api_backend.py` → should move to `tests/temp_files/`
- `test_export_syntax.py` → should move to `tests/temp_files/`

### ❌ Temporary Documentation  
- `EXPORT_TESTING_SUITE_SUMMARY.md` → should move to `docs/archived/`
- `README_backup.md` → should move to `docs/archived/`
- `test_session_management.md` → should move to `docs/testing/`

### ❌ Misplaced Scripts
- `run_export_coverage.py` → should move to `scripts/`
- `run_tests.sh` → should move to `scripts/`

### ❌ Configuration Duplicates
- `pytest.ini` in root (duplicate of `data_tools/tests/pytest.ini`)

## Safety Features

- ✅ **Dry run by default** - Never changes anything without `--execute`
- ✅ **Automatic backups** - All files are backed up before moving/deleting  
- ✅ **Rollback capability** - Can restore from any backup
- ✅ **Selective cleanup** - Can target specific categories only
- ✅ **Detailed reporting** - Full logs of all operations

## Configuration

Edit `cleanup_config.json` to modify cleanup rules, patterns, and targets.

## More Information

See `docs/guides/PROJECT_CLEANUP_GUIDE.md` for complete documentation.