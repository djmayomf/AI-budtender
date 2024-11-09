from flask_security import Security, auth_required, hash_password
from argon2 import PasswordHasher
import pyotp
import qrcode
import jwt

class AuthSecurity:
    def __init__(self, app):
        self.app = app
        self.ph = PasswordHasher()
        self.security = Security(app, user_datastore)
        self.setup_auth_rules()

    def setup_auth_rules(self):
        @self.app.before_request
        def enforce_security():
            if not request.is_secure:
                abort(400, "HTTPS Required")

    def generate_secure_token(self, user_data):
        return jwt.encode(
            user_data,
            self.app.config['SECRET_KEY'],
            algorithm='HS512'
        )

    def verify_password(self, stored_hash, provided_password):
        try:
            return self.ph.verify(stored_hash, provided_password)
        except:
            return False

    def setup_2fa(self, user):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        qr = qrcode.make(totp.provisioning_uri(
            user.email, 
            issuer_name="YourSecureApp"
        ))
        return secret, qr
