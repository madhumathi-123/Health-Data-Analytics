"""
Prediction Routes
Handles outbreak predictions and demand forecasting
"""
from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required, role_required, log_action
from utils.data_utils import get_all_predictions, get_prediction_by_id
from services.prediction_service import PredictionService, run_daily_predictions

predictions_bp = Blueprint('predictions', __name__)

# Initialize prediction service
prediction_service = PredictionService()

@predictions_bp.route('/outbreaks', methods=['GET'])
@token_required
def get_outbreaks(current_user):
    """Get all outbreak predictions"""
    status = request.args.get('status')
    predictions = get_all_predictions(status)
    
    return jsonify({
        'predictions': predictions,
        'count': len(predictions)
    }), 200

@predictions_bp.route('/outbreaks/<int:prediction_id>', methods=['GET'])
@token_required
def get_outbreak(current_user, prediction_id):
    """Get outbreak prediction by ID"""
    prediction = get_prediction_by_id(prediction_id)
    
    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404
    
    return jsonify({'prediction': prediction}), 200

@predictions_bp.route('/run-prediction', methods=['POST'])
@token_required
@role_required(['admin', 'manager'])
def run_prediction(current_user):
    """Run outbreak prediction pipeline"""
    try:
        # Load models if not already loaded
        if not prediction_service.models_loaded:
            success = prediction_service.load_models()
            if not success:
                return jsonify({'error': 'Failed to load ML models'}), 500
        
        # Get parameters
        data = request.get_json() or {}
        months_ahead = data.get('months_ahead', 3)
        
        # Run predictions
        predictions = prediction_service.predict_outbreaks(months_ahead)
        
        # Log action
        log_action(current_user['user_id'], 'run_prediction', 'outbreak_predictions',
                  details=f"Generated {len(predictions)} predictions")
        
        return jsonify({
            'message': 'Predictions generated successfully',
            'count': len(predictions),
            'predictions': predictions[:20]  # Return first 20
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/demand-forecast', methods=['POST'])
@token_required
@role_required(['admin', 'manager'])
def forecast_demand(current_user):
    """Forecast medicine demand"""
    try:
        data = request.get_json()
        
        if 'medicine_id' not in data:
            return jsonify({'error': 'medicine_id required'}), 400
        
        # Load models if not already loaded
        if not prediction_service.models_loaded:
            success = prediction_service.load_models()
            if not success:
                return jsonify({'error': 'Failed to load ML models'}), 500
        
        medicine_id = data['medicine_id']
        months_ahead = data.get('months_ahead', 3)
        outbreak_prediction = data.get('outbreak_prediction')
        
        # Forecast demand
        forecasts = prediction_service.forecast_medicine_demand(
            medicine_id, outbreak_prediction, months_ahead
        )
        
        if not forecasts:
            return jsonify({'error': 'Failed to generate forecast'}), 500
        
        return jsonify({
            'forecasts': forecasts
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/reorder-recommendations', methods=['GET'])
@token_required
def get_reorder_recommendations(current_user):
    """Get reorder recommendations based on demand forecast"""
    try:
        # Load models if not already loaded
        if not prediction_service.models_loaded:
            success = prediction_service.load_models()
            if not success:
                return jsonify({'error': 'Failed to load ML models'}), 500
        
        # Calculate recommendations
        recommendations = prediction_service.calculate_reorder_recommendations()
        
        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/risk-map', methods=['GET'])
@token_required
def get_risk_map(current_user):
    """Get outbreak risk map data"""
    try:
        # Load models if not already loaded
        if not prediction_service.models_loaded:
            success = prediction_service.load_models()
            if not success:
                return jsonify({'error': 'Failed to load ML models'}), 500
        
        risk_map = prediction_service.get_outbreak_risk_map()
        
        return jsonify({
            'locations': risk_map
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
