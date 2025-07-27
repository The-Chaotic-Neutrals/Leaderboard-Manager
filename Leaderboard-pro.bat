@echo off

REM Check if venv exists
if exist venv (
    echo Activating existing virtual environment...
    call venv\Scripts\activate.bat
    echo Starting the program...
    python leaderboard_pro.py
) else (
    echo Creating virtual environment...
    python -m venv venv
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if exist requirements.txt (
        echo Installing requirements...
        pip install -r requirements.txt
    ) else (
        echo requirements.txt not found, skipping installation.
    )
    echo Starting the program...
    python leaderboard_pro.py
)

pause