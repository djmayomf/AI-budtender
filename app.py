from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)

# Set up your Stripe secret key
stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'

@app.route('/')
def index():
    return 'Welcome to the Budtender App'

@app.route('/create_payment_intent', methods=['POST'])
def create_payment_intent():
    try:
        # Create a PaymentIntent with the amount and currency
        intent = stripe.PaymentIntent.create(
            amount=1000,  # amount in cents
            currency='usd',
            payment_method_types=['card'],
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    try:
        # Confirm the payment
        intent = stripe.PaymentIntent.confirm(
            data['paymentIntentId'],
            payment_method=data['paymentMethodId'],
        )
        return jsonify({'success': True})
    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
from flask_sqlalchemy import SQLAlchemy
from models import db, UserProfile

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    try:
        user = UserProfile(
            email=data['email'],
            phone_number=data['phone_number'],
            date_of_birth=data['date_of_birth'],
            payment_method=data.get('payment_method')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/apply_promo_code', methods=['POST'])
def apply_promo_code():
    data = request.json
    total_amount = data['total_amount']
    code = data['promo_code']
    discounted_amount = apply_promo_code(code, total_amount)
    return jsonify({'discounted_amount': discounted_amount})
from flask import Flask, request, jsonify
import stripe
import smtplib
from email.mime.text import MIMEText
from models import db, UserProfile
from promos import apply_promo_code
from cart import cart, add_to_cart, checkout
from location import get_location_info, get_distance
from currency import convert_currency

app = Flask(__name__)

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

# Set up Stripe secret key
stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'

@app.route('/create_payment_intent', methods=['POST'])
def create_payment_intent():
    try:
        intent = stripe.PaymentIntent.create(
            amount=1000,  # amount in cents
            currency='usd',
            payment_method_types=['card'],
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    try:
        intent = stripe.PaymentIntent.confirm(
            data['paymentIntentId'],
            payment_method=data['paymentMethodId'],
        )
        return jsonify({'success': True})
    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    try:
        user = User(
            email=data['email'],
            phone=data['phone'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            payment_method=data.get('payment_method')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_payment_info', methods=['POST'])
def update_payment_info():
    data = request.json
    user = UserProfile.query.filter_by(email=data['email']).first()
    if user:
        user.payment_method = data['payment_method']
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/request_verification_code', methods=['POST'])
def request_verification_code():
    data = request.json
    code = generate_verification_code()
    success = send_verification_code(data['email'], code)
    if success:
        return jsonify({'success': True, 'code': code})
    else:
        return jsonify({'error': 'Failed to send verification code'}), 500

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.json
    input_code = data['input_code']
    actual_code = data['actual_code']
    if input_code == actual_code:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Invalid code'}), 400

@app.route('/apply_promo_code', methods=['POST'])
def apply_promo_code_route():
    data = request.json
    total_amount = data['total_amount']
    code = data['promo_code']
    discounted_amount = apply_promo_code(code, total_amount)
    return jsonify({'discounted_amount': discounted_amount})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    item = request.json
    cart.append(item)
    return jsonify({'success': True, 'cart': cart})

@app.route('/checkout', methods=['POST'])
def checkout_route():
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    # Apply taxes and handle payment here
    return jsonify({'total_amount': total_amount})

@app.route('/get_location_info', methods=['POST'])
def get_location_info_route():
    data = request.json
    address = data['address']
    location_info = get_location_info(address)
    return jsonify(location_info)

@app.route('/get_distance', methods=['POST'])
def get_distance_route():
    data = request.json
    coord1 = (data['latitude1'], data['longitude1'])
    coord2 = (data['latitude2'], data['longitude2'])
    distance = get_distance(coord1, coord2)
    return jsonify({'distance': distance})

@app.route('/convert_currency', methods=['POST'])
def convert_currency_route():
    data = request.json
    amount = data['amount']
    from_currency = data['from_currency']
    to_currency = data['to_currency']
    converted_amount = convert_currency(amount, from_currency, to_currency)
    return jsonify({'converted_amount': converted_amount})

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, jsonify
from web_scrapers import scrape_leafly_strains, scrape_weedmaps_deals

app = Flask(__name__)

@app.route('/scrape/leafly/strains', methods=['GET'])
def scrape_leafly_strains_route():
    strains = scrape_leafly_strains()
    return jsonify(strains)

@app.route('/scrape/weedmaps/deals', methods=['GET'])
def scrape_weedmaps_deals_route():
    deals = scrape_weedmaps_deals()
    return jsonify(deals)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# Load the model
with open('recommendation_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Dummy database for user preferences
user_preferences = pd.DataFrame(columns=['user_id', 'product_id', 'rating'])

@app.route('/feedback', methods=['POST'])
def receive_feedback():
    global user_preferences
    data = request.json
    user_id = data['user_id']
    product_id = data['product_id']
    rating = data['rating']
    
    # Save feedback
    feedback = pd.DataFrame([[user_id, product_id, rating]], columns=['user_id', 'product_id', 'rating'])
    user_preferences = pd.concat([user_preferences, feedback], ignore_index=True)
    
    # Retrain the model in a separate thread or batch process
    # train_model()

    return jsonify({'status': 'Feedback received'})

def train_model():
    global user_preferences
    user_product_ratings = user_preferences.pivot(index='user_id', columns='product_id', values='rating').fillna(0)
    model = NearestNeighbors(n_neighbors=5, algorithm='auto')
    model.fit(user_product_ratings)
    
    with open('recommendation_model.pkl', 'wb') as f:
        pickle.dump(model, f)

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id', type=int)
    user_product_ratings = user_preferences.pivot(index='user_id', columns='product_id', values='rating').fillna(0)
    
    if user_id not in user_product_ratings.index:
        return jsonify({'error': 'User not found'}), 404
    
    user_ratings = user_product_ratings.loc[user_id].values.reshape(1, -1)
    distances, indices = model.kneighbors(user_ratings)
    
    recommended_products = set()
    for index in indices[0]:
        similar_user_ratings = user_product_ratings.iloc[index]
        recommended_products.update(similar_user_ratings[similar_user_ratings > 0].index)
    
    return jsonify(list(recommended_products))

if __name__ == '__main__':
    app.run(debug=True)