from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import stripe
import os
import pandas as pd
import pickle
from sklearn.neighbors import NearestNeighbors
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Set up Stripe secret key from environment variable
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# UserProfile model
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    date_of_birth = db.Column(db.String(10))
    payment_method = db.Column(db.String(100))

# Load the recommendation model
with open('recommendation_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Dummy database for user preferences
user_preferences = pd.DataFrame(columns=['user_id', 'product_id', 'rating'])

@app.route('/')
def index():
    return 'Welcome to the Budtender App'

@app.route('/create_payment_intent', methods=['POST'])
def create_payment_intent():
    data = request.json
    amount = data.get('amount', 1000)  # Default to 1000 cents if not provided
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method_types=['card'],
        )
        return jsonify({'clientSecret': intent.client_secret})
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

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