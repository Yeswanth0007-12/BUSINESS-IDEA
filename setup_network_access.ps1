# PackOptima Network Access Setup Script
# Run this as Administrator in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PackOptima Network Access Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Step 1: Opening Firewall Ports..." -ForegroundColor Yellow
Write-Host ""

# Remove existing rules if they exist
Write-Host "Removing old firewall rules (if any)..." -ForegroundColor Gray
netsh advfirewall firewall delete rule name="PackOptima Frontend" 2>$null
netsh advfirewall firewall delete rule name="PackOptima Backend" 2>$null

# Add new rules
Write-Host "Adding firewall rule for Frontend (port 8080)..." -ForegroundColor Gray
netsh advfirewall firewall add rule name="PackOptima Frontend" dir=in action=allow protocol=TCP localport=8080

Write-Host "Adding firewall rule for Backend (port 8000)..." -ForegroundColor Gray
netsh advfirewall firewall add rule name="PackOptima Backend" dir=in action=allow protocol=TCP localport=8000

Write-Host ""
Write-Host "✓ Firewall ports opened successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Checking Docker Status..." -ForegroundColor Yellow
Write-Host ""

# Check if Docker is running
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker is running" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Step 3: Restarting Docker Containers..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Stopping containers..." -ForegroundColor Gray
    docker-compose down
    
    Write-Host "Starting containers..." -ForegroundColor Gray
    docker-compose up -d
    
    Write-Host ""
    Write-Host "✓ Docker containers restarted!" -ForegroundColor Green
} else {
    Write-Host "⚠ Docker is not running or not installed" -ForegroundColor Yellow
    Write-Host "Please start Docker Desktop and run this script again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your Network Information:" -ForegroundColor Cyan
Write-Host "  Computer IP: 10.249.42.28" -ForegroundColor White
Write-Host "  Frontend URL: http://10.249.42.28:8080" -ForegroundColor White
Write-Host "  Backend API: http://10.249.42.28:8000" -ForegroundColor White
Write-Host ""

Write-Host "Access from other devices:" -ForegroundColor Cyan
Write-Host "  1. Connect device to SAME WiFi network" -ForegroundColor White
Write-Host "  2. Open browser on device" -ForegroundColor White
Write-Host "  3. Go to: http://10.249.42.28:8080" -ForegroundColor White
Write-Host ""

Write-Host "Testing URLs:" -ForegroundColor Cyan
Write-Host "  From this computer: http://localhost:8080" -ForegroundColor White
Write-Host "  From phone/tablet: http://10.249.42.28:8080" -ForegroundColor White
Write-Host ""

Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host
