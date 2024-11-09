from datetime import datetime, timedelta
from redis import Redis
import jwt

class SessionManager:
    def __init__(self, app):
        self.redis = Redis.from_url(app.config['REDIS_URL'])
        self.app = app

    def create_session(self, user_id, device_info):
        session_id = self._generate_session_id()
        session_data = {
            'user_id': user_id,
            'device': device_info,
            'created_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat()
        }
        
        # Store in Redis with expiration
        self.redis.setex(
            f'session:{session_id}',
            timedelta(days=7),
            jwt.encode(session_data, self.app.config['SECRET_KEY'])
        )
        
        return session_id

    def validate_session(self, session_id):
        session_data = self.redis.get(f'session:{session_id}')
        if not session_data:
            return None
            
        try:
            decoded = jwt.decode(
                session_data, 
                self.app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return decoded
        except jwt.InvalidTokenError:
            return None
