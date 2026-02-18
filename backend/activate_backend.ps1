# SafeSquare Backend Activation Helper
# Run this script to activate the virtual environment and start the server

Write-Host "🔧 Activating SafeSquare Backend Environment..." -ForegroundColor Cyan

# Navigate to backend directory
Set-Location -Path $PSScriptRoot

# Activate virtual environment
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Green
    & ".\venv\Scripts\Activate.ps1"
    
    Write-Host "`n📦 Environment activated!" -ForegroundColor Green
    Write-Host "`n🚀 To start the development server, run:" -ForegroundColor Yellow
    Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host "`n📊 To verify database, run:" -ForegroundColor Yellow
    Write-Host "   python verify_data.py" -ForegroundColor White
    Write-Host "`n⚙️  To run ingestion scripts:" -ForegroundColor Yellow
    Write-Host "   set PYTHONPATH=%CD%; python scripts\[script_name].py" -ForegroundColor White
    
} else {
    Write-Host "❌ Virtual environment not found at .\venv\" -ForegroundColor Red
    Write-Host "   Run: python -m venv venv" -ForegroundColor Yellow
    Write-Host "   Then: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "   Then: pip install -r requirements.txt" -ForegroundColor Yellow
}
