"""
Authentication and Authorization Utilities
Handles JWT tokens, password hashing, and role-based access control
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import sqlite3
import os

# JWT Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'inventory.db')

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(user_id, username, role):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_from_token(token):
    """Extract user information from token"""
    payload = decode_token(token)
    if payload:
        return {
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'role': payload.get('role')
        }
    return None

def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        user = get_user_from_token(token)
        if not user:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Pass user info to the route
        return f(current_user=user, *args, **kwargs)
    
    return decorated

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get current user from kwargs (set by token_required)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = current_user.get('role')
            
            # Admin has access to everything
            if user_role == 'admin':
                return f(*args, **kwargs)
            
            # Check if user role is in allowed roles
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id, username, email, password_hash, role FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return None
    
    user_id, username, email, password_hash, role = user
    
    # Verify password
    if verify_password(password, password_hash):
        return {
            'user_id': user_id,
            'username': username,
            'email': email,
            'role': role
        }
    
    return None

def create_user(username, email, password, role='viewer'):
    """Create new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT user_id FROM users WHERE email = ? OR username = ?', (email, username))
    if cursor.fetchone():
        conn.close()
        return None, 'User already exists'
    
    # Hash password
    password_hash = hash_password(password)
    
    # Insert user
    try:
        cursor.execute('''INSERT INTO users (username, email, password_hash, role) 
                         VALUES (?, ?, ?, ?)''', (username, email, password_hash, role))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {
            'user_id': user_id,
            'username': username,
            'email': email,
            'role': role
        }, None
    except Exception as e:
        conn.close()
        return None, str(e)

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id, username, email, role, created_at FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'user_id': user[0],
            'username': user[1],
            'email': user[2],
            'role': user[3],
            'created_at': user[4]
        }
    
    return None

def log_action(user_id, action, table_affected, record_id=None, details=None):
    """Log user action to audit trail"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO audit_logs (user_id, action, table_affected, record_id, details)
                     VALUES (?, ?, ?, ?, ?)''', (user_id, action, table_affected, record_id, details))
    conn.commit()
    conn.close()

# Role permissions configuration
ROLE_PERMISSIONS = {
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

def has_permission(user_role, required_permission):
    """Check if user role has required permission"""
    if user_role == 'admin':
        return True
    
    role_perms = ROLE_PERMISSIONS.get(user_role, {})
    permissions = role_perms.get('permissions', [])
    
    return required_permission in permissions or 'all' in permissions

def has_access(user_role, resource):
    """Check if user role has access to resource"""
    if user_role == 'admin':
        return True
    
    role_perms = ROLE_PERMISSIONS.get(user_role, {})
    access_list = role_perms.get('access', [])
    
    return resource in access_list or 'all' in access_list
