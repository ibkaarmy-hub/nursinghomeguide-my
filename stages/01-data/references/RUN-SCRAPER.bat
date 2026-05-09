@echo off
echo ============================================
echo  Facility Website Pricing Scraper
echo ============================================
echo.
echo Installing required tools...
pip install requests beautifulsoup4 pandas openpyxl -q
echo.
echo Scraping facility websites for pricing...
python "%~dp0scrape-facility-websites.py"
echo.
pause
