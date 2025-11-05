# OMNIVID Backend Startup Script
# This script starts all required services for the OMNIVID backend

Write-Host "🎬 Starting OMNIVID Backend..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".\.env")) {
    Write-Host "⚠️  .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "✓ Created .env file. Please update with your settings!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n📦 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "`n📚 Checking dependencies..." -ForegroundColor Cyan
$packages = pip list
if ($packages -notmatch "fastapi") {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check Redis connection
Write-Host "`n🔗 Checking Redis connection..." -ForegroundColor Cyan
try {
    $redis = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue
    if (-not $redis.TcpTestSucceeded) {
        Write-Host "❌ Redis not running on port 6379!" -ForegroundColor Red
        Write-Host "Please start Redis first:" -ForegroundColor Yellow
        Write-Host "  - WSL: wsl redis-server" -ForegroundColor White
        Write-Host "  - Docker: docker run -d -p 6379:6379 redis:latest" -ForegroundColor White
        exit 1
    }
    Write-Host "✓ Redis is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not verify Redis connection" -ForegroundColor Yellow
}

# Create required directories
Write-Host "`n📁 Creating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path ".\output" | Out-Null
New-Item -ItemType Directory -Force -Path ".\assets" | Out-Null
New-Item -ItemType Directory -Force -Path ".\tmp" | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green

# Ask user what to start
Write-Host "`n🚀 What would you like to start?" -ForegroundColor Cyan
Write-Host "1. API Server only" -ForegroundColor White
Write-Host "2. Celery Worker only" -ForegroundColor White
Write-Host "3. Both (requires 2 terminals)" -ForegroundColor White
Write-Host "4. Run tests" -ForegroundColor White
$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n🌐 Starting FastAPI server..." -ForegroundColor Cyan
        Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
        python main.py
    }
    "2" {
        Write-Host "`n⚙️  Starting Celery worker..." -ForegroundColor Cyan
        celery -A celery_app worker --loglevel=info --pool=solo
    }
    "3" {
        Write-Host "`n⚠️  Please start in separate terminals:" -ForegroundColor Yellow
        Write-Host "Terminal 1: celery -A celery_app worker --loglevel=info --pool=solo" -ForegroundColor White
        Write-Host "Terminal 2: python main.py" -ForegroundColor White
    }
    "4" {
        Write-Host "`n🧪 Running tests..." -ForegroundColor Cyan
        python test_remotion.py
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
    }
}
