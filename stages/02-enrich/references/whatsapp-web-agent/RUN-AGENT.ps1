Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  WhatsApp Pricing Agent" -ForegroundColor Cyan
Write-Host "============================================"
Write-Host ""

# Kill any stuck node processes
Write-Host "Clearing any stuck Node processes..." -ForegroundColor Yellow
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue

# Clean node_modules if corrupted
if (Test-Path "node_modules") {
    Write-Host "Removing old node_modules..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "node_modules"
}
if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json"
}

Write-Host ""
Write-Host "Installing packages (takes 1-2 mins first time)..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  BEFORE STARTING - make sure you have:" -ForegroundColor Cyan
Write-Host "  1. Filled in config.js with your Anthropic key" -ForegroundColor Cyan
Write-Host "  2. Your WhatsApp phone nearby to scan QR code" -ForegroundColor Cyan
Write-Host "============================================"
Write-Host ""
Read-Host "Press Enter to start"
Write-Host ""

node agent.js
Read-Host "Press Enter to exit"
