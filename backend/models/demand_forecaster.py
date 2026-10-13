"""
Medicine Demand Forecasting Model
Uses XGBoost and Gradient Boosting for predicting medicine demand
Predicts: quantity needed, optimal reorder timing
"""
import numpy as np
import pandas as pd
import pickle
import os
import sys
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import joblib

class DemandForecaster:
    """
    ML Model for forecasting medicine demand
    """
    
    def __init__(self, models_dir=None):
        if models_dir is None:
            self.models_dir = os.path.join(os.path.dirname(__file__), 'trained_models')
        else:
            self.models_dir = models_dir
        
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.demand_model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_names = None
        
    def load_data(self, data_dir):
        """Load preprocessed training data"""
        print("📂 Loading preprocessed data...")
        
        self.X_train = np.load(os.path.join(data_dir, 'X_train_demand.npy'))
        self.X_test = np.load(os.path.join(data_dir, 'X_test_demand.npy'))
        self.y_train = np.load(os.path.join(data_dir, 'y_train_demand.npy'))
        self.y_test = np.load(os.path.join(data_dir, 'y_test_demand.npy'))
        
        # Load scalers and encoders
        with open(os.path.join(data_dir, 'scaler_demand.pkl'), 'rb') as f:
            self.scaler = pickle.load(f)
        
        with open(os.path.join(data_dir, 'label_encoders.pkl'), 'rb') as f:
            self.label_encoders = pickle.load(f)
        
        with open(os.path.join(data_dir, 'feature_names.pkl'), 'rb') as f:
            feature_dict = pickle.load(f)
            self.feature_names = feature_dict['demand_features']
        
        print(f"✅ Loaded training data: {self.X_train.shape}")
        print(f"✅ Loaded test data: {self.X_test.shape}")
        
    def train_model(self):
        """Train demand forecasting model"""
        print("\n🤖 Training medicine demand forecasting model...")
        
        # XGBoost Regressor for demand prediction
        self.demand_model = xgb.XGBRegressor(
            n_estimators=250,
            max_depth=10,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            random_state=42,
            n_jobs=-1
        )
        
        self.demand_model.fit(
            self.X_train, 
            self.y_train,
            eval_set=[(self.X_test, self.y_test)],
            verbose=False
        )
        
        # Evaluate
        train_pred = self.demand_model.predict(self.X_train)
        test_pred = self.demand_model.predict(self.X_test)
        
        train_rmse = np.sqrt(mean_squared_error(self.y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(self.y_test, test_pred))
        train_mae = mean_absolute_error(self.y_train, train_pred)
        test_mae = mean_absolute_error(self.y_test, test_pred)
        train_r2 = r2_score(self.y_train, train_pred)
        test_r2 = r2_score(self.y_test, test_pred)
        
        print(f"✅ Demand Model Training Complete")
        print(f"   Train - RMSE: {train_rmse:.2f}, MAE: {train_mae:.2f}, R²: {train_r2:.4f}")
        print(f"   Test  - RMSE: {test_rmse:.2f}, MAE: {test_mae:.2f}, R²: {test_r2:.4f}")
        
        # Feature importance
        feature_importance = self.demand_model.feature_importances_
        top_features_idx = np.argsort(feature_importance)[-5:]
        
        print("\n📊 Top 5 Important Features:")
        for idx in reversed(top_features_idx):
            print(f"   {self.feature_names[idx]}: {feature_importance[idx]:.4f}")
        
        return {
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2
        }
    
    def save_model(self):
        """Save trained model"""
        print("\n💾 Saving model...")
        
        joblib.dump(self.demand_model, os.path.join(self.models_dir, 'demand_forecast_model.pkl'))
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'trained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': 'XGBoost Regressor'
        }
        
        with open(os.path.join(self.models_dir, 'demand_model_metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"✅ Model saved to {self.models_dir}")
    
    def load_model(self):
        """Load trained model"""
        print("📂 Loading trained model...")
        
        self.demand_model = joblib.load(os.path.join(self.models_dir, 'demand_forecast_model.pkl'))
        
        # Load metadata
        with open(os.path.join(self.models_dir, 'demand_model_metadata.pkl'), 'rb') as f:
            metadata = pickle.load(f)
            self.feature_names = metadata['feature_names']
        
        print("✅ Model loaded successfully")
    
    def predict(self, features):
        """
        Make demand prediction for new data
        
        Args:
            features: numpy array or dict of features
        
        Returns:
            dict with predictions
        """
        if isinstance(features, dict):
            # Convert dict to array in correct order
            features = np.array([features[f] for f in self.feature_names]).reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict demand
        predicted_demand = self.demand_model.predict(features_scaled)[0]
        
        # Calculate confidence interval (simplified)
        confidence = 0.85  # 85% confidence
        margin = predicted_demand * 0.15  # ±15% margin
        
        return {
            'predicted_quantity': max(0, int(predicted_demand)),
            'lower_bound': max(0, int(predicted_demand - margin)),
            'upper_bound': int(predicted_demand + margin),
            'confidence': confidence
        }
    
    def forecast_demand(self, medicine, disease, location, outbreak_cases, months_ahead=3):
        """
        Forecast medicine demand for upcoming months
        
        Args:
            medicine: medicine name
            disease: disease name
            location: dict with state info
            outbreak_cases: predicted outbreak cases
            months_ahead: number of months to forecast
        
        Returns:
            list of demand forecasts
        """
        forecasts = []
        current_date = datetime.now()
        
        for month_offset in range(1, months_ahead + 1):
            future_date = current_date + timedelta(days=30 * month_offset)
            
            # Create features for future date
            features = self._create_features_for_date(
                medicine, disease, location, future_date, outbreak_cases
            )
            
            # Make prediction
            prediction = self.predict(features)
            prediction['forecast_date'] = future_date.strftime('%Y-%m-%d')
            prediction['month'] = future_date.month
            prediction['medicine'] = medicine
            prediction['disease'] = disease
            prediction['location'] = location.get('state', 'Unknown')
            
            forecasts.append(prediction)
        
        return forecasts
    
    def calculate_reorder_quantity(self, current_stock, predicted_demand, lead_time_days=14, safety_factor=1.5):
        """
        Calculate optimal reorder quantity
        
        Args:
            current_stock: current inventory level
            predicted_demand: predicted demand
            lead_time_days: supplier lead time
            safety_factor: safety stock multiplier
        
        Returns:
            dict with reorder recommendations
        """
        # Calculate daily demand
        daily_demand = predicted_demand / 30
        
        # Calculate lead time demand
        lead_time_demand = daily_demand * lead_time_days
        
        # Calculate safety stock
        safety_stock = lead_time_demand * (safety_factor - 1)
        
        # Calculate reorder point
        reorder_point = lead_time_demand + safety_stock
        
        # Calculate order quantity
        if current_stock < reorder_point:
            order_quantity = int(predicted_demand * safety_factor - current_stock)
            should_reorder = True
        else:
            order_quantity = 0
            should_reorder = False
        
        # Calculate days until stockout
        if daily_demand > 0:
            days_until_stockout = int(current_stock / daily_demand)
        else:
            days_until_stockout = 999
        
        return {
            'should_reorder': should_reorder,
            'reorder_quantity': max(0, order_quantity),
            'reorder_point': int(reorder_point),
            'safety_stock': int(safety_stock),
            'days_until_stockout': days_until_stockout,
            'urgency': 'Critical' if days_until_stockout < 7 else 'High' if days_until_stockout < 14 else 'Medium' if days_until_stockout < 30 else 'Low'
        }
    
    def _create_features_for_date(self, medicine, disease, location, date, outbreak_cases):
        """Create feature vector for a specific date"""
        month = date.month
        quarter = (month - 1) // 3 + 1
        day_of_week = date.weekday()
        week_of_year = date.isocalendar()[1]
        
        # Encode medicine, disease, and location
        medicine_encoded = self.label_encoders['medicine_name'].transform([medicine])[0]
        disease_encoded = self.label_encoders['disease_name'].transform([disease])[0]
        state_encoded = self.label_encoders['state'].transform([location.get('state', 'Unknown')])[0]
        
        features = np.array([
            medicine_encoded,
            disease_encoded,
            state_encoded,
            month,
            quarter,
            day_of_week,
            week_of_year,
            1 if month in [6, 7, 8, 9] else 0,  # is_monsoon
            1 if month in [11, 12, 1, 2] else 0,  # is_winter
            50,   # prev_usage (placeholder)
            75,   # prev_7d_avg (placeholder)
            100,  # prev_30d_avg (placeholder)
            outbreak_cases,
            0.90  # effectiveness_rate (placeholder)
        ]).reshape(1, -1)
        
        return features


def main():
    """Main training pipeline"""
    print("="*60)
    print("🚀 MEDICINE DEMAND FORECASTING MODEL TRAINING")
    print("="*60)
    
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'processed')
    
    # Initialize forecaster
    forecaster = DemandForecaster()
    
    # Load data
    forecaster.load_data(data_dir)
    
    # Train model
    metrics = forecaster.train_model()
    
    # Save model
    forecaster.save_model()
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print("\n📊 Final Metrics:")
    print(f"   Test RMSE: {metrics['test_rmse']:.2f}")
    print(f"   Test MAE: {metrics['test_mae']:.2f}")
    print(f"   Test R²: {metrics['test_r2']:.4f}")
    print("\n🎯 Model ready for deployment!")


if __name__ == '__main__':
    if '--train' in sys.argv:
        main()
    else:
        print("Usage: python demand_forecaster.py --train")
        print("Or import DemandForecaster class for inference")
