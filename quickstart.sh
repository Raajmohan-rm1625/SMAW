#!/bin/bash

# Smart Bin AI - Quick Start Script
# This script helps you run the entire system

echo "========================================"
echo "Smart Bin AI - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    echo "Please install Python 3.7 or later"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo ""

# Install required Python modules
echo "Checking for required Python modules..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing flask..."
    pip3 install flask > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ flask installed successfully"
    else
        echo "❌ Failed to install flask"
        exit 1
    fi
else
    echo "✅ flask is already installed"
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing requests..."
    pip3 install requests > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ requests installed successfully"
    else
        echo "❌ Failed to install requests"
        exit 1
    fi
else
    echo "✅ requests is already installed"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the system:"
echo ""
echo "1. Terminal 1 - Start Python backend:"
echo "   cd /Users/raajmohan/Documents/VS Code/Mess waste Sys"
echo "   python3 smwis.py"
echo ""
echo "2. Terminal 2 - Open Frontend:"
echo "   Open this file in your browser:"
echo "   /Users/raajmohan/Documents/VS Code/Mess waste Sys/index.html"
echo ""
echo "✅ Server will be available at: http://localhost:8000"
echo "✅ Frontend will be available at the file path above"
echo ""
echo "For more help, see README copy.md"
