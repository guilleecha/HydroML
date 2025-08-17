"""
Data Tools API Documentation
============================

This module provides comprehensive API endpoints for data analysis, visualization, 
and SQL operations within the HydroML platform.

## Overview

The Data Tools API is organized into functional modules:

- **DataSource APIs**: Column analysis and data source operations
- **SQL APIs**: Query execution and history management  
- **Visualization APIs**: Chart generation and data visualization

## Authentication

All API endpoints require user authentication. Users can only access DataSources 
from projects they own.

## Base Classes and Mixins

### BaseAPIView
Base class for all data tools API views. Provides:
- User authentication via LoginRequiredMixin
- DataSource access validation
- Consistent error handling
- Standardized JSON responses

### DataSourceAccessMixin
Provides secure access to DataSources with validation:
```python
datasource = self.get_datasource(datasource_id)
validation_error = self.validate_datasource_status(datasource)
```

### APIResponseMixin
Standardizes API response format:
```python
return self.success_response({'data': result})
return self.error_response('Error message', status=400)
```

## API Endpoints

### DataSource Operations

#### GET /api/get-columns/<uuid:datasource_id>/
**Purpose**: Retrieve column information and metadata for a DataSource

**Response Format**:
```json
{
  "columns": [
    {
      "name": "column_name",
      "dtype": "float64",
      "non_null_count": 1000,
      "null_count": 0,
      "null_percentage": 0.0,
      "sample_values": [1.2, 3.4, 5.6],
      "min": 1.2,
      "max": 5.6,
      "mean": 3.4,
      "std": 1.8
    }
  ],
  "total_rows": 1000,
  "total_columns": 5
}
```

**Supported File Formats**:
- CSV (with automatic delimiter detection)
- Parquet
- Excel (.xlsx, .xls)

#### POST /api/get-fusion-columns/
**Purpose**: Get combined column information from multiple DataSources for data fusion

**Parameters**:
- `datasource_ids[]`: List of DataSource UUIDs

**Response Format**:
```json
{
  "fusion_columns": [
    {
      "datasource_id": "uuid",
      "datasource_name": "Dataset 1", 
      "column": "temperature",
      "dtype": "float64"
    }
  ],
  "datasources": [
    {
      "id": "uuid",
      "name": "Dataset 1",
      "columns": ["temp", "humidity"],
      "total_rows": 1000
    }
  ]
}
```

### SQL Operations

#### POST /api/execute-sql/
**Purpose**: Execute SQL queries against DataSource data

**Parameters**:
- `sql_query`: SQL query string (SELECT statements only)
- `datasource_id`: UUID of target DataSource

**Security Features**:
- SQL injection protection
- Read-only operations (no DDL/DML)
- Query validation

**Response Format**:
```json
{
  "data": [
    {"column1": "value1", "column2": "value2"}
  ],
  "columns": ["column1", "column2"],
  "row_count": 100,
  "column_count": 2,
  "execution_time": 0.045,
  "timestamp": 1692234567.123
}
```

**Automatic History Tracking**:
All queries are automatically saved to QueryHistory with:
- Execution time
- Success/failure status  
- Row counts
- Error messages (if applicable)

#### GET /api/query-history/
**Purpose**: Retrieve paginated SQL query execution history

**Query Parameters**:
- `datasource_id`: Filter by DataSource (optional)
- `success`: Filter by success status ('true'/'false') (optional)
- `page`: Page number (default: 1)
- `limit`: Items per page (max: 100, default: 50)

**Response Format**:
```json
{
  "history": [
    {
      "id": "uuid",
      "query": "SELECT * FROM data LIMIT 10",
      "query_preview": "SELECT * FROM data...",
      "datasource_name": "My Dataset",
      "success": true,
      "execution_time": 0.045,
      "rows_returned": 10,
      "created_at": "2023-08-17T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 245,
    "has_next": true,
    "has_previous": false
  }
}
```

### Visualization Operations

#### POST /api/generate-chart/
**Purpose**: Generate interactive charts using Plotly

**Common Parameters**:
- `datasource_id`: UUID of DataSource
- `chart_type`: Type of chart to generate
- `title`: Chart title (optional)

**Supported Chart Types**:

##### Scatter Plot
```
chart_type: 'scatter'
Required: x_axis, y_axis  
Optional: color_by, size_by, title
```

##### Line Plot
```
chart_type: 'line'
Required: x_axis, y_axis
Optional: color_by, title  
```

##### Bar Chart
```
chart_type: 'bar'
Required: x_axis, y_axis
Optional: color_by, title
```

##### Histogram  
```
chart_type: 'histogram'
Required: column
Optional: bins, color_by, title
```

##### Box Plot
```
chart_type: 'box' 
Required: y_axis
Optional: x_axis, color_by, title
```

##### Heatmap
```
chart_type: 'heatmap'
Required: x_axis, y_axis, values
Optional: title
```

**Response Format**:
```json
{
  "chart": {
    "data": [...],
    "layout": {...}
  },
  "chart_type": "scatter",
  "datasource_name": "My Dataset",
  "data_points": 1000
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

**Common Error Codes**:
- `DATASOURCE_NOT_FOUND`: DataSource doesn't exist or no access
- `DATASOURCE_NOT_READY`: DataSource is not in READY status
- `INVALID_PARAMETERS`: Missing or invalid request parameters
- `SQL_SECURITY_ERROR`: Unsafe SQL query detected
- `FILE_FORMAT_ERROR`: Unsupported or corrupted file format

## Performance Considerations

1. **File Loading**: Large files are read efficiently using pandas with chunking
2. **SQL Execution**: Uses in-memory SQLite for fast query processing
3. **Chart Generation**: Plotly charts are optimized for interactive web display
4. **Pagination**: Query history is paginated to handle large result sets

## Usage Examples

### Python/Requests
```python
import requests

# Get DataSource columns
response = requests.get(
    'http://localhost:8000/data-tools/api/get-columns/uuid-here/',
    headers={'Authorization': 'Bearer your-token'}
)

# Execute SQL query
response = requests.post(
    'http://localhost:8000/data-tools/api/execute-sql/',
    data={
        'sql_query': 'SELECT * FROM data WHERE temperature > 25',
        'datasource_id': 'uuid-here'
    },
    headers={'Authorization': 'Bearer your-token'}
)
```

### JavaScript/Fetch
```javascript
// Generate scatter plot
const response = await fetch('/data-tools/api/generate-chart/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken
    },
    body: new URLSearchParams({
        'datasource_id': dataSourceId,
        'chart_type': 'scatter',
        'x_axis': 'temperature',
        'y_axis': 'humidity',
        'color_by': 'season'
    })
});
```

## Testing

All API views include comprehensive test coverage:

```python
from django.test import TestCase
from data_tools.views.api.sql_api_views import SQLExecutionAPIView

class TestSQLExecutionAPIView(TestCase):
    def test_sql_execution_success(self):
        # Test implementation
        pass
```

## Extension Points

The modular architecture makes it easy to extend:

1. **New Chart Types**: Add methods to `ChartGenerationAPIView`
2. **Advanced SQL Features**: Extend `SQLExecutionAPIView`
3. **Custom Validations**: Create new mixins
4. **API Versioning**: Inherit from base classes for v2 APIs

This documentation covers the complete Data Tools API suite for the HydroML platform.
"""
