from flask_security import Security, SQLAlchemyUserDatastore
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
import ssl
from datetime import timedelta
import os

class SecurityConfig:
    # Security Settings
    SECURITY_PASSWORD_SALT = 'your-security-salt'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_TRACKABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TWO_FACTOR = True
    SECURITY_TWO_FACTOR_REQUIRED = True
    
    # Session Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # CORS Settings
    CORS_ORIGINS = ['https://yourdomain.com']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_EXPOSE_HEADERS = ['Content-Range', 'X-Total-Count']
    
    # OAuth2 Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    OAUTH2_PROVIDERS = {
        'google': {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'token_url': 'https://accounts.google.com/o/oauth2/token',
            'userinfo_url': 'https://www.googleapis.com/oauth2/v1/userinfo'
        }
    }
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'"
    }
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
