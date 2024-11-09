import sentry_sdk
from elasticsearch import Elasticsearch
from prometheus_client import Counter, Histogram
import logging.config
import os

# Sentry configuration for error tracking
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=0.1,
    environment=os.getenv('FLASK_ENV', 'production')
)

# Elasticsearch configuration for logging
es_client = Elasticsearch([os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')])

# Prometheus metrics
REQUEST_LATENCY = Histogram(
    'request_duration_seconds',
    'Request latency in seconds',
    ['endpoint']
)

REQUEST_COUNT = Counter(
    'request_count_total',
    'Total request count',
    ['endpoint', 'method', 'status']
)

ERROR_COUNT = Counter(
    'error_count_total',
    'Total error count',
    ['type']
)

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(timestamp)s %(level)s %(name)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'elasticsearch': {
            'class': 'monitoring.handlers.ElasticsearchHandler',
            'formatter': 'json',
            'level': 'INFO',
            'es_client': es_client,
            'index': 'app-logs'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'elasticsearch'],
            'level': 'INFO'
        }
    }
} 