# TgSecret - Windows Automatic Start Script
# Run: .\start-all.ps1

Write-Host "`n🚀 TgSecret Core Local - Windows Startup`n" -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host "`n📦 Checking dependencies...`n" -ForegroundColor Cyan

# Check backend node_modules
if (-Not (Test-Path "D:\USERBOT\backend\node_modules")) {
    Write-Host "⚠️  Installing backend dependencies (first time)..." -ForegroundColor Yellow
    cd D:\USERBOT\backend
    npm install
    npx prisma generate
    npx prisma db push
}

# Check admin node_modules
if (-Not (Test-Path "D:\USERBOT\admin\node_modules")) {
    Write-Host "⚠️  Installing admin dependencies (first time)..." -ForegroundColor Yellow
    cd D:\USERBOT\admin
    npm install
}

# Check userbot venv
if (-Not (Test-Path "D:\USERBOT\userbot\venv")) {
    Write-Host "⚠️  Creating Python virtual environment..." -ForegroundColor Yellow
    cd D:\USERBOT\userbot
    python -m venv venv
}

Write-Host "`n🎯 Starting services...`n" -ForegroundColor Cyan

# Start Backend API
Write-Host "1️⃣  Starting Backend API on http://localhost:3001" -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\USERBOT\backend; Write-Host '🔧 Backend API Starting...' -ForegroundColor Blue; npm run dev"

Start-Sleep -Seconds 2

# Start Admin Panel
Write-Host "2️⃣  Starting Admin Panel on http://localhost:3000" -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\USERBOT\admin; Write-Host '🎨 Admin Panel Starting...' -ForegroundColor Blue; npm run dev"

Start-Sleep -Seconds 1

# Start Userbot (if configured)
if ((Test-Path "D:\USERBOT\userbot\.env") -and (Select-String -Path "D:\USERBOT\userbot\.env" -Pattern "API_ID=YOUR" -Quiet) -eq $false) {
    Write-Host "3️⃣  Starting Telegram Userbot" -ForegroundColor Magenta
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\USERBOT\userbot; .\venv\Scripts\Activate.ps1; Write-Host '🤖 Userbot Starting...' -ForegroundColor Blue; python -m src.main"
} else {
    Write-Host "⚠️  Userbot not configured yet. Edit D:\USERBOT\userbot\.env first" -ForegroundColor Yellow
    Write-Host "   Get API credentials from: https://my.telegram.org" -ForegroundColor Yellow
}

Write-Host "`n✅ All services started!`n" -ForegroundColor Green
Write-Host "📍 URLs:" -ForegroundColor Cyan
Write-Host "   Backend API:  http://localhost:3001" -ForegroundColor White
Write-Host "   Admin Panel:  http://localhost:3000" -ForegroundColor White
Write-Host "   Health Check: http://localhost:3001/webhook/health" -ForegroundColor White
Write-Host "`n💡 To stop: Close all PowerShell windows`n" -ForegroundColor Yellow
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
