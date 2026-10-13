"""
Configuration settings for the Outbreak-Linked Smart Drug Inventory System
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database Settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'inventory.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # ML Models Path
    MODELS_DIR = os.path.join(BASE_DIR, 'models', 'trained_models')
    
    # Data Paths
    DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    
    # Email Configuration (SMTP)
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_EMAIL = os.environ.get('SMTP_EMAIL') or 'deepigaptks@gmail.com'
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or 'jmnk wkqi pzel ycvu'
    SMTP_USE_TLS = True
    
    # Notification Settings
    ALERT_EMAIL_RECIPIENTS = [
        'deepigakds@gmail.com',
        'deepigakkpgirl@gmail.com'
    ]
    
    # Prediction Settings
    PREDICTION_SCHEDULE_HOUR = 10  # Run predictions at 2 AM daily
    OUTBREAK_PROBABILITY_THRESHOLD = 0.7  # Alert if probability > 70%
    LOW_STOCK_THRESHOLD_DAYS = 30  # Alert if stock < 30 days supply
    
    # Inventory Settings
    DEFAULT_REORDER_LEVEL = 100
    SAFETY_STOCK_MULTIPLIER = 1.5
    
    # Report Settings
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # CORS Settings
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3000'
    ]
    
    # Role Definitions
    ROLES = {
        'admin': {
            'permissions': ['all'],
            'access': ['dashboard', 'users', 'inventory', 'orders', 
                      'predictions', 'reports', 'settings', 'audit_logs']
        },
        'manager': {
            'permissions': ['read', 'write', 'approve_orders'],
            'access': ['dashboard', 'inventory', 'orders', 'predictions', 
                      'reports', 'notifications']
        },
        'staff': {
            'permissions': ['read', 'write_inventory'],
            'access': ['dashboard', 'inventory', 'orders:view', 'notifications']
        },
        'viewer': {
            'permissions': ['read'],
            'access': ['dashboard:view', 'reports:view']
        }
    }
    
    # Disease Categories
    DISEASE_CATEGORIES = [
        'Viral Infection',
        'Bacterial Infection',
        'Parasitic Disease',
        'Respiratory Disease',
        'Vector-borne Disease',
        'Waterborne Disease',
        'Foodborne Disease'
    ]
    
    # Severity Levels
    SEVERITY_LEVELS = ['Low', 'Medium', 'High', 'Critical']
    
    # Order Status
    ORDER_STATUS = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    # Notification Types
    NOTIFICATION_TYPES = [
        'outbreak_alert',
        'low_stock',
        'order_update',
        'expiry_warning',
        'prediction_complete'
    ]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
