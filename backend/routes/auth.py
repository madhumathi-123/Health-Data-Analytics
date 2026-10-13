"""
Authentication Routes
Handles user login, signup, and token verification
"""
from flask import Blueprint, request, jsonify
from utils.auth_utils import (
    authenticate_user, create_user, generate_token,
    token_required, get_user_by_id, log_action
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Authenticate user
    user = authenticate_user(email, password)
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = generate_token(user['user_id'], user['username'], user['role'])
    
    # Log action
    log_action(user['user_id'], 'login', 'users')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    role = data.get('role', 'viewer')  # Default role is viewer
    
    # Validate role
    valid_roles = ['admin', 'manager', 'staff', 'viewer']
    if role not in valid_roles:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Create user
    user, error = create_user(username, email, password, role)
    
    if error:
        return jsonify({'error': error}), 400
    
    # Generate token
    token = generate_token(user['user_id'], user['username'], user['role'])
    
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 201

@auth_bp.route('/verify-token', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify JWT token"""
    return jsonify({
        'valid': True,
        'user': current_user
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile"""
    user = get_user_by_id(current_user['user_id'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user}), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """User logout (client-side token removal)"""
    log_action(current_user['user_id'], 'logout', 'users')
    
    return jsonify({'message': 'Logout successful'}), 200
