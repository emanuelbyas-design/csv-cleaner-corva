@echo off
cd /d "%~dp0"

echo ============================================
echo    Corva Automatic CSV Formatter - Windows
echo ============================================
echo.

where py >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed.
    echo Download it from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Installing required packages...
py -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install required packages.
    echo.
    pause
    exit /b 1
)
echo.
echo Launching Corva Automatic CSV Formatter...
echo.
py main.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application exited with an error.
    echo.
    pause
)
