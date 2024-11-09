from database import db
from datetime import datetime

class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    dispensary = db.Column(db.String(100))
    location = db.Column(db.String(100))
    original_price = db.Column(db.Float)
    discounted_price = db.Column(db.Float)
    savings = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'dispensary': self.dispensary,
            'location': self.location,
            'original_price': self.original_price,
            'discounted_price': self.discounted_price,
            'savings': self.savings,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }
