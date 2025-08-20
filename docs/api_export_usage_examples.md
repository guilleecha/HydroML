# Export API Usage Examples

## Overview
The Export API provides RESTful endpoints for managing data export jobs and templates. This document shows practical examples of how to use the API endpoints.

## Authentication
All endpoints require user authentication. Include session authentication or login before making requests.

## Export Jobs API

### 1. Create Export Job
```bash
POST /data-tools/api/v1/exports/
Content-Type: application/json

{
    "datasource": "123e4567-e89b-12d3-a456-426614174000",
    "format": "csv",
    "filters": {
        "columns": ["col1", "col2", "col3"],
        "limit": 1000,
        "where_conditions": [
            {"column": "col1", "operator": ">", "value": 100}
        ]
    }
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Export job created successfully",
    "data": {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "status": "pending",
        "format": "csv",
        "progress": 0,
        "created_at": "2024-01-01T10:00:00Z",
        "datasource": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "My Data Source"
        }
    }
}
```

### 2. List Export Jobs
```bash
GET /data-tools/api/v1/exports/?page=1&page_size=20&status=completed
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Export jobs retrieved successfully",
    "data": {
        "export_jobs": [
            {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "status": "completed",
                "format": "csv",
                "progress": 100,
                "file_size": 1024000,
                "row_count": 5000,
                "created_at": "2024-01-01T10:00:00Z",
                "completed_at": "2024-01-01T10:05:30Z"
            }
        ],
        "pagination": {
            "total_count": 15,
            "page_count": 1,
            "current_page": 1,
            "has_next": false,
            "has_previous": false,
            "page_size": 20
        }
    }
}
```

### 3. Get Export Job Detail
```bash
GET /data-tools/api/v1/exports/456e7890-e89b-12d3-a456-426614174001/
```

### 4. Cancel Export Job
```bash
POST /data-tools/api/v1/exports/456e7890-e89b-12d3-a456-426614174001/cancel/
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Export job cancelled successfully",
    "data": {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "status": "cancelled",
        "completed_at": "2024-01-01T10:03:00Z"
    }
}
```

### 5. Retry Failed Export Job
```bash
POST /data-tools/api/v1/exports/456e7890-e89b-12d3-a456-426614174001/retry/
```

### 6. Download Export File
```bash
GET /data-tools/api/v1/exports/456e7890-e89b-12d3-a456-426614174001/download/
```

**Response:** Binary file download with appropriate content-type header.

### 7. Delete Export Job
```bash
DELETE /data-tools/api/v1/exports/456e7890-e89b-12d3-a456-426614174001/
```

## Export Templates API

### 1. Create Export Template
```bash
POST /data-tools/api/v1/export-templates/
Content-Type: application/json

{
    "name": "CSV Full Export Template",
    "description": "Template for full CSV exports with headers",
    "configuration": {
        "format": "csv",
        "filters": {
            "include_headers": true,
            "columns": ["*"]
        },
        "options": {
            "delimiter": ",",
            "encoding": "utf-8"
        }
    }
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Export template created successfully",
    "data": {
        "id": "789e0123-e89b-12d3-a456-426614174002",
        "name": "CSV Full Export Template",
        "template_type": "user",
        "is_active": true,
        "usage_count": 0,
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

### 2. List Export Templates
```bash
GET /data-tools/api/v1/export-templates/?type=user&format=csv
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Export templates retrieved successfully",
    "data": {
        "templates": [
            {
                "id": "789e0123-e89b-12d3-a456-426614174002",
                "name": "CSV Full Export Template",
                "template_type": "user",
                "format": "csv",
                "usage_count": 5,
                "has_filters": true
            }
        ],
        "total_count": 1
    }
}
```

### 3. Update Export Template
```bash
PUT /data-tools/api/v1/export-templates/789e0123-e89b-12d3-a456-426614174002/
Content-Type: application/json

{
    "name": "Updated CSV Template",
    "description": "Updated description",
    "configuration": {
        "format": "csv",
        "filters": {
            "columns": ["col1", "col2"],
            "limit": 5000
        }
    }
}
```

### 4. Delete Export Template
```bash
DELETE /data-tools/api/v1/export-templates/789e0123-e89b-12d3-a456-426614174002/
```

## Error Responses

### Validation Error (400 Bad Request)
```json
{
    "success": false,
    "error": {
        "format": "Invalid format. Must be one of: csv, json, parquet, excel"
    }
}
```

### Permission Error (403 Forbidden)
```json
{
    "success": false,
    "error": "You do not have permission to modify this template"
}
```

### Not Found (404 Not Found)
```json
{
    "success": false,
    "error": "Export job not found"
}
```

### Conflict Error (409 Conflict)
```json
{
    "success": false,
    "error": "Cannot delete job that is currently processing. Cancel it first."
}
```

## Query Parameters

### Export Jobs List
- `page`: Page number (default: 1)
- `page_size`: Items per page (max: 100, default: 20)
- `status`: Filter by status (pending, processing, completed, failed, cancelled)
- `format`: Filter by format (csv, json, parquet, excel)
- `datasource`: Filter by datasource ID
- `search`: Search in datasource name or error message

### Export Templates List
- `type`: Filter by template type (user, system, shared)
- `format`: Filter by format
- `search`: Search in name or description

## Filter Structure for Export Jobs

### Supported Filter Types
```json
{
    "filters": {
        "columns": ["col1", "col2", "col3"],
        "where_conditions": [
            {"column": "age", "operator": ">", "value": 18},
            {"column": "status", "operator": "=", "value": "active"}
        ],
        "limit": 1000,
        "order_by": "created_at DESC",
        "group_by": "category",
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    }
}
```

## Best Practices

1. **Pagination**: Always use pagination for large result sets
2. **Status Checking**: Poll job status for long-running exports
3. **Error Handling**: Implement proper error handling for all status codes
4. **File Cleanup**: Download and clean up completed exports promptly
5. **Template Reuse**: Use templates for common export configurations
6. **Permissions**: Ensure users only access their own exports and templates