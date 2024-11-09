from flask import Blueprint, jsonify, request
from models import Deal
from database import db

deals_bp = Blueprint('deals', __name__)

@deals_bp.route('/api/deals')
def get_deals():
    location = request.args.get('location', '')
    query = Deal.query
    
    if location:
        query = query.filter(Deal.location.ilike(f'%{location}%'))
    
    deals = query.order_by(Deal.created_at.desc()).limit(12).all()
    return jsonify({
        'deals': [deal.to_dict() for deal in deals]
    })
