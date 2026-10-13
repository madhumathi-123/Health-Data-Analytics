"""
Main Flask Application
Outbreak-Linked Smart Drug Inventory & Supply Chain Tracking System
"""
from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

# Import configuration
from config import config

# Import routes
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.inventory import inventory_bp
from routes.orders import orders_bp
from routes.predictions import predictions_bp
from routes.reports import reports_bp

# Import services
from services.prediction_service import run_daily_predictions
from services.notification_service import NotificationService

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# Initialize scheduler for automated predictions
scheduler = BackgroundScheduler()

def scheduled_prediction_job():
    """Job to run daily predictions"""
    print(f"\n{'='*60}")
    print(f"🤖 Running scheduled prediction job at {datetime.now()}")
    print(f"{'='*60}\n")
    
    try:
        run_daily_predictions()
        print("✅ Scheduled prediction job completed successfully")
    except Exception as e:
        print(f"❌ Scheduled prediction job failed: {str(e)}")

def scheduled_notification_job():
    """Job to process pending notifications"""
    try:
        notification_service = NotificationService()
        count = notification_service.process_pending_notifications()
        if count > 0:
            print(f"📧 Processed {count} pending notifications")
    except Exception as e:
        print(f"❌ Notification job failed: {str(e)}")

# Schedule jobs
if not app.config['TESTING']:
    # Run predictions daily at configured hour (default 2 AM)
    scheduler.add_job(
        func=scheduled_prediction_job,
        trigger="cron",
        hour=app.config['PREDICTION_SCHEDULE_HOUR'],
        minute=0,
        id='daily_predictions',
        name='Daily outbreak predictions',
        replace_existing=True
    )
    
    # Process notifications every hour
    scheduler.add_job(
        func=scheduled_notification_job,
        trigger="interval",
        hours=1,
        id='process_notifications',
        name='Process pending notifications',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler started for automated jobs")

# Root endpoint
@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'name': 'Outbreak-Linked Smart Drug Inventory System',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': '/api/auth',
            'dashboard': '/api/dashboard',
            'inventory': '/api/inventory',
            'orders': '/api/orders',
            'predictions': '/api/predictions',
            'reports': '/api/reports'
        }
    }), 200

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({'error': 'Access forbidden'}), 403

@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 errors"""
    return jsonify({'error': 'Unauthorized access'}), 401

# Shutdown scheduler on app exit
import atexit
atexit.register(lambda: scheduler.shutdown() if scheduler.running else None)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 OUTBREAK-LINKED SMART DRUG INVENTORY SYSTEM")
    print("="*60)
    print(f"Environment: {env}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(f"Database: {app.config['DATABASE_PATH']}")
    print(f"Server: http://localhost:5000")
    print("="*60 + "\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
