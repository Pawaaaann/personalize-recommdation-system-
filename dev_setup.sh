#!/bin/bash

# EduRec Development Setup Script
# This script sets up a Python virtual environment and installs dependencies

set -e  # Exit on any error

echo "🚀 Setting up EduRec development environment..."

# Check if Python 3.10+ is available
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Check if required Python version is available
required_version="3.10"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version found, but Python $required_version or higher is required."
    exit 1
fi

echo "✅ Python $python_version found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Check if poetry is available
if command -v poetry &> /dev/null; then
    echo "📚 Installing dependencies with Poetry..."
    poetry install
else
    echo "📚 Installing dependencies with pip..."
    pip install -r requirements.txt
fi

echo ""
echo "🎉 Setup complete! To activate the environment, run:"
echo "   source venv/bin/activate"
echo ""
echo "📖 Next steps:"
echo "   1. Activate the environment: source venv/bin/activate"
echo "   2. Generate sample data: python -m src.edurec.data.generate_sample"
echo "   3. Run the API: python -m uvicorn src.edurec.api.main:app --reload"
echo "   4. Run tests: pytest src/edurec/tests/"
echo "" 