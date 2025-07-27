#!/bin/bash

# Check if venv exists
if [ -d "venv" ]; then
    echo "Activating existing virtual environment..."
    source venv/bin/activate
    echo "Starting the program..."
    python leaderboard_pro.py
else
    echo "Creating virtual environment..."
    python -m venv venv
    echo "Activating virtual environment..."
    source venv/bin/activate
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements..."
        pip install -r requirements.txt
    else
        echo "requirements.txt not found, skipping installation."
    fi
    echo "Starting the program..."
    python leaderboard_pro.py
fi

read -p "Press enter to continue..."