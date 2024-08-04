from flask import Flask, request, jsonify

app = Flask(__name__)

cart = []

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
