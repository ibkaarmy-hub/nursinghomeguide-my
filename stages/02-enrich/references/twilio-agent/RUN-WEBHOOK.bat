@echo off
echo ============================================
echo  Step 1: Start Webhook Server
echo ============================================
echo.
echo Installing packages...
pip install -r requirements.txt -q
echo.
echo Starting Flask webhook on port 5000...
echo Keep this window open while agent is running.
echo.
python app.py
pause
