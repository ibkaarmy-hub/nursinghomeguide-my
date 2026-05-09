@echo off
echo ============================================
echo  Facebook Page Finder for Nursing Homes
echo ============================================
echo.
echo Installing required tools...
pip install requests beautifulsoup4 pandas -q
echo.
echo Searching for Facebook pages...
python "%~dp0find-facebook-pages.py"
echo.
pause
