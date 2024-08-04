from flask import Flask, request, jsonify
from models import db, Product

app = Flask(__name__)

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
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

@app.route('/product/<int:product_id>/add_to_wishlist', methods=['POST'])
def add_to_wishlist(product_id):
    # Logic to add product to wishlist for a user
    # Example: user_id should be passed in the request
    data = request.json
    user_id = data.get('user_id')
    # Implement wishlist logic here
    return jsonify({'success': True})

@app.route('/product/<int:product_id>/add_to_cart', methods=['POST'])
def add_to_cart(product_id):
    data = request.json
    quantity = data.get('quantity', 1)
    # Logic to add product to cart
    # Example: cart should be maintained globally or per session
    return jsonify({'success': True})
