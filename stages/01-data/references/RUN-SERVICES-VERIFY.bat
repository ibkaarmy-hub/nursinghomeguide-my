@echo off
echo ============================================
echo  Facility Services and Care Type Verifier
echo ============================================
echo.
echo Installing required tools...
pip install requests beautifulsoup4 pandas -q
echo.
echo Analysing facility websites...
python "%~dp0scrape-services-verify.py"
echo.
pause
