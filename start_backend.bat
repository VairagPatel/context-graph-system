@echo off
REM Start Backend Server
REM Run this from the backend folder

echo ================================================================================
echo Starting Backend Server
echo ================================================================================
echo.

REM Check if we're in the backend folder
if not exist "app\main.py" (
    echo ERROR: This script must be run from the backend folder
    echo.
    echo Please run:
    echo   cd backend
    echo   start_backend.bat
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo.
    echo Please run setup_backend.bat first:
    echo   setup_backend.bat
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found
    echo.
    echo Please configure .env:
    echo   copy .env.example .env
    echo   notepad .env
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo.
echo Backend will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload
