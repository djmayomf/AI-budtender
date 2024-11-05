from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'  # Explicitly define the table name

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)
    payment_method = db.Column(db.String(255))  # Store payment method info

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address, "Provided email is not valid"
        return address

    @validates('phone_number')
    def validate_phone_number(self, key, number):
        assert number.isdigit(), "Phone number should contain only digits"
        return number

    def __repr__(self):
        return f'<UserProfile {self.email}>'
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
        return f'<Product {self.name}>'
