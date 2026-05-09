@echo off
echo ============================================
echo  Step 3: Send Opening Messages (Outreach)
echo ============================================
echo.
echo This sends the first WhatsApp message to all
echo facilities that don't have pricing yet.
echo.
echo Make sure Steps 1 and 2 are done first:
echo   Step 1: RUN-WEBHOOK.bat is running
echo   Step 2: ngrok is running and webhook URL is set in Twilio
echo.
pause
python send_outreach.py
pause
