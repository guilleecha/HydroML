"""
API Documentation System for Data Studio
Provides interactive API documentation with examples and testing
"""

import json
import logging
from typing import Dict, Any, List
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views import View

from data_tools.services.api_performance_service import get_api_stats, rate_limit, monitor_performance

logger = logging.getLogger(__name__)


class APIDocumentationView(View):
    """
    Interactive API documentation view
    """
    
    def get(self, request):
        """
        Serve API documentation page
        """
        api_specs = self.get_api_specifications()
        context = {
            'api_specs': api_specs,
            'base_url': request.build_absolute_uri('/data-tools/api/'),
            'websocket_url': self.get_websocket_url(request)
        }
        
        return TemplateResponse(request, 'data_tools/api_documentation.html', context)
    
    def get_websocket_url(self, request):
        """Get WebSocket URL for the current environment"""
        is_secure = request.is_secure()
        host = request.get_host()
        protocol = 'wss' if is_secure else 'ws'
        return f"{protocol}://{host}/ws/data-studio/"
    
    def get_api_specifications(self) -> Dict[str, Any]:
        """
        Get comprehensive API specifications
        """
        return {
            "info": {
                "title": "HydroML Data Studio API",
                "version": "2.0.0",
                "description": "Advanced API for data transformation, analysis, and real-time operations"
            },
            "authentication": {
                "type": "session",
                "description": "Django session authentication required for all endpoints"
            },
            "rate_limiting": {
                "description": "Most endpoints have rate limiting applied",
                "headers": {
                    "X-RateLimit-Limit": "Maximum requests allowed",
                    "X-RateLimit-Remaining": "Requests remaining in window",
                    "X-RateLimit-Reset": "Time when rate limit resets"
                }
            },
            "caching": {
                "description": "Read-only endpoints use intelligent caching",
                "headers": {
                    "X-Cache": "HIT or MISS to indicate cache status",
                    "X-Cache-TTL": "Cache time-to-live in seconds"
                }
            },
            "real_time": {
                "websocket_url": "/ws/data-studio/<datasource_id>/",
                "description": "Real-time updates for transformations and bulk operations"
            },
            "endpoints": {
                "session_management": {
                    "base_path": "/api/studio/<datasource_id>/session/",
                    "endpoints": {
                        "initialize": {
                            "method": "POST",
                            "path": "initialize/",
                            "description": "Initialize a new data transformation session",
                            "rate_limit": "10 requests per hour",
                            "parameters": {},
                            "response_example": {
                                "success": True,
                                "session_info": {
                                    "session_exists": True,
                                    "session_id": "uuid",
                                    "history_length": 1,
                                    "current_position": 0
                                },
                                "data_preview": [],
                                "column_info": []
                            }
                        },
                        "status": {
                            "method": "GET",
                            "path": "status/",
                            "description": "Get current session status",
                            "rate_limit": "60 requests per minute",
                            "cached": True,
                            "cache_ttl": "30 seconds",
                            "response_example": {
                                "success": True,
                                "session_info": {
                                    "session_exists": False
                                }
                            }
                        },
                        "undo": {
                            "method": "POST",
                            "path": "undo/",
                            "description": "Undo last transformation",
                            "rate_limit": "30 requests per minute",
                            "websocket_events": ["session_state_changed"]
                        },
                        "redo": {
                            "method": "POST",
                            "path": "redo/",
                            "description": "Redo previously undone transformation",
                            "rate_limit": "30 requests per minute",
                            "websocket_events": ["session_state_changed"]
                        },
                        "save": {
                            "method": "POST",
                            "path": "save/",
                            "description": "Save current session as new dataset",
                            "rate_limit": "5 requests per hour",
                            "parameters": {
                                "name": "string (optional)",
                                "description": "string (optional)"
                            }
                        }
                    }
                },
                "bulk_operations": {
                    "base_path": "/api/studio/<datasource_id>/bulk/",
                    "endpoints": {
                        "start_operation": {
                            "method": "POST",
                            "path": "",
                            "description": "Start a bulk operation with real-time progress",
                            "rate_limit": "10 requests per hour",
                            "websocket_events": ["bulk_operation_progress"],
                            "parameters": {
                                "operation_type": {
                                    "type": "string",
                                    "required": True,
                                    "options": ["delete_rows", "update_cells", "apply_transformations", "column_operations"]
                                },
                                "items": {
                                    "type": "array",
                                    "required": True,
                                    "description": "List of items to process"
                                },
                                "parameters": {
                                    "type": "object",
                                    "required": False,
                                    "description": "Operation-specific parameters"
                                },
                                "options": {
                                    "type": "object",
                                    "required": False,
                                    "properties": {
                                        "batch_size": "number (default: 100)"
                                    }
                                }
                            },
                            "request_example": {
                                "operation_type": "delete_rows",
                                "items": [1, 2, 3, 10, 15],
                                "options": {
                                    "batch_size": 50
                                }
                            },
                            "response_example": {
                                "success": True,
                                "data": {
                                    "operation_id": "uuid",
                                    "status": "started",
                                    "total_items": 5
                                }
                            }
                        },
                        "get_status": {
                            "method": "GET",
                            "path": "?operation_id=<uuid>",
                            "description": "Get bulk operation status",
                            "rate_limit": "60 requests per minute",
                            "cached": True,
                            "cache_ttl": "10 seconds",
                            "response_example": {
                                "success": True,
                                "data": {
                                    "id": "uuid",
                                    "status": "running",
                                    "total_items": 100,
                                    "processed_items": 45,
                                    "errors": [],
                                    "started_at": 1234567890.123,
                                    "duration": 15.5
                                }
                            }
                        }
                    }
                },
                "transformations": {
                    "base_path": "/api/studio/<datasource_id>/transform/",
                    "endpoints": {
                        "imputation": {
                            "method": "POST",
                            "path": "imputation/",
                            "description": "Apply missing data imputation",
                            "rate_limit": "20 requests per hour",
                            "websocket_events": ["data_transformation_update"],
                            "parameters": {
                                "columns": "array of column names",
                                "method": "string (mean, median, mode, forward_fill, backward_fill)",
                                "custom_value": "optional custom fill value"
                            }
                        },
                        "encoding": {
                            "method": "POST",
                            "path": "encoding/",
                            "description": "Apply feature encoding",
                            "parameters": {
                                "columns": "array of column names",
                                "encoding_type": "string (onehot, label, ordinal)"
                            }
                        },
                        "scaling": {
                            "method": "POST",
                            "path": "scaling/",
                            "description": "Apply feature scaling",
                            "parameters": {
                                "columns": "array of numeric column names",
                                "scaler_type": "string (standard, minmax, robust)"
                            }
                        }
                    }
                },
                "data_access": {
                    "base_path": "/api/studio/<datasource_id>/",
                    "endpoints": {
                        "data_preview": {
                            "method": "GET",
                            "path": "data/",
                            "description": "Get paginated data preview",
                            "rate_limit": "100 requests per hour",
                            "cached": True,
                            "cache_ttl": "60 seconds",
                            "parameters": {
                                "page": "number (default: 1)",
                                "page_size": "number (default: 25, max: 1000)",
                                "sort_by": "string (column name)",
                                "sort_order": "string (asc, desc)"
                            }
                        }
                    }
                },
                "nan_cleaning": {
                    "base_path": "/api/studio/<datasource_id>/nan/",
                    "endpoints": {
                        "analysis": {
                            "method": "GET",
                            "path": "analysis/",
                            "description": "Analyze missing data patterns",
                            "cached": True,
                            "cache_ttl": "300 seconds"
                        },
                        "quick_clean": {
                            "method": "POST",
                            "path": "quick-clean/",
                            "description": "Quick NaN cleaning operations"
                        }
                    }
                },
                "export": {
                    "base_path": "/api/v1/exports/",
                    "endpoints": {
                        "create_job": {
                            "method": "POST",
                            "path": "",
                            "description": "Create new export job",
                            "rate_limit": "10 requests per hour"
                        },
                        "job_status": {
                            "method": "GET",
                            "path": "<job_id>/",
                            "description": "Get export job status"
                        },
                        "download": {
                            "method": "GET",
                            "path": "<job_id>/download/",
                            "description": "Download completed export"
                        }
                    }
                }
            },
            "websocket_events": {
                "connection_established": {
                    "description": "Sent when WebSocket connection is established",
                    "example": {
                        "type": "connection_established",
                        "datasource_id": "uuid",
                        "timestamp": 1234567890.123,
                        "message": "Real-time updates enabled"
                    }
                },
                "data_transformation_update": {
                    "description": "Real-time transformation progress updates",
                    "example": {
                        "type": "transformation_progress",
                        "operation_id": "uuid",
                        "progress": 0.75,
                        "status": "running",
                        "message": "Processing batch 3 of 4",
                        "timestamp": 1234567890.123
                    }
                },
                "bulk_operation_progress": {
                    "description": "Bulk operation progress updates",
                    "example": {
                        "type": "bulk_progress",
                        "operation_id": "uuid",
                        "processed": 750,
                        "total": 1000,
                        "status": "running",
                        "errors": [],
                        "timestamp": 1234567890.123
                    }
                },
                "session_update": {
                    "description": "Session state changes",
                    "example": {
                        "type": "session_update",
                        "session_info": {
                            "session_exists": True,
                            "history_length": 5,
                            "current_position": 3
                        },
                        "timestamp": 1234567890.123
                    }
                },
                "data_preview": {
                    "description": "Updated data preview after transformations",
                    "example": {
                        "type": "data_preview",
                        "preview_data": [],
                        "column_info": [],
                        "row_count": 1000,
                        "timestamp": 1234567890.123
                    }
                },
                "error": {
                    "description": "Error notifications",
                    "example": {
                        "type": "error",
                        "error_type": "transformation_failed",
                        "message": "Failed to apply scaling transformation",
                        "details": "Column 'age' contains non-numeric values",
                        "timestamp": 1234567890.123
                    }
                },
                "notification": {
                    "description": "System notifications",
                    "example": {
                        "type": "notification",
                        "level": "info",
                        "title": "Export Complete",
                        "message": "Your dataset has been exported successfully",
                        "timestamp": 1234567890.123
                    }
                }
            },
            "error_codes": {
                "400": "Bad Request - Invalid parameters or missing required fields",
                "401": "Unauthorized - Authentication required",
                "403": "Forbidden - Insufficient permissions",
                "404": "Not Found - Resource does not exist",
                "429": "Too Many Requests - Rate limit exceeded",
                "500": "Internal Server Error - Server encountered an error"
            },
            "response_format": {
                "success_response": {
                    "success": True,
                    "data": "Response data (optional)",
                    "message": "Success message (optional)"
                },
                "error_response": {
                    "success": False,
                    "error": "Error message",
                    "details": "Detailed error information (optional)"
                }
            }
        }


@csrf_exempt
@require_http_methods(["GET"])
@rate_limit(limit=60, window_seconds=3600)
def api_stats_endpoint(request):
    """
    Get API performance statistics
    """
    try:
        stats = get_api_stats()
        return JsonResponse({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_health_check(request):
    """
    API health check endpoint
    """
    try:
        import time
        from django.db import connection
        from django.core.cache import cache
        
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }
        
        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_data['checks']['database'] = 'healthy'
        except Exception as e:
            health_data['checks']['database'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # Cache check
        try:
            cache_key = 'health_check_test'
            cache.set(cache_key, 'test', 10)
            if cache.get(cache_key) == 'test':
                health_data['checks']['cache'] = 'healthy'
            else:
                health_data['checks']['cache'] = 'unhealthy: cache not working'
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['checks']['cache'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # WebSocket check (simplified)
        try:
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer:
                health_data['checks']['websocket'] = 'healthy'
            else:
                health_data['checks']['websocket'] = 'unhealthy: no channel layer'
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['checks']['websocket'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        return JsonResponse(health_data, status=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def openapi_spec(request):
    """
    Generate OpenAPI 3.0 specification
    """
    try:
        doc_view = APIDocumentationView()
        specs = doc_view.get_api_specifications()
        
        # Convert to OpenAPI format
        openapi_spec = {
            "openapi": "3.0.0",
            "info": specs["info"],
            "servers": [
                {
                    "url": request.build_absolute_uri('/data-tools/api/'),
                    "description": "Data Studio API Server"
                }
            ],
            "components": {
                "securitySchemes": {
                    "sessionAuth": {
                        "type": "apiKey",
                        "in": "cookie",
                        "name": "sessionid"
                    }
                },
                "schemas": {
                    "SuccessResponse": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": True},
                            "data": {"type": "object"},
                            "message": {"type": "string"}
                        }
                    },
                    "ErrorResponse": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "error": {"type": "string"},
                            "details": {"type": "string"}
                        }
                    }
                }
            },
            "security": [{"sessionAuth": []}],
            "paths": {}
        }
        
        # This would be expanded to include all endpoints
        # For brevity, including a sample
        openapi_spec["paths"]["/studio/{datasource_id}/session/status/"] = {
            "get": {
                "summary": "Get session status",
                "parameters": [
                    {
                        "name": "datasource_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Session status retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                            }
                        }
                    }
                }
            }
        }
        
        return JsonResponse(openapi_spec)
        
    except Exception as e:
        logger.error(f"Error generating OpenAPI spec: {e}")
        return JsonResponse({
            'error': 'Failed to generate API specification'
        }, status=500)