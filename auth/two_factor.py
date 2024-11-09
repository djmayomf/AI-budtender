from pyotp import TOTP
from qrcode import make as make_qr

class TwoFactorAuth:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or self.generate_secret()
        self.totp = TOTP(self.secret_key)

    def generate_secret(self):
        return TOTP.random_base32()

    def get_qr_code(self, email):
        provisioning_uri = self.totp.provisioning_uri(
            email, 
            issuer_name="YourApp"
        )
        qr = make_qr(provisioning_uri)
        return qr

    def verify_code(self, code):
        return self.totp.verify(code)
