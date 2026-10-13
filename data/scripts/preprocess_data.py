"""
Data Preprocessing Pipeline for ML Model Training
Cleans, transforms, and prepares data for outbreak prediction and demand forecasting
"""
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os

print("🔄 Starting Data Preprocessing Pipeline...")

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'processed')
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# ============================================================================
# 1. LOAD RAW DATA
# ============================================================================
print("\n📂 Loading raw datasets...")

outbreak_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'disease_outbreaks.csv'))
medicine_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'medicine_inventory.csv'))
usage_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'medicine_usage_history.csv'))
supply_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'supply_chain.csv'))

print(f"✅ Loaded outbreak data: {outbreak_df.shape}")
print(f"✅ Loaded medicine data: {medicine_df.shape}")
print(f"✅ Loaded usage data: {usage_df.shape}")
print(f"✅ Loaded supply chain data: {supply_df.shape}")

# ============================================================================
# 2. DATA CLEANING
# ============================================================================
print("\n🧹 Cleaning data...")

# Convert date columns
outbreak_df['outbreak_date'] = pd.to_datetime(outbreak_df['outbreak_date'])
usage_df['usage_date'] = pd.to_datetime(usage_df['usage_date'])
supply_df['order_date'] = pd.to_datetime(supply_df['order_date'])

# Remove duplicates
outbreak_df = outbreak_df.drop_duplicates()
usage_df = usage_df.drop_duplicates()

# Handle missing values
outbreak_df = outbreak_df.fillna(method='ffill')
usage_df = usage_df.fillna(method='ffill')

print("✅ Data cleaning complete")

# ============================================================================
# 3. FEATURE ENGINEERING FOR OUTBREAK PREDICTION
# ============================================================================
print("\n🔧 Engineering features for outbreak prediction...")

# Sort by date
outbreak_df = outbreak_df.sort_values('outbreak_date')

# Create temporal features
outbreak_df['day_of_week'] = outbreak_df['outbreak_date'].dt.dayofweek
outbreak_df['day_of_year'] = outbreak_df['outbreak_date'].dt.dayofyear
outbreak_df['week_of_year'] = outbreak_df['outbreak_date'].dt.isocalendar().week
outbreak_df['is_monsoon'] = outbreak_df['month'].isin([6, 7, 8, 9]).astype(int)
outbreak_df['is_winter'] = outbreak_df['month'].isin([11, 12, 1, 2]).astype(int)

# Create lag features (previous outbreak information)
for disease in outbreak_df['disease_name'].unique():
    disease_mask = outbreak_df['disease_name'] == disease
    outbreak_df.loc[disease_mask, 'prev_cases'] = outbreak_df.loc[disease_mask, 'number_of_cases'].shift(1)
    outbreak_df.loc[disease_mask, 'prev_severity'] = outbreak_df.loc[disease_mask, 'severity_level'].shift(1)
    outbreak_df.loc[disease_mask, 'days_since_last'] = outbreak_df.loc[disease_mask, 'outbreak_date'].diff().dt.days

# Fill NaN values from lag features
outbreak_df['prev_cases'] = outbreak_df['prev_cases'].fillna(0)
outbreak_df['days_since_last'] = outbreak_df['days_since_last'].fillna(365)

# Encode categorical variables
label_encoders = {}
categorical_cols = ['disease_name', 'country', 'state', 'city', 'severity_level', 'prev_severity']

for col in categorical_cols:
    if col in outbreak_df.columns:
        le = LabelEncoder()
        outbreak_df[col + '_encoded'] = le.fit_transform(outbreak_df[col].astype(str))
        label_encoders[col] = le

# Create aggregated features by location
location_stats = outbreak_df.groupby(['state', 'disease_name']).agg({
    'number_of_cases': ['mean', 'std', 'max'],
    'duration_days': 'mean'
}).reset_index()
location_stats.columns = ['state', 'disease_name', 'avg_cases', 'std_cases', 'max_cases', 'avg_duration']

outbreak_df = outbreak_df.merge(location_stats, on=['state', 'disease_name'], how='left')

print("✅ Outbreak features engineered")

# ============================================================================
# 4. PREPARE OUTBREAK PREDICTION DATASET
# ============================================================================
print("\n📊 Preparing outbreak prediction dataset...")

# Select features for prediction
feature_cols = [
    'disease_name_encoded', 'state_encoded', 'month', 'quarter',
    'day_of_week', 'week_of_year', 'is_monsoon', 'is_winter',
    'prev_cases', 'days_since_last', 'avg_cases', 'std_cases', 'max_cases',
    'latitude', 'longitude'
]

target_col = 'number_of_cases'
severity_target = 'severity_level_encoded'

# Remove rows with NaN in critical columns
outbreak_clean = outbreak_df.dropna(subset=feature_cols + [target_col])

X_outbreak = outbreak_clean[feature_cols]
y_outbreak_cases = outbreak_clean[target_col]
y_outbreak_severity = outbreak_clean[severity_target]

# Split data
X_train_out, X_test_out, y_train_cases, y_test_cases = train_test_split(
    X_outbreak, y_outbreak_cases, test_size=0.2, random_state=42
)

_, _, y_train_severity, y_test_severity = train_test_split(
    X_outbreak, y_outbreak_severity, test_size=0.2, random_state=42
)

# Scale features
scaler_outbreak = StandardScaler()
X_train_out_scaled = scaler_outbreak.fit_transform(X_train_out)
X_test_out_scaled = scaler_outbreak.transform(X_test_out)

print(f"✅ Training set: {X_train_out_scaled.shape}")
print(f"✅ Test set: {X_test_out_scaled.shape}")

# ============================================================================
# 5. FEATURE ENGINEERING FOR DEMAND FORECASTING
# ============================================================================
print("\n🔧 Engineering features for demand forecasting...")

# Sort by date
usage_df = usage_df.sort_values('usage_date')

# Create temporal features
usage_df['day_of_week'] = usage_df['usage_date'].dt.dayofweek
usage_df['day_of_year'] = usage_df['usage_date'].dt.dayofyear
usage_df['week_of_year'] = usage_df['usage_date'].dt.isocalendar().week
usage_df['is_monsoon'] = usage_df['month'].isin([6, 7, 8, 9]).astype(int)
usage_df['is_winter'] = usage_df['month'].isin([11, 12, 1, 2]).astype(int)

# Create lag features for medicine usage
for medicine in usage_df['medicine_name'].unique():
    med_mask = usage_df['medicine_name'] == medicine
    usage_df.loc[med_mask, 'prev_usage'] = usage_df.loc[med_mask, 'quantity_used'].shift(1)
    usage_df.loc[med_mask, 'prev_7d_avg'] = usage_df.loc[med_mask, 'quantity_used'].rolling(window=7, min_periods=1).mean()
    usage_df.loc[med_mask, 'prev_30d_avg'] = usage_df.loc[med_mask, 'quantity_used'].rolling(window=30, min_periods=1).mean()

usage_df['prev_usage'] = usage_df['prev_usage'].fillna(0)
usage_df['prev_7d_avg'] = usage_df['prev_7d_avg'].fillna(0)
usage_df['prev_30d_avg'] = usage_df['prev_30d_avg'].fillna(0)

# Encode categorical variables
for col in ['medicine_name', 'disease_name', 'state']:
    if col not in label_encoders:
        le = LabelEncoder()
        usage_df[col + '_encoded'] = le.fit_transform(usage_df[col].astype(str))
        label_encoders[col] = le
    else:
        # Use existing encoder
        usage_df[col + '_encoded'] = label_encoders[col].transform(usage_df[col].astype(str))

# Merge with outbreak data to get context
usage_with_outbreak = usage_df.merge(
    outbreak_df[['disease_name', 'state', 'month', 'year', 'number_of_cases']],
    on=['disease_name', 'state', 'month', 'year'],
    how='left'
)
usage_with_outbreak['outbreak_cases'] = usage_with_outbreak['number_of_cases'].fillna(0)

print("✅ Demand forecasting features engineered")

# ============================================================================
# 6. PREPARE DEMAND FORECASTING DATASET
# ============================================================================
print("\n📊 Preparing demand forecasting dataset...")

demand_feature_cols = [
    'medicine_name_encoded', 'disease_name_encoded', 'state_encoded',
    'month', 'quarter', 'day_of_week', 'week_of_year',
    'is_monsoon', 'is_winter', 'prev_usage', 'prev_7d_avg', 'prev_30d_avg',
    'outbreak_cases', 'effectiveness_rate'
]

demand_target = 'quantity_used'

# Remove rows with NaN
usage_clean = usage_with_outbreak.dropna(subset=demand_feature_cols + [demand_target])

X_demand = usage_clean[demand_feature_cols]
y_demand = usage_clean[demand_target]

# Split data
X_train_dem, X_test_dem, y_train_dem, y_test_dem = train_test_split(
    X_demand, y_demand, test_size=0.2, random_state=42
)

# Scale features
scaler_demand = StandardScaler()
X_train_dem_scaled = scaler_demand.fit_transform(X_train_dem)
X_test_dem_scaled = scaler_demand.transform(X_test_dem)

print(f"✅ Training set: {X_train_dem_scaled.shape}")
print(f"✅ Test set: {X_test_dem_scaled.shape}")

# ============================================================================
# 7. SAVE PROCESSED DATA
# ============================================================================
print("\n💾 Saving processed data...")

# Save processed dataframes
outbreak_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'outbreak_processed.csv'), index=False)
usage_with_outbreak.to_csv(os.path.join(PROCESSED_DATA_DIR, 'usage_processed.csv'), index=False)

# Save train/test splits
np.save(os.path.join(PROCESSED_DATA_DIR, 'X_train_outbreak.npy'), X_train_out_scaled)
np.save(os.path.join(PROCESSED_DATA_DIR, 'X_test_outbreak.npy'), X_test_out_scaled)
np.save(os.path.join(PROCESSED_DATA_DIR, 'y_train_cases.npy'), y_train_cases.values)
np.save(os.path.join(PROCESSED_DATA_DIR, 'y_test_cases.npy'), y_test_cases.values)
np.save(os.path.join(PROCESSED_DATA_DIR, 'y_train_severity.npy'), y_train_severity.values)
np.save(os.path.join(PROCESSED_DATA_DIR, 'y_test_severity.npy'), y_test_severity.values)

np.save(os.path.join(PROCESSED_DATA_DIR, 'X_train_demand.npy'), X_train_dem_scaled)
np.save(os.path.join(PROCESSED_DATA_DIR, 'X_test_demand.npy'), X_test_dem_scaled)
np.save(os.path.join(PROCESSED_DATA_DIR, 'y_train_demand.npy'), y_train_dem.values)
np.save(os.path.join(PROCESSED_DATA_DIR, 'y_test_demand.npy'), y_test_dem.values)

# Save scalers and encoders
with open(os.path.join(PROCESSED_DATA_DIR, 'scaler_outbreak.pkl'), 'wb') as f:
    pickle.dump(scaler_outbreak, f)

with open(os.path.join(PROCESSED_DATA_DIR, 'scaler_demand.pkl'), 'wb') as f:
    pickle.dump(scaler_demand, f)

with open(os.path.join(PROCESSED_DATA_DIR, 'label_encoders.pkl'), 'wb') as f:
    pickle.dump(label_encoders, f)

# Save feature names
with open(os.path.join(PROCESSED_DATA_DIR, 'feature_names.pkl'), 'wb') as f:
    pickle.dump({
        'outbreak_features': feature_cols,
        'demand_features': demand_feature_cols
    }, f)

print("✅ All processed data saved")

# ============================================================================
# 8. SUMMARY
# ============================================================================
print("\n" + "="*60)
print("✅ DATA PREPROCESSING COMPLETE!")
print("="*60)
print(f"\n📁 Processed data saved to: {PROCESSED_DATA_DIR}\n")
print("Saved Files:")
print("  1. outbreak_processed.csv")
print("  2. usage_processed.csv")
print("  3. Train/Test splits (.npy files)")
print("  4. Scalers and encoders (.pkl files)")
print("\n🎯 Next Step: Train ML models using outbreak_predictor.py and demand_forecaster.py")
