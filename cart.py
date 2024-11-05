from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cart.db'
db = SQLAlchemy(app)

# Cart model
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.json
    cart.append(item)
    return jsonify({'success': True, 'cart': cart})

@app.route('/checkout', methods=['POST'])
def checkout():
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    # Apply taxes and handle payment here
    return jsonify({'total_amount': total_amount})
