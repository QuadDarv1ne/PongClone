#!/bin/bash
# PyPong - Cross-platform Pong game
# Linux/macOS launch script

echo "Starting PyPong..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ using your package manager"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "Error: Python 3.10+ is required (found: $PYTHON_VERSION)"
    exit 1
fi

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame-ce..."
    python3 -m pip install --user "pygame-ce>=2.4.0,<3.0.0"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install pygame"
        exit 1
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the game
cd "$SCRIPT_DIR"
python3 -c "from PyPong.pong import PongGame; PongGame().run()"
if [ $? -ne 0 ]; then
    echo "Error: Failed to run the game"
    exit 1
fi
