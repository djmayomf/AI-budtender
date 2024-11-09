from functools import wraps
from flask import request, jsonify
import logging
from time import time

logger = logging.getLogger(__name__)

def error_handler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    return decorated_function

def timer_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time()
        response = f(*args, **kwargs)
        duration = time() - start_time
        
        logger.info(f"{request.path} took {duration:.2f} seconds")
        return response
    return decorated_function 