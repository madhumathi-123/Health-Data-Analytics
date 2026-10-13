"""
Inventory Management Routes
CRUD operations for medicines and inventory management
"""
from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required, role_required, log_action
from utils.data_utils import (
    get_all_medicines, get_medicine_by_id, get_low_stock_medicines,
    get_expiring_medicines, update_medicine_stock, execute_query
)

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/medicines', methods=['GET'])
@token_required
def get_medicines(current_user):
    """Get all medicines"""
    medicines = get_all_medicines()
    
    return jsonify({
        'medicines': medicines,
        'count': len(medicines)
    }), 200

@inventory_bp.route('/medicines/<int:medicine_id>', methods=['GET'])
@token_required
def get_medicine(current_user, medicine_id):
    """Get medicine by ID"""
    medicine = get_medicine_by_id(medicine_id)
    
    if not medicine:
        return jsonify({'error': 'Medicine not found'}), 404
    
    return jsonify({'medicine': medicine}), 200

@inventory_bp.route('/medicines', methods=['POST'])
@token_required
@role_required(['admin', 'manager'])
def create_medicine(current_user):
    """Create new medicine"""
    data = request.get_json()
    
    required_fields = ['medicine_name', 'disease_id', 'current_stock', 
                      'reorder_level', 'unit_price', 'supplier_id', 'expiry_date']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    query = '''
        INSERT INTO medicines 
        (medicine_name, disease_id, current_stock, reorder_level, unit_price, 
         supplier_id, expiry_date, batch_number, storage_location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    medicine_id = execute_query(query, (
        data['medicine_name'],
        data['disease_id'],
        data['current_stock'],
        data['reorder_level'],
        data['unit_price'],
        data['supplier_id'],
        data['expiry_date'],
        data.get('batch_number', ''),
        data.get('storage_location', '')
    ))
    
    # Log action
    log_action(current_user['user_id'], 'create', 'medicines', medicine_id, 
              f"Created medicine: {data['medicine_name']}")
    
    return jsonify({
        'message': 'Medicine created successfully',
        'medicine_id': medicine_id
    }), 201

@inventory_bp.route('/medicines/<int:medicine_id>', methods=['PUT'])
@token_required
@role_required(['admin', 'manager', 'staff'])
def update_medicine(current_user, medicine_id):
    """Update medicine"""
    medicine = get_medicine_by_id(medicine_id)
    if not medicine:
        return jsonify({'error': 'Medicine not found'}), 404
    
    data = request.get_json()
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    allowed_fields = ['medicine_name', 'current_stock', 'reorder_level', 
                     'unit_price', 'supplier_id', 'expiry_date', 
                     'batch_number', 'storage_location']
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = ?")
            params.append(data[field])
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
    
    params.append(medicine_id)
    query = f"UPDATE medicines SET {', '.join(update_fields)} WHERE medicine_id = ?"
    
    execute_query(query, tuple(params))
    
    # Log action
    log_action(current_user['user_id'], 'update', 'medicines', medicine_id,
              f"Updated medicine: {medicine['medicine_name']}")
    
    return jsonify({'message': 'Medicine updated successfully'}), 200

@inventory_bp.route('/medicines/<int:medicine_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_medicine(current_user, medicine_id):
    """Delete medicine (admin only)"""
    medicine = get_medicine_by_id(medicine_id)
    if not medicine:
        return jsonify({'error': 'Medicine not found'}), 404
    
    query = "DELETE FROM medicines WHERE medicine_id = ?"
    execute_query(query, (medicine_id,))
    
    # Log action
    log_action(current_user['user_id'], 'delete', 'medicines', medicine_id,
              f"Deleted medicine: {medicine['medicine_name']}")
    
    return jsonify({'message': 'Medicine deleted successfully'}), 200

@inventory_bp.route('/low-stock', methods=['GET'])
@token_required
def get_low_stock(current_user):
    """Get medicines with low stock"""
    low_stock = get_low_stock_medicines()
    
    return jsonify({
        'medicines': low_stock,
        'count': len(low_stock)
    }), 200

@inventory_bp.route('/expiring', methods=['GET'])
@token_required
def get_expiring(current_user):
    """Get expiring medicines"""
    days = request.args.get('days', 90, type=int)
    expiring = get_expiring_medicines(days)
    
    return jsonify({
        'medicines': expiring,
        'count': len(expiring)
    }), 200

@inventory_bp.route('/medicines/<int:medicine_id>/stock', methods=['PUT'])
@token_required
@role_required(['admin', 'manager', 'staff'])
def update_stock(current_user, medicine_id):
    """Update medicine stock"""
    data = request.get_json()
    
    if 'quantity' not in data or 'operation' not in data:
        return jsonify({'error': 'Quantity and operation required'}), 400
    
    quantity = data['quantity']
    operation = data['operation']  # 'add', 'subtract', or 'set'
    
    if operation not in ['add', 'subtract', 'set']:
        return jsonify({'error': 'Invalid operation'}), 400
    
    success = update_medicine_stock(medicine_id, quantity, operation)
    
    if not success:
        return jsonify({'error': 'Failed to update stock'}), 400
    
    # Log action
    log_action(current_user['user_id'], 'update_stock', 'medicines', medicine_id,
              f"Stock {operation}: {quantity}")
    
    return jsonify({'message': 'Stock updated successfully'}), 200
