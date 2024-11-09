from flask import request, g
import time
from functools import wraps
from monitoring.config import REQUEST_LATENCY, REQUEST_COUNT
from cache import cache

def performance_middleware():
    """Middleware to track request performance"""
    
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Start timing
            start_time = time.time()
            
            # Execute request
            try:
                response = f(*args, **kwargs)
                status = response.status_code
            except Exception as e:
                status = 500
                raise e
            finally:
                # Record metrics
                duration = time.time() - start_time
                endpoint = request.endpoint or 'unknown'
                
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
                REQUEST_COUNT.labels(
                    endpoint=endpoint,
                    method=request.method,
                    status=status
                ).inc()
                
            return response
        return wrapped
    return decorator

def cache_response(timeout=300):
    """Cache response based on request path and query parameters"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            cache_key = f"{request.path}:{str(request.args)}"
            response = cache.get(cache_key)
            
            if response is None:
                response = f(*args, **kwargs)
                cache.set(cache_key, response, timeout=timeout)
                
            return response
        return wrapped
    return decorator 