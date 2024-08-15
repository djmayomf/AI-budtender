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
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    price = data.get('price')

    if not product_id or quantity is None or price is None:
        return jsonify({'error': 'Missing product_id, quantity, or price'}), 400

    # Check if the item already exists in the cart
    existing_item = CartItem.query.filter_by(product_id=product_id).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(product_id=product_id, quantity=quantity, price=price)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({'success': True, 'cart': get_cart_items()})


@app.route('/checkout', methods=['POST'])
def checkout():
    total_amount = sum(item.price * item.quantity for item in CartItem.query.all())
    # Here you can apply taxes and handle payment
    # For example, total_amount *= 1.1  # Apply 10% tax
    clear_cart()  # Clear the cart after checkout
    return jsonify({'total_amount': total_amount})

@app.route('/cart', methods=['GET'])
def get_cart_items():
    items = CartItem.query.all()
    cart_items = [{'product_id': item.product_id, 'quantity': item.quantity, 'price': item.price} for item in items]
    return jsonify(cart_items)

@app.route('/remove_from_cart/<product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    item = CartItem.query.filter_by(product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed from cart'})
    else:
        return jsonify({'error': 'Item not found in cart'}), 404

def clear_cart():
    db.session.query(CartItem).delete()
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)