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
    
    # Retrain the model
    train_model()

    return jsonify({'status': 'Feedback received'})

def train_model():
    global user_preferences
    # Pivot user preferences
    user_product_ratings = user_preferences.pivot(index='user_id', columns='product_id', values='rating').fillna(0)
    
    # Train a KNN model
    model = NearestNeighbors(n_neighbors=5, algorithm='auto')
    model.fit(user_product_ratings)
    
    # Save the model
    with open('recommendation_model.pkl', 'wb') as f:
        pickle.dump(model, f)

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id', type=int)
    
    # Pivot user preferences
    user_product_ratings = user_preferences.pivot(index='user_id', columns='product_id', values='rating').fillna(0)
    
    # Get the user's ratings
    user_ratings = user_product_ratings.loc[user_id].values.reshape(1, -1)
    
    # Predict similar users
    distances, indices = model.kneighbors(user_ratings)
    
    # Aggregate recommendations
    recommended_products = set()
    for index in indices[0]:
        similar_user_ratings = user_product_ratings.iloc[index]
        recommended_products.update(similar_user_ratings[similar_user_ratings > 0].index)
    
    return jsonify(list(recommended_products))

if __name__ == '__main__':
    app.run(debug=True)
import sqlite3

def store_feedback(user_id, product_id, rating):
    conn = sqlite3.connect('preferences.db')
    c = conn.cursor()
    c.execute('INSERT INTO preferences (user_id, product_id, rating) VALUES (?, ?, ?)', 
              (user_id, product_id, rating))
    conn.commit()
    conn.close()
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data['message']
    
    # Simple mood-based responses
    mood_responses = {
        'happy': ['You might enjoy something uplifting and energetic!', 'How about a fun and exciting product?'],
        'relaxed': ['Maybe a calming product is what you need.', 'How about something gentle and soothing?'],
        'sad': ['A comforting product might help you feel better.', 'Consider something with a warm and cozy vibe.'],
        'tired': ['You might like something that helps you relax and recharge.', 'How about a product that helps you unwind?'],
        'stressed': ['Consider a product that can help you relieve stress.', 'How about something to help you relax and calm down?'],
    }
    
    mood = get_mood(user_message)
    response = mood_responses.get(mood, 'I am not sure how you feel. Could you tell me more?')
    
    return jsonify({'response': response})

def get_mood(message):
    # Simple keyword matching to determine mood
    keywords = {
        'happy': ['happy', 'excited', 'joyful'],
        'relaxed': ['relaxed', 'calm', 'chilled'],
        'sad': ['sad', 'depressed', 'down'],
        'tired': ['tired', 'exhausted', 'weary'],
        'stressed': ['stressed', 'anxious', 'overwhelmed']
    }
    
    message = message.lower()
    for mood, words in keywords.items():
        if any(word in message for word in words):
            return mood
    return 'neutral'

if __name__ == '__main__':
    app.run(debug=True)
from flask import send_from_directory

@app.route('/chatbot.html')
def serve_chatbot():
    return send_from_directory('.', 'chatbot.html')
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/scrape_leafly', methods=['POST'])
def scrape_leafly():
    import leafly_scraper  # Ensure leafly_scraper.py is in the same directory
    return jsonify({'status': 'Leafly data scraped and stored successfully.'})

@app.route('/scrape_weedmaps', methods=['POST'])
def scrape_weedmaps():
    import weedmaps_scraper  # Ensure weedmaps_scraper.py is in the same directory
    return jsonify({'status': 'Weedmaps data scraped and stored successfully.'})

@app.route('/leafly_strains', methods=['GET'])
def get_leafly_strains():
    conn = sqlite3.connect('leafly.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM strains')
    strains = cursor.fetchall()
    conn.close()
    return jsonify(strains)

@app.route('/weedmaps_dispensaries', methods=['GET'])
def get_weedmaps_dispensaries():
    conn = sqlite3.connect('weedmaps.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dispensaries')
    dispensaries = cursor.fetchall()
    conn.close()
    return jsonify(dispensaries)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import io
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    id_image = db.Column(db.LargeBinary)
    medical_card_number = db.Column(db.String(50))
    medical_card_expiration = db.Column(db.Date)
    address = db.Column(db.String(255))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

db.create_all()

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
        password_hash=data['password_hash'],
        medical_card_number=data.get('medical_card_number'),
        medical_card_expiration=datetime.strptime(data.get('medical_card_expiration'), '%Y-%m-%d').date() if data.get('medical_card_expiration') else None
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': 'User registered successfully'}), 201

@app.route('/upload_id', methods=['POST'])
def upload_id():
    user_id = request.form['user_id']
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    user = User.query.get(user_id)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
        user.id_image = f.read()
    db.session.commit()
    
    return jsonify({'status': 'ID uploaded successfully'}), 200

@app.route('/get_profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'date_of_birth': user.date_of_birth.isoformat(),
            'address': user.address,
            'medical_card_number': user.medical_card_number,
            'medical_card_expiration': user.medical_card_expiration.isoformat() if user.medical_card_expiration else None
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/get_id_image/<int:user_id>', methods=['GET'])
def get_id_image(user_id):
    user = User.query.get(user_id)
    if user and user.id_image:
        return send_file(
            io.BytesIO(user.id_image),
            mimetype='image/jpeg',
            as_attachment=True,
            attachment_filename='id_image.jpg'
        )
    return jsonify({'error': 'ID image not found'}), 404

@app.route('/update_address/<int:user_id>', methods=['POST'])
def update_address(user_id):
    data = request.json
    user = User.query.get(user_id)
    if user:
        user.address = data['address']
        db.session.commit()
        return jsonify({'status': 'Address updated successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/update_medical_card/<int:user_id>', methods=['POST'])
def update_medical_card(user_id):
    data = request.json
    user = User.query.get(user_id)
    if user:
        user.medical_card_number = data.get('medical_card_number')
        user.medical_card_expiration = datetime.strptime(data.get('medical_card_expiration'), '%Y-%m-%d').date() if data.get('medical_card_expiration') else None
        db.session.commit()
        return jsonify({'status': 'Medical card updated successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/get_reviews/<int:user_id>', methods=['GET'])
def get_reviews(user_id):
    reviews = Review.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'product_name': review.product_name,
        'review_text': review.review_text,
        'rating': review.rating
    } for review in reviews])

@app.route('/get_orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'order_date': order.order_date.isoformat(),
        'total_amount': order.total_amount
    } for order in orders])

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import io
from datetime import datetime
from google.cloud import vision
from google.oauth2 import service_account

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Initialize Google Vision client
credentials = service_account.Credentials.from_service_account_file('path_to_your_service_account_key.json')
client = vision.ImageAnnotatorClient(credentials=credentials)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    id_image = db.Column(db.LargeBinary)
    medical_card_number = db.Column(db.String(50))
    medical_card_expiration = db.Column(db.Date)
    address = db.Column(db.String(255))

db.create_all()

# Routes
@app.route('/upload_id', methods=['POST'])
def upload_id():
    user_id = request.form['user_id']
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Process the uploaded file
    with open(file_path, 'rb') as img_file:
        image = vision.Image(content=img_file.read())
        response = client.text_detection(image=image)
        text_annotations = response.text_annotations
        id_text = text_annotations[0].description if text_annotations else ""
    
    user = User.query.get(user_id)
    with open(file_path, 'rb') as f:
        user.id_image = f.read()
        user.id_text = id_text
    db.session.commit()
    
    return jsonify({'status': 'ID uploaded and processed successfully', 'id_text': id_text}), 200

@app.route('/get_profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'date_of_birth': user.date_of_birth.isoformat(),
            'address': user.address,
            'medical_card_number': user.medical_card_number,
            'medical_card_expiration': user.medical_card_expiration.isoformat() if user.medical_card_expiration else None,
            'id_text': user.id_text  # Include extracted text from ID
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/get_id_image/<int:user_id>', methods=['GET'])
def get_id_image(user_id):
    user = User.query.get(user_id)
    if user and user.id_image:
        return send_file(
            io.BytesIO(user.id_image),
            mimetype='image/jpeg',
            as_attachment=True,
            attachment_filename='id_image.jpg'
        )
    return jsonify({'error': 'ID image not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
