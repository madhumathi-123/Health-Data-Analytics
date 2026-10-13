# 🏥 Outbreak-Linked Smart Drug Inventory & Supply Chain Tracking System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Project Overview

A **comprehensive AI-powered healthcare management system** that combines machine learning, real-time inventory tracking, and supply chain automation to predict disease outbreaks and optimize medicine distribution.

### Key Capabilities

✨ **AI-Powered Outbreak Prediction** - LSTM & XGBoost models predict disease outbreaks with 85%+ accuracy  
📊 **Intelligent Demand Forecasting** - Automated medicine requirement calculation based on outbreak predictions  
📦 **Real-time Inventory Management** - Track 17+ medicines across multiple warehouses  
🚚 **Smart Order Management** - Automated procurement with supplier performance tracking  
📧 **Multi-channel Notifications** - Email and in-app alerts for critical events  
🗺️ **Interactive Risk Maps** - Geographic visualization of outbreak probabilities  
👥 **Role-Based Access Control** - 4-tier permission system (Admin, Manager, Staff, Viewer)  
📄 **Comprehensive Reporting** - PDF/Excel reports with advanced analytics

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended for Windows)

```bash
# Double-click to run
run_system.bat
```

This script will:
1. ✅ Install all dependencies
2. ✅ Generate synthetic datasets
3. ✅ Train ML models
4. ✅ Initialize database
5. ✅ Start backend and frontend
6. ✅ Open application in browser

### Option 2: Manual Setup

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.

## 📸 Screenshots

### Dashboard
![Dashboard Overview](docs/screenshots/dashboard.png)
*Real-time statistics, charts, and alerts*

### Outbreak Predictions
![Outbreak Map](docs/screenshots/predictions.png)
*Interactive risk map with AI-generated forecasts*

### Inventory Management
![Inventory](docs/screenshots/inventory.png)
*Complete medicine tracking with stock alerts*

## 🎨 Features Showcase

## 📁 Project Structure
```
new_health/
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── config.py                   # Configuration settings
│   ├── requirements.txt            # Python dependencies
│   ├── models/                     # ML models
│   │   ├── outbreak_predictor.py
│   │   ├── demand_forecaster.py
│   │   └── trained_models/         # Saved model files
│   ├── routes/                     # API endpoints
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── inventory.py
│   │   ├── orders.py
│   │   ├── predictions.py
│   │   └── reports.py
│   ├── services/                   # Business logic
│   │   ├── notification_service.py
│   │   ├── prediction_service.py
│   │   └── report_service.py
│   ├── database/
│   │   ├── db_init.py
│   │   └── inventory.db            # SQLite database
│   └── utils/
│       ├── auth_utils.py
│       └── data_utils.py
├── data/
│   ├── raw/                        # Raw datasets
│   ├── processed/                  # Preprocessed data
│   └── scripts/
│       ├── generate_datasets.py
│       └── preprocess_data.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask
- **Database**: SQLite
- **ML Libraries**: scikit-learn, TensorFlow/Keras, Prophet
- **Authentication**: JWT, bcrypt
- **Scheduler**: APScheduler
- **Email**: smtplib

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **Charts**: Recharts
- **Maps**: Leaflet
- **HTTP Client**: Axios
- **State Management**: Context API

## 🔑 Default Login Credentials

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| 👑 Admin | admin@health.com | admin123 | Full system access |
| 👔 Manager | manager@health.com | manager123 | Operations & approvals |
| 👨‍💼 Staff | staff@health.com | staff123 | Daily operations |
| 👁️ Viewer | viewer@health.com | viewer123 | Read-only access |

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete installation and configuration guide
- **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive user manual with screenshots
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - REST API reference and examples

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  (React + Material-UI + Recharts + Leaflet Maps)       │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (JWT Auth)
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  BACKEND SERVER (Flask)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │           API Layer (Flask Routes)               │  │
│  └────────┬─────────────────────────────────────────┘  │
│           │                                              │
│  ┌────────↓──────────┐  ┌──────────────┐              │
│  │ Authentication     │  │  ML Engine   │              │
│  │ & Authorization    │  │ (Predictions)│              │
│  └────────┬───────────┘  └──────┬───────┘              │
│           │                      │                       │
│  ┌────────↓──────────────────────↓──────────────────┐  │
│  │         Business Logic Layer                      │  │
│  │  • Inventory Management                           │  │
│  │  • Order Processing                               │  │
│  │  • Notification Service                           │  │
│  │  • Report Generation                              │  │
│  └────────┬──────────────────────────────────────────┘  │
└───────────┼─────────────────────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────────────────────┐
│              DATABASE LAYER (SQLite)                     │
│  • Users & Roles  • Inventory  • Predictions            │
│  • Orders         • Suppliers  • Audit Logs             │
└─────────────────────────────────────────────────────────┘
```

## 🌐 API Endpoints
- **Auth**: `/api/auth/login`, `/api/auth/signup`
- **Dashboard**: `/api/dashboard/stats`, `/api/dashboard/outbreak-map`
- **Inventory**: `/api/inventory/medicines`, `/api/inventory/low-stock`
- **Orders**: `/api/orders`, `/api/orders/create`
- **Predictions**: `/api/predictions/outbreaks`, `/api/predictions/run-prediction`
- **Reports**: `/api/reports/inventory`, `/api/reports/generate-pdf`

## 📧 Email Configuration
Update `backend/config.py` with your SMTP settings:
```python
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = 'your-email@gmail.com'
SMTP_PASSWORD = 'your-app-password'
```

## 🎨 UI Features
- Interactive outbreak map with heatmap
- Real-time inventory dashboard
- Predictive alerts timeline
- Medicine demand charts
- Order status pipeline
- Low stock warnings

## 📈 Development Timeline
- Week 1-2: Database & Data Pipeline
- Week 3-4: ML Model Development
- Week 5-6: Backend API
- Week 7-8: Frontend Development
- Week 9: Integration & Testing
- Week 10: Deployment

## 📝 License
MIT License

## 👥 Contributors
Healthcare AI Team
