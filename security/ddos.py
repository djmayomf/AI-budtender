from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

class DDoSProtection:
    def __init__(self, app):
        self.redis = redis.Redis()
        self.limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
    def configure_rate_limits(self):
        @self.limiter.limit("1 per second")
        def login_limit():
            pass

        @self.limiter.limit("5 per minute")
        def api_limit():
            pass

    def track_suspicious_activity(self, request):
        ip = request.remote_addr
        key = f"suspicious:{ip}"
        
        if self.redis.get(key):
            count = self.redis.incr(key)
            if count > 10:
                self.block_ip(ip)
        else:
            self.redis.setex(key, 3600, 1)
