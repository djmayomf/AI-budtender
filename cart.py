from flask import Flask, request, jsonify

app = Flask(__name__)

cart = []

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.json
    if 'price' not in item or 'quantity' not in item:
        return jsonify({'error': 'Invalid item format. Must include price and quantity.'}), 400
    try:
        item['price'] = float(item['price'])
        item['quantity'] = int(item['quantity'])
    except ValueError:
        return jsonify({'error': 'Invalid data type for price or quantity.'}), 400
    cart.append(item)
    return jsonify({'success': True, 'cart': cart})

@app.route('/checkout', methods=['POST'])
def checkout():
    if not cart:
        return jsonify({'error': 'Cart is empty.'}), 400
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    # Apply taxes and handle payment here
    cart.clear()  # Optionally clear the cart after checkout
    return jsonify({'total_amount': total_amount})

if __name__ == '__main__':
    app.run(debug=True)