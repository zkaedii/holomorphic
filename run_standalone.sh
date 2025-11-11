#!/bin/bash
# Quick start script for Holomorphic Standalone Application

echo "=============================================="
echo "🧠 Holomorphic Signal Processing"
echo "   Standalone Full-Stack Application"
echo "=============================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check dependencies
echo "📦 Checking dependencies..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "⚠️  FastAPI not found. Installing..."
    pip install fastapi uvicorn[standard] numpy
}

python3 -c "import uvicorn" 2>/dev/null || {
    echo "⚠️  Uvicorn not found. Installing..."
    pip install uvicorn[standard]
}

python3 -c "import numpy" 2>/dev/null || {
    echo "⚠️  NumPy not found. Installing..."
    pip install numpy
}

echo "✓ All dependencies installed"
echo ""

# Start the application
echo "🚀 Starting application..."
echo ""
echo "   Access the app at: http://localhost:8080"
echo "   Press Ctrl+C to stop"
echo ""
echo "=============================================="
echo ""

python3 standalone_app.py
