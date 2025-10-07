#!/usr/bin/env bash
echo "Starting NovaFit Plus CLI..."
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

echo "Launching NovaFit Plus CLI..."
python -m novafit_plus.app
