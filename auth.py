from google.oauth2 import id_token
from google.auth.transport import requests
from flask import current_app, session
from functools import wraps
import jwt
from datetime import datetime, timedelta

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

class GoogleAuth:
    def __init__(self, client_id):
        self.client_id = client_id
        self.flow = None

    def verify_token(self, token):
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            return idinfo
        except ValueError:
            raise AuthError({"code": "invalid_token",
                           "description": "Invalid token"}, 401)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            raise AuthError({"code": "unauthorized",
                           "description": "Authentication required"}, 401)
        return f(*args, **kwargs)
    return decorated 