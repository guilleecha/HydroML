# Data Fusion API Testing Guide

## Quick Test Commands

### 1. Basic API Validation (Recommended)
```bash
docker-compose exec web python manage.py test_fusion_api --verbose
```

### 2. DataSource Format Management
```bash
# Check current file formats
docker-compose exec web python manage.py verify_datasource_formats --show-details

# Convert all files to Parquet (dry run first)
docker-compose exec web python manage.py convert_datasources_to_parquet --dry-run

# Actually convert files (with backup)
docker-compose exec web python manage.py convert_datasources_to_parquet --backup
```

### 3. Manual API Testing via cURL
```bash
# Test missing parameters
docker-compose exec web curl -X GET "http://localhost:8000/tools/api/get-fusion-columns/" \
  -H "Accept: application/json"

# Test with sample UUIDs (will return 404)
docker-compose exec web curl -X GET "http://localhost:8000/tools/api/get-fusion-columns/?ds_a=00000000-0000-0000-0000-000000000000&ds_b=11111111-1111-1111-1111-111111111111" \
  -H "Accept: application/json"
```

### 3. Django Shell Testing
```bash
docker-compose exec web python manage.py shell
```

Then in the shell:
```python
from django.test import Client
from django.contrib.auth.models import User
import json

# Setup
client = Client()
user = User.objects.first()
client.force_login(user)

# Test the API
response = client.get('/tools/api/get-fusion-columns/')
print(f"Status: {response.status_code}")
print(f"Response: {json.loads(response.content)}")
```

## API Test Results Summary

✅ **All Tests Passing:**
- Parameter validation (returns 400 for missing parameters)
- UUID validation and DataSource existence checking (returns 404 for non-existent)
- URL configuration and routing
- Authentication requirements (redirects unauthenticated users)
- **Integration testing with real Parquet data** (NEW: Working after file conversion)

✅ **File Format Issue Resolved:**
- All DataSources successfully converted to Parquet format
- API now works end-to-end with real data
- Sample test result: DataSource A (5 columns) + DataSource B (28 columns)

## DataSource Management Commands

### Convert Files to Parquet Format
```bash
# Check what needs conversion (safe preview)
docker-compose exec web python manage.py convert_datasources_to_parquet --dry-run

# Convert with backup of original files
docker-compose exec web python manage.py convert_datasources_to_parquet --backup

# Force conversion (overwrite existing Parquet files)
docker-compose exec web python manage.py convert_datasources_to_parquet --force

# Convert without backup (removes original files)
docker-compose exec web python manage.py convert_datasources_to_parquet
```

### Verify DataSource Formats
```bash
# Quick format check
docker-compose exec web python manage.py verify_datasource_formats

# Detailed information with row/column counts
docker-compose exec web python manage.py verify_datasource_formats --show-details
```

## Command Features

### convert_datasources_to_parquet
- **Smart Detection**: Automatically detects file formats (CSV, Excel, JSON, TSV)
- **Encoding Handling**: Tries multiple encodings for CSV files (UTF-8, Latin-1, CP1252)
- **Safety Features**: Dry-run mode, backup options, force overwrite
- **Database Updates**: Automatically updates DataSource file paths
- **Verification**: Validates converted files are readable
- **Idempotent**: Safe to run multiple times

### verify_datasource_formats  
- **Format Overview**: Shows file extensions and sizes
- **Data Inspection**: Optional row/column counts for Parquet files
- **Health Check**: Identifies missing or corrupted files
- **Summary Stats**: Clear overview of format distribution

## File Format Issue Resolution

✅ **RESOLVED**: The file format conversion is now complete and working perfectly.

### What Was Done:
1. **Created conversion utility** - `convert_datasources_to_parquet` command
2. **Converted existing files** - CSV files successfully converted to Parquet
3. **Verified conversion** - All files now in correct format
4. **Tested integration** - API endpoint now works end-to-end with real data

### Before:
```
✗ DataSource files in mixed formats (CSV, etc.)
✗ API integration test failing with "Parquet magic bytes not found"
```

### After:
```
✓ All DataSources in Parquet format
✓ API integration test passing
✓ Real data: DataSource A (5 columns) + DataSource B (28 columns)
```

## Best Practices for Django API Testing

1. **Use Management Commands** - Avoids shell command parsing issues
2. **Test in stages** - Basic validation → Authentication → Integration
3. **Handle all error cases** - 400, 404, 500 responses
4. **Use Django test settings** - Override ALLOWED_HOSTS for test client
5. **Test with real data** - When available, test with actual datasources

## Performance Notes

- Management command execution: ~2-3 seconds
- Much faster than shell command substitution approach
- Clean, readable output with colored status indicators
- Easy to extend with additional test cases
