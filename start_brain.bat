@echo off
echo Starting CavalierOne Brain...
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in PATH. Please install Python.
    pause
    exit /b
)

:: Start the Flask App in a new window
start "CavalierOne Server" python app.py

:: Wait a few seconds for server to start
timeout /t 5 /nobreak >nul

:: Open the Brain page
start http://127.0.0.1:5000/brain

echo SERVER RUNNING!
echo.
echo If you see "Authentication Error" on the page:
echo 1. Make sure you have NotebookLM open in Chrome.
echo 2. Run 'python manual_auth.py' in this folder.
echo.
pause
