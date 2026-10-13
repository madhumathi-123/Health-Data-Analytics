@echo off
echo ============================================================
echo  OUTBREAK-LINKED SMART DRUG INVENTORY SYSTEM
echo  Automated Setup and Run Script
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/8] Checking Python dependencies...
cd backend
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo     ✓ Python dependencies installed

echo.
echo [2/8] Generating datasets...
cd ..\data\scripts
if not exist ..\raw\disease_outbreaks.csv (
    python generate_datasets.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to generate datasets
        pause
        exit /b 1
    )
    echo     ✓ Datasets generated
) else (
    echo     ✓ Datasets already exist
)

echo.
echo [3/8] Preprocessing data...
if not exist ..\processed\X_train_outbreak.npy (
    python preprocess_data.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to preprocess data
        pause
        exit /b 1
    )
    echo     ✓ Data preprocessed
) else (
    echo     ✓ Preprocessed data already exists
)

echo.
echo [4/8] Training ML models...
cd ..\..\backend\models
if not exist trained_models\outbreak_cases_model.pkl (
    echo     Training outbreak prediction model...
    python outbreak_predictor.py --train
    if %errorlevel% neq 0 (
        echo ERROR: Failed to train outbreak model
        pause
        exit /b 1
    )
    echo     ✓ Outbreak model trained
) else (
    echo     ✓ Outbreak model already exists
)

if not exist trained_models\demand_forecast_model.pkl (
    echo     Training demand forecasting model...
    python demand_forecaster.py --train
    if %errorlevel% neq 0 (
        echo ERROR: Failed to train demand model
        pause
        exit /b 1
    )
    echo     ✓ Demand model trained
) else (
    echo     ✓ Demand model already exists
)

echo.
echo [5/8] Initializing database...
cd ..\database
if not exist inventory.db (
    python db_init.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
    echo     ✓ Database initialized
) else (
    echo     ✓ Database already exists
)

echo.
echo [6/8] Installing frontend dependencies...
cd ..\..\frontend
if not exist node_modules (
    echo     This may take a few minutes...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
    echo     ✓ Frontend dependencies installed
) else (
    echo     ✓ Frontend dependencies already installed
)

echo.
echo [7/8] Starting backend server...
cd ..\backend
start "Backend Server" cmd /k "python app.py"
timeout /t 5 /nobreak >nul
echo     ✓ Backend server started on http://localhost:5000

echo.
echo [8/8] Starting frontend application...
cd ..\frontend
start "Frontend App" cmd /k "npm start"
echo     ✓ Frontend starting on http://localhost:3000

echo.
echo ============================================================
echo  SYSTEM STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo  Backend:  http://localhost:5000
echo  Frontend: http://localhost:3000
echo.
echo  Default Login:
echo    Email:    admin@health.com
echo    Password: admin123
echo.
echo  Press any key to open the application in your browser...
pause >nul

start http://localhost:3000

echo.
echo  To stop the system:
echo    1. Close the Backend Server window
echo    2. Close the Frontend App window
echo.
echo  Press any key to exit this window...
pause >nul
