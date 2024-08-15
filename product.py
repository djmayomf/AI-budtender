from flask import Flask, request, jsonify
from models import db, Product, Wishlist, Cart  # Assuming Wishlist and Cart models exist
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Update with your database URI
db.init_app(app)

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'weight': product.weight,
                'availability': product.availability,
                'deals': product.deals,
                'promos': product.promos
            })
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/product/<int:product_id>/add_to_wishlist', methods=['POST'])
def add_to_wishlist(product_id):
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        # Logic to add product to wishlist for the user
        wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product added to wishlist'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/product/<int:product_id>/add_to_cart', methods=['POST'])
def add_to_cart(product_id):
    data = request.json
    quantity = data.get('quantity', 1)

    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than zero'}), 400

    try:
        # Logic to add product to cart
        cart_item = Cart(product_id=product_id, quantity=quantity)  # Assuming Cart model exists
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product added to cart'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)