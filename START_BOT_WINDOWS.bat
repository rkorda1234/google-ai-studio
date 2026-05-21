@echo off
:: Double-click this file on Windows to start the Campaign Generator Slack bot.

cd /d "%~dp0"

echo ======================================
echo   Campaign Generator Bot - Starting
echo ======================================

:: Install dependencies if needed
python -c "import slack_bolt" 2>nul
if errorlevel 1 (
  echo Installing dependencies (first time only)...
  pip install -r requirements.txt
)

:: Check .env exists
if not exist .env (
  echo ERROR: .env file not found.
  echo Copy .env.example to .env and fill in your tokens.
  pause
  exit /b 1
)

echo.
echo Bot is running! Go to Slack and type /campaign
echo Press Ctrl+C to stop.
echo.

python -m slack_bot.app
pause
