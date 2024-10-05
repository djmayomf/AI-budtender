from flask import Flask, request, jsonify
from models import db, Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
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
        # Implement wishlist logic here
        # Example: Add product to user's wishlist in the database
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/product/<int:product_id>/add_to_cart', methods=['POST'])
def add_to_cart(product_id):
    data = request.json
    quantity = data.get('quantity', 1)
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({'error': 'Invalid quantity'}), 400

    try:
        # Implement cart logic here
        # Example: Add product to user's cart in the database
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)