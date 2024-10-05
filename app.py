# app.py
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import stripe
import os
import io
from datetime import datetime
from google.cloud import vision
from google.oauth2 import service_account
import pandas as pd
import pickle
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

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
    id_text = db.Column(db.Text)

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
@app.route('/')
def index():
    return 'Welcome to the Budtender App'

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

@app.route('/apply_promo_code', methods=['POST'])
def apply_promo_code_route():
    data = request.json
    total_amount = data['total_amount']
    code = data['promo_code']
    discounted_amount = apply_promo_code(code, total_amount)
    return jsonify({'discounted_amount': discounted_amount})

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