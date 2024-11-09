from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import helmet

def configure_security(app):
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="redis://localhost:6379"
    )

    # Security headers
    Talisman(app,
        force_https=True,
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy={
            'default-src': "'self'",
            'img-src': "'self' data: https:",
            'script-src': "'self' 'unsafe-inline' https://accounts.google.com",
            'style-src': "'self' 'unsafe-inline'",
            'frame-src': "'self' https://accounts.google.com"
        }
    )

    # Additional security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response 