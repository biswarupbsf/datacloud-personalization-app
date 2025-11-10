#!/bin/bash

echo "========================================"
echo "  DATA CLOUD MANAGER - QUICK START"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Create data directory
mkdir -p data
mkdir -p templates/email_templates

echo "✅ Directories created"

echo ""
echo "========================================"
echo "  STARTING APPLICATION"
echo "========================================"
echo ""
echo "🚀 Server starting on http://localhost:5000"
echo "📖 Press Ctrl+C to stop the server"
echo ""

# Run the application
python3 app.py





