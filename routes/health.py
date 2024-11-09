from flask import Blueprint, jsonify
from database import db
from cache import cache
import psutil
import os

health = Blueprint('health', __name__)

@health.route('/health')
def health_check():
    """System health check endpoint"""
    try:
        # Check database
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'
    
    # Check cache
    try:
        cache.set('health_check', 'ok')
        cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'unhealthy'
    except Exception:
        cache_status = 'unhealthy'
    
    # System metrics
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' and cache_status == 'healthy' else 'unhealthy',
        'services': {
            'database': db_status,
            'cache': cache_status
        },
        'metrics': {
            'cpu_usage': cpu_usage,
            'memory_used': memory.percent,
            'disk_used': disk.percent
        }
    }) 