@echo off
REM Setup and Import Script for Windows
REM This script sets up the backend and imports SAP O2C data

echo ================================================================================
echo Graph Query System - Setup and Import
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Step 1: Setting up backend environment...
echo.

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Checking configuration...
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please copy .env.example to .env and configure your credentials
    echo.
    echo Press any key to open .env.example...
    pause >nul
    notepad .env.example
    echo.
    echo After configuring .env, run this script again
    pause
    exit /b 1
)

echo Configuration found!
echo.

cd ..

echo Step 3: Importing SAP O2C data...
echo.

REM Check if data directory exists
if not exist "sap-o2c-data" (
    echo ERROR: sap-o2c-data directory not found
    echo Please ensure the SAP O2C data is in the project root
    pause
    exit /b 1
)

REM Run import script
python import_sap_data.py

if errorlevel 1 (
    echo.
    echo ERROR: Import failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Setup and Import Complete!
echo ================================================================================
echo.
echo Next steps:
echo 1. Start the backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 2. Start the frontend (in a new terminal):
echo    cd frontend
echo    npm install
echo    npm run dev
echo.
echo 3. Open http://localhost:5173 in your browser
echo.
pause
