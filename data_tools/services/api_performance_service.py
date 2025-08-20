"""
API Performance Service for Data Studio Backend
Provides rate limiting, caching, and performance optimizations
"""

import time
import logging
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Advanced rate limiting for API endpoints with multiple strategies
    """
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.RLock()
        
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limits using sliding window
        
        Returns:
            (is_allowed, rate_info)
        """
        with self.lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Clean old requests
            self.requests[key] = [req_time for req_time in self.requests[key] 
                                if req_time > window_start]
            
            current_count = len(self.requests[key])
            
            if current_count < limit:
                self.requests[key].append(now)
                return True, {
                    'limit': limit,
                    'remaining': limit - current_count - 1,
                    'reset_time': window_start + window_seconds,
                    'window_seconds': window_seconds
                }
            else:
                # Calculate retry after
                oldest_request = min(self.requests[key]) if self.requests[key] else now
                retry_after = int((oldest_request + window_seconds) - now) + 1
                
                return False, {
                    'limit': limit,
                    'remaining': 0,
                    'reset_time': oldest_request + window_seconds,
                    'retry_after': retry_after,
                    'window_seconds': window_seconds
                }


class APICache:
    """
    Intelligent caching system for API responses with TTL and invalidation
    """
    
    def __init__(self):
        self.default_ttl = getattr(settings, 'API_CACHE_TTL', 300)  # 5 minutes
        
    def get_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Generate consistent cache key"""
        # Create deterministic hash of parameters
        params_str = str(sorted(params.items()))
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        return f"api_cache:{prefix}:{params_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            cached_data = cache.get(key)
            if cached_data:
                logger.debug(f"Cache hit for key: {key}")
                return cached_data
            logger.debug(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL"""
        try:
            cache_ttl = ttl or self.default_ttl
            # Store with metadata
            cached_data = {
                'data': value,
                'cached_at': time.time(),
                'ttl': cache_ttl
            }
            cache.set(key, cached_data, cache_ttl)
            logger.debug(f"Cached data for key: {key}, TTL: {cache_ttl}s")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            cache.delete(key)
            logger.debug(f"Deleted cache for key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all cache keys matching pattern"""
        # Note: This is a simplified version. In production, consider using
        # Redis with SCAN or implement a key tracking mechanism
        deleted_count = 0
        try:
            # This would need to be implemented based on cache backend
            logger.info(f"Cache pattern clear requested: {pattern}")
            # For Django's default cache, we'd need to track keys separately
            return deleted_count
        except Exception as e:
            logger.warning(f"Cache pattern clear error: {e}")
            return 0


class PerformanceMonitor:
    """
    API performance monitoring and metrics collection
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = threading.RLock()
    
    def record_request(self, endpoint: str, duration: float, status_code: int, user_id: str = None):
        """Record API request metrics"""
        with self.lock:
            metric = {
                'endpoint': endpoint,
                'duration': duration,
                'status_code': status_code,
                'timestamp': time.time(),
                'user_id': user_id
            }
            
            # Keep only recent metrics (last hour)
            cutoff_time = time.time() - 3600
            self.metrics[endpoint] = [m for m in self.metrics[endpoint] 
                                    if m['timestamp'] > cutoff_time]
            self.metrics[endpoint].append(metric)
    
    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get performance statistics for endpoint"""
        with self.lock:
            metrics = self.metrics.get(endpoint, [])
            
            if not metrics:
                return {
                    'endpoint': endpoint,
                    'request_count': 0,
                    'avg_duration': 0,
                    'min_duration': 0,
                    'max_duration': 0,
                    'success_rate': 0
                }
            
            durations = [m['duration'] for m in metrics]
            success_count = sum(1 for m in metrics if 200 <= m['status_code'] < 300)
            
            return {
                'endpoint': endpoint,
                'request_count': len(metrics),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'success_rate': (success_count / len(metrics)) * 100,
                'last_hour_requests': len(metrics)
            }


# Global instances
rate_limiter = RateLimiter()
api_cache = APICache()
performance_monitor = PerformanceMonitor()


def rate_limit(limit: int = 100, window_seconds: int = 3600, per_user: bool = True):
    """
    Decorator for rate limiting API endpoints
    
    Args:
        limit: Maximum requests allowed
        window_seconds: Time window in seconds
        per_user: Whether to apply limit per user or globally
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Generate rate limit key
            if per_user and request.user.is_authenticated:
                rate_key = f"rate_limit:{func.__name__}:{request.user.id}"
            else:
                rate_key = f"rate_limit:{func.__name__}:{request.META.get('REMOTE_ADDR', 'unknown')}"
            
            # Check rate limit
            allowed, rate_info = rate_limiter.is_allowed(rate_key, limit, window_seconds)
            
            if not allowed:
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'rate_limit_info': rate_info
                }, status=429)
                
                # Add rate limit headers
                response['X-RateLimit-Limit'] = str(rate_info['limit'])
                response['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response['X-RateLimit-Reset'] = str(int(rate_info['reset_time']))
                if 'retry_after' in rate_info:
                    response['Retry-After'] = str(rate_info['retry_after'])
                
                return response
            
            # Add rate limit headers to successful response
            response = func(request, *args, **kwargs)
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = str(rate_info['limit'])
                response['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response['X-RateLimit-Reset'] = str(int(rate_info['reset_time']))
            
            return response
        return wrapper
    return decorator


def cache_response(ttl: int = 300, cache_key_params: list = None, vary_by_user: bool = True):
    """
    Decorator for caching API responses
    
    Args:
        ttl: Time to live in seconds
        cache_key_params: List of parameter names to include in cache key
        vary_by_user: Whether to include user ID in cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Build cache key parameters
            cache_params = {
                'func': func.__name__,
                'method': request.method,
            }
            
            if vary_by_user and request.user.is_authenticated:
                cache_params['user_id'] = str(request.user.id)
            
            # Add specified parameters
            if cache_key_params:
                for param in cache_key_params:
                    if param in kwargs:
                        cache_params[param] = str(kwargs[param])
                    elif hasattr(request, param):
                        cache_params[param] = str(getattr(request, param))
            
            # Add query parameters for GET requests
            if request.method == 'GET':
                cache_params.update(request.GET.dict())
            
            cache_key = api_cache.get_cache_key(f"response:{func.__name__}", cache_params)
            
            # Try to get cached response
            cached_response = api_cache.get(cache_key)
            if cached_response:
                # Return cached JsonResponse
                response = JsonResponse(cached_response['data'])
                response['X-Cache'] = 'HIT'
                response['X-Cache-TTL'] = str(cached_response.get('ttl', ttl))
                return response
            
            # Execute function and cache result
            start_time = time.time()
            response = func(request, *args, **kwargs)
            duration = time.time() - start_time
            
            # Cache successful JSON responses
            if (hasattr(response, 'status_code') and 
                200 <= response.status_code < 300 and 
                hasattr(response, 'content')):
                
                try:
                    # For JsonResponse, extract data
                    import json
                    response_data = json.loads(response.content.decode())
                    api_cache.set(cache_key, response_data, ttl)
                    
                    if hasattr(response, '__setitem__'):
                        response['X-Cache'] = 'MISS'
                        response['X-Cache-TTL'] = str(ttl)
                except Exception as e:
                    logger.warning(f"Failed to cache response: {e}")
            
            # Record performance metrics
            endpoint = f"{request.method} {func.__name__}"
            user_id = str(request.user.id) if request.user.is_authenticated else None
            performance_monitor.record_request(
                endpoint, duration, response.status_code, user_id
            )
            
            return response
        return wrapper
    return decorator


def monitor_performance(func: Callable) -> Callable:
    """
    Decorator to monitor API endpoint performance
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        
        try:
            response = func(request, *args, **kwargs)
            duration = time.time() - start_time
            
            # Record metrics
            endpoint = f"{request.method} {func.__name__}"
            user_id = str(request.user.id) if request.user.is_authenticated else None
            performance_monitor.record_request(
                endpoint, duration, response.status_code, user_id
            )
            
            # Add performance headers
            if hasattr(response, '__setitem__'):
                response['X-Response-Time'] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            endpoint = f"{request.method} {func.__name__}"
            user_id = str(request.user.id) if request.user.is_authenticated else None
            performance_monitor.record_request(endpoint, duration, 500, user_id)
            raise
    
    return wrapper


class BulkOperationManager:
    """
    Manager for bulk operations with progress tracking and optimization
    """
    
    def __init__(self):
        self.operations = {}
        self.lock = threading.RLock()
    
    def start_operation(self, operation_id: str, total_items: int, user_id: str) -> str:
        """Start a new bulk operation"""
        with self.lock:
            operation_data = {
                'id': operation_id,
                'user_id': user_id,
                'total_items': total_items,
                'processed_items': 0,
                'status': 'running',
                'started_at': time.time(),
                'errors': [],
                'results': []
            }
            self.operations[operation_id] = operation_data
            
            # Cache operation status
            cache_key = f"bulk_operation:{operation_id}"
            api_cache.set(cache_key, operation_data, ttl=3600)  # 1 hour TTL
            
            return operation_id
    
    def update_progress(self, operation_id: str, processed: int, error: str = None, result: Any = None):
        """Update bulk operation progress"""
        with self.lock:
            if operation_id in self.operations:
                op = self.operations[operation_id]
                op['processed_items'] = processed
                
                if error:
                    op['errors'].append({
                        'item': processed,
                        'error': str(error),
                        'timestamp': time.time()
                    })
                
                if result:
                    op['results'].append(result)
                
                # Update cache
                cache_key = f"bulk_operation:{operation_id}"
                api_cache.set(cache_key, op, ttl=3600)
    
    def complete_operation(self, operation_id: str, success: bool = True):
        """Mark bulk operation as complete"""
        with self.lock:
            if operation_id in self.operations:
                op = self.operations[operation_id]
                op['status'] = 'completed' if success else 'failed'
                op['completed_at'] = time.time()
                op['duration'] = op['completed_at'] - op['started_at']
                
                # Update cache with longer TTL for completed operations
                cache_key = f"bulk_operation:{operation_id}"
                api_cache.set(cache_key, op, ttl=24*3600)  # 24 hours TTL
    
    def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get bulk operation status"""
        # Try cache first
        cache_key = f"bulk_operation:{operation_id}"
        cached_op = api_cache.get(cache_key)
        if cached_op:
            return cached_op['data']
        
        # Fall back to in-memory storage
        with self.lock:
            return self.operations.get(operation_id)


# Global bulk operation manager
bulk_operation_manager = BulkOperationManager()


def get_api_stats() -> Dict[str, Any]:
    """
    Get comprehensive API performance statistics
    """
    stats = {
        'performance': {},
        'cache': {
            'hit_rate': 'N/A',  # Would need to implement hit tracking
            'memory_usage': 'N/A'
        },
        'rate_limiting': {
            'active_limits': len(rate_limiter.requests),
            'total_requests': sum(len(requests) for requests in rate_limiter.requests.values())
        },
        'timestamp': time.time()
    }
    
    # Get performance stats for all monitored endpoints
    for endpoint in list(performance_monitor.metrics.keys()):
        stats['performance'][endpoint] = performance_monitor.get_endpoint_stats(endpoint)
    
    return stats