@echo off
REM Backend Setup Script - Uses full Python path
REM Run this from the backend folder

echo ================================================================================
echo Backend Setup
echo ================================================================================
echo.

REM Check if we're in the backend folder
if not exist "requirements.txt" (
    echo ERROR: This script must be run from the backend folder
    echo.
    echo Please run:
    echo   cd backend
    echo   setup_backend.bat
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
echo.

REM Create venv using full Python path
C:\Users\vaira\AppData\Local\Python\bin\python3.exe -m venv venv

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo.
    echo Python may not be installed correctly.
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
echo.

REM Activate venv
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated!
echo.

echo Step 3: Installing dependencies...
echo.

REM Install requirements
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Backend Setup Complete!
echo ================================================================================
echo.
echo Next steps:
echo.
echo 1. Make sure you configured .env with your credentials
echo    (Neo4j URI, password, and LLM API key)
echo.
echo 2. Import SAP data (from project root):
echo    cd ..
echo    C:\Users\vaira\AppData\Local\Python\bin\python3.exe import_sap_data.py
echo.
echo 3. Start the backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
pause
