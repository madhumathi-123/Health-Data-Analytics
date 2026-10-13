"""
Order Management Routes
Handles order creation, tracking, and approval
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from utils.auth_utils import token_required, role_required, log_action
from utils.data_utils import (
    get_all_orders, get_order_by_id, create_order,
    update_order_status, get_all_suppliers, get_medicine_by_id
)
from services.notification_service import send_order_update

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@token_required
def get_orders(current_user):
    """Get all orders"""
    status = request.args.get('status')
    orders = get_all_orders(status)
    
    return jsonify({
        'orders': orders,
        'count': len(orders)
    }), 200

@orders_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    """Get order by ID"""
    order = get_order_by_id(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({'order': order}), 200

@orders_bp.route('/create', methods=['POST'])
@token_required
@role_required(['admin', 'manager'])
def create_new_order(current_user):
    """Create new order"""
    data = request.get_json()
    
    required_fields = ['medicine_id', 'supplier_id', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    medicine = get_medicine_by_id(data['medicine_id'])
    if not medicine:
        return jsonify({'error': 'Medicine not found'}), 404
    
    # Calculate expected delivery (default 14 days)
    lead_time = data.get('lead_time_days', 14)
    expected_delivery = (datetime.now() + timedelta(days=lead_time)).strftime('%Y-%m-%d')
    
    # Calculate total cost
    total_cost = medicine['unit_price'] * data['quantity']
    
    # Create order
    order_id = create_order(
        medicine_id=data['medicine_id'],
        supplier_id=data['supplier_id'],
        quantity=data['quantity'],
        expected_delivery=expected_delivery,
        total_cost=total_cost,
        created_by=current_user['user_id'],
        notes=data.get('notes')
    )
    
    # Log action
    log_action(current_user['user_id'], 'create', 'orders', order_id,
              f"Created order for {medicine['medicine_name']}")
    
    return jsonify({
        'message': 'Order created successfully',
        'order_id': order_id
    }), 201

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@token_required
@role_required(['admin', 'manager'])
def update_status(current_user, order_id):
    """Update order status"""
    order = get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'error': 'Status required'}), 400
    
    new_status = data['status']
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Update status
    update_order_status(order_id, new_status, current_user['user_id'])
    
    # Send notification (if email provided)
    if 'notify_email' in data:
        send_order_update(order_id, new_status, data['notify_email'])
    
    # Log action
    log_action(current_user['user_id'], 'update_status', 'orders', order_id,
              f"Status changed to: {new_status}")
    
    return jsonify({'message': 'Order status updated successfully'}), 200

@orders_bp.route('/suppliers', methods=['GET'])
@token_required
def get_suppliers(current_user):
    """Get all suppliers"""
    suppliers = get_all_suppliers()
    
    return jsonify({
        'suppliers': suppliers,
        'count': len(suppliers)
    }), 200
