from flask import request, abort, current_app
import re
from functools import wraps
from typing import List, Dict, Any
import jwt
from datetime import datetime, timedelta
import rate_limit
from security.waf import WAF

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.waf = WAF()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.setup_security_headers()
        self.setup_request_validation()
        
    def setup_security_headers(self):
        @self.app.after_request
        def add_security_headers(response):
            # HTTPS redirect
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            # XSS Protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            # Content Security Policy
            response.headers['Content-Security-Policy'] = self._get_csp_policy()
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            # Frame Options
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            # Feature Policy
            response.headers['Permissions-Policy'] = self._get_permissions_policy()
            return response

    def _get_csp_policy(self) -> str:
        """Generate Content Security Policy"""
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://maps.googleapis.com",
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
            "img-src 'self' data: https: blob:",
            "font-src 'self' https://cdnjs.cloudflare.com",
            "connect-src 'self' https://api.leafly.com https://api.weedmaps.com",
            "frame-src 'self' https://www.google.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'self'",
            "upgrade-insecure-requests"
        ])

    def _get_permissions_policy(self) -> str:
        """Generate Permissions Policy"""
        return ", ".join([
            "geolocation=(self)",
            "camera=()",
            "microphone=()",
            "payment=(self)",
            "usb=()",
            "fullscreen=(self)"
        ])

    def setup_request_validation(self):
        @self.app.before_request
        def validate_request():
            # Check WAF rules
            if not self.waf.check_request(request):
                abort(403)

            # Validate Content-Type
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not request.is_json:
                    abort(400, 'Content-Type must be application/json')

            # Validate request size
            max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
            if request.content_length and request.content_length > max_size:
                abort(413)

            # Validate origin for CORS
            origin = request.headers.get('Origin')
            if origin and origin not in current_app.config['ALLOWED_ORIGINS']:
                abort(403)

    def require_auth(self, f):
        """Authentication decorator"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                abort(401)

            try:
                # Verify JWT token
                payload = jwt.decode(
                    token.split(' ')[1],
                    current_app.config['JWT_SECRET_KEY'],
                    algorithms=['HS256']
                )
                request.user = payload
            except jwt.InvalidTokenError:
                abort(401)

            return f(*args, **kwargs)
        return decorated

    def require_role(self, role: str):
        """Role-based access control decorator"""
        def decorator(f):
            @wraps(f)
            @self.require_auth
            def decorated(*args, **kwargs):
                if request.user.get('role') != role:
                    abort(403)
                return f(*args, **kwargs)
            return decorated
        return decorator

    def sanitize_input(self, data: Any) -> Any:
        """Sanitize user input"""
        if isinstance(data, str):
            # Remove potential XSS
            data = re.sub(r'<[^>]*?>', '', data)
            # Remove potential SQL injection
            data = re.sub(r'[\'";\-\-]', '', data)
            return data
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        return data

    def rate_limit(self, limit: str):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                key = f"{request.remote_addr}:{request.endpoint}"
                if not rate_limit.check(key, limit):
                    abort(429)
                return f(*args, **kwargs)
            return decorated
        return decorator 