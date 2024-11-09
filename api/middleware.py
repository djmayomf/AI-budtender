from functools import wraps
from cachetools import TTLCache
import time

class APIMiddleware:
    def __init__(self):
        self.rate_limit_cache = TTLCache(maxsize=10000, ttl=60)
        self.response_cache = TTLCache(maxsize=1000, ttl=300)

    def rate_limit(self, limit=60, window=60):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                key = f"{request.remote_addr}:{f.__name__}"
                current = time.time()
                
                # Check rate limit
                requests = self.rate_limit_cache.get(key, [])
                requests = [req for req in requests if req > current - window]
                
                if len(requests) >= limit:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                requests.append(current)
                self.rate_limit_cache[key] = requests
                
                return f(*args, **kwargs)
            return wrapped
        return decorator

    def cache_response(self, ttl=300):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                cache_key = f"{request.path}:{request.query_string}"
                
                # Check cache
                cached = self.response_cache.get(cache_key)
                if cached:
                    return cached
                
                # Get fresh response
                response = f(*args, **kwargs)
                self.response_cache[cache_key] = response
                
                return response
            return wrapped
        return decorator
