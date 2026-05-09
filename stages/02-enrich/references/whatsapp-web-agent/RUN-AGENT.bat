@echo off
echo ============================================
echo  WhatsApp Pricing Agent (No Twilio)
echo ============================================
echo.
echo Checking for Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please download and install from: https://nodejs.org
    echo Choose the LTS version.
    pause
    exit
)
echo Node.js found.
echo.
echo Installing packages (first time only, takes 1-2 mins)...
npm install
echo.
echo ============================================
echo  BEFORE STARTING - make sure you have:
echo  1. Filled in config.js with your Anthropic key
echo  2. Your WhatsApp phone nearby to scan QR code
echo ============================================
echo.
echo Press any key to start...
pause > nul
echo.
node agent.js
pause
