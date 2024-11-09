import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging
from elasticsearch import Elasticsearch
from datetime import datetime

class LogManager:
    def __init__(self, app):
        self.app = app
        self.es = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        
        # Configure Sentry
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=app.config['ENVIRONMENT']
        )

    def log_error(self, error, context=None):
        error_doc = {
            'timestamp': datetime.utcnow(),
            'error': str(error),
            'type': type(error).__name__,
            'context': context or {},
            'environment': self.app.config['ENVIRONMENT']
        }
        
        # Log to Elasticsearch
        self.es.index(index='app-errors', document=error_doc)
        
        # Log to application logger
        logging.error(f"Error: {error}", extra=context)
