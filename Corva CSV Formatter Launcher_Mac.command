#!/bin/bash
cd "$(dirname "$0")"

echo "============================================"
echo "   Corva Automatic CSV Formatter - Mac"
echo "============================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Download it from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo "Installing required packages..."
pip3 install -r requirements.txt --quiet
echo ""
echo "Launching Corva Automatic CSV Formatter..."
echo ""
python3 main.py
