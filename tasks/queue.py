from celery import Celery
from redis import Redis
import json
from datetime import datetime

class TaskQueue:
    def __init__(self, app):
        self.celery = Celery(
            app.name,
            broker=app.config['CELERY_BROKER_URL']
        )
        self.redis = Redis.from_url(app.config['REDIS_URL'])

    def enqueue_task(self, task_name, data, priority=0):
        task_id = self.celery.send_task(
            task_name,
            args=[data],
            countdown=priority
        )
        
        # Store task metadata
        self.redis.setex(
            f'task:{task_id}',
            3600,
            json.dumps({
                'status': 'pending',
                'data': data,
                'created_at': datetime.utcnow().isoformat()
            })
        )
        
        return task_id

    def get_task_status(self, task_id):
        return self.redis.get(f'task:{task_id}')
