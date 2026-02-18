#!/bin/bash
# SafeSquare Backend Activation Helper (Linux/Mac)

echo "🔧 Activating SafeSquare Backend Environment..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "./venv/bin/activate" ]; then
    echo "✅ Activating virtual environment..."
    source ./venv/bin/activate
    
    echo ""
    echo "📦 Environment activated!"
    echo ""
    echo "🚀 To start the development server, run:"
    echo "   uvicorn app.main:app --reload"
    echo ""
    echo "📊 To verify database, run:"
    echo "   python verify_data.py"
    echo ""
    echo "⚙️  To run ingestion scripts:"
    echo "   PYTHONPATH=\$(pwd) python scripts/[script_name].py"
    
else
    echo "❌ Virtual environment not found at ./venv/"
    echo "   Run: python -m venv venv"
    echo "   Then: source ./venv/bin/activate"
    echo "   Then: pip install -r requirements.txt"
fi
