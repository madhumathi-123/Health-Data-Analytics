"""
Outbreak Prediction Model
Uses Random Forest and XGBoost for disease outbreak prediction
Predicts: outbreak probability, expected cases, severity level
"""
import numpy as np
import pandas as pd
import pickle
import os
import sys
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, classification_report
import xgboost as xgb
import joblib

class OutbreakPredictor:
    """
    ML Model for predicting disease outbreaks
    """
    
    def __init__(self, models_dir=None):
        if models_dir is None:
            self.models_dir = os.path.join(os.path.dirname(__file__), 'trained_models')
        else:
            self.models_dir = models_dir
        
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.cases_model = None
        self.severity_model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_names = None
        
    def load_data(self, data_dir):
        """Load preprocessed training data"""
        print("📂 Loading preprocessed data...")
        
        self.X_train = np.load(os.path.join(data_dir, 'X_train_outbreak.npy'))
        self.X_test = np.load(os.path.join(data_dir, 'X_test_outbreak.npy'))
        self.y_train_cases = np.load(os.path.join(data_dir, 'y_train_cases.npy'))
        self.y_test_cases = np.load(os.path.join(data_dir, 'y_test_cases.npy'))
        self.y_train_severity = np.load(os.path.join(data_dir, 'y_train_severity.npy'))
        self.y_test_severity = np.load(os.path.join(data_dir, 'y_test_severity.npy'))
        
        # Load scalers and encoders
        with open(os.path.join(data_dir, 'scaler_outbreak.pkl'), 'rb') as f:
            self.scaler = pickle.load(f)
        
        with open(os.path.join(data_dir, 'label_encoders.pkl'), 'rb') as f:
            self.label_encoders = pickle.load(f)
        
        with open(os.path.join(data_dir, 'feature_names.pkl'), 'rb') as f:
            feature_dict = pickle.load(f)
            self.feature_names = feature_dict['outbreak_features']
        
        print(f"✅ Loaded training data: {self.X_train.shape}")
        print(f"✅ Loaded test data: {self.X_test.shape}")
        
    def train_cases_model(self):
        """Train model to predict number of outbreak cases"""
        print("\n🤖 Training outbreak cases prediction model...")
        
        # XGBoost Regressor for cases prediction
        self.cases_model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        self.cases_model.fit(
            self.X_train, 
            self.y_train_cases,
            eval_set=[(self.X_test, self.y_test_cases)],
            verbose=False
        )
        
        # Evaluate
        train_pred = self.cases_model.predict(self.X_train)
        test_pred = self.cases_model.predict(self.X_test)
        
        train_rmse = np.sqrt(mean_squared_error(self.y_train_cases, train_pred))
        test_rmse = np.sqrt(mean_squared_error(self.y_test_cases, test_pred))
        train_mae = mean_absolute_error(self.y_train_cases, train_pred)
        test_mae = mean_absolute_error(self.y_test_cases, test_pred)
        
        print(f"✅ Cases Model Training Complete")
        print(f"   Train RMSE: {train_rmse:.2f}, MAE: {train_mae:.2f}")
        print(f"   Test RMSE: {test_rmse:.2f}, MAE: {test_mae:.2f}")
        
        return {
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae
        }
    
    def train_severity_model(self):
        """Train model to predict outbreak severity"""
        print("\n🤖 Training severity classification model...")
        
        # Random Forest Classifier for severity
        self.severity_model = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.severity_model.fit(self.X_train, self.y_train_severity)
        
        # Evaluate
        train_pred = self.severity_model.predict(self.X_train)
        test_pred = self.severity_model.predict(self.X_test)
        
        train_acc = accuracy_score(self.y_train_severity, train_pred)
        test_acc = accuracy_score(self.y_test_severity, test_pred)
        
        print(f"✅ Severity Model Training Complete")
        print(f"   Train Accuracy: {train_acc:.4f}")
        print(f"   Test Accuracy: {test_acc:.4f}")
        
        # Print classification report
        print("\n📊 Classification Report:")
        print(classification_report(self.y_test_severity, test_pred))
        
        return {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc
        }
    
    def save_models(self):
        """Save trained models"""
        print("\n💾 Saving models...")
        
        joblib.dump(self.cases_model, os.path.join(self.models_dir, 'outbreak_cases_model.pkl'))
        joblib.dump(self.severity_model, os.path.join(self.models_dir, 'outbreak_severity_model.pkl'))
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'trained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': 'XGBoost + RandomForest'
        }
        
        with open(os.path.join(self.models_dir, 'outbreak_model_metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"✅ Models saved to {self.models_dir}")
    
    def load_models(self):
        """Load trained models"""
        print("📂 Loading trained models...")
        
        self.cases_model = joblib.load(os.path.join(self.models_dir, 'outbreak_cases_model.pkl'))
        self.severity_model = joblib.load(os.path.join(self.models_dir, 'outbreak_severity_model.pkl'))
        
        # Load metadata
        with open(os.path.join(self.models_dir, 'outbreak_model_metadata.pkl'), 'rb') as f:
            metadata = pickle.load(f)
            self.feature_names = metadata['feature_names']
        
        print("✅ Models loaded successfully")
    
    def predict(self, features):
        """
        Make predictions for new data
        
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
        
        # Predict cases
        predicted_cases = self.cases_model.predict(features_scaled)[0]
        
        # Predict severity
        severity_encoded = self.severity_model.predict(features_scaled)[0]
        severity_proba = self.severity_model.predict_proba(features_scaled)[0]
        
        # Decode severity
        severity_levels = ['Low', 'Medium', 'High', 'Critical']
        severity_label = severity_levels[int(severity_encoded)] if int(severity_encoded) < len(severity_levels) else 'Unknown'
        
        # Calculate outbreak probability (based on predicted cases and severity)
        outbreak_probability = min(predicted_cases / 1000.0, 1.0) * max(severity_proba)
        
        return {
            'predicted_cases': max(0, int(predicted_cases)),
            'severity_level': severity_label,
            'severity_confidence': float(max(severity_proba)),
            'outbreak_probability': float(outbreak_probability),
            'risk_score': float(outbreak_probability * 100)
        }
    
    def predict_future_outbreaks(self, disease, location, months_ahead=3):
        """
        Predict potential outbreaks for upcoming months
        
        Args:
            disease: disease name
            location: dict with state, latitude, longitude
            months_ahead: number of months to predict
        
        Returns:
            list of predictions
        """
        predictions = []
        current_date = datetime.now()
        
        for month_offset in range(1, months_ahead + 1):
            future_date = current_date + timedelta(days=30 * month_offset)
            
            # Create features for future date
            features = self._create_features_for_date(disease, location, future_date)
            
            # Make prediction
            prediction = self.predict(features)
            prediction['predicted_date'] = future_date.strftime('%Y-%m-%d')
            prediction['month'] = future_date.month
            prediction['disease'] = disease
            prediction['location'] = location.get('state', 'Unknown')
            
            predictions.append(prediction)
        
        return predictions
    
    def _create_features_for_date(self, disease, location, date):
        """Create feature vector for a specific date"""
        # This is a simplified version - in production, you'd use historical data
        month = date.month
        quarter = (month - 1) // 3 + 1
        day_of_week = date.weekday()
        week_of_year = date.isocalendar()[1]
        
        # Encode disease and location
        disease_encoded = self.label_encoders['disease_name'].transform([disease])[0]
        state_encoded = self.label_encoders['state'].transform([location.get('state', 'Unknown')])[0]
        
        features = np.array([
            disease_encoded,
            state_encoded,
            month,
            quarter,
            day_of_week,
            week_of_year,
            1 if month in [6, 7, 8, 9] else 0,  # is_monsoon
            1 if month in [11, 12, 1, 2] else 0,  # is_winter
            100,  # prev_cases (placeholder)
            30,   # days_since_last (placeholder)
            150,  # avg_cases (placeholder)
            50,   # std_cases (placeholder)
            500,  # max_cases (placeholder)
            location.get('latitude', 0),
            location.get('longitude', 0)
        ]).reshape(1, -1)
        
        return features


def main():
    """Main training pipeline"""
    print("="*60)
    print("🚀 OUTBREAK PREDICTION MODEL TRAINING")
    print("="*60)
    
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'processed')
    
    # Initialize predictor
    predictor = OutbreakPredictor()
    
    # Load data
    predictor.load_data(data_dir)
    
    # Train models
    cases_metrics = predictor.train_cases_model()
    severity_metrics = predictor.train_severity_model()
    
    # Save models
    predictor.save_models()
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print("\n📊 Final Metrics:")
    print(f"   Cases Prediction - Test RMSE: {cases_metrics['test_rmse']:.2f}")
    print(f"   Severity Classification - Test Accuracy: {severity_metrics['test_accuracy']:.4f}")
    print("\n🎯 Models ready for deployment!")


if __name__ == '__main__':
    if '--train' in sys.argv:
        main()
    else:
        print("Usage: python outbreak_predictor.py --train")
        print("Or import OutbreakPredictor class for inference")
