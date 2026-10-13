"""
Generate synthetic datasets for the Outbreak-Linked Smart Drug Inventory System
This script creates realistic training data for ML models
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Create data directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'raw')
os.makedirs(RAW_DATA_DIR, exist_ok=True)

print("🔄 Generating synthetic datasets...")

# ============================================================================
# 1. DISEASE OUTBREAK DATA
# ============================================================================
print("\n📊 Generating Disease Outbreak Data...")

diseases = [
    'Influenza', 'Dengue', 'Malaria', 'Cholera', 'Typhoid',
    'COVID-19', 'Tuberculosis', 'Hepatitis A', 'Measles', 'Chickenpox'
]

locations = [
    {'country': 'India', 'state': 'Maharashtra', 'city': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
    {'country': 'India', 'state': 'Delhi', 'city': 'New Delhi', 'lat': 28.6139, 'lon': 77.2090},
    {'country': 'India', 'state': 'Karnataka', 'city': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946},
    {'country': 'India', 'state': 'Tamil Nadu', 'city': 'Chennai', 'lat': 13.0827, 'lon': 80.2707},
    {'country': 'India', 'state': 'West Bengal', 'city': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639},
    {'country': 'India', 'state': 'Gujarat', 'city': 'Ahmedabad', 'lat': 23.0225, 'lon': 72.5714},
    {'country': 'India', 'state': 'Rajasthan', 'city': 'Jaipur', 'lat': 26.9124, 'lon': 75.7873},
    {'country': 'India', 'state': 'Uttar Pradesh', 'city': 'Lucknow', 'lat': 26.8467, 'lon': 80.9462},
    {'country': 'USA', 'state': 'California', 'city': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
    {'country': 'USA', 'state': 'New York', 'city': 'New York City', 'lat': 40.7128, 'lon': -74.0060},
]

severity_levels = ['Low', 'Medium', 'High', 'Critical']

# Generate outbreak data for past 3 years
outbreak_data = []
start_date = datetime.now() - timedelta(days=3*365)

for _ in range(2000):  # Generate 2000 outbreak records
    disease = random.choice(diseases)
    location = random.choice(locations)
    outbreak_date = start_date + timedelta(days=random.randint(0, 3*365))
    
    # Add seasonality patterns
    month = outbreak_date.month
    if disease in ['Influenza', 'COVID-19']:
        # More common in winter months
        if month in [11, 12, 1, 2]:
            cases = random.randint(100, 1000)
        else:
            cases = random.randint(10, 200)
    elif disease in ['Dengue', 'Malaria']:
        # More common in monsoon
        if month in [6, 7, 8, 9]:
            cases = random.randint(150, 800)
        else:
            cases = random.randint(20, 150)
    else:
        cases = random.randint(50, 500)
    
    # Determine severity based on cases
    if cases > 700:
        severity = 'Critical'
    elif cases > 400:
        severity = 'High'
    elif cases > 150:
        severity = 'Medium'
    else:
        severity = 'Low'
    
    duration = random.randint(7, 90)  # Duration in days
    
    outbreak_data.append({
        'disease_name': disease,
        'country': location['country'],
        'state': location['state'],
        'city': location['city'],
        'latitude': location['lat'],
        'longitude': location['lon'],
        'outbreak_date': outbreak_date.strftime('%Y-%m-%d'),
        'number_of_cases': cases,
        'severity_level': severity,
        'duration_days': duration,
        'month': month,
        'year': outbreak_date.year,
        'quarter': (month - 1) // 3 + 1
    })

outbreak_df = pd.DataFrame(outbreak_data)
outbreak_df.to_csv(os.path.join(RAW_DATA_DIR, 'disease_outbreaks.csv'), index=False)
print(f"✅ Generated {len(outbreak_df)} outbreak records")

# ============================================================================
# 2. MEDICINE INVENTORY DATA
# ============================================================================
print("\n💊 Generating Medicine Inventory Data...")

medicines = [
    {'name': 'Oseltamivir', 'disease': 'Influenza', 'unit_price': 150},
    {'name': 'Paracetamol', 'disease': 'Influenza', 'unit_price': 5},
    {'name': 'Dengue NS1 Test Kit', 'disease': 'Dengue', 'unit_price': 200},
    {'name': 'Platelet Concentrate', 'disease': 'Dengue', 'unit_price': 500},
    {'name': 'Chloroquine', 'disease': 'Malaria', 'unit_price': 50},
    {'name': 'Artemisinin', 'disease': 'Malaria', 'unit_price': 120},
    {'name': 'ORS Solution', 'disease': 'Cholera', 'unit_price': 10},
    {'name': 'Doxycycline', 'disease': 'Cholera', 'unit_price': 80},
    {'name': 'Azithromycin', 'disease': 'Typhoid', 'unit_price': 100},
    {'name': 'Ceftriaxone', 'disease': 'Typhoid', 'unit_price': 150},
    {'name': 'Remdesivir', 'disease': 'COVID-19', 'unit_price': 5000},
    {'name': 'Dexamethasone', 'disease': 'COVID-19', 'unit_price': 50},
    {'name': 'Isoniazid', 'disease': 'Tuberculosis', 'unit_price': 30},
    {'name': 'Rifampicin', 'disease': 'Tuberculosis', 'unit_price': 60},
    {'name': 'Hepatitis A Vaccine', 'disease': 'Hepatitis A', 'unit_price': 800},
    {'name': 'MMR Vaccine', 'disease': 'Measles', 'unit_price': 600},
    {'name': 'Acyclovir', 'disease': 'Chickenpox', 'unit_price': 200},
]

suppliers = [
    'PharmaCorp India', 'MediSupply Ltd', 'HealthCare Distributors',
    'Global Pharma', 'MedTech Solutions', 'BioMed Suppliers'
]

medicine_inventory = []
for i, med in enumerate(medicines):
    current_stock = random.randint(100, 5000)
    reorder_level = random.randint(50, 500)
    expiry_date = datetime.now() + timedelta(days=random.randint(30, 730))
    
    medicine_inventory.append({
        'medicine_id': i + 1,
        'medicine_name': med['name'],
        'disease_treated': med['disease'],
        'current_stock': current_stock,
        'reorder_level': reorder_level,
        'unit_price': med['unit_price'],
        'supplier_id': random.randint(1, len(suppliers)),
        'supplier_name': random.choice(suppliers),
        'expiry_date': expiry_date.strftime('%Y-%m-%d'),
        'batch_number': f'BATCH{random.randint(1000, 9999)}',
        'storage_location': f'Warehouse-{random.choice(["A", "B", "C"])}'
    })

medicine_df = pd.DataFrame(medicine_inventory)
medicine_df.to_csv(os.path.join(RAW_DATA_DIR, 'medicine_inventory.csv'), index=False)
print(f"✅ Generated {len(medicine_df)} medicine records")

# ============================================================================
# 3. HISTORICAL MEDICINE USAGE DATA
# ============================================================================
print("\n📈 Generating Historical Medicine Usage Data...")

usage_data = []
for _ in range(5000):  # Generate 5000 usage records
    medicine = random.choice(medicine_inventory)
    location = random.choice(locations)
    usage_date = start_date + timedelta(days=random.randint(0, 3*365))
    
    # Usage correlates with outbreak data
    month = usage_date.month
    disease = medicine['disease_treated']
    
    # Seasonal patterns
    if disease in ['Influenza', 'COVID-19'] and month in [11, 12, 1, 2]:
        quantity = random.randint(100, 500)
    elif disease in ['Dengue', 'Malaria'] and month in [6, 7, 8, 9]:
        quantity = random.randint(80, 400)
    else:
        quantity = random.randint(10, 150)
    
    effectiveness = random.uniform(0.75, 0.98)  # 75-98% effectiveness
    
    usage_data.append({
        'medicine_id': medicine['medicine_id'],
        'medicine_name': medicine['medicine_name'],
        'disease_name': disease,
        'country': location['country'],
        'state': location['state'],
        'city': location['city'],
        'quantity_used': quantity,
        'usage_date': usage_date.strftime('%Y-%m-%d'),
        'effectiveness_rate': round(effectiveness, 2),
        'month': month,
        'year': usage_date.year,
        'quarter': (month - 1) // 3 + 1
    })

usage_df = pd.DataFrame(usage_data)
usage_df.to_csv(os.path.join(RAW_DATA_DIR, 'medicine_usage_history.csv'), index=False)
print(f"✅ Generated {len(usage_df)} usage records")

# ============================================================================
# 4. SUPPLY CHAIN DATA
# ============================================================================
print("\n🚚 Generating Supply Chain Data...")

supply_chain_data = []
for i in range(1000):  # Generate 1000 order records
    order_date = start_date + timedelta(days=random.randint(0, 3*365))
    delivery_time = random.randint(3, 30)  # 3-30 days delivery
    delivery_date = order_date + timedelta(days=delivery_time)
    
    medicine = random.choice(medicine_inventory)
    location = random.choice(locations)
    
    status_options = ['delivered', 'delivered', 'delivered', 'shipped', 'pending']  # More delivered
    status = random.choice(status_options)
    
    if status == 'pending':
        delivery_date = None
        delivery_time = None
    
    supply_chain_data.append({
        'order_id': f'ORD{str(i+1).zfill(6)}',
        'medicine_id': medicine['medicine_id'],
        'medicine_name': medicine['medicine_name'],
        'supplier_id': medicine['supplier_id'],
        'supplier_name': medicine['supplier_name'],
        'quantity_ordered': random.randint(100, 2000),
        'order_date': order_date.strftime('%Y-%m-%d'),
        'expected_delivery_date': delivery_date.strftime('%Y-%m-%d') if delivery_date else None,
        'delivery_time_days': delivery_time,
        'destination_city': location['city'],
        'destination_state': location['state'],
        'status': status,
        'total_cost': medicine['unit_price'] * random.randint(100, 2000)
    })

supply_df = pd.DataFrame(supply_chain_data)
supply_df.to_csv(os.path.join(RAW_DATA_DIR, 'supply_chain.csv'), index=False)
print(f"✅ Generated {len(supply_df)} supply chain records")

# ============================================================================
# 5. SUPPLIER DATA
# ============================================================================
print("\n🏢 Generating Supplier Data...")

supplier_data = []
for i, supplier in enumerate(suppliers):
    supplier_data.append({
        'supplier_id': i + 1,
        'supplier_name': supplier,
        'contact_email': f'contact@{supplier.lower().replace(" ", "")}.com',
        'contact_phone': f'+91-{random.randint(7000000000, 9999999999)}',
        'address': f'{random.randint(1, 999)} Business Park, {random.choice([loc["city"] for loc in locations])}',
        'rating': round(random.uniform(3.5, 5.0), 1),
        'avg_delivery_time_days': random.randint(5, 20),
        'reliability_score': round(random.uniform(0.80, 0.99), 2)
    })

supplier_df = pd.DataFrame(supplier_data)
supplier_df.to_csv(os.path.join(RAW_DATA_DIR, 'suppliers.csv'), index=False)
print(f"✅ Generated {len(supplier_df)} supplier records")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("✅ DATASET GENERATION COMPLETE!")
print("="*60)
print(f"\n📁 Datasets saved to: {RAW_DATA_DIR}\n")
print("Generated Files:")
print(f"  1. disease_outbreaks.csv       - {len(outbreak_df)} records")
print(f"  2. medicine_inventory.csv      - {len(medicine_df)} records")
print(f"  3. medicine_usage_history.csv  - {len(usage_df)} records")
print(f"  4. supply_chain.csv            - {len(supply_df)} records")
print(f"  5. suppliers.csv               - {len(supplier_df)} records")
print("\n🎯 Next Step: Run preprocess_data.py to prepare data for ML training")
