from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from database import db, init_db
from routes.deals import deals_bp
from routes.auth import auth_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///budgetbud.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(deals_bp)
    app.register_blueprint(auth_bp)
    
    # Create database tables
    with app.app_context():
        init_db()
    
    return app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)