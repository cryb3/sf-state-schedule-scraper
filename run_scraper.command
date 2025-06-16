#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

echo "====================================================="
echo "SF State Class Schedule Scraper - macOS Launcher"
echo "====================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo ""
        echo "Please install Python from: https://python.org"
        echo "Or install via Homebrew: brew install python"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo "ERROR: pip is not installed"
        echo ""
        echo "Please install pip or reinstall Python"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

# Check if required packages are installed
echo "Checking for required packages..."
$PYTHON_CMD -c "import selenium, pandas, openpyxl, bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    $PIP_CMD install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install required packages"
        echo ""
        echo "Please run the following command manually:"
        echo "$PIP_CMD install -r requirements.txt"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Run the scraper
echo ""
echo "Starting SF State Schedule Scraper..."
echo ""
$PYTHON_CMD sf_state_scraper_interactive.py

echo ""
echo "Script completed."
read -p "Press Enter to exit..." 