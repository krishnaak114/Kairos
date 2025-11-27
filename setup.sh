#!/bin/bash

# Quick Start Script for Kair�s (Linux/Mac)
# Author: Krishna Agrawal

set -e  # Exit on error

echo "🚀 Kair�s - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Run tests
echo "Running tests..."
python -m pytest tests/ -v --tb=short
echo ""

# Run demo
echo "Running demo with sample data..."
python -m app.main --file data/events.json --interval 60 --allowed-misses 3
echo ""

echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run CLI: python -m app.main --file your_events.json --interval 60 --allowed-misses 3"
echo "  3. Run API: python -m app.main --api --port 8000"
echo "  4. Run tests: pytest tests/ -v"
echo "  5. Check docs: cat docs/ARCHITECTURE.md"
echo ""
echo "For more information, see README.md"
echo ""
