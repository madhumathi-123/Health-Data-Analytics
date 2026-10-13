"""
Prediction Service
Integrates ML models for outbreak prediction and demand forecasting
"""
import os
import sys
import pickle
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.outbreak_predictor import OutbreakPredictor
from models.demand_forecaster import DemandForecaster
from utils.data_utils import (
    get_all_diseases, get_disease_by_name, create_prediction,
    get_all_medicines, get_medicine_by_id, get_high_risk_predictions
)
from services.notification_service import send_outbreak_alert
from config import Config

class PredictionService:
    """Service for running ML predictions"""
    
    def __init__(self):
        self.outbreak_predictor = None
        self.demand_forecaster = None
        self.models_loaded = False
        
        # Paths
        self.models_dir = Config.MODELS_DIR
        self.data_dir = Config.PROCESSED_DATA_DIR
    
    def load_models(self):
        """Load trained ML models"""
        try:
            print("📂 Loading ML models...")
            
            # Initialize predictors
            self.outbreak_predictor = OutbreakPredictor(self.models_dir)
            self.demand_forecaster = DemandForecaster(self.models_dir)
            
            # Load models
            self.outbreak_predictor.load_models()
            self.demand_forecaster.load_model()
            
            # Load scalers and encoders
            with open(os.path.join(self.data_dir, 'scaler_outbreak.pkl'), 'rb') as f:
                self.outbreak_predictor.scaler = pickle.load(f)
            
            with open(os.path.join(self.data_dir, 'scaler_demand.pkl'), 'rb') as f:
                self.demand_forecaster.scaler = pickle.load(f)
            
            with open(os.path.join(self.data_dir, 'label_encoders.pkl'), 'rb') as f:
                encoders = pickle.load(f)
                self.outbreak_predictor.label_encoders = encoders
                self.demand_forecaster.label_encoders = encoders
            
            self.models_loaded = True
            print("✅ ML models loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load models: {str(e)}")
            return False
    
    def predict_outbreaks(self, months_ahead=3):
        """
        Run outbreak predictions for all diseases and locations
        
        Args:
            months_ahead: Number of months to predict ahead
        
        Returns:
            list of predictions
        """
        if not self.models_loaded:
            self.load_models()
        
        print(f"\n🔮 Running outbreak predictions for next {months_ahead} months...")
        
        # Define locations to predict for
        locations = [
            {'state': 'Maharashtra', 'city': 'Mumbai', 'latitude': 19.0760, 'longitude': 72.8777},
            {'state': 'Delhi', 'city': 'New Delhi', 'latitude': 28.6139, 'longitude': 77.2090},
            {'state': 'Karnataka', 'city': 'Bangalore', 'latitude': 12.9716, 'longitude': 77.5946},
            {'state': 'Tamil Nadu', 'city': 'Chennai', 'latitude': 13.0827, 'longitude': 80.2707},
            {'state': 'West Bengal', 'city': 'Kolkata', 'latitude': 22.5726, 'longitude': 88.3639},
        ]
        
        # Get all diseases
        diseases = get_all_diseases()
        
        all_predictions = []
        high_risk_count = 0
        
        for disease in diseases:
            disease_name = disease['disease_name']
            
            for location in locations:
                try:
                    # Predict for this disease-location combination
                    predictions = self.outbreak_predictor.predict_future_outbreaks(
                        disease_name, location, months_ahead
                    )
                    
                    for pred in predictions:
                        # Save to database
                        prediction_id = create_prediction(
                            disease_id=disease['disease_id'],
                            location=location['city'],
                            state=location['state'],
                            latitude=location['latitude'],
                            longitude=location['longitude'],
                            predicted_date=pred['predicted_date'],
                            probability=pred['outbreak_probability'],
                            severity_level=pred['severity_level'],
                            predicted_cases=pred['predicted_cases'],
                            risk_score=pred['risk_score']
                        )
                        
                        pred['prediction_id'] = prediction_id
                        all_predictions.append(pred)
                        
                        # Send alert if high risk
                        if pred['outbreak_probability'] >= Config.OUTBREAK_PROBABILITY_THRESHOLD:
                            high_risk_count += 1
                            print(f"⚠️  High-risk outbreak detected: {disease_name} in {location['city']}")
                            # Send notification
                            send_outbreak_alert(prediction_id)
                
                except Exception as e:
                    print(f"❌ Error predicting {disease_name} in {location['city']}: {str(e)}")
                    continue
        
        print(f"\n✅ Predictions complete: {len(all_predictions)} predictions generated")
        print(f"⚠️  High-risk predictions: {high_risk_count}")
        
        return all_predictions
    
    def forecast_medicine_demand(self, medicine_id, outbreak_prediction=None, months_ahead=3):
        """
        Forecast demand for a specific medicine
        
        Args:
            medicine_id: ID of the medicine
            outbreak_prediction: Optional outbreak prediction data
            months_ahead: Number of months to forecast
        
        Returns:
            list of demand forecasts
        """
        if not self.models_loaded:
            self.load_models()
        
        medicine = get_medicine_by_id(medicine_id)
        if not medicine:
            return None
        
        # Get disease info
        disease_name = medicine['disease_name']
        
        # Default location (can be parameterized)
        location = {'state': 'Maharashtra'}
        
        # Get outbreak cases (if prediction provided)
        outbreak_cases = 0
        if outbreak_prediction:
            outbreak_cases = outbreak_prediction.get('predicted_cases', 0)
        else:
            # Use average historical cases
            outbreak_cases = 200
        
        # Forecast demand
        forecasts = self.demand_forecaster.forecast_demand(
            medicine=medicine['medicine_name'],
            disease=disease_name,
            location=location,
            outbreak_cases=outbreak_cases,
            months_ahead=months_ahead
        )
        
        return forecasts
    
    def calculate_reorder_recommendations(self):
        """
        Calculate reorder recommendations for all medicines
        
        Returns:
            list of medicines that need reordering
        """
        if not self.models_loaded:
            self.load_models()
        
        print("\n📊 Calculating reorder recommendations...")
        
        medicines = get_all_medicines()
        recommendations = []
        
        for medicine in medicines:
            try:
                # Forecast demand for next month
                forecasts = self.forecast_medicine_demand(medicine['medicine_id'], months_ahead=1)
                
                if forecasts and len(forecasts) > 0:
                    predicted_demand = forecasts[0]['predicted_quantity']
                    
                    # Calculate reorder recommendation
                    reorder_info = self.demand_forecaster.calculate_reorder_quantity(
                        current_stock=medicine['current_stock'],
                        predicted_demand=predicted_demand,
                        lead_time_days=14,
                        safety_factor=Config.SAFETY_STOCK_MULTIPLIER
                    )
                    
                    if reorder_info['should_reorder']:
                        recommendations.append({
                            'medicine_id': medicine['medicine_id'],
                            'medicine_name': medicine['medicine_name'],
                            'disease': medicine['disease_name'],
                            'current_stock': medicine['current_stock'],
                            'predicted_demand': predicted_demand,
                            'reorder_quantity': reorder_info['reorder_quantity'],
                            'urgency': reorder_info['urgency'],
                            'days_until_stockout': reorder_info['days_until_stockout']
                        })
            
            except Exception as e:
                print(f"❌ Error calculating reorder for {medicine['medicine_name']}: {str(e)}")
                continue
        
        # Sort by urgency
        urgency_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        recommendations.sort(key=lambda x: urgency_order.get(x['urgency'], 4))
        
        print(f"✅ Found {len(recommendations)} medicines that need reordering")
        
        return recommendations
    
    def get_outbreak_risk_map(self):
        """
        Get outbreak risk data for map visualization
        
        Returns:
            list of location-based risk data
        """
        predictions = get_high_risk_predictions(threshold=0.5)
        
        # Group by location
        risk_map = {}
        for pred in predictions:
            location_key = f"{pred['location']}, {pred['state']}"
            
            if location_key not in risk_map:
                risk_map[location_key] = {
                    'location': pred['location'],
                    'state': pred['state'],
                    'latitude': pred['latitude'],
                    'longitude': pred['longitude'],
                    'predictions': [],
                    'max_risk_score': 0,
                    'total_cases': 0
                }
            
            risk_map[location_key]['predictions'].append({
                'disease': pred['disease_name'],
                'probability': pred['probability'],
                'severity': pred['severity_level'],
                'cases': pred['predicted_cases'],
                'date': pred['predicted_date']
            })
            
            risk_map[location_key]['max_risk_score'] = max(
                risk_map[location_key]['max_risk_score'],
                pred['risk_score']
            )
            
            risk_map[location_key]['total_cases'] += pred['predicted_cases']
        
        return list(risk_map.values())


# Standalone functions
def run_daily_predictions():
    """Run daily prediction pipeline"""
    print("\n" + "="*60)
    print("🚀 RUNNING DAILY PREDICTION PIPELINE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    service = PredictionService()
    
    # Load models
    if not service.load_models():
        print("❌ Failed to load models. Exiting.")
        return False
    
    # Run outbreak predictions
    predictions = service.predict_outbreaks(months_ahead=3)
    
    # Calculate reorder recommendations
    recommendations = service.calculate_reorder_recommendations()
    
    print("\n" + "="*60)
    print("✅ DAILY PREDICTION PIPELINE COMPLETE")
    print("="*60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total predictions: {len(predictions)}")
    print(f"Reorder recommendations: {len(recommendations)}")
    
    return True


if __name__ == '__main__':
    # Test prediction service
    if '--run' in sys.argv:
        run_daily_predictions()
    else:
        print("Usage: python prediction_service.py --run")
        print("Or import PredictionService class for use in API")
