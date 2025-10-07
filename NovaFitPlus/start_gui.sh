#!/usr/bin/env bash
echo "Starting NovaFit Plus GUI..."
echo

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment not found. Creating one..."
    python -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Launching NovaFit Plus GUI..."
python -m novafit_plus.ui_tk
