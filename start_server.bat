@echo off
echo Starting CavalierOne Server...
cd /d "c:\Users\jason.m.chgv\Documents\CavalierOne"

:: Activate Virtual Environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Warning: .venv not found. Using global python.
)

:: Run the application
python app.py

:: If the app crashes or stops, pause so errors can be seen
echo Server stopped.
pause
