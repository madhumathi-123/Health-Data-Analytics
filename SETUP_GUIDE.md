# Setup Guide - Outbreak-Linked Smart Drug Inventory System

## 📋 Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **Git** (optional, for version control)
- **Windows/Linux/Mac** operating system

## 🚀 Quick Start (Step-by-Step)

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Generate Datasets

```bash
cd ../data/scripts
python generate_datasets.py
```

**Expected Output:**
- `disease_outbreaks.csv` - 2000 outbreak records
- `medicine_inventory.csv` - 17 medicine records
- `medicine_usage_history.csv` - 5000 usage records
- `supply_chain.csv` - 1000 order records
- `suppliers.csv` - 6 supplier records

### Step 3: Preprocess Data

```bash
python preprocess_data.py
```

**Expected Output:**
- Processed CSV files
- Train/test splits (.npy files)
- Scalers and encoders (.pkl files)

### Step 4: Train ML Models

```bash
cd ../../backend/models
python outbreak_predictor.py --train
python demand_forecaster.py --train
```

**Expected Output:**
- `outbreak_cases_model.pkl`
- `outbreak_severity_model.pkl`
- `demand_forecast_model.pkl`
- Model metadata files

**Training Time:** ~2-5 minutes depending on your system

### Step 5: Initialize Database

```bash
cd ../database
python db_init.py
```

**Expected Output:**
- `inventory.db` created with all tables
- Sample data inserted
- Default users created

### Step 6: Start Backend Server

```bash
cd ..
python app.py
```

**Expected Output:**
```
🚀 OUTBREAK-LINKED SMART DRUG INVENTORY SYSTEM
Environment: development
Debug Mode: True
Database: C:\...\backend\database\inventory.db
Server: http://localhost:5000
```

**Keep this terminal running!**

### Step 7: Install Frontend Dependencies

Open a **NEW terminal** window:

```bash
cd frontend
npm install
```

**Installation Time:** ~2-3 minutes

### Step 8: Start Frontend Application

```bash
npm start
```

**Expected Output:**
```
Compiled successfully!
You can now view the app in the browser.
Local: http://localhost:3000
```

The application will automatically open in your default browser!

## 🔐 Default Login Credentials

| Role    | Email                  | Password   |
|---------|------------------------|------------|
| Admin   | admin@health.com       | admin123   |
| Manager | manager@health.com     | manager123 |
| Staff   | staff@health.com       | staff123   |
| Viewer  | viewer@health.com      | viewer123  |

## 📊 Testing the System

### 1. Login
- Go to `http://localhost:3000`
- Login with admin credentials

### 2. View Dashboard
- See real-time statistics
- View charts and graphs
- Check low stock alerts

### 3. Run Predictions
- Navigate to **Predictions** page
- Click **"Run Prediction"** button
- Wait for AI models to generate predictions (~30 seconds)
- View outbreak risk map

### 4. Manage Inventory
- Navigate to **Inventory** page
- View all medicines
- Filter by stock status
- Update stock levels

### 5. Create Orders
- Navigate to **Orders** page
- Click **"Create Order"**
- Select medicine and supplier
- Submit order

### 6. Generate Reports
- Navigate to **Reports** page
- Download PDF or Excel reports
- View comprehensive analytics

## 🔧 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'flask'`
```bash
cd backend
pip install -r requirements.txt
```

**Problem:** `Database file not found`
```bash
cd backend/database
python db_init.py
```

**Problem:** `ML models not found`
```bash
cd backend/models
python outbreak_predictor.py --train
python demand_forecaster.py --train
```

### Frontend Issues

**Problem:** `npm: command not found`
- Install Node.js from https://nodejs.org/

**Problem:** `Module not found` errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem:** `Port 3000 already in use`
```bash
# Kill the process using port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill
```

### API Connection Issues

**Problem:** `Network Error` or `CORS Error`
- Ensure backend is running on `http://localhost:5000`
- Check `frontend/src/services/api.js` has correct API_URL
- Verify CORS is enabled in `backend/app.py`

## 📁 Project Structure

```
new_health/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── database/
│   │   ├── db_init.py        # Database initialization
│   │   └── inventory.db      # SQLite database
│   ├── models/
│   │   ├── outbreak_predictor.py
│   │   ├── demand_forecaster.py
│   │   └── trained_models/   # Saved ML models
│   ├── routes/               # API endpoints
│   ├── services/             # Business logic
│   └── utils/                # Helper functions
├── data/
│   ├── raw/                  # Generated datasets
│   ├── processed/            # Preprocessed data
│   └── scripts/
│       ├── generate_datasets.py
│       └── preprocess_data.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── context/          # React context
│   │   └── App.js
│   └── package.json
└── README.md
```

## 🎯 Next Steps

1. **Explore Features:**
   - Test all CRUD operations
   - Run predictions multiple times
   - Generate reports

2. **Customize:**
   - Add more diseases in database
   - Modify prediction parameters
   - Customize UI theme

3. **Deploy:**
   - Set up production database
   - Configure email SMTP settings
   - Deploy to cloud (AWS, Azure, GCP)

## 📧 Email Configuration (Optional)

To enable email notifications:

1. Edit `backend/config.py`:
```python
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = 'your-email@gmail.com'
SMTP_PASSWORD = 'your-app-password'  # Use App Password for Gmail
```

2. For Gmail:
   - Enable 2-Factor Authentication
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Use the generated password in config

## 🔄 Automated Predictions

The system automatically runs predictions daily at 2 AM. To change this:

Edit `backend/config.py`:
```python
PREDICTION_SCHEDULE_HOUR = 2  # Change to desired hour (0-23)
```

## 💾 Backup & Restore

### Backup Database
```bash
cp backend/database/inventory.db backup/inventory_backup_$(date +%Y%m%d).db
```

### Restore Database
```bash
cp backup/inventory_backup_YYYYMMDD.db backend/database/inventory.db
```

## 🆘 Support

For issues or questions:
1. Check this guide
2. Review error logs in terminal
3. Check `backend/app.py` logs
4. Verify all dependencies are installed

## ✅ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4 GB | 8 GB |
| Storage | 2 GB | 5 GB |
| CPU | Dual Core | Quad Core |
| Python | 3.8 | 3.10+ |
| Node.js | 16.x | 18.x+ |

---

**Congratulations! Your system is now ready to use! 🎉**
