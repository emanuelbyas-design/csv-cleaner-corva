@echo off
cd /d "%~dp0"

echo ============================================
echo    CSV Cleaner for Corva - Windows Launcher
echo ============================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed.
    echo Download it from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt --quiet
echo.
echo Launching CSV Cleaner...
echo.
python main.py
