"""
Data Utilities
Helper functions for database operations and data processing
"""
import sqlite3
import os
from datetime import datetime, timedelta
import json

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'inventory.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def dict_from_row(row):
    """Convert SQLite row to dictionary"""
    return dict(zip(row.keys(), row)) if row else None

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute SQL query and return results"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    if fetch_one:
        result = dict_from_row(cursor.fetchone())
    elif fetch_all:
        result = [dict_from_row(row) for row in cursor.fetchall()]
    else:
        conn.commit()
        result = cursor.lastrowid
    
    conn.close()
    return result

def paginate_results(query, params=None, page=1, per_page=20):
    """Paginate query results"""
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM ({query})"
    total = execute_query(count_query, params, fetch_one=True)['total']
    
    # Get paginated results
    paginated_query = f"{query} LIMIT ? OFFSET ?"
    if params:
        params = list(params) + [per_page, offset]
    else:
        params = [per_page, offset]
    
    results = execute_query(paginated_query, params, fetch_all=True)
    
    return {
        'data': results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }

# ============================================================================
# DISEASE OPERATIONS
# ============================================================================

def get_all_diseases():
    """Get all diseases"""
    query = "SELECT * FROM diseases ORDER BY disease_name"
    return execute_query(query, fetch_all=True)

def get_disease_by_id(disease_id):
    """Get disease by ID"""
    query = "SELECT * FROM diseases WHERE disease_id = ?"
    return execute_query(query, (disease_id,), fetch_one=True)

def get_disease_by_name(disease_name):
    """Get disease by name"""
    query = "SELECT * FROM diseases WHERE disease_name = ?"
    return execute_query(query, (disease_name,), fetch_one=True)

# ============================================================================
# MEDICINE OPERATIONS
# ============================================================================

def get_all_medicines():
    """Get all medicines with disease info"""
    query = '''
        SELECT m.*, d.disease_name, s.supplier_name
        FROM medicines m
        LEFT JOIN diseases d ON m.disease_id = d.disease_id
        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
        ORDER BY m.medicine_name
    '''
    return execute_query(query, fetch_all=True)

def get_medicine_by_id(medicine_id):
    """Get medicine by ID"""
    query = '''
        SELECT m.*, d.disease_name, s.supplier_name
        FROM medicines m
        LEFT JOIN diseases d ON m.disease_id = d.disease_id
        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
        WHERE m.medicine_id = ?
    '''
    return execute_query(query, (medicine_id,), fetch_one=True)

def get_low_stock_medicines(threshold_days=30):
    """Get medicines with low stock"""
    query = '''
        SELECT m.*, d.disease_name,
               CASE 
                   WHEN m.current_stock < m.reorder_level THEN 'Critical'
                   WHEN m.current_stock < m.reorder_level * 1.5 THEN 'Low'
                   ELSE 'Adequate'
               END as stock_status
        FROM medicines m
        LEFT JOIN diseases d ON m.disease_id = d.disease_id
        WHERE m.current_stock < m.reorder_level * 1.5
        ORDER BY m.current_stock ASC
    '''
    return execute_query(query, fetch_all=True)

def get_expiring_medicines(days=90):
    """Get medicines expiring within specified days"""
    expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    query = '''
        SELECT m.*, d.disease_name,
               julianday(m.expiry_date) - julianday('now') as days_until_expiry
        FROM medicines m
        LEFT JOIN diseases d ON m.disease_id = d.disease_id
        WHERE m.expiry_date <= ?
        ORDER BY m.expiry_date ASC
    '''
    return execute_query(query, (expiry_date,), fetch_all=True)

def update_medicine_stock(medicine_id, quantity, operation='add'):
    """Update medicine stock"""
    medicine = get_medicine_by_id(medicine_id)
    if not medicine:
        return False
    
    current_stock = medicine['current_stock']
    
    if operation == 'add':
        new_stock = current_stock + quantity
    elif operation == 'subtract':
        new_stock = max(0, current_stock - quantity)
    else:
        new_stock = quantity
    
    query = "UPDATE medicines SET current_stock = ? WHERE medicine_id = ?"
    execute_query(query, (new_stock, medicine_id))
    return True

# ============================================================================
# OUTBREAK PREDICTION OPERATIONS
# ============================================================================

def get_all_predictions(status=None):
    """Get all outbreak predictions"""
    if status:
        query = '''
            SELECT p.*, d.disease_name
            FROM outbreak_predictions p
            LEFT JOIN diseases d ON p.disease_id = d.disease_id
            WHERE p.status = ?
            ORDER BY p.predicted_date DESC
        '''
        return execute_query(query, (status,), fetch_all=True)
    else:
        query = '''
            SELECT p.*, d.disease_name
            FROM outbreak_predictions p
            LEFT JOIN diseases d ON p.disease_id = d.disease_id
            ORDER BY p.predicted_date DESC
        '''
        return execute_query(query, fetch_all=True)

def get_prediction_by_id(prediction_id):
    """Get prediction by ID"""
    query = '''
        SELECT p.*, d.disease_name
        FROM outbreak_predictions p
        LEFT JOIN diseases d ON p.disease_id = d.disease_id
        WHERE p.prediction_id = ?
    '''
    return execute_query(query, (prediction_id,), fetch_one=True)

def create_prediction(disease_id, location, state, latitude, longitude, 
                     predicted_date, probability, severity_level, 
                     predicted_cases, risk_score):
    """Create new outbreak prediction"""
    query = '''
        INSERT INTO outbreak_predictions 
        (disease_id, location, state, latitude, longitude, predicted_date, 
         probability, severity_level, predicted_cases, risk_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    '''
    return execute_query(query, (disease_id, location, state, latitude, longitude,
                                 predicted_date, probability, severity_level,
                                 predicted_cases, risk_score))

def get_high_risk_predictions(threshold=0.7):
    """Get high-risk outbreak predictions"""
    query = '''
        SELECT p.*, d.disease_name
        FROM outbreak_predictions p
        LEFT JOIN diseases d ON p.disease_id = d.disease_id
        WHERE p.probability >= ? AND p.status = 'pending'
        ORDER BY p.probability DESC, p.predicted_date ASC
    '''
    return execute_query(query, (threshold,), fetch_all=True)

# ============================================================================
# ORDER OPERATIONS
# ============================================================================

def get_all_orders(status=None):
    """Get all orders"""
    if status:
        query = '''
            SELECT o.*, m.medicine_name, s.supplier_name, u.username as created_by_name
            FROM orders o
            LEFT JOIN medicines m ON o.medicine_id = m.medicine_id
            LEFT JOIN suppliers s ON o.supplier_id = s.supplier_id
            LEFT JOIN users u ON o.created_by = u.user_id
            WHERE o.status = ?
            ORDER BY o.order_date DESC
        '''
        return execute_query(query, (status,), fetch_all=True)
    else:
        query = '''
            SELECT o.*, m.medicine_name, s.supplier_name, u.username as created_by_name
            FROM orders o
            LEFT JOIN medicines m ON o.medicine_id = m.medicine_id
            LEFT JOIN suppliers s ON o.supplier_id = s.supplier_id
            LEFT JOIN users u ON o.created_by = u.user_id
            ORDER BY o.order_date DESC
        '''
        return execute_query(query, fetch_all=True)

def get_order_by_id(order_id):
    """Get order by ID"""
    query = '''
        SELECT o.*, m.medicine_name, s.supplier_name, u.username as created_by_name
        FROM orders o
        LEFT JOIN medicines m ON o.medicine_id = m.medicine_id
        LEFT JOIN suppliers s ON o.supplier_id = s.supplier_id
        LEFT JOIN users u ON o.created_by = u.user_id
        WHERE o.order_id = ?
    '''
    return execute_query(query, (order_id,), fetch_one=True)

def create_order(medicine_id, supplier_id, quantity, expected_delivery, 
                total_cost, created_by, notes=None):
    """Create new order"""
    query = '''
        INSERT INTO orders 
        (medicine_id, supplier_id, quantity, expected_delivery, total_cost, created_by, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    '''
    return execute_query(query, (medicine_id, supplier_id, quantity, 
                                 expected_delivery, total_cost, created_by, notes))

def update_order_status(order_id, status, approved_by=None):
    """Update order status"""
    if approved_by:
        query = "UPDATE orders SET status = ?, approved_by = ? WHERE order_id = ?"
        execute_query(query, (status, approved_by, order_id))
    else:
        query = "UPDATE orders SET status = ? WHERE order_id = ?"
        execute_query(query, (status, order_id))
    
    # If delivered, update medicine stock
    if status == 'delivered':
        order = get_order_by_id(order_id)
        if order:
            update_medicine_stock(order['medicine_id'], order['quantity'], 'add')
            
            # Update actual delivery date
            query = "UPDATE orders SET actual_delivery = ? WHERE order_id = ?"
            execute_query(query, (datetime.now().strftime('%Y-%m-%d'), order_id))
    
    return True

# ============================================================================
# SUPPLIER OPERATIONS
# ============================================================================

def get_all_suppliers():
    """Get all suppliers"""
    query = "SELECT * FROM suppliers ORDER BY supplier_name"
    return execute_query(query, fetch_all=True)

def get_supplier_by_id(supplier_id):
    """Get supplier by ID"""
    query = "SELECT * FROM suppliers WHERE supplier_id = ?"
    return execute_query(query, (supplier_id,), fetch_one=True)

# ============================================================================
# NOTIFICATION OPERATIONS
# ============================================================================

def create_notification(prediction_id, notification_type, title, message, 
                       sent_to, priority='medium'):
    """Create new notification"""
    query = '''
        INSERT INTO notifications 
        (prediction_id, notification_type, title, message, sent_to, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    '''
    return execute_query(query, (prediction_id, notification_type, title, 
                                 message, sent_to, priority))

def get_pending_notifications():
    """Get pending notifications"""
    query = "SELECT * FROM notifications WHERE status = 'pending' ORDER BY notification_id"
    return execute_query(query, fetch_all=True)

def mark_notification_sent(notification_id):
    """Mark notification as sent"""
    query = "UPDATE notifications SET status = 'sent', sent_at = ? WHERE notification_id = ?"
    execute_query(query, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notification_id))

# ============================================================================
# DASHBOARD STATISTICS
# ============================================================================

def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = {}
    
    # Total medicines
    stats['total_medicines'] = execute_query(
        "SELECT COUNT(*) as count FROM medicines", fetch_one=True)['count']
    
    # Low stock count
    stats['low_stock_count'] = execute_query(
        "SELECT COUNT(*) as count FROM medicines WHERE current_stock < reorder_level",
        fetch_one=True)['count']
    
    # Pending predictions
    stats['pending_predictions'] = execute_query(
        "SELECT COUNT(*) as count FROM outbreak_predictions WHERE status = 'pending'",
        fetch_one=True)['count']
    
    # High risk predictions
    stats['high_risk_predictions'] = execute_query(
        "SELECT COUNT(*) as count FROM outbreak_predictions WHERE probability >= 0.7 AND status = 'pending'",
        fetch_one=True)['count']
    
    # Pending orders
    stats['pending_orders'] = execute_query(
        "SELECT COUNT(*) as count FROM orders WHERE status = 'pending'",
        fetch_one=True)['count']
    
    # Total inventory value
    stats['total_inventory_value'] = execute_query(
        "SELECT SUM(current_stock * unit_price) as total FROM medicines",
        fetch_one=True)['total'] or 0
    
    return stats
