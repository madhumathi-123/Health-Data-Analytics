"""
Dashboard Routes
Provides dashboard statistics, outbreak maps, and overview data
"""
from flask import Blueprint, jsonify
from utils.auth_utils import token_required
from utils.data_utils import (
    get_dashboard_stats, get_low_stock_medicines,
    get_high_risk_predictions, get_all_predictions
)
from services.prediction_service import PredictionService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    """Get dashboard statistics"""
    stats = get_dashboard_stats()
    
    return jsonify({
        'stats': stats
    }), 200

@dashboard_bp.route('/outbreak-map', methods=['GET'])
@token_required
def get_outbreak_map(current_user):
    """Get outbreak risk map data"""
    try:
        prediction_service = PredictionService()
        prediction_service.load_models()
        risk_map = prediction_service.get_outbreak_risk_map()
        
        return jsonify({
            'locations': risk_map
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/inventory-status', methods=['GET'])
@token_required
def get_inventory_status(current_user):
    """Get inventory status overview"""
    low_stock = get_low_stock_medicines()
    
    # Categorize by urgency
    critical = [m for m in low_stock if m['stock_status'] == 'Critical']
    low = [m for m in low_stock if m['stock_status'] == 'Low']
    
    return jsonify({
        'low_stock': {
            'critical': critical[:10],  # Top 10 critical
            'low': low[:10],  # Top 10 low
            'total_count': len(low_stock)
        }
    }), 200

@dashboard_bp.route('/recent-predictions', methods=['GET'])
@token_required
def get_recent_predictions(current_user):
    """Get recent outbreak predictions"""
    predictions = get_all_predictions()
    
    # Get latest 10
    recent = predictions[:10] if len(predictions) > 10 else predictions
    
    return jsonify({
        'predictions': recent
    }), 200

@dashboard_bp.route('/high-risk-alerts', methods=['GET'])
@token_required
def get_high_risk_alerts(current_user):
    """Get high-risk outbreak alerts"""
    high_risk = get_high_risk_predictions(threshold=0.7)
    
    return jsonify({
        'alerts': high_risk
    }), 200
