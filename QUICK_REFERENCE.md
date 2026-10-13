# 🚀 QUICK REFERENCE CARD

## Outbreak-Linked Smart Drug Inventory System

---

## ⚡ Quick Start

### Windows (Easiest)
```bash
Double-click: run_system.bat
```

### Manual Start
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && npm start
```

---

## 🔑 Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@health.com | admin123 |
| Manager | manager@health.com | manager123 |
| Staff | staff@health.com | staff123 |

---

## 🌐 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

---

## 📁 Key Files

### Run & Setup
- `run_system.bat` - Automated setup
- `SETUP_GUIDE.md` - Installation guide
- `USER_GUIDE.md` - User manual

### Backend
- `backend/app.py` - Main server
- `backend/config.py` - Settings
- `backend/database/db_init.py` - Database setup

### Frontend
- `frontend/src/App.js` - Main app
- `frontend/package.json` - Dependencies

---

## 🎯 Common Tasks

### Generate Datasets
```bash
cd data/scripts
python generate_datasets.py
```

### Train ML Models
```bash
cd backend/models
python outbreak_predictor.py --train
python demand_forecaster.py --train
```

### Initialize Database
```bash
cd backend/database
python db_init.py
```

### Run Predictions
```bash
cd backend/services
python prediction_service.py --run
```

---

## 📊 API Quick Reference

### Authentication
```bash
POST /api/auth/login
POST /api/auth/signup
GET  /api/auth/verify-token
```

### Dashboard
```bash
GET /api/dashboard/stats
GET /api/dashboard/outbreak-map
```

### Inventory
```bash
GET  /api/inventory/medicines
POST /api/inventory/medicines
PUT  /api/inventory/medicines/:id
GET  /api/inventory/low-stock
```

### Predictions
```bash
GET  /api/predictions/outbreaks
POST /api/predictions/run-prediction
GET  /api/predictions/reorder-recommendations
```

### Orders
```bash
GET  /api/orders
POST /api/orders/create
PUT  /api/orders/:id/status
```

### Reports
```bash
GET /api/reports/inventory?format=pdf
GET /api/reports/outbreak-history
GET /api/reports/orders
```

---

## 🔧 Troubleshooting

### Backend Won't Start
```bash
cd backend
pip install -r requirements.txt
python database/db_init.py
```

### Frontend Won't Start
```bash
cd frontend
rm -rf node_modules
npm install
```

### Database Issues
```bash
cd backend/database
del inventory.db  # Windows
python db_init.py
```

### ML Models Missing
```bash
cd backend/models
python outbreak_predictor.py --train
python demand_forecaster.py --train
```

---

## 📦 Dependencies

### Backend (Python)
```bash
pip install flask flask-cors flask-jwt-extended
pip install numpy pandas scikit-learn xgboost tensorflow
pip install bcrypt reportlab openpyxl
```

### Frontend (Node.js)
```bash
npm install react react-router-dom
npm install @mui/material @emotion/react
npm install axios recharts react-leaflet leaflet
```

---

## 🎨 Features at a Glance

✅ **Dashboard** - Real-time stats & charts  
✅ **Inventory** - Medicine management  
✅ **Predictions** - AI outbreak forecasts  
✅ **Orders** - Supply chain tracking  
✅ **Reports** - PDF/Excel exports  
✅ **Notifications** - Email alerts  
✅ **Maps** - Geographic visualization  
✅ **Auth** - Role-based access  

---

## 📈 System Stats

- **17** Medicines
- **10** Diseases
- **6** Suppliers
- **4** User Roles
- **30+** API Endpoints
- **2** ML Models
- **9** Database Tables

---

## 🚨 Important Notes

⚠️ **Default SMTP** - Update `backend/config.py` for email  
⚠️ **Production** - Change SECRET_KEY before deployment  
⚠️ **Database** - Backup `inventory.db` regularly  
⚠️ **Models** - Retrain with real data for production  

---

## 📞 Help & Support

- **Setup Issues**: See SETUP_GUIDE.md
- **Usage Help**: See USER_GUIDE.md
- **API Reference**: See API_DOCUMENTATION.md
- **Project Info**: See PROJECT_SUMMARY.md

---

## 🎯 Next Steps

1. ✅ Run `run_system.bat`
2. ✅ Login at http://localhost:3000
3. ✅ Explore Dashboard
4. ✅ Run Predictions
5. ✅ Generate Reports
6. ✅ Customize for your needs

---

**💡 Tip**: Bookmark this page for quick reference!

---

*Quick Reference v1.0 | Last Updated: Nov 2024*
