from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import ValidationError
from validation.schema import DealSchema, UserSchema
from models import Deal, User, db
from security.auth import require_auth, require_role
from cache import cache
from typing import Dict, Any
import logging
from chatbot.bot import BudBot

api = Blueprint('api', __name__)
limiter = Limiter(key_func=get_remote_address)

@api.route('/api/v1/deals', methods=['GET'])
@limiter.limit("100/minute")
@cache.cached(timeout=300)
def get_deals():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        deals = Deal.query.order_by(Deal.created_at.desc()).paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        
        if not deals.items:
            return jsonify({'message': 'No deals found'}), 404
            
        return jsonify({
            'deals': [deal.to_dict() for deal in deals.items],
            'total': deals.total,
            'pages': deals.pages,
            'current_page': deals.page
        })
    except Exception as e:
        logging.error(f"Error fetching deals: {str(e)}")
        return jsonify({'error': 'Failed to fetch deals'}), 500

@api.route('/api/v1/deals/bulk', methods=['POST'])
@require_role('admin')
@limiter.limit("10/minute")
def bulk_create_deals():
    """Bulk create deals"""
    try:
        deals_data = request.json.get('deals', [])
        if not deals_data:
            return jsonify({'error': 'No deals provided'}), 400
            
        schema = DealSchema(many=True)
        deals = schema.load(deals_data)
        
        for deal in deals:
            db.session.add(Deal(**deal))
        db.session.commit()
        
        return jsonify({'message': f'Created {len(deals)} deals'}), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400

@api.route('/api/v1/users/dashboard', methods=['GET'])
@require_auth
@cache.cached(timeout=60, key_prefix='user_dashboard')
def get_user_dashboard():
    """Get user dashboard data"""
    user_id = request.user.id
    favorite_deals = Deal.query.filter_by(user_id=user_id).limit(5).all()
    
    return jsonify({
        'favorite_deals': [deal.to_dict() for deal in favorite_deals],
        'notifications': get_user_notifications(user_id),
        'price_alerts': get_price_alerts(user_id)
    })

@api.route('/api/v1/alerts', methods=['POST'])
@require_auth
def create_price_alert():
    """Create a price alert"""
    try:
        data = request.json
        product_id = data['product_id']
        target_price = data['target_price']
        
        alert = PriceAlert(
            user_id=request.user.id,
            product_id=product_id,
            target_price=target_price
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({'message': 'Alert created successfully'}), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400

@api.route('/api/chatbot', methods=['POST'])
def chatbot_response():
    """Handle chatbot requests"""
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'No message provided'}), 400
            
        # Get response from BudBot
        bot = BudBot()
        response = bot.generate_response(message)
        
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        return jsonify({'error': 'Failed to generate response'}), 500

@api.route('/api/v1/recommendations/mood', methods=['POST'])
def get_mood_recommendations():
    """Get mood-based recommendations"""
    try:
        mood = request.json.get('mood')
        if not mood:
            return jsonify({'error': 'Mood is required'}), 400
            
        bot = BudBot()
        recommendations = bot.recommendation_engine.get_mood_based_recommendations(mood)
        
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@api.route('/api/v1/recommendations/personal', methods=['GET'])
@require_auth
def get_personal_recommendations():
    """Get personalized recommendations"""
    try:
        bot = BudBot()
        recommendations = bot.get_personalized_recommendations(request.user.id)
        
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@api.route('/api/v1/strains/rate', methods=['POST'])
@require_auth
def rate_strain():
    """Rate a strain"""
    try:
        strain_id = request.json.get('strain_id')
        rating = request.json.get('rating')
        
        if not strain_id or not rating:
            return jsonify({'error': 'Strain ID and rating are required'}), 400
            
        bot = BudBot()
        bot.handle_strain_rating(request.user.id, strain_id, rating)
        
        return jsonify({'message': 'Rating saved successfully'})
    except Exception as e:
        logger.error(f"Error saving rating: {str(e)}")
        return jsonify({'error': 'Failed to save rating'}), 500

# Error handlers
@api.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429

@api.errorhandler(ValidationError)
def validation_error_handler(e):
    return jsonify({'error': str(e)}), 400

@api.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Unhandled error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500