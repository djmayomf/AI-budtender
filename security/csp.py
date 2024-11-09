from flask_talisman import Talisman

class ContentSecurity:
    def __init__(self, app):
        self.csp = {
            'default-src': "'self'",
            'img-src': ["'self'", 'https:', 'data:'],
            'script-src': [
                "'self'",
                "'unsafe-inline'",
                'https://www.google.com',
                'https://www.gstatic.com'
            ],
            'style-src': ["'self'", "'unsafe-inline'"],
            'frame-src': ["'self'", 'https://www.google.com'],
            'connect-src': ["'self'", 'https://api.yourdomain.com'],
            'form-action': "'self'",
            'frame-ancestors': "'none'",
            'base-uri': "'self'",
            'object-src': "'none'"
        }
        
        Talisman(
            app,
            content_security_policy=self.csp,
            force_https=True,
            strict_transport_security=True,
            session_cookie_secure=True,
            feature_policy={
                'geolocation': "'none'",
                'microphone': "'none'",
                'camera': "'none'"
            }
        )
