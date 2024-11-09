import ssl
from OpenSSL import SSL

class SSLConfig:
    def __init__(self, app):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.configure_ssl(app)

    def configure_ssl(self, app):
        self.context.load_cert_chain(
            certfile='path/to/cert.pem',
            keyfile='path/to/key.pem'
        )
        
        # Configure SSL options
        self.context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        self.context.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
        
        # Set cipher suite
        self.context.set_ciphers(
            'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384'
        )
