@echo off
title SF State Schedule Scraper
echo.
echo =====================================================
echo SF State Class Schedule Scraper - Windows Launcher
echo =====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking for required packages...
python -c "import selenium, pandas, openpyxl, beautifulsoup4" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        echo.
        echo Please run the following command manually:
        echo pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

REM Run the scraper
echo.
echo Starting SF State Schedule Scraper...
echo.
python sf_state_scraper_interactive.py

echo.
echo Script completed.
pause 