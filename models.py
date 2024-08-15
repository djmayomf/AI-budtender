from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'  # Explicitly define the table name

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)  # Use Date type for better validation
    payment_method = db.Column(db.String(255), nullable=True)  # Nullable for flexibility

    def __repr__(self):
        return f'<UserProfile id={self.id}, email={self.email}, phone={self.phone_number}>'

class Product(db.Model):
    __tablename__ = 'products'  # Explicitly define the table name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)
    deals = db.Column(db.String(255), nullable=True)
    promos = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Product id={self.id}, name={self.name}, price={self.price}>'

# Example usage
if __name__ == '__main__':
    # This block is for demonstration purposes and should be part of your Flask app context
    db.create_all()  # Create tables based on the models