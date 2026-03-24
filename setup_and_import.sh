#!/bin/bash
# Setup and Import Script for Linux/Mac
# This script sets up the backend and imports SAP O2C data

set -e  # Exit on error

echo "================================================================================"
echo "Graph Query System - Setup and Import"
echo "================================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://www.python.org/downloads/"
    exit 1
fi

echo "Step 1: Setting up backend environment..."
echo ""

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Checking configuration..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Please copy .env.example to .env and configure your credentials"
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your Neo4j and LLM credentials"
    exit 1
fi

echo "Configuration found!"
echo ""

cd ..

echo "Step 3: Importing SAP O2C data..."
echo ""

# Check if data directory exists
if [ ! -d "sap-o2c-data" ]; then
    echo "ERROR: sap-o2c-data directory not found"
    echo "Please ensure the SAP O2C data is in the project root"
    exit 1
fi

# Run import script
python3 import_sap_data.py

echo ""
echo "================================================================================"
echo "Setup and Import Complete!"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
