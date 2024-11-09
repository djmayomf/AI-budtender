from flask import jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AuthError as e:
            return jsonify(e.error), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    return wrapper
