from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)
    payment_method = db.Column(db.String(255))  # Store payment method info

    def __repr__(self):
        return f'<UserProfile {self.email}>'
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)
    deals = db.Column(db.String(255), nullable=True)
    promos = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Product {self.name}>'
