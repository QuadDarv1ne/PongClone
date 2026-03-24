@echo off
REM PyPong - Cross-platform Pong game
REM Windows launch script

echo Starting PyPong...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if pygame is installed
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pygame-ce...
    python -m pip install pygame-ce>=2.4.0,<3.0.0
    if %errorlevel% neq 0 (
        echo Error: Failed to install pygame
        pause
        exit /b 1
    )
)

REM Run the game
python -c "from PyPong.pong import PongGame; PongGame().run()"
if %errorlevel% neq 0 (
    echo Error: Failed to run the game
    pause
    exit /b 1
)
