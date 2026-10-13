"""
Database Initialization Script
Creates SQLite database with all required tables and sample data
"""
import sqlite3
import os
from datetime import datetime, timedelta
import random
import bcrypt

# Database path
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, 'inventory.db')

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_database():
    """Create database and all tables"""
    print("🔄 Initializing database...")
    
    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("   Removed existing database")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ========================================================================
    # CREATE TABLES
    # ========================================================================
    
    # Users Table
    cursor.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ Created users table")
    
    # Diseases Table
    cursor.execute('''
    CREATE TABLE diseases (
        disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease_name TEXT NOT NULL,
        symptoms TEXT,
        severity TEXT,
        category TEXT
    )
    ''')
    print("✅ Created diseases table")
    
    # Medicines Table
    cursor.execute('''
    CREATE TABLE medicines (
        medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_name TEXT NOT NULL,
        disease_id INTEGER,
        current_stock INTEGER,
        reorder_level INTEGER,
        unit_price REAL,
        supplier_id INTEGER,
        expiry_date DATE,
        batch_number TEXT,
        storage_location TEXT,
        FOREIGN KEY (disease_id) REFERENCES diseases(disease_id)
    )
    ''')
    print("✅ Created medicines table")
    
    # Outbreak Predictions Table
    cursor.execute('''
    CREATE TABLE outbreak_predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease_id INTEGER,
        location TEXT,
        state TEXT,
        latitude REAL,
        longitude REAL,
        predicted_date DATE,
        probability REAL,
        severity_level TEXT,
        predicted_cases INTEGER,
        risk_score REAL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (disease_id) REFERENCES diseases(disease_id)
    )
    ''')
    print("✅ Created outbreak_predictions table")
    
    # Medicine Usage History
    cursor.execute('''
    CREATE TABLE medicine_usage (
        usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        disease_id INTEGER,
        location TEXT,
        state TEXT,
        quantity_used INTEGER,
        usage_date DATE,
        effectiveness_rate REAL,
        FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
        FOREIGN KEY (disease_id) REFERENCES diseases(disease_id)
    )
    ''')
    print("✅ Created medicine_usage table")
    
    # Orders Table
    cursor.execute('''
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        supplier_id INTEGER,
        quantity INTEGER,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expected_delivery DATE,
        actual_delivery DATE,
        status TEXT DEFAULT 'pending',
        total_cost REAL,
        created_by INTEGER,
        approved_by INTEGER,
        notes TEXT,
        FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    )
    ''')
    print("✅ Created orders table")
    
    # Suppliers Table
    cursor.execute('''
    CREATE TABLE suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        contact_email TEXT,
        contact_phone TEXT,
        address TEXT,
        rating REAL,
        avg_delivery_time INTEGER,
        reliability_score REAL
    )
    ''')
    print("✅ Created suppliers table")
    
    # Notifications Table
    cursor.execute('''
    CREATE TABLE notifications (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id INTEGER,
        notification_type TEXT,
        title TEXT,
        message TEXT,
        sent_to TEXT,
        sent_at TIMESTAMP,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'medium',
        FOREIGN KEY (prediction_id) REFERENCES outbreak_predictions(prediction_id)
    )
    ''')
    print("✅ Created notifications table")
    
    # Audit Logs
    cursor.execute('''
    CREATE TABLE audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        table_affected TEXT,
        record_id INTEGER,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    print("✅ Created audit_logs table")
    
    conn.commit()
    
    # ========================================================================
    # INSERT SAMPLE DATA
    # ========================================================================
    
    print("\n📝 Inserting sample data...")
    
    # Insert Users
    users = [
        ('admin', 'admin@health.com', hash_password('admin123'), 'admin'),
        ('manager', 'manager@health.com', hash_password('manager123'), 'manager'),
        ('staff', 'staff@health.com', hash_password('staff123'), 'staff'),
        ('viewer', 'viewer@health.com', hash_password('viewer123'), 'viewer'),
    ]
    cursor.executemany('INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)', users)
    print("✅ Inserted users")
    
    # Insert Diseases
    diseases = [
        ('Influenza', 'Fever, cough, body ache, fatigue', 'Medium', 'Viral Infection'),
        ('Dengue', 'High fever, severe headache, joint pain, rash', 'High', 'Vector-borne Disease'),
        ('Malaria', 'Fever, chills, sweating, headache', 'High', 'Parasitic Disease'),
        ('Cholera', 'Severe diarrhea, dehydration, vomiting', 'Critical', 'Waterborne Disease'),
        ('Typhoid', 'Prolonged fever, weakness, abdominal pain', 'High', 'Bacterial Infection'),
        ('COVID-19', 'Fever, dry cough, breathing difficulty', 'Critical', 'Viral Infection'),
        ('Tuberculosis', 'Persistent cough, weight loss, night sweats', 'High', 'Bacterial Infection'),
        ('Hepatitis A', 'Jaundice, fatigue, abdominal pain', 'Medium', 'Viral Infection'),
        ('Measles', 'Fever, rash, cough, red eyes', 'Medium', 'Viral Infection'),
        ('Chickenpox', 'Itchy rash, fever, tiredness', 'Low', 'Viral Infection'),
    ]
    cursor.executemany('INSERT INTO diseases (disease_name, symptoms, severity, category) VALUES (?, ?, ?, ?)', diseases)
    print("✅ Inserted diseases")
    
    # Insert Suppliers
    suppliers = [
        ('PharmaCorp India', 'contact@pharmacorp.com', '+91-9876543210', 'Mumbai Business Park, Mumbai', 4.5, 7, 0.95),
        ('MediSupply Ltd', 'info@medisupply.com', '+91-9876543211', 'Healthcare Plaza, Delhi', 4.2, 10, 0.90),
        ('HealthCare Distributors', 'sales@healthcare.com', '+91-9876543212', 'Medical District, Bangalore', 4.7, 5, 0.97),
        ('Global Pharma', 'contact@globalpharma.com', '+91-9876543213', 'Pharma Hub, Chennai', 4.0, 12, 0.88),
        ('MedTech Solutions', 'info@medtech.com', '+91-9876543214', 'Tech Park, Hyderabad', 4.6, 6, 0.96),
        ('BioMed Suppliers', 'sales@biomed.com', '+91-9876543215', 'Bio Complex, Pune', 4.3, 8, 0.92),
    ]
    cursor.executemany('''INSERT INTO suppliers (supplier_name, contact_email, contact_phone, address, 
                          rating, avg_delivery_time, reliability_score) VALUES (?, ?, ?, ?, ?, ?, ?)''', suppliers)
    print("✅ Inserted suppliers")
    
    # Insert Medicines
    medicines = [
        ('Oseltamivir', 1, 2500, 500, 150.00, 1, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'), 'BATCH1001', 'Warehouse-A'),
        ('Paracetamol', 1, 5000, 1000, 5.00, 1, (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d'), 'BATCH1002', 'Warehouse-A'),
        ('Dengue NS1 Test Kit', 2, 800, 200, 200.00, 2, (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'), 'BATCH2001', 'Warehouse-B'),
        ('Platelet Concentrate', 2, 300, 100, 500.00, 3, (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'), 'BATCH2002', 'Warehouse-C'),
        ('Chloroquine', 3, 1500, 300, 50.00, 1, (datetime.now() + timedelta(days=540)).strftime('%Y-%m-%d'), 'BATCH3001', 'Warehouse-A'),
        ('Artemisinin', 3, 1200, 250, 120.00, 2, (datetime.now() + timedelta(days=450)).strftime('%Y-%m-%d'), 'BATCH3002', 'Warehouse-A'),
        ('ORS Solution', 4, 3000, 500, 10.00, 4, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'), 'BATCH4001', 'Warehouse-B'),
        ('Doxycycline', 4, 1000, 200, 80.00, 1, (datetime.now() + timedelta(days=600)).strftime('%Y-%m-%d'), 'BATCH4002', 'Warehouse-A'),
        ('Azithromycin', 5, 1800, 350, 100.00, 2, (datetime.now() + timedelta(days=480)).strftime('%Y-%m-%d'), 'BATCH5001', 'Warehouse-A'),
        ('Ceftriaxone', 5, 1500, 300, 150.00, 3, (datetime.now() + timedelta(days=420)).strftime('%Y-%m-%d'), 'BATCH5002', 'Warehouse-B'),
        ('Remdesivir', 6, 500, 100, 5000.00, 5, (datetime.now() + timedelta(days=270)).strftime('%Y-%m-%d'), 'BATCH6001', 'Warehouse-C'),
        ('Dexamethasone', 6, 2000, 400, 50.00, 1, (datetime.now() + timedelta(days=540)).strftime('%Y-%m-%d'), 'BATCH6002', 'Warehouse-A'),
        ('Isoniazid', 7, 2500, 500, 30.00, 4, (datetime.now() + timedelta(days=600)).strftime('%Y-%m-%d'), 'BATCH7001', 'Warehouse-B'),
        ('Rifampicin', 7, 2200, 450, 60.00, 4, (datetime.now() + timedelta(days=600)).strftime('%Y-%m-%d'), 'BATCH7002', 'Warehouse-B'),
        ('Hepatitis A Vaccine', 8, 600, 150, 800.00, 5, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'), 'BATCH8001', 'Warehouse-C'),
        ('MMR Vaccine', 9, 800, 200, 600.00, 5, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'), 'BATCH9001', 'Warehouse-C'),
        ('Acyclovir', 10, 1200, 250, 200.00, 2, (datetime.now() + timedelta(days=480)).strftime('%Y-%m-%d'), 'BATCH1003', 'Warehouse-A'),
    ]
    cursor.executemany('''INSERT INTO medicines (medicine_name, disease_id, current_stock, reorder_level, 
                          unit_price, supplier_id, expiry_date, batch_number, storage_location) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', medicines)
    print("✅ Inserted medicines")
    
    # Insert some sample outbreak predictions
    locations = [
        ('Mumbai', 'Maharashtra', 19.0760, 72.8777),
        ('Delhi', 'Delhi', 28.6139, 77.2090),
        ('Bangalore', 'Karnataka', 12.9716, 77.5946),
        ('Chennai', 'Tamil Nadu', 13.0827, 80.2707),
    ]
    
    predictions = []
    for i in range(10):
        disease_id = random.randint(1, 10)
        location = random.choice(locations)
        pred_date = (datetime.now() + timedelta(days=random.randint(7, 90))).strftime('%Y-%m-%d')
        probability = round(random.uniform(0.5, 0.95), 2)
        severity = random.choice(['Low', 'Medium', 'High', 'Critical'])
        cases = random.randint(50, 800)
        risk_score = probability * 100
        
        predictions.append((disease_id, location[0], location[1], location[2], location[3], 
                          pred_date, probability, severity, cases, risk_score, 'pending'))
    
    cursor.executemany('''INSERT INTO outbreak_predictions (disease_id, location, state, latitude, longitude,
                          predicted_date, probability, severity_level, predicted_cases, risk_score, status)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', predictions)
    print("✅ Inserted sample predictions")
    
    # Insert some sample orders
    orders = []
    for i in range(5):
        medicine_id = random.randint(1, 17)
        supplier_id = random.randint(1, 6)
        quantity = random.randint(100, 1000)
        order_date = datetime.now() - timedelta(days=random.randint(1, 30))
        expected_delivery = order_date + timedelta(days=random.randint(5, 15))
        status = random.choice(['pending', 'confirmed', 'shipped', 'delivered'])
        total_cost = quantity * random.uniform(10, 500)
        
        orders.append((medicine_id, supplier_id, quantity, order_date.strftime('%Y-%m-%d %H:%M:%S'),
                      expected_delivery.strftime('%Y-%m-%d'), status, total_cost, 1))
    
    cursor.executemany('''INSERT INTO orders (medicine_id, supplier_id, quantity, order_date, 
                          expected_delivery, status, total_cost, created_by)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', orders)
    print("✅ Inserted sample orders")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE INITIALIZATION COMPLETE!")
    print("="*60)
    print(f"\n📁 Database created at: {DB_PATH}")
    print("\n🔑 Default User Credentials:")
    print("   Admin:   admin@health.com   / admin123")
    print("   Manager: manager@health.com / manager123")
    print("   Staff:   staff@health.com   / staff123")
    print("   Viewer:  viewer@health.com  / viewer123")
    print("\n🎯 Database is ready for use!")

if __name__ == '__main__':
    create_database()
